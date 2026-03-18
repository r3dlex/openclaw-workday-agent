defmodule Orchestrator.Pipeline.Registry do
  @moduledoc """
  Registry of named pipeline definitions.

  Each pipeline is a list of `Step` structs that are executed sequentially
  by the Runner.
  """

  alias Orchestrator.Pipeline.Step
  alias Orchestrator.Workday.{SSO, Tasks, TimeTracking}

  @pipelines %{
    sso_login: [
      %Step{name: "navigate_to_workday", module: SSO, function: :step_navigate_to_workday},
      %Step{name: "detect_login_screen", module: SSO, function: :step_detect_login_screen},
      %Step{name: "click_provider", module: SSO, function: :step_click_provider},
      %Step{name: "fallback_direct_link", module: SSO, function: :step_fallback_direct_link},
      %Step{name: "verify_authenticated", module: SSO, function: :step_verify_authenticated}
    ],
    task_approval: [
      %Step{name: "ensure_authenticated", module: Tasks, function: :step_ensure_authenticated},
      %Step{name: "navigate_to_tasks", module: Tasks, function: :step_navigate_to_tasks},
      %Step{name: "list_tasks", module: Tasks, function: :step_list_tasks},
      %Step{name: "get_task_details", module: Tasks, function: :step_get_task_details},
      %Step{name: "analyze_compliance", module: Tasks, function: :step_analyze_compliance}
    ],
    time_tracking: [
      %Step{
        name: "ensure_authenticated",
        module: TimeTracking,
        function: :step_ensure_authenticated
      },
      %Step{
        name: "navigate_to_time_tracking",
        module: TimeTracking,
        function: :step_navigate_to_time_tracking
      },
      %Step{name: "get_entries", module: TimeTracking, function: :step_get_entries},
      %Step{name: "validate_entries", module: TimeTracking, function: :step_validate_entries}
    ]
  }

  @doc """
  Get the steps for a named pipeline.

  ## Examples

      iex> Orchestrator.Pipeline.Registry.get(:sso_login)
      {:ok, [%Orchestrator.Pipeline.Step{} | _]}

      iex> Orchestrator.Pipeline.Registry.get(:nonexistent)
      {:error, :not_found}
  """
  @spec get(atom()) :: {:ok, [Step.t()]} | {:error, :not_found}
  def get(name) when is_map_key(@pipelines, name) do
    {:ok, Map.fetch!(@pipelines, name)}
  end

  def get(_name), do: {:error, :not_found}

  @doc """
  List all registered pipeline names.
  """
  @spec list() :: [atom()]
  def list, do: Map.keys(@pipelines)
end
