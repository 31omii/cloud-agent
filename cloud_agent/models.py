from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SessionRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    repository: str = Field(pattern=r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", max_length=200)
    task: str = Field(min_length=1, max_length=4000)


class Session(SessionRequest):
    id: UUID
    status: Literal["queued"] = "queued"
