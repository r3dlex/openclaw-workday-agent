defmodule Orchestrator do
  @moduledoc """
  Public API for the Workday automation orchestrator.

  Coordinates headless browser automation (Python/Playwright) with
  fallback to CDP relay (Node.js scripts).
  """

  alias Orchestrator.Pipeline.Runner

  @doc """
  Run a named pipeline with optional parameters.

  ## Examples

      Orchestrator.run_pipeline(:task_approval, %{task_id: "12345"})
      Orchestrator.run_pipeline(:sso_login)
  """
  @spec run_pipeline(atom(), map()) :: {:ok, map()} | {:error, term()}
  def run_pipeline(name, params \\ %{}) do
    Runner.run(name, params)
  end

  @doc """
  Get the current status of the orchestrator.

  Returns the state of the pipeline runner and browser manager.
  """
  @spec get_status() :: map()
  def get_status do
    %{
      pipeline: Runner.status(),
      browser: Orchestrator.Browser.Manager.status()
    }
  end
end
