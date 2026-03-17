#!/usr/bin/env node
/**
 * approve-workday.js — Click "Approve" on a Workday task via Chrome DevTools Protocol.
 *
 * Requires: CHROME_CDP_TOKEN, CHROME_CDP_PORT in environment (loaded from .env).
 * Usage:    node scripts/approve-workday.js
 *           docker compose run --rm agent node scripts/approve-workday.js
 */

"use strict";

const WebSocket = require("ws");
const http = require("http");
const path = require("path");

// ---------------------------------------------------------------------------
// Load .env from project root (works inside or outside Docker)
// ---------------------------------------------------------------------------
try {
  const envPath = path.resolve(__dirname, "..", ".env");
  require("fs")
    .readFileSync(envPath, "utf8")
    .split("\n")
    .forEach((line) => {
      const match = line.match(/^\s*([\w]+)\s*=\s*(.*)\s*$/);
      if (match && !match[1].startsWith("#")) {
        process.env[match[1]] = process.env[match[1]] || match[2];
      }
    });
} catch (_) {
  // .env not found — rely on environment variables
}

const TOKEN = process.env.CHROME_CDP_TOKEN;
const PORT = parseInt(process.env.CHROME_CDP_PORT, 10);

if (!TOKEN || !PORT) {
  console.error("Error: CHROME_CDP_TOKEN and CHROME_CDP_PORT must be set.");
  console.error("Copy .env.example to .env and fill in your values.");
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Chrome DevTools Protocol helpers
// ---------------------------------------------------------------------------

function getTabs() {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: process.env.CDP_HOST || "localhost",
      port: PORT,
      path: `/json?token=${encodeURIComponent(TOKEN)}`,
      headers: { Authorization: `Bearer ${TOKEN}` },
    };
    const req = http.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        if (res.statusCode === 200) {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(new Error(`Invalid JSON from CDP: ${e.message}`));
          }
        } else {
          reject(new Error(`CDP returned HTTP ${res.statusCode}`));
        }
      });
    });
    req.on("error", reject);
    req.end();
  });
}

async function run() {
  const tabs = await getTabs();
  const tab = tabs.find(
    (t) => t.url.includes("workday.com") || t.title.includes("Workday")
  );

  if (!tab) {
    console.log("No Workday tab found. Open Workday in Chrome first.");
    process.exit(0);
  }

  let wsUrl = tab.webSocketDebuggerUrl;
  if (wsUrl && !wsUrl.includes("token=")) {
    wsUrl += `?token=${encodeURIComponent(TOKEN)}`;
  }

  console.log(`Connecting to tab: ${tab.title}`);

  const ws = new WebSocket(wsUrl);

  ws.on("open", () => {
    ws.send(
      JSON.stringify({
        id: 1,
        method: "Runtime.evaluate",
        params: {
          expression: `
            (function () {
              var buttons = document.querySelectorAll('button, div[role="button"]');
              for (var i = 0; i < buttons.length; i++) {
                if (buttons[i].innerText.trim() === "Approve") {
                  buttons[i].click();
                  return "Clicked Approve";
                }
              }
              return "Approve button not found";
            })()
          `,
          returnByValue: true,
        },
      })
    );
  });

  ws.on("message", (raw) => {
    const res = JSON.parse(raw);
    if (res.id === 1) {
      console.log("Result:", res.result.result.value);
      ws.close();
    }
  });

  ws.on("error", (e) => {
    console.error("WebSocket error:", e.message);
    process.exit(1);
  });
}

run().catch((e) => {
  console.error("Error:", e.message);
  process.exit(1);
});
