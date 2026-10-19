# CampusRelay — frontend redesign notes (V2 baseline)

**Update:** V3 adds theme depth and animations. See `V3_VISUAL_POLISH.md` for the current look. The description below documents the original V2 direction.

## Design direction

The UI is intentionally a **practical, restrained campus service-desk interface**, rather than a marketing dashboard. The design prioritizes legibility, usable controls, and visual hierarchy. It uses near-white surfaces, cool neutral backgrounds, a muted cobalt primary action, limited semantic status colors, native system fonts, and measured spacing. No external icons, images, fonts, animations, or paid UI library is required.

The login layout has been redesigned with an editorial-style product preview using ordinary HTML/CSS (the requests shown there are *illustrative*, not live ticket records). After signing in, the product uses a compact navigation rail, concise breadcrumb bar, a staff/student-specific next action, database-backed metrics, a legible request directory, and consistent detail dialogs.

## What changed

- A cohesive, light professional design replaces neon gradients, glows, dark marketing panels, and oversized decorative artwork.
- Navigation labels reflect real tasks: Overview, Requests, AI triage, Analytics and Help & guide.
- One consistent set of spacing, typography, border, and color tokens covers every view.
- Statuses and priorities use soft, semantic labels; dashboard charts only show values returned by the API.
- Mobile navigation uses a backdrop and supports Escape to close. The dialog supports Escape and keyboard focus wrapping.
- The login password can be shown or hidden without submitting the form.
- A context-aware, real-data dashboard callout points staff to high-priority requests; students see a clear request action.
- The request directory retains existing rows while fetching filters, guards against stale overlapping queries, and shows pagination, loading, error, and empty states.
- `prefers-reduced-motion` is respected and all interactions use keyboard-reachable native controls.
- Existing backend APIs, authentication/authorization, database logic, model and evaluation methodology remain unchanged.

## Preview files

Screenshots are in `docs/screenshots/` (desktop, mobile and tablet).

**Important testing distinction:** In this authoring environment, Chromium refuses local HTTP and file navigation (`ERR_BLOCKED_BY_ADMINISTRATOR`). To review the visual interface, screenshots were generated in headless Chromium by injecting the actual production CSS/JS with mock `fetch` responses populated from the running local API. They are useful for testing **responsive layout, navigation, JS execution, and visual presentation**; they are *not* proof of a real-browser end-to-end login or deployment. Back-end HTTP smoke checks and API tests were run separately. A real live-browser deployment check must still be done by the submitter.

### Screen sizes reviewed

| Viewport | Preview pages | Result |
| --- | --- | --- |
| 1440 × 900 | Login, dashboard, requests, AI triage, request modal | No JS page errors or horizontal overflow in isolated visual preview |
| 900 × 850 | Login, dashboard | No JS page errors or horizontal overflow in isolated visual preview |
| 390 × 844 | Login, dashboard, mobile drawer, requests | No JS page errors or horizontal overflow in isolated visual preview |

## Next checks before showing an evaluator

1. On your actual Windows computer, launch `run.bat` and verify Student and Staff demo logins.
2. Create a report, run the AI suggestion, and search it in Requests.
3. As Staff, update status and assignment and verify that the change survives refresh.
4. Open the app on an actual Android/iPhone browser if available; test keyboard, scrolling and opening/closing the drawer.
5. Deploy using the README, and open the real HTTPS URL to test the full browser-to-server flow.

The visual redesign does not by itself guarantee design originality, an examiner's impression or any specific evaluation score.
