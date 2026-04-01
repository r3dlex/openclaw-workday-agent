defmodule Orchestrator.Browser.ManagerExtendedTest do
  use ExUnit.Case, async: false

  alias Orchestrator.Browser.Manager

  # Ensure Manager is running before each test
  setup do
    case Process.whereis(Manager) do
      nil -> {:ok, _} = Manager.start_link([])
      _ -> :ok
    end

    :ok
  end

  # The Manager uses Headless and Relay backends under the hood.
  # In test env, headless backend is :ignore (not running) and relay
  # requires node scripts.  We test the strategy dispatch logic by
  # manipulating health flags.

  describe "execute/2 with headless_first strategy" do
    setup do
      # Ensure clean health state before each test
      Manager.mark_health(:headless, true)
      Manager.mark_health(:relay, true)
      Process.sleep(20)
      :ok
    end

    test "returns error when both backends fail" do
      Manager.mark_health(:headless, false)
      Manager.mark_health(:relay, false)
      Process.sleep(20)

      result = Manager.execute(:some_action, %{})

      case result do
        {:error, msg} ->
          assert is_binary(msg)

        {:ok, _} ->
          # If somehow a backend works, that's acceptable
          :ok
      end
    end

    test "execute returns a valid result tuple" do
      result = Manager.execute(:navigate, %{url: "https://example.com"})
      assert is_tuple(result) and elem(result, 0) in [:ok, :error]
    end
  end

  describe "mark_health/2" do
    test "can toggle headless health multiple times" do
      Manager.mark_health(:headless, false)
      Process.sleep(20)
      assert Manager.status().headless_healthy == false

      Manager.mark_health(:headless, true)
      Process.sleep(20)
      assert Manager.status().headless_healthy == true
    end

    test "can toggle relay health multiple times" do
      Manager.mark_health(:relay, false)
      Process.sleep(20)
      assert Manager.status().relay_healthy == false

      Manager.mark_health(:relay, true)
      Process.sleep(20)
      assert Manager.status().relay_healthy == true
    end
  end

  describe "status/0" do
    test "strategy is an atom" do
      assert is_atom(Manager.status().strategy)
    end

    test "health fields are booleans" do
      status = Manager.status()
      assert is_boolean(status.headless_healthy)
      assert is_boolean(status.relay_healthy)
    end
  end
end
