"""Small explicit settings layer. Environment variables always override local .env."""
from dataclasses import dataclass
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent


def read_dotenv(path: Path) -> None:
    """Load simple KEY=value pairs without requiring an optional package."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or not key.replace("_", "").isalnum():
            continue
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, "true" if default else "false").lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Settings:
    db_path: Path
    app_env: str = "development"
    enable_demo_data: bool = False
    secure_cookies: bool = False
    allowed_origins: tuple[str, ...] = ()
    bootstrap_admin_email: str = ""
    bootstrap_admin_password: str = ""
    trusted_hosts: tuple[str, ...] = ()

    @classmethod
    def from_env(cls) -> "Settings":
        read_dotenv(ROOT / ".env")
        env = os.getenv("APP_ENV", "development").strip().lower()
        db_path = Path(os.getenv("DATABASE_PATH", str(ROOT / "instance" / "campusrelay.db")))
        return cls(
            db_path=db_path,
            app_env=env,
            enable_demo_data=env_bool("ENABLE_DEMO_DATA", env == "development"),
            secure_cookies=env_bool("COOKIE_SECURE", env == "production"),
            allowed_origins=tuple(x.strip().rstrip("/") for x in os.getenv("ALLOWED_ORIGINS", "").split(",") if x.strip()),
            bootstrap_admin_email=os.getenv("BOOTSTRAP_ADMIN_EMAIL", "").strip().lower(),
            bootstrap_admin_password=os.getenv("BOOTSTRAP_ADMIN_PASSWORD", ""),
            trusted_hosts=tuple(x.strip() for x in os.getenv("TRUSTED_HOSTS", "").split(",") if x.strip()),
        )
