"""Training loop, EarlyStopping, and history plotting."""

import os, time
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt


class EarlyStopping:
    def __init__(self, patience: int = 20, delta: float = 1e-4,
                 checkpoint_path: str = "best_model.pth"):
        self.patience = patience
        self.delta    = delta
        self.path     = checkpoint_path
        self.best     = np.inf
        self.counter  = 0
        self.stop     = False

    def __call__(self, val_loss: float, model: nn.Module) -> None:
        if val_loss < self.best - self.delta:
            self.best    = val_loss
            self.counter = 0
            torch.save(model.state_dict(), self.path)
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.stop = True

    def load_best(self, model: nn.Module) -> nn.Module:
        model.load_state_dict(torch.load(self.path, weights_only=True))
        return model


def fit(model, train_loader, val_loader, cfg: dict,
        checkpoint_dir: str = "checkpoints", dataset_name: str = "yoga82"):
    """
    Train DUAL-Pose.
    Returns history dict: {train_loss, val_loss, train_acc, val_acc}.
    """
    os.makedirs(checkpoint_dir, exist_ok=True)
    ckpt_path = os.path.join(checkpoint_dir, f"best_{dataset_name}.pth")

    device    = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model     = model.to(device)

    optimiser = torch.optim.AdamW(model.parameters(),
                                 lr=cfg.get("lr", 0.001),
                                 weight_decay=1e-3)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                    optimiser, T_max=cfg["epochs"])
    criterion = nn.CrossEntropyLoss(label_smoothing=0.2)
    stopper   = EarlyStopping(cfg["patience"], checkpoint_path=ckpt_path)

    history = {"train_loss": [], "val_loss": [],
               "train_acc":  [], "val_acc":  []}

    for epoch in range(1, cfg["epochs"] + 1):
        t0 = time.time()
        # ── train ─────────────────────────────────────────────────────────────
        model.train()
        run_loss, correct, total = 0.0, 0, 0
        for kp, gf, labels in train_loader:
            kp, gf, labels = kp.to(device), gf.to(device), labels.to(device)
            
            # Explicit Noise Augmentation on Features (Optional but helpful)
            kp_noise = torch.randn_like(kp) * 0.01
            kp = kp + kp_noise
            gf_noise = torch.randn_like(gf) * 0.01
            gf = gf + gf_noise

            optimiser.zero_grad()
            logits = model(kp, gf)
            loss   = criterion(logits, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimiser.step()
            run_loss += loss.item() * labels.size(0)
            correct  += (logits.argmax(1) == labels).sum().item()
            total    += labels.size(0)
        train_loss = run_loss / total
        train_acc  = correct  / total

        # ── validate ──────────────────────────────────────────────────────────
        model.eval()
        run_loss, correct, total = 0.0, 0, 0
        with torch.no_grad():
            for kp, gf, labels in val_loader:
                kp, gf, labels = kp.to(device), gf.to(device), labels.to(device)
                logits  = model(kp, gf)
                loss    = criterion(logits, labels)
                run_loss += loss.item() * labels.size(0)
                correct  += (logits.argmax(1) == labels).sum().item()
                total    += labels.size(0)
        val_loss = run_loss / total
        val_acc  = correct  / total

        scheduler.step()
        stopper(val_loss, model)

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(train_acc)
        history["val_acc"].append(val_acc)

        print(f"Epoch {epoch:03d}/{cfg['epochs']}  "
              f"train {train_loss:.4f}/{train_acc*100:.2f}%  "
              f"val {val_loss:.4f}/{val_acc*100:.2f}%  "
              f"({time.time()-t0:.1f}s)")

        if stopper.stop:
            print(f"Early stopping at epoch {epoch}.")
            break

    model = stopper.load_best(model)
    return model, history


def plot_history(history: dict, save_path: str = "results/training_curve.png"):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    epochs = range(1, len(history["train_loss"]) + 1)

    ax1.plot(epochs, history["train_loss"], label="Train")
    ax1.plot(epochs, history["val_loss"],   label="Val")
    ax1.set_title("Loss"); ax1.set_xlabel("Epoch"); ax1.legend()

    ax2.plot(epochs, [a*100 for a in history["train_acc"]], label="Train")
    ax2.plot(epochs, [a*100 for a in history["val_acc"]],   label="Val")
    ax2.set_title("Accuracy (%)"); ax2.set_xlabel("Epoch"); ax2.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved training curve -> {save_path}")
