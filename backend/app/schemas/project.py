"""Pydantic project schemas."""

from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Shared project fields."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class ProjectCreate(ProjectBase):
    """Payload used to create a project."""


class ProjectRead(ProjectBase):
    """Project response returned by the API."""

    id: int

    model_config = {"from_attributes": True}
