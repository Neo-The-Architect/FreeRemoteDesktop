# Security policy

Do not connect a raw desktop MCP HTTP endpoint directly to the public internet.
STDIO is preferred for local use. Restrict project roots and run as an unprivileged
OS user. Do not turn on write, shell, GUI or browser tools in untrusted chats.
Prompt injections in files and websites can cause agents to propose unwanted actions.
The default command allowlist is conservative, but an intentionally changed allowlist
can run commands with the agent user's full operating-system permissions.

Audit log: ~/.freeremotedesktop/audit.jsonl (local only).
Report vulnerabilities privately to the project maintainer before disclosure.
Until a security contact is published, do not include credentials in public issues.
