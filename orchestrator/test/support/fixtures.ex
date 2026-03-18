defmodule Orchestrator.Test.Fixtures do
  @moduledoc """
  Test fixtures and mock step modules for pipeline testing.
  """

  alias Orchestrator.Pipeline.Step

  defmodule SuccessStep do
    @moduledoc false

    def execute(context) do
      {:ok, Map.put(context, :step_executed, true)}
    end

    def add_value(context, key, value) do
      {:ok, Map.put(context, key, value)}
    end
  end

  defmodule FailingStep do
    @moduledoc false

    def execute(_context) do
      {:error, "intentional test failure"}
    end
  end

  defmodule CountingStep do
    @moduledoc false

    def execute(context) do
      count = Map.get(context, :step_count, 0)
      {:ok, Map.put(context, :step_count, count + 1)}
    end
  end

  @doc """
  Build a successful pipeline with the given number of counting steps.
  """
  def counting_steps(n) do
    for i <- 1..n do
      %Step{
        name: "counting_step_#{i}",
        module: CountingStep,
        function: :execute
      }
    end
  end

  @doc """
  A single success step.
  """
  def success_step(name \\ "success") do
    %Step{name: name, module: SuccessStep, function: :execute}
  end

  @doc """
  A single failing step.
  """
  def failing_step(name \\ "failure") do
    %Step{name: name, module: FailingStep, function: :execute}
  end

  @doc """
  Sample task data for testing.
  """
  def sample_task do
    %{
      "id" => "task-001",
      "title" => "Approve Time Off Request",
      "type" => "approval",
      "status" => "pending"
    }
  end

  @doc """
  Sample time entries for testing.
  """
  def sample_time_entries do
    [
      %{"date" => "2026-03-16", "hours" => 8, "project" => "PROJ-001"},
      %{"date" => "2026-03-17", "hours" => 7.5, "project" => "PROJ-001"},
      %{"date" => "2026-03-18", "hours" => 8, "project" => "PROJ-002"}
    ]
  end
end
