defmodule OrchestratorTest do
  use ExUnit.Case, async: false

  setup do
    case Process.whereis(Orchestrator.Browser.Manager) do
      nil -> {:ok, _} = Orchestrator.Browser.Manager.start_link([])
      _ -> :ok
    end

    case Process.whereis(Orchestrator.Pipeline.Runner) do
      nil -> {:ok, _} = Orchestrator.Pipeline.Runner.start_link([])
      _ -> :ok
    end

    :ok
  end

  describe "run_pipeline/2" do
    test "returns error for unknown pipeline" do
      assert {:error, :not_found} = Orchestrator.run_pipeline(:nonexistent)
    end

    test "run_pipeline/1 with default params uses empty map" do
      # Still returns :not_found for unknown; proves arity-1 call works
      assert {:error, :not_found} = Orchestrator.run_pipeline(:does_not_exist)
    end
  end

  describe "get_status/0" do
    test "returns a map with pipeline and browser keys" do
      status = Orchestrator.get_status()
      assert is_map(status)
      assert Map.has_key?(status, :pipeline)
      assert Map.has_key?(status, :browser)
    end

    test "pipeline status includes status and current_pipeline fields" do
      %{pipeline: pipeline_status} = Orchestrator.get_status()
      assert Map.has_key?(pipeline_status, :status)
      assert Map.has_key?(pipeline_status, :current_pipeline)
    end

    test "browser status includes strategy and health fields" do
      %{browser: browser_status} = Orchestrator.get_status()
      assert Map.has_key?(browser_status, :strategy)
      assert Map.has_key?(browser_status, :headless_healthy)
      assert Map.has_key?(browser_status, :relay_healthy)
    end
  end
end
