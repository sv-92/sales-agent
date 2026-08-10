"""Entry point for running SalesFlow Agent: python -m salesflow_agent"""

import os
import subprocess
import sys
import time

from dotenv import load_dotenv

load_dotenv()


def main():
    # Validate environment
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key.")
        sys.exit(1)

    mcp_port = os.environ.get("MCP_SERVER_PORT", "8001")

    print("=" * 60)
    print("  SalesFlow Agent - GenAI Sales Assistant")
    print("=" * 60)

    # Start MCP CRM server as subprocess
    mcp_process = None
    try:
        print(f"\n[1/3] Starting MCP CRM server on port {mcp_port}...")
        mcp_process = subprocess.Popen(
            [sys.executable, "-m", "salesflow_agent.mcp.crm_server"],
            env={**os.environ, "MCP_SERVER_PORT": mcp_port},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        time.sleep(5)  # Give MCP server time to start

        if mcp_process.poll() is not None:
            stderr = mcp_process.stderr.read().decode() if mcp_process.stderr else ""
            print(f"  WARNING: MCP server failed to start: {stderr}")
            mcp_process = None
        else:
            print(f"  MCP CRM server running (PID: {mcp_process.pid})")

        # Seed database if needed
        from salesflow_agent.data.seed import ensure_seeded
        print("\n[2/3] Checking database...")
        ensure_seeded()
        print("  Database ready")

        # Start FastAPI
        print("\n[3/3] Starting FastAPI application...")
        print(f"\n  API: http://localhost:8000")
        print(f"  Docs: http://localhost:8000/docs")
        print(f"  MCP: http://localhost:{mcp_port}")
        print("\n" + "=" * 60)
        print("  Ready! Send queries to POST /agent/query")
        print("=" * 60 + "\n")

        import uvicorn
        uvicorn.run(
            "salesflow_agent.main:app",
            host="0.0.0.0",
            port=8000,
            log_level="info",
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        if mcp_process and mcp_process.poll() is None:
            mcp_process.terminate()
            mcp_process.wait(timeout=5)
            print("MCP server stopped")


if __name__ == "__main__":
    main()
