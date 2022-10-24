from ast import Try, arg
from faker import Faker
import requests
import sys
import random
from pymongo import MongoClient
fake = Faker()

# First argument is the number of authors to create, second argument is method to populate the database(1 for API, 0 for direct connection)
# Can leave both blank for default of 10, 0
# Use direct connection for now
def main(args=None):
    inserted_authors = []
    inserted_posts = []
    numAuthorsToCreate = 10
    howToPopulate = 0
    if args is None:
        args = sys.argv[1:]
        if len(args) != 0:
            numAuthorsToCreate = int(args[0])
            try:
                howToPopulate = int(args[1])
                if(howToPopulate == 1):
                    print("Populating through API")
            except:
                howToPopulate = 0
    database, mongodb_client = connect_to_db()
    for i in range(numAuthorsToCreate):
        fakeuuid = fake.uuid4()
        fakename = fake.name()
        if(howToPopulate == 1):
            populate_through_api()
        else:
            author = {
                "_id": fakeuuid,
                "url": "http://127.0.0.1:8000/authors/"+fakeuuid,
                "host": "http://127.0.0.1:8000/",
                "displayName": fakename,
                "github": "http://github.com/"+ fakename.replace(" ", "_"),
                "profileImage": fake.image_url(),
                "type": "author",
                "authLevel": "user"
            }
            author_manager = {
                "_id": fake.uuid4(),
                "owner": fakeuuid,
                "followers": [],
                "following": [],
                "posts": [],
                "inbox": [],
                "requests": []
            }
            ins_author = database["authors"].insert_one(author)
            ins_author_manager = database["authorManagers"].insert_one(author_manager)
            inserted_authors.append(author)
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
            "contentType":"text/plain",
            "content": fake.paragraph(),
            "author": {"id": chosenAuthor["_id"]},
            "categories": fake.random_choices(elements=('web', 'tutorial', 'gaming', 'comedy',"documentary", "life", "school")),
            "count": 0,
            "comments":"http://127.0.0.1:5454/authors/{}/{}/comments".format(chosenAuthor["_id"], fakeuuid),
            "commentsSrc": {},
            "published": (fake.date_time()).isoformat(),
            "visibility":"PUBLIC",
            "unlisted":"false"
        }
        ins_post = database["post"].insert_one(post)
        inserted_posts.append(post)
    print("Inserted {} posts successfully".format(len(inserted_posts)))
    destroy_connect_to_db(mongodb_client)

def populate_through_api():
    fakeuuid = fake.uuid4()
    fakename = fake.name()
    print(fakeuuid , " asd")
    author = {
        "id": fakeuuid,
        "displayName": fakename,
        "github": "http://github.com/"+ fakename.replace(" ", "_"),
        "profileImage": fake.image_url()
    }
    # author_id = database["authors"].insert_one(author).inserted_id
    # print(f"Created author with id {author_id}")
    requests.post("http://localhost:8000/service/authors/", json = author)
    

def connect_to_db():
    mongodb_client = MongoClient("mongodb://localhost:27017")
    database = mongodb_client["socialnetwork"]
    print("Connected to MongoDB")
    return database, mongodb_client

def destroy_connect_to_db(mongodb_client):
    mongodb_client.close()
    print("Disconnected to MongoDB")


if __name__ == "__main__":
    main()