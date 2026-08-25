# Cloudflare agent setup — status and instructions

**Date:** 14 August 2026
**Scope:** Setting up Claude Code to work against the Cloudflare developer platform.

---

## Plain English first

Three separate things make up "Cloudflare setup". They are not the same and
they do not all persist in the same place:

1. **Skills** — reference material that teaches the agent how Cloudflare
   works (Workers, DNS, Durable Objects, Wrangler CLI). Files on disk.
2. **MCP servers** — live connections that let the agent actually read and
   change your Cloudflare account (DNS records, R2 buckets, deployments).
   These require you to log in via OAuth before they do anything.
3. **Wrangler CLI** — the command-line tool that deploys Workers.

Installing item 1 does **not** give account access. Only item 2 does, and only
after a browser login.

---

## What was actually done, and what was proven

Installed in the remote session container on 14 Aug 2026:

| Step | Command | Verified result |
|---|---|---|
| Add marketplace | `claude plugin marketplace add cloudflare/skills` | PASS — cloned from `github.com/cloudflare/skills`, marketplace `cloudflare` registered |
| Install plugin | `claude plugin install cloudflare@cloudflare` | PASS — `cloudflare@cloudflare` v1.0.0, user scope |
| Inventory check | `claude plugin details cloudflare` | PASS — 15 skills present on disk |
| MCP registration | `claude mcp list` | REGISTERED, **NOT AUTHENTICATED** (see below) |

**Skills installed (15):** `agents-sdk`, `build-agent`, `build-mcp`,
`cloudflare`, `cloudflare-email-service`, `cloudflare-one`,
`cloudflare-one-migrations`, `durable-objects`, `sandbox-migrate-to-next`,
`sandbox-next`, `sandbox-stable`, `turnstile-spin`, `web-perf`,
`workers-best-practices`, `wrangler`.

**MCP servers registered (5):**

| Server | Endpoint | State |
|---|---|---|
| `cloudflare-api` | `https://mcp.cloudflare.com/mcp` | Needs authentication |
| `cloudflare-docs` | `https://docs.mcp.cloudflare.com/mcp` | Needs authentication |
| `cloudflare-bindings` | `https://bindings.mcp.cloudflare.com/mcp` | Needs authentication |
| `cloudflare-builds` | `https://builds.mcp.cloudflare.com/mcp` | Needs authentication |
| `cloudflare-observability` | `https://observability.mcp.cloudflare.com/mcp` | Needs authentication |

---

## NOT PROVEN — read this before relying on any of it

- **No Cloudflare account access has been established.** All five MCP servers
  report `Needs authentication`. They are registered, not connected. Nothing
  has read from or written to any Cloudflare account.
- **No Cloudflare account was inspected, and no DNS, Workers, R2, or zone
  data was touched.**
- **The install above lives in an ephemeral remote container.** When that
  container is reclaimed, `~/.claude/settings.json` and the installed plugin
  go with it. It does **not** reach your own machine.
- **The instructions were not read from the exact URL requested.** This
  environment's network policy blocks general outbound HTTPS, so
  `https://developers.cloudflare.com/agent-setup/prompt.md` could not be
  fetched by either `curl` or the fetch tool (403 at the egress proxy). The
  steps recorded here were retrieved instead from Cloudflare's own
  documentation MCP server, specifically the page
  `developers.cloudflare.com/agent-setup/claude-code/`. That is a first-party
  Cloudflare source, but it is not byte-for-byte the file that was asked for.

---

## Recurring cost disclosure

The plugin adds roughly **2,135 tokens of always-on context to every Claude
Code session** in which it is enabled, plus a per-use cost each time a skill
fires (the heaviest are `turnstile-spin` ~11.1k and `cloudflare-one` ~8.7k on
invoke). There is no monthly dollar charge for the plugin itself. Cloudflare
account usage is billed separately by Cloudflare according to whatever plan
the account is on.

If the always-on overhead is not wanted in sessions that have nothing to do
with Cloudflare, the plugin can be turned off with
`claude plugin disable cloudflare` and re-enabled later.

---

## To set up your own machine (the durable version)

Run these two commands inside Claude Code, from the root of the project you
want to work on:

```txt
/plugin marketplace add cloudflare/skills
/plugin install cloudflare@cloudflare
```

Then, the first time the agent calls a Cloudflare tool, a browser window will
open asking you to authorise access and choose which permissions to grant.
Until that login is completed, the Cloudflare tools will not work.

To confirm it worked afterwards:

```bash
claude mcp list
```

Each Cloudflare entry should read as connected rather than
`Needs authentication`.

---

## Optional: make this repo configure itself

Committing the following as `.claude/settings.json` in the repository root
means any checkout of this repo picks up the Cloudflare plugin automatically,
without anyone re-running the commands above:

```json
{
  "extraKnownMarketplaces": {
    "cloudflare": {
      "source": {
        "source": "github",
        "repo": "cloudflare/skills"
      }
    }
  },
  "enabledPlugins": {
    "cloudflare@cloudflare": true
  }
}
```

This file was **not** committed in this change — writing agent-configuration
files is gated by a permission guard in this environment, and it needs an
explicit approval. It still would not remove the OAuth login step, which is
per-person and per-machine by design.

---

## Verification commands

Re-runnable at any time:

```bash
claude plugin details cloudflare   # what is installed
claude mcp list                    # connection + auth state
npx wrangler whoami                # which Cloudflare account the CLI is using
```
