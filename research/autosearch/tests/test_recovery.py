from dataclasses import replace
import pandas as pd
import pytest
import torch
from torch import nn
from synap_search.config import ModelConfig, TrainConfig, DataConfig
from synap_search.io import read_json, write_json, sha256
from synap_search.search import halving_decision
from synap_search.finalize import verify_bundle, paired_seed_bootstrap, verify_manifest
from synap_search.data import max_grade_box_localization
from sfibai_b.data import LesionAnnotation


class TinyModel(nn.Module):
    def __init__(self, config, seed, pretrained):
        super().__init__()
        self.base=nn.Module()
        self.base.backbone=nn.Linear(3,4)
        self.base.grading_head=nn.Linear(4,36)
        self.config=config
        self.has_aux=False

    def forward(self,x):
        return {"logits":self.base.grading_head(self.base.backbone(x.mean((2,3))))}


class TinyDataset(torch.utils.data.Dataset):
    def __len__(self):
        return 4

    def __getitem__(self,index):
        index=index[0] if isinstance(index,tuple) else index
        return {"image":torch.ones(3,8,8)*(index+1)/4,"label_bin":torch.tensor(index*10),
                "true_score":torch.tensor(float(index)),"image_uid":f"i{index}","patient_uid":f"p{index}","center_id":f"c{index//2}","split":"val"}


def configure_training(monkeypatch,tmp_path):
    import synap_search.training as training
    torch.set_num_threads(1)
    monkeypatch.setattr(training,"SearchModel",TinyModel)
    monkeypatch.setattr(training,"make_datasets",lambda *args:[TinyDataset(),TinyDataset()])
    write_json(tmp_path/"DATA_AUDIT.json",{"status":"PASS","development_files":{}})
    config={"data":{"output":str(tmp_path)}}
    return training,config,ModelConfig(mechanism="A_legacy"),TrainConfig(device="cpu",batch_size=2,pretrained=False),DataConfig()


def test_training_strict_resume_matches_uninterrupted(monkeypatch,tmp_path):
    training,config,model,train,data=configure_training(monkeypatch,tmp_path)
    full=training.train_trial(config,model,train,data,tmp_path/"full",target_epoch=22)
    training.train_trial(config,model,train,data,tmp_path/"resumed",target_epoch=21)
    resumed=training.train_trial(config,model,train,data,tmp_path/"resumed",target_epoch=22,resume=True)
    left=torch.load(tmp_path/"full/last.pt",weights_only=False)
    right=torch.load(tmp_path/"resumed/last.pt",weights_only=False)
    for name in left["model"]:
        assert torch.equal(left["model"][name],right["model"][name]),name
    assert full["best"]["key"]==resumed["best"]["key"]
    with pytest.raises(ValueError,match="changed"):
        training.train_trial(config,model,replace(train,lr=.002),data,tmp_path/"resumed",target_epoch=23,resume=True)


def test_resume_replays_pending_rung_callback(monkeypatch,tmp_path):
    training,config,model,train,data=configure_training(monkeypatch,tmp_path)
    def fail_at_rung(epoch,*_):
        if epoch==30:
            raise OSError("simulated power interruption after checkpoint")
    with pytest.raises(OSError):
        training.train_trial(config,model,train,data,tmp_path/"run",target_epoch=31,callback=fail_at_rung)
    visited=[]
    training.train_trial(config,model,train,data,tmp_path/"run",target_epoch=31,resume=True,callback=lambda e,*_:visited.append(e))
    assert visited==[30,31]


def test_prune_replay_uses_frozen_peer_snapshot(tmp_path):
    path=tmp_path/"rung.json"
    assert halving_decision(path,.5,[.1,.2,.3])
    assert halving_decision(path,.5,[.9,.9,.9])
    assert read_json(path)["peers"]==[.1,.2,.3]


def test_mid_proposal_tpe_resume_preserves_all_future_parameters(tmp_path):
    import optuna
    from synap_search.search import DeterministicTPESampler
    def proposals(storage, interrupted):
        study=optuna.create_study(storage=storage,study_name="test",sampler=DeterministicTPESampler())
        result=[]
        for index in range(9):
            trial=study.ask()
            a=trial.suggest_float("a",1e-5,1e-3,log=True)
            if interrupted and index==7:
                study=optuna.load_study(storage=storage,study_name="test",sampler=DeterministicTPESampler())
                trial=optuna.Trial(study,trial._trial_id)
                assert a==trial.suggest_float("a",1e-5,1e-3,log=True)
            b=trial.suggest_categorical("b",[1,3,10])
            result.append((a,b))
            study.tell(trial,a*b)
        return result
    left=proposals("sqlite:///"+(tmp_path/"a.db").as_posix(),False)
    right=proposals("sqlite:///"+(tmp_path/"b.db").as_posix(),True)
    assert left==right


def test_report_bundle_tampering_is_rejected(tmp_path):
    names=["predictions_full.csv.gz","metrics.json","regions.json","deployment.json"]
    for name in names:
        (tmp_path/name).write_text("fixture",encoding="utf-8")
    write_json(tmp_path/"COMPLETE.json",{"checkpoint_sha256":"abc","files":{n:sha256(tmp_path/n) for n in names}})
    verify_bundle(tmp_path,{"checkpoint_sha256":"abc"})
    (tmp_path/"metrics.json").write_text("tampered",encoding="utf-8")
    with pytest.raises(ValueError,match="hash"):
        verify_bundle(tmp_path,{"checkpoint_sha256":"abc"})


def test_nonfrozen_manifest_cannot_open_test(tmp_path):
    write_json(tmp_path/"FINAL_MANIFEST.json",{"status":"PENDING","results":[]})
    with pytest.raises(ValueError):
        verify_manifest(tmp_path/"FINAL_MANIFEST.json")


def test_paired_seed_bootstrap_identical_models():
    frame=pd.DataFrame({"image_uid":list("abcd"),"patient_uid":["p1","p1","p2","p3"],"center_id":["c1","c1","c1","c2"],"true_score":[0.,3.,1.,2.],"pred_score":[1.,2.,1.,2.]})
    result=paired_seed_bootstrap([frame]*3,[frame]*3,resamples=20)
    assert result["mean_delta"]==0 and result["ci95"]==[0,0]
    with pytest.raises(ValueError):
        paired_seed_bootstrap([frame]*2,[frame]*2,resamples=20)


def test_localization_uses_predicted_boxes_only():
    annotation=LesionAnnotation(1,.1,.1,.5,.5)
    overlaps=max_grade_box_localization([{"box_roi_xyxy":[10,10,50,50]}],[annotation],(100,100))
    assert overlaps==[1.]
    assert max_grade_box_localization([],[annotation],(100,100))==[0.]


def test_run_all_stops_before_confirmation_and_test_on_failed_search(monkeypatch,tmp_path):
    import sys
    import types
    import synap_search.__main__ as cli
    monkeypatch.setattr(sys,"argv",["synap_search","run-all","--config","fixture.yaml"])
    monkeypatch.setattr(cli,"load_config",lambda _: {"data":{"output":str(tmp_path)}})
    visited=[]
    def run(args,check):
        command=args[4]
        visited.append(command)
        return types.SimpleNamespace(returncode=2 if command=="search" else 0)
    monkeypatch.setattr(cli.subprocess,"run",run)
    assert cli.main()==2
    assert visited==["audit","smoke","search"]
