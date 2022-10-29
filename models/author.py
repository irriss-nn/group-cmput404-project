import secrets
import uuid

from dataclasses import dataclass, field
from pydantic import BaseModel, root_validator
from passlib.hash import bcrypt

@dataclass
class Author:
    displayName: str 
    github: str 
    type = "author"  # TODO: Remove
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    # TODO: Remove URLs
    url: str = "http://127.0.0.1:8000/" + str(uuid.uuid4())
    host: str = "http://127.0.0.1:8000/"
    authLevel: str = "user"  # TODO: More efficient to store bool or int
    hashedPassword: str = secrets.token_urlsafe(8)
    posts:dict|None = None
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

    @staticmethod
    def init_with_dict(data: dict):
        return Author(
                    id=data["_id"],
                    url=data["url"],
                    host=data["host"],
                    displayName=data["displayName"],
                    github=data["github"],
                    profileImage=data["profileImage"],
                    authLevel=data["authLevel"],
                    hashedPassword=data["hashedPassword"],
                    posts=data["posts"])

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
                "hashedPassword": "as#!%lls",
                "posts":{}
            }
        }
