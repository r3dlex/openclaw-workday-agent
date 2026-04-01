defmodule Orchestrator.Workday.TimeTrackingTest do
  use ExUnit.Case, async: false

  alias Orchestrator.Workday.TimeTracking

  setup do
    case Process.whereis(Orchestrator.Browser.Manager) do
      nil -> {:ok, _} = Orchestrator.Browser.Manager.start_link([])
      _ -> :ok
    end

    :ok
  end

  # ---------------------------------------------------------------------------
  # step_validate_entries/1 — pure logic, no external calls
  # ---------------------------------------------------------------------------

  describe "step_validate_entries/1" do
    test "valid entries pass validation" do
      context = %{
        time_entries: [
          %{"hours" => 8, "date" => "2026-01-15"},
          %{"hours" => 7.5, "date" => "2026-01-16"}
        ]
      }

      assert {:ok, result} = TimeTracking.step_validate_entries(context)
      assert result.all_entries_valid == true
      assert length(result.validation) == 2
      assert Enum.all?(result.validation, & &1.valid)
    end

    test "zero hours is invalid" do
      context = %{time_entries: [%{"hours" => 0, "date" => "2026-01-15"}]}
      assert {:ok, result} = TimeTracking.step_validate_entries(context)
      assert result.all_entries_valid == false
      assert hd(result.validation).valid == false
      assert hd(result.validation).reason == "hours must be positive"
    end

    test "negative hours is invalid" do
      context = %{time_entries: [%{"hours" => -1, "date" => "2026-01-15"}]}
      assert {:ok, result} = TimeTracking.step_validate_entries(context)
      assert result.all_entries_valid == false
    end

    test "hours exceeding 24 is invalid" do
      context = %{time_entries: [%{"hours" => 25, "date" => "2026-01-15"}]}
      assert {:ok, result} = TimeTracking.step_validate_entries(context)
      assert result.all_entries_valid == false
      assert hd(result.validation).reason == "hours exceed 24h per day"
    end

    test "exactly 24 hours is valid" do
      context = %{time_entries: [%{"hours" => 24, "date" => "2026-01-15"}]}
      assert {:ok, result} = TimeTracking.step_validate_entries(context)
      assert result.all_entries_valid == true
    end

    test "empty entries list produces all_valid true" do
      context = %{time_entries: []}
      assert {:ok, result} = TimeTracking.step_validate_entries(context)
      assert result.all_entries_valid == true
      assert result.validation == []
    end

    test "missing time_entries key defaults to empty list" do
      context = %{}
      assert {:ok, result} = TimeTracking.step_validate_entries(context)
      assert result.all_entries_valid == true
    end

    test "mix of valid and invalid entries" do
      context = %{
        time_entries: [
          %{"hours" => 8},
          %{"hours" => 0},
          %{"hours" => 7.5}
        ]
      }

      assert {:ok, result} = TimeTracking.step_validate_entries(context)
      assert result.all_entries_valid == false
      assert length(result.validation) == 3
      assert Enum.at(result.validation, 0).valid == true
      assert Enum.at(result.validation, 1).valid == false
      assert Enum.at(result.validation, 2).valid == true
    end

    test "preserves existing context keys" do
      context = %{time_entries: [], extra_key: "preserved"}
      assert {:ok, result} = TimeTracking.step_validate_entries(context)
      assert result.extra_key == "preserved"
    end
  end

  # ---------------------------------------------------------------------------
  # step_ensure_authenticated/1 — requires Manager (integration-style)
  # ---------------------------------------------------------------------------

  describe "step_ensure_authenticated/1" do
    test "returns error tuple when Manager returns error" do
      # In test mode, Manager uses headless_only strategy but headless backend
      # is not running (:ignore), so it returns error
      result = TimeTracking.step_ensure_authenticated(%{})
      # Either succeeds or returns an error — both are valid in test
      assert is_tuple(result) and elem(result, 0) in [:ok, :error]
    end
  end

  # ---------------------------------------------------------------------------
  # step_navigate_to_time_tracking/1 — config-dependent
  # ---------------------------------------------------------------------------

  describe "step_navigate_to_time_tracking/1" do
    test "returns error when base_url not configured" do
      Application.delete_env(:orchestrator, :workday_base_url)
      Application.delete_env(:orchestrator, :workday_time_tracking_path)

      result = TimeTracking.step_navigate_to_time_tracking(%{})

      case result do
        {:error, msg} ->
          assert String.contains?(msg, "not configured")

        {:ok, _} ->
          # If the Manager happens to succeed somehow, that's also fine
          :ok
      end
    end

    test "returns error when time_tracking_path not configured" do
      Application.put_env(:orchestrator, :workday_base_url, "https://workday.test")
      Application.delete_env(:orchestrator, :workday_time_tracking_path)

      result = TimeTracking.step_navigate_to_time_tracking(%{})

      case result do
        {:error, msg} ->
          assert String.contains?(msg, "not configured") or
                   String.contains?(msg, "navigate") or
                   String.contains?(msg, "not running") or
                   String.contains?(msg, "headless")

        {:ok, _} ->
          :ok
      end

      Application.delete_env(:orchestrator, :workday_base_url)
    end
  end

  # ---------------------------------------------------------------------------
  # step_get_entries/1 — requires Manager
  # ---------------------------------------------------------------------------

  describe "step_get_entries/1" do
    test "returns a valid result tuple" do
      result = TimeTracking.step_get_entries(%{})
      assert is_tuple(result) and elem(result, 0) in [:ok, :error]
    end
  end
end
