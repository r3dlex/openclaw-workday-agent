defmodule Orchestrator.Workday.SSOSuccessTest do
  @moduledoc """
  Tests SSO step functions with a MockManager that returns success responses.
  """
  use ExUnit.Case, async: false

  alias Orchestrator.Workday.SSO
  alias Orchestrator.Test.MockManager

  defp with_mock(responses, fun), do: MockManager.replace_for_test(responses, fun)

  describe "step_navigate_to_workday/1 success path" do
    test "returns ok when Manager navigate succeeds" do
      Application.put_env(:orchestrator, :workday_base_url, "https://workday.test")
      Application.put_env(:orchestrator, :workday_home_path, "/home")

      with_mock(%{navigate: {:ok, %{"loaded" => true}}}, fn ->
        assert {:ok, ctx} = SSO.step_navigate_to_workday(%{})
        assert ctx.navigated_to == "https://workday.test/home"
      end)

      Application.delete_env(:orchestrator, :workday_base_url)
      Application.delete_env(:orchestrator, :workday_home_path)
    end
  end

  describe "step_detect_login_screen/1" do
    test "returns ok with login_screen_detected true when found" do
      with_mock(%{detect_element: {:ok, %{"found" => true, "selector" => "#login"}}}, fn ->
        assert {:ok, ctx} = SSO.step_detect_login_screen(%{})
        assert ctx.login_screen_detected == true
      end)
    end

    test "returns ok with login_screen_detected false when not found" do
      with_mock(%{detect_element: {:ok, %{"found" => false}}}, fn ->
        assert {:ok, ctx} = SSO.step_detect_login_screen(%{})
        assert ctx.login_screen_detected == false
      end)
    end

    test "returns error when detect_element fails" do
      with_mock(%{detect_element: {:error, "failed"}}, fn ->
        assert {:error, msg} = SSO.step_detect_login_screen(%{})
        assert String.contains?(msg, "failed to detect login screen")
      end)
    end
  end

  describe "step_click_provider/1 success path" do
    test "returns ok when click succeeds and login screen was detected" do
      Application.put_env(:orchestrator, :sso_provider_name, "TestSSO")

      with_mock(%{click_text: {:ok, %{"clicked" => true}}}, fn ->
        context = %{login_screen_detected: true}
        assert {:ok, ctx} = SSO.step_click_provider(context)
        assert ctx.provider_clicked == true
      end)

      Application.delete_env(:orchestrator, :sso_provider_name)
    end

    test "returns error when click fails" do
      Application.put_env(:orchestrator, :sso_provider_name, "TestSSO")

      with_mock(%{click_text: {:error, "element not found"}}, fn ->
        context = %{login_screen_detected: true}
        assert {:error, msg} = SSO.step_click_provider(context)
        assert String.contains?(msg, "failed to click SSO provider")
      end)

      Application.delete_env(:orchestrator, :sso_provider_name)
    end
  end

  describe "step_fallback_direct_link/1 success paths" do
    test "finds SSO link and navigates when provider not clicked" do
      with_mock(
        %{
          find_sso_link: {:ok, %{"url" => "https://sso.example.com/tenant"}},
          navigate: {:ok, %{"loaded" => true}}
        },
        fn ->
          context = %{provider_clicked: false, login_screen_detected: true}
          assert {:ok, ctx} = SSO.step_fallback_direct_link(context)
          assert ctx.fallback_used == true
        end
      )
    end

    test "returns error when find_sso_link fails" do
      with_mock(%{find_sso_link: {:error, "link not found"}}, fn ->
        context = %{provider_clicked: false, login_screen_detected: true}
        assert {:error, msg} = SSO.step_fallback_direct_link(context)
        assert String.contains?(msg, "fallback link")
      end)
    end

    test "returns error when navigate after sso link fails" do
      with_mock(
        %{
          find_sso_link: {:ok, %{"url" => "https://sso.example.com"}},
          navigate: {:error, "navigation failed"}
        },
        fn ->
          context = %{provider_clicked: false, login_screen_detected: true}
          assert {:error, msg} = SSO.step_fallback_direct_link(context)
          assert String.contains?(msg, "fallback navigation failed")
        end
      )
    end
  end

  describe "step_verify_authenticated/1" do
    test "returns ok when authenticated page detected" do
      with_mock(%{detect_element: {:ok, %{"found" => true}}}, fn ->
        assert {:ok, ctx} = SSO.step_verify_authenticated(%{})
        assert ctx.authenticated == true
      end)
    end

    test "returns error when not on authenticated page" do
      with_mock(%{detect_element: {:ok, %{"found" => false}}}, fn ->
        assert {:error, msg} = SSO.step_verify_authenticated(%{})
        assert String.contains?(msg, "verification failed")
      end)
    end

    test "returns error when detect fails" do
      with_mock(%{detect_element: {:error, "timeout"}}, fn ->
        assert {:error, msg} = SSO.step_verify_authenticated(%{})
        assert String.contains?(msg, "failed to verify authentication")
      end)
    end
  end
end
