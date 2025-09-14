from google.adk.agents import Agent
from google.adk.tools import AgentTool
from . import prompt
from .sub_agents.data_analyst import data_analyst_agent
from .sub_agents.resource_manager import resource_manager_agent
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
)
from mcp import StdioServerParameters

MODEL = "gemini-2.0-flash"


financial_coordinator = Agent(
    name="financial_coordinator",
    model=MODEL,
    description=(
        "guide users through a structured process to receive financial "
        "advice by orchestrating a series of expert subagents. help them "
        "analyze a trend, visualize data, "
        "and evaluate the overall."
    ),
    instruction=prompt.FINANCIAL_COORDINATOR_PROMPT,
    output_key="financial_coordinator_output",
    tools=[
        AgentTool(agent=data_analyst_agent),
        AgentTool(agent=resource_manager_agent),
    ],
)

root_agent = financial_coordinator
