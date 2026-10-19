"""One-time admin creation; use a private terminal, not a publicly accessible endpoint."""
import getpass
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.config import Settings  # noqa: E402
from app.database import init_database  # noqa: E402
from app.seed import bootstrap_admin  # noqa: E402


def main():
    settings = Settings.from_env()
    email = input('Admin email: ').strip().lower()
    password = getpass.getpass('Admin password (12+ characters): ')
    confirm = getpass.getpass('Confirm admin password: ')
    if password != confirm:
        raise SystemExit('Passwords do not match.')
    if '@' not in email:
        raise SystemExit('A valid email is required.')
    init_database(settings.db_path)
    created = bootstrap_admin(settings.db_path, email, password)
    print('Admin account created.' if created else 'This account already exists. No changes made.')


if __name__ == '__main__':
    main()
