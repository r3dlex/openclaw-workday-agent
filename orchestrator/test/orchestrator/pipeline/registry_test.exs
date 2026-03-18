defmodule Orchestrator.Pipeline.RegistryTest do
  use ExUnit.Case, async: true

  alias Orchestrator.Pipeline.{Registry, Step}

  describe "get/1" do
    test "returns steps for :sso_login pipeline" do
      assert {:ok, steps} = Registry.get(:sso_login)
      assert is_list(steps)
      assert length(steps) > 0
      assert Enum.all?(steps, &match?(%Step{}, &1))
    end

    test "returns steps for :task_approval pipeline" do
      assert {:ok, steps} = Registry.get(:task_approval)
      assert is_list(steps)
      assert length(steps) > 0
      assert Enum.all?(steps, &match?(%Step{}, &1))
    end

    test "returns steps for :time_tracking pipeline" do
      assert {:ok, steps} = Registry.get(:time_tracking)
      assert is_list(steps)
      assert length(steps) > 0
      assert Enum.all?(steps, &match?(%Step{}, &1))
    end

    test "returns error for unknown pipeline" do
      assert {:error, :not_found} = Registry.get(:nonexistent)
    end

    test "all steps have required fields" do
      for name <- Registry.list() do
        {:ok, steps} = Registry.get(name)

        for step <- steps do
          assert is_binary(step.name), "step name should be a string"
          assert is_atom(step.module), "step module should be an atom"
          assert is_atom(step.function), "step function should be an atom"
        end
      end
    end
  end

  describe "list/0" do
    test "returns all registered pipeline names" do
      names = Registry.list()
      assert :sso_login in names
      assert :task_approval in names
      assert :time_tracking in names
    end
  end
end
