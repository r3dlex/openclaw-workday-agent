defmodule Orchestrator.Browser.Manager do
  @moduledoc """
  GenServer that manages browser automation strategy.

  Supports three strategies:
  - :headless_first — try headless (Python/Playwright), fall back to CDP relay
  - :headless_only — headless only, no fallback
  - :relay_only — CDP relay only, no headless
  """

  use GenServer
  require Logger

  alias Orchestrator.Browser.{Headless, Relay}

  defstruct strategy: :headless_first,
            headless_healthy: true,
            relay_healthy: true

  # Client API

  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  @doc """
  Execute a browser action using the configured strategy.
  """
  @spec execute(atom(), map()) :: {:ok, term()} | {:error, term()}
  def execute(action, params \\ %{}) do
    GenServer.call(__MODULE__, {:execute, action, params}, 60_000)
  end

  @doc """
  Get the current browser manager status.
  """
  @spec status() :: map()
  def status do
    GenServer.call(__MODULE__, :status)
  end

  @doc """
  Mark a backend as healthy or unhealthy.
  """
  @spec mark_health(atom(), boolean()) :: :ok
  def mark_health(backend, healthy) when backend in [:headless, :relay] do
    GenServer.cast(__MODULE__, {:mark_health, backend, healthy})
  end

  # Server callbacks

  @impl true
  def init(_opts) do
    strategy = Application.get_env(:orchestrator, :browser_strategy, :headless_first)
    {:ok, %__MODULE__{strategy: strategy}}
  end

  @impl true
  def handle_call({:execute, action, params}, _from, state) do
    {result, state} = do_execute(action, params, state)
    {:reply, result, state}
  end

  @impl true
  def handle_call(:status, _from, state) do
    {:reply,
     %{
       strategy: state.strategy,
       headless_healthy: state.headless_healthy,
       relay_healthy: state.relay_healthy
     }, state}
  end

  @impl true
  def handle_cast({:mark_health, :headless, healthy}, state) do
    {:noreply, %{state | headless_healthy: healthy}}
  end

  @impl true
  def handle_cast({:mark_health, :relay, healthy}, state) do
    {:noreply, %{state | relay_healthy: healthy}}
  end

  # Private

  defp do_execute(action, params, %{strategy: :headless_first} = state) do
    if state.headless_healthy do
      case Headless.send_action(action, params) do
        {:ok, _} = result ->
          {result, state}

        {:error, reason} ->
          Logger.warning("Headless failed (#{reason}), falling back to relay")
          state = %{state | headless_healthy: false}
          try_relay(action, params, state)
      end
    else
      try_relay(action, params, state)
    end
  end

  defp do_execute(action, params, %{strategy: :headless_only} = state) do
    result = Headless.send_action(action, params)

    case result do
      {:error, _} -> {result, %{state | headless_healthy: false}}
      _ -> {result, state}
    end
  end

  defp do_execute(action, params, %{strategy: :relay_only} = state) do
    try_relay(action, params, state)
  end

  defp try_relay(action, params, state) do
    if state.relay_healthy do
      case Relay.execute(action, params) do
        {:ok, _} = result ->
          {result, state}

        {:error, _} = error ->
          {error, %{state | relay_healthy: false}}
      end
    else
      {{:error, "no healthy browser backend available"}, state}
    end
  end
end
