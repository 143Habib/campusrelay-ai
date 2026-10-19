"""Strict request schemas: reject unknown JSON fields and invalid values."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

Category = Literal["Facilities", "IT", "Safety", "Academic", "Transport"]
Priority = Literal["Low", "Medium", "High"]
Status = Literal["Open", "In Progress", "Resolved", "Reopened"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Login(StrictModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class Register(StrictModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=10, max_length=128)

    @field_validator("password")
    @classmethod
    def strong_password(cls, value):
        if not any(c.isupper() for c in value) or not any(c.islower() for c in value) or not any(c.isdigit() for c in value):
            raise ValueError("Use uppercase, lowercase and numeric characters in your password.")
        return value


class TicketCreate(StrictModel):
    title: str = Field(min_length=8, max_length=120)
    description: str = Field(min_length=20, max_length=2000)
    location: str = Field(min_length=3, max_length=120)
    category: Category
    priority: Priority


class TicketUpdate(StrictModel):
    status: Status
    note: str = Field(default="", max_length=500)


class TicketAssign(StrictModel):
    assignee_id: int | None = Field(default=None, ge=1)


class Comment(StrictModel):
    note: str = Field(min_length=2, max_length=500)


class Suggest(StrictModel):
    text: str = Field(min_length=20, max_length=2200)
