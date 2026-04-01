defmodule Orchestrator.Application do
  @moduledoc false

  use Application

  # MQ processes are skipped in test env (no IAMQ available, would block/reconnect-loop)
  @start_mq Mix.env() != :test

  @impl true
  def start(_type, _args) do
    mq_children =
      if @start_mq do
        [
          # Inter-Agent Message Queue client (register, heartbeat, inbox polling)
          Orchestrator.MqClient,
          # IAMQ WebSocket client (real-time message push)
          Orchestrator.MqWsClient
        ]
      else
        []
      end

    children =
      mq_children ++
        [
          Orchestrator.Pipeline.Runner,
          Orchestrator.Browser.Manager
        ]

    opts = [strategy: :one_for_one, name: Orchestrator.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
