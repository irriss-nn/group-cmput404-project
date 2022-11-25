from dataclasses import asdict
from pymongo import ASCENDING, MongoClient
from fastapi.encoders import jsonable_encoder
from models.author import Author, AuthorManager
from models.post import Post
from models.like import Like
from models.inbox import InboxItem
from pprint import pprint


def mongo_encode_dataclass(dataclass) -> dict:
    dataclass = asdict(dataclass)
    dataclass["_id"] = dataclass["id"]
    del dataclass["id"]

    return dataclass


class SocialDatabase:
    __slots__ = ['__mongo_client', 'db_name', 'database', 'host']
    _instance = None

    def __new__(cls, host: str = "localhost", port: int = 27017):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.__mongo_client = MongoClient(host, port)
            cls.db_name = "socialnetwork"
            cls.database = cls.__mongo_client[cls.db_name]
            cls.host = host

        return cls._instance

    def __del__(self):
        return self.__mongo_client.close()

    def close(self):
        return self.__del__()

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

    def get_author(self, author_id: str) -> Author | None:
        author = self.database.authors.find_one({"_id": author_id})
        if author is None:
            return None

        return Author.init_from_mongo(author)

    def get_author_byname(self, author_name: str) -> Author | None:
        author = self.database.authors.find_one({"displayName": author_name})
        if author is None:
            return None

        return Author.init_from_mongo(author)

    def get_authors(self, offset: int = 0, limit: int = 0) -> list[Author]:
        return [Author.init_from_mongo(author) for author in
                self.database.authors.find(skip=offset, limit=limit,
                                           sort=[("_id", ASCENDING)])]

    def get_author_manager(self, author_id: str) -> AuthorManager | None:
        manager = self.database.authorManagers.find_one({"_id": author_id})
        if not manager:
            return None

        return AuthorManager.init_from_mongo(manager)

    def get_inbox(self, author_id: str) -> list[Post] | None:
        manager = self.get_author_manager(author_id)
        if not manager:
            return None

        return asdict(manager)["inbox"]

    def get_post(self, author_id: str, post_id: str) -> Post | None:
        manager = self.get_author_manager(author_id)
        if manager and post_id in manager.posts:
            return Post.init_from_mongo(manager.posts[post_id])

        return None

    def get_posts(self, author_id: str, limit: int = 0) -> list[Post] | None:
        manager = self.get_author_manager(author_id)
        if not manager:
            return None

        return asdict(manager)["posts"]

    def get_post_by_id(self, post_id: str) -> Post | None:
        authorsManagers = self.database["authorManagers"].find()
        # iterate through all iauthor managers and find the post
        for authorManager in authorsManagers:
            if authorManager and post_id in authorManager["posts"].keys():
                return authorManager["posts"][post_id]
        return None

    def get_comment_by_id(self, comment_id: str) -> dict | None:
        comment = self.database["comments"].find_one({"_id": comment_id})
        if comment:
            return comment
        return None

    def create_post(self, author_id: str, post: Post) -> bool:
        manager = self.get_author_manager(author_id)
        if not manager or post.id in manager.posts.keys():
            return False

        result = self.database.authorManagers.update_one({"_id": author_id},
                                                         {"$set": {f"posts.{post.id}": mongo_encode_dataclass(post)}})
        return result.acknowledged

    def update_post(self, author_id: str, post_id: str, post: Post) -> bool:
        manager = self.get_author_manager(author_id)
        if not (manager and post_id in manager.posts.keys()):
            return False

        result = self.database.authorManagers.update_one({"_id": author_id},
                                                         {"$set": {f"posts.{post.id}": mongo_encode_dataclass(post)}})
        return result.acknowledged

    def like_post(self,  post_id: str, like_author: str) -> bool:
        author = jsonable_encoder(self.get_author(like_author))
        if author is None:
            return False
        like_obj = Like(author=author, object=post_id)
        post = self.get_post_by_id(post_id)
        like_obj = jsonable_encoder(like_obj)
        if not post:
            return False
        # Check if already liked
        if "likes" in post:
            for likes in post["likes"]:
                if likes["author"]["id"] == like_author:
                    print("Already liked")
                    return False
        postid = post["_id"]
        # update the post with the new like
        result = self.database.authorManagers.update_one({"_id": post["author"]["id"]},
                                                         {"$push": {f"posts.{postid}.likes": like_obj}})
        if result.acknowledged == True:
            res = self.create_inbox_like_notification(
                post["author"]["id"], "post", like_obj)
        return True

    def like_comment(self, comment_id: str, like_author: str) -> bool:
        author = jsonable_encoder(self.get_author(like_author))
        if author is None:
            return False
        like_obj = Like(author=author, object=comment_id)
        comment = self.get_comment_by_id(comment_id)
        like_obj = jsonable_encoder(like_obj)
        if not comment:
            return False
        # Check if already liked
        if "likes" in comment:
            for like in comment["likes"]:
                if like["author"]["id"] == like_author:
                    return False
        # update the comment with the new like
        result = self.database["comments"].update_one({"_id": comment_id},
                                                      {"$push": {"likes": like_obj}})
        # Make inbox notification
        if result.acknowledged == True:
            res = self.create_inbox_like_notification(
                comment["author"], "comment", like_obj)

        return True

    def create_inbox_like_notification(self, target_author_id: str, typeLike: str, likeObj: Like) -> bool:
        inbox_item = InboxItem(
            action=f"Like Notification",
            actionDescription="{} liked your {}".format(
                likeObj["author"]["displayName"], typeLike),
            actionReference=likeObj["object"],
        )
        inbox_item = jsonable_encoder(inbox_item)
        result = self.database.authorManagers.update_one({"_id": target_author_id},
                                                         {"$push": {"inbox": inbox_item}})
        return result.acknowledged

    def create_generic_like_notification(self, author_id: str) -> bool:
        inbox_item = InboxItem(
            action=f"Like Notification",
            actionDescription="You have recieved a like",
            actionReference="Anonymous",
        )
        inbox_item = jsonable_encoder(inbox_item)
        result = self.database.authorManagers.update_one({"_id": author_id},
                                                         {"$push": {"inbox": inbox_item}})
        return result.acknowledged

    def get_likes_for_post(self, post_id: str, author_id: str) -> list[Like] | None:
        post = self.get_post_by_id(post_id)

        if not post:
            return []
        if "likes" not in post:
            return []
        likes = []
        for like in post["likes"]:
            if like["author"]["id"] != author_id:
                likes.append(like)
        return likes

    def get_likes_on_comment_on_post(self, post_id: str, comment_id: str, author_id: str) -> list[Like] | None:
        comment = self.get_comment_by_id(comment_id)

        if not comment:
            return []
        if "likes" not in comment:
            return []
        likes = []
        for likes in comment["likes"]:
            if likes["author"]["id"] != author_id:
                likes.append(likes)
        return likes

    def delete_post(self, author_id: str, post_id: str) -> bool:
        manager = self.get_author_manager(author_id)
        if not (manager and post_id in manager.posts.keys()):
            return False

        result = self.database.authorManagers.update_one({"_id": author_id},
                                                         {"$unset": {f"posts.{post_id}": ""}})
        return result.acknowledged

    def get_profile(self, author_id: str) -> dict | None:
        found_user = self.database["authors"].find_one({"_id": author_id})
        found_posts = self.database["authorManagers"].find_one({"_id": author_id})[
            "posts"]
        found_user["posts"] = found_posts
        if not found_user:
            return None
        return found_user

    def is_following(self, author_id: str, target_author_id: str) -> bool:
        manager = self.get_author_manager(author_id)
        if not manager:
            return False
        return target_author_id in manager.following

    def get_following_feed(self, author_id: str, limit: int = 0) -> list[Post] | None:
        manager = self.get_author_manager(author_id)
        if not manager:
            return None
        allCurrentFollowing = manager.following

        postsToReturn = []
        for following in allCurrentFollowing:
            # Get post of each following
            found_following = self.get_author_manager(following)
            followed_author = self.get_author(following)
            try:
                for post in found_following.posts:
                    found_following.posts[post]["displayName"] = followed_author.displayName
                    postsToReturn.append(found_following.posts[post])
            except:
                pass
        # Sort posts by recent
        postsToReturn = sorted(
            postsToReturn, key=lambda d: d['published'], reverse=True)
        return postsToReturn
