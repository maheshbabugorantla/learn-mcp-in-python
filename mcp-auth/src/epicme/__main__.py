"""Run the EpicMe authorization server: `uv run epicme-auth`.

You need this running in its own terminal whenever you want to talk to your
resource server from a real MCP client or the Inspector. The tests don't need
it — they run the same app in-process.
"""

from __future__ import annotations

import uvicorn

from epicme.auth_server import AUTH_SERVER_PORT, auth_app


def main() -> None:
    print(f"EpicMe authorization server on http://localhost:{AUTH_SERVER_PORT}")
    print("  metadata: /.well-known/oauth-authorization-server")
    print("  users:    kody, olivia (no password — pick one on the consent screen)")
    uvicorn.run(auth_app, host="localhost", port=AUTH_SERVER_PORT, log_level="warning")


if __name__ == "__main__":
    main()
