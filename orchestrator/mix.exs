defmodule Orchestrator.MixProject do
  use Mix.Project

  def project do
    [
      app: :orchestrator,
      version: "0.1.0",
      elixir: "~> 1.17",
      elixirc_paths: elixirc_paths(Mix.env()),
      start_permanent: Mix.env() == :prod,
      deps: deps(),
      name: "WorkdayOrchestrator",
      source_url: "https://github.com/r3dlex/openclaw-workday-agent",
      docs: [
        main: "readme",
        extras:
          if(File.exists?("../README.md"), do: ["../README.md"], else: []) ++
            if(File.exists?("spec"), do: Path.wildcard("spec/*.md"), else: []),
        output: "doc/",
        formatters: ["html"]
      ],
      test_coverage: [
        summary: [threshold: 90],
        ignore_modules: [
          Orchestrator.Application,
          Orchestrator.MqClient,
          Orchestrator.MqWsClient,
          Orchestrator.Browser.Headless
        ]
      ]
    ]
  end

  def application do
    [
      extra_applications: [:logger],
      mod: {Orchestrator.Application, []}
    ]
  end

  defp elixirc_paths(:test), do: ["lib", "test/support"]
  defp elixirc_paths(_), do: ["lib"]

  defp deps do
    [
      {:jason, "~> 1.4"},
      {:req, "~> 0.5"},
      {:websockex, "~> 0.5"},
      {:ex_doc, "~> 0.34", only: :dev, runtime: false}
    ]
  end
end
