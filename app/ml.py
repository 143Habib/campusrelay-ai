"""Explainable TF-IDF + multinomial logistic regression for issue routing.

Only synthetic authored training and holdout examples are provided. Accuracy on
these examples is NOT an estimate of deployment performance on real complaints.
"""
import csv
from collections import Counter
from pathlib import Path
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent.parent
CATEGORIES = ("Facilities", "IT", "Safety", "Academic", "Transport")

PRIORITY_RULES = {
    "High": ["fire", "smoke", "sparking", "electrocution", "gas leak", "chemical spill", "exposed wire", "electric shock", "emergency exit", "injury", "violent", "threaten", "dangerous", "unsafe", "stolen", "stealing", "theft", "threatens", "leaking gas", "urgent", "immediately", "broken glass", "locked emergency"],
    "Medium": ["broken", "leak", "fails", "failed", "error", "offline", "blocked", "late", "missing", "jammed", "cannot", "not working", "stopped", "damaged", "delay", "crash", "out of service"],
}


def read_labeled(path: Path) -> tuple[list[str], list[str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows or any(not x.get("text") or x.get("category") not in CATEGORIES for x in rows):
        raise ValueError(f"Invalid or empty labeled data: {path}")
    return [r["text"] for r in rows], [r["category"] for r in rows]


class CampusClassifier:
    def __init__(self, root: Path = ROOT):
        self.root = Path(root)
        train_x, train_y = read_labeled(self.root / "data" / "train.csv")
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True,
                                      strip_accents="unicode", min_df=1, stop_words="english", max_features=20000)),
            ("model", LogisticRegression(max_iter=1200, random_state=42, class_weight="balanced")),
        ])
        self.pipeline.fit(train_x, train_y)
        self.training_size = len(train_x)
        self.metrics = self.evaluate()

    def evaluate(self):
        x, y = read_labeled(self.root / "data" / "holdout.csv")
        pred = self.pipeline.predict(x)
        return {
            "train_examples": self.training_size,
            "holdout_examples": len(x),
            "accuracy": round(float(accuracy_score(y, pred)), 4),
            "macro_f1": round(float(f1_score(y, pred, average="macro", zero_division=0)), 4),
            "labels": list(CATEGORIES),
            "confusion_matrix": confusion_matrix(y, pred, labels=CATEGORIES).tolist(),
            "per_class": {
                key: {metric: round(float(value), 4) if isinstance(value, (float, int)) else value
                      for metric, value in report[key].items()}
                for key in CATEGORIES
            } if (report := classification_report(y, pred, labels=CATEGORIES, output_dict=True, zero_division=0)) else {},
            "limitations": "Synthetic, related-domain examples only; not validated on real campus incidents or non-English reports.",
        }

    def suggest(self, text: str) -> dict:
        text = text.strip()
        if not text:
            raise ValueError("A description is required")
        probabilities = self.pipeline.predict_proba([text])[0]
        labels = self.pipeline.named_steps["model"].classes_
        ranked = sorted(zip(labels, probabilities), key=lambda item: item[1], reverse=True)
        category, confidence = ranked[0]
        matched_high = [x for x in PRIORITY_RULES["High"] if re.search(r"(?<!\w)" + re.escape(x) + r"(?!\w)", text.lower())]
        matched_medium = [x for x in PRIORITY_RULES["Medium"] if re.search(r"(?<!\w)" + re.escape(x) + r"(?!\w)", text.lower())]
        if matched_high:
            priority = "High"
            reason = "Priority rule matched safety/urgency indicator(s): " + ", ".join(matched_high[:3]) + "."
        elif category == "Safety":
            priority = "High"
            reason = "Safety-category issues are provisionally escalated for human review."
        elif matched_medium:
            priority = "Medium"
            reason = "Priority rule matched service-disruption indicator(s): " + ", ".join(matched_medium[:3]) + "."
        else:
            priority = "Low"
            reason = "No predefined urgent or disruptive term found; review manually."
        uncertain = confidence < 0.55
        return {
            "category": str(category),
            "confidence": round(float(confidence), 4),
            "priority": priority,
            "low_confidence": bool(uncertain),
            "alternatives": [{"category": str(label), "probability": round(float(prob), 4)} for label, prob in ranked[:3]],
            "explanation": ("Low confidence: choose the correct category yourself. " if uncertain else "Text-category model predicted the best-matching category. ") + reason,
            "model": "TF-IDF + Logistic Regression; deterministic keyword-based priority policy",
            "human_override": True,
        }
