# CampusRelay AI — V3 visual polish

Updated: 19 October 2026. This update is a **visual-only enhancement** of the existing V2 frontend. APIs, validation, authorization, data model, ML classifier and business workflow were not changed.

## Design decisions

- **Dark navy navigation** creates an unmistakable workspace frame without darkening the content area. Navigation hover slides a few pixels and the active route has a restrained violet-blue selection stripe.
- **Soft tinted page canvas** replaces pure white. Dashboard summary cards have four understated individual tints and slim color rails; activity panels stay highly readable.
- **Action banner** has a solid navy-to-cobalt gradient with white text to draw attention to the next meaningful task.
- **Subtle material depth:** soft card shadows, rounded corners, translucent sticky header, precise focus rings and small elevation changes on hover.
- **Sign-in:** calm bright form side paired with a dark indigo product-preview side. The floating preview moves five pixels over seven seconds, and the motion is removed when the system requests reduced motion.
- **Motion:** one-time page-content and card entrance transitions, restrained buttons and modal transitions, and chart fill animation. No extra javascript library or external CDN.
- **Accessibility and stability:** preserves keyboard-first controls, visible focus indicators and reduced-motion handling; animations do not convey essential information. CSS-only enhancements work with the existing functional JS.

## Verified here

- `python -m pytest -q`: **25 passed**.
- `node --check static/app.js`: passed.
- Isolated Chromium *mocked-data* previews at **1440 × 900**, **900 × 850**, and **390 × 844**: no page JavaScript errors, no page-level horizontal overflow.
- Preview screenshots: `docs/screenshots/desktop_dashboard_v3.png`, `desktop_login_v3.png`, `mobile_dashboard_v3.png`, `mobile_login_v3.png`, `tablet_dashboard_v3.png`.

**Scope:** Chromium preview injects the shipped HTML/CSS/JS and supplies responses copied from the local API through a mock fetch. It validates visual layout and runtime JS execution but **is not** a real HTTPS or browser-to-server end-to-end test. Deployment, real-device browsers, loading behavior under weak mobile internet, and live login workflow still require checks on the submitter's environment.

## How to run

From the project folder on Windows, double-click `run.bat`. On macOS/Linux, run `./run.sh`. Open `http://127.0.0.1:8000` in a browser and use the demo-account choices on the sign-in page. Check the live review guide at `docs/LIVE_REVIEW.md`.

To avoid a cached V2 stylesheet after replacing a running app, use **Ctrl+Shift+R** once in the browser.
