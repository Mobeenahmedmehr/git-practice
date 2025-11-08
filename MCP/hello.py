from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
mcp = FastMCP(name="hello_mcp",stateless_http=True)

#Implementing TOOLS:

@mcp.tool(name="online_researcher", description="Search the web for information")
def search_online(query: str) -> str:
    # TODO: Implement search logic
    return f"Results for {query}..."

@mcp.tool(name="Get_Weather",description="fetch the weather of given city")
def Get_weather(city:str)->str:
    return f"the weather in {city} is sunny."

#Implementing RESOURCES:

docs = {
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
    return list(docs.keys())


@mcp.resource(
    "docs://{doc_id}",
    mime_type="text/plain"
)
def get_doc(doc_id: str) -> str:
    return docs[doc_id]


#PROMPTS
@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format."
)
def format_document(
    doc_id: str = Field(description="Id of the document to format")
) -> list[base.Message]:
    prompt = f"""
Your goal is to reformat a document to be written with markdown syntax.

The id of the document you need to reformat is:
<document_id>
{doc_id}
</document_id>

Add in headers, bullet points, tables, etc as necessary. Feel free to add in structure.
Use the 'edit_document' tool to edit the document. After the document has been reformatted...
"""
    
    return [
        base.UserMessage(prompt)
    ]




mcp_app = mcp.streamable_http_app()
