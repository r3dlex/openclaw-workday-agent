defmodule Orchestrator.Application do
  @moduledoc false

  use Application

  @impl true
  def start(_type, _args) do
    children = [
      # Inter-Agent Message Queue client (register, heartbeat, inbox polling)
      Orchestrator.MqClient,
      Orchestrator.Pipeline.Runner,
      Orchestrator.Browser.Manager
    ]

    opts = [strategy: :one_for_one, name: Orchestrator.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
