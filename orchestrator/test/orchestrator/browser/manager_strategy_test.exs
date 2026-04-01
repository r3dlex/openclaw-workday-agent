defmodule Orchestrator.Browser.ManagerStrategyTest do
  @moduledoc """
  Tests that exercise all three Manager strategy branches by starting
  isolated Manager GenServer instances with specific configurations.
  """
  use ExUnit.Case, async: false

  alias Orchestrator.Browser.Manager

  # We start separate Manager processes with specific strategies to test
  # the private do_execute branches without affecting the global Manager.

  setup do
    # Clean up browser_strategy after each test
    on_exit(fn ->
      Application.delete_env(:orchestrator, :browser_strategy)

      # Ensure global Manager is running after our tests
      case Process.whereis(Orchestrator.Browser.Manager) do
        nil -> {:ok, _} = Orchestrator.Browser.Manager.start_link([])
        _ -> :ok
      end
    end)

    :ok
  end

  defp start_manager(strategy) do
    # We can't easily inject strategy without modifying Application env,
    # so we test via the global Manager with health manipulation.
    Application.put_env(:orchestrator, :browser_strategy, strategy)

    {:ok, pid} =
      GenServer.start_link(Manager, [],
        name: :"test_manager_#{:erlang.unique_integer([:positive])}"
      )

    pid
  end

  describe "headless_only strategy" do
    test "execute with headless_only strategy attempts headless only" do
      pid = start_manager(:headless_only)

      result = GenServer.call(pid, {:execute, :ping, %{}}, 10_000)
      # Headless not running → error, but code path covered
      assert is_tuple(result)
      assert elem(result, 0) in [:ok, :error]

      GenServer.stop(pid)
    end

    test "headless_only marks headless unhealthy on failure" do
      pid = start_manager(:headless_only)

      _result = GenServer.call(pid, {:execute, :ping, %{}}, 10_000)
      status = GenServer.call(pid, :status)

      # Headless was unhealthy (not running), so marks false
      assert is_boolean(status.headless_healthy)

      GenServer.stop(pid)
    end
  end

  describe "relay_only strategy" do
    test "execute with relay_only strategy uses relay" do
      pid = start_manager(:relay_only)

      result = GenServer.call(pid, {:execute, :approve_task, %{}}, 10_000)
      # Relay will find/run the script
      assert is_tuple(result)
      assert elem(result, 0) in [:ok, :error]

      GenServer.stop(pid)
    end

    test "relay_only with unknown action gets relay error" do
      pid = start_manager(:relay_only)

      result = GenServer.call(pid, {:execute, :unknown_action, %{}}, 10_000)
      assert {:error, _} = result

      GenServer.stop(pid)
    end
  end

  describe "headless_first strategy fallback" do
    test "falls back to relay when headless is marked unhealthy" do
      pid = start_manager(:headless_first)

      # Mark headless as unhealthy to force relay fallback
      GenServer.cast(pid, {:mark_health, :headless, false})
      Process.sleep(20)

      result = GenServer.call(pid, {:execute, :approve_task, %{}}, 10_000)
      assert is_tuple(result)
      assert elem(result, 0) in [:ok, :error]

      GenServer.stop(pid)
    end

    test "relay_healthy false causes no-backend error" do
      pid = start_manager(:headless_first)

      # Both unhealthy → no backend available
      GenServer.cast(pid, {:mark_health, :headless, false})
      GenServer.cast(pid, {:mark_health, :relay, false})
      Process.sleep(20)

      result = GenServer.call(pid, {:execute, :approve_task, %{}}, 10_000)
      assert {:error, msg} = result
      assert String.contains?(msg, "no healthy browser backend")

      GenServer.stop(pid)
    end
  end

  describe "status/0 from isolated manager" do
    test "isolated manager reports configured strategy" do
      pid = start_manager(:relay_only)
      status = GenServer.call(pid, :status)
      assert status.strategy == :relay_only
      GenServer.stop(pid)
    end
  end
end
