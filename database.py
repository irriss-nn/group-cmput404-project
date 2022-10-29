from dataclasses import asdict
from pymongo import MongoClient

from models.author import Author, AuthorManager
from models.post import Post

def mongo_encode_dataclass(dataclass) -> dict:
    dataclass = asdict(dataclass)
    dataclass["_id"] = dataclass["id"]
    del dataclass["id"]

    return dataclass

class SocialDatabase:
    __slots__ = ['__mongo_client', 'db_name', 'database']
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

    def create_author(self, author: Author) -> bool:
        # Check not needed if insert_one does not overwrite data
        if self.get_author(author.id):
            return False

        data = mongo_encode_dataclass(author)
        result = self.database.authors.insert_one(data)
        if result.acknowledged:
            manager = mongo_encode_dataclass(AuthorManager(id=author.id))
            self.database.authorManagers.insert_one(manager)

        return result.acknowledged

    def update_author(self, author: Author) -> bool:
        data = mongo_encode_dataclass(author)
        result = self.database.authors.update_one({"_id": author.id},
                                                 {"$set": data})
        return result.acknowledged

    def delete_author(self, author_id: str) -> bool:
        result = self.database.authors.delete_one({"_id": author_id})
        if result.acknowledged:
            self.database.authorManagers.delete_one({"_id": author_id})

        return result.acknowledged

    def get_author(self, author_id: str) -> Author|None:
        author = self.database.authors.find_one({"_id": author_id})
        if author is None:
            return None

        return Author.init_with_dict(author)

    def get_author_manager(self, author_id: str) -> AuthorManager|None:
        manager = self.database.authorManagers.find_one({"_id": author_id})
        if not manager:
            return None

        return AuthorManager.init_with_dict(manager)

    def get_authors(self, limit: int = 0) -> list[Author]:
        return []

    def get_post(self, author_id: str, post_id: str) -> Post|None:
        manager = self.get_author_manager(author_id)
        if manager and post_id in manager.posts.keys():
            return Post.init_with_dict(manager.posts[post_id])

        return None

    def get_posts(self, author_id: str, limit: int = 0) -> list[Post]|None:
        manager = self.get_author_manager(author_id)
        if not manager:
            return None

        return asdict(manager)["posts"]

    def create_post(self, author_id: str, post: Post) -> bool:
        manager = self.get_author_manager(author_id)
        if not manager or post.id in manager.posts.keys():
            return False

        manager.posts[post.id] = post
        posts = asdict(manager)["posts"]
        result = self.database.authorManagers.update_one({"_id": author_id},
                                                  {"$set": {"posts": posts}})
        return result.acknowledged
