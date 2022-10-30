from dataclasses import dataclass, fields

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
