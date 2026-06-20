"""HTTP/SSE transport for Sentor MCP — for remote deployment (Claude.ai web, hosted environments)."""

import os
from sentor_mcp.server import mcp

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    mcp.run(transport="sse", host="0.0.0.0", port=port)
