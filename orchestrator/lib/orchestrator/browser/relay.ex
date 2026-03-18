defmodule Orchestrator.Browser.Relay do
  @moduledoc """
  CDP relay backend using Node.js scripts.

  Executes existing Node.js automation scripts and parses their output.
  """

  require Logger

  @scripts_dir Path.expand("../../../scripts", __DIR__)

  @script_map %{
    approve_task: "approve-workday.js",
    get_token: "get-token.js"
  }

  @doc """
  Execute a Node.js script by action name.
  """
  @spec execute(atom(), map()) :: {:ok, map()} | {:error, String.t()}
  def execute(action, params \\ %{}) do
    case Map.get(@script_map, action) do
      nil ->
        {:error, "unknown relay action: #{action}"}

      script_name ->
        run_script(script_name, params)
    end
  end

  defp run_script(script_name, params) do
    script_path = Path.join(@scripts_dir, script_name)

    unless File.exists?(script_path) do
      {:error, "script not found: #{script_path}"}
    else
      args = build_args(params)
      env = build_env()

      Logger.debug("Running relay script: #{script_name} with args: #{inspect(args)}")

      case System.cmd("node", [script_path | args], env: env, stderr_to_stdout: true) do
        {output, 0} ->
          parse_output(output)

        {output, exit_code} ->
          {:error, "script #{script_name} exited with code #{exit_code}: #{String.trim(output)}"}
      end
    end
  end

  defp build_args(params) when map_size(params) == 0, do: []

  defp build_args(params) do
    Enum.flat_map(params, fn {key, value} ->
      ["--#{key}", to_string(value)]
    end)
  end

  defp build_env do
    []
    |> maybe_add("CHROME_CDP_TOKEN", :cdp_token)
    |> maybe_add("CHROME_CDP_PORT", :cdp_port)
    |> maybe_add("WORKDAY_BASE_URL", :workday_base_url)
    |> maybe_add("WORKDAY_TASKS_PATH", :workday_tasks_path)
  end

  defp maybe_add(env, name, config_key) do
    case Application.get_env(:orchestrator, config_key) do
      nil -> env
      value -> [{name, value} | env]
    end
  end

  defp parse_output(output) do
    case Jason.decode(String.trim(output)) do
      {:ok, parsed} ->
        {:ok, parsed}

      {:error, _} ->
        {:ok, %{"raw_output" => String.trim(output)}}
    end
  end
end
