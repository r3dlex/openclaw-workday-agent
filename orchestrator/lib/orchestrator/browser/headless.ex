defmodule Orchestrator.Browser.Headless do
  @moduledoc """
  Port-based interop with the Python/Playwright pipeline runner.

  Communicates via JSON lines over stdin/stdout.
  """

  use GenServer
  require Logger

  @timeout 30_000

  defstruct port: nil, pending: nil

  # Client API

  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  @doc """
  Send an action to the headless browser backend.
  """
  @spec send_action(atom(), map()) :: {:ok, map()} | {:error, String.t()}
  def send_action(action, params \\ %{}) do
    try do
      GenServer.call(__MODULE__, {:send_action, action, params}, @timeout)
    catch
      :exit, {:noproc, _} ->
        {:error, "headless backend not running"}

      :exit, {:timeout, _} ->
        {:error, "headless backend timeout"}
    end
  end

  # Server callbacks

  @impl true
  def init(_opts) do
    runner_path = Application.get_env(:orchestrator, :pipeline_runner_path, "../tools/pipeline_runner")

    case open_port(runner_path) do
      {:ok, port} ->
        {:ok, %__MODULE__{port: port}}

      {:error, reason} ->
        Logger.warning("Failed to start headless backend: #{inspect(reason)}")
        :ignore
    end
  end

  @impl true
  def handle_call({:send_action, action, params}, from, state) do
    message =
      Jason.encode!(%{action: action, params: params})

    send(state.port, {self(), {:command, "#{message}\n"}})
    {:noreply, %{state | pending: from}}
  end

  @impl true
  def handle_info({port, {:data, data}}, %{port: port, pending: from} = state)
      when from != nil do
    result =
      case Jason.decode(to_string(data)) do
        {:ok, %{"status" => "ok"} = response} ->
          {:ok, Map.delete(response, "status")}

        {:ok, %{"status" => "error", "message" => message}} ->
          {:error, message}

        {:ok, other} ->
          {:ok, other}

        {:error, _} ->
          {:error, "invalid JSON response from headless backend"}
      end

    GenServer.reply(from, result)
    {:noreply, %{state | pending: nil}}
  end

  @impl true
  def handle_info({port, {:exit_status, code}}, %{port: port} = state) do
    Logger.error("Headless backend exited with code #{code}")

    if state.pending do
      GenServer.reply(state.pending, {:error, "headless backend crashed"})
    end

    {:stop, :port_closed, %{state | port: nil, pending: nil}}
  end

  @impl true
  def handle_info(_msg, state), do: {:noreply, state}

  # Private

  defp open_port(runner_path) do
    try do
      port =
        Port.open({:spawn_executable, System.find_executable("python3") || "python3"},
          args: [runner_path, "--stdio"],
          line: 1_048_576,
          env: build_env()
        )

      {:ok, port}
    rescue
      e -> {:error, Exception.message(e)}
    end
  end

  defp build_env do
    []
    |> maybe_add_env("WORKDAY_BASE_URL", :workday_base_url)
    |> maybe_add_env("SSO_PROVIDER_NAME", :sso_provider_name)
    |> maybe_add_env("CHROME_CDP_TOKEN", :cdp_token)
    |> maybe_add_env("CHROME_CDP_PORT", :cdp_port)
  end

  defp maybe_add_env(acc, env_name, config_key) do
    case Application.get_env(:orchestrator, config_key) do
      nil -> acc
      value -> [{String.to_charlist(env_name), String.to_charlist(value)} | acc]
    end
  end
end
