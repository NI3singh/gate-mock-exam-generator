from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class RegisterRequest(BaseModel):
    display_name: Optional[str] = None
    preferred_paper: Optional[str] = None

    @field_validator("preferred_paper")
    @classmethod
    def validate_paper(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("CS", "DA"):
            raise ValueError("preferred_paper must be 'CS' or 'DA'")
        return v


class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    preferred_paper: Optional[str] = None

    @field_validator("preferred_paper")
    @classmethod
    def validate_paper(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("CS", "DA"):
            raise ValueError("preferred_paper must be 'CS' or 'DA'")
        return v


class UserResponse(BaseModel):
    id: UUID
    firebase_uid: str
    email: str
    display_name: Optional[str] = None
    preferred_paper: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)