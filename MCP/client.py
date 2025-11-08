import requests



url = "http://127.0.0.1:8000/mcp/"

#TOOLS:
tool_headers = {
    "Accept":"application/json,text/event-stream",
}

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
response = requests.post(url,headers=tool_headers,json=tool_body)
print(response.text)

#RESOURCES:

R_headers = {"Accept": "application/json,text/event-stream"}

def get_body(method: str, params: dict = {}, id: int = 1):
    return {
        "jsonrpc": "2.0",
        "method": method,
        "id": id,
        "params": params,
    }

response_list = requests.post(url, headers=R_headers, json=get_body("resources/list", id=1))
print("\nList Resources:", response_list.text)

response_read = requests.post(url, headers=R_headers, json=get_body("resources/read", {"uri": "docs://documents"}, id=2))
print("\nRead Resource:", response_read.text)

## Templated Resources

body_templates = get_body("resources/templates/list", id=3)
response_templates = requests.post(url, headers=R_headers, json=body_templates)
print("\nList Templates:", response_templates.text)

body_read = get_body("resources/read", {"uri": "docs://plan.md"}, id=4)
response_read = requests.post(url, headers=R_headers, json=body_read)
print("\nRead Resource:", response_read.text)

#PROMPTS:

headers = {"Accept": "application/json,text/event-stream"}

def get__body(method: str, params: dict = {}, id: int = 1):
    return {
        "jsonrpc": "2.0",
        "method": method,
        "id": id,
        "params": params,
    }

response_list = requests.post(url, headers=headers, json=get__body("prompts/list", id=1))
print("\nList Prompts:", response_list.text)

response_read = requests.post(url, headers=headers, json=get__body("prompts/get", {"name": "format", "arguments": {"doc_id": "Agentic AI is a new paradigm in AI that is based on the idea that AI should be able to learn and adapt to new tasks and environments."}}, id=2))
print("\nRead Prompt:", response_read.text)