# Roadmap and ship gates

## Verified in developer preview v0.2.1
- Local STDIO MCP with eleven tools and JSON-RPC init/tool discovery.
- Windows Codex client setup (configuration backup), configurable Claude Desktop setup.
- Capability and workspace restrictions with deny-by-default writes, shell, GUI and browser.
- Basic audit log and a local Tkinter permission control center.
- HTTP loopback-only bearer transport (not a hosted remote connector).
- MIT repository, unit tests, UV-based MCP Bundle manifest validated by MCPB CLI.
- Package run verified with UV; cross-platform CI for core tests.

## Required before recommending production remote desktop access
- OAuth 2.1 / PKCE authenticated remote MCP gateway with per-user and per-device identities.
- Outbound-only device pairing, secure revocation and token rotation; no direct unprotected desktop exposure.
- Device-side per-action consent for high-risk actions; isolated unprivileged execution.
- Signed and reproducible Windows/macOS/Linux installers and updates.
- Screen-sharing session consent, redaction, frame-rate limits, secure streaming and revocation.
- Browser permissions, download protections, allowlisted URLs and end-to-end interactive testing.
- Secret scanning and content-based DLP, symlink race/hardlink protections, stricter process sandboxing.
- Prompt injection red-team audit, pentest, threat model, vulnerability reporting contact.
- Host-specific @mention/plugin onboarding and actual ChatGPT/Claude end-to-end integration tests.
- Cost/latency/tokens benchmark against baseline (no unverified token-saving claims).
- Accessibility tests, usability tests, privacy policy, release signing, license attribution checks.

## Current capability caution

The following features exist only as code paths or opt-in adapters and have not been live tested on a real
Claude/ChatGPT remote session: GUI click, Playwright Chromium browser use, computer vision tool rendering,
and remote network gateway.

Do not advertise the current developer preview as production secure remote control.
