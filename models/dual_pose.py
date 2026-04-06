"""
DUAL-Pose model:
  GCN branch  → local anatomical topology
  MLP branch  → global geometric relations (113-D features)
  Attention-based aggregation over num_views synthetic yaw rotations
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from models.gcn_layers import GCNLayer


class GCNBranch(nn.Module):
    """Two GCN layers → global average pool → embedding."""

    def __init__(self, in_features: int = 3, hidden: int = 32,
                 embed_dim: int = 64, num_joints: int = 33,
                 dropout: float = 0.3):
        super().__init__()
        self.gcn1 = GCNLayer(in_features, hidden, num_joints)
        self.gcn2 = GCNLayer(hidden, embed_dim, num_joints)
        self.drop = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, N, 3)
        h = self.gcn1(x)
        h = self.drop(h)
        h = self.gcn2(h)            # (B, N, embed_dim)
        return h.mean(dim=1)        # global avg pool → (B, embed_dim)


class MLPBranch(nn.Module):
    """Two-layer MLP on 113-D global features → embedding."""

    def __init__(self, in_features: int = 113, hidden: int = 64,
                 embed_dim: int = 64, dropout: float = 0.3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, hidden),
            nn.BatchNorm1d(hidden),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(hidden, embed_dim),
            nn.BatchNorm1d(embed_dim),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)   # (B, embed_dim)


class DualPose(nn.Module):
    """
    Args:
        num_classes : number of pose categories (82 for Yoga-82, 16 for Yoga-16)
        num_joints  : 33 (BlazePose)
        gcn_hidden  : hidden dim inside GCN branch
        mlp_hidden  : hidden dim inside MLP branch
        embed_dim   : embedding dim for each branch
        global_dim  : dimensionality of global feature vector (default 113)
        num_views   : number of synthetic yaw-rotation views
        dropout     : dropout probability

    Forward inputs:
        kp_views  : (B, V, N, 3)   skeleton views
        gf_views  : (B, V, global_dim) global features per view

    Returns:
        logits    : (B, num_classes)
    """

    def __init__(self, num_classes: int, num_joints: int = 33,
                 gcn_hidden: int = 32, mlp_hidden: int = 64,
                 embed_dim: int = 64, global_dim: int = 113,
                 num_views: int = 16, dropout: float = 0.3):
        super().__init__()
        self.num_views = num_views

        self.gcn_branch = GCNBranch(3, gcn_hidden, embed_dim,
                                    num_joints, dropout)
        self.mlp_branch = MLPBranch(global_dim, mlp_hidden, embed_dim,
                                    dropout)

        # per-view classifier head
        self.classifier = nn.Linear(embed_dim * 2, num_classes)

        # attention over views: 1 scalar weight per view per sample
        self.attn_fc = nn.Linear(embed_dim * 2, 1)

    def forward(self, kp_views: torch.Tensor,
                gf_views: torch.Tensor) -> torch.Tensor:
        B, V, N, C = kp_views.shape

        # flatten view dimension into batch for branch forward passes
        kp_flat = kp_views.reshape(B * V, N, C)
        gf_flat = gf_views.reshape(B * V, -1)

        gcn_emb = self.gcn_branch(kp_flat)   # (B*V, embed_dim)
        mlp_emb = self.mlp_branch(gf_flat)   # (B*V, embed_dim)

        fused = torch.cat([gcn_emb, mlp_emb], dim=-1)  # (B*V, embed_dim*2)

        # attention weights
        attn_w = self.attn_fc(fused).reshape(B, V)      # (B, V)
        attn_w = F.softmax(attn_w, dim=1).unsqueeze(-1) # (B, V, 1)

        # weighted sum over views
        fused = fused.reshape(B, V, -1)                  # (B, V, E)
        agg   = (attn_w * fused).sum(dim=1)              # (B, E)

        return self.classifier(agg)                      # (B, num_classes)


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
