# Remote Code Execution on an MCP Server with Novita Sandbox

This is a sample command-line application demonstrating how to create and use a remote code execution server with Novita AI’s Sandbox & Model API, MCP (Model Context Protocol), and the mcp-use library.

## How it works:

- **MCP Server**:  
  We build an MCP server that exposes several functions for:  
  - Code and command tool execution in the Sandbox.  
  - Creating and stopping sandbox sessions.  
  - Mock resource representing the user’s stock portfolio.  
  - An instruction prompt on interacting with the Sandbox.  
  
  The server runs over HTTP and makes these tools/resource/prompt available for clients to call.

- **MCP Client**:  
  The MCP client acts as the user interface. It connects to the MCP server using the **mcp-use** library, which:  
  - Manages communication with the LLM and MCP server.  
  - Handles tool function calls, resource and prompt access.  

  **mcp-use** creates and manages the AI agent that ties everything together.

- **User Interaction**:  
  The **user** provides prompts and the AI agent can use the MCP server if needed before responding.

## Prerequisites

- Python 3.11 or higher
- **[uv](https://github.com/astral-sh/uv) package manager** (We strongly recommend using this to setup the project).

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Studio1HQ/mcp_remote_execution.git
cd mcp_remote_execution
```

### 2. Install Dependencies

```bash
# Creates a virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate # For Mac/Linux
# or
.venv\Scripts\activate # For Windows

# Install dependencies
uv sync
```

### 3. Environment Configuration
Create a .env file in the root directory and add your API key and the below:

```bash
NOVITA_API_KEY="<your-novita-api-key>"
NOVITA_BASE_URL="https://api.novita.ai/v3/openai"

NOVITA_E2B_DOMAIN="sandbox.novita.ai"
NOVITA_E2B_TEMPLATE="code-interpreter-v1"
```


### 4. Start the MCP Server

```bash
uv run mcp_server.py
```

### 5. Run the MCP Client Application

```bash
uv run mcp_client.py
```

> **Note:** Make sure the URL in the MCP config dict matches the URL the MCP server is running on.  
> The default is `127.0.0.1:8000`, but yours might differ.

## 🖼️ Screenshots
**1.**
![Screenshot_1](/screenshots/screenshot_1.png)

**2.**
![Screenshot_2](/screenshots/screenshot_2.png)

**3.**
![Screenshot_3](/screenshots/screenshot_3.png)

## 📽️ Demo 1
I have $2,000. Get the performance of the major US stock indices from yfinance over the past 6 months and run ML models to predict how to allocate this investment to maximize potential returns over the next 2 months.


https://github.com/user-attachments/assets/397db075-bdd5-4882-84b9-571bf27a9005




## 📽️ Demo 2
Run multiple simulations of a U.S. economic deflation crash, pick the most probable and explain the impact it will have on my stock portfolio.



https://github.com/user-attachments/assets/83c01dc1-c8b9-49ab-8943-1448548d79fe







