from google.adk.tools import FunctionTool
from google.adk import Agent
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPConnectionParams,
)
from rich import print
from google.adk.tools.tool_context import ToolContext

# MODEL = "gemini-1.5-pro"
MODEL = "gemini-2.0-flash"


async def list_files(tool_context: ToolContext):
    """Tool to list available artifacts for the user."""
    available_files = await tool_context.list_artifacts()
    print("available_files :", available_files)

    if not available_files:
        return {
            "status": "error",
            "message": "You have no saved artifacts.",
            "data": available_files,
        }

    return {"status": "success", "data": available_files}


async def load_file(filename: str, tool_context: ToolContext):
    try:
        # Load the latest version
        report_artifact = await tool_context.load_artifact(filename=filename)

        if report_artifact is None or report_artifact.inline_data is None:
            return {
                "status": "error",
                "message": f"Python artifact '{filename}' not found.",
                "data": {},
            }

        print(f"Successfully loaded latest Python artifact '{filename}'.")
        print(f"MIME Type: {report_artifact.inline_data.mime_type}")
        # Process the report_artifact.inline_data.data (bytes)
        content_bytes = report_artifact.inline_data.data
        return {"status": "success", "message": "success", "data": content_bytes}

    except ValueError as e:
        return {
            "status": "error",
            "message": f"Error loading Python artifact: {e}. Is ArtifactService configured?",
            "data": {},
        }
    except Exception as e:
        # Handle potential storage errors
        return {
            "status": "error",
            "message": f"An unexpected error occurred during Python artifact load: {e}",
            "data": {},
        }


resource_manager_agent = Agent(
    model=MODEL,
    name="resource_manager_agent",
    # instruction=prompt.RESOURCE_MANAGER_PROMPT,
    description="Data Resource Manager",
    output_key="data_resource_manager_output",
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="http://127.0.0.1:8010/mcp"
            )
        ),
        FunctionTool(func=list_files),
        FunctionTool(func=load_file),
    ],
)
