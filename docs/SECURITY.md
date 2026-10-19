# Security, validation and responsible deployment

## Implemented controls

| Threat / concern | Code-level defense | Reproducible check |
|---|---|---|
| Plaintext passwords | Salted PBKDF2-HMAC-SHA256 (310,000 iterations) and constant-time comparison | `test_password_hashes_salted_and_verifiable` |
| Cookie theft by JavaScript | Opaque random session token kept in HttpOnly, SameSite=Lax cookie; only its SHA-256 digest in database; 12-hour expiry | `test_auth_failure_and_signout` |
| CSRF on writes | Per-session random CSRF token via `/api/auth/me` or login; mandatory `X-CSRF-Token` on POST/PATCH authenticated routes | `test_csrf_guard_prevents_mutations` |
| Cross-site origin submits | Unsafe API requests with a supplied `Origin` must match same origin or configured allowlist; strict JSON Content-Type | `test_unsafe_content_type_and_cross_origin_are_rejected` |
| Student access to others' records | Ownership predicate for lists, details, comments and student dashboards, enforced at API/database level | `test_student_cannot_read_other_student_ticket` |
| Student impersonates staff | Server-side permission check on assignment, transition, assignee listing and export; register forces `student` role | `test_admin_has_staff_capabilities` and privacy test |
| SQL injection | Parameterized queries; search wildcard escaping and bounded filter arguments | `test_filters_pagination` |
| Invalid state transitions | Explicit transition graph; DB status checks; transaction and event audit | `test_staff_validated_workflow_assignment_and_reopen` |
| Invalid data | Strict Pydantic schemas, max lengths, enums and database `CHECK` / `FOREIGN KEY` constraints | `test_invalid_ticket_data_rejected` |
| Login guessing | SQLite-backed 8 failed login attempts per identifier/IP within rolling 15-minute window | `test_login_rate_limit` |
| Spreadsheet formula injection | CSV fields prefixed with apostrophe when opening characters could be formula operators | `test_csv_formula_injection_guard` |
| Common browser attacks | CSP (`script-src 'self'`), frame denial, no MIME sniffing, referrer and permissions policy headers; user strings HTML-escaped | `test_security_headers`, frontend `esc()` |

**Site security assumptions:** The frontend and API are served from the same origin behind HTTPS in production. Reverse proxies must forward the correct scheme/host. `COOKIE_SECURE=true` is mandatory on HTTPS. Cookie sessions and CSRF mitigate browser threats but do not replace real institutional authentication, account recovery, MFA, privacy compliance or operational incident response.

## Threat-model boundary

The prototype is useful for a class demonstration. It is **not a fully hardened university service**. Consider further work before production: centralized logs, monitoring/alerting, secure domain/TLS configuration, security review, dependency scanning and updates, server-side password reset, email verification, MFA, account suspension and moderation, backup/restore, retention/deletion policy, encryption at rest, compliance and data subject requests. Do not store confidential health/student disciplinary records in it. The model's safety routing must **never** be treated as an emergency service.

### Public-demo rules

1. `ENABLE_DEMO_DATA=true` enables known example passwords and fictional tickets. Treat such deployments as public sandboxes only. Do not submit real personal data.
2. For a genuine institution, set `ENABLE_DEMO_DATA=false`, configure `APP_ENV=production`, `COOKIE_SECURE=true`, `TRUSTED_HOSTS` and `ALLOWED_ORIGINS`, bootstrap a unique admin in a private environment, and integrate proper account provisioning.
3. HTTPS terminates at the hosting provider. Test cookie behavior on the actual deployed domain.
4. Render free web services may delete locally written SQLite state during restarts/redeploys. Do not assume backups or durability without a mounted persistent disk.
5. On multi-process or replicated deployments, move session/login attempt storage and database to shared infrastructure.

## How to verify authorization manually

Login as student, open `/api/tickets/4` (ticket owned by the other fictional student): expect `404`. Try an authenticated staff endpoint `/api/users/assignees`: expect `403`. Attempt to create a ticket without `X-CSRF-Token`: expect `403`. Attempt status transition `Open` directly to `Resolved`: expect `409`. Then log in as staff and demonstrate legitimate assignment and status progression. These scenarios are covered in automated tests.
