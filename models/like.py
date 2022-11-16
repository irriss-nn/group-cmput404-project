import uuid
from pydantic import BaseModel, Field
import datetime

class Like(BaseModel):
    context: str = "https://www.w3.org/ns/activitystreams" # change this
    type: str = "Like"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    author: dict # person who liked comment
    object: str # id of the post or comment, aka target of like

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                        "author":{"name": "Billy joel",
                                  "id": "283218319873918"
                                  },  
                        object: "posts/12321331231232333"
            }
            }