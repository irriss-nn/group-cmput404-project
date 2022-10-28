from pymongo import MongoClient

from models.author import Author


class SocialDatabase:
    singleton = None

    def __init__(self, host: str = "localhost", port: int = 27017) -> None:
        self.__mongo_client = MongoClient(host, port)
        self.db_name = "socialnetwork"
        self.database = self.__mongo_client[self.db_name]

    def __new__(cls, *args, **kwargs):
        if cls.singleton is None:
            cls.singleton = super().__new__(cls)

        return cls.singleton

    def __del__(self):
        return self.__mongo_client.close()

    def close(self):
        return self.__del__();

    def add_author(self, data):
        pass

    def get_author(self, author_id: str) -> Author|None:
        data = self.database["authors"].find_one({"_id": author_id})
        if data is None:
            return None

        return Author.init_with_dict(data)

    def get_authors(self, limit: int) -> list:
        pass
