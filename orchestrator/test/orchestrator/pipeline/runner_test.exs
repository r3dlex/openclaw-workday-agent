defmodule Orchestrator.Pipeline.RunnerTest do
  use ExUnit.Case, async: false

  alias Orchestrator.Pipeline.{Runner, Step}
  alias Orchestrator.Test.Fixtures
  alias Orchestrator.Test.Fixtures.SuccessStep

  # We test the step execution logic directly since the GenServer
  # depends on the Registry which has real pipeline definitions.

  setup do
    case Process.whereis(Orchestrator.Browser.Manager) do
      nil -> {:ok, _} = Orchestrator.Browser.Manager.start_link([])
      _ -> :ok
    end

    case Process.whereis(Runner) do
      nil -> {:ok, _} = Runner.start_link([])
      _ -> :ok
    end

    :ok
  end

  describe "Step.execute/2" do
    test "successful step returns updated context" do
      step = Fixtures.success_step()
      assert {:ok, context} = Step.execute(step, %{})
      assert context.step_executed == true
    end

    test "failing step returns error" do
      step = Fixtures.failing_step()
      assert {:error, "intentional test failure"} = Step.execute(step, %{})
    end

    test "step with extra args passes them through" do
      step = %Step{
        name: "add_value",
        module: SuccessStep,
        function: :add_value,
        args: [:my_key, "my_value"]
      }

      assert {:ok, context} = Step.execute(step, %{})
      assert context.my_key == "my_value"
    end
  end

  describe "sequential step execution" do
    test "multiple counting steps execute in order" do
      steps = Fixtures.counting_steps(3)
      context = %{}

      result =
        Enum.reduce_while(steps, {:ok, context}, fn step, {:ok, ctx} ->
          case Step.execute(step, ctx) do
            {:ok, _} = ok -> {:cont, ok}
            {:error, _} = err -> {:halt, err}
          end
        end)

      assert {:ok, final_context} = result
      assert final_context.step_count == 3
    end

    test "execution stops on first failure" do
      steps = [
        Fixtures.success_step("first"),
        Fixtures.failing_step("second"),
        Fixtures.success_step("third")
      ]

      context = %{steps_run: []}

      result =
        Enum.reduce_while(steps, {:ok, context}, fn step, {:ok, ctx} ->
          case Step.execute(step, ctx) do
            {:ok, updated} ->
              {:cont, {:ok, Map.update(updated, :steps_run, [step.name], &[step.name | &1])}}

            {:error, _} = err ->
              {:halt, err}
          end
        end)

      assert {:error, "intentional test failure"} = result
    end
  end

  describe "Runner GenServer" do
    test "status returns idle when no pipeline is running" do
      assert %{status: :idle, current_pipeline: nil} = Runner.status()
    end

    test "run with unknown pipeline returns error" do
      assert {:error, :not_found} = Runner.run(:nonexistent_pipeline)
    end
  end
end
