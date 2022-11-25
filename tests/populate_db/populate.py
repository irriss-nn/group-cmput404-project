# To run on windows python -m tests.populate_db.populate
import random
import requests
import secrets
import sys

from fastapi.encoders import jsonable_encoder
from faker import Faker
from pymongo import MongoClient
from os import getenv

from models.author import Author
from models.inbox import InboxItem
from database import SocialDatabase
# sys.path.append('../../')
fake = Faker()
# First argument is the number of authors to create, second argument is method to populate the database(1 for API, 0 for direct connection)
# Can leave both blank for default of 10, 0
# Use direct connection for now


def main(args=None):
    inserted_authors = []
    inserted_author_managers = []
    inserted_posts = []
    inserted_comments = []
    numAuthorsToCreate = 10
    howToPopulate = 0
    if args is None:
        args = sys.argv[1:]
        if len(args) != 0:
            numAuthorsToCreate = int(args[0])
            try:
                howToPopulate = int(args[1])
                if (howToPopulate == 1):
                    print("Populating through API")
            except:
                howToPopulate = 0
    database, mongodb_client = connect_to_db()
    mongodb_client.drop_database("socialnetwork")
    print("Dropped database")
    for i in range(numAuthorsToCreate):
        fakeuuid = fake.uuid4()
        fakename = fake.name()
        if howToPopulate == 1:
            populate_through_api()
        else:
            author = {
                "_id": fakeuuid,
                "url": "http://127.0.0.1:8000/authors/" + fakeuuid,
                "host": "http://127.0.0.1:8000/",
                "displayName": fakename,
                "github": "http://github.com/" + fakename.replace(" ", "_"),
                "profileImage": fake.image_url(),
                "type": "author",
                "authLevel": "user",
                "hashedPassword": secrets.token_urlsafe(8)
            }

            SocialDatabase().create_author(Author.init_from_mongo(author))
            # print(author)
            author_manager = SocialDatabase().get_author_manager(author["id"])
            inserted_authors.append(author)
            inserted_author_managers.append(author_manager)

    print("Inserted {} authors successfully".format(len(inserted_authors)))

    # Create fake posts
    for i in range(numAuthorsToCreate):
        chosenAuthor = random.choice(inserted_authors)
        fakeuuid = fake.uuid4()
        post = {
            "type": "post",
            "title": fake.sentence(),
            "_id": fakeuuid,
            "source": fake.url(),
            "origin": fake.url(),
            "description": fake.sentence(),
            "contentType": "text/plain",
            "content": fake.paragraph(),
            "author": {"id": chosenAuthor["id"]},
            "categories": fake.random_choices(elements=('web', 'tutorial', 'gaming', 'comedy', "documentary", "life", "school")),
            "count": 0,
            "comments": "http://127.0.0.1:5454/authors/{}/{}/comments".format(chosenAuthor["id"], fakeuuid),
            "commentsSrc": {},
            "published": (fake.date_time()).isoformat(),
            "visibility": "PUBLIC",
            "unlisted": "false"
        }
        database["authorManagers"].update_one({"_id": chosenAuthor["id"]}, {
                                              "$set": {"posts.{}".format(fakeuuid): post}})
        # adding_to_author = database["authors"].update_one({"_id": chosenAuthor["_id"]}, {"$push": {"posts": post}})
        inserted_posts.append(post)

    # Make fake comments
    for i in range(numAuthorsToCreate):
        chosenPost = random.choice(inserted_posts)
        chosentPostAuthor = chosenPost["author"]["id"]
        chosenAuthor = random.choice(inserted_authors)
        fakeuuid = fake.uuid4()
        comment = {
            "type": "comment",
            "_id":  fakeuuid,
            "author": chosenAuthor["id"],  # Author ID of the post
            "post": chosenPost["_id"],  # ObjectId of the post
            "comment":  fake.sentence(),
            "contentType": "text/markdown",
            "published": str((fake.date_time()).isoformat())
        }
        inbox_item = InboxItem(
            action="Comment Notification",
            actionDescription="{} commented: {}".format(
                chosenAuthor["displayName"], comment["comment"]),
            actionReference=comment["_id"],
        )
        inbox_item = jsonable_encoder(inbox_item)
        # add inbox item to array of inbox of chosenpostauthor
        database["authorManagers"].update_one({"_id": chosentPostAuthor}, {
                                              "$push": {"inbox": inbox_item}})
        database["comments"].insert_one(comment)
        inserted_comments.append(comment)

    # Make fake followers
    inserted = 0
    for i in range(numAuthorsToCreate*3):
        chosenAuthorManager = random.choice(inserted_author_managers)
        chosenFollowerManager = random.choice(inserted_author_managers)
        if chosenAuthorManager.id != chosenFollowerManager.id:
            database["authorManagers"].update_one({"_id": chosenAuthorManager.id},
                                                  {"$push": {"followers": chosenFollowerManager.id}})
            database["authorManagers"].update_one({"_id": chosenFollowerManager.id},
                                                  {"$push": {"following": chosenAuthorManager.id}})
            inserted += 1

    print("Inserted {} followers successfully".format(inserted))
    print("Inserted {} posts successfully".format(len(inserted_posts)))
    print("Inserted {} comments successfully".format(len(inserted_comments)))
    disconnect_db()


def populate_through_api():
    fakeuuid = fake.uuid4()
    fakename = fake.name()
    print(fakeuuid, " asd")
    author = {
        "id": fakeuuid,
        "displayName": fakename,
        "github": "http://github.com/" + fakename.replace(" ", "_"),
        "profileImage": fake.image_url()
    }
    # author_id = database["authors"].insert_one(author).inserted_id
    # print(f"Created author with id {author_id}")
    requests.post("http://localhost:8000/service/authors/", json=author)


def connect_to_db():
    args = {}
    host = getenv('MONGODB_ADDR')
    port = getenv('MONGODB_PORT')

    if host:
        args['host'] = host

    if port and port.isnumeric():
        args['port'] = port

    social_db = SocialDatabase(**args)
    database = social_db.database
    mongodb_client = database.client
    print("Connected to MongoDB")
    return database, mongodb_client


def disconnect_db():
    SocialDatabase().close()
    print("Disconnected from MongoDB")


if __name__ == "__main__":
    main()
