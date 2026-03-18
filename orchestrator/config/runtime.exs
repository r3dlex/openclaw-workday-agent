import Config

config :orchestrator,
  browser_strategy:
    System.get_env("BROWSER_STRATEGY", "headless_first") |> String.to_atom(),
  pipeline_runner_path:
    System.get_env("PIPELINE_RUNNER_PATH", "../tools/pipeline_runner"),
  workday_base_url: System.get_env("WORKDAY_BASE_URL"),
  workday_tasks_path: System.get_env("WORKDAY_TASKS_PATH"),
  workday_time_tracking_path: System.get_env("WORKDAY_TIME_TRACKING_PATH"),
  workday_home_path: System.get_env("WORKDAY_HOME_PATH"),
  sso_provider_name: System.get_env("SSO_PROVIDER_NAME"),
  cdp_token: System.get_env("CHROME_CDP_TOKEN"),
  cdp_port: System.get_env("CHROME_CDP_PORT")
