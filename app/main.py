"""CampusRelay AI: same-origin FastAPI application and documented REST API."""
from __future__ import annotations
from contextlib import asynccontextmanager
import csv
from datetime import datetime, timedelta, timezone
from io import StringIO
import logging
from pathlib import Path
import sqlite3
import time

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .auth import (
    DUMMY_HASH, SESSION_SECONDS, User, check_csrf, check_origin, clear_login_attempts,
    create_session, get_user, hash_password, hash_token, record_login_failure,
    require_json, throttle_login, utc_now, verify_password,
)
from .config import ROOT, Settings
from .database import connection, init_database
from .ml import CampusClassifier, CATEGORIES
from .schemas import Comment, Login, Register, Suggest, TicketAssign, TicketCreate, TicketUpdate
from .seed import bootstrap_admin, seed_demo

log = logging.getLogger("campusrelay")
STATUSES = ("Open", "In Progress", "Resolved", "Reopened")
PRIORITIES = ("Low", "Medium", "High")
TRANSITIONS = {
    "Open": {"In Progress"},
    "In Progress": {"Resolved"},
    "Resolved": {"Reopened"},
    "Reopened": {"In Progress"},
}


def record_to_dict(row) -> dict:
    return dict(row)


def require_staff(user: User) -> None:
    if user.role not in ("staff", "admin"):
        raise HTTPException(403, detail="Only staff or administrators may perform this action.")


def current_with_csrf(request: Request, user: User = Depends(get_user)) -> User:
    check_csrf(request, user)
    return user


def visibility_sql(user: User, alias: str = "t") -> tuple[str, tuple]:
    return (f"{alias}.creator_id=?", (user.id,)) if user.role == "student" else ("1=1", ())


def fetch_ticket(db: sqlite3.Connection, ticket_id: int, user: User) -> dict:
    sql = """SELECT t.*, u.name AS creator_name, u.email AS creator_email, a.name AS assignee_name
              FROM tickets t JOIN users u ON u.id=t.creator_id LEFT JOIN users a ON a.id=t.assignee_id
              WHERE t.id=?"""
    row = db.execute(sql, (ticket_id,)).fetchone()
    # Return 404 rather than disclosing another student's ticket existence.
    if not row or (user.role == "student" and row["creator_id"] != user.id):
        raise HTTPException(404, detail="Ticket not found.")
    return record_to_dict(row)


def log_event(db, ticket_id, actor_id, event_type, note="", before=None, after=None):
    db.execute("""INSERT INTO ticket_events(ticket_id,actor_id,event_type,from_status,to_status,note,created_at)
                  VALUES (?,?,?,?,?,?,?)""",
               (ticket_id, actor_id, event_type, before, after, note, utc_now()))


def safe_csv(value) -> str:
    """Prevent spreadsheet formula execution when opening downloaded CSV exports."""
    value = "" if value is None else str(value)
    return "'" + value if value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r", "\n")) else value


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        init_database(settings.db_path)
        app.state.classifier = CampusClassifier(ROOT)
        if settings.enable_demo_data:
            seed_demo(settings.db_path, app.state.classifier)
        if settings.bootstrap_admin_email and settings.bootstrap_admin_password:
            bootstrap_admin(settings.db_path, settings.bootstrap_admin_email, settings.bootstrap_admin_password)
        if settings.app_env == "production" and not settings.secure_cookies:
            log.warning("Production COOKIE_SECURE is disabled; use HTTPS and COOKIE_SECURE=true.")
        yield

    app = FastAPI(title="CampusRelay AI REST API", version="1.0.0", lifespan=lifespan,
                  description="AI-assisted campus issue management. /api endpoints need cookie authentication and CSRF for writes.")
    app.state.settings = settings
    if settings.trusted_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.trusted_hosts))
    app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")

    @app.middleware("http")
    async def protection_headers(request: Request, call_next):
        if request.method in ("POST", "PATCH", "PUT", "DELETE") and request.url.path.startswith("/api/"):
            try:
                check_origin(request)
                require_json(request)
            except HTTPException as exc:
                return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
            "font-src 'self'; connect-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'"
        )
        response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/api/") else "no-cache"
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, error: RequestValidationError):
        details = [{"field": ".".join(str(x) for x in e["loc"]), "message": str(e["msg"])} for e in error.errors()]
        return JSONResponse({"detail": "Please correct the highlighted input.", "errors": details}, status_code=422)

    @app.get("/", include_in_schema=False)
    async def home():
        return FileResponse(ROOT / "static" / "index.html")

    @app.get("/health", tags=["Operations"])
    async def health():
        # Check DB read viability, not only process availability.
        with connection(settings.db_path) as db:
            db.execute("SELECT 1").fetchone()
        return {"status": "ok", "service": "CampusRelay AI", "version": "1.0.0"}

    @app.get("/api/meta", tags=["Operations"])
    async def meta(request: Request):
        return {"application": "CampusRelay AI", "demo_mode": settings.enable_demo_data,
                "categories": list(CATEGORIES), "statuses": list(STATUSES),
                "ml_model": "TF-IDF + Logistic Regression", "version": "1.0.0"}

    @app.post("/api/auth/register", status_code=201, tags=["Authentication"])
    async def register(payload: Register):
        email = payload.email.strip().lower()
        if "@" not in email or email.startswith("@") or email.endswith("@") or " " in email:
            raise HTTPException(422, detail="Please enter a valid email address.")
        try:
            with connection(settings.db_path, write=True) as db:
                db.execute("INSERT INTO users(name,email,password_hash,role,created_at) VALUES (?,?,?,?,?)",
                           (payload.name, email, hash_password(payload.password), "student", utc_now()))
        except sqlite3.IntegrityError:
            raise HTTPException(409, detail="An account with this email already exists.") from None
        return {"message": "Account created. Please sign in."}

    @app.post("/api/auth/login", tags=["Authentication"])
    async def login(payload: Login, request: Request):
        email = payload.email.strip().lower()
        ip = request.client.host if request.client else "unknown"
        throttle_login(settings.db_path, email, ip)
        with connection(settings.db_path) as db:
            row = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        valid = verify_password(payload.password, row["password_hash"] if row else DUMMY_HASH)
        if not row or not valid:
            record_login_failure(settings.db_path, email, ip)
            raise HTTPException(401, detail="Incorrect email or password.")
        clear_login_attempts(settings.db_path, email, ip)
        token, csrf = create_session(settings.db_path, row["id"])
        response = JSONResponse({"user": {"id": row["id"], "name": row["name"], "email": row["email"], "role": row["role"]},
                                 "csrf_token": csrf})
        response.set_cookie("cr_session", token, max_age=SESSION_SECONDS, httponly=True,
                            secure=settings.secure_cookies, samesite="lax", path="/")
        return response

    @app.get("/api/auth/me", tags=["Authentication"])
    async def auth_me(user: User = Depends(get_user)):
        return {"user": user.public(), "csrf_token": user.csrf}

    @app.post("/api/auth/logout", tags=["Authentication"])
    async def logout(request: Request, user: User = Depends(current_with_csrf)):
        token = request.cookies.get("cr_session", "")
        with connection(settings.db_path, write=True) as db:
            db.execute("DELETE FROM sessions WHERE token_hash=?", (hash_token(token),))
        response = JSONResponse({"message": "Signed out successfully."})
        response.delete_cookie("cr_session", path="/", secure=settings.secure_cookies, httponly=True, samesite="lax")
        return response

    @app.post("/api/ai/suggest", tags=["AI"])
    async def ai_suggest(payload: Suggest, request: Request, user: User = Depends(current_with_csrf)):
        return request.app.state.classifier.suggest(payload.text)

    @app.get("/api/ai/model-card", tags=["AI"])
    async def model_card(request: Request, user: User = Depends(get_user)):
        return request.app.state.classifier.metrics

    @app.get("/api/users/assignees", tags=["Users"])
    async def assignees(user: User = Depends(get_user)):
        require_staff(user)
        with connection(settings.db_path) as db:
            rows = db.execute("SELECT id,name,role FROM users WHERE role IN ('staff','admin') ORDER BY name").fetchall()
        return {"users": [dict(x) for x in rows]}

    @app.get("/api/dashboard", tags=["Analytics"])
    async def dashboard(user: User = Depends(get_user)):
        where, params = visibility_sql(user)
        with connection(settings.db_path) as db:
            total = db.execute(f"SELECT COUNT(*) AS n FROM tickets t WHERE {where}", params).fetchone()["n"]
            by_status = {row["status"]: row["n"] for row in db.execute(
                f"SELECT status,COUNT(*) AS n FROM tickets t WHERE {where} GROUP BY status", params)}
            by_category = {row["category"]: row["n"] for row in db.execute(
                f"SELECT category,COUNT(*) AS n FROM tickets t WHERE {where} GROUP BY category", params)}
            high = db.execute(f"SELECT COUNT(*) AS n FROM tickets t WHERE {where} AND priority='High' AND status!='Resolved'", params).fetchone()["n"]
            assigned = db.execute(f"SELECT COUNT(*) AS n FROM tickets t WHERE {where} AND assignee_id IS NOT NULL AND status!='Resolved'", params).fetchone()["n"]
            recent = db.execute(f"""SELECT t.id,t.ref,t.title,t.status,t.category,t.priority,t.created_at,
                   u.name AS creator_name FROM tickets t JOIN users u ON t.creator_id=u.id
                   WHERE {where} ORDER BY t.created_at DESC,t.id DESC LIMIT 6""", params).fetchall()
            days = [(datetime.now(timezone.utc) - timedelta(days=i)).date().isoformat() for i in range(6, -1, -1)]
            trend_data = dict((r["day"], r["n"]) for r in db.execute(f"""SELECT substr(created_at,1,10) AS day,
                   COUNT(*) AS n FROM tickets t WHERE {where} AND substr(created_at,1,10)>=? GROUP BY day""",
                   params + (days[0],)))
        return {"total": total, "status_counts": {s: by_status.get(s, 0) for s in STATUSES},
                "category_counts": {c: by_category.get(c, 0) for c in CATEGORIES},
                "open_high_priority": high, "assigned_active": assigned,
                "resolved": by_status.get("Resolved", 0), "recent": [dict(r) for r in recent],
                "trend": [{"date": d, "count": trend_data.get(d, 0)} for d in days],
                "scope": "own" if user.role == "student" else "all"}

    @app.get("/api/tickets", tags=["Tickets"])
    async def list_tickets(user: User = Depends(get_user), search: str = Query("", max_length=120),
                           status: str = Query("All"), category: str = Query("All"),
                           priority: str = Query("All"), page: int = Query(1, ge=1, le=100000),
                           page_size: int = Query(8, ge=1, le=50)):
        if status not in (*STATUSES, "All") or category not in (*CATEGORIES, "All") or priority not in (*PRIORITIES, "All"):
            raise HTTPException(422, detail="Invalid ticket filter.")
        where, args = visibility_sql(user)
        clauses, params = [where], list(args)
        if search.strip():
            escaped = search.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            clauses.append("(t.title LIKE ? ESCAPE '\\' OR t.ref LIKE ? ESCAPE '\\' OR t.location LIKE ? ESCAPE '\\')")
            params.extend([f"%{escaped}%"] * 3)
        if status != "All":
            clauses.append("t.status=?")
            params.append(status)
        if category != "All":
            clauses.append("t.category=?")
            params.append(category)
        if priority != "All":
            clauses.append("t.priority=?")
            params.append(priority)
        condition = " AND ".join(clauses)
        with connection(settings.db_path) as db:
            total = db.execute(f"SELECT COUNT(*) AS n FROM tickets t WHERE {condition}", params).fetchone()["n"]
            rows = db.execute(f"""SELECT t.*,u.name AS creator_name,a.name AS assignee_name
                 FROM tickets t JOIN users u ON u.id=t.creator_id LEFT JOIN users a ON a.id=t.assignee_id
                 WHERE {condition} ORDER BY t.created_at DESC,t.id DESC LIMIT ? OFFSET ?""",
                 params + [page_size, (page-1) * page_size]).fetchall()
        return {"items": [dict(row) for row in rows], "total": total, "page": page,
                "page_size": page_size, "pages": max(1, (total + page_size - 1) // page_size)}

    @app.post("/api/tickets", status_code=201, tags=["Tickets"])
    async def create_ticket(payload: TicketCreate, request: Request, user: User = Depends(current_with_csrf)):
        # Never trust a client-provided AI result; recalculate on the server.
        prediction = request.app.state.classifier.suggest(payload.title + ". " + payload.description)
        with connection(settings.db_path, write=True) as db:
            now = utc_now()
            cursor = db.execute("""INSERT INTO tickets(ref,creator_id,title,description,location,category,priority,
              status,ai_category,ai_confidence,ai_priority,created_at,updated_at)
              VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
              ("PENDING-" + str(time.time_ns()), user.id, payload.title, payload.description, payload.location,
               payload.category, payload.priority, "Open", prediction["category"], prediction["confidence"],
               prediction["priority"], now, now))
            ticket_id = cursor.lastrowid
            ref = f"CR-{datetime.now(timezone.utc).year}-{ticket_id:04d}"
            db.execute("UPDATE tickets SET ref=? WHERE id=?", (ref, ticket_id))
            log_event(db, ticket_id, user.id, "created", "Issue submitted by reporter.", after="Open")
        return {"id": ticket_id, "ref": ref, "message": "Issue reported successfully.",
                "ai": prediction, "human_override": payload.category != prediction["category"] or payload.priority != prediction["priority"]}

    @app.get("/api/tickets/{ticket_id}", tags=["Tickets"])
    async def ticket_detail(ticket_id: int, user: User = Depends(get_user)):
        with connection(settings.db_path) as db:
            ticket = fetch_ticket(db, ticket_id, user)
            events = db.execute("""SELECT e.id,e.event_type,e.from_status,e.to_status,e.note,e.created_at,
                     u.name AS actor_name FROM ticket_events e JOIN users u ON u.id=e.actor_id
                     WHERE ticket_id=? ORDER BY e.id ASC""", (ticket_id,)).fetchall()
        return {"ticket": ticket, "events": [dict(e) for e in events],
                "allowed_next": sorted(TRANSITIONS[ticket["status"]]) if user.role != "student" else []}

    @app.patch("/api/tickets/{ticket_id}/status", tags=["Tickets"])
    async def update_status(ticket_id: int, payload: TicketUpdate, user: User = Depends(current_with_csrf)):
        require_staff(user)
        with connection(settings.db_path, write=True) as db:
            ticket = fetch_ticket(db, ticket_id, user)
            if payload.status not in TRANSITIONS[ticket["status"]]:
                raise HTTPException(409, detail=f"Cannot move from {ticket['status']} to {payload.status}. Follow the defined workflow.")
            now = utc_now()
            resolved = now if payload.status == "Resolved" else None
            db.execute("UPDATE tickets SET status=?,updated_at=?,resolved_at=? WHERE id=?",
                       (payload.status, now, resolved, ticket_id))
            log_event(db, ticket_id, user.id, "status", payload.note or "Status changed by staff.",
                      ticket["status"], payload.status)
        return {"message": "Status updated.", "status": payload.status}

    @app.patch("/api/tickets/{ticket_id}/assignee", tags=["Tickets"])
    async def assign_ticket(ticket_id: int, payload: TicketAssign, user: User = Depends(current_with_csrf)):
        require_staff(user)
        with connection(settings.db_path, write=True) as db:
            ticket = fetch_ticket(db, ticket_id, user)
            name = "Unassigned"
            if payload.assignee_id is not None:
                assignee = db.execute("SELECT id,name FROM users WHERE id=? AND role IN ('staff','admin')", (payload.assignee_id,)).fetchone()
                if not assignee:
                    raise HTTPException(422, detail="Please select an eligible staff member.")
                name = assignee["name"]
            db.execute("UPDATE tickets SET assignee_id=?,updated_at=? WHERE id=?",
                       (payload.assignee_id, utc_now(), ticket_id))
            log_event(db, ticket_id, user.id, "assigned", f"Assignment changed to {name}.")
        return {"message": "Assignment saved.", "assignee_name": name}

    @app.post("/api/tickets/{ticket_id}/comments", status_code=201, tags=["Tickets"])
    async def add_comment(ticket_id: int, payload: Comment, user: User = Depends(current_with_csrf)):
        with connection(settings.db_path, write=True) as db:
            fetch_ticket(db, ticket_id, user)
            log_event(db, ticket_id, user.id, "comment", payload.note)
            db.execute("UPDATE tickets SET updated_at=? WHERE id=?", (utc_now(), ticket_id))
        return {"message": "Comment added."}

    @app.get("/api/export/tickets.csv", tags=["Analytics"])
    async def export_csv(user: User = Depends(get_user)):
        require_staff(user)
        fields = ["ref", "title", "description", "location", "category", "priority", "status",
                  "creator_name", "assignee_name", "created_at", "updated_at", "resolved_at"]
        with connection(settings.db_path) as db:
            rows = db.execute("""SELECT t.ref,t.title,t.description,t.location,t.category,t.priority,t.status,
               u.name AS creator_name,a.name AS assignee_name,t.created_at,t.updated_at,t.resolved_at
               FROM tickets t JOIN users u ON u.id=t.creator_id LEFT JOIN users a ON a.id=t.assignee_id
               ORDER BY t.id DESC""").fetchall()
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(fields)
        for row in rows:
            writer.writerow([safe_csv(row[field]) for field in fields])
        return Response(content=output.getvalue(), media_type="text/csv; charset=utf-8",
                        headers={"Content-Disposition": 'attachment; filename="campusrelay_tickets.csv"'})

    return app


app = create_app()
