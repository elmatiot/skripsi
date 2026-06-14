"""
Train & Validate - Receipt Region Classifier
=============================================
Dataset  : /home/ubuntu/skripsi/train  (597 images, 45 valid)
Labels   : rec_gt_train.txt / rec_gt_valid.txt
           Format: image_path\t[{transcription, points}, ...]
Classes  : struk_belanja, daftar_barang, total, waktu
Model    : MobileNetV3_small (PaddlePaddle)
Output   : output/classifier/  + plots saved as PNG
"""

import os
import io
import json
import math
import time
import random
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ── PaddlePaddle ──────────────────────────────────────────────────────────────
import paddle
import paddle.nn as nn
import paddle.optimizer as optim
from paddle.vision import transforms
from paddle.vision.models import mobilenet_v3_small

# ── PIL ───────────────────────────────────────────────────────────────────────
from PIL import Image

# ── Matplotlib (plots) ────────────────────────────────────────────────────────
import matplotlib
matplotlib.use("Agg")          # headless / no display needed
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MaxNLocator

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR    = "/home/ubuntu/skripsi"
TRAIN_DIR   = os.path.join(BASE_DIR, "train")
VALID_DIR   = os.path.join(BASE_DIR, "valid")
TRAIN_GT    = os.path.join(TRAIN_DIR, "rec_gt_train.txt")
VALID_GT    = os.path.join(VALID_DIR, "rec_gt_valid.txt")
OUTPUT_DIR  = os.path.join(BASE_DIR, "output", "classifier")
PLOT_PATH   = os.path.join(OUTPUT_DIR, "training_curves.png")

CLASSES     = ["struk_belanja", "daftar_barang", "total", "waktu"]
CLASS2IDX   = {c: i for i, c in enumerate(CLASSES)}
NUM_CLASSES = len(CLASSES)

IMG_SIZE    = 224
BATCH_SIZE  = 32
EPOCHS      = 30
LR          = 1e-3
SEED        = 42

os.makedirs(OUTPUT_DIR, exist_ok=True)
paddle.seed(SEED)
random.seed(SEED)
np.random.seed(SEED)

USE_GPU = paddle.is_compiled_with_cuda()
paddle.set_device("gpu" if USE_GPU else "cpu")
print(f"[INFO] Device : {'GPU' if USE_GPU else 'CPU'}")
print(f"[INFO] PaddlePaddle : {paddle.__version__}")

# ─────────────────────────────────────────────────────────────────────────────
#  DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────
def parse_label_file(gt_path: str, data_dir: str):
    """
    Parse rec_gt_*.txt:
      Each line: <rel_path>\t<JSON: list of {transcription, points}>
    Returns list of (abs_image_path, class_idx, (x1,y1,x2,y2))
    """
    samples = []
    with open(gt_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t", 1)
            if len(parts) < 2:
                continue
            rel_path, json_str = parts
            # abs path - handle both "train/img.jpg" and just "img.jpg"
            img_path = os.path.join(BASE_DIR, rel_path) if not os.path.isabs(rel_path) else rel_path
            if not os.path.exists(img_path):
                img_path = os.path.join(data_dir, os.path.basename(rel_path))
            if not os.path.exists(img_path):
                continue
            try:
                annots = json.loads(json_str)
            except json.JSONDecodeError:
                continue
            for ann in annots:
                cls = ann.get("transcription", "").strip()
                if cls not in CLASS2IDX:
                    continue
                pts = ann.get("points", [])  # [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
                if len(pts) < 2:
                    continue
                # Convert 4-corner points → axis-aligned bbox
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                x1, y1 = int(min(xs)), int(min(ys))
                x2, y2 = int(max(xs)), int(max(ys))
                if x2 <= x1 or y2 <= y1:
                    continue
                samples.append((img_path, CLASS2IDX[cls], (x1, y1, x2, y2)))
    return samples

print("[INFO] Parsing label files ...")
train_samples = parse_label_file(TRAIN_GT, TRAIN_DIR)
valid_samples = parse_label_file(VALID_GT, VALID_DIR)
print(f"[INFO] Train crops : {len(train_samples)}")
print(f"[INFO] Valid crops : {len(valid_samples)}")

# Class distribution
for split_name, split in [("Train", train_samples), ("Valid", valid_samples)]:
    dist = {c: 0 for c in CLASSES}
    for _, ci, _ in split:
        dist[CLASSES[ci]] += 1
    print(f"[INFO] {split_name} distribution: {dist}")

# ─────────────────────────────────────────────────────────────────────────────
#  TRANSFORMS
# ─────────────────────────────────────────────────────────────────────────────
mean = [0.485, 0.456, 0.406]
std  = [0.229, 0.224, 0.225]

train_tfm = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(brightness=0.3, contrast=0.3),
    transforms.ToTensor(),
    transforms.Normalize(mean=mean, std=std),
])
valid_tfm = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=mean, std=std),
])

# ─────────────────────────────────────────────────────────────────────────────
#  DATASET
# ─────────────────────────────────────────────────────────────────────────────
class CropDataset(paddle.io.Dataset):
    def __init__(self, samples, transform=None):
        self.samples   = samples
        self.transform = transform
        self._cache    = {}   # cache PIL crops in memory

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label, (x1, y1, x2, y2) = self.samples[idx]
        key = (img_path, x1, y1, x2, y2)
        if key not in self._cache:
            try:
                img = Image.open(img_path).convert("RGB")
                crop = img.crop((x1, y1, x2, y2))
            except Exception:
                crop = Image.new("RGB", (IMG_SIZE, IMG_SIZE), (128, 128, 128))
            self._cache[key] = crop
        crop = self._cache[key]
        if self.transform:
            crop = self.transform(crop)
        return crop, np.int64(label)


train_ds = CropDataset(train_samples, train_tfm)
valid_ds = CropDataset(valid_samples, valid_tfm)

train_loader = paddle.io.DataLoader(
    train_ds, batch_size=BATCH_SIZE, shuffle=True,
    num_workers=2, drop_last=False,
)
valid_loader = paddle.io.DataLoader(
    valid_ds, batch_size=BATCH_SIZE, shuffle=False,
    num_workers=2, drop_last=False,
)

# ─────────────────────────────────────────────────────────────────────────────
#  MODEL
# ─────────────────────────────────────────────────────────────────────────────
print("[INFO] Building MobileNetV3_small ...")
model = mobilenet_v3_small(pretrained=True, num_classes=1000)
# Replace classifier head
model.classifier[-1] = nn.Linear(1024, NUM_CLASSES)
model.train()

criterion = nn.CrossEntropyLoss()
scheduler = paddle.optimizer.lr.CosineAnnealingDecay(
    learning_rate=LR, T_max=EPOCHS, eta_min=1e-5
)
optimizer = optim.Adam(
    parameters=model.parameters(),
    learning_rate=scheduler,
    weight_decay=1e-4,
)

# ─────────────────────────────────────────────────────────────────────────────
#  TRAIN / EVAL HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def run_epoch(loader, model, criterion, optimizer=None, is_train=True):
    if is_train:
        model.train()
    else:
        model.eval()

    total_loss = 0.0
    correct    = 0
    total      = 0

    for images, labels in loader:
        logits = model(images)
        loss   = criterion(logits, labels)

        if is_train:
            loss.backward()
            optimizer.step()
            optimizer.clear_grad()

        total_loss += float(loss) * images.shape[0]
        preds       = paddle.argmax(logits, axis=1)
        correct    += int((preds == labels).sum())
        total      += images.shape[0]

    return total_loss / max(total, 1), correct / max(total, 1)

# ─────────────────────────────────────────────────────────────────────────────
#  TRAINING LOOP
# ─────────────────────────────────────────────────────────────────────────────
history = {
    "train_loss": [], "train_acc": [],
    "val_loss"  : [], "val_acc"  : [],
    "lr"        : [],
}
best_val_acc = 0.0
best_epoch   = 0

print(f"\n{'='*65}")
print(f"  Training {EPOCHS} epochs | Batch={BATCH_SIZE} | LR={LR}")
print(f"  Train samples={len(train_samples)} | Valid samples={len(valid_samples)}")
print(f"{'='*65}")
print(f"{'Ep':>4} | {'TrainLoss':>10} | {'TrainAcc':>9} | {'ValLoss':>9} | {'ValAcc':>8} | {'LR':>10} | {'Time':>7}")
print(f"{'-'*65}")

for epoch in range(1, EPOCHS + 1):
    t0 = time.time()
    current_lr = float(optimizer.get_lr())

    tr_loss, tr_acc = run_epoch(train_loader, model, criterion, optimizer, is_train=True)
    vl_loss, vl_acc = run_epoch(valid_loader, model, criterion, optimizer=None, is_train=False)

    scheduler.step()

    elapsed = time.time() - t0
    history["train_loss"].append(tr_loss)
    history["train_acc" ].append(tr_acc)
    history["val_loss"  ].append(vl_loss)
    history["val_acc"   ].append(vl_acc)
    history["lr"        ].append(current_lr)

    marker = " ★" if vl_acc > best_val_acc else ""
    if vl_acc > best_val_acc:
        best_val_acc = vl_acc
        best_epoch   = epoch
        paddle.save(model.state_dict(), os.path.join(OUTPUT_DIR, "best_model.pdparams"))

    print(f"{epoch:>4} | {tr_loss:>10.4f} | {tr_acc*100:>8.2f}% | "
          f"{vl_loss:>9.4f} | {vl_acc*100:>7.2f}% | {current_lr:>10.2e} | {elapsed:>5.1f}s{marker}")

# Always save latest
paddle.save(model.state_dict(), os.path.join(OUTPUT_DIR, "last_model.pdparams"))

print(f"\n[✓] Best Val Acc: {best_val_acc*100:.2f}% @ Epoch {best_epoch}")
print(f"[✓] Model saved  : {OUTPUT_DIR}")

# ─────────────────────────────────────────────────────────────────────────────
#  PLOT TRAINING CURVES
# ─────────────────────────────────────────────────────────────────────────────
def plot_training_curves(history, best_epoch, best_val_acc, save_path):
    epochs_x = list(range(1, len(history["train_loss"]) + 1))

    # ── Style ──────────────────────────────────────────────────────────────
    plt.style.use("dark_background")
    DARK_BG  = "#0d1117"
    CARD_BG  = "#161b22"
    BLUE     = "#58a6ff"
    GREEN    = "#3fb950"
    ORANGE   = "#f0883e"
    PURPLE   = "#d2a8ff"
    RED      = "#f85149"
    GRAY     = "#8b949e"
    WHITE    = "#e6edf3"

    fig = plt.figure(figsize=(16, 10), facecolor=DARK_BG)
    fig.suptitle(
        "🏋️  Receipt Region Classifier — Training Report",
        fontsize=18, fontweight="bold", color=WHITE, y=0.98
    )

    gs   = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35,
                             left=0.07, right=0.97, top=0.91, bottom=0.08)
    axes = [fig.add_subplot(gs[r, c]) for r in range(2) for c in range(2)]

    def style_ax(ax, title):
        ax.set_facecolor(CARD_BG)
        ax.set_title(title, color=WHITE, fontsize=13, fontweight="bold", pad=10)
        ax.tick_params(colors=GRAY, labelsize=9)
        ax.xaxis.label.set_color(GRAY)
        ax.yaxis.label.set_color(GRAY)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        for spine in ax.spines.values():
            spine.set_edgecolor("#30363d")
        ax.grid(True, color="#21262d", linestyle="--", linewidth=0.6)

    # ── 1. Loss Curve ──────────────────────────────────────────────────────
    ax = axes[0]
    style_ax(ax, "📉  Loss")
    ax.plot(epochs_x, history["train_loss"], color=BLUE,   lw=2.0, label="Train Loss", marker="o", ms=3)
    ax.plot(epochs_x, history["val_loss"],   color=ORANGE, lw=2.0, label="Val Loss",   marker="s", ms=3)
    ax.axvline(best_epoch, color=GREEN, ls="--", lw=1.2, alpha=0.7)
    ax.set_xlabel("Epoch"); ax.set_ylabel("Loss")
    ax.legend(facecolor="#21262d", edgecolor="#30363d", labelcolor=WHITE, fontsize=9)

    # ── 2. Accuracy Curve ──────────────────────────────────────────────────
    ax = axes[1]
    style_ax(ax, "📈  Accuracy")
    ax.plot(epochs_x, [v * 100 for v in history["train_acc"]], color=BLUE,   lw=2.0, label="Train Acc", marker="o", ms=3)
    ax.plot(epochs_x, [v * 100 for v in history["val_acc"]],   color=GREEN,  lw=2.0, label="Val Acc",   marker="s", ms=3)
    ax.axvline(best_epoch, color=ORANGE, ls="--", lw=1.2, alpha=0.7)
    ax.set_xlabel("Epoch"); ax.set_ylabel("Accuracy (%)")
    ax.set_ylim(0, 105)
    ax.legend(facecolor="#21262d", edgecolor="#30363d", labelcolor=WHITE, fontsize=9)

    # ── 3. Learning Rate Schedule ──────────────────────────────────────────
    ax = axes[2]
    style_ax(ax, "📐  Learning Rate Schedule")
    ax.plot(epochs_x, history["lr"], color=PURPLE, lw=2.0, marker=".", ms=4)
    ax.set_xlabel("Epoch"); ax.set_ylabel("LR")
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))

    # ── 4. Summary Stats ───────────────────────────────────────────────────
    ax = axes[3]
    ax.set_facecolor(CARD_BG)
    for spine in ax.spines.values():
        spine.set_edgecolor("#30363d")
    ax.axis("off")

    best_tr_acc  = max(history["train_acc"]) * 100
    best_vl_acc  = best_val_acc * 100
    final_tr_loss= history["train_loss"][-1]
    final_vl_loss= history["val_loss"][-1]

    rows = [
        ("Model",          "MobileNetV3 Small"),
        ("Classes",        ", ".join(CLASSES)),
        ("Train Samples",  str(len(train_samples))),
        ("Valid Samples",  str(len(valid_samples))),
        ("Epochs",         str(len(epochs_x))),
        ("Batch Size",     str(BATCH_SIZE)),
        ("Best Epoch",     f"{best_epoch}"),
        ("Best Val Acc",   f"{best_vl_acc:.2f} %"),
        ("Best Train Acc", f"{best_tr_acc:.2f} %"),
        ("Final Train Loss",f"{final_tr_loss:.4f}"),
        ("Final Val Loss", f"{final_vl_loss:.4f}"),
    ]

    ax.set_title("📊  Summary", color=WHITE, fontsize=13, fontweight="bold", pad=10)
    for i, (k, v) in enumerate(rows):
        y_pos = 0.97 - i * 0.085
        ax.text(0.04, y_pos, f"  {k}:", transform=ax.transAxes,
                fontsize=9.5, color=GRAY, va="top")
        ax.text(0.52, y_pos, v, transform=ax.transAxes,
                fontsize=9.5, color=WHITE, va="top", fontweight="bold")

    # ── Timestamp ──────────────────────────────────────────────────────────
    fig.text(0.97, 0.01, f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
             ha="right", fontsize=8, color=GRAY)

    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
    plt.close(fig)
    print(f"\n[✓] Plot saved  : {save_path}")


plot_training_curves(history, best_epoch, best_val_acc, PLOT_PATH)

# ─────────────────────────────────────────────────────────────────────────────
#  FINAL REPORT
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  TRAINING COMPLETE")
print("=" * 65)
print(f"  Best epoch        : {best_epoch} / {EPOCHS}")
print(f"  Best val accuracy : {best_val_acc * 100:.2f}%")
print(f"  Train loss (final): {history['train_loss'][-1]:.4f}")
print(f"  Val   loss (final): {history['val_loss'][-1]:.4f}")
print(f"  Model dir         : {OUTPUT_DIR}")
print(f"  Plot              : {PLOT_PATH}")
print("=" * 65)
