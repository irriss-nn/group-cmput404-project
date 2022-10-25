import uuid
from pydantic import BaseModel, Field
import datetime

class Comment(BaseModel):
    type: str = "comment"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    author: str = "" # Author ID of the post
    post: str = ""#ObjectId of the post
    comment: str = ""
    contentType: str = "text/markdown"
    published: str = datetime.datetime.now().isoformat()

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                        "comment":"Sick Olde English",  
            }
            }