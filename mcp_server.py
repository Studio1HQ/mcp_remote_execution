import asyncio
import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from sandbox_manager import SandboxManager

# load .env variables
load_dotenv()

console = Console()

# Initialize FastMCP server
mcp = FastMCP("MCP_Server")

# Initialize sandbox manager for the singleton sandbox instance.
sandbox_manager = SandboxManager(
    sandbox_template=os.getenv("NOVITA_E2B_TEMPLATE"),
    api_key_for_sandbox=os.getenv("NOVITA_API_KEY"),
    sandbox_domain=os.getenv("NOVITA_E2B_DOMAIN"),
    sandbox_timeout=900,  # 900 seconds (15 minutes), sandbox instance will be killed automatically after.
)


def display_sandbox_code_output(code_result: dict):
    """
    Beautifully display the output from sandbox code execution.

    Args:
        code_result (dict): Sandbox execution results with structure:
            {
                "outputs": list[str],
                "logs": list[str],
                "error": list[str]
            }
    """

    if not code_result["error"]:
        output_table = Table(show_header=True, header_style="bold magenta")
        output_table.add_column("Code Execution Output")

        output_table.add_row(str(code_result))
        console.print(output_table)

    else:
        console.print(
            Panel(
                f"[bold red]Error:[/bold red] {code_result['error']}",
                title="Execution Error",
                border_style="red",
            )
        )


def display_sandbox_command_output(command_result: dict):
    """
    Beautifully display the output from sandbox command execution.

    Args:
        command_result (dict): Sandbox command results with structure:
            {
                "output": str,
                "execution error": str
            }
    """

    if command_result["output"]:
        output_table = Table(show_header=True, header_style="bold magenta")
        output_table.add_column("Command Execution Output")
        output_table.add_row(str(command_result["output"]))
        console.print(output_table)

    if command_result["execution error"]:
        console.print(
            Panel(
                f"[bold red]Error:[/bold red] {command_result['execution error']}",
                title="Execution Error",
                border_style="red",
            )
        )


@mcp.prompt()
def instructions_for_sandbox_use() -> str:
    """
    RETURNS MUST READ INSTRUCTIONS FOR SANDBOX USE.
    """
    return """
    When you want to use the sandbox function, you must first create a new sandbox session by calling the create_sandbox_session() function.
    Then you can use the run_python_code() or run_on_command_line() function to run on the sandbox.
    When you are done, you must kill the sandbox session by calling the stop_sandbox_session() function.

    Note: 
    - There can only be one sandbox session at a time, creating another sandbox when one is active will kill
    the previous sandbox session.

    - The sandbox already comes pre-installed with the usual data analysis packages but if there's a package you
    are not sure exists or your code had an import error due to a missing package, you can check if it's installed and if not install it.
    """


@mcp.tool()
def create_sandbox_session() -> str:
    """
    This will create a new singleton sandbox instance meaning any pre-existing sandbox will be killed.
    """
    return sandbox_manager.create_sandbox_session()


@mcp.tool()
def stop_sandbox_session() -> str:
    """
    This will kill the active singleton sandbox instance if any.
    """
    return sandbox_manager.stop_sandbox_session()


@mcp.tool()
def run_python_code(python_code: str) -> dict:
    """
    Runs the python code on the active sandbox, and if there any image outputs they are skipped.

    Args:
        python_code (str): The python code to run.

    Returns:
        dict: Containing stdout, logs, error, etc.
    """
    console.print(
        Panel(
            python_code,
            title="Agent Executing Python Code",
            border_style="blue",
        )
    )
    result = sandbox_manager.run_python_code(python_code)
    # display the result. Note: only do this in test not in prod.
    display_sandbox_code_output(result)
    return result


@mcp.tool()
def run_on_command_line(command_line: str) -> dict:
    """
    Runs the command line on the active sandbox, and if there are any image outputs they are skipped.

    Args:
        command_line (str): The command line to run.

    Returns:
        dict: Containing stdout, logs, error, etc.
    """
    console.print(
        Panel(
            command_line,
            title="Agent Executing Command Line",
            border_style="blue",
        )
    )
    result = sandbox_manager.run_on_command_line(command_line)
    # display the result. Note: only do this in test not in prod.
    display_sandbox_command_output(result)
    return result


@mcp.resource("data://user_stock_portfolio")
def get_user_portfolio() -> dict:
    """
    Returns the user's portfolio holdings across major index ETFs
    and individual stocks.

    Returns:
        dict: Portfolio with ticker symbols, quantities, and average purchase prices
    """
    portfolio = {
        "holdings": [
            # Major Index ETFs
            {
                "ticker": "SPY",
                "name": "SPDR S&P 500 ETF",
                "quantity": 4,
                "avg_purchase_price": 670.13,
                "asset_type": "ETF",
            },
            {
                "ticker": "QQQ",
                "name": "Invesco QQQ Trust",
                "quantity": 2,
                "avg_purchase_price": 610.34,
                "asset_type": "ETF",
            },
            {
                "ticker": "DIA",
                "name": "SPDR Dow Jones Industrial Average ETF",
                "quantity": 5,
                "avg_purchase_price": 468.90,
                "asset_type": "ETF",
            },
            # Individual Tech Stocks
            {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "quantity": 2,
                "avg_purchase_price": 257.13,
                "asset_type": "Stock",
            },
            {
                "ticker": "NVDA",
                "name": "NVIDIA Corporation",
                "quantity": 6,
                "avg_purchase_price": 188.94,
                "asset_type": "Stock",
            },
            # Other Sectors
            {
                "ticker": "JNJ",
                "name": "Johnson & Johnson",
                "quantity": 1,
                "avg_purchase_price": 185.98,
                "asset_type": "Stock",
            },
            {
                "ticker": "TSLA",
                "name": "Tesla, Inc.",
                "quantity": 5,
                "avg_purchase_price": 436.00,
                "asset_type": "Stock",
            },
            {
                "ticker": "KO",
                "name": "The Coca-Cola Company",
                "quantity": 3,
                "avg_purchase_price": 66.10,
                "asset_type": "Stock",
            },
        ]
    }

    return portfolio


if __name__ == "__main__":
    # run the server
    # Note: We use streamable-http as the transport protocol instead of stdio because we are
    # printing to the console which would block stdio.
    # Also in production you should use SSE or streamable-http rather than stdio.
    try:
        asyncio.run(mcp.run(transport="streamable-http"))
    finally:
        # When server stops abruptly, we need to kill the sandbox session if it exists.
        sandbox_manager.stop_sandbox_session()
        sandbox_manager = None
