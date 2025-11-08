

## 🧐 Deeper Dive into the Model Context Protocol (MCP)

### What is MCP? The "USB-C for AI" 🔌

The **Model Context Protocol (MCP)** is an **open standard** that was introduced to solve the "N×M integration problem" in AI. Before MCP, every Large Language Model (LLM) and every external tool (like a database or a weather API) required custom "glue code" for them to talk, which was inefficient and hard to maintain.

MCP standardizes this communication, making it possible for **AI Agents** to:

1.  **Read Contextual Data (Resources):** Access up-to-date, external information like documents, databases, or configuration files (beyond their training data).
2.  **Execute Actions (Tools):** Call real-world functions like searching the web, sending an email, or performing a calculation.
3.  **Use Structured Workflows (Prompts):** Access expert-defined instructions to perform complex tasks reliably.

### MCP Architecture: Client, Server, and Transport

Your code implements the **MCP Server** part of this architecture, and your `client.py` simulates the **MCP Client** sending requests.

| Component | Role in MCP | Your Implementation |
| :--- | :--- | :--- |
| **MCP Server** | Exposes capabilities (Tools, Resources, Prompts) to the network. | **`main.py`** using `FastMCP`. |
| **MCP Client** | Part of the AI host (e.g., an IDE or Claude) that sends JSON-RPC requests to the server. | **`client.py`** using Python's `requests` library. |
| **Transport Layer** | The method of communication. | **HTTP** using **JSON-RPC 2.0** messages. |

-----

## 🧑‍💻 `main.py` Code Breakdown: The **MCP Server**

This server defines the specific capabilities made available to any connected AI agent.

### 1\. **Initialization** 🚀

```python
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
# Imports the necessary libraries. FastMCP is the SDK, and base provides MCP message structures.

mcp = FastMCP(name="hello_mcp",stateless_http=True)
# Initializes the FastMCP application. The 'name' is reported to clients. 
# 'stateless_http=True' configures it to run as a web server, which is the most common transport for remote, sharable MCP servers.

mcp_app = mcp.streamable_http_app()
# Exposes the MCP server logic as a standard FastAPI application, ready to be run by a web server like Uvicorn.
```

### 2\. **Tools: Actionable Functions** 🔨

Tools are defined as standard Python functions, but the `@mcp.tool` decorator registers their metadata (name, description, arguments) with the MCP interface. An LLM uses the `description` to decide *if* and *how* to call the tool.

```python
@mcp.tool(name="online_researcher", description="Search the web for information")
def search_online(query: str) -> str:
    # This function is exposed via the MCP method "tools/call".
    # The 'query: str' argument is automatically validated by FastMCP/Pydantic.
    return f"Results for {query}..."

@mcp.tool(name="Get_Weather",description="fetch the weather of given city")
def Get_weather(city:str)->str:
    # When a client sends a JSON-RPC request for 'Get_Weather', this function is executed.
    return f"the weather in {city} is sunny."
```

### 3\. **Resources: Contextual Data** 📁

Resources allow clients to retrieve static or dynamic context. They are accessed via a **Uniform Resource Identifier (URI)**.

  * **URI Scheme:** `docs://` is a custom scheme you defined.
  * **MIME Type:** Specifies the data format (e.g., `application/json`, `text/plain`).

<!-- end list -->

```python
# Internal document store
docs = { 
    "report.pdf": "...", 
    "plan.md": "...", 
    "spec.txt": "...", 
    "financial.docx": "..."
}

# Static Resource: Lists all available documents
@mcp.resource(
    "docs://documents",
    mime_type="application/json"
)
def list_docs() -> list[str]:
    # Accessible via the MCP method "resources/read" with URI="docs://documents"
    return list(docs.keys())

# Templated Resource: Reads a single document
@mcp.resource(
    "docs://{doc_id}",
    mime_type="text/plain"
)
def get_doc(doc_id: str) -> str:
    # Accessible via "resources/read" with URI like "docs://plan.md"
    return docs[doc_id]
```

### 4\. **Prompts: Structured Tasks** 📝

Prompts are reusable, named instructions. A client calls the `prompts/get` method to receive the structured `base.Message` object, which is then passed to the LLM.

```python
@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format."
)
def format_document(
    doc_id: str = Field(description="Id of the document to format") # Pydantic Field adds rich LLM metadata
) -> list[base.Message]:
    prompt = f"""
Your goal is to reformat a document to be written with markdown syntax...
"""
    return [
        base.UserMessage(prompt)
    ] # The output is a list of Message objects, adhering to the MCP Prompt output specification.
```

-----

## 📞 `client.py` Code Breakdown: The **MCP Client Simulator**

This client simulates how an external system (like an AI agent or a development environment) communicates with your MCP Server using **JSON-RPC 2.0 over HTTP**.

### 1\. **Client Setup**

```python
import requests
url = "http://127.0.0.1:8000/mcp/" # The endpoint where the FastMCP server is running
```

The core of the client relies on two reusable helper functions to construct the standard JSON-RPC request body:

```python
def get_body(method: str, params: dict = {}, id: int = 1):
    # This structure is mandatory for the JSON-RPC 2.0 protocol
    return {
        "jsonrpc": "2.0",
        "method": method, # The specific MCP method (e.g., "tools/call")
        "id": id,         # A unique identifier for the request
        "params": params, # The arguments for the method
    }
```

### 2\. **Calling Tools** (`method`: `tools/call`)

```python
# The payload instructs the server to execute the 'Get_Weather' tool with 'New York' as the 'city' argument.
tool_body = { 
    "jsonrpc":"2.0",
    "method": "tools/call", 
    "id": 1, 
    "params": { 
        "name": "Get_Weather", 
        "arguments": { 
            "city": "New York" 
        } 
    }
}
response = requests.post(url, headers=tool_headers, json=tool_body)
print(response.text) 
# Expected Output: {"jsonrpc": "2.0", "result": "the weather in New York is sunny.", "id": 1}
```

### 3\. **Accessing Resources**

  * **Discovery (`method`: `resources/list` and `resources/templates/list`)**:

    ```python
    response_list = requests.post(url, headers=R_headers, json=get_body("resources/list", id=1)) 
    # Lists all static URIs ("docs://documents")

    response_templates = requests.post(url, headers=R_headers, json=get_body("resources/templates/list", id=3))
    # Lists all templated URIs ("docs://{doc_id}")
    ```

  * **Reading Content (`method`: `resources/read`)**:

    ```python
    # Read the static 'list_docs' resource
    requests.post(url, ..., json=get_body("resources/read", {"uri": "docs://documents"}, id=2))

    # Read the templated 'get_doc' resource for a specific file
    requests.post(url, ..., json=get_body("resources/read", {"uri": "docs://plan.md"}, id=4))
    ```

### 4\. **Retrieving Prompts** (`method`: `prompts/list` and `prompts/get`)

```python
# Discovery
requests.post(url, headers=headers, json=get__body("prompts/list", id=1)) 
# Returns a list containing the name "format"

# Retrieval
requests.post(url, headers=headers, json=get__body("prompts/get", {
    "name": "format", 
    "arguments": {"doc_id": "..."}
}, id=2)) 
# Returns the structured base.Message content generated by the format_document function.




