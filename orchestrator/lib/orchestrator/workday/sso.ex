defmodule Orchestrator.Workday.SSO do
  @moduledoc """
  SSO login pipeline steps for Workday authentication.
  """

  alias Orchestrator.Browser.Manager

  @doc """
  Navigate the browser to the Workday home page.
  """
  @spec step_navigate_to_workday(map()) :: {:ok, map()} | {:error, String.t()}
  def step_navigate_to_workday(context) do
    base_url = Application.get_env(:orchestrator, :workday_base_url)
    home_path = Application.get_env(:orchestrator, :workday_home_path, "/")

    case base_url do
      nil ->
        {:error, "WORKDAY_BASE_URL not configured"}

      url ->
        target_url = url <> home_path

        case Manager.execute(:navigate, %{url: target_url}) do
          {:ok, result} ->
            {:ok, Map.merge(context, %{navigated_to: target_url, page_state: result})}

          {:error, reason} ->
            {:error, "failed to navigate to Workday: #{reason}"}
        end
    end
  end

  @doc """
  Detect whether we are on a login/SSO screen.
  """
  @spec step_detect_login_screen(map()) :: {:ok, map()} | {:error, String.t()}
  def step_detect_login_screen(context) do
    case Manager.execute(:detect_element, %{
           selectors: ["[data-automation-id='loginScreen']", ".login-form", "#login"]
         }) do
      {:ok, %{"found" => true} = result} ->
        {:ok, Map.put(context, :login_screen_detected, true) |> Map.put(:login_state, result)}

      {:ok, _} ->
        {:ok, Map.put(context, :login_screen_detected, false)}

      {:error, reason} ->
        {:error, "failed to detect login screen: #{reason}"}
    end
  end

  @doc """
  Click the SSO provider button on the login screen.
  """
  @spec step_click_provider(map()) :: {:ok, map()} | {:error, String.t()}
  def step_click_provider(context) do
    if Map.get(context, :login_screen_detected, false) do
      provider_name = Application.get_env(:orchestrator, :sso_provider_name)

      case Manager.execute(:click_text, %{text: provider_name}) do
        {:ok, result} ->
          {:ok, Map.put(context, :provider_clicked, true) |> Map.put(:click_result, result)}

        {:error, reason} ->
          {:error, "failed to click SSO provider: #{reason}"}
      end
    else
      {:ok, Map.put(context, :provider_clicked, false)}
    end
  end

  @doc """
  Fallback: navigate directly to the SSO link if button click failed.
  """
  @spec step_fallback_direct_link(map()) :: {:ok, map()} | {:error, String.t()}
  def step_fallback_direct_link(context) do
    if Map.get(context, :provider_clicked, false) do
      {:ok, context}
    else
      if Map.get(context, :login_screen_detected, false) do
        case Manager.execute(:find_sso_link, %{}) do
          {:ok, %{"url" => url}} ->
            case Manager.execute(:navigate, %{url: url}) do
              {:ok, result} ->
                {:ok, Map.put(context, :fallback_used, true) |> Map.put(:fallback_result, result)}

              {:error, reason} ->
                {:error, "fallback navigation failed: #{reason}"}
            end

          {:error, reason} ->
            {:error, "could not find SSO fallback link: #{reason}"}
        end
      else
        {:ok, context}
      end
    end
  end

  @doc """
  Verify that authentication was successful.
  """
  @spec step_verify_authenticated(map()) :: {:ok, map()} | {:error, String.t()}
  def step_verify_authenticated(context) do
    case Manager.execute(:detect_element, %{
           selectors: ["[data-automation-id='globalNav']", ".home-page", "#dashboard"]
         }) do
      {:ok, %{"found" => true}} ->
        {:ok, Map.put(context, :authenticated, true)}

      {:ok, _} ->
        {:error, "authentication verification failed: not on authenticated page"}

      {:error, reason} ->
        {:error, "failed to verify authentication: #{reason}"}
    end
  end
end
