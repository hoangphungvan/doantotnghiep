"""
Pipeline huấn luyện GCN Model cho Candidate-Job Matching.

Features:
- BCEWithLogitsLoss với pos_weight=10 (xử lý mất cân bằng lớp)
- Train/Val split
- Early stopping
- Metrics: Accuracy, Precision, Recall, F1, AUC-ROC
"""

import os
import time
from typing import Optional

import torch
import torch.nn as nn
from torch.optim import Adam
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch_geometric.loader import DataLoader
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report,
)
import numpy as np

import config
from model import GCNModel, get_loss_fn


def train_epoch(model: GCNModel, loader: DataLoader,
                optimizer: torch.optim.Optimizer,
                loss_fn: nn.Module, device: torch.device) -> float:
    """Huấn luyện 1 epoch, trả về average loss."""
    model.train()
    total_loss = 0
    num_batches = 0

    for batch in loader:
        batch = batch.to(device)
        optimizer.zero_grad()

        logits = model(batch).squeeze(-1)
        labels = batch.y.to(device)

        loss = loss_fn(logits, labels)
        loss.backward()

        nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        total_loss += loss.item()
        num_batches += 1

    return total_loss / max(num_batches, 1)


@torch.no_grad()
def evaluate(model: GCNModel, loader: DataLoader,
             loss_fn: nn.Module, device: torch.device) -> dict:
    """Đánh giá model, trả về dict metrics."""
    model.eval()
    all_logits = []
    all_labels = []
    total_loss = 0
    num_batches = 0

    for batch in loader:
        batch = batch.to(device)
        logits = model(batch).squeeze(-1)
        labels = batch.y.to(device)

        loss = loss_fn(logits, labels)
        total_loss += loss.item()
        num_batches += 1

        all_logits.append(logits.cpu())
        all_labels.append(labels.cpu())

    all_logits = torch.cat(all_logits)
    all_labels = torch.cat(all_labels)

    probs = torch.sigmoid(all_logits).numpy()
    preds = (probs >= 0.5).astype(int)
    labels_np = all_labels.numpy().astype(int)

    metrics = {
        "loss": total_loss / max(num_batches, 1),
        "accuracy": accuracy_score(labels_np, preds),
        "precision": precision_score(labels_np, preds, zero_division=0),
        "recall": recall_score(labels_np, preds, zero_division=0),
        "f1": f1_score(labels_np, preds, zero_division=0),
    }

    if len(np.unique(labels_np)) > 1:
        metrics["auc_roc"] = roc_auc_score(labels_np, probs)
    else:
        metrics["auc_roc"] = 0.0

    return metrics


def train(data_list: list,
          input_dim: int,
          val_ratio: float = 0.2,
          num_epochs: int = None,
          batch_size: int = None,
          lr: float = None,
          device: Optional[torch.device] = None,
          save_path: str = None,
          patience: int = 15) -> tuple:
    """
    Pipeline huấn luyện đầy đủ.

    Args:
        data_list: List các PyG Data objects
        input_dim: Kích thước input features (3 * embedding_dim)
        val_ratio: Tỷ lệ validation set
        num_epochs: Số epoch huấn luyện
        batch_size: Kích thước batch
        lr: Learning rate
        device: CPU hoặc CUDA
        save_path: Đường dẫn lưu model tốt nhất
        patience: Số epoch chờ trước khi early stop

    Returns:
        (model, history)
    """
    num_epochs = num_epochs or config.NUM_EPOCHS
    batch_size = batch_size or config.BATCH_SIZE
    lr = lr or config.LEARNING_RATE

    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Train] Device: {device}")

    n_val = max(1, int(len(data_list) * val_ratio))
    n_train = len(data_list) - n_val

    indices = np.random.permutation(len(data_list))
    train_data = [data_list[i] for i in indices[:n_train]]
    val_data = [data_list[i] for i in indices[n_train:]]

    train_labels = [d.y.item() for d in train_data]
    val_labels = [d.y.item() for d in val_data]
    print(f"[Train] Train: {n_train} (pos={sum(l==1 for l in train_labels)}, neg={sum(l==0 for l in train_labels)})")
    print(f"[Train] Val: {n_val} (pos={sum(l==1 for l in val_labels)}, neg={sum(l==0 for l in val_labels)})")

    train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=batch_size, shuffle=False)

    model = GCNModel(input_dim=input_dim).to(device)
    optimizer = Adam(model.parameters(), lr=lr, weight_decay=config.WEIGHT_DECAY)
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
    loss_fn = get_loss_fn().to(device)

    best_val_loss = float('inf')
    best_epoch = 0
    epochs_no_improve = 0
    history = {"train_loss": [], "val_loss": [], "val_f1": [], "val_auc": []}

    save_path = save_path or os.path.join(config.MODEL_DIR, "best_model.pt")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    print(f"\n{'='*60}")
    print(f"{'Epoch':>6} | {'Train Loss':>10} | {'Val Loss':>10} | {'Val F1':>8} | {'Val AUC':>8} | {'LR':>10}")
    print(f"{'='*60}")

    for epoch in range(1, num_epochs + 1):
        train_loss = train_epoch(model, train_loader, optimizer, loss_fn, device)
        val_metrics = evaluate(model, val_loader, loss_fn, device)

        scheduler.step(val_metrics["loss"])

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_metrics["loss"])
        history["val_f1"].append(val_metrics["f1"])
        history["val_auc"].append(val_metrics["auc_roc"])

        current_lr = optimizer.param_groups[0]['lr']

        if epoch % 5 == 0 or epoch == 1:
            print(f"{epoch:>6} | {train_loss:>10.4f} | {val_metrics['loss']:>10.4f} | "
                  f"{val_metrics['f1']:>8.4f} | {val_metrics['auc_roc']:>8.4f} | {current_lr:>10.6f}")

        if val_metrics["loss"] < best_val_loss:
            best_val_loss = val_metrics["loss"]
            best_epoch = epoch
            epochs_no_improve = 0
            torch.save({
                "model_state_dict": model.state_dict(),
                "input_dim": input_dim,
                "epoch": epoch,
                "val_metrics": val_metrics,
            }, save_path)
        else:
            epochs_no_improve += 1

        if epochs_no_improve >= patience:
            print(f"\n[Early Stop] Không cải thiện sau {patience} epoch. Dừng tại epoch {epoch}.")
            break

    print(f"\n[Train] Best model tại epoch {best_epoch} với val_loss={best_val_loss:.4f}")
    print(f"[Train] Model đã lưu tại: {save_path}")

    checkpoint = torch.load(save_path, weights_only=False, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])

    print("\n=== Final Evaluation ===")
    final_metrics = evaluate(model, val_loader, loss_fn, device)
    for k, v in final_metrics.items():
        print(f"  {k}: {v:.4f}")

    return model, history


if __name__ == "__main__":
    from dataset import create_sample_dataset

    print("=== Training với sample data ===")
    dataset = create_sample_dataset(num_samples=50, positive_ratio=0.1)

    input_dim = dataset[0].x.shape[1]
    print(f"Input dim: {input_dim}")

    model, history = train(
        data_list=dataset.data_list,
        input_dim=input_dim,
        num_epochs=30,
        batch_size=8,
    )
