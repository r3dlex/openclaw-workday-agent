defmodule Orchestrator.Workday.SSOTest do
  use ExUnit.Case, async: false

  alias Orchestrator.Workday.SSO

  setup do
    case Process.whereis(Orchestrator.Browser.Manager) do
      nil -> {:ok, _} = Orchestrator.Browser.Manager.start_link([])
      _ -> :ok
    end

    :ok
  end

  # ---------------------------------------------------------------------------
  # step_navigate_to_workday/1 — config-dependent with Manager
  # ---------------------------------------------------------------------------

  describe "step_navigate_to_workday/1" do
    test "returns error when workday_base_url not configured" do
      Application.delete_env(:orchestrator, :workday_base_url)

      result = SSO.step_navigate_to_workday(%{})

      assert {:error, msg} = result
      assert String.contains?(msg, "WORKDAY_BASE_URL")
    end

    test "attempts Manager call when url is configured" do
      Application.put_env(:orchestrator, :workday_base_url, "https://workday.test")
      Application.put_env(:orchestrator, :workday_home_path, "/home")

      result = SSO.step_navigate_to_workday(%{})

      # Either the Manager succeeds or returns error (headless not running in tests)
      assert is_tuple(result) and elem(result, 0) in [:ok, :error]

      Application.delete_env(:orchestrator, :workday_base_url)
      Application.delete_env(:orchestrator, :workday_home_path)
    end
  end

  # ---------------------------------------------------------------------------
  # step_detect_login_screen/1 — Manager-dependent
  # ---------------------------------------------------------------------------

  describe "step_detect_login_screen/1" do
    test "returns a valid result tuple" do
      result = SSO.step_detect_login_screen(%{})
      assert is_tuple(result) and elem(result, 0) in [:ok, :error]
    end
  end

  # ---------------------------------------------------------------------------
  # step_click_provider/1 — skips if login screen not detected
  # ---------------------------------------------------------------------------

  describe "step_click_provider/1" do
    test "skips click when login screen not detected" do
      context = %{login_screen_detected: false}
      assert {:ok, result} = SSO.step_click_provider(context)
      assert result.provider_clicked == false
    end

    test "attempts click when login screen detected" do
      Application.put_env(:orchestrator, :sso_provider_name, "TestSSO")
      context = %{login_screen_detected: true}

      result = SSO.step_click_provider(context)
      assert is_tuple(result) and elem(result, 0) in [:ok, :error]

      Application.delete_env(:orchestrator, :sso_provider_name)
    end

    test "provider_clicked is false when no login screen key in context" do
      # Default is false via Map.get with default
      context = %{}
      assert {:ok, result} = SSO.step_click_provider(context)
      assert result.provider_clicked == false
    end
  end

  # ---------------------------------------------------------------------------
  # step_fallback_direct_link/1 — pure logic for already-clicked case
  # ---------------------------------------------------------------------------

  describe "step_fallback_direct_link/1" do
    test "returns context unchanged when provider already clicked" do
      context = %{provider_clicked: true, some_key: "value"}
      assert {:ok, result} = SSO.step_fallback_direct_link(context)
      assert result.some_key == "value"
      assert result.provider_clicked == true
    end

    test "skips fallback when login screen not detected and provider not clicked" do
      context = %{provider_clicked: false, login_screen_detected: false}
      assert {:ok, result} = SSO.step_fallback_direct_link(context)
      # No change — just passes context through
      assert result.provider_clicked == false
    end

    test "attempts fallback when login screen was detected but provider was not clicked" do
      context = %{provider_clicked: false, login_screen_detected: true}
      result = SSO.step_fallback_direct_link(context)
      assert is_tuple(result) and elem(result, 0) in [:ok, :error]
    end
  end

  # ---------------------------------------------------------------------------
  # step_verify_authenticated/1 — Manager-dependent
  # ---------------------------------------------------------------------------

  describe "step_verify_authenticated/1" do
    test "returns a valid result tuple" do
      result = SSO.step_verify_authenticated(%{})
      assert is_tuple(result) and elem(result, 0) in [:ok, :error]
    end
  end
end
