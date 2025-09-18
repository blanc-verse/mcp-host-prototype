import os
from dotenv import load_dotenv
import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from rich import print
from services.agent_runner.openai_runner_service import OpenAiRunnerService
from services.application.local_disk_storage_provider import LocalDiskStorageProvider
from services.content_parser.openai_content_parser import OpenAiContentParser
from services.file_storage.openai_storage_service import OpenAiStorageService


load_dotenv()


@cl.data_layer
def get_data_layer():
    db_connection_string = os.getenv("DATABASE_URL") or ""

    print(db_connection_string)

    return SQLAlchemyDataLayer(
        conninfo=db_connection_string,
        storage_provider=LocalDiskStorageProvider(),
    )


@cl.on_chat_start
async def on_chat_start():
    global runner
    runner = OpenAiRunnerService(
        file_storage_service=OpenAiStorageService(),
    )
    await runner.build_finance_agent()

    global content_parser
    content_parser = OpenAiContentParser()


@cl.password_auth_callback
async def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(
            display_name="SUper User",
            identifier="admin",
            metadata={
                "role": "admin",
                "provider": "credentials",
            },
        )
    else:
        return None


@cl.on_message
async def on_message(message: cl.Message):
    # Send a response back to the user
    # input = await content_parser.from_chainlit(message)

    items = await content_parser.from_chainlit(message)

    result = runner.runner.run_streamed(
        starting_agent=runner.agent,
        # input=message.content,
        input=items,
        # session=runner.session,
    )

    print("=== Run starting ===")
    message = cl.Message(content="", elements=[])
    async for event in result.stream_events():
        # We'll ignore the raw responses event deltas
        if event.type == "raw_response_event":
            await content_parser.to_chainlit(
                message,
                file_storage_service=runner.file_storage_service,
                event=event,
            )

        # When the agent updates, print that
        elif event.type == "agent_updated_stream_event":
            print(f"Agent updated: {event.new_agent.name}")
            continue

    print("=== Run complete ===")
    await message.send()
