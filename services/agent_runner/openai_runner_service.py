from contextlib import AsyncExitStack
import os
from typing import List
import uuid
from agents import (
    Agent,
    CodeInterpreterTool,
    ModelSettings,
    RunConfig,
    RunHooks,
    RunResultStreaming,
    Runner,
    Session,
    TContext,
    TResponseInputItem,
)
from dotenv import load_dotenv
from internal_agents.openai.function_tools import list_artifacts, read_artifact
from services.agent_runner.agent_runner_service import AgentRunnerService
from services.content_parser.openai_content_parser import OpenAiContentParser
from services.file_storage.openai_storage_service import OpenAiStorageService
from agents.mcp import MCPServer, MCPServerStreamableHttp, MCPServerStreamableHttpParams
from agents.extensions.memory.sqlalchemy_session import SQLAlchemySession
from sqlalchemy.ext.asyncio import create_async_engine
import chainlit as cl

load_dotenv()

DEFAULT_MAX_TURNS = 10


class OpenAiRunnerService(AgentRunnerService):
    def __init__(
        self,
        user_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        file_storage_service=OpenAiStorageService(),
        content_parser=OpenAiContentParser(
            file_root_path="/Users/macbookpro/src/avian/jalin_web_host/public/artifacts"
        ),
    ) -> None:
        self.name = "intelligent_data_assistant"
        self.user_id = user_id
        self.session_id = session_id

        db_url = os.getenv("DATABASE_URL") or ""
        self.db_engine = create_async_engine(db_url)

        self.session = SQLAlchemySession(
            session_id=session_id,
            engine=self.db_engine,
            create_tables=True,  # Auto-create tables for the demo
        )

        self.file_storage_service = file_storage_service

        self.exit_stack = AsyncExitStack()
        self.mcp_servers: List[MCPServer] = []

        self.agent = Agent(name="Default Agent")

        self.content_parser = content_parser

        self.runner = Runner()

    async def run_streamed(
        self,
        message: cl.Message,
        context: TContext | None = None,
        max_turns: int = DEFAULT_MAX_TURNS,
        hooks: RunHooks[TContext] | None = None,
        run_config: RunConfig | None = None,
        previous_response_id: str | None = None,
    ) -> RunResultStreaming:
        await self.content_parser.save_attachments(message)

        # runner could only receive string input of we have session attached
        return self.runner.run_streamed(
            self.agent,
            message.content,
            context,
            max_turns,
            hooks,
            run_config,
            previous_response_id,
            self.session,
        )

    async def build_finance_agent(self):

        server = await self.exit_stack.enter_async_context(
            MCPServerStreamableHttp(
                name="Finance Database",
                params=MCPServerStreamableHttpParams(url="http://127.0.0.1:8010/mcp"),
            )
        )

        await server.connect()

        self.mcp_servers = [server]

        # TODO: add tools to read artifact (so model could get access to previous uplaoded files)
        self.agent = Agent(
            model="gpt-5",
            name="Orchestrator Agent",
            model_settings=ModelSettings(tool_choice="required"),
            instructions=(
                "You are 'Blanc', a highly experienced and respected senior data consultant from Indonesia."
                "Your persona is defined by wisdom, humility, and a calm, guiding demeanor."
                "You always speak in formal and polite Bahasa Indonesia."
                "You see the user as a junior colleague or a student ('Anda' or 'Kamu') whom you are mentoring."
                "Your goal is not just to give answers, but to guide them through the data to find insights together."
                "Your core objective is to act as a wise data analyst and consultant, providing insightful advice by interpreting data and guiding the user toward making well-informed decisions."
                "The user is often a non-tech person, you should start with most user friendly answer before user asking technical question"
            ),
            mcp_servers=self.mcp_servers,
            tools=[
                CodeInterpreterTool(
                    tool_config={
                        "type": "code_interpreter",
                        "container": {"type": "auto"},
                    }
                ),
                list_artifacts,
                read_artifact,
            ],
        )
