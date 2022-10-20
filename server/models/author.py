import uuid
from typing import Optional
from pydantic import BaseModel, Field


class Author(BaseModel):
    id: str 
    url: str 
    host:str 
    displayName: str 
    github: str 
    profileImage: str 

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "066de609-b04a-4b30-b97c-32537c7f1f6h",
                "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "host":"http://127.0.0.1:8000/",
                "displayName":"Lara Croft",
                "github": "http://github.com/laracroft",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
            }
        }
        