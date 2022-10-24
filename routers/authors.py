from fastapi import APIRouter, HTTPException, Request, Body, status
from fastapi.encoders import jsonable_encoder

from models.author import Author
from models.author_manager import AuthorManager


router = APIRouter(
    prefix="/service/authors",
    tags=["author"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def read_authors(request: Request, page: int|None = None, size: int|None = None):
    if (page is None or size is None):
        authors = list(request.app.database["authors"].find(limit=100))
    else:
        authors = list(request.app.database["authors"].find().sort("_id",1).skip(( ( page - 1 ) * size ) if page > 0 else 0).limit(size))

    return authors

@router.post("/")
async def create_author(request: Request, author: Author = Body(...)):
    author = jsonable_encoder(author)
    author["_id"] = author["id"]
    author.pop('id', None)
    
    if request.app.database["authors"].find_one({"_id": author["_id"]}):
        request.app.database["authors"].update_one({"_id": author["_id"]}, {"$set": author})
    else:
        # We create a new author manager when creating a new author, assume if updating author, author manager already exists
        authm = jsonable_encoder(AuthorManager(owner=author["_id"]))
        authm["_id"] = authm["id"]
        authm.pop('id', None)
        request.app.database["authors"].insert_one(author)
        request.app.database["authorManagers"].insert_one(authm)
    return request.app.database["authors"].find_one({"_id": author["_id"]})

'''
Get author by id
'''
@router.get("/{author_id}")
async def read_item(author_id: str, request: Request):
    request.app.database["authors"].find_one({"id": author_id})
    return { "author_id": author_id}

# Follower functionalities
'''
Delete a follower frmo authors follower list
'''
@router.delete("/{author_id}/followers/{foreign_author_id}")
async def delete_follower(author_id: str, foreign_author_id: str, request: Request):
    request.app.database["authorManagers"].update_one({"owner": author_id}, {"$pull": {"followers": foreign_author_id}})
    return {"message": "Successfully deleted follower", "author_id": author_id, "foreign_author_id": foreign_author_id}

'''
Add a user to the list of followers of the author
'''
@router.put("/{author_id}/followers/{foreign_author_id}")
async def add_follower(author_id: str, foreign_author_id: str, request: Request):
    # We need to handle authentication here !!! TO DO !!!
    request.app.database["authorManagers"].update_one({"owner": author_id}, {"$push": {"followers": foreign_author_id}})
    return {"message": "Successfully added follower", "author_id": author_id, "foreign_author_id": foreign_author_id}

'''
Get a list of all followers of the author
'''
@router.get("/{author_id}/followers/{foreign_author_id}")
# Check if foreign author id is a follower of author id, if it is return message if not return error
async def check_follower(author_id: str, foreign_author_id: str, request: Request):
    if request.app.database["authorManagers"].find_one({"owner": author_id, "followers": foreign_author_id}):
        return {"message": "Foreign author is a follower of author", "author_id": author_id, "foreign_author_id": foreign_author_id}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foreign author is not a follower of author")

'''
Get a list of all followers of the author
'''
@router.get("/{author_id}/followers")
async def read_followers(author_id: str, request: Request):
    return_list = []
    follower_list =  request.app.database["authorManagers"].find_one({"owner": author_id})["followers"]
    if follower_list is None:
        return { "type": "followers", "items": return_list }

    for objId in follower_list:
        return_list.append(request.app.database["authors"].find_one({"_id": objId}))
    return { "type": "followers", "items": return_list }
