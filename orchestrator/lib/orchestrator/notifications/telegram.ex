defmodule Orchestrator.Notifications.Telegram do
  @moduledoc """
  Sends notifications to the user via Telegram Bot API.

  Configuration is read from environment variables:
  - TELEGRAM_BOT_TOKEN: Bot token from @BotFather
  - TELEGRAM_CHAT_ID: Target chat ID

  If either variable is missing, notifications are silently skipped
  and a warning is logged.
  """

  require Logger

  @base_url "https://api.telegram.org"

  @doc """
  Send a text message to the configured Telegram chat.

  Returns :ok on success, {:error, reason} on failure,
  or :skipped if credentials are not configured.
  """
  @spec send_message(String.t()) :: :ok | :skipped | {:error, term()}
  def send_message(text) do
    case config() do
      {:ok, token, chat_id} ->
        do_send(token, chat_id, text)

      :not_configured ->
        Logger.warning("Telegram not configured: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing")
        log_notification(:skipped, text, "not configured")
        :skipped
    end
  end

  @doc """
  Send a notification for a specific event type.

  Formats the message with priority prefix and timestamp.
  """
  @spec notify(atom(), String.t()) :: :ok | :skipped | {:error, term()}
  def notify(priority, message) when priority in [:high, :medium, :low] do
    timestamp = Calendar.strftime(DateTime.utc_now(), "%Y-%m-%d %H:%M UTC")
    prefix = priority_prefix(priority)

    formatted = """
    #{prefix} #{message}

    _#{timestamp}_
    """

    send_message(String.trim(formatted))
  end

  # --- Private ---

  defp config do
    token = System.get_env("TELEGRAM_BOT_TOKEN", "")
    chat_id = System.get_env("TELEGRAM_CHAT_ID", "")

    if token != "" and chat_id != "" do
      {:ok, token, chat_id}
    else
      :not_configured
    end
  end

  defp do_send(token, chat_id, text) do
    url = "#{@base_url}/bot#{token}/sendMessage"

    body =
      Jason.encode!(%{
        chat_id: chat_id,
        text: text,
        parse_mode: "MarkdownV2"
      })

    case Req.post(url, body: body, headers: [{"content-type", "application/json"}]) do
      {:ok, %Req.Response{status: 200}} ->
        Logger.info("Telegram notification sent")
        log_notification(:sent, text, "ok")
        :ok

      {:ok, %Req.Response{status: status, body: resp_body}} ->
        Logger.error("Telegram API error: #{status} - #{inspect(resp_body)}")
        log_notification(:failed, text, "HTTP #{status}")
        {:error, {:http_error, status}}

      {:error, reason} ->
        Logger.error("Telegram request failed: #{inspect(reason)}")
        log_notification(:failed, text, inspect(reason))
        {:error, reason}
    end
  end

  defp priority_prefix(:high), do: "*\\[HIGH\\]*"
  defp priority_prefix(:medium), do: "*\\[MEDIUM\\]*"
  defp priority_prefix(:low), do: "\\[LOW\\]"

  defp log_notification(status, text, detail) do
    log_dir = System.get_env("LOG_DIR", "logs")
    log_path = Path.join(log_dir, "notifications.log")

    timestamp = Calendar.strftime(DateTime.utc_now(), "%Y-%m-%d %H:%M:%S UTC")
    # Truncate message for log (no sensitive data in full)
    preview = String.slice(text, 0, 100)
    line = "[#{timestamp}] #{status} | #{detail} | #{preview}\n"

    File.mkdir_p!(log_dir)
    File.write!(log_path, line, [:append])
  rescue
    error ->
      Logger.warning("Failed to write notification log: #{inspect(error)}")
  end
end
