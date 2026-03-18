"""Configuration loaded from environment variables via pydantic-settings."""

from pydantic_settings import BaseSettings


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
        "env_file": ".env",
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
