"""Pydantic calculation schemas."""

from pydantic import BaseModel, Field


class CalculationCreate(BaseModel):
    """Payload for an acoustic calculation request."""

    project_id: int
    material: str = Field(..., examples=["concrete"])
    thickness_mm: float = Field(..., gt=0, examples=[120.0])


class CalculationRead(BaseModel):
    """Calculation response with normalized result data."""

    id: int
    project_id: int
    result: dict[str, float | str | list[float]]

    model_config = {"from_attributes": True}
