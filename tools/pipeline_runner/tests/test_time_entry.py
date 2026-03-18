"""Tests for pipeline_runner.actions.time_entry."""

import pytest

from pipeline_runner.actions.time_entry import validate_entry


class TestValidateEntry:
    def test_valid_entry_within_flex(self):
        entry = {"hours": 8, "start_time": "08:00", "end_time": "16:30"}
        result = validate_entry(entry)
        assert result["valid"] is True
        assert result["errors"] == []

    def test_rejects_before_flex_start(self):
        entry = {"hours": 8, "start_time": "06:00", "end_time": "14:00"}
        result = validate_entry(entry)
        assert result["valid"] is False
        assert any("before flex frame" in e for e in result["errors"])

    def test_rejects_after_flex_end(self):
        entry = {"hours": 8, "start_time": "11:00", "end_time": "20:00"}
        result = validate_entry(entry)
        assert result["valid"] is False
        assert any("after flex frame" in e for e in result["errors"])

    def test_warns_on_exceeding_max_hours(self):
        entry = {"hours": 11, "start_time": "07:00", "end_time": "18:00"}
        result = validate_entry(entry)
        assert result["valid"] is True  # warning, not error
        assert any("exceed maximum" in w for w in result["warnings"])

    def test_warns_on_late_start_vs_core(self):
        entry = {"hours": 6, "start_time": "10:00", "end_time": "16:00"}
        result = validate_entry(entry)
        assert result["valid"] is True
        assert any("after core hours start" in w for w in result["warnings"])

    def test_warns_on_early_end_vs_core(self):
        entry = {"hours": 6, "start_time": "07:00", "end_time": "13:00"}
        result = validate_entry(entry)
        assert result["valid"] is True
        assert any("before core hours end" in w for w in result["warnings"])

    def test_rejects_negative_hours(self):
        entry = {"hours": -1, "start_time": "09:00", "end_time": "17:00"}
        result = validate_entry(entry)
        assert result["valid"] is False
        assert any("negative" in e for e in result["errors"])

    def test_custom_rules(self):
        entry = {"hours": 6, "start_time": "08:00", "end_time": "14:00"}
        rules = {"max_daily_hours": 5, "flex_start": "07:00", "flex_end": "19:00",
                 "core_start": "09:00", "core_end": "16:00"}
        result = validate_entry(entry, rules)
        assert any("exceed maximum" in w for w in result["warnings"])

    def test_no_times_provided(self):
        entry = {"hours": 8}
        result = validate_entry(entry)
        assert result["valid"] is True
        assert result["errors"] == []
