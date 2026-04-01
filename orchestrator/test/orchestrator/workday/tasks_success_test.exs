defmodule Orchestrator.Workday.TasksSuccessTest do
  @moduledoc """
  Tests Tasks step functions with a MockManager that returns success responses.
  """
  use ExUnit.Case, async: false

  alias Orchestrator.Workday.Tasks
  alias Orchestrator.Test.MockManager

  defp with_mock(responses, fun), do: MockManager.replace_for_test(responses, fun)

  describe "step_ensure_authenticated/1" do
    test "returns ok when authenticated" do
      with_mock(%{check_auth: {:ok, %{"authenticated" => true}}}, fn ->
        assert {:ok, ctx} = Tasks.step_ensure_authenticated(%{})
        assert ctx.authenticated == true
      end)
    end

    test "returns error when not authenticated" do
      with_mock(%{check_auth: {:ok, %{"authenticated" => false}}}, fn ->
        assert {:error, msg} = Tasks.step_ensure_authenticated(%{})
        assert String.contains?(msg, "not authenticated")
      end)
    end

    test "returns error when check_auth fails" do
      with_mock(%{check_auth: {:error, "connection failed"}}, fn ->
        assert {:error, msg} = Tasks.step_ensure_authenticated(%{})
        assert String.contains?(msg, "auth check failed")
      end)
    end
  end

  describe "step_navigate_to_tasks/1" do
    test "returns ok when navigation succeeds" do
      Application.put_env(:orchestrator, :workday_base_url, "https://workday.test")
      Application.put_env(:orchestrator, :workday_tasks_path, "/tasks")

      with_mock(%{navigate: {:ok, %{"loaded" => true}}}, fn ->
        assert {:ok, ctx} = Tasks.step_navigate_to_tasks(%{})
        assert ctx.tasks_url == "https://workday.test/tasks"
      end)

      Application.delete_env(:orchestrator, :workday_base_url)
      Application.delete_env(:orchestrator, :workday_tasks_path)
    end

    test "returns error when navigation fails" do
      Application.put_env(:orchestrator, :workday_base_url, "https://workday.test")
      Application.put_env(:orchestrator, :workday_tasks_path, "/tasks")

      with_mock(%{navigate: {:error, "timeout"}}, fn ->
        assert {:error, msg} = Tasks.step_navigate_to_tasks(%{})
        assert String.contains?(msg, "failed to navigate to tasks")
      end)

      Application.delete_env(:orchestrator, :workday_base_url)
      Application.delete_env(:orchestrator, :workday_tasks_path)
    end
  end

  describe "step_list_tasks/1" do
    test "returns ok with tasks when extract succeeds" do
      tasks = [%{"id" => "1", "title" => "Test Task"}]

      with_mock(%{extract_tasks: {:ok, %{"tasks" => tasks}}}, fn ->
        assert {:ok, ctx} = Tasks.step_list_tasks(%{})
        assert length(ctx.tasks) == 1
      end)
    end

    test "returns ok with empty tasks when result has no tasks key" do
      with_mock(%{extract_tasks: {:ok, %{"other" => "data"}}}, fn ->
        assert {:ok, ctx} = Tasks.step_list_tasks(%{})
        assert ctx.tasks == []
      end)
    end

    test "returns error when extract fails" do
      with_mock(%{extract_tasks: {:error, "scraping failed"}}, fn ->
        assert {:error, msg} = Tasks.step_list_tasks(%{})
        assert String.contains?(msg, "failed to list tasks")
      end)
    end
  end

  describe "step_get_task_details/1 with task_id" do
    test "returns ok with details when fetch succeeds" do
      details = %{"title" => "Test Task", "status" => "pending"}

      with_mock(%{get_task_detail: {:ok, details}}, fn ->
        assert {:ok, ctx} = Tasks.step_get_task_details(%{task_id: "task-001"})
        assert ctx.task_details["title"] == "Test Task"
      end)
    end

    test "returns error when detail fetch fails" do
      with_mock(%{get_task_detail: {:error, "not found"}}, fn ->
        assert {:error, msg} = Tasks.step_get_task_details(%{task_id: "task-999"})
        assert String.contains?(msg, "failed to get task details")
      end)
    end
  end
end
