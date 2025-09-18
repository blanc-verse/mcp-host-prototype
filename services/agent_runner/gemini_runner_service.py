import uuid
from internal_agents.gemini import agent
from services.artifacts.local_disk_artifact_service import LocalDiskArtifactService
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner


class GeminiRunnerService:
    def __init__(self) -> None:
        self.artifact_service = LocalDiskArtifactService()

        app_name = "intelligent_data_assistant"
        self.user_id = str(uuid.uuid4())

        self.session_service = InMemorySessionService()
        self.session = self.session_service.create_session_sync(
            app_name=app_name, user_id=self.user_id
        )
        self.runner = Runner(
            app_name=app_name,
            agent=agent.data_analyst_agent,
            session_service=self.session_service,
            artifact_service=self.artifact_service,
        )
