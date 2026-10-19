# Submission — read this before sending

**App:** CampusRelay AI — Intelligent Campus Issue Desk

**Frontend update:** A professional light-theme interface with new login, dashboard, request directory, analytics, AI triage, responsive navigation, dialog interactions, and screenshots. Review `docs/FRONTEND_REDESIGN.md`.

**Status:** Local source complete. Tests passed (25/25). Trained text ML feature included; synthetic holdout accuracy 92%, macro-F1 0.9165.

**What to send to the instructor:**

1. **GitHub repository URL** of this project after you push the included Git history.
2. **Working deployment URL** after you personally deploy and verify it; if you cannot host it, demonstrate locally (the assignment allows this).
3. Short description: “CampusRelay AI is a responsive full-stack campus issue management application with student/staff/admin authorization, SQLite CRUD workflows, activity history, analytics, and a real supervised ML-based routing recommendation with a transparent manual override.”
4. **Optional extra attachment:** source ZIP if allowed. `.env.example`, README, tests, AI evaluation and reviewer guide are all included.

**Before submission (essential):**

- Make an empty GitHub repository, then push this local repository into it (`docs/DEPLOYMENT.md`).
- Ensure Github Actions completes successfully and paste that repository URL.
- If deploying, open your actual HTTPS URL and verify a demo login and full ticket flow. Do not write a placeholder URL in the final submission.
- Do **not** upload a personal `.env` or real password, or the local SQLite DB.
- Practice the 5-minute demonstration described in `docs/LIVE_REVIEW.md`.

**Local start on Windows:** Extract → double-click `run.bat` → open http://127.0.0.1:8000 → choose Staff demo or Student demo.

**IMPORTANT:** 100/100 is the maximum in the rubric, not a guaranteed result. Assessment depends on your live explanation, actual deployment/repository evidence and evaluator judgment. The project was created with AI assistance: comply with any university AI-use policy.

## V3 visual update
The October V3 build adds a navy navigation frame, soft colored dashboard cards and measured transitions. See `docs/V3_VISUAL_POLISH.md` and the files named `*_v3.png` in `docs/screenshots/`. Backend behavior remains unchanged.
