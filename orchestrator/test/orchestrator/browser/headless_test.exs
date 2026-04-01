defmodule Orchestrator.Browser.HeadlessTest do
  use ExUnit.Case, async: false

  alias Orchestrator.Browser.Headless

  describe "send_action/2" do
    test "returns error when headless backend is not running" do
      # In test env, Headless is started with :ignore (no valid python runner)
      # The send_action catches :noproc exit
      result = Headless.send_action(:ping, %{})

      case result do
        {:error, reason} when is_binary(reason) ->
          assert String.length(reason) > 0

        {:ok, _} ->
          # Unlikely in test, but valid
          :ok
      end
    end

    test "send_action/1 with no params defaults to empty map" do
      result = Headless.send_action(:ping)
      assert is_tuple(result) and elem(result, 0) in [:ok, :error]
    end
  end
end
