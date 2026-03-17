#!/usr/bin/env node
/**
 * get-token.js — Extract the OpenClaw gateway auth token from its config file.
 *
 * Reads OPENCLAW_CONFIG_PATH (default: ~/.openclaw/openclaw.json)
 * and prints the gateway auth token to stdout.
 *
 * Usage:  node scripts/get-token.js
 */

"use strict";

const fs = require("fs");
const path = require("path");
const os = require("os");

const configPath =
  process.env.OPENCLAW_CONFIG_PATH ||
  path.join(os.homedir(), ".openclaw", "openclaw.json");

try {
  const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
  const token = config?.gateway?.auth?.token;
  if (!token) {
    console.error(`No gateway.auth.token found in ${configPath}`);
    process.exit(1);
  }
  process.stdout.write(token);
} catch (e) {
  console.error(`Failed to read ${configPath}: ${e.message}`);
  process.exit(1);
}
