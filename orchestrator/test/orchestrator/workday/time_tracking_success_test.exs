defmodule Orchestrator.Workday.TimeTrackingSuccessTest do
  @moduledoc """
  Tests TimeTracking step functions with a MockManager that returns success responses.
  """
  use ExUnit.Case, async: false

  alias Orchestrator.Workday.TimeTracking
  alias Orchestrator.Test.MockManager

  defp with_mock(responses, fun), do: MockManager.replace_for_test(responses, fun)

  describe "step_ensure_authenticated/1" do
    test "returns ok when authenticated" do
      with_mock(%{check_auth: {:ok, %{"authenticated" => true}}}, fn ->
        assert {:ok, ctx} = TimeTracking.step_ensure_authenticated(%{})
        assert ctx.authenticated == true
      end)
    end

    test "returns error when not authenticated" do
      with_mock(%{check_auth: {:ok, %{"status" => "logged_out"}}}, fn ->
        assert {:error, msg} = TimeTracking.step_ensure_authenticated(%{})
        assert String.contains?(msg, "not authenticated")
      end)
    end

    test "returns error when check fails" do
      with_mock(%{check_auth: {:error, "timeout"}}, fn ->
        assert {:error, msg} = TimeTracking.step_ensure_authenticated(%{})
        assert String.contains?(msg, "auth check failed")
      end)
    end
  end

  describe "step_navigate_to_time_tracking/1" do
    test "returns ok when navigation succeeds" do
      Application.put_env(:orchestrator, :workday_base_url, "https://workday.test")
      Application.put_env(:orchestrator, :workday_time_tracking_path, "/time-tracking")

      with_mock(%{navigate: {:ok, %{"loaded" => true}}}, fn ->
        assert {:ok, ctx} = TimeTracking.step_navigate_to_time_tracking(%{})
        assert ctx.time_tracking_url == "https://workday.test/time-tracking"
      end)

      Application.delete_env(:orchestrator, :workday_base_url)
      Application.delete_env(:orchestrator, :workday_time_tracking_path)
    end

    test "returns error when navigation fails" do
      Application.put_env(:orchestrator, :workday_base_url, "https://workday.test")
      Application.put_env(:orchestrator, :workday_time_tracking_path, "/time-tracking")

      with_mock(%{navigate: {:error, "connection refused"}}, fn ->
        assert {:error, msg} = TimeTracking.step_navigate_to_time_tracking(%{})
        assert String.contains?(msg, "failed to navigate to time tracking")
      end)

      Application.delete_env(:orchestrator, :workday_base_url)
      Application.delete_env(:orchestrator, :workday_time_tracking_path)
    end
  end

  describe "step_get_entries/1" do
    test "returns ok with entries list" do
      entries = [%{"date" => "2026-01-15", "hours" => 8}]

      with_mock(%{extract_time_entries: {:ok, %{"entries" => entries}}}, fn ->
        assert {:ok, ctx} = TimeTracking.step_get_entries(%{})
        assert length(ctx.time_entries) == 1
      end)
    end

    test "returns ok with empty entries when no entries key" do
      with_mock(%{extract_time_entries: {:ok, %{"other" => "data"}}}, fn ->
        assert {:ok, ctx} = TimeTracking.step_get_entries(%{})
        assert ctx.time_entries == []
      end)
    end

    test "returns error when extraction fails" do
      with_mock(%{extract_time_entries: {:error, "extraction failed"}}, fn ->
        assert {:error, msg} = TimeTracking.step_get_entries(%{})
        assert String.contains?(msg, "failed to get time entries")
      end)
    end
  end
end
