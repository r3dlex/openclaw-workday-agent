defmodule Orchestrator.Pipeline.Runner do
  @moduledoc """
  GenServer that executes pipelines sequentially, threading context
  through each step.
  """

  use GenServer
  require Logger

  alias Orchestrator.Pipeline.{Registry, Step}

  defstruct current_pipeline: nil, status: :idle

  # Client API

  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  @doc """
  Run a named pipeline with the given parameters as initial context.
  """
  @spec run(atom(), map()) :: {:ok, map()} | {:error, term()}
  def run(pipeline_name, params \\ %{}) do
    GenServer.call(__MODULE__, {:run, pipeline_name, params}, :infinity)
  end

  @doc """
  Get the current runner status.
  """
  @spec status() :: map()
  def status do
    GenServer.call(__MODULE__, :status)
  end

  # Server callbacks

  @impl true
  def init(_opts) do
    {:ok, %__MODULE__{}}
  end

  @impl true
  def handle_call({:run, pipeline_name, params}, _from, state) do
    case Registry.get(pipeline_name) do
      {:ok, steps} ->
        state = %{state | current_pipeline: pipeline_name, status: :running}
        result = execute_steps(steps, params)
        state = %{state | current_pipeline: nil, status: :idle}
        {:reply, result, state}

      {:error, :not_found} = error ->
        {:reply, error, state}
    end
  end

  @impl true
  def handle_call(:status, _from, state) do
    {:reply,
     %{
       current_pipeline: state.current_pipeline,
       status: state.status
     }, state}
  end

  # Private

  defp execute_steps([], context), do: {:ok, context}

  defp execute_steps([step | rest], context) do
    Logger.debug("Executing step: #{step.name}")

    case Step.execute(step, context) do
      {:ok, updated_context} ->
        Logger.debug("Step #{step.name} completed successfully")
        execute_steps(rest, updated_context)

      {:error, reason} = error ->
        Logger.error("Step #{step.name} failed: #{reason}")
        error
    end
  end
end
