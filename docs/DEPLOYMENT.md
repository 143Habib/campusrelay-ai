# GitHub, deployment and review submission

## 1. Push the complete code into your own GitHub repository

Inside the extracted `CampusRelay_AI` directory, run (Git installed):

```bash
git status
# This ZIP includes a local Git history. Set YOUR real name/email for future commits.
git config user.name "YOUR NAME"
git config user.email "your-github-email@example.com"
# Check tracked files; secret files must not appear.
git ls-files
# If you're using a package without .git, start: git init -b main
# Then: git add . && git commit -m "Initial complete campus issue desk"
git remote add origin https://github.com/YOUR_USERNAME/campusrelay-ai.git
git branch -M main
git push -u origin main
```

Create an empty GitHub repository named `campusrelay-ai` **without initializing it with a separate README**, then run the remote/push commands. If `origin` already exists, use `git remote set-url origin ...`. You may use GitHub Desktop rather than commands. Before pushing, run `git status`, `git ls-files` and ensure `.env`, tokens and databases are not included. The ZIP's `.git` contains a logical history of changes; future work should be committed with your own configured identity.

GitHub Actions `.github/workflows/ci.yml` starts on push and checks unit/API integration tests, ML evaluation and JS syntax. Submit a GitHub repo link, **not a local filesystem link**.

## 2. Deploy on Render (Blueprint)

1. Sign in to [render.com](https://render.com/) and authorize access to your new GitHub repository.
2. Choose **New → Blueprint**, select this repository and use the included `render.yaml`.
3. Confirm the web service; it builds the provided `Dockerfile`, serves the UI + API and exposes `/health`.
4. Wait for the deployment to become live; visit `https://YOUR-SERVICE.onrender.com/health`, then the root URL.
5. Log in with a demo account and test ticket creation, AI suggestion, assignment and logout on the live HTTPS domain.
6. Set `ALLOWED_ORIGINS` to the exact deployed `https://YOUR-SERVICE.onrender.com` origin if your reverse proxy does not consistently pass scheme/host headers. Optional `TRUSTED_HOSTS=YOUR-SERVICE.onrender.com` restricts Host headers. **Never use arbitrary wildcard origins in production.**

**Free-hosting caveat:** Render free services have ephemeral filesystem storage. The deployed SQLite DB initially seeds fictional reports, but ticket changes, accounts and comments can disappear on restart/redeploy, and sleeping free services may take time to wake. That is acceptable as a transparent *temporary class demo*, not as durable production storage. For persistence, provision a Render service with a persistent disk mounted at `/app/instance` (paid tier) or migrate database code to managed PostgreSQL. The code is explicitly a SQLite implementation: migrating requires modifying connection/query logic; merely setting a Postgres environment variable is not sufficient.

**Do not publish a fake deployment link.** Only paste the actual link after opening it and verifying it works.

## 3. Run with Docker (alternative)

```bash
docker build -t campusrelay-ai .
docker run --rm -p 8000:8000 \
  -e ENABLE_DEMO_DATA=true \
  -e APP_ENV=development \
  -e COOKIE_SECURE=false \
  -v campusrelay_db:/app/instance \
  campusrelay-ai
```

Visit http://localhost:8000. The named Docker volume persists the DB locally. For HTTPS hosting set production cookie security back to true.

Windows PowerShell: the multiline backslash syntax above is for a Unix shell; run on one line or use PowerShell backticks for line continuation.

## 4. Deploy without Render

Any Docker host that supports Python 3.12 and a writable SQLite directory can run the service with persistent storage. Ensure HTTPS, bind to the platform's assigned `$PORT`, configure `APP_ENV`, cookie security, database volume, and allowed host/origin. Avoid serverless functions with ephemeral SQLite writes unless using a compatible external persistent database.

## 5. Submission checklist

- [ ] GitHub public or reviewer-accessible repository URL copied
- [ ] Main branch contains app, static UI, data, tests, documentation, `.env.example`, CI, Docker and Render configuration
- [ ] GitHub Actions tests are green
- [ ] Demo credentials confirmed, or private setup instructions provided
- [ ] Actual live HTTPS URL opens and works, OR be ready to run locally in front of evaluator
- [ ] Tests and ML evaluation command verified (`python -m pytest -q`, `python scripts/evaluate_model.py`)
- [ ] All source, model limitations and workflow decisions understood by submitter
- [ ] No real secrets, customer data or institutional records uploaded

## 6. Troubleshooting

| Problem | Cause / fix |
|---|---|
| `ModuleNotFoundError: fastapi` | Activate venv and run `python -m pip install -r requirements.txt` |
| Port 8000 already in use | Stop old server or run `python -m uvicorn app.main:app --port 8010` |
| Browser says `403 Untrusted request origin` | Verify your deployment HTTPS host and configure exact `ALLOWED_ORIGINS` |
| Browser login immediately loops | Make sure `COOKIE_SECURE=true` on HTTPS; use false only on HTTP local dev |
| Demo accounts don't work | `ENABLE_DEMO_DATA=true` only seeds an empty DB. Use a fresh demo database/volume, or create accounts explicitly. Don't delete genuine data. |
| Data resets after deploying | Render free SQLite storage is ephemeral; upgrade to volume or managed database for persistence |
| `pip install` fails | Check Python version (3.11–3.13) and connectivity; use 3.12 as in Docker |
| AI confidence is low | Small synthetic training set; correct the category/priority manually; see model card |

These are documented steps, not a claim that a public deployment has already been made.
