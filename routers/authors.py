from dataclasses import asdict
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from pathlib import Path
#from pydoc import doc

from database import SocialDatabase
from models.author import Author

static_dir = f"{Path.cwd()}/static"
templates = Jinja2Templates(directory=f"{static_dir}/templates")
router = APIRouter(
    prefix="/service/authors",
    tags=["author"],
    responses={404: {"description": "Not found"}},
)

def encode_author(author: Author):
    del author.authLevel
    del author.hashedPassword
    enc_author = asdict(author)
    enc_author["type"] = "author"

    return enc_author

@router.get("/")
async def read_authors(page: int|None = 0, size: int|None = 0):
    if page is None or size is None:
        authors = SocialDatabase().get_authors()
    else:
        authors = SocialDatabase().get_authors(page*size, size)

    return [encode_author(author) for author in authors]

@router.post("/{author_id}")
async def create_author(author_id: str, author: Author):
    if author.id != author_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Author ids do not match")

    db = SocialDatabase()
    if not (db.create_author(author) or db.update_author(author)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return encode_author(author)

@router.get("/{author_id}")
async def read_item(author_id: str):
    '''Get author by id'''
    author = SocialDatabase().get_author(author_id)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Author does not exist")

    return encode_author(author)

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
