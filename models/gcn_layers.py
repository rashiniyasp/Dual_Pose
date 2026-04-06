"""
GCN building block + BlazePose adjacency matrix.
"""

import torch
import torch.nn as nn
import numpy as np


# BlazePose 33-joint skeleton edges (undirected)
BLAZEPOSE_EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 7),          # face L
    (0, 4), (4, 5), (5, 6), (6, 8),          # face R
    (9, 10),                                   # mouth
    (11, 12),                                  # shoulders
    (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),  # left arm
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22),  # right arm
    (11, 23), (12, 24),                        # torso
    (23, 24),                                  # hips
    (23, 25), (25, 27), (27, 29), (27, 31),   # left leg
    (24, 26), (26, 28), (28, 30), (28, 32),   # right leg
    (0, 11), (0, 12),                          # head-shoulder
]


def build_adjacency(num_joints: int = 33,
                    edges: list = BLAZEPOSE_EDGES,
                    self_loops: bool = True) -> torch.Tensor:
    """Return normalised adjacency matrix A_hat = D^{-1/2} (A+I) D^{-1/2}."""
    A = np.zeros((num_joints, num_joints), dtype=np.float32)
    for i, j in edges:
        A[i, j] = 1.0
        A[j, i] = 1.0
    if self_loops:
        A += np.eye(num_joints, dtype=np.float32)
    D = np.diag(A.sum(1) ** -0.5)
    A_hat = D @ A @ D
    return torch.tensor(A_hat, dtype=torch.float32)


class GCNLayer(nn.Module):
    """
    Single spectral GCN layer.
      H_out = σ( A_hat  H_in  W )
    Input  shape: (B, N, F_in)
    Output shape: (B, N, F_out)
    """

    def __init__(self, in_features: int, out_features: int,
                 num_joints: int = 33, activation: bool = True):
        super().__init__()
        self.register_buffer("A_hat", build_adjacency(num_joints))
        self.linear = nn.Linear(in_features, out_features, bias=True)
        self.act    = nn.ReLU(inplace=True) if activation else nn.Identity()
        self.bn     = nn.BatchNorm1d(num_joints)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, N, F)
        out = torch.bmm(self.A_hat.unsqueeze(0).expand(x.size(0), -1, -1), x)
        out = self.linear(out)
        B, N, F = out.shape
        out = self.bn(out.reshape(B * N, F).unsqueeze(-1)
                       .reshape(B, N, F).reshape(B * N, F)).reshape(B, N, F)
        return self.act(out)
