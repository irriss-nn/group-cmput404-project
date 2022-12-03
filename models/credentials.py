from dataclasses import asdict, dataclass

from models.base import Base

@dataclass
class Credentials(Base):
    host: str  # Url-safe base64-encoded host name
    username: str
    password: str

    @classmethod
    def init_from_mongo(cls, data: dict):
        data["host"] = data["_id"]
        del data["_id"]
        return cls.init_with_dict(data)

    def encode_for_mongo(self) -> dict:
        data = asdict(self)
        data["_id"] = data["host"]
        del data["host"]

        return data

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "host":"http://127.0.0.1/",
                "username": "admin",
                "password": "admin",
            }
        }
