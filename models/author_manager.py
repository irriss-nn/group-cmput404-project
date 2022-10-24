import uuid
from pydantic import BaseModel, Field


class AuthorManager(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    owner: str
    followers: list = []
    following: list = []
    posts: list = []
    inbox: list = []
    requests: list = []

    class Config:
        schema_extra = {
            "example": {
                "owner": "066de609-b04a-4b30-b97c-32537c7f1f6h"
            }
        }
