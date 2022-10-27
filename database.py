from dataclasses import asdict
from pymongo import MongoClient

from models.author import Author
from models.post import Post

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

    def add_author(self, data):
        pass

    def get_author(self, author_id: str) -> Author|None:
        data = self.database.authors.find_one({"_id": author_id})
        if data is None:
            return None

        return Author.init_with_dict(data)

    def get_authors(self, limit: int = 0) -> list[Author]:
        return []

    def get_post(self, author_id: str, post_id: str) -> Post|None:
        author = self.get_author(author_id)
        if author and post_id in author.posts.keys():
            return Post.init_with_dict(author.posts[post_id])

        return None

    def get_posts(self, author_id: str, limit: int = 0) -> list[Post]|None:
        author = self.get_author(author_id)
        if not author:
            return None

        return [Post.init_with_dict(post) for post in author.posts.values()]

    def create_post(self, author_id: str, post: Post) -> bool:
        author = self.get_author(author_id)
        if not author or post._id in author.posts.keys():
            return False

        author.posts[post._id] = post
        posts = asdict(author)["posts"]
        result = self.database.authors.update_one({"_id": author_id},
                                                  {"$set": {"posts": posts}})
        return result.acknowledged
