# FreeRemoteDesktop v0.3.0 — Developer preview

New in v0.3.0:
- Local zero-additional-inference engineering CLI (`frd.py`) with explicit
  permission-gated recipes, offline scheduling and local job receipts.
- Local retrieval tools: `search_text` and `read_lines`, bounded and scoped
  to an approved workspace for context-efficient MCP usage.
- Studio: optional local Ollama chat UI, proposed action approval, private screen
  preview and browser inspection panel. Designed for local-only access.
- Official Secure MCP Tunnel onboarding helper for eligible ChatGPT accounts.
- Additional tests for offline jobs, retrieval, Studio agent flow and local HTTP
  security protections.

**Developer preview only.** The local Studio has passed mock-model automation tests and a live basic
response using Ollama qwen2.5-coder:1.5b; tool-calling quality on such a tiny
model remains limited and is not comparable to Codex. A local model is installed on the reference machine, but OpenAI Secure MCP
Tunnel is not yet authenticated. Claude
Desktop GUI installation, browser Chromium on macOS/Linux and live GUI input and end-to-end
remote ChatGPT/Claude control are not yet verified.

This release cannot bypass hosted chatbot usage limitations or guarantee
token-free AI reasoning. The included deterministic workflows make zero model
calls, while an optional local model may perform inference without paid APIs.

Live Windows verification: headless Google Chrome navigated to the allowlisted
example.com page, returning title and body text. Local Ollama model responded
successfully to a simple chat prompt. Full autonomous coding benchmarks remain open.
