"""Reproduce the ML metrics included in reports/."""
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.ml import CampusClassifier, read_labeled  # noqa: E402


def main():
    model = CampusClassifier()
    result = {"model": "TF-IDF + balanced multinomial logistic regression",
              "evaluation_set": "Separately authored synthetic English issue descriptions",
              "data_provenance": "Authored examples in data/train.csv and data/holdout.csv; NOT real institution data",
              **model.metrics}
    path = ROOT / 'reports' / 'model_evaluation.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
