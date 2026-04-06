"""
Train DUAL-Pose on Yoga-82 or Yoga-16.

Usage:
    python train.py --dataset yoga82
    python train.py --dataset yoga16
"""

import argparse, os, sys
import torch
from torch.utils.data import DataLoader, random_split

sys.path.insert(0, os.path.dirname(__file__))
from configs.config import DATASETS, MODEL, GLOBAL_FEAT_DIM, CHECKPOINT_DIR, RESULTS_DIR
from data.dataset import DualPoseDataset
from models.dual_pose import DualPose, count_parameters
from utils.training import fit, plot_history


def main(dataset_name: str):
    cfg  = DATASETS[dataset_name]
    mcfg = MODEL

    # ── Data ──────────────────────────────────────────────────────────────────
    train_ds = DualPoseDataset(cfg["skeleton_data_root"], split="train",
                               num_views=mcfg["num_views"])
    test_ds  = DualPoseDataset(cfg["skeleton_data_root"], split="test",
                               num_views=mcfg["num_views"])

    # If no val split exists, carve 10 % from training
    val_size   = max(1, int(0.1 * len(train_ds)))
    train_size = len(train_ds) - val_size
    train_ds, val_ds = random_split(train_ds, [train_size, val_size],
                                    generator=torch.Generator().manual_seed(42))

    train_loader = DataLoader(train_ds, batch_size=cfg["batch_size"],
                              shuffle=True,  num_workers=4, pin_memory=True)
    val_loader   = DataLoader(val_ds,   batch_size=cfg["batch_size"],
                              shuffle=False, num_workers=4, pin_memory=True)

    print(f"Train: {len(train_ds)}  Val: {len(val_ds)}  Test: {len(test_ds)}")

    # ── Model ─────────────────────────────────────────────────────────────────
    model = DualPose(
        num_classes = cfg["num_classes"],
        num_joints  = mcfg["num_joints"],
        gcn_hidden  = mcfg["gcn_hidden"],
        mlp_hidden  = mcfg["mlp_hidden"],
        embed_dim   = mcfg["embed_dim"],
        global_dim  = GLOBAL_FEAT_DIM,
        num_views   = mcfg["num_views"],
        dropout     = mcfg["dropout"],
    )
    print(f"Parameters: {count_parameters(model):,}")

    # ── Train ─────────────────────────────────────────────────────────────────
    model, history = fit(model, train_loader, val_loader, cfg,
                         checkpoint_dir=CHECKPOINT_DIR,
                         dataset_name=dataset_name)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    plot_history(history,
                 save_path=os.path.join(RESULTS_DIR,
                                        f"{dataset_name}_training_curve.png"))
    print("Training complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="yoga82",
                        choices=list(DATASETS.keys()))
    args = parser.parse_args()
    main(args.dataset)
