"""Evaluation: top-1/top-5 accuracy and confusion matrix."""

import os
import numpy as np
import torch
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns


def test(model, loader, device=None, top_k=(1, 5)):
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval().to(device)

    all_preds, all_labels, all_logits = [], [], []
    with torch.no_grad():
        for kp, gf, labels in loader:
            kp, gf = kp.to(device), gf.to(device)
            logits = model(kp, gf)
            all_logits.append(logits.cpu())
            all_labels.append(labels)

    logits = torch.cat(all_logits)
    labels = torch.cat(all_labels)

    results = {}
    for k in top_k:
        topk_preds = logits.topk(k, dim=1).indices
        correct = topk_preds.eq(labels.unsqueeze(1).expand_as(topk_preds))
        results[f"top{k}"] = correct.any(dim=1).float().mean().item() * 100

    results["preds"]  = logits.argmax(1).numpy()
    results["labels"] = labels.numpy()
    return results


def plot_confusion_matrix(labels, preds, class_names=None,
                          save_path="results/confusion_matrix.png",
                          figsize=(14, 12)):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    cm = confusion_matrix(labels, preds)
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(cm_norm, annot=len(class_names or []) <= 30,
                fmt=".2f", cmap="Blues",
                xticklabels=class_names or "auto",
                yticklabels=class_names or "auto",
                ax=ax)
    ax.set_xlabel("Predicted"); ax.set_ylabel("True")
    ax.set_title("Normalised Confusion Matrix")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved confusion matrix → {save_path}")


def print_report(labels, preds, class_names=None):
    print(classification_report(labels, preds,
                                 target_names=class_names,
                                 digits=4))
