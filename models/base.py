from dataclasses import asdict, dataclass, fields

@dataclass
class Base:
    @classmethod
    def init_with_dict(cls, data: dict):
        class_fields = {field.name for field in fields(cls) if field.init}
        if not class_fields:
            return cls()

        init_args = {key: value for key, value in data.items() if key in class_fields}
        return cls(**init_args)

    @classmethod
    def init_from_mongo(cls, data: dict):
        data["id"] = data["_id"]
        del data["_id"]
        return cls.init_with_dict(data)

    def encode_for_mongo(self) -> dict:
        data = asdict(self)
        data["_id"] = data["id"]
        del data["id"]

        return data

    def json(self) -> dict:
        '''Return a JSON representation of the object'''
        return asdict(self)
