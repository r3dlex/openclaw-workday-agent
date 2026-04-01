defmodule Orchestrator.Test.MockManager do
  @moduledoc """
  A test double for Orchestrator.Browser.Manager that returns configurable responses.
  """
  use GenServer

  def start_link(opts \\ []) do
    responses = Keyword.get(opts, :responses, %{})
    GenServer.start_link(__MODULE__, responses, name: Orchestrator.Browser.Manager)
  end

  def init(responses) do
    {:ok, responses}
  end

  def handle_call({:execute, action, _params}, _from, responses) do
    result =
      case Map.get(responses, action) do
        nil -> {:error, "mock: no response configured for #{action}"}
        response -> response
      end

    {:reply, result, responses}
  end

  def handle_call(:status, _from, responses) do
    {:reply,
     %{
       strategy: :mock,
       headless_healthy: true,
       relay_healthy: true
     }, responses}
  end

  def handle_cast({:mark_health, _, _}, responses) do
    {:noreply, responses}
  end

  @doc """
  Replace the global Manager with a mock for the duration of a test.

  Stops the real Manager, starts a mock, runs fun/0, then restores.
  Always uses on_exit to ensure cleanup even if fun raises.
  """
  def replace_for_test(responses, fun, ctx \\ %{}) do
    _ = ctx

    # Stop the real Manager (must be done before starting mock with same name)
    stop_real_manager()

    # Start mock - handle edge case where Manager restarts quickly
    mock_pid =
      case start_link(responses: responses) do
        {:ok, pid} ->
          pid

        {:error, {:already_started, existing_pid}} ->
          # Stop the existing one and try again
          stop_named_manager(existing_pid)
          {:ok, pid} = start_link(responses: responses)
          pid
      end

    try do
      fun.()
    after
      # Stop mock
      if Process.alive?(mock_pid) do
        ref = Process.monitor(mock_pid)
        GenServer.stop(mock_pid, :normal)

        receive do
          {:DOWN, ^ref, :process, ^mock_pid, _} -> :ok
        after
          500 -> :ok
        end
      end

      # Restart real Manager
      ensure_manager_running()
    end
  end

  defp stop_real_manager do
    case Process.whereis(Orchestrator.Browser.Manager) do
      nil ->
        :ok

      pid ->
        stop_named_manager(pid)
    end
  end

  defp stop_named_manager(pid) do
    ref = Process.monitor(pid)
    GenServer.stop(pid, :normal)

    receive do
      {:DOWN, ^ref, :process, ^pid, _} -> :ok
    after
      1000 -> :ok
    end
  end

  defp ensure_manager_running do
    case Process.whereis(Orchestrator.Browser.Manager) do
      nil ->
        {:ok, _} = Orchestrator.Browser.Manager.start_link([])
        :ok

      _ ->
        :ok
    end
  end
end
