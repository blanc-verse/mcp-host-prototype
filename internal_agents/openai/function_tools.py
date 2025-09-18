import os
from typing import List
from agents import function_tool
import pandas as pd

ARTIFACT_ROOT_PATH = "/Users/macbookpro/src/avian/jalin_web_host/public/artifacts"


@function_tool
async def list_artifacts() -> List[str]:
    paths = []

    for root, dirs, files in os.walk(ARTIFACT_ROOT_PATH):
        print(f"Current Directory: {root}")
        print(f"Subdirectories: {dirs}")
        print(f"Files: {files}")
        for file in files:
            paths.append(f"{root}/{file}")

    return paths


@function_tool
async def read_artifact(file_path: str) -> str:
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
        json_string = df.to_json()
        return json_string

    return ""
