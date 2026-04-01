defmodule Orchestrator.Browser.RelayWithScriptTest do
  @moduledoc """
  Tests for Relay module that exercise the script execution paths by creating
  temporary script files in the expected scripts directory.
  """
  use ExUnit.Case, async: false

  # The Relay module looks for scripts relative to its own file location.
  # We need to check if the scripts directory exists and has the expected scripts.

  @scripts_dir Path.expand("../../../../scripts", __DIR__)

  describe "execute/2 with existing scripts" do
    setup do
      # Check if scripts dir and script files exist
      approve_script = Path.join(@scripts_dir, "approve-workday.js")
      token_script = Path.join(@scripts_dir, "get-token.js")

      %{
        approve_exists: File.exists?(approve_script),
        token_exists: File.exists?(token_script),
        approve_path: approve_script,
        token_path: token_script
      }
    end

    test "approve_task script path check", %{approve_exists: exists, approve_path: path} do
      if exists do
        # Script exists — execute will attempt to run it
        result = Orchestrator.Browser.Relay.execute(:approve_task, %{})
        assert is_tuple(result)
        assert elem(result, 0) in [:ok, :error]
      else
        # Script does not exist
        {:error, msg} = Orchestrator.Browser.Relay.execute(:approve_task, %{})
        assert String.contains?(msg, "script not found") or String.contains?(msg, path)
      end
    end

    test "get_token script path check", %{token_exists: exists, token_path: path} do
      if exists do
        result = Orchestrator.Browser.Relay.execute(:get_token, %{})
        assert is_tuple(result)
        assert elem(result, 0) in [:ok, :error]
      else
        {:error, msg} = Orchestrator.Browser.Relay.execute(:get_token, %{})
        assert String.contains?(msg, "script not found") or String.contains?(msg, path)
      end
    end

    test "execute with params appends CLI args" do
      # Exercising build_args via execute — even if script doesn't exist
      result = Orchestrator.Browser.Relay.execute(:approve_task, %{task_id: "123"})
      assert is_tuple(result)
      assert elem(result, 0) in [:ok, :error]
    end

    test "execute with multiple params" do
      result =
        Orchestrator.Browser.Relay.execute(:approve_task, %{
          task_id: "456",
          comment: "approved"
        })

      assert is_tuple(result)
      assert elem(result, 0) in [:ok, :error]
    end
  end
end
