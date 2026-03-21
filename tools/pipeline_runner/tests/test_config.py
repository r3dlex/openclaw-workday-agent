"""Tests for pipeline_runner.config."""

import pytest

from pipeline_runner.config import PipelineConfig


class TestPipelineConfig:
    def test_loads_from_env(self, dummy_env):
        config = PipelineConfig()  # type: ignore[call-arg]
        assert config.WORKDAY_BASE_URL == "https://workday.example.com"
        assert config.SSO_PROVIDER_NAME == "TestSSO"
        assert config.PLAYWRIGHT_HEADLESS is True
        assert config.PLAYWRIGHT_TIMEOUT == 5000

    def test_defaults(self, monkeypatch):
        monkeypatch.setenv("WORKDAY_BASE_URL", "https://wd.test")
        # Clear env vars that CI may set so we test true defaults
        for var in ("BROWSER_STRATEGY", "SSO_PROVIDER_NAME", "PLAYWRIGHT_TIMEOUT",
                     "PLAYWRIGHT_HEADLESS", "WORKDAY_TASKS_PATH",
                     "WORKDAY_TIME_TRACKING_PATH", "WORKDAY_HOME_PATH"):
            monkeypatch.delenv(var, raising=False)
        # Disable .env file loading to test true defaults
        config = PipelineConfig(_env_file=None)  # type: ignore[call-arg]
        assert config.WORKDAY_TASKS_PATH == "/tasks"
        assert config.WORKDAY_TIME_TRACKING_PATH == "/time-tracking"
        assert config.WORKDAY_HOME_PATH == "/home"
        assert config.PLAYWRIGHT_HEADLESS is True
        assert config.PLAYWRIGHT_TIMEOUT == 30000
        assert config.BROWSER_STRATEGY == "headless_first"

    def test_computed_urls(self, dummy_env):
        config = PipelineConfig()  # type: ignore[call-arg]
        assert config.tasks_url == "https://workday.example.com/tasks"
        assert config.time_tracking_url == "https://workday.example.com/time-tracking"
        assert config.home_url == "https://workday.example.com/home"

    def test_missing_required_var_raises(self, monkeypatch):
        # WORKDAY_BASE_URL is required and has no default
        monkeypatch.delenv("WORKDAY_BASE_URL", raising=False)
        with pytest.raises(Exception):
            # Disable .env file so the required var is truly missing
            PipelineConfig(_env_file=None)  # type: ignore[call-arg]
