"""Configuration loaded from environment variables via pydantic-settings."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings

# Resolve workspace root .env: tools/pipeline_runner/pipeline_runner/config.py -> repo root
# Fall back to WORKSPACE_ROOT env var or cwd if path calculation fails
try:
    _resolved = Path(__file__).resolve()
    # normal path: config.py -> pipeline_runner/ -> tools/pipeline_runner/ -> tools/ -> repo_root (parents[4])
    # symlink / venv path may be shorter; try multiple offsets
    for n in [4, 3, 2]:
        try:
            _cand = _resolved.parents[n - 1] / ".env"
            if _cand.exists() or n == 2:
                _WORKSPACE_ROOT = _resolved.parents[n - 1]
                break
        except IndexError:
            continue
    else:
        _WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", "."))
except Exception:
    _WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", "."))

import os
_ENV_FILES = [
    _WORKSPACE_ROOT / ".env",  # workspace root (primary)
    Path(".env"),               # cwd fallback
]


class PipelineConfig(BaseSettings):
    """All configuration is read from environment variables. No hardcoded secrets."""

    # Workday URLs and paths
    WORKDAY_BASE_URL: str
    WORKDAY_TASKS_PATH: str = "/tasks"
    WORKDAY_TIME_TRACKING_PATH: str = "/time-tracking"
    WORKDAY_HOME_PATH: str = "/home"

    # SSO configuration
    SSO_PROVIDER_NAME: str = ""
    ORG_TENANT_DIRECT_LINK: str = ""

    # Chrome DevTools Protocol (relay fallback)
    CHROME_CDP_TOKEN: str = ""
    CHROME_CDP_PORT: int = 9222

    # Playwright settings
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_TIMEOUT: int = 30000

    # Browser strategy: "headless_first", "cdp_only", "headed"
    BROWSER_STRATEGY: str = "headless_first"

    model_config = {
        "env_file": [str(f) for f in _ENV_FILES],
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def tasks_url(self) -> str:
        return f"{self.WORKDAY_BASE_URL.rstrip('/')}{self.WORKDAY_TASKS_PATH}"

    @property
    def time_tracking_url(self) -> str:
        return f"{self.WORKDAY_BASE_URL.rstrip('/')}{self.WORKDAY_TIME_TRACKING_PATH}"

    @property
    def home_url(self) -> str:
        return f"{self.WORKDAY_BASE_URL.rstrip('/')}{self.WORKDAY_HOME_PATH}"
