# Live technical review playbook (5–8 minutes)

**Before the presentation:** start the server with `run.bat`/`run.sh` or use your verified HTTPS deployment. Open `http://localhost:8000`, `/docs`, `/health`, and the repository's GitHub Actions page in separate tabs. Ensure the demo environment is enabled. Test the connections ahead of time.

## Demonstration script

| Time | Show and do | Technical talking points |
|---|---|---|
| 00:00–00:35 | Describe campus issue-reporting fragmentation. Login as Student via demo button. | Real operational problem, roles, protected sessions. |
| 00:35–01:15 | Visit Overview, Issue tracker, search and filter; explain why only some records appear. | API scopes student records by creator ID. Dashboard counts come from SQLite. |
| 01:15–02:25 | Report an issue: `Wi-Fi unavailable in Room 306`; explain problem text and location; click **Suggest**; show alternatives and low-confidence label; manually set IT + Medium. Submit. | Scikit-learn TF-IDF + logistic regression; priority via separate transparent rules. Final choices are human controlled; model predictions separately stored. |
| 02:25–03:10 | Open the created report. Add a comment and show timeline, AI metadata, and reference. | Transactions and audit trail; creation/event recorded atomically. |
| 03:10–04:25 | Sign out, login as Staff; open all issues, find newly reported ticket, assign to staff, move `Open → In Progress → Resolved`. | Staff authorization; transition graph and invalid jump rejected with 409. |
| 04:25–05:10 | View Insights, category bars, resolution charts, CSV export, and AI assistant's model report. | Aggregated SQL, safe CSV, validation, measured evaluation. |
| 05:10–06:00 | Open `/docs`; show `app/main.py`, `app/database.py`, `app/auth.py` and tests. Run `python -m pytest -q`. | Modular design, input validation, FK/indexes, PBKDF2, CSRF, role scoping, continuous integration. |
| 06:00–07:00 | Open `docs/AI_MODEL_CARD.md` and `reports/model_evaluation.json`; show exact metrics and limitations. | Synthetic 50-example holdout, 92% overall accuracy but 70% safety recall. No autonomous safety decisions. |

## Prepare for evaluator changes

- **Change request — add a new status:** update DB `CHECK` constraint/migration, schema type, `STATUSES`, `TRANSITIONS`, UI filters, and tests. Explain why migrations matter for existing DBs.
- **Change request — tighten password policy:** edit `schemas.Register` validation and add test cases. Existing hashes remain valid.
- **Change request — add a category:** update `CATEGORIES`, label data, SQL enum check, schema type, UI choices, retrain and re-evaluate the model. Explain that adding labels is not a frontend-only change.
- **Change request — allow a student to resolve a ticket:** point to `require_staff` and discuss why the product intentionally prohibits it. It can be changed but requires a policy decision, not simply removing a button.
- **Debugging task — forbidden access:** reproduce a 403 with student login and staff-only endpoints; show test and backend guard. Explain 401 vs 403 vs 404.

## Sample technical questions with concise answers

**How is it full-stack?** FastAPI serves a responsive SPA-like JavaScript client and REST routes; all issue/user/session/event data are stored in normalized SQLite tables. Routes implement a workflow with actual business rules, not just static mockups.

**What makes the AI real?** Scikit-learn trains a statistical supervised multiclass text classifier using TF-IDF features and logistic regression. It returns model probabilities and alternatives. The urgency policy is intentionally rule-based and is labeled accordingly.

**How did you evaluate it?** Separate authored holdout CSV never used to fit the model; measured accuracy, macro-F1 and per-class confusion matrix. Limitation: both splits are synthetic, and safety recall is just 70% on the sample.

**How do you protect student records?** The session identifies a user from the server-side token store; every route and aggregate scopes by role/creator. We test access to another student's ticket, comments and staff-only operations.

**How do you prevent invalid actions?** Pydantic schema constraints, SQL foreign keys/`CHECK`, CSRF tokens, staff checks, legal transition mapping, and atomic writes with event logging.

**How do you deploy it?** Docker with Uvicorn, persistent SQLite volume for durable usage, or Render Blueprint for temporary demo. Free Render disk is ephemeral. The app has a `/health` readiness probe and no third-party AI keys.

**Why SQLite and not Postgres?** Faster, self-contained evaluator setup and full CRUD integrity; a real multi-instance institution should use managed Postgres, centralized secrets and backups after proper migration.

**Can we trust 92%?** Only for the supplied synthetic holdout; not a measured campus deployment score. Human checks and escalation are mandatory.

**Did you test on phones?** Styles include small-screen layouts and keyboard-accessible controls; a genuine device/browser QA pass remains a preproduction task. Unit/API integration tests and JavaScript syntax were checked; browser visual verification was blocked in the authoring environment.
