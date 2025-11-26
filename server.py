import argparse
import logging
import subprocess
from pathlib import Path
from fastmcp import FastMCP

DUMP_PATH = None
SYMBOLS_PATH = None
VOL_BIN = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

mcp = FastMCP("Volatility 3")

@mcp.tool()
def list_plugins() -> str:
    """
    List available Volatility plugins
    :return: string representation of available plugins
    """
    cmd = [
        VOL_BIN,
        "-h"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            return f"Error running Volatility: {result.stderr}"
        marker = "For plugin specific options, run 'vol.exe <plugin> --help'"
        plugin_result = result.stdout
        if marker in plugin_result:
            lst = plugin_result.split(marker)
            if len(lst) > 1:
                return lst[1]
            else:
                return "Unable to list plugins"
        else:
            return "Unable to list plugins"
    except FileNotFoundError:
        return f"Could not find the Volatility binary at: {VOL_BIN}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

@mcp.tool()
def plugin_help(plugin: str) -> str:
    """
    Gets the help text (-h) for a plugin
    :return: The help text (-h) for a plugin
    """
    cmd = [
        VOL_BIN,
        "-s", SYMBOLS_PATH,
        "-f", DUMP_PATH,
        plugin,
        "-h"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            return f"Error running Volatility: {result.stderr}"

        return result.stdout

    except FileNotFoundError:
        return f"Could not find the Volatility binary at: {VOL_BIN}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

@mcp.tool()
def execute_plugin(plugin: str, args: dict) -> str:
    """
    Execute a Volatility plugin.
    :param plugin: The name of the plugin e.g. 'linux.pslist.PsList'
    :param args: Arguments for the plugin e.g. '--pid 1234', meaning the arg should look like this: {"--pid", 1234}
    :return: The results of the plugin execution
    """

    cmd = [
        VOL_BIN,
        "-s", SYMBOLS_PATH,
        "-f", DUMP_PATH,
        "-r", "pretty",
        plugin
    ]
    checked_args = {}

    for key, value in args.items():
        if "--" in key:
            new_key = key
        else:
            new_key = f"--{key}"
        checked_args[new_key] = value

    for key, value in checked_args.items():
        cmd.append(key.strip("'\""))
        if value not in (None, ""):
            cmd.append(str(value))

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            return f"Error running Volatility: {result.stderr}"

        return result.stdout

    except FileNotFoundError:
        return f"Could not find the Volatility binary at: {VOL_BIN}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Volatility MCP Server - Memory Analysis via MCP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using default paths (assumes dump in ./dumps/ and symbols in venv)
  python vol_mcp_server.py --dump ./dumps/memory.raw

  # Specifying custom paths
  python vol_mcp_server.py --dump /path/to/dump.raw --symbols /path/to/symbols
        """
    )

    parser.add_argument(
        '--dump', '-d',
        dest='dump_path',
        required=False,
        default=Path("./dumps/malware-linux.raw"),
        help='Path to the memory dump file (default: ./dumps/malware-linux.raw)'
    )

    parser.add_argument(
        '--symbols', '-s',
        dest='symbols_path',
        required=False,
        default=Path(".venv/Lib/site-packages/volatility3/symbols"),
        help='Path to Volatility symbols directory (default: .venv/Lib/site-packages/volatility3/symbols)'
    )

    parser.add_argument(
        '--bin', '-b',
        dest='vol_bin',
        required=False,
        default=Path(".venv/Scripts/vol.exe"),
        help='Path to Volatility binary (default: .venv/Scripts/vol.exe)'
    )

    return parser.parse_args()

def init_server():
    try:
        args = parse_arguments()
        global DUMP_PATH
        DUMP_PATH = args.dump_path
        global SYMBOLS_PATH
        SYMBOLS_PATH = args.symbols_path
        global VOL_BIN
        VOL_BIN = args.vol_bin
    except Exception as e:
        logger.error("Error in server init: %s", e)

def main():
    init_server()
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()