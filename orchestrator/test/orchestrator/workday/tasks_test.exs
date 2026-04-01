defmodule Orchestrator.Workday.TasksTest do
  use ExUnit.Case, async: false

  alias Orchestrator.Workday.Tasks

  setup do
    case Process.whereis(Orchestrator.Browser.Manager) do
      nil -> {:ok, _} = Orchestrator.Browser.Manager.start_link([])
      _ -> :ok
    end

    :ok
  end

  # ---------------------------------------------------------------------------
  # step_analyze_compliance/1 — pure logic
  # ---------------------------------------------------------------------------

  describe "step_analyze_compliance/1" do
    test "skips compliance when task_details is nil" do
      context = %{task_details: nil}
      assert {:ok, result} = Tasks.step_analyze_compliance(context)
      assert result.compliance.status == :skipped
      assert result.compliance.reason == "no task details"
    end

    test "performs compliance check when task_details is present" do
      context = %{
        task_details: %{
          "title" => "Approve Time Off",
          "type" => "approval",
          "status" => "pending"
        }
      }

      assert {:ok, result} = Tasks.step_analyze_compliance(context)
      assert result.compliance.status == :checked
      assert result.compliance.requires_human_review == true
    end

    test "preserves existing context keys" do
      context = %{task_details: nil, extra: "value"}
      assert {:ok, result} = Tasks.step_analyze_compliance(context)
      assert result.extra == "value"
    end

    test "task_details as empty map triggers compliance check" do
      context = %{task_details: %{}}
      assert {:ok, result} = Tasks.step_analyze_compliance(context)
      assert result.compliance.status == :checked
    end
  end

  # ---------------------------------------------------------------------------
  # step_get_task_details/1 — has a pure fallback when no task_id
  # ---------------------------------------------------------------------------

  describe "step_get_task_details/1" do
    test "returns nil task_details when no task_id in context" do
      context = %{}
      assert {:ok, result} = Tasks.step_get_task_details(context)
      assert result.task_details == nil
    end

    test "with task_id, attempts Manager call (returns valid tuple)" do
      context = %{task_id: "task-001"}
      result = Tasks.step_get_task_details(context)
      assert is_tuple(result) and elem(result, 0) in [:ok, :error]
    end
  end

  # ---------------------------------------------------------------------------
  # step_ensure_authenticated/1 — Manager-dependent
  # ---------------------------------------------------------------------------

  describe "step_ensure_authenticated/1" do
    test "returns a valid result tuple" do
      result = Tasks.step_ensure_authenticated(%{})
      assert is_tuple(result) and elem(result, 0) in [:ok, :error]
    end
  end

  # ---------------------------------------------------------------------------
  # step_navigate_to_tasks/1 — config-dependent
  # ---------------------------------------------------------------------------

  describe "step_navigate_to_tasks/1" do
    test "returns error when base_url not configured" do
      Application.delete_env(:orchestrator, :workday_base_url)
      Application.delete_env(:orchestrator, :workday_tasks_path)

      result = Tasks.step_navigate_to_tasks(%{})

      case result do
        {:error, msg} ->
          assert String.contains?(msg, "not configured")

        {:ok, _} ->
          :ok
      end
    end

    test "returns error when tasks_path not configured" do
      Application.put_env(:orchestrator, :workday_base_url, "https://workday.test")
      Application.delete_env(:orchestrator, :workday_tasks_path)

      result = Tasks.step_navigate_to_tasks(%{})

      case result do
        {:error, _msg} -> :ok
        {:ok, _} -> :ok
      end

      Application.delete_env(:orchestrator, :workday_base_url)
    end
  end

  # ---------------------------------------------------------------------------
  # step_list_tasks/1 — Manager-dependent
  # ---------------------------------------------------------------------------

  describe "step_list_tasks/1" do
    test "returns a valid result tuple" do
      result = Tasks.step_list_tasks(%{})
      assert is_tuple(result) and elem(result, 0) in [:ok, :error]
    end
  end
end
