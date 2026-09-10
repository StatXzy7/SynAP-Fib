from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import torch
from sfibai_b.model import build_model
from sfibai_b.loss import SFibAIObjective, _soft_labels
from sfibai_b.data import FormalImageDataset
from sfibai_b.evaluation import evaluate_predictions, score_to_grade, score_cor
from synap_search.config import ModelConfig, TrainConfig, DataConfig
from synap_search.models import SearchModel, SearchObjective, gradient_scale, image_outputs
from synap_search.data import inner_partition, geometry, transform_box, predicted_regions, safe_image_path, DevelopmentDataset
from synap_search.training import learning_rate_factor, loader, rng_state, restore_rng
from synap_search.search import feasible, pruning_allowed
from synap_search.io import cache_key, digest
from synap_search.smoke import synthetic_batch, gradient_matrix


@pytest.fixture(autouse=True)
def threads():
    torch.set_num_threads(2)


@pytest.mark.parametrize("value,expected", [(0.,0),(.1,1),(.4,4),(.5,5),(1.5,15),(2.5,25),(3.5,35)])
def test_bins_and_grade_boundaries(value, expected):
    assert FormalImageDataset._score_to_bin(str(value)) == expected
    assert score_to_grade([value])[0] == sum(value >= x for x in [.5,1.5,2.5])


@pytest.mark.parametrize("value", ["-0.1", "3.6", "0.15", "nan"])
def test_invalid_labels(value):
    with pytest.raises((ValueError, OverflowError)):
        FormalImageDataset._score_to_bin(value)


def test_zero_only_excluded_not_clinical_f0():
    batch = synthetic_batch()
    batch.update(label_bin=torch.tensor([0,4]))
    output = {"logits": torch.zeros(2,36), "lesion_logits": torch.zeros(2,1,4,4)}
    values = SFibAIObjective(lambda_position=0, lambda_box=.1).loss_components(output,batch)
    assert values["valid_box_count"] == 1
    assert values["grade0_ignored_box_count"] == 1


def test_legacy_kl_clamp_duplicates_are_preserved():
    labels = torch.tensor([0,35])
    logits = torch.linspace(-1,1,36).repeat(2,1)
    objective = SFibAIObjective(lambda_position=0,lambda_box=0)
    kl = torch.nn.functional.kl_div(logits.log_softmax(1),_soft_labels(labels,36,1),reduction="none")
    expected = (kl[0,0]*3+kl[0,1]+kl[0,2]+kl[1,35]*3+kl[1,34]+kl[1,33])/2
    assert torch.allclose(objective._grading_components(logits,labels)["grading_kl"],expected)


@pytest.mark.parametrize("name,arm",[("A_legacy","A"),("A_tuned","A"),("E_reference","E"),("M0","E")])
def test_legacy_behavior_and_paired_initialization(name,arm):
    legacy=build_model(arm=arm,seed=42,pretrained=False).eval()
    wrapped=SearchModel(ModelConfig(mechanism=name),42).eval()
    batch=synthetic_batch()["image"]
    with torch.no_grad():
        left,right=legacy(batch),wrapped(batch)
    for key in left:
        assert torch.equal(left[key],right[key]),key
    new=SearchModel(ModelConfig(),42)
    for key,value in legacy.backbone.state_dict().items():
        assert torch.equal(value,new.base.backbone.state_dict()[key])


def test_a_f_shared_gradients_fp32():
    batch=synthetic_batch()
    gradients=[]
    for arm in ("A","F"):
        model=build_model(arm=arm,seed=42,pretrained=False).eval()
        from sfibai_b.loss import build_objective
        build_objective(arm)(model(batch["image"]),batch).backward()
        gradients.append({n:p.grad.clone() for n,p in model.named_parameters() if n.startswith(("backbone.","grading_head."))})
    assert gradients[0].keys()==gradients[1].keys()
    for key in gradients[0]:
        assert torch.equal(gradients[0][key],gradients[1][key]),key


@pytest.mark.parametrize("eta",[0,.1,.3,1])
def test_gradient_scale_exact(eta):
    x=torch.tensor([2.],requires_grad=True)
    y=gradient_scale(x,eta)
    assert torch.equal(x,y)
    y.sum().backward()
    assert x.grad.item()==pytest.approx(eta)


@pytest.mark.parametrize("eta,inject",[(0,0),(.3,0),(.3,1)])
def test_independent_gradient_axes_and_actual_head_update(eta,inject):
    model=SearchModel(ModelConfig(mechanism="M3",fusion="logit",auxiliary_eta=eta,injection_eta=inject),42).eval()
    batch=synthetic_batch()
    matrix=gradient_matrix(model,batch)["norms"]
    assert (matrix["position"]["backbone"]>0)==(eta>0)
    assert (matrix["box_raw"]["backbone"]>0)==(eta>0)
    assert (matrix["grading"]["position"]>0)==(inject>0)
    assert (matrix["grading"]["lesion"]>0)==(inject>0)
    assert matrix["position"]["position"]>0 and matrix["box_raw"]["lesion"]>0
    before=model.base.position_head.weight.detach().clone()
    opt=torch.optim.SGD(model.parameters(),lr=.01)
    opt.zero_grad()
    SearchObjective(model.config).loss_components(model(batch["image"]),batch)["total"].backward()
    opt.step()
    assert not torch.equal(before,model.base.position_head.weight)


def test_illegal_gt_input_and_three_outputs():
    model=SearchModel(ModelConfig(),42).eval()
    with pytest.raises(ValueError):
        model({"image":synthetic_batch()["image"],"position_norm":torch.tensor([1,2])})
    with pytest.raises(TypeError):
        model(synthetic_batch()["image"],position_norm=torch.tensor([1,2]))
    result=image_outputs(model,synthetic_batch()["image"])
    assert result["probabilities"].shape==(2,36)
    assert result["position_probabilities"].shape==(2,6)
    assert ((result["heatmap"]>=0)&(result["heatmap"]<=1)).all()


def test_patient_derived_samples_stay_together():
    frame=pd.DataFrame({"image_uid":list("abcdef"),"parent_image_uid":["a","a","c","d","e","f"],"patient_uid":["p1","p1","p2","p3","p4","p5"],"split":"train"})
    folded=inner_partition(frame)
    assert (folded.groupby("patient_uid").inner_split.nunique()==1).all()
    assert (folded.groupby("parent_image_uid").inner_split.nunique()==1).all()
    with pytest.raises(ValueError):
        inner_partition(frame.assign(split="test"))


@pytest.mark.parametrize("mode",["stretch","letterbox"])
def test_inverse_box_and_prediction_region(mode):
    matrix=geometry((31,79),512,mode)
    box=np.array([10,5,30,20])
    assert np.allclose(transform_box(transform_box(box,matrix),np.linalg.inv(matrix)),box)
    heatmap=np.zeros((32,32));heatmap[10:20,10:20]=.8
    regions=predicted_regions(heatmap,np.linalg.inv(matrix),512,(31,79))
    assert len(regions)==1 and regions[0]["confidence"]==pytest.approx(.8)


def test_test_access_denied_before_image_loading(tmp_path):
    with pytest.raises(ValueError):
        DevelopmentDataset(root=tmp_path,manifest=tmp_path/"missing",annotations=None,partition="test",config=DataConfig(),seed=1,training=False)
    path=tmp_path/"manifest.csv"
    pd.DataFrame({"split":["train","test"]}).to_csv(path,index=False)
    with pytest.raises(ValueError,match="contains test"):
        DevelopmentDataset(root=tmp_path,manifest=path,annotations=None,partition="native_train",config=DataConfig(),seed=1,training=True)
    with pytest.raises(ValueError):
        safe_image_path(tmp_path,"test/a.jpg","train")


def test_canonical_patient_max_and_center_weighting():
    frame=pd.DataFrame({"image_uid":list("abcd"),"patient_uid":["p1","p1","p2","p3"],"center_id":["c1","c1","c1","c2"],"true_score":[0.,3.,1.,2.],"pred_score":[3.,0.,2.,1.]})
    result=evaluate_predictions(frame)
    pm=score_cor([3,1,2],[3,2,1])["cor"]
    cb=(np.sqrt(2)*score_cor([3,1],[3,2])["cor"]+score_cor([2],[1])["cor"])/(np.sqrt(2)+1)
    assert result["patient_max"]["cor"]==pytest.approx(pm)
    assert result["r_final"]==pytest.approx(.4*score_cor(frame.true_score,frame.pred_score)["cor"]+.4*pm+.2*cb)


def test_prune_protection_and_horizon():
    assert not pruning_allowed(ModelConfig(mechanism="G_slow"),30,False)
    assert not pruning_allowed(ModelConfig(),30,True)
    assert pruning_allowed(ModelConfig(),30,False)
    cfg=TrainConfig(scheduler="cosine")
    assert learning_rate_factor(30,cfg)>0.8
    assert learning_rate_factor(120,cfg)==pytest.approx(0)


def test_rng_resume_and_zero_workers():
    torch.manual_seed(5)
    saved=rng_state()
    first=torch.rand(8)
    restore_rng(saved)
    assert torch.equal(first,torch.rand(8))
    dataset=torch.utils.data.TensorDataset(torch.arange(5))
    batches,_=loader(dataset,TrainConfig(workers=0,batch_size=2,device="cpu"),False)
    assert sum(len(x[0]) for x in batches)==5


def test_cache_and_manifest_hash_invalidation():
    key=cache_key("image","ann",{"resize":"stretch"})
    assert key!=cache_key("image2","ann",{"resize":"stretch"})
    assert key!=cache_key("image","ann2",{"resize":"stretch"})
    assert key!=cache_key("image","ann",{"resize":"letterbox"})
    assert digest({"seed":34001})!=digest({"seed":34002})


def test_auxiliary_constraints_do_not_compensate():
    reference={"position":{"macro_f1":.5},"lesion":{"iou_at_0_5":.3}}
    assert feasible(reference,reference)
    assert not feasible({"position":{"macro_f1":.9},"lesion":{"iou_at_0_5":.29}},reference)


def test_search_import_graph_has_no_legacy_runner():
    import ast
    import synap_search
    root=Path(synap_search.__file__).parent
    for name in ("search.py","training.py","data.py","models.py"):
        tree=ast.parse((root/name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node,ast.ImportFrom):
                assert node.module not in {"sfibai_b.runner","sfibai_b.queue","sfibai_b.ranking","sfibai_b.gate","finalize"}
