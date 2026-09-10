from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F
from sfibai_b.model import build_model, _component_seed
from sfibai_b.loss import SFibAIObjective
from .config import ModelConfig


def gradient_scale(x, eta):
    return x.detach() + eta * (x - x.detach())


class Decoder(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        dims = [256, 512, 1024, 2048] if config.decoder == "fpn" else [1024]
        self.lateral = nn.ModuleList([nn.Conv2d(d, config.width, 1) for d in dims])
        self.output = nn.Sequential(nn.Conv2d(config.width, config.width, 3, padding=1), nn.ReLU(), nn.Conv2d(config.width, 1, 1))

    def forward(self, features, size):
        selected = features if self.config.decoder == "fpn" else [features[2]]
        target = (size[0] // self.config.stride, size[1] // self.config.stride)
        if self.config.decoder == "fpn":
            pyramid = self.lateral[-1](selected[-1])
            for level in range(2, -1, -1):
                pyramid = self.lateral[level](selected[level]) + F.interpolate(pyramid, size=selected[level].shape[-2:], mode="bilinear", align_corners=False)
        else:
            pyramid = self.lateral[0](selected[0])
        return self.output(F.interpolate(pyramid, size=target, mode="bilinear", align_corners=False))


class SearchModel(nn.Module):
    """Image-only forward; targets are accepted only by the training objective."""
    def __init__(self, config: ModelConfig, seed: int, pretrained=False):
        super().__init__()
        self.config = config
        legacy = config.mechanism in {"A_legacy", "A_tuned", "E_reference", "M0", "G_slow"}
        arm = "A" if config.mechanism.startswith("A_") else "G" if config.mechanism == "G_slow" else "E"
        self.base = build_model(arm=arm if legacy else "F", seed=seed, pretrained=pretrained)
        self.legacy = legacy
        self.has_aux = not config.mechanism.startswith("A_")
        if not legacy:
            # F modules provide paired auxiliary initialization; remove unused injections.
            for name in ("position_residual", "position_gate", "lesion_residual", "lesion_gate"):
                delattr(self.base, name)
            with _component_seed(seed + 30001):
                if config.mechanism != "M1":
                    del self.base.lesion_head
                    self.decoder = Decoder(config)
                if config.fusion != "none":
                    out_dim = 2048 if config.fusion == "feature" else 36
                    self.fusion = nn.Sequential(nn.Linear(1030, 64), nn.ReLU(), nn.Linear(64, out_dim))
                    nn.init.normal_(self.fusion[-1].weight, std=0.001)
                    nn.init.zeros_(self.fusion[-1].bias)
                    if config.fusion == "experts":
                        self.experts = nn.ModuleList([nn.Sequential(nn.Linear(2048, 16), nn.ReLU(), nn.Linear(16, 36)) for _ in range(6)])
                        for expert in self.experts:
                            nn.init.normal_(expert[-1].weight, std=0.001)
                            nn.init.zeros_(expert[-1].bias)
                if config.mechanism == "M4":
                    self.local_severity = nn.Conv2d(1024, 36, 1)

    def forward(self, image):
        if not isinstance(image, torch.Tensor) or image.ndim != 4 or image.shape[1] != 3:
            raise ValueError("forward accepts only N x 3 x H x W image tensors")
        if self.legacy:
            return self.base(image)
        b = self.base.backbone
        x = b.maxpool(b.relu(b.bn1(b.conv1(image))))
        features = []
        for layer in (b.layer1, b.layer2, b.layer3, b.layer4):
            x = layer(x)
            features.append(x)
        local = features[2]
        pooled = torch.flatten(b.avgpool(x), 1)
        q_logits = self.base.position_head(gradient_scale(pooled, self.config.auxiliary_eta))
        q = q_logits.float().softmax(1)
        with torch.autocast(image.device.type, enabled=False):
            scaled = [gradient_scale(f.float(), self.config.auxiliary_eta) for f in features]
            lesion = self.base.lesion_head(scaled[2]) if self.config.mechanism == "M1" else self.decoder(scaled, image.shape[-2:])
        attention = lesion.sigmoid()
        fused = pooled
        extra_logits = 0
        if self.config.fusion != "none":
            routing = gradient_scale(q, self.config.injection_eta)
            weights = gradient_scale(attention, self.config.injection_eta)
            weights = F.interpolate(weights, size=local.shape[-2:], mode="bilinear", align_corners=False)
            weights = weights / weights.sum((2, 3), keepdim=True).clamp_min(1e-8)
            evidence = (weights * local).sum((2, 3))
            residual = self.fusion(torch.cat([routing, evidence], 1))
            if self.config.fusion == "feature":
                fused = pooled + residual
            else:
                extra_logits = residual
                if self.config.fusion == "experts":
                    expert_logits = torch.stack([e(pooled) for e in self.experts], 1)
                    extra_logits = extra_logits + (routing.unsqueeze(-1) * expert_logits).sum(1)
        result = {"logits": self.base.grading_head(fused) + extra_logits,
                  "position_logits": q_logits, "position_probs": q,
                  "lesion_logits": lesion, "lesion_attention": attention}
        if self.config.mechanism == "M4":
            result["local_logits"] = self.local_severity(gradient_scale(local,self.config.auxiliary_eta))
        return result


class SearchObjective(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        auxiliary = not config.mechanism.startswith("A_")
        self.base = SFibAIObjective(lambda_position=config.position_weight if auxiliary else 0,
                                   lambda_box=config.lesion_weight if auxiliary else 0,
                                   arm="G" if config.mechanism == "G_slow" else None)

    def set_epoch(self, epoch):
        self.base.set_epoch(epoch)
        if self.config.mechanism != "G_slow" and self.config.warmup:
            self.base.aux_scale = min(1., epoch / self.config.warmup)

    def loss_components(self, outputs, batch):
        # Explicit FP32 reductions, including KL, expected bins and weak box pooling.
        outputs = {k: v.float() for k, v in outputs.items()}
        result = self.base.loss_components(outputs, batch)
        if self.config.loss == "cdf":
            probabilities = outputs["logits"].softmax(1)
            target = F.one_hot(batch["label_bin"].long(), 36).float()
            cdf = (probabilities.cumsum(1) - target.cumsum(1)).square().mean()
            result["cdf"] = cdf
            result["total"] = result["total"] + 0.1 * cdf
        if "local_logits" in outputs:
            logits = outputs["local_logits"]
            targets = F.interpolate(batch["local_target"].float(), size=logits.shape[-2:], mode="nearest")[:, 0].long()
            valid = targets >= 0
            loss = F.cross_entropy(logits, targets, ignore_index=-1) if valid.any() else logits.sum() * 0
            result["local_severity"] = loss
            result["total"] = result["total"] + self.base.aux_scale * self.config.local_weight * loss
        return result


def image_outputs(model, images):
    result = model(images)
    p = result["logits"].float().softmax(1)
    score = (p * torch.arange(36, device=p.device)).sum(1) / 10
    output = {"probabilities": p, "score": score,
              "grade": torch.bucketize(score, score.new_tensor([0.5, 1.5, 2.5]), right=True)}
    if model.has_aux:
        output.update(position_probabilities=result["position_probs"], position=result["position_probs"].argmax(1) + 1,
                      heatmap=result["lesion_attention"])
    return output
