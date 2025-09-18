from typing_extensions import override
import chainlit as cl
import google.genai.types as types
import pandas as pd
from internal_agents.utils import EXCEL_MIMES
from google.adk.artifacts.base_artifact_service import BaseArtifactService
from google.adk.sessions import Session as GeminiSession
from .content_parser import ContentParser


class GeminiContentParser(ContentParser):
    @override
    async def from_chainlit(
        self,
        message: cl.Message,
        artifact_service: BaseArtifactService | None,
        session: GeminiSession,
    ) -> types.Content:
        content = types.Content(parts=[], role="user")
        parts = []
        for element in message.elements:
            if element.type == "file" and element.mime in EXCEL_MIMES:
                continue

            if element.type == "file" and element.mime == "text/csv":
                df = pd.read_csv(str(element.path))
                data_bytes = bytes(df.to_string().encode())
                file_name = element.name

                # This part will only passes to artifact, not content
                part = types.Part.from_bytes(data=data_bytes, mime_type="text/csv")

                if artifact_service:
                    await artifact_service.save_artifact(
                        app_name=session.app_name,
                        artifact=part,
                        filename=file_name,
                        session_id=session.id,
                        user_id=session.user_id,
                    )

                    # File will not inlcuded in content
                    parts.append(
                        types.Part(
                            text=f"Uploaded file: {file_name}. It is saved into artifacts"
                        )
                    )
                    continue

            # Another types of files goes here

        parts.append(types.Part.from_text(text=message.content))

        content.parts = parts
        return content

    @override
    def to_chainlit(self, gemini_content: types.Content) -> cl.Message:
        if gemini_content.parts is None:
            return cl.Message(content="No response from the model.")

        text = ""
        elements = []
        for part in gemini_content.parts:
            if part.text:
                text += part.text + "\n"
            if (
                part.file_data
                and part.file_data.display_name is not None
                and part.file_data.display_name.endswith((".jpg", ".jpeg", ".png"))
            ):
                elements.append(
                    cl.Image(
                        path=part.file_data.file_uri, name=part.file_data.display_name
                    )
                )

            if (
                part.code_execution_result
                and part.code_execution_result.outcome == types.Outcome.OUTCOME_OK
            ):
                elements.append(part.code_execution_result.output)

            if part.inline_data:
                elements.append(
                    cl.Image(
                        name=str(part.inline_data.display_name),
                        display="inline",
                        content=part.inline_data.data,
                    )
                )

        return cl.Message(content=text.strip(), elements=elements)
