import base64
from agents import (
    RawResponsesStreamEvent,
    TResponseInputItem,
)
import agents
from dotenv import load_dotenv
from typing_extensions import override
import chainlit as cl
import google.genai.types as types
import pandas as pd
from prebuilt_agents.utils import EXCEL_MIMES
from services.file_storage.openai_storage_service import OpenAiStorageService
from .content_parser import ContentParser
from openai.types.responses import (
    ResponseTextDeltaEvent,
    ResponseCreatedEvent,
    ResponseOutputItemAddedEvent,
    ResponseCodeInterpreterCallCodeDeltaEvent,
    ResponseOutputTextAnnotationAddedEvent,
    ResponseTextDoneEvent,
    ResponseContentPartAddedEvent,
    ResponseOutputItemDoneEvent,
    ResponseCodeInterpreterCallCompletedEvent,
    ResponseInProgressEvent,
    ResponseCompletedEvent,
    ResponseOutputItemDoneEvent,
    ResponseContentPartDoneEvent,
    EasyInputMessageParam,
    ResponseInputImageParam,
    ResponseInputMessageContentListParam,
    ResponseInputImage,
    EasyInputMessage,
    ResponseInputTextParam,
    ResponseInputFileParam,
)
from rich import print

load_dotenv()


class OpenAiContentParser(ContentParser):
    @override
    async def from_chainlit(
        self,
        message: cl.Message,
    ) -> list[TResponseInputItem]:
        content: ResponseInputMessageContentListParam = []
        for element in message.elements:
            if element.type == "file" and element.mime in EXCEL_MIMES:
                continue

            if element.type == "file" and element.mime == "text/csv":
                df = pd.read_csv(str(element.path))

                content.append(
                    ResponseInputTextParam(
                        type="input_text",
                        text=df.to_csv(),
                    ),
                )

            # Another types of files goes here

        # User message appended as the last item of content
        content.append(
            ResponseInputTextParam(text=message.content, type="input_text"),
        )

        return [
            EasyInputMessageParam(
                content=content,
                role="user",
                type="message",
            ),
        ]

    @override
    async def to_chainlit(
        self,
        message: cl.Message,
        file_storage_service: OpenAiStorageService,
        event: RawResponsesStreamEvent,
    ):
        if isinstance(event.data, ResponseTextDeltaEvent):
            await message.stream_token(event.data.delta)
            return

        # Pass since already handled on ResponseTextDeltaEvent
        if isinstance(event.data, ResponseTextDoneEvent):
            return

        # Pass since already handled on ResponseTextDeltaEvent
        if isinstance(event.data, ResponseCreatedEvent):
            return

        # Pass since already handled on ResponseTextDeltaEvent
        if isinstance(event.data, ResponseOutputItemDoneEvent):
            return

        # I dont think user need to know ResponseOutputItemAddedEvent
        if isinstance(event.data, ResponseOutputItemAddedEvent):
            return

        # I dont think user need to know ResponseContentPartAddedEvent
        if isinstance(event.data, ResponseContentPartAddedEvent):
            return

        # Belum nemu cara streaming content code, lets just skip it for now
        if isinstance(event.data, ResponseCodeInterpreterCallCodeDeltaEvent):
            return

        # Not sure how to dislay this event yet
        if isinstance(event.data, ResponseCodeInterpreterCallCompletedEvent):
            return

        # Not sure how to dislay this event yet
        if isinstance(event.data, ResponseInProgressEvent):
            return

        # Not sure how to dislay this event yet
        if isinstance(event.data, ResponseCompletedEvent):
            return

        # Not sure how to dislay this event yet
        if isinstance(event.data, ResponseOutputItemDoneEvent):
            return

        # Not sure how to dislay this event yet
        if isinstance(event.data, ResponseContentPartDoneEvent):
            return

        if isinstance(event.data, ResponseOutputTextAnnotationAddedEvent):
            annotation = event.data.annotation
            if isinstance(annotation, dict):
                # {
                #     'type': 'container_file_citation',
                #     'container_id': 'cntr_68c252437a8c81908b96c178968d9272032a8d1695410078',
                #     'end_index': 290,
                #     'file_id': 'cfile_68c2543d78c88191b4763f375ba2077d',
                #     'filename': 'transaction_amount_histogram.png',
                #     'start_index': 240
                # }
                print("annotation - Container ID: ", annotation["container_id"])
                print("annotation - Annotation ID: ", annotation["file_id"])

                file_content = file_storage_service.get_file(
                    annotation["container_id"], annotation["file_id"]
                )

                with open(
                    f"/Users/macbookpro/src/avian/ida_client/public/artifacts/{annotation['filename']}",
                    mode="bw",
                ) as writer:
                    writer.write(file_content)

                if str(annotation["filename"]).endswith(("png", "jpg", "jpeg")):
                    image = cl.Image(
                        content=file_content,
                        name=annotation["filename"],
                        display="inline",
                    )
                    message.elements.append(image)  # type: ignore
                else:
                    file = cl.File(
                        content=file_content,
                        name=annotation["filename"],
                        display="inline",
                    )
                    message.elements.append(file)  # type: ignore

                return

        print("raw_response_event", type(event.data), event.data)
