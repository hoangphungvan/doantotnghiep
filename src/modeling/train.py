"""
Pipeline huấn luyện GCN Model cho Candidate-Job Matching.

Features:
- Nhãn thang mức phù hợp 0..NUM_GRADES, train bằng soft-label BCE
  (target = grade / NUM_GRADES)
- Train/Val split theo nhóm CV (query-aware) để đánh giá xếp hạng không bị leakage
- Early stopping theo val_loss
- Metrics: MAE trên grade, AUC-ROC (binarized theo RELEVANT_GRADE)
- Ranking metrics trên val: NDCG@K, MRR, Recall@K
"""

import os
import sys
from typing import Optional

import torch
import torch.nn as nn
import numpy as np
from torch.optim import Adam
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch_geometric.loader import DataLoader
from sklearn.metrics import roc_auc_score

# Hỗ trợ chạy trực tiếp: python src/modeling/train.py (từ thư mục gốc dự án)
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from src.modeling.model import GCNModel, get_loss_fn, grade_to_target
from src.evaluation.metrics import evaluate_ranking, format_ranking_metrics


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_query_id(data) -> Optional[str]:
    """
    Trả về id nhóm (một CV) mà graph này thuộc về, None nếu không có.

    Ưu tiên cv_source (đặt bởi prepare_training_data/dataset),
    sau đó cv_path (đặt bởi CJMDataset khi xử lý từ CSV).
    """
    for attr in ("cv_source", "cv_path"):
        value = getattr(data, attr, None)
        if value:
            return str(value)
    return None


def split_by_query(data_list: list, val_ratio: float = 0.2):
    """
    Chia train/val theo nhóm CV: mọi cặp của cùng một CV nằm cùng bên split
    (tránh leakage khi đánh giá xếp hạng — model không "nhớ lại" CV đã thấy).

    Nếu graph không có thông tin nhóm → fallback chia ngẫu nhiên từng cặp.
    """
    query_ids = [get_query_id(d) for d in data_list]

    if all(q is not None for q in query_ids) and len(set(query_ids)) >= 4:
        unique_queries = sorted(set(query_ids))
        rng = np.random.default_rng(42)
        rng.shuffle(unique_queries)
        n_val_queries = max(1, int(len(unique_queries) * val_ratio))
        val_queries = set(unique_queries[:n_val_queries])

        train_data = [d for d, q in zip(data_list, query_ids) if q not in val_queries]
        val_data = [d for d, q in zip(data_list, query_ids) if q in val_queries]
        print(f"[Train] Split theo nhóm CV: {len(unique_queries)} CVs → "
              f"{len(unique_queries) - n_val_queries} train / {n_val_queries} val")
        return train_data, val_data

    print("[Train] [WARN] Graph không có cv_source/cv_path → chia ngẫu nhiên, "
          "không tính được ranking metrics.")
    indices = np.random.permutation(len(data_list))
    n_val = max(1, int(len(data_list) * val_ratio))
    return ([data_list[i] for i in indices[:-n_val]],
            [data_list[i] for i in indices[-n_val:]])


def print_grade_distribution(data_list: list, name: str):
    """In phân phối nhãn theo thang 0..NUM_GRADES."""
    grades = [d.y.item() for d in data_list]
    counts = {g: grades.count(g) for g in sorted(set(grades))}
    parts = [f"grade {int(g)}: {c}" for g, c in counts.items()]
    print(f"[Train] {name}: {len(grades)} mẫu — {' | '.join(parts)}")


# ---------------------------------------------------------------------------
# Train / evaluate
# ---------------------------------------------------------------------------

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
        targets = grade_to_target(batch.y.to(device))

        loss = loss_fn(logits, targets)
        loss.backward()

        nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        total_loss += loss.item()
        num_batches += 1

    return total_loss / max(num_batches, 1)


@torch.no_grad()
def evaluate(model: GCNModel, loader: DataLoader,
             loss_fn: nn.Module, device: torch.device) -> dict:
    """Đánh giá model trên dataloader: loss, MAE theo grade, AUC-ROC."""
    model.eval()
    all_logits = []
    all_labels = []
    total_loss = 0
    num_batches = 0

    for batch in loader:
        batch = batch.to(device)
        logits = model(batch).squeeze(-1)
        labels = batch.y.to(device)

        loss = loss_fn(logits, grade_to_target(labels))
        total_loss += loss.item()
        num_batches += 1

        all_logits.append(logits.cpu())
        all_labels.append(labels.cpu())

    all_logits = torch.cat(all_logits)
    all_labels = torch.cat(all_labels)

    scores = torch.sigmoid(all_logits).numpy()
    grades = all_labels.numpy()
    # MAE giữa grade dự đoán (score * NUM_GRADES) và grade thật
    pred_grades = scores * config.NUM_GRADES
    mae = float(np.mean(np.abs(pred_grades - grades)))

    metrics = {
        "loss": total_loss / max(num_batches, 1),
        "mae": mae,
    }

    # AUC-ROC trên bài toán nhị phân hóa: relevant = grade >= RELEVANT_GRADE
    binary_labels = (grades >= config.RELEVANT_GRADE).astype(int)
    if len(np.unique(binary_labels)) > 1:
        metrics["auc_roc"] = roc_auc_score(binary_labels, scores)
    else:
        metrics["auc_roc"] = 0.0

    return metrics


@torch.no_grad()
def evaluate_ranking_model(model: GCNModel, data_list: list,
                           device: torch.device) -> dict:
    """
    Tính ranking metrics (NDCG@K, MRR, Recall@K) trên danh sách graph.

    Group các cặp theo CV (cv_source/cv_path); với mỗi CV, xếp hạng các JD
    theo score của model rồi so với grade thật.
    """
    model.eval()

    query_groups: dict = {}
    for data in data_list:
        qid = get_query_id(data)
        if qid is None:
            continue
        data = data.to(device)
        logits = model(data)
        score = torch.sigmoid(logits).item()
        query_groups.setdefault(qid, []).append((data.y.item(), score))

    if not query_groups:
        return None
    return evaluate_ranking(query_groups, ks=config.RANKING_KS)


def train(data_list: list,
          input_dim: int,
          val_ratio: float = 0.2,
          num_epochs: int = None,
          batch_size: int = None,
          lr: float = None,
          device: Optional[torch.device] = None,
          save_path: str = None,
          patience: int = 15,
          pos_weight: float = None) -> tuple:
    """
    Pipeline huấn luyện đầy đủ với nhãn thang 0..NUM_GRADES.

    Args:
        data_list: List các PyG Data objects (y = grade 0..NUM_GRADES,
                   nên có cv_source/cv_path để split & đánh giá xếp hạng)
        input_dim: Kích thước input features (3 * embedding_dim)
        val_ratio: Tỷ lệ validation (theo số CV nếu có thông tin nhóm)
        num_epochs: Số epoch huấn luyện
        batch_size: Kích thước batch
        lr: Learning rate
        device: CPU hoặc CUDA
        save_path: Đường dẫn lưu model tốt nhất
        patience: Số epoch chờ trước khi early stop
        pos_weight: Chỉ dùng khi train nhãn nhị phân thuần (mặc định: không)

    Returns:
        (model, history)
    """
    num_epochs = num_epochs or config.NUM_EPOCHS
    batch_size = batch_size or config.BATCH_SIZE
    lr = lr or config.LEARNING_RATE

    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Train] Device: {device}")

    print_grade_distribution(data_list, "Toàn bộ dataset")

    train_data, val_data = split_by_query(data_list, val_ratio=val_ratio)
    print_grade_distribution(train_data, "Train")
    print_grade_distribution(val_data, "Val")

    train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=batch_size, shuffle=False)

    model = GCNModel(input_dim=input_dim).to(device)
    optimizer = Adam(model.parameters(), lr=lr, weight_decay=config.WEIGHT_DECAY)
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
    loss_fn = get_loss_fn(pos_weight=pos_weight).to(device)

    best_val_loss = float('inf')
    best_epoch = 0
    epochs_no_improve = 0
    history = {"train_loss": [], "val_loss": [], "val_mae": [], "val_auc": []}

    save_path = save_path or os.path.join(config.MODEL_DIR, "best_model.pt")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    print(f"\n{'='*70}")
    print(f"{'Epoch':>6} | {'Train Loss':>10} | {'Val Loss':>10} | {'Val MAE':>8} | {'Val AUC':>8} | {'LR':>10}")
    print(f"{'='*70}")

    for epoch in range(1, num_epochs + 1):
        train_loss = train_epoch(model, train_loader, optimizer, loss_fn, device)
        val_metrics = evaluate(model, val_loader, loss_fn, device)

        scheduler.step(val_metrics["loss"])

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_metrics["loss"])
        history["val_mae"].append(val_metrics["mae"])
        history["val_auc"].append(val_metrics["auc_roc"])

        current_lr = optimizer.param_groups[0]['lr']

        if epoch % 5 == 0 or epoch == 1:
            print(f"{epoch:>6} | {train_loss:>10.4f} | {val_metrics['loss']:>10.4f} | "
                  f"{val_metrics['mae']:>8.4f} | {val_metrics['auc_roc']:>8.4f} | {current_lr:>10.6f}")

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

    print("\n=== Final Evaluation (classification) ===")
    final_metrics = evaluate(model, val_loader, loss_fn, device)
    print(f"  loss: {final_metrics['loss']:.4f} | MAE: {final_metrics['mae']:.4f} | "
          f"AUC-ROC: {final_metrics['auc_roc']:.4f}")

    print("\n=== Final Evaluation (ranking theo CV) ===")
    ranking = evaluate_ranking_model(model, val_data, device)
    if ranking is not None:
        print(f"  Số query (CV) đánh giá: {ranking['num_queries']}")
        print(f"  {format_ranking_metrics(ranking)}")
    else:
        print("  [WARN] Không có thông tin nhóm CV (cv_source/cv_path) → bỏ qua ranking metrics.")

    return model, history


if __name__ == "__main__":
    import argparse
    from src.data_collection.prepare_training_data import load_all_graphs

    parser = argparse.ArgumentParser(description="Train GCN model từ dữ liệu đã chuẩn bị")
    parser.add_argument("--epochs",    type=int,   default=config.NUM_EPOCHS)
    parser.add_argument("--batch",     type=int,   default=config.BATCH_SIZE)
    parser.add_argument("--lr",        type=float, default=config.LEARNING_RATE)
    parser.add_argument("--patience",  type=int,   default=20)
    parser.add_argument("--save",      type=str,   default=None,
                        help="Đường dẫn lưu model (mặc định: models/best_model.pt)")
    args = parser.parse_args()

    graphs = load_all_graphs()

    if len(graphs) == 0:
        print("[ERROR] Chưa có dữ liệu training.")
        print("  Chạy trước: python main.py --mode prepare")
        print("           hoặc: python src/data_collection/prepare_training_data.py --mode file")
        raise SystemExit(1)

    print(f"\n[Train] Dataset: {len(graphs)} graphs")
    print_grade_distribution(graphs, "Dataset")

    grades = {g.y.item() for g in graphs}
    if len(grades) < 2:
        print(f"[ERROR] Dataset cần có ít nhất 2 mức grade khác nhau (0..{config.NUM_GRADES}), "
              f"hiện chỉ có: {sorted(grades)}")
        raise SystemExit(1)

    input_dim = graphs[0].x.shape[1]
    model, history = train(
        data_list=graphs,
        input_dim=input_dim,
        num_epochs=args.epochs,
        batch_size=args.batch,
        lr=args.lr,
        save_path=args.save,
        patience=args.patience,
    )
