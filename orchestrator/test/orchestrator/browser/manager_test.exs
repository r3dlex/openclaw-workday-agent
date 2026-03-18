defmodule Orchestrator.Browser.ManagerTest do
  use ExUnit.Case, async: false

  alias Orchestrator.Browser.Manager

  describe "status/0" do
    test "returns current strategy and health" do
      status = Manager.status()

      assert Map.has_key?(status, :strategy)
      assert Map.has_key?(status, :headless_healthy)
      assert Map.has_key?(status, :relay_healthy)
      assert is_boolean(status.headless_healthy)
      assert is_boolean(status.relay_healthy)
    end
  end

  describe "mark_health/2" do
    test "marks headless as unhealthy" do
      Manager.mark_health(:headless, false)
      # Give cast time to process
      Process.sleep(50)
      status = Manager.status()
      assert status.headless_healthy == false

      # Restore
      Manager.mark_health(:headless, true)
      Process.sleep(50)
    end

    test "marks relay as unhealthy" do
      Manager.mark_health(:relay, false)
      Process.sleep(50)
      status = Manager.status()
      assert status.relay_healthy == false

      # Restore
      Manager.mark_health(:relay, true)
      Process.sleep(50)
    end
  end

  describe "strategy behavior" do
    test "headless_first is the default strategy" do
      status = Manager.status()
      assert status.strategy == :headless_first
    end
  end
end
