# FreeRemoteDesktop: ChatGPT / Claude / local fallback

FreeRemoteDesktop offers three independent paths. They cannot be combined to bypass
a hosted model provider's subscriptions, rate limits or inference metering.

## A. Local MCP — Codex, Claude Desktop, Pi, other STDIO clients
Use `python setup.py install --client codex`, the Claude Desktop MCP Bundle
(`.mcpb`), or configure a custom STDIO command `python server.py`.
Tool availability is always subject to the local capabilities configuration.

## B. Local AI Studio (zero paid inference when using local Ollama)

1. Install [Ollama](https://ollama.com/download), if not already installed.
2. Download **a model that supports tool calling** suited to your own hardware:
   `ollama pull <your-selected-model>`. Model licenses and hardware needs vary.
3. Run `python local_studio.py`.
4. Open `http://127.0.0.1:8899` in a browser on that same computer.
5. Select the local model and use the approved workspace. The browser controls
   only the localhost Studio; no external account is required.

Studio implements local chat, multi-step bounded tool calls, human approval for
write/control proposals, a deterministic job panel, a private screen preview
(requires local permission), and an approved-host headless browser panel.
The current Studio is a local development preview, not a hosted service. A basic
Ollama qwen2.5-coder:1.5b reply has been verified on Windows, but a small model
cannot be assumed to reliably perform multi-step engineering tool calls.

**No remote model bill** does not mean no tokens are computed by the local model,
and it does not mean the output quality is equivalent to a large cloud coding
assistant. CPU-only models may be slow. A remote ChatGPT tab with exhausted
usage cannot switch itself to this local Studio.

## C. ChatGPT via official private MCP tunnel

1. Read [OpenAI Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)
   and [tunnel-client](https://github.com/openai/tunnel-client).
2. Have your organization's tunnel ID and runtime key, and the correct workspace
   permissions; use **runtime** credentials, never admin credentials in the daemon.
3. Install the official `tunnel-client`.
4. On the computer, set the following in a secure local terminal/session:
   `CONTROL_PLANE_TUNNEL_ID` and `CONTROL_PLANE_API_KEY`.
   **Do not send secrets through ChatGPT or commit them to GitHub.**
5. Run `python connect_chatgpt.py plan`, `python connect_chatgpt.py init`,
   `python connect_chatgpt.py doctor`, then `python connect_chatgpt.py run`.
6. In ChatGPT Plugins, add a custom MCP server under the supported workspace,
   select Tunnel and use the appropriate tunnel ID. Name it FreeRemoteDesktop,
   then test `desktop_status`.

This keeps the desktop MCP server private and uses the official outbound tunnel.
It is **not** an account-wide, free replacement for ChatGPT/Codex.
As of November 2026, ChatGPT Pro custom MCP access is read/fetch only;
full custom MCP write access requires an eligible Business or Enterprise/Edu
workspace. Entitlements and policies can change.

The current project has no direct public MCP endpoint. Do **not** expose its
localhost Studio or bearer-only HTTP endpoint through a public proxy. An
OAuth-protected hosted gateway for multi-user Claude/ChatGPT use is a separate
deployment and security review requirement.

## Free / open-source economics

- License: MIT; no subscription to this project's author for local tool execution.
- Local deterministic recipes: **0 LLM calls**.
- Local Ollama chat: **0 paid cloud-model calls**, but consumes local inference
  tokens, RAM/GPU/CPU, storage and electricity.
- MCP into a paid or free hosted model: subject to that provider's API/chat
  usage meter, available connector permissions and fair-use rules.
- Optional cloud hosting, tunneling and bandwidth: depend on service provider.

## Security / UX

Defaults: no approved paths until configured; no shell, write, screen, mouse
or browser access. Workspace roots, browser hosts and execution capabilities
are selected on the local machine. Studio requires explicit approval for every
proposed mutating tool call. Use a dedicated unprivileged OS account for any
unattended or remotely accessible deployment.

Never enable a public URL for your actual desktop without robust user auth,
audience-bound tokens, per-device revocation, rate limits, audit review and
independent threat-model / penetration testing.
