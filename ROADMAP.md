# Ship gates and outstanding engineering

## Implemented / tested
- Local MCP STDIO server with capability-gated tools and bounded output.
- Claude Desktop MCP Bundle manifest and Python/UV package validated.
- Local Codex configuration installed on reference Windows computer.
- Offline deterministic job engine and resumable local history receipts.
- Scoped text retrieval and bounded file search.
- Localhost Studio with Ollama tool-calling integration, explicit action queue,
  HTTP request Origin/Host/session checks, optional screen/browser panel.
- Multi-platform Python CI, tests and developer documentation.

## Remaining before claiming production-ready cross-platform remote control
- ChatGPT connector end-to-end test in an eligible paid workspace.
- Official OpenAI tunnel-client registration with user-controlled runtime key and
  tunnel ID, which the reference computer does not currently have.
- Production OAuth remote gateway for Claude/web and other public MCP hosts,
  plus multi-tenant device identity, outbound pairing and revocation.
- Broader model/hardware inference evaluations: a 1.5B local coder model
  produced a verified simple response, but robust agent tool execution is not established.
- Actual Windows/macOS/Linux GUI end-to-end tests with real screenshots,
  headless browser Chromium on macOS/Linux, and input consent across multiple monitors.
- Strong process sandboxing, filesystem race/secret protection, local per-action
  approval for external MCP clients, screen redaction, trust-model review.
- Signed installers, auto-update validation, accessibility tests and UI review,
  external security audit, release provenance/SBOM.
- Cost/latency/quality benchmark compared with providers; claims must be factual.
- Further UX polish, public documentation site and maintainer security contact.

Do not publish the localhost endpoint as an internet-facing public service.

Windows example.com Playwright+Chrome navigation is live-tested. Browser auth,
forms, downloads, and multi-step hostile-content scenarios need broader testing.
