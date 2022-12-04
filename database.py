from dataclasses import asdict
from pymongo import ASCENDING, MongoClient
from fastapi.encoders import jsonable_encoder

from models.author import Author, AuthorManager
from models.credentials import Credentials
from models.post import Post
from models.like import Like
from models.inbox import InboxItem


class SocialDatabase:
    __slots__ = ['__mongo_client', 'db_name', 'database']
    _instance = None

    def __new__(cls, host: str = "localhost", port: int = 27017):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.__mongo_client = MongoClient(host, port)
            cls.db_name = "socialnetwork"
            cls.database = cls.__mongo_client[cls.db_name]

        return cls._instance

    def __del__(self):
        return self.__mongo_client.close()

    def close(self):
        return self.__del__()

    def create_author(self, author: Author) -> bool:
        # Check not needed if insert_one does not overwrite data
        if self.get_author(author.id):
            return False

        data = author.encode_for_mongo()
        result = self.database.authors.insert_one(data)
        if result.acknowledged:
            manager = AuthorManager(id=author.id).encode_for_mongo()
            self.database.authorManagers.insert_one(manager)

        return result.acknowledged

    def update_author(self, author: Author) -> bool:
        data = author.encode_for_mongo()
        result = self.database.authors.update_one({"_id": author.id},
                                                  {"$set": data})
        return result.acknowledged

    def update_author_using_fields(self, name: str, github: str, password: str, auth_level: str, profileImage: str, id: str) -> bool:
        result = self.database.authors.update_one({"_id": id}, {"$set": {
                                                  "displayName": name, "github": github, "hashedPassword": password, "authLevel": auth_level, "profileImage": profileImage}})
        return result.acknowledged

    def delete_author(self, author_id: str) -> bool:
        result = self.database.authors.delete_one({"_id": author_id})
        if result.acknowledged:
            self.database.authorManagers.delete_one({"_id": author_id})

        return result.acknowledged

    def get_author(self, author_id: str) -> Author | None:
        '''Return an author by id'''
        author = self.database.authors.find_one({"_id": author_id})
        if not author:
            return None

        return Author.init_from_mongo(author)

    def get_author_byname(self, author_name: str) -> Author | None:
        '''Return an author by display name'''
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

    def approve_author(self, author_id: str) -> bool:
        result = self.database.authors.update_one(
            {"_id": author_id}, {"$set": {"authLevel": "user"}})
        return result.acknowledged

    def get_inbox(self, author_id: str) -> list[Post] | None:
        manager = self.get_author_manager(author_id)
        if not manager:
            return None

        return asdict(manager)["inbox"]

    def get_post(self, author_id: str, post_id: str) -> Post | None:
        manager = self.get_author_manager(author_id)
        if manager and post_id in manager.posts:
            # return manager.posts[post_id]
            return Post.init_from_mongo(manager.posts[post_id])

        return None

    def get_posts(self, author_id: str, limit: int = 0) -> list[dict] | None:
        manager = self.get_author_manager(author_id)
        if not manager:
            return None

        # return manager.posts
        return asdict(manager)["posts"]

    def get_post_by_id(self, post_id: str) -> Post | None:
        authorsManagers = self.database["authorManagers"].find()

        # iterate through all author managers and find the post
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
                                                         {"$set": {f"posts.{post.id}": post.encode_for_mongo()}})
        return result.acknowledged

    def update_post(self, author_id: str, post_id: str, post: Post) -> bool:
        manager = self.get_author_manager(author_id)
        if not (manager and post_id in manager.posts.keys()):
            return False

        result = self.database.authorManagers.update_one({"_id": author_id},
                                                         {"$set": {f"posts.{post.id}": post.encode_for_mongo()}})
        return result.acknowledged

    def update_post_using_fields(self, title: str, content: str, contentType: str, description: str, visibility: str, unlisted: str, post_id: str, author_id: str) -> bool:
        result = self.database.authorManagers.update_one({"_id": author_id}, {"$set": {
            f"posts.{post_id}.title": title, f"posts.{post_id}.content": content, f"posts.{post_id}.contentType": contentType, f"posts.{post_id}.description": description, f"posts.{post_id}.visibility": visibility, f"posts.{post_id}.unlisted": unlisted}})
        return result.acknowledged

    def check_liked(self, item:dict, like_author: str)->bool:
        '''Check if this user liked this post/comment already'''
        if "likes" in item:
            for like in item["likes"]:
                print(item, like_author)
                if like["author"]["id"] == like_author:
                    print("Already liked")
                    return True
        return False

    def get_author_likes(self, author_id:str)->list:
        '''Return all liked item from author with author_id into a list'''
        posts = self.get_all_posts()
        author_likes = []
        for post in posts:
            if "likes" in post.keys():
                for like in post["likes"]: # for each post with like attribute
                     if author_id == like["author"]["id"]: # if liked by this author
                        author_likes.append(like)

        return author_likes

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
        if self.check_liked(post, like_author):
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
        if self.check_liked(comment, like_author):
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

    def is_login_user_admin(self, author_id: str) -> bool:
        author = self.get_author(author_id)
        if (author.authLevel == "admin"):
            return True
        return False

    def get_total_users(self) -> int:
        return self.database["authors"].count_documents({})

    def get_all_users(self) -> list[Author]:
        users = self.database["authors"].find({})
        return [Author(**user) for user in users]

    def get_all_authors_and_authormanagers_combined(self) -> list:
        users = list(self.database["authors"].find({}))
        managers = list(self.database["authorManagers"].find({}))
        # Go Through all users and add fields of managers to users list
        for user in users:
            for manager in managers:
                if user["_id"] == manager["_id"]:
                    user["posts"] = manager["posts"]
                    user["inbox"] = manager["inbox"]
                    user["followers"] = manager["followers"]
                    user["following"] = manager["following"]
                    user["requests"] = manager["requests"]
        return users

    # TODO: Functions should match their type hints
    def get_all_posts(self) -> list[Post]:
        posts = []
        # go through all authormanagers and add posts in them to posts list
        for manager in self.database["authorManagers"].find({}):
            for post in manager["posts"].values():
                posts.append(post)
        return posts

    def get_all_public_posts(self) -> list[Post]:
        '''fetch all public posts'''
        posts = self.get_all_posts()
        return [post for post in posts if post['visibility'] == 'PUBLIC']

    def get_all_author_posts(self, author_id: str) -> list[Post]:
        author = self.get_author_manager(author_id)
        if not author:
            return []
        return list(author.posts.values())

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

    def get_credentials(self, remote_host: str) -> Credentials | None:
        '''Get credentials for a remote host'''
        credentials = self.database.remote_credentials.find_one({'_id': remote_host})
        if not credentials:
            return None

        return Credentials.init_from_mongo(credentials)

    def check_friends(self, current_author_id:str, foreign_author_id:str):
        '''Check if two users are True friend'''
        current_manager = self.database.authorManagers.find_one({"_id": current_author_id})
        foreign_manager  = self.database.authorManagers.find_one({"_id": foreign_author_id})

        if not current_manager or not foreign_manager:
            return False

        # True friends
        if current_author_id in foreign_manager["following"] and foreign_author_id in current_manager["following"]:
            return True
