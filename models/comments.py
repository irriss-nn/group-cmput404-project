import uuid
from pydantic import BaseModel, Field, date
import datetime

class Comment(BaseModel):
    type: str = 'comment'
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    author: str # Author ID of the post
    post: str #ObjectId of the post
    comment: str
    contentType: str = 'text/markdown'
    published: str = datetime.datetime.now().isoformat()

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                    "type":"comment",
                        "author": "066de609-b04a-4b30-b97c-32537c7f1f6h",
                        "comment":"Sick Olde English",
                        "contentType":"text/markdown",
                        "published":"2015-03-09T13:07:04+00:00",
                        "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments/f6255bb01c648fe967714d52a89e8e9c",
            
        }