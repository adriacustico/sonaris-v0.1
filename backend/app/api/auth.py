"""Authentication endpoints.

Example:
    POST /auth/login with an email/password payload once auth is implemented.
"""

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class LoginRequest(BaseModel):
    """Basic login payload placeholder."""

    email: str
    password: str


@router.post("/login")
def login(payload: LoginRequest) -> dict[str, str]:
    """Return a placeholder token response for early frontend integration."""
    return {"access_token": "development-token", "token_type": "bearer"}
