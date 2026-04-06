"""
Evaluate a trained DUAL-Pose checkpoint.

Usage:
    python test.py --dataset yoga82
    python test.py --dataset yoga16
"""

import argparse, os, sys
import torch
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.dirname(__file__))
from configs.config import DATASETS, MODEL, GLOBAL_FEAT_DIM, CHECKPOINT_DIR, RESULTS_DIR
from data.dataset import DualPoseDataset
from models.dual_pose import DualPose
from utils.evaluation import test, plot_confusion_matrix, print_report


def main(dataset_name: str):
    cfg  = DATASETS[dataset_name]
    mcfg = MODEL

    test_ds = DualPoseDataset(cfg["skeleton_data_root"], split="test",
                              num_views=mcfg["num_views"])
    loader  = DataLoader(test_ds, batch_size=cfg["batch_size"],
                         shuffle=False, num_workers=4, pin_memory=True)

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

    ckpt = os.path.join(CHECKPOINT_DIR, f"best_{dataset_name}.pth")
    if not os.path.exists(ckpt):
        raise FileNotFoundError(f"Checkpoint not found: {ckpt}\nRun train.py first.")
    model.load_state_dict(torch.load(ckpt, weights_only=True))
    print(f"Loaded checkpoint: {ckpt}")

    results = test(model, loader)
    print(f"\nDataset : {dataset_name}")
    print(f"Top-1   : {results['top1']:.2f}%")
    print(f"Top-5   : {results['top5']:.2f}%")

    label_file = os.path.join(cfg["skeleton_data_root"], "labels.txt")
    class_names = (open(label_file).read().strip().split("\n")
                   if os.path.exists(label_file) else None)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    plot_confusion_matrix(
        results["labels"], results["preds"],
        class_names=class_names,
        save_path=os.path.join(RESULTS_DIR, f"{dataset_name}_confusion.png"))
    print_report(results["labels"], results["preds"], class_names)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="yoga82",
                        choices=list(DATASETS.keys()))
    args = parser.parse_args()
    main(args.dataset)
