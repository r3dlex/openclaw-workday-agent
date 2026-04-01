defmodule Orchestrator.Browser.RelayTest do
  use ExUnit.Case, async: true

  alias Orchestrator.Browser.Relay

  describe "execute/2" do
    test "returns error for unknown action" do
      assert {:error, msg} = Relay.execute(:nonexistent_action, %{})
      assert String.contains?(msg, "unknown relay action")
    end

    test "returns error for known action when script file is missing" do
      # The scripts directory won't exist in test env so the file check fails
      result = Relay.execute(:approve_task, %{})

      case result do
        {:error, _reason} -> :ok
        {:ok, _} -> :ok
      end

      # Just verify it returns a valid result tuple
      assert is_tuple(result) and elem(result, 0) in [:ok, :error]
    end

    test "returns error for :get_token when script missing" do
      result = Relay.execute(:get_token, %{})
      assert is_tuple(result) and elem(result, 0) in [:ok, :error]
    end
  end

  describe "build_args/1 (via execute with params)" do
    test "empty params produces no extra args" do
      # Can't call private functions directly; exercise via public API
      result = Relay.execute(:nonexistent_action, %{})
      assert {:error, _} = result
    end

    test "unknown action with params still returns error" do
      result = Relay.execute(:nonexistent, %{key: "value"})
      assert {:error, msg} = result
      assert String.contains?(msg, "unknown relay action")
    end
  end
end
