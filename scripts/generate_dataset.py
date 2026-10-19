"""Create a transparent, reproducible synthetic-text baseline dataset.

This is intentionally illustrative data, not a claim of real campus model performance.
The holdout phrases are separately authored (rather than copying training rows).
"""
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parent.parent
TRAIN = {
"Facilities": [
"the classroom air conditioner is not cooling", "a ceiling fan stopped spinning", "the lecture hall lights are flickering",
"the library washroom tap is leaking", "a water pipe burst near the cafeteria", "the hostel lift is stuck between floors",
"the desk chair has a broken leg", "the door lock in the study room is jammed", "the projector screen mount has fallen",
"the water filter is not working", "the corridor smells of sewage", "there is no water in the restrooms",
"the window glass is cracked", "the lecture room is too hot without ventilation", "the building elevator is malfunctioning",
"the drinking fountain has stopped", "the floor tiles are coming loose", "the classroom furniture is damaged",
"the wall paint is peeling", "the bathroom toilet is blocked", "a roof leak is dripping onto desks",
"the heater in the seminar hall is not running", "the hallway ceiling light is out", "the sink in the laboratory is clogged",
"the classroom door handle broke", "the wash basin is overflowing", "the staircase handrail is loose",
"the auditorium ventilation system is noisy", "the overhead light is broken", "the common room has no electricity for fans",
"the building air conditioning unit is making loud noise", "the meeting room tables are unstable",
"the restroom flush does not work", "the dormitory plumbing needs repair", "the corridor floor is waterlogged",
"the cafeteria water dispenser is leaking", "the window latch cannot close", "the toilet cubicle door is damaged",
],
"IT": [
"campus wifi keeps disconnecting from my laptop", "the student portal login page shows an error", "my university email cannot send messages",
"the computer laboratory desktops will not boot", "the learning management website is down", "the classroom printer has a paper jam",
"the digital attendance system fails to load", "the course registration app crashes", "the password reset link does not arrive",
"the online payment gateway returns an error", "the laboratory computer is showing a blue screen", "the campus network connection is very slow",
"the smart card scanner cannot connect", "the wifi router is offline", "the university website cannot be reached",
"the university VPN is failing to authenticate", "the exam software freezes during launch", "the library computer has a broken keyboard",
"the classroom display does not receive the HDMI signal", "my student account was locked out",
"the online library database times out", "the course management dashboard has an API error",
"the printer driver is not installed", "a classroom microphone software driver keeps crashing",
"the desktop monitor has no signal", "the online assignment upload fails", "the network firewall blocks the education website",
"the IT lab workstation has no internet", "the campus app is displaying a server error",
"the e-learning video player will not load", "the account authentication service reports invalid token",
"the meeting room webcam is not recognized", "the library barcode scanner software is frozen",
"the router needs a firmware update", "the web portal returns a 500 server error",
"the lab computer has malware warnings", "the digital timetable page will not refresh", "the password change form is broken",
],
"Safety": [
"a fire extinguisher is missing from the corridor", "someone left exposed electrical wires in the stairwell",
"the emergency exit is blocked by boxes", "the laboratory chemical cabinet is unlocked", "a broken railing creates a fall hazard",
"there is smoke coming out of the electrical room", "the fire alarm is not working", "a suspicious person entered a restricted building",
"the corridor is slippery and people are falling", "a bicycle was stolen near the entrance", "the walkway lighting is unsafe at night",
"the emergency staircase door will not open", "a security camera has been vandalized", "a violent confrontation is occurring by the gate",
"an electrical socket is sparking", "the lab gas cylinder is leaking", "broken glass is scattered in the hallway",
"the boundary gate is not being monitored", "a tree branch may fall onto pedestrians", "the ceiling fixture could fall and injure someone",
"there is an unattended bag near the library", "the emergency exit sign is missing", "someone is threatening students near the dorm",
"the pedestrian crossing is dangerous without markings", "the floodwater near electrical panels is dangerous",
"the security guard is absent at night", "a dangerous crack appeared in the staircase",
"the first aid cabinet is empty", "the fire escape route has a locked door", "the emergency alarm bell is disconnected",
"the laboratory acid container is spilled", "students reported theft in the common area",
"the campus entrance has a damaged security barrier", "a live wire is hanging from the pole",
"the evacuation route is obstructed", "a gas smell is coming from the canteen kitchen",
"there is a serious risk of injury near the construction area", "the campus security hotline is unanswered",
],
"Academic": [
"my exam grade is missing from the results portal", "the class timetable has a scheduling conflict",
"a lecturer has not posted the course syllabus", "the assignment due date is incorrect", "my course credit transfer has not been approved",
"the examination hall allocation is wrong", "the attendance record is inaccurate", "the course section has no assigned instructor",
"the transcript contains an incorrect mark", "my semester advising request has not been answered",
"the class makeup schedule is not announced", "my scholarship academic record is incorrect",
"the thesis supervisor allocation is pending", "an examination paper has an incorrect question",
"the tutorial section enrollment limit is wrong", "the academic calendar has conflicting dates",
"the lab session has been canceled without notice", "the course registration prerequisite is incorrect",
"the published CGPA calculation appears wrong", "the final exam result has not been released",
"the department forgot to assign a classroom", "my academic certificate spelling is incorrect",
"the subject enrollment permission is missing", "the elective course list is outdated",
"the lecture schedule clashes with another compulsory subject", "the lecturer uploaded the wrong course materials",
"the classroom change was not communicated", "the academic advisor appointment was canceled",
"the grading rubric for our assignment is unavailable", "the quiz marks are not reflected",
"the enrollment deadline is displayed incorrectly", "the department has not approved course withdrawal",
"the class attendance percentage is miscalculated", "the thesis defense date has not been published",
"the teaching assistant office hours are not scheduled", "my exam script recheck application is pending",
"the department published the wrong course code", "the credit completion status is inconsistent",
],
"Transport": [
"the campus shuttle bus arrived forty minutes late", "the university bus route is missing a stop",
"the transport schedule is not updated", "the shuttle driver skipped the designated pickup point",
"the student bus broke down on the road", "the bus pass was not recognized at boarding",
"the campus shuttle is overcrowded every morning", "the bus departure time was changed without notice",
"the university shuttle has no wheelchair access", "the morning bus was canceled",
"the shuttle pickup location sign is missing", "the student transportation route is too long",
"the campus bus left earlier than its posted time", "the bus tracking display is inaccurate",
"the university vehicle did not arrive for the field trip", "the student transport ticket was charged twice",
"the campus shuttle has a broken air conditioner", "the shuttle seat is damaged",
"the bus stop has no timetable information", "the shuttle service ends before evening classes",
"the university bus is not available on the weekend", "the bus conductor denied access with a valid pass",
"the parking shuttle is delayed in traffic", "the university transport office ignored the bus route request",
"the bus stop queue is extremely long", "the evening bus stopped running",
"the campus shuttle vehicle is not clean", "the university bus fleet lacks enough seats",
"the bus route map contains wrong destinations", "the transport booking system marked my shuttle as canceled",
"the morning shuttle missed my departure", "the bus service does not cover the east gate",
"the campus bus is running behind schedule", "the transport office needs an additional pickup time",
"the university shuttle has a punctured tire", "the bus driver took a wrong route",
"the shuttle stop is too far from the classroom blocks", "the transport pass renewal is pending",
]}

TEST = {
"Facilities": [
"There is a dripping faucet in the chemistry building washroom.",
"The dorm ceiling fan makes grinding noises and stops.",
"Please repair the broken bathroom commode in block B.",
"Water is pooling from a damaged overhead pipe in the reading room.",
"The seminar hall air-conditioning no longer works.",
"Several classroom seats have snapped hinges.",
"The corridor fluorescent bulbs keep going dark.",
"The elevator doors fail to shut on the third floor.",
"The canteen sink drain is blocked with debris.",
"A loose wooden door frame needs maintenance.",
],
"IT": [
"My laptop cannot join the eduroam wireless network.",
"The campus student dashboard displays HTTP 503.",
"The multimedia lab PCs reboot unexpectedly.",
"I cannot access the Moodle course website.",
"The classroom laser printer refuses to print documents.",
"Account recovery emails never reach my inbox.",
"The smart classroom screen will not detect the laptop connection.",
"The computer lab internet service drops during assignments.",
"University single sign-on rejects my correct password.",
"The online form crashes whenever I attach a PDF.",
],
"Safety": [
"The locked emergency stairwell is preventing evacuation.",
"An electrical cable is exposed beside the drinking fountain.",
"Someone is stealing backpacks outside the examination hall.",
"There is a strong smell of leaking cooking gas.",
"Students are slipping on wet stairs and getting hurt.",
"A loose overhead sign threatens to fall onto the footpath.",
"The smoke detector in the laboratory is silent.",
"Strangers are forcing their way through the back security gate.",
"Broken glass is lying where pedestrians walk barefoot.",
"A chemical spill in the science lab needs immediate attention.",
],
"Academic": [
"The department entered the wrong grade on my transcript.",
"Two compulsory lectures are listed at exactly the same time.",
"My academic adviser has not signed my study plan.",
"The course outline for statistics is unavailable.",
"My final assessment score was calculated incorrectly.",
"The examination timetable shows the wrong room number.",
"I am unable to obtain approval for course overload.",
"A required lecture was postponed without an alternative date.",
"The portal shows the wrong instructor for this subject.",
"The published scholarship eligibility credits are inaccurate.",
],
"Transport": [
"The university shuttle missed the north gate pickup again.",
"Our student bus is delayed by almost an hour each day.",
"The campus transport van did not show up for the trip.",
"My bus boarding pass is being rejected by the conductor.",
"Evening shuttle service stopped before the last lecture.",
"We need more university buses on the morning route.",
"The shuttle tracking map has the wrong bus location.",
"The bus departed from a different stop without warning.",
"The transport schedule lists an incorrect departure time.",
"The route through the south gate has been discontinued.",
]}


def write_csv(path: Path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "category"])
        writer.writerows(rows)


def main():
    rows = []
    for category, phrases in TRAIN.items():
        for index, phrase in enumerate(phrases):
            variants = [f"Please help: {phrase} in the university campus.",
                        f"A student reported that {phrase}; this is affecting campus activities."]
            rows.extend((variant, category) for variant in variants)
    ROOT.joinpath("data").mkdir(exist_ok=True)
    write_csv(ROOT / "data" / "train.csv", rows)
    write_csv(ROOT / "data" / "holdout.csv", [(t, c) for c, examples in TEST.items() for t in examples])
    print(f"Training rows: {len(rows)}; holdout rows: {sum(map(len,TEST.values()))}")


if __name__ == "__main__":
    main()
