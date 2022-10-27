import uuid

from dataclasses import asdict
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from pathlib import Path

from database import SocialDatabase
from models.post import Post

router = APIRouter(
    prefix="/service/authors",
    tags=["posts"],
    responses={404: {"description": "Not found"}},
)

static_dir = f"{Path.cwd()}/static"
templates = Jinja2Templates(directory=f"{static_dir}/templates")

@router.get("/{author_id}/posts/{post_id}/view")
async def read_post(request: Request, author_id:str, post_id:str):
    '''Method to view post form template'''
    try:
        author = request.app.database["authors"].find_one({"_id":author_id})
        document = author["posts"][post_id]
        document["author"] = author_id
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if document:
        return templates.TemplateResponse("post.html", {"request": request, "post": document})
    raise HTTPException(status_code=404, detail="Post_not_found")

@router.get("/{author_id}/posts/{post_id}")
async def read_post(author_id: str, post_id: str):
    '''Return a post belonging to an author'''
    post = SocialDatabase().get_post(author_id, post_id)
    if post:
        return asdict(post)

    raise HTTPException(status_code=404, detail="Post not found")

@router.get("/{author_id}/posts/")
async def read_posts(author_id: str):
    '''Return all posts belonging to an author'''
    author = SocialDatabase().get_author(author_id)
    if author:
        return asdict(author)["posts"]

    raise HTTPException(status_code=400, detail="Author does not exist")

@router.post("/{author_id}/posts/")
async def create_post_without_id(author_id: str, post: Post):
    '''Create a new post'''
    if SocialDatabase().create_post(author_id, post):
        return

    raise HTTPException(status_code=400, detail="Could not create post")
    
@router.post("/{author_id}/posts/{post_id}")
async def update_post(request: Request, author_id:str, post_id:str, post: Post):
    '''update a post with post_id'''
    post = jsonable_encoder(post)
    if post["id"] != post_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Post_id_mismatch")

    # check author_id
    author = request.app.database["authors"].find_one({"_id":author_id})
    if not author:
        raise HTTPException(status_code=404, detail="Author_not_found")

    # check post in author
    if post_id not in author["posts"].keys():
        raise HTTPException(status_code=404, detail="Post_not_found")

    # update post under author
    author["posts"][post_id] = post
    # update user at the end
    request.app.database["authors"].update_one({"_id": author_id}, {"$set": author})

@router.delete("/{author_id}/posts/{post_id}")
async def delete_post(request: Request, author_id:str, post_id:str):
    '''Delete a post'''
    author = request.app.database["authors"].find_one({"_id":author_id})

    if not author:
        raise HTTPException(status_code=404, detail="Author_not_found")

    if post_id not in author["posts"].keys():
        raise HTTPException(status_code=404, detail="Post_not_found")

    author["posts"].pop(post_id, None) # remove post from author's dictionary
    request.app.database["authors"].update_one({"_id": author_id}, {"$set": author}) # update author

@router.put("/{author_id}/posts/{post_id}")
async def put_post(author_id: str, post_id: str, post: Post):
    '''Create a new post with given post_id'''
    post._id, post.id = post_id
    if SocialDatabase().create_post(author_id, post):
        return

    raise HTTPException(status_code=400, detail="Could not create post")
