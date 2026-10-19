# CampusRelay AI — Intelligent Campus Issue Desk

**Working full-stack project · professional responsive interface · AI/ML · secure authentication · SQLite · documented REST API**

**UI update (October 2026):** Version **3** adds a premium dark-navy navigation frame, softer tinted dashboard, gradient action banners, subtle card depth and accessible micro-animations while retaining the tested workflows. See [`docs/V3_VISUAL_POLISH.md`](docs/V3_VISUAL_POLISH.md) and `docs/screenshots/*_v3.png`. Backend APIs, security and ML model remain unchanged.

CampusRelay AI solves a practical operational problem: students report broken facilities, campus IT outages, safety hazards, academic service issues and bus delays through a single portal, but routing and progress updates are often scattered. CampusRelay provides one place to **report, triage, assign, track, and resolve** campus issues.

The application is designed for **live technical review**: it starts locally with fictional seeded tickets, role-based demo accounts, an interactive dashboard, a trained text classifier, filters, real CRUD-like ticket workflows, comments, audit events, and an exported CSV for administrators. No API key or paid AI service is required.

> **Submission status:** Source, environment example, tests, model evaluation, and deployment configuration are included. A public deployment URL and GitHub repository link cannot be prefilled: the submitter must create/push a GitHub repository and deploy under their own account. No score or publication outcome is guaranteed.

## 1. Quick start (Windows / Linux / macOS)

**Requirements:** Python 3.11+ (prefer 3.12), internet access for first-time dependency installation. Free to run afterward.

**Windows — easiest:** Double-click `run.bat`, wait for packages to install, then open **http://127.0.0.1:8000**. The command window must remain open.

**macOS / Linux — easiest:**

```bash
chmod +x run.sh
./run.sh
```

**Manual cross-platform setup:**

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
# Windows: copy .env.example .env
# macOS/Linux: cp .env.example .env
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Launch **http://127.0.0.1:8000**. The first startup trains the model from the included CSV, creates the SQLite schema, and populates 24 fictional example reports **only when demo data is enabled and the database has no users**. Subsequent runs retain local changes in `instance/campusrelay.db`.

**API docs:** http://127.0.0.1:8000/docs · **Health:** http://127.0.0.1:8000/health

### Fictional demo credentials

| Access | Email | Password | Demonstrate |
|---|---|---|---|
| Student | `student@campusrelay.demo` | `Student@2026!` | Own-ticket privacy, new issue, comments, AI, status tracking |
| Staff | `staff@campusrelay.demo` | `Staff@2026!` | All tickets, assignment, status transitions, analytics, CSV export |
| Administrator | `admin@campusrelay.demo` | `Admin@2026!` | Administrator access to staff workflows |

The sign-in page also provides **one-click demo logins** when `ENABLE_DEMO_DATA=true`. An additional fictional student (`mina@campusrelay.demo`) owns some seeded reports to illustrate privacy boundaries. **Never deploy demo credentials for a real university or put real user data into a public demonstration.**

## 2. Features implemented

| Area | What's genuinely implemented |
|---|---|
| Responsive frontend | Reworked desktop/tablet/mobile layouts, editorial sign-in, accessible navigation & modal, real-data dashboard, issue directory, readable charts, status labels, search, filters and AI recommendations |
| Authentication | PBKDF2-hashed passwords with unique salts, opaque server-side sessions with HttpOnly cookies, 12-hour session timeout, logout, student self-registration |
| Authorization | Student sees only own reports, staff/admin see all; server-controlled assignment, transitions, CSV export, signed-in AI endpoints |
| Database and APIs | Parameterized SQLite queries, schema constraints, foreign keys, indexes, create/list/read tickets, status/assignment updates, comments, metrics and CSV export |
| Business workflow | **Open → In Progress → Resolved → Reopened → In Progress**; unauthorized/illegal transitions rejected; every change audit logged |
| AI / ML | Text classification into **Facilities, IT, Safety, Academic, Transport** with **TF-IDF + logistic regression**; probabilities, low-confidence warning, alternatives, explainable priority policy and manual overrides |
| Evaluation | 380 labeled synthetic training texts, **50 separately authored synthetic holdout examples**; measured **92% accuracy / 0.9165 macro-F1**. These are not real-world performance claims |
| Quality | 25 automated unit + API integration + frontend asset-contract tests, deterministic AI evaluation, GitHub Actions workflow, Docker deployment, architecture/security docs, reviewer demo script |

## 3. How to demonstrate in ~5 minutes

1. **Log in as Student.** Open the Overview and Issue tracker. Student sees only own reports. Click **Report an issue**.
2. Title: `Wi-Fi unavailable in Lecture Room 306`; description: `The campus wireless internet keeps disconnecting and students cannot open their assignments during class.`; location: `Academic Block A, Room 306`.
3. Click **Suggest category & priority**. Explain the model probability, keyword policy and manual override fields. Set category to **IT** and priority to **Medium**, then submit.
4. Open the newly created issue and add a comment. Show saved event history.
5. **Sign out**, then **sign in as Staff**. Find the ticket through Search; assign a staff member; change **Open → In Progress → Resolved**. Show transition validation when skipping stages.
6. View Insights and download staff-only CSV. Show `/docs`, the model report, and the automated tests.

Expanded instructions: [`docs/LIVE_REVIEW.md`](docs/LIVE_REVIEW.md).

## 4. Run automated tests and reproduce the ML evaluation

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python scripts/evaluate_model.py
python scripts/smoke_test.py http://127.0.0.1:8000
node --check static/app.js  # optional: Node.js installed
```

Verified in the authoring environment: **25 tests passing** and evaluation generated in [`reports/model_evaluation.json`](reports/model_evaluation.json). Smoke testing checks the read-only routes of a running application.

> **Evaluation limitation:** 92% is the result of a held-out but **synthetic** English sample from a similar authored domain. The safety class's holdout recall is **70%**, so the tool is unsuitable for unattended safety triage. All safety emergencies should be escalated to campus emergency services independently of this prototype.

## 5. API overview

All API endpoints live under `/api/`. FastAPI exposes request/response schemas at `/docs` and `/openapi.json`.

| Method | Endpoint | Permissions |
|---|---|---|
| POST | `/api/auth/register`, `/api/auth/login` | Public, validated JSON, origin checked |
| GET | `/api/auth/me` | Signed in |
| POST | `/api/auth/logout` | Signed in + CSRF |
| GET | `/api/meta` | Public |
| POST | `/api/ai/suggest` | Signed in + CSRF |
| GET | `/api/ai/model-card` | Signed in |
| GET | `/api/dashboard` | Signed in; per-role scope |
| GET, POST | `/api/tickets` | Signed in (POST requires CSRF) |
| GET | `/api/tickets/{id}` | Ticket owner or staff/admin |
| PATCH | `/api/tickets/{id}/status` | Staff/admin + CSRF + transition checks |
| PATCH | `/api/tickets/{id}/assignee` | Staff/admin + CSRF + role validation |
| POST | `/api/tickets/{id}/comments` | Ticket owner or staff/admin + CSRF |
| GET | `/api/users/assignees` | Staff/admin |
| GET | `/api/export/tickets.csv` | Staff/admin; formula injection protected |

Browser clients receive a per-session CSRF token in the login or `/api/auth/me` response. Set `X-CSRF-Token` on all authenticated POST/PATCH operations. JSON mutations additionally check the `Origin` header and `Content-Type: application/json`.

## 6. Deployment and Git submission

- **GitHub:** follow [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) to initialize/push the complete source and collect meaningful commit history. **Do not add `.env`, `instance/`, or credentials**; these are in `.gitignore`.
- **Render:** deploy with the included `render.yaml` Blueprint (`Dockerfile`), then copy the HTTPS URL into your submission. The free instance uses **ephemeral SQLite**; records may reset on restart/redeploy. For actual deployments, use a persistent disk or migrate the database to managed PostgreSQL. Details in the deployment guide.
- **Security:** `APP_ENV=production`, `COOKIE_SECURE=true`, `ENABLE_DEMO_DATA=false` (except a fictional evaluator demo), configure your actual domains, and create an admin account securely.
- **GitHub Actions:** automatically runs tests, evaluation and JS syntax checking on push/pull request.

## 7. Architecture

```text
Browser (HTML + CSS + vanilla JS)
  |  HTTPS + SameSite/HttpOnly session + CSRF on writes
  v
FastAPI routes (validation, role/owner enforcement, workflows)
  |                                |
  v                                v
SQLite relational DB             TF-IDF + Logistic Regression
(users, sessions, tickets,      (data/train.csv, model evaluated
 events, login attempts)         against data/holdout.csv)
```

Data model, route design and reliability tradeoffs: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). Security controls and limitations: [`docs/SECURITY.md`](docs/SECURITY.md). Model design and analysis: [`docs/AI_MODEL_CARD.md`](docs/AI_MODEL_CARD.md).

## 8. Files and recommended submission

Submit **your GitHub repository URL**, **your deployment URL** (or demonstrate locally if unavailable), and a short summary. A separate ZIP of this source is useful as an extra attachment only if your evaluator accepts it. Keep these files:

```text
app/                    Back end, security, database, AI and example data loader
static/                 Polished responsive frontend (HTML, CSS, JS, SVG)
data/                   Labeled training and separate holdout CSV files
scripts/                Evaluation, seed generator, admin CLI and smoke test
reports/                Reproducible AI evaluation JSON
 tests/                  21 automated tests
 docs/                   Design, security, deployment, review, rubric coverage
.github/workflows/      Continuous integration
.env.example            Environment variable template (no real secrets)
Dockerfile, render.yaml Deployment
run.bat, run.sh          Quick-start helpers
requirements*.txt       Runtime and test dependencies
README.md               This guide
```

**Known limitations:** no email notifications or uploads, SQLite suited to a single small deployment, free hosting storage is ephemeral, no real institution dataset, English-only synthetic ML evaluation, login throttling is per SQLite database, and real-browser visual QA was not completed in the authoring environment (browser access was blocked). These are deliberate scope boundaries, not hidden features.

## 9. Project attribution

This codebase was generated with AI assistance and should be **read, understood, tested and explained by the submitting team**. If the course has an AI-use disclosure requirement, disclose assistance honestly. All ticket data in the demo is fictional.

**License:** MIT. See [`LICENSE`](LICENSE).
