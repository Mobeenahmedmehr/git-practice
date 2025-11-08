## 🧐 Understanding the Modular Communication Protocol (MCP)

### What is MCP? 🧠

The **Modular Communication Protocol (MCP)** is a standardized specification for building **composable AI agents and services**. It defines a universal set of interfaces (like Tools, Resources, and Prompts) that allow different services, models, and agents to interact with each other in a predictable way using **JSON-RPC** over HTTP.

In essence, MCP acts as a **middleware for AI systems**, making it easy to discover, execute, and share capabilities and data across a distributed system.

### Why Use `FastMCP`? 🛠️

`FastMCP` is a Python implementation built on the high-performance **FastAPI** framework. It simplifies the process of creating an MCP server by providing decorators (`@mcp.tool`, `@mcp.resource`, `@mcp.prompt`) that automatically handle the necessary routing, JSON-RPC serialization, and documentation.

-----

## 🧑‍💻 `main.py` Code Breakdown: The Server

This file defines the **MCP server**, exposing its capabilities through the standard protocol.

```python
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
# Imports necessary components. Field from Pydantic is used for structured argument definition.

mcp = FastMCP(name="hello_mcp",stateless_http=True)
# Initializes the FastMCP application.
# 'name': The application's public name.
# 'stateless_http=True': Configures the server to use standard HTTP request/response handling, 
# suitable for stateless operations like tools, resources, and prompts.

#Implementing TOOLS:
# Tools are external capabilities or actions the server can perform.

@mcp.tool(name="online_researcher", description="Search the web for information")
def search_online(query: str) -> str:
    # Decorator registers the Python function as an MCP Tool.
    # 'name' and 'description' are exposed via the MCP interface.
    # The function signature (query: str) defines the required input arguments.
    # TODO: Implement search logic (e.g., calling the Google Search API).
    return f"Results for {query}..."

@mcp.tool(name="Get_Weather",description="fetch the weather of given city")
def Get_weather(city:str)->str:
    # Another Tool example with 'city' as the required argument.
    return f"the weather in {city} is sunny."

#Implementing RESOURCES:
# Resources expose data (documents, databases, etc.) to the client.

docs = {
    # A simple dictionary acting as an in-memory document store.
    "report.pdf": "the report details the state of a 20m condenser tower.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
    "financial.docx": "these financial outline the projects budget and expenditure."
}

@mcp.resource(
    "docs://documents",
    mime_type="application/json"
)
def list_docs() -> list[str]:
    # A static Resource that returns a list of all document keys (IDs).
    # "docs://documents" is the unique URI clients use to access this resource.
    # mime_type="application/json" specifies the expected output format.
    return list(docs.keys())

@mcp.resource(
    "docs://{doc_id}",
    mime_type="text/plain"
)
def get_doc(doc_id: str) -> str:
    # A templated Resource. {doc_id} acts as a path parameter in the URI.
    # When a client requests "docs://plan.md", the function is called with doc_id="plan.md".
    # mime_type="text/plain" indicates the content is plain text.
    return docs[doc_id]

#PROMPTS: Structured tasks for AI models

@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format."
)
def format_document(
    doc_id: str = Field(description="Id of the document to format")
) -> list[base.Message]:
    # A Prompt defines a specific generative task, providing a structured query for an AI.
    # Field from Pydantic adds richer documentation/metadata to the argument.
    prompt = f"""
Your goal is to reformat a document to be written with markdown syntax.
...
"""
    return [
        base.UserMessage(prompt)
    ]
    # Returns a list of base.Message objects (e.g., a UserMessage), which is the standard 
    # MCP format for structured prompts that an agent or model can process.

mcp_app = mcp.streamable_http_app()
# The final FastAPI application object, ready to be served by a WSGI/ASGI server like Uvicorn.
```

-----

## 📞 `client.py` Code Breakdown: The Client

The client demonstrates how to use **`requests`** to communicate with the `FastMCP` server using the **JSON-RPC 2.0** protocol over HTTP POST.

### 🌐 Key Client Concepts

  * **URL:** The base endpoint for all MCP requests is `http://127.0.0.1:8000/mcp/`.
  * **Headers:** `Accept` headers typically include `application/json` and `text/event-stream` for both synchronous and streaming responses.
  * **JSON-RPC Body:** Every request is a JSON object with:
      * `"jsonrpc": "2.0"`: Specifies the protocol version.
      * `"method"`: The MCP interface being called (e.g., `tools/call`, `resources/read`).
      * `"id"`: A unique identifier for the request, allowing the client to match responses.
      * `"params"`: A dictionary containing the method-specific arguments.

### 1\. Tools Usage 🧰

```python
# TOOLS:
tool_body = {
    "jsonrpc":"2.0",
    "method": "tools/call", # The method to execute a tool
    "id": 1,
    "params": {
        "name": "Get_Weather", # The registered name of the tool
        "arguments": {
            "city": "New York" # The arguments expected by the tool function
        }
    }
}
response = requests.post(url,headers=tool_headers,json=tool_body)
print(response.text) # Prints the tool's return value ("the weather in New York is sunny.")
```

### 2\. Resources Usage 📁

A helper function `get_body` is used to structure the standard JSON-RPC request body.

```python
def get_body(method: str, params: dict = {}, id: int = 1):
    # Standardizes the JSON-RPC request structure.
    return {
        "jsonrpc": "2.0",
        "method": method,
        "id": id,
        "params": params,
    }

# List Resources: Calls the 'resources/list' method to discover available resources.
response_list = requests.post(url, ..., json=get_body("resources/list", id=1))

# Read Static Resource: Calls 'resources/read' with the static URI "docs://documents"
response_read = requests.post(url, ..., json=get_body("resources/read", {"uri": "docs://documents"}, id=2)) 
# Response contains the list of document keys.

# List Templates: Calls 'resources/templates/list' to discover templated URIs (like "docs://{doc_id}").
body_templates = get_body("resources/templates/list", id=3)

# Read Templated Resource: Calls 'resources/read' with a concrete URI, "docs://plan.md"
body_read = get_body("resources/read", {"uri": "docs://plan.md"}, id=4)
# Response contains the content of "plan.md".
```

### 3\. Prompts Usage 📝

```python
# List Prompts: Calls 'prompts/list' to discover available prompt names ("format").
response_list = requests.post(url, ..., json=get__body("prompts/list", id=1))

# Get Prompt: Calls 'prompts/get' to generate the structured message for the "format" prompt.
response_read = requests.post(url, ..., json=get__body("prompts/get", {
    "name": "format", 
    "arguments": {
        "doc_id": "Agentic AI is a new paradigm..." # Passes the required argument
    }
}, id=2))
# Response contains the structured prompt text defined in main.py, ready for an AI model.
```
