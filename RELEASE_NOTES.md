# FreeRemoteDesktop v0.2.1 — Developer preview

A permission-first, MIT-licensed, self-hosted MCP desktop bridge.

## Working today
- Local MCP server, tested on Windows and via cross-platform CI
- Codex/Claude Desktop configuration installers and local permission UI
- Read-only directory and file tools by default
- Optional write, exact-allowlist command, screenshot, GUI and browser adapters
- UV-based MCP Bundle (`.mcpb`) for compatible local desktop clients

## Before using
Choose a single approved project workspace. No folders are approved on a new installation.
Write, shell, desktop control, screen capture and browser tools are disabled by default.

**Not a remote-service replacement yet:** ChatGPT/Claude cloud connector setup,
OAuth, production pairing, signed installers, reliable live computer vision and browser
end-to-end verification remain open milestones. There is no guarantee of zero model
tokens or access to paid model features.

Follow README and SECURITY instructions.
