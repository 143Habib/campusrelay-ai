# Model card — CampusRelay issue categorizer (v1)

## Task and intended users

The model suggests a **campus service team** for text descriptions of issues. It is an advisory aid for authenticated student/staff users in a prototype, **not** a safety detector, emergency responder or autonomous decision maker.

## Input and output

- **Input:** English free-text report (20–2200 characters in the API).
- **Model:** deterministic scikit-learn `TfidfVectorizer` with unigrams and bigrams, English stop-word filtering and balanced `LogisticRegression(random_state=42)`.
- **Categories:** Facilities, IT, Safety, Academic, Transport.
- **Output:** top predicted category, model probability (`confidence`), top 3 options, uncertainty flag, and explanation.
- **Priority:** **separate heuristic keyword policy**, NOT a learned classifier. High-priority emergency words and provisional Safety categorization produce High; generic disruption words Medium; otherwise Low. No assertion that this represents verified severity. Staff and reporter must review.
- **Override:** final category and priority are controlled by the human reporter. Backend recalculates and stores the AI recommendation as separate auditable metadata.

## Dataset / provenance

`data/train.csv`: **380 fictional training rows**, generated from 190 originally authored incident phrases, expanded into two similar writing contexts. `data/holdout.csv`: **50 separately authored fictional examples** (10 per category). These examples are not copied from training files, but both share author, campus domain and vocabulary. Splitting does not eliminate synthetic distribution bias. `scripts/generate_dataset.py` reconstructs these exact CSV files for transparency. No real student data was collected.

## Evaluation procedure

The model is fit on training CSV only. `python scripts/evaluate_model.py` loads the distinct holdout CSV, predicts once, computes scikit-learn accuracy, macro-averaged F1, class-level precision/recall/F1, and confusion matrix. The measured output is saved in `reports/model_evaluation.json`.

| Metric | Measured on synthetic holdout |
|---|---:|
| Training records | 380 |
| Holdout records | 50 |
| Accuracy | **0.9200** (46/50) |
| Macro F1 | **0.9165** |
| Facilities recall | 1.00 |
| IT recall | 1.00 |
| **Safety recall** | **0.70** |
| Academic recall | 1.00 |
| Transport recall | 0.90 |

Confusion matrix (rows=true; columns=predicted, in order Facilities, IT, Safety, Academic, Transport):

```text
            Facil.   IT   Safety   Academic   Transport
Facilities    10      0      0       0          0
IT             0     10      0       0          0
Safety         1      1      7       1          0
Academic       0      0      0      10          0
Transport      0      0      1       0          9
```

**Interpretation:** The sample is small and synthetic. Strong held-out metrics can overstate real-campus performance. In particular, three safety complaints were misrouted in this synthetic evaluation. The rule-based priority policy may surface hazard words even when the text classifier misroutes them, but it is not a reliable safety backstop. Humans must review all safety-relevant reports, and campus emergency services must be contacted directly for emergencies.

## Failure modes and mitigations

- Ambiguous multi-topic complaints, novel building terms, misspellings, Bangla / code-mixed language, multilingual text, sarcasm and brief phrases may fail.
- Model probabilities are not calibrated guarantees. A <55% top probability triggers a low-confidence warning; even higher probabilities may be wrong.
- Keywords may be negated ("no fire") or appear in unrelated contexts; keyword priority is simplistic.
- Synthetic data provides no demographic representativeness, and no institution-specific accuracy or fairness claims can be made.
- Keep manual override, explanation and visible alternatives. Avoid automatic high-risk decisions or invisible risk downgrading.

## Next validation iteration

Collect consented, de-identified real issues following institution policy; have two independent reviewers label each complaint; preserve a time-based institutional holdout; measure per-class safety recall and calibration, confusion matrix, multilingual performance, false negatives, auditability and drift. Obtain expert approval before real campus deployment. Never expose students' personal data in training files.
