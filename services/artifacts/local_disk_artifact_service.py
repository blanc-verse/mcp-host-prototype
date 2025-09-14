import logging
import mimetypes
import os
from pathlib import Path
from typing import Optional
from google.genai import types
from pydantic import BaseModel
from pydantic import Field
from typing_extensions import override
from google.adk.artifacts import BaseArtifactService
from rich import print

logger = logging.getLogger("ida_clinet." + __name__)


class LocalDiskArtifactService(BaseArtifactService, BaseModel):
    """An in-memory implementation of the artifact service.

    It is not suitable for multi-threaded production environments. Use it for
    testing and development only.
    """

    artifacts: dict[str, list[types.Part]] = Field(default_factory=dict)

    base_dir: Path = Path("/Users/macbookpro/src/avian/ida_client/datasets/artifacts")

    def _file_has_user_namespace(self, filename: str) -> bool:
        """Checks if the filename has a user namespace.

        Args:
            filename: The filename to check.

        Returns:
            True if the filename has a user namespace (starts with "user:"),
            False otherwise.
        """
        return filename.startswith("user:")

    def _artifact_path(
        self, app_name: str, user_id: str, session_id: str, filename: str
    ) -> str:
        """Constructs the artifact path.

        Args:
            app_name: The name of the application.
            user_id: The ID of the user.
            session_id: The ID of the session.
            filename: The name of the artifact file.

        Returns:
            The constructed artifact path.
        """
        if self._file_has_user_namespace(filename):
            return f"{app_name}/{str(user_id)}/user/{filename}"
        return f"{app_name}/{str(user_id)}/{str(session_id)}/{filename}"

    @override
    async def save_artifact(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
        artifact: types.Part,
    ) -> int:
        path = self._artifact_path(app_name, user_id, session_id, filename)

        if artifact.inline_data is None:
            raise Exception("Could not save artifact, file corrupted")

        full_path = f"{self.base_dir}/{path}"
        os.makedirs("/".join(full_path.split("/")[:-1]), exist_ok=True)

        # For now, new artifact with same name will replace the old one
        if path not in self.artifacts:
            self.artifacts[path] = []
        version = len(self.artifacts[path])
        self.artifacts[path].append(artifact)

        with open(full_path, "wb") as f:
            f.write(artifact.inline_data.data or bytes())
            print(f"File saved successfully to: {full_path} ✅")

        return version

    @override
    async def load_artifact(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
        version: Optional[int] = None,
    ) -> Optional[types.Part]:
        path = self._artifact_path(app_name, user_id, session_id, filename)
        versions = self.artifacts.get(path)
        if not versions:
            return None
        if version is None:
            version = -1

        file_to_load = versions[version]

        return file_to_load

    @override
    async def list_artifact_keys(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> list[str]:
        session_prefix = f"{app_name}/{user_id}/{session_id}/"
        usernamespace_prefix = f"{app_name}/{user_id}/user/"
        filenames = []

        print("artifact list: ", self.artifacts)
        for path in self.artifacts:
            if path.startswith(session_prefix):
                filename = path.removeprefix(session_prefix)
                filenames.append(filename)
            elif path.startswith(usernamespace_prefix):
                filename = path.removeprefix(usernamespace_prefix)
                filenames.append(filename)

        full_session_prefix = f"{self.base_dir}/{session_prefix}"
        if os.path.exists(full_session_prefix):
            file_paths = os.listdir(full_session_prefix)
            for path in file_paths:
                if os.path.isfile(path):
                    filename = "".join(path.split("/")[:-1])
                    filenames.append(filename)

        full_usernamespace_prefix = f"{self.base_dir}/{session_prefix}"
        if os.path.exists(full_usernamespace_prefix):
            file_paths = os.listdir(full_usernamespace_prefix)
            for path in file_paths:
                if os.path.isfile(path):
                    filename = "".join(path.split("/")[:-1])
                    filenames.append(filename)

        return sorted(filenames)

    @override
    async def delete_artifact(
        self, *, app_name: str, user_id: str, session_id: str, filename: str
    ) -> None:
        path = self._artifact_path(app_name, user_id, session_id, filename)
        if not self.artifacts.get(path):
            return None
        self.artifacts.pop(path, None)

    @override
    async def list_versions(
        self, *, app_name: str, user_id: str, session_id: str, filename: str
    ) -> list[int]:
        path = self._artifact_path(app_name, user_id, session_id, filename)
        versions = self.artifacts.get(path)
        if not versions:
            return []
        return list(range(len(versions)))
