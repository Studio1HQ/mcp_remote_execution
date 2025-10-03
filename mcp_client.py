import asyncio
import os
from datetime import datetime

import mcp_use
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Load environment variables
load_dotenv()

console = Console()

# Note: 1 for INFO level, 2 for full verbose DEBUG level and 0 for NO debug output.
mcp_use.set_debug(1)


async def main(model: str, base_url: str, api_key: str):

    # Create configuration dictionary
    config = {
        "mcpServers": {
            "stock&sandbox": {
                # If the url the mcp server is running at is different replace below,
                # also remember to add /mcp.
                "url": "http://127.0.0.1:8000/mcp",
            }
        }
    }

    # Create MCPClient from configuration dictionary
    client = MCPClient(config)

    # Create LLM
    llm = ChatOpenAI(model=model, base_url=base_url, api_key=api_key)

    # Create agent with the client
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=25,
        memory_enabled=True,  # mcp-use will auto handle the conversation history.
        system_prompt=f"""
        You are a helpful assistant and the current date is {datetime.now().strftime('%Y-%m-%d')}
        
        MUST REMEMBER:
        - Before any tool call first call instructions_for_sandbox_use() so you can read them.
        - Ensure you call stop_sandbox_session() after using the sandbox before responding to the user.
        """,
    )

    console.print(
        Panel(
            "[bold green]MCP Session Started[/bold green]\nType 'quit()' to exit.",
            title="MCP Session",
            border_style="green",
        )
    )

    try:
        while True:
            user_input = Prompt.ask("\n[bold yellow]>>> User Message[/bold yellow]")

            if user_input.lower().strip() == "quit()":
                break

            # Pass the query to the agent and await the response.
            response = await agent.run(user_input)
            console.print(f"\n[bold green]>>> Assistant Response: {response} [/]")

    finally:
        # Will trigger closure of sandbox on MCP server if it sill active.
        session = await client.create_session("stock&sandbox")
        await session.call_tool(name="stop_sandbox_session", arguments=None)
        await session.disconnect()


if __name__ == "__main__":
    asyncio.run(
        main(
            model="qwen/qwen3-coder-480b-a35b-instruct",
            base_url=os.getenv("NOVITA_BASE_URL"),
            api_key=os.getenv("NOVITA_API_KEY"),
        )
    )
