# volatility-mcp
A PoC implementation of a MCP-Server for Volatility3.

I made this on Windows, see usage und the default values for why that matters.

## Setup

1. ``uv pip install``
2. Connect your LLM:
```json
{
 "mcpServers": {
    "volatility": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8000/mcp",
        "--allow-http"
      ]
    }
  }
}
```
3. Put your symbol files either in the ``.venv/Lib/site-packages/volatility3/symbols`` folder

## Usage

Start the server: ``uv run server.py``, you must provide the following flag:
- --dump <path/to/memory/dump>, default is the (empty) ``dumps/malware-linux.raw`` folder

You may specify where your volatility3 binary lives and which symbol files should be used:
- --symbols <path/to/your/symbols>, default is ``.venv/Lib/site-packages/volatility3/symbols`` 
- --bin <path/to/your/volatility/binary>, default is ``.venv/Scripts/vol.exe``

## LLMs

Use the prompt in the GEMINI.md for an agentic memory forensic scout that generates reports.
Or use it in the gemini-cli.
