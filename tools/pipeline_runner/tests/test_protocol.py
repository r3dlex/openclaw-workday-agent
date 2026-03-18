"""Tests for pipeline_runner.protocol."""

import json

import pytest

from pipeline_runner.protocol import Request, Response, format_response, parse_request


class TestParseRequest:
    def test_valid_json(self):
        line = json.dumps({"action": "login", "params": {"key": "val"}, "request_id": "r1"})
        req = parse_request(line)
        assert req.action == "login"
        assert req.params == {"key": "val"}
        assert req.request_id == "r1"

    def test_minimal_request(self):
        line = json.dumps({"action": "ping"})
        req = parse_request(line)
        assert req.action == "ping"
        assert req.params == {}
        assert req.request_id == ""

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError, match="Invalid JSON"):
            parse_request("{not valid json")

    def test_empty_line_raises(self):
        with pytest.raises(ValueError, match="Empty input"):
            parse_request("")

    def test_missing_action_raises(self):
        with pytest.raises(ValueError, match="Missing or invalid 'action'"):
            parse_request(json.dumps({"params": {}}))

    def test_non_object_raises(self):
        with pytest.raises(ValueError, match="Expected JSON object"):
            parse_request(json.dumps([1, 2, 3]))


class TestFormatResponse:
    def test_ok_response(self):
        resp = Response(status="ok", result={"count": 5}, request_id="r1")
        out = format_response(resp)
        data = json.loads(out)
        assert data["status"] == "ok"
        assert data["result"]["count"] == 5
        assert data["request_id"] == "r1"
        assert "error" not in data

    def test_error_response(self):
        resp = Response(status="error", error="something broke", request_id="r2")
        out = format_response(resp)
        data = json.loads(out)
        assert data["status"] == "error"
        assert data["error"] == "something broke"
        assert "result" not in data

    def test_no_trailing_newline(self):
        resp = Response(status="ok", result={})
        out = format_response(resp)
        assert not out.endswith("\n")


class TestRoundTrip:
    def test_request_response_roundtrip(self):
        original = {"action": "list_tasks", "params": {"limit": 10}, "request_id": "abc"}
        req = parse_request(json.dumps(original))

        resp = Response(status="ok", result={"tasks": []}, request_id=req.request_id)
        out = format_response(resp)
        data = json.loads(out)

        assert data["request_id"] == "abc"
        assert data["status"] == "ok"
