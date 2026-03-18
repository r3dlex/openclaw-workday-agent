defmodule Orchestrator.Workday.Tasks do
  @moduledoc """
  Task approval pipeline steps for Workday.
  """

  alias Orchestrator.Browser.Manager

  @doc """
  Ensure the user is authenticated before proceeding.
  """
  @spec step_ensure_authenticated(map()) :: {:ok, map()} | {:error, String.t()}
  def step_ensure_authenticated(context) do
    case Manager.execute(:check_auth, %{}) do
      {:ok, %{"authenticated" => true}} ->
        {:ok, Map.put(context, :authenticated, true)}

      {:ok, _} ->
        {:error, "not authenticated — run sso_login pipeline first"}

      {:error, reason} ->
        {:error, "auth check failed: #{reason}"}
    end
  end

  @doc """
  Navigate to the Workday tasks/inbox page.
  """
  @spec step_navigate_to_tasks(map()) :: {:ok, map()} | {:error, String.t()}
  def step_navigate_to_tasks(context) do
    base_url = Application.get_env(:orchestrator, :workday_base_url)
    tasks_path = Application.get_env(:orchestrator, :workday_tasks_path)

    case {base_url, tasks_path} do
      {nil, _} ->
        {:error, "WORKDAY_BASE_URL not configured"}

      {_, nil} ->
        {:error, "WORKDAY_TASKS_PATH not configured"}

      {url, path} ->
        target = url <> path

        case Manager.execute(:navigate, %{url: target}) do
          {:ok, result} ->
            {:ok, Map.merge(context, %{tasks_url: target, page_state: result})}

          {:error, reason} ->
            {:error, "failed to navigate to tasks: #{reason}"}
        end
    end
  end

  @doc """
  List available tasks on the current page.
  """
  @spec step_list_tasks(map()) :: {:ok, map()} | {:error, String.t()}
  def step_list_tasks(context) do
    case Manager.execute(:extract_tasks, %{}) do
      {:ok, %{"tasks" => tasks}} ->
        {:ok, Map.put(context, :tasks, tasks)}

      {:ok, result} ->
        {:ok, Map.put(context, :tasks, []) |> Map.put(:task_extract_result, result)}

      {:error, reason} ->
        {:error, "failed to list tasks: #{reason}"}
    end
  end

  @doc """
  Get details for a specific task (uses task_id from context).
  """
  @spec step_get_task_details(map()) :: {:ok, map()} | {:error, String.t()}
  def step_get_task_details(%{task_id: task_id} = context) do
    case Manager.execute(:get_task_detail, %{task_id: task_id}) do
      {:ok, details} ->
        {:ok, Map.put(context, :task_details, details)}

      {:error, reason} ->
        {:error, "failed to get task details: #{reason}"}
    end
  end

  def step_get_task_details(context) do
    {:ok, Map.put(context, :task_details, nil)}
  end

  @doc """
  Analyze whether the task complies with organizational policies.
  """
  @spec step_analyze_compliance(map()) :: {:ok, map()} | {:error, String.t()}
  def step_analyze_compliance(context) do
    details = Map.get(context, :task_details)

    cond do
      is_nil(details) ->
        {:ok, Map.put(context, :compliance, %{status: :skipped, reason: "no task details"})}

      true ->
        {:ok,
         Map.put(context, :compliance, %{
           status: :checked,
           details: details,
           requires_human_review: true
         })}
    end
  end
end
