import datetime
import uuid

from pydantic import BaseModel, Field

class Comment(BaseModel):
    type: str = "comment"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    author: str|dict = "" # Author ID of the post or returning author json
    post: str = ""#ObjectId of the post
    comment: str = ""
    contentType: str = "text/markdown"
    published: str = datetime.datetime.now().isoformat()
    likes: list = []

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                        "comment":"Sick Olde English",
            }
            }
