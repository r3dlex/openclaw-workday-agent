defmodule Orchestrator.Workday.TimeTracking do
  @moduledoc """
  Time tracking pipeline steps for Workday.
  """

  alias Orchestrator.Browser.Manager

  @doc """
  Ensure the user is authenticated before proceeding.
  """
  @spec step_ensure_authenticated(map()) :: {:ok, map()} | {:error, String.t()}
  def step_ensure_authenticated(context) do
    case Manager.execute(:check_auth, %{}) do
      {:ok, %{"authenticated" => true}} ->
        {:ok, Map.put(context, :authenticated, true)}

      {:ok, _} ->
        {:error, "not authenticated — run sso_login pipeline first"}

      {:error, reason} ->
        {:error, "auth check failed: #{reason}"}
    end
  end

  @doc """
  Navigate to the Workday time tracking page.
  """
  @spec step_navigate_to_time_tracking(map()) :: {:ok, map()} | {:error, String.t()}
  def step_navigate_to_time_tracking(context) do
    base_url = Application.get_env(:orchestrator, :workday_base_url)
    time_path = Application.get_env(:orchestrator, :workday_time_tracking_path)

    case {base_url, time_path} do
      {nil, _} ->
        {:error, "WORKDAY_BASE_URL not configured"}

      {_, nil} ->
        {:error, "WORKDAY_TIME_TRACKING_PATH not configured"}

      {url, path} ->
        target = url <> path

        case Manager.execute(:navigate, %{url: target}) do
          {:ok, result} ->
            {:ok, Map.merge(context, %{time_tracking_url: target, page_state: result})}

          {:error, reason} ->
            {:error, "failed to navigate to time tracking: #{reason}"}
        end
    end
  end

  @doc """
  Extract time entries from the current page.
  """
  @spec step_get_entries(map()) :: {:ok, map()} | {:error, String.t()}
  def step_get_entries(context) do
    case Manager.execute(:extract_time_entries, %{}) do
      {:ok, %{"entries" => entries}} ->
        {:ok, Map.put(context, :time_entries, entries)}

      {:ok, result} ->
        {:ok, Map.put(context, :time_entries, []) |> Map.put(:extract_result, result)}

      {:error, reason} ->
        {:error, "failed to get time entries: #{reason}"}
    end
  end

  @doc """
  Validate time entries against organizational rules.
  """
  @spec step_validate_entries(map()) :: {:ok, map()} | {:error, String.t()}
  def step_validate_entries(context) do
    entries = Map.get(context, :time_entries, [])

    validation =
      Enum.map(entries, fn entry ->
        hours = Map.get(entry, "hours", 0)

        cond do
          hours <= 0 ->
            %{entry: entry, valid: false, reason: "hours must be positive"}

          hours > 24 ->
            %{entry: entry, valid: false, reason: "hours exceed 24h per day"}

          true ->
            %{entry: entry, valid: true, reason: nil}
        end
      end)

    all_valid = Enum.all?(validation, & &1.valid)

    {:ok,
     Map.merge(context, %{
       validation: validation,
       all_entries_valid: all_valid
     })}
  end
end
