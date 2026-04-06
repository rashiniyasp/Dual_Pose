"""
Step 2 – DualPoseDataset
  • Loads pre-extracted .npy skeleton files (33 × 4: x, y, z, vis)
  • Canonical alignment: centre at hip midpoint, scale by torso length,
    zero yaw via shoulder-hip axis
  • Generates `num_views` synthetic yaw-rotated copies
  • Computes 113-D global feature vector (99 joint coords + 14 limb angles)
"""

import os
import numpy as np
import torch
from torch.utils.data import Dataset


# ── 14 angle triplets (vertex is the middle index) ────────────────────────────
ANGLE_TRIPLETS = [
    (11, 13, 15),  # left elbow
    (12, 14, 16),  # right elbow
    (23, 11, 13),  # left shoulder
    (24, 12, 14),  # right shoulder
    (11, 23, 25),  # left hip
    (12, 24, 26),  # right hip
    (23, 25, 27),  # left knee
    (24, 26, 28),  # right knee
    (25, 27, 29),  # left ankle
    (26, 28, 30),  # right ankle
    (13, 15, 17),  # left wrist
    (14, 16, 18),  # right wrist
    (0,  11, 23),  # left trunk
    (0,  12, 24),  # right trunk
]  # 14 angles  →  99 + 14 = 113-D


def _angle(a, v, b):
    """Angle at vertex v formed by rays v→a and v→b (in radians)."""
    u1 = a - v;  u1 /= (np.linalg.norm(u1) + 1e-8)
    u2 = b - v;  u2 /= (np.linalg.norm(u2) + 1e-8)
    return np.arccos(np.clip(np.dot(u1, u2), -1.0, 1.0))


def canonical_align(kp: np.ndarray) -> np.ndarray:
    """
    kp: (33, 3)
    Returns canonically aligned (33, 3).
      1. Translate: hip midpoint → origin
      2. Scale:     torso length → 1
      3. Yaw zero:  rotate so that shoulder-midpoint lies on +X axis
    """
    kp = kp.copy()
    hip_mid  = (kp[23] + kp[24]) / 2.0
    kp      -= hip_mid

    torso_len = np.linalg.norm(kp[11] + kp[12]) / 2.0 + 1e-8
    kp       /= torso_len

    shoulder_mid = (kp[11] + kp[12]) / 2.0
    yaw = np.arctan2(shoulder_mid[2], shoulder_mid[0])
    cy, sy = np.cos(-yaw), np.sin(-yaw)
    R = np.array([[cy, 0, -sy], [0, 1, 0], [sy, 0, cy]], dtype=np.float32)
    kp = (R @ kp.T).T
    return kp


def yaw_rotate(kp: np.ndarray, angle_rad: float) -> np.ndarray:
    """Apply yaw rotation about Y-axis."""
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    R = np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]], dtype=np.float32)
    return (R @ kp.T).T


def global_features(kp: np.ndarray) -> np.ndarray:
    """kp: (33, 3) → 113-D feature vector."""
    coords = kp.flatten()                                       # 99-D
    angles = np.array([_angle(kp[a], kp[v], kp[b])
                        for a, v, b in ANGLE_TRIPLETS],
                      dtype=np.float32)                         # 14-D
    return np.concatenate([coords, angles])                     # 113-D


class DualPoseDataset(Dataset):
    """
    Folder layout expected:
        root/
            train/ (or test/)
                class_name/
                    sample.npy
        root/labels.txt    ← one class name per line, sorted
    """

    def __init__(self, root: str, split: str = "train", num_views: int = 16):
        self.num_views = num_views
        self.yaw_angles = np.linspace(0, 2 * np.pi, num_views, endpoint=False)

        label_file = os.path.join(root, "labels.txt")
        if os.path.exists(label_file):
            class_names = open(label_file).read().strip().split("\n")
        else:
            class_names = sorted(os.listdir(os.path.join(root, split)))
        self.cls2idx = {c: i for i, c in enumerate(class_names)}

        split_dir = os.path.join(root, split)
        self.samples = []  # (path, label_idx)
        for cls in class_names:
            cls_dir = os.path.join(split_dir, cls)
            if not os.path.isdir(cls_dir):
                continue
            for fname in os.listdir(cls_dir):
                if fname.endswith(".npy"):
                    self.samples.append((os.path.join(cls_dir, fname),
                                         self.cls2idx[cls]))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        raw = np.load(path)                  # (33, 4) or (33, 3)
        kp  = raw[:, :3].astype(np.float32)  # keep only xyz

        kp_aligned = canonical_align(kp)     # (33, 3)

        # Multi-view: stack num_views rotated copies
        views = np.stack([yaw_rotate(kp_aligned, a) for a in self.yaw_angles])
        # → (V, 33, 3)

        # Global features for each view
        gf = np.stack([global_features(views[v]) for v in range(self.num_views)])
        # → (V, 113)

        return (torch.tensor(views, dtype=torch.float32),
                torch.tensor(gf,   dtype=torch.float32),
                label)
