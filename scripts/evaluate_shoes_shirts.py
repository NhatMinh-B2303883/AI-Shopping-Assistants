"""Evaluation script for test_shoes_shirts dataset using SigLIP 2 (google/siglip2-base-patch16-256).

Evaluates:
1. Zero-shot Classification Accuracy & Detailed Classification Report (Precision, Recall, F1).
2. Confusion Matrix.
3. Multi-class ROC Curve & One-vs-Rest (OvR) AUC (Area Under the Curve).
4. Content-Based Image Retrieval (CBIR) Metrics: Top-1 Accuracy, Top-5 Accuracy, Mean Average Precision (mAP).
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from transformers import AutoModel, AutoProcessor

MODEL_NAME = "google/siglip2-base-patch16-256"
DATA_DIR = Path("test_shoes_shirts")
LABELS_CSV = DATA_DIR / "labels.csv"
CACHE_EMBEDDINGS_PATH = DATA_DIR / "image_embeddings.pt"

# Classes mapping
CLASSES = ["giay", "ao_thun", "ao_somi"]
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASSES)}
IDX_TO_CLASS = {i: c for i, c in enumerate(CLASSES)}

# Enhanced prompt engineering tailored for SigLIP 2 zero-shot classification
CLASS_PROMPTS = {
    "giay": [
        "a pair of shoes",
        "sports shoes, sneakers, sandals or formal leather shoes",
        "footwear",
    ],
    "ao_thun": [
        "a casual t-shirt",
        "a cotton round-neck t-shirt",
        "a short sleeve graphic or plain tee",
    ],
    "ao_somi": [
        "a button-up dress shirt",
        "a collared formal shirt with buttons",
        "a button-down long sleeve or short sleeve shirt",
    ],
}


def load_dataset():
    """Load items from labels.csv and verify image files exist."""
    items = []
    with open(LABELS_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            img_id = row["id"]
            nhom = row["nhom"].strip()
            article_type = row.get("articleType", "")
            mau = row.get("mau", "")

            img_path = DATA_DIR / nhom / f"{img_id}.jpg"
            if not img_path.is_file():
                candidates = list(DATA_DIR.glob(f"**/{img_id}.jpg"))
                if candidates:
                    img_path = candidates[0]
                else:
                    print(f"Warning: Image file not found for ID {img_id} in {nhom}")
                    continue

            items.append({
                "id": img_id,
                "nhom": nhom,
                "class_idx": CLASS_TO_IDX[nhom],
                "article_type": article_type,
                "mau": mau,
                "path": img_path,
            })
    return items


def extract_features(output):
    """Support Tensor and ModelOutput return forms across Transformers versions."""
    if isinstance(output, torch.Tensor):
        tensor = output
    elif getattr(output, "pooler_output", None) is not None:
        tensor = output.pooler_output
    elif isinstance(output, (tuple, list)):
        candidates = [item for item in output if isinstance(item, torch.Tensor)]
        tensor = [item for item in candidates if item.ndim == 2][-1]
    else:
        tensor = output
    return F.normalize(tensor.float(), p=2, dim=-1)


def main():
    print("=" * 70)
    print("  EVALUATION SUITE: SigLIP 2 on test_shoes_shirts Dataset")
    print(f"  Model: {MODEL_NAME}")
    print("=" * 70, flush=True)

    dataset = load_dataset()
    total_samples = len(dataset)
    print(f"Loaded {total_samples} samples from {LABELS_CSV}", flush=True)
    for c in CLASSES:
        count = sum(1 for d in dataset if d["nhom"] == c)
        print(f"  - Class '{c}': {count} images", flush=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Check if image embeddings are already cached
    all_image_embeddings = None
    if CACHE_EMBEDDINGS_PATH.is_file():
        try:
            cached_data = torch.load(CACHE_EMBEDDINGS_PATH, map_location="cpu", weights_only=True)
            if cached_data.shape[0] == total_samples and cached_data.shape[1] == 768:
                all_image_embeddings = cached_data
                print(f"\n[CACHE HIT] Loaded precomputed image embeddings from {CACHE_EMBEDDINGS_PATH}", flush=True)
        except Exception as e:
            print(f"Could not load cache: {e}", flush=True)

    print("\nLoading processor and model...", flush=True)
    t0 = time.time()
    processor = AutoProcessor.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME)
    model.eval()
    model.to(device)
    print(f"Model loaded in {time.time() - t0:.2f}s on {device}", flush=True)

    # 1. Encode Class Text Prompts
    print("\nEncoding class text prompts...", flush=True)
    class_text_embeddings = []
    with torch.no_grad():
        for c in CLASSES:
            prompts = CLASS_PROMPTS[c]
            inputs = processor(text=prompts, padding="max_length", max_length=64, return_tensors="pt").to(device)
            feat = model.get_text_features(**inputs)
            norm_feat = extract_features(feat)
            avg_emb = F.normalize(norm_feat.mean(dim=0, keepdim=True), p=2, dim=-1)
            class_text_embeddings.append(avg_emb)

    class_text_embeddings = torch.cat(class_text_embeddings, dim=0).cpu()  # Shape: (3, 768)

    # 2. Encode Images if not cached
    if all_image_embeddings is None:
        print(f"\nEncoding {total_samples} test images (batch_size=32)...", flush=True)
        batch_size = 32
        embeddings_list = []
        t_start = time.time()

        for i in range(0, total_samples, batch_size):
            batch_items = dataset[i : i + batch_size]
            images = []
            for item in batch_items:
                try:
                    img = Image.open(item["path"]).convert("RGB")
                    images.append(img)
                except Exception as e:
                    print(f"Error loading {item['path']}: {e}", flush=True)
                    images.append(Image.new("RGB", (256, 256), color="black"))

            inputs = processor(images=images, return_tensors="pt").to(device)
            with torch.no_grad():
                feat = model.get_image_features(**inputs)
                norm_feat = extract_features(feat)
                embeddings_list.append(norm_feat.cpu())

            print(f"  Processed {min(i + batch_size, total_samples)}/{total_samples} images...", flush=True)

        print(f"Image feature extraction completed in {time.time() - t_start:.2f}s.", flush=True)
        all_image_embeddings = torch.cat(embeddings_list, dim=0)
        torch.save(all_image_embeddings, CACHE_EMBEDDINGS_PATH)
        print(f"Saved cached embeddings to {CACHE_EMBEDDINGS_PATH}", flush=True)

    # 3. Compute Similarity Logits & Probabilities for Zero-Shot Classification
    similarity = torch.matmul(all_image_embeddings, class_text_embeddings.T)

    # SigLIP logit scale
    temperature = 0.07
    logits = similarity / temperature
    probabilities = F.softmax(logits, dim=-1).numpy()
    predictions = np.argmax(probabilities, axis=1)
    ground_truth = np.array([d["class_idx"] for d in dataset])

    # 4. Calculate Classification Metrics
    accuracy = accuracy_score(ground_truth, predictions)
    report = classification_report(
        ground_truth,
        predictions,
        target_names=CLASSES,
        output_dict=True,
        zero_division=0,
    )
    conf_matrix = confusion_matrix(ground_truth, predictions)

    # 5. Calculate Multi-class ROC-AUC (One-vs-Rest)
    y_true_onehot = np.zeros((total_samples, len(CLASSES)))
    for idx, c in enumerate(ground_truth):
        y_true_onehot[idx, c] = 1

    ovr_auc_scores = {}
    for i, c in enumerate(CLASSES):
        auc = roc_auc_score(y_true_onehot[:, i], probabilities[:, i])
        ovr_auc_scores[c] = float(auc)

    macro_auc = float(roc_auc_score(y_true_onehot, probabilities, multi_class="ovr", average="macro"))
    weighted_auc = float(roc_auc_score(y_true_onehot, probabilities, multi_class="ovr", average="weighted"))

    # 6. Calculate Content-Based Image Retrieval (CBIR) Metrics
    print("\nComputing Content-Based Image Retrieval (CBIR) metrics...", flush=True)
    pairwise_sim = torch.matmul(all_image_embeddings, all_image_embeddings.T).numpy()
    np.fill_diagonal(pairwise_sim, -np.inf)

    top1_correct = 0
    top5_correct = 0
    precisions_at_5 = []
    ap_scores = []

    for idx in range(total_samples):
        query_class = ground_truth[idx]
        sorted_indices = np.argsort(-pairwise_sim[idx])
        sorted_other_indices = sorted_indices[:-1]  # drop self-match (599 samples)

        # Top-1 check
        if ground_truth[sorted_other_indices[0]] == query_class:
            top1_correct += 1

        # Top-5 check
        top5_classes = ground_truth[sorted_other_indices[:5]]
        if query_class in top5_classes:
            top5_correct += 1

        precisions_at_5.append(np.mean(top5_classes == query_class))

        # Average Precision (AP)
        relevant_mask = (ground_truth[sorted_other_indices] == query_class)
        ranks = np.arange(1, total_samples)  # 1 to 599
        cumulative_hits = np.cumsum(relevant_mask)
        precision_at_k = cumulative_hits / ranks
        ap = np.sum(precision_at_k * relevant_mask) / np.sum(relevant_mask)
        ap_scores.append(ap)

    retrieval_top1 = float(top1_correct / total_samples)
    retrieval_top5 = float(top5_correct / total_samples)
    mAP = float(np.mean(ap_scores))
    p_at_5 = float(np.mean(precisions_at_5))

    # Output Results
    print("\n" + "=" * 70, flush=True)
    print("                    EVALUATION RESULTS SUMMARY", flush=True)
    print("=" * 70, flush=True)
    print(f"Total Test Samples          : {total_samples}", flush=True)
    print(f"Overall Accuracy            : {accuracy * 100:.2f}% ({accuracy:.4f})", flush=True)
    print(f"Macro-average ROC-AUC       : {macro_auc:.4f}", flush=True)
    print(f"Weighted ROC-AUC            : {weighted_auc:.4f}", flush=True)
    print("-" * 70, flush=True)
    print("Per-Class Classification Metrics:", flush=True)
    for c in CLASSES:
        prec = report[c]["precision"]
        rec = report[c]["recall"]
        f1 = report[c]["f1-score"]
        auc = ovr_auc_scores[c]
        print(f"  [{c.upper():<7}] Precision: {prec * 100:.2f}% | Recall: {rec * 100:.2f}% | F1: {f1 * 100:.2f}% | AUC: {auc:.4f}", flush=True)

    print("-" * 70, flush=True)
    print("Confusion Matrix (Rows: True Class, Columns: Predicted Class):", flush=True)
    print(f"{'':>12} {'GIAY':>10} {'AO_THUN':>10} {'AO_SOMI':>10}", flush=True)
    for i, c in enumerate(CLASSES):
        print(f"{c.upper():>12} {conf_matrix[i, 0]:>10} {conf_matrix[i, 1]:>10} {conf_matrix[i, 2]:>10}", flush=True)

    print("-" * 70, flush=True)
    print("Image-to-Image Visual Retrieval (CBIR) Performance:", flush=True)
    print(f"  Recall@1 (Top-1 Accuracy)   : {retrieval_top1 * 100:.2f}%", flush=True)
    print(f"  Recall@5 (Top-5 Hit Rate)   : {retrieval_top5 * 100:.2f}%", flush=True)
    print(f"  Precision@5                 : {p_at_5 * 100:.2f}%", flush=True)
    print(f"  Mean Average Precision (mAP): {mAP * 100:.2f}%", flush=True)
    print("=" * 70, flush=True)

    # Save results as JSON
    results_json_path = DATA_DIR / "eval_results.json"
    results_data = {
        "model": MODEL_NAME,
        "total_samples": total_samples,
        "overall_accuracy": accuracy,
        "macro_auc": macro_auc,
        "weighted_auc": weighted_auc,
        "per_class_auc": ovr_auc_scores,
        "classification_report": report,
        "confusion_matrix": conf_matrix.tolist(),
        "retrieval": {
            "top1_accuracy": retrieval_top1,
            "top5_accuracy": retrieval_top5,
            "precision_at_5": p_at_5,
            "mean_average_precision": mAP,
        },
    }
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2, ensure_ascii=False)

    print(f"\nSaved raw evaluation data to {results_json_path}", flush=True)


if __name__ == "__main__":
    main()
