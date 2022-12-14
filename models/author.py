import secrets
import uuid

from dataclasses import asdict, dataclass, field
from pydantic import root_validator

from models.base import Base
#from models.post import Post

@dataclass
class Author(Base):
    displayName: str
    github: str
    id: str = str(uuid.uuid4())
    # TODO: Remove hardcoded URLs
    url: str = "http://127.0.0.1:8000/" + str(uuid.uuid4())
    host: str = "http://127.0.0.1:8000/"
    authLevel: str = "user"  # TODO: More efficient to store bool or int
    hashedPassword: str = secrets.token_urlsafe(8)
    profileImage: str = "https://www.pngitem.com/pimgs/m/22-223968_default-profile-picture-circle-hd-png-download.png"

    @root_validator
    def compute_url(cls, values) -> dict:
        new_url = values["host"] + "authors/"+ values["id"]
        if values["url"]:
            values["url"] = new_url
        # This basically makes it so the password is still hashed even if it is randomly generated
        # if(values["hashedPassword"] is not None): Not hashing right now for simplicity
        #     values["hashedPassword"] = bcrypt.hash(values["hashedPassword"])

        return values

    def json(self) -> dict:
        data = asdict(self)
        data["type"] = "author"
        del data['authLevel']
        del data['hashedPassword']

        return data

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "066de609-b04a-4b30-b97c-32537c7f1f6h",
                "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "host":"http://127.0.0.1:8000/",
                "displayName":"Lara Croft",
                "github": "http://github.com/laracroft",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg",
                "hashedPassword": "as#!%lls"
            }
        }

@dataclass
class AuthorManager(Base):
    id: str
    followers: list = field(default_factory=list)
    following: list = field(default_factory=list)
    posts: dict = field(default_factory=dict)
    inbox: list = field(default_factory=list)
    requests: list = field(default_factory=list)

    @classmethod
    def init_from_mongo(cls, data: dict):
        # TODO: Recursively replace id of children
        data["id"] = data["_id"]
        del data["_id"]
        return cls.init_with_dict(data)

    class Config:
        schema_extra = {
            "example": {
                "id": "066de609-b04a-4b30-b97c-32537c7f1f6h"
            }
        }
