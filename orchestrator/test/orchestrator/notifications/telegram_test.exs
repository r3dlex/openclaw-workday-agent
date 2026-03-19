defmodule Orchestrator.Notifications.TelegramTest do
  use ExUnit.Case, async: false

  alias Orchestrator.Notifications.Telegram

  describe "send_message/1" do
    test "returns :skipped when not configured" do
      # Ensure env vars are not set
      System.delete_env("TELEGRAM_BOT_TOKEN")
      System.delete_env("TELEGRAM_CHAT_ID")

      assert Telegram.send_message("test message") == :skipped
    end

    test "returns :skipped when token is empty" do
      System.put_env("TELEGRAM_BOT_TOKEN", "")
      System.put_env("TELEGRAM_CHAT_ID", "12345")

      assert Telegram.send_message("test message") == :skipped
    after
      System.delete_env("TELEGRAM_BOT_TOKEN")
      System.delete_env("TELEGRAM_CHAT_ID")
    end

    test "returns :skipped when chat_id is empty" do
      System.put_env("TELEGRAM_BOT_TOKEN", "test_token")
      System.put_env("TELEGRAM_CHAT_ID", "")

      assert Telegram.send_message("test message") == :skipped
    after
      System.delete_env("TELEGRAM_BOT_TOKEN")
      System.delete_env("TELEGRAM_CHAT_ID")
    end
  end

  describe "notify/2" do
    test "formats high priority message" do
      System.delete_env("TELEGRAM_BOT_TOKEN")
      System.delete_env("TELEGRAM_CHAT_ID")

      # Will be :skipped but exercises formatting
      assert Telegram.notify(:high, "Test alert") == :skipped
    end

    test "formats medium priority message" do
      System.delete_env("TELEGRAM_BOT_TOKEN")
      System.delete_env("TELEGRAM_CHAT_ID")

      assert Telegram.notify(:medium, "Test info") == :skipped
    end

    test "formats low priority message" do
      System.delete_env("TELEGRAM_BOT_TOKEN")
      System.delete_env("TELEGRAM_CHAT_ID")

      assert Telegram.notify(:low, "Test debug") == :skipped
    end
  end
end
