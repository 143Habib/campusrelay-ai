"""Opt-in fictional demo records; NEVER seed fixed passwords in production."""
from datetime import datetime, timedelta, timezone
from .database import connection
from .auth import hash_password, utc_now

DEMO_ACCOUNTS = (
    ("Ayesha Rahman", "student@campusrelay.demo", "Student@2026!", "student"),
    ("Rafiq Hasan", "staff@campusrelay.demo", "Staff@2026!", "staff"),
    ("Nadia Karim", "admin@campusrelay.demo", "Admin@2026!", "admin"),
    ("Mina Islam", "mina@campusrelay.demo", "Student@2026!", "student"),
)

SAMPLE_TICKETS = [
 ("Air conditioning stopped in Room 501", "The classroom air conditioner in Room 501 is not cooling, making afternoon lectures uncomfortable.", "Academic Block C, 5th floor", "Facilities", "Medium", "Open", 0),
 ("Student portal shows server error", "The student portal shows a server error whenever I try to access my course registration information.", "Student services / online", "IT", "Medium", "In Progress", 1),
 ("Exposed electrical wiring near stairs", "There are exposed electrical wires hanging near the main stairwell and students might receive an electric shock.", "Science Building, 2nd floor", "Safety", "High", "Open", 2),
 ("Shuttle bus missing North Gate stop", "The afternoon campus shuttle bus regularly skips the North Gate pickup and students are left waiting.", "North Gate bus stop", "Transport", "Medium", "Resolved", 3),
 ("Incorrect midterm grade published", "My statistics midterm grade appears incorrectly on the academic result portal and needs verification.", "Department of CSE", "Academic", "Low", "In Progress", 4),
 ("Library Wi-Fi drops frequently", "The campus wifi network in the library keeps disconnecting and students cannot access learning resources.", "Central Library, level 2", "IT", "Medium", "Resolved", 5),
 ("Leaking water tap in corridor", "A drinking water tap in the main corridor has been leaking continuously and needs maintenance.", "Academic Block A, ground floor", "Facilities", "Medium", "Resolved", 6),
 ("Emergency exit blocked by furniture", "The emergency exit is blocked by old furniture and would prevent safe evacuation during a fire.", "Engineering Lab Block", "Safety", "High", "In Progress", 7),
 ("Morning bus schedule inaccurate", "The morning bus is leaving before its posted departure time, and the university transport timetable is incorrect.", "Main campus bus terminal", "Transport", "Medium", "Open", 8),
 ("Wrong classroom on exam timetable", "Our published examination timetable lists the wrong room for the final assessment next week.", "Faculty of Business", "Academic", "Low", "Resolved", 9),
 ("Computer lab printers offline", "The printer in the computer laboratory has gone offline and students cannot print their course assignments.", "Computer Lab 3", "IT", "Medium", "Open", 10),
 ("Restroom light not working", "The restroom ceiling lights have stopped working, and the room remains dark during the day.", "Library Ground Floor", "Facilities", "Medium", "Reopened", 11),
 ("Chemical cabinet is unlocked", "A dangerous chemical storage cabinet was left unlocked in the science lab and needs safety inspection.", "Chemistry Lab", "Safety", "High", "Resolved", 12),
 ("Credit transfer application pending", "My academic credit transfer request is still pending despite submitting the required documents last month.", "Registrar Office", "Academic", "Low", "Open", 13),
 ("Evening shuttle arrives late", "The university evening shuttle arrived more than forty minutes late after the last lecture several times.", "West Gate transport stop", "Transport", "Medium", "In Progress", 14),
 ("Online assignment upload fails", "The learning management website fails whenever I upload my assignment file, even with a stable connection.", "Student portal", "IT", "Medium", "Resolved", 15),
 ("Broken classroom desks", "Several classroom desks have unstable legs and require repair before the next round of lectures.", "Academic Block B, room 207", "Facilities", "Medium", "Open", 16),
 ("Smoke detector needs attention", "The fire smoke detector is not working in the workshop even during its scheduled safety test.", "Workshop Building", "Safety", "High", "In Progress", 17),
 ("Class timetable overlaps", "Two mandatory lectures have been assigned to the same time slot and students cannot attend both courses.", "Department of EEE", "Academic", "Low", "Resolved", 18),
 ("Shuttle seating capacity too low", "The campus shuttle becomes overcrowded during morning hours and students cannot find available seats.", "South Gate bus stand", "Transport", "Low", "Open", 19),
 ("Network outage in design studio", "The university internet connection in the design studio is offline and online coursework is blocked.", "Design Studio, 4th floor", "IT", "Medium", "In Progress", 20),
 ("Water cooler out of service", "The drinking water cooler has stopped working and there is no clean cold water for this area.", "Cafeteria entrance", "Facilities", "Medium", "Open", 21),
 ("Library walkway is slippery", "The wet walkway outside the library is slippery and several students nearly fell this morning.", "Main Library Entrance", "Safety", "High", "Open", 22),
 ("Exam hall assignment unconfirmed", "My exam hall allocation is still not available despite the examination being scheduled for tomorrow.", "Examination Office", "Academic", "Medium", "Open", 23),
]


def seed_demo(path, classifier):
    with connection(path, write=True) as db:
        if db.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]:
            return False
        users = {}
        for name, email, password, role in DEMO_ACCOUNTS:
            cursor = db.execute("INSERT INTO users(name,email,password_hash,role,created_at) VALUES (?,?,?,?,?)",
                                (name, email, hash_password(password), role, utc_now()))
            users[role] = cursor.lastrowid
            if email.startswith("mina"):
                users["other_student"] = cursor.lastrowid
            elif role == "student":
                users["student"] = cursor.lastrowid
        for title, description, location, category, priority, status, index in SAMPLE_TICKETS:
            # A few records owned by a second student for explicit privacy testing.
            creator = users["other_student"] if index in (3, 6, 9, 12, 16, 21) else users["student"]
            assignee = users["staff"] if status in ("Resolved", "In Progress", "Reopened") else None
            day = datetime.now(timezone.utc) - timedelta(days=(index * 2) % 12, hours=index % 6)
            created = day.isoformat(timespec="seconds")
            updated = (day + timedelta(hours=(index % 5) + 1)).isoformat(timespec="seconds") if status != "Open" else created
            suggested = classifier.suggest(title + ". " + description)
            cursor = db.execute("""INSERT INTO tickets(ref,creator_id,assignee_id,title,description,location,category,priority,status,
              ai_category,ai_confidence,ai_priority,created_at,updated_at,resolved_at)
              VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
              (f"CR-2026-{index+1:04d}", creator, assignee, title, description, location, category, priority, status,
               suggested["category"], suggested["confidence"], suggested["priority"], created, updated, updated if status == "Resolved" else None))
            tid = cursor.lastrowid
            db.execute("INSERT INTO ticket_events(ticket_id,actor_id,event_type,to_status,note,created_at) VALUES (?,?,?,?,?,?)",
                       (tid, creator, "created", "Open", "Issue was reported.", created))
            if status != "Open":
                steps = ["In Progress"]
                if status in ("Resolved", "Reopened"):
                    steps.append("Resolved")
                if status == "Reopened":
                    steps.append("Reopened")
                previous = "Open"
                for step_number, next_status in enumerate(steps, start=1):
                    step_time = (day + timedelta(minutes=30 * step_number)).isoformat(timespec="seconds")
                    db.execute("INSERT INTO ticket_events(ticket_id,actor_id,event_type,from_status,to_status,note,created_at) VALUES (?,?,?,?,?,?,?)",
                               (tid, users["staff"], "status", previous, next_status,
                                "Demo status progression." if next_status != "Reopened" else "Reopened after issue returned.", step_time))
                    previous = next_status
        return True


def bootstrap_admin(path, email: str, password: str):
    if not email or not password:
        return False
    if len(password) < 12:
        raise ValueError("BOOTSTRAP_ADMIN_PASSWORD must have at least 12 characters.")
    with connection(path, write=True) as db:
        if db.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
            return False
        db.execute("INSERT INTO users(name,email,password_hash,role,created_at) VALUES (?,?,?,?,?)",
                   ("Campus Administrator", email, hash_password(password), "admin", utc_now()))
    return True
