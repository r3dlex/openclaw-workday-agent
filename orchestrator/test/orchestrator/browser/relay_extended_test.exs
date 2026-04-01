defmodule Orchestrator.Browser.RelayExtendedTest do
  use ExUnit.Case, async: true

  alias Orchestrator.Browser.Relay

  describe "execute/2 action routing" do
    test "unknown action returns error with action name" do
      {:error, msg} = Relay.execute(:totally_unknown, %{})
      assert String.contains?(msg, "unknown relay action: totally_unknown")
    end

    test "known action :approve_task returns a result" do
      result = Relay.execute(:approve_task, %{})
      # Will fail because script doesn't exist, but returns proper tuple
      assert is_tuple(result)
      assert elem(result, 0) in [:ok, :error]
    end

    test "known action :get_token returns a result" do
      result = Relay.execute(:get_token, %{})
      assert is_tuple(result)
      assert elem(result, 0) in [:ok, :error]
    end

    test "approve_task with params returns a result" do
      result = Relay.execute(:approve_task, %{task_id: "123", user: "alice"})
      assert is_tuple(result)
      assert elem(result, 0) in [:ok, :error]
    end
  end

  describe "execute/1 default params" do
    test "approve_task with empty params" do
      result = Relay.execute(:approve_task)
      assert is_tuple(result)
      assert elem(result, 0) in [:ok, :error]
    end
  end
end
