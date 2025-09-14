# pip install openai-agents python-dotenv
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Callable
import os, threading, asyncio

from dotenv import load_dotenv
from agents import Agent, Runner, SQLiteSession, RunConfig
from agents.mcp.server import (
    MCPServerStreamableHttp,
)  # <-- Streamable HTTP (your server)

# If your server were SSE, you'd use: from agents.mcp.server import MCPServerSse

load_dotenv()
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"  # silence noisy tracing 400s


@dataclass
class ChatTurn:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class OpenAIChat:
    server_url: str
    model: str = "gpt-5"
    history: List[ChatTurn] = field(default_factory=list)

    # --- internal: background loop management ---
    _loop: Optional[asyncio.AbstractEventLoop] = field(init=False, default=None)
    _thread: Optional[threading.Thread] = field(init=False, default=None)

    def __post_init__(self):
        # 1) Spin up a persistent event loop in a background thread
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

        # 2) Build the MCP server (Streamable HTTP)
        self.mcp_server = MCPServerStreamableHttp(
            params={"url": self.server_url},  # e.g. "http://127.0.0.1:8010/mcp"
            name="ax2012",
            cache_tools_list=True,
        )

        # 3) Connect on the SAME loop/thread
        self._await(self.mcp_server.connect())

        # (Optional) Preflight: list tools once so we know we're good
        try:
            tools = self._await(self.mcp_server.list_tools())
            print("MCP tools:", [t.name for t in tools])
        except Exception as e:
            print(f"[warn] tools/list failed: {e}")

        # 4) Build Agent + Session
        self.agent = Agent(
            name="Assistant",
            instructions="",
            model=self.model,
            mcp_servers=[self.mcp_server],
        )
        self.session = SQLiteSession("default")
        self.run_config = RunConfig(tracing_disabled=True)

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _await(self, coro):
        """Run an async coroutine on the background loop and wait for the result."""
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result()

    def add(self, role: str, content: str) -> None:
        self.history.append(ChatTurn(role=role, content=content))
        if role == "system":
            self.agent.instructions = content

    def _last_user_input(self) -> str:
        return self.history[-1].content if self.history else ""

    def ask(self, prompt: str) -> str:
        self.add("user", prompt)
        result = Runner.run_sync(
            self.agent,
            input=self._last_user_input(),
            session=self.session,
            run_config=self.run_config,
        )
        text = result.final_output or ""
        self.add("assistant", text)
        return text

    def close(self):
        # Clean up in the SAME loop/thread, then stop the loop
        try:
            if self.mcp_server:
                self._await(self.mcp_server.cleanup())
        finally:
            if self._loop and self._loop.is_running():
                self._loop.call_soon_threadsafe(self._loop.stop)
            if self._thread:
                self._thread.join(timeout=2)

    def repl(self) -> None:
        print(f"Connected to MCP (Streamable HTTP): {self.server_url}")
        print("Connected. Type 'quit' to exit.")
        try:
            while True:
                q = input("\nYou: ").strip()
                if q.lower() in {"quit", "exit"}:
                    break
                print("Assistant: ", end="", flush=True)
                print(self.ask(q))
        finally:
            self.close()


# ----------------------------- usage -----------------------------
if __name__ == "__main__":
    chat = OpenAIChat(
        model="gpt-5",
        server_url="http://127.0.0.1:8010/mcp",  # your Streamable HTTP endpoint
    )
    chat.add("system", "You are helpful and use weather MCP tools when relevant.")
    chat.repl()
