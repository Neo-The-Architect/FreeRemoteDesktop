# FreeRemoteDesktop

**Your computer. Your model. Your rules.**

A model-neutral, self-hosted Model Context Protocol (MCP) desktop bridge.
FreeRemoteDesktop does not operate an LLM, bypass model subscriptions, or promise free tokens.
It replaces metered third-party desktop execution with a local tool server. MIT licensed.

## One-click Claude Desktop install (MCP Bundle)

Build and install the \`FreeRemoteDesktop-0.2.1.mcpb\` bundle using \`python pack_mcpb.py\`.
Choose this bundle from Claude Desktop's Extensions > Install Extension.
Select your approved workspace when prompted. Requires an MCPB host supporting the
UV runtime. This package does **not** embed Python; the host UV runtime manages it.
The manifest is validated with \`@anthropic-ai/mcpb\`; actual Claude GUI installation
has not yet been tested.

## Quick start

Requirements: Python 3.10+; Windows, macOS or Linux (GUI capture is primarily tested on Windows).

```sh
python setup.py plan --client codex
python setup.py install --client codex
python test_product.py
```

For Claude Desktop:

```sh
python setup.py plan --client claude-desktop
python setup.py install --client claude-desktop
```

Restart the selected client. Invoke `desktop_status` to confirm.
Fresh installations start with zero approved roots; choose one project directory in the dashboard or edit the config. Configuration is created at `~/.freeremotedesktop/config.json`, and existing
Codex/Claude config is backed up before editing. The installer never silently
changes another agent's configuration.

## Tools

| Tool | Default |
| --- | --- |
| desktop_status | enabled |
| list_directory | enabled within roots |
| read_text_file | enabled within roots |
| write_text_file | disabled |
| run_command | disabled; exact command allowlist |
| capture_screen | disabled; requires Pillow |
| gui_click | disabled; requires PyAutoGUI |
| browser_navigate / browser_snapshot / browser_screenshot / browser_click | disabled; Playwright + hostname allowlist; click also requires allow_gui |

Set the exact approved workspace paths and enable capabilities locally by editing
`~/.freeremotedesktop/config.json`. The user must explicitly opt in for every dangerous
capability. Avoid adding sensitive paths to `roots`. File-name checks are not a DLP solution.

Optional dependencies:
```sh
python -m pip install pillow pyautogui playwright
python -m playwright install chromium
```
The normal read-only installation has **zero third-party Python dependencies**.

## HTTP mode (local integration only)

```sh
# set FRD_BEARER_TOKEN to a strong, random secret using your OS secure environment settings
python server.py --transport http --port 8765
```

The HTTP listener binds **127.0.0.1 only**, requires bearer authentication, and is
not a production remote MCP deployment. Never publicly proxy it as-is. A remote
deployment needs OAuth, per-device user authentication, hardened host/origin and
network controls, token rotation, TLS, abuse prevention, and an audit review.

## Client/platform matrix

- **Codex and Claude Desktop:** supported via STDIO installer.
- **Other STDIO MCP agents:** configure command `python`, args `/absolute/path/server.py`.
- **Claude web/mobile:** needs an authenticated remote HTTPS MCP gateway; not supplied yet.
- **ChatGPT:** remote MCP connector availability and write tools depend on plan; not supplied yet.
- **@FreeRemoteDesktop:** availability depends on the host client's tool/plugin naming UI.
- **Computer vision:** `capture_screen` returns image bytes when enabled; host client must support rendering or consuming them.

## Security model

No privileged agent, daemon, unattended background service, or public endpoint installed.
Writes and control are opt-in. Protected filename/extension denylist, configured roots,
output/timeout caps, command exact-match allowlist, explicit overwrite flag, and JSONL
audit trail. These are protections, **not a sandbox**. Run under a low-privilege OS user.
Do not use on shared machines without additional OS account separation.
GUI and browser tools can expose confidential information; enable only with supervision.
No telemetry sent to Efficient Labs or any third party by this package.

## Architecture

```
MCP client -> STDIO transport -> policy-gated tools -> local computer
                           \-> optional authenticated loopback HTTP
```

## Current release status

**Developer preview v0.2.1; not ready for public production.** Remote authentication,
visual UI, full screen-streaming, per-action approvals,
machine-level integration tests, signed installers, packaging, cross-platform CI and
public vulnerability review remain to be implemented and verified.

## License

MIT. Copyright 2026 Efficient Labs contributors.
