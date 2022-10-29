from dataclasses import asdict
from pprint import pprint
from fastapi import APIRouter, HTTPException, Request, Body, status
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from pathlib import Path
from pydoc import doc

from database import SocialDatabase
from models.author import Author
from models.author_manager import AuthorManager


static_dir = f"{Path.cwd()}/static"
templates = Jinja2Templates(directory=f"{static_dir}/templates")
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
    for i in range(len(authors)):
        authors[i].pop("hashedPassword", None)
        authors[i]["id"] = authors[i]["_id"]
        authors[i].pop('_id', None)
    return authors

@router.post("/{author_id}")
async def create_author(author_id: str, request: Request, author: Author = Body(...)):
    author = jsonable_encoder(author)
    if "id" in author.keys() and author["id"] != author_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Updating author id is not the same as url author id")
    author["_id"] = author["id"]
    author.pop('id', None)
    if request.app.database["authors"].find_one({"_id": author_id}):
        request.app.database["authors"].update_one({"_id": author_id}, {"$set": author})
    else:
        # We create a new author manager when creating a new author, assume if updating author, author manager already exists
        authm = jsonable_encoder(AuthorManager(owner=author["_id"]))
        authm["_id"] = authm["id"]
        authm.pop('id', None)
        request.app.database["authors"].insert_one(author)
        request.app.database["authorManagers"].insert_one(authm)
    return request.app.database["authors"].find_one({"_id": author["_id"]})

@router.get("/{author_id}")
async def read_item(author_id: str):
    '''Get author by id'''
    author = asdict(SocialDatabase().get_author(author_id))
    author.pop("hashedPassword", None)
    return author

# Follower functionalities
@router.delete("/{author_id}/followers/{foreign_author_id}")
async def delete_follower(author_id: str, foreign_author_id: str, request: Request):
    '''Delete a follower from authors follower list'''
    request.app.database["authorManagers"].update_one({"owner": author_id}, {"$pull": {"followers": foreign_author_id}})
    return {"message": "Successfully deleted follower", "author_id": author_id, "foreign_author_id": foreign_author_id}

@router.put("/{author_id}/followers/{foreign_author_id}")
async def add_follower(author_id: str, foreign_author_id: str, request: Request):
    '''Add a user to the list of followers of the author'''
    # We need to handle authentication here !!! TO DO !!!
    request.app.database["authorManagers"].update_one({"owner": author_id}, {"$push": {"followers": foreign_author_id}})
    return {"message": "Successfully added follower", "author_id": author_id, "foreign_author_id": foreign_author_id}

@router.get("/{author_id}/followers/{foreign_author_id}")
# Check if foreign author id is a follower of author id, if it is return message if not return error
async def check_follower(author_id: str, foreign_author_id: str, request: Request):
    '''
    Check if foreign author id is a follower of author id, return message if so
    otherwise return error
    '''
    if request.app.database["authorManagers"].find_one({"owner": author_id, "followers": foreign_author_id}):
        return {"message": "Foreign author is a follower of author", "author_id": author_id, "foreign_author_id": foreign_author_id}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foreign author is not a follower of author")

@router.get("/{author_id}/followers")
async def read_followers(author_id: str, request: Request):
    '''Get a list of all followers of the author'''
    return_list = []
    follower_list =  request.app.database["authorManagers"].find_one({"owner": author_id})
    if follower_list is None:
        return { "type": "followers", "items": return_list }
    for objId in follower_list["followers"]:
        return_list.append(request.app.database["authors"].find_one({"_id": objId}))
    return { "type": "followers", "items": return_list }

@router.get("/{author_id}/{foreign_author_id}/status")
async def check_follow_status(author_id: str, foreign_author_id: str, request: Request):
    '''As an author, When I befriend someone I follow them, only when the other author befriends me do I count as a real friend'''
    if request.app.database["authorManagers"].find_one({"owner": author_id, "following": {"$in": [foreign_author_id]}}) and request.app.database["authorManagers"].find_one({"owner": foreign_author_id, "following": {"$in": [author_id]}}): 
        return {"message": "We are true friends", "author_id": author_id, "foreign_author_id": foreign_author_id}
    elif request.app.database["authorManagers"].find_one({"owner": author_id, "following": {"$in": [foreign_author_id]}}): 
        return {"message": "I am just a friend", "author_id": author_id, "foreign_author_id": foreign_author_id}
    else:
        return {"message": "We are not friends", "author_id": author_id, "foreign_author_id": foreign_author_id}

#### USER FACING VIEWS ####
@router.get("/{author_id}/view")
async def read_item( request: Request, author_id: str,):
    '''
    Display author profile
    '''
    try:
        document = request.app.database["authors"].find_one({"_id": author_id})
        if (document is None):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
        return templates.TemplateResponse("author.html", {"request": request, "post": document})
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
