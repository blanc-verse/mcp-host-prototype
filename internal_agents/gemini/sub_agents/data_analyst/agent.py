from google.adk.code_executors import BuiltInCodeExecutor
from google.adk import Agent
# from . import prompt

MODEL = "gemini-2.0-flash"

data_analyst_agent = Agent(
    model=MODEL,
    name="data_analyst_agent",
    description="Data Analyst Expertise",
    # instruction=prompt.DATA_ANALYST_PROMPT,
    output_key="data_analyst_output",
    code_executor=BuiltInCodeExecutor(),
)
