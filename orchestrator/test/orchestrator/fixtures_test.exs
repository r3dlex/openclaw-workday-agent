defmodule Orchestrator.Test.FixturesTest do
  use ExUnit.Case, async: true

  alias Orchestrator.Test.Fixtures

  describe "sample_task/0" do
    test "returns a map with expected fields" do
      task = Fixtures.sample_task()
      assert is_map(task)
      assert Map.has_key?(task, "id")
      assert Map.has_key?(task, "title")
      assert Map.has_key?(task, "type")
      assert Map.has_key?(task, "status")
    end
  end

  describe "sample_time_entries/0" do
    test "returns a list of time entries" do
      entries = Fixtures.sample_time_entries()
      assert is_list(entries)
      assert length(entries) > 0
    end

    test "each entry has date, hours, and project fields" do
      entries = Fixtures.sample_time_entries()

      for entry <- entries do
        assert Map.has_key?(entry, "date")
        assert Map.has_key?(entry, "hours")
        assert Map.has_key?(entry, "project")
      end
    end

    test "hours are numeric" do
      entries = Fixtures.sample_time_entries()
      assert Enum.all?(entries, fn e -> is_number(e["hours"]) end)
    end
  end

  describe "counting_steps/1" do
    test "returns correct number of steps" do
      assert length(Fixtures.counting_steps(1)) == 1
      assert length(Fixtures.counting_steps(5)) == 5
    end
  end

  describe "success_step/0 and success_step/1" do
    test "default name is 'success'" do
      step = Fixtures.success_step()
      assert step.name == "success"
    end

    test "custom name is used" do
      step = Fixtures.success_step("my_step")
      assert step.name == "my_step"
    end
  end

  describe "failing_step/0 and failing_step/1" do
    test "default name is 'failure'" do
      step = Fixtures.failing_step()
      assert step.name == "failure"
    end

    test "custom name is used" do
      step = Fixtures.failing_step("oops")
      assert step.name == "oops"
    end
  end
end
