from dataclasses import asdict
from fastapi import APIRouter, HTTPException, Request, status
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

def encode_post(post: Post):
    enc_post = asdict(post)
    enc_post["type"] = "post"
    return enc_post

@router.get("/{author_id}/posts/{post_id}/view")
async def read_post(request: Request, author_id: str, post_id: str):
    '''Method to view post form template'''
    try:
        author = request.app.database["authors"].find_one({"_id":author_id})
        author_manager = request.app.database["authorManagers"].find_one({"_id": author_id})

        authorImg = author["profileImage"]
        document = author_manager["posts"][post_id]
        document["author"]["profileImage"] = authorImg
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if document:
        return templates.TemplateResponse("post.html", {"request": request, "post": document})

    raise HTTPException(status_code=404, detail="Post not found")

@router.get("/{author_id}/posts/{post_id}")
async def read_post(author_id: str, post_id: str):
    '''Return a post belonging to an author'''
    post = SocialDatabase().get_post(author_id, post_id)
    if post:
        return encode_post(post)

    raise HTTPException(status_code=404, detail="Post not found")

@router.get("/{author_id}/posts/")
async def read_posts(author_id: str):
    '''Return all posts belonging to an author'''
    posts = SocialDatabase().get_posts(author_id)
    if posts:
        return posts

    raise HTTPException(status_code=404, detail="Author does not exist")

@router.post("/{author_id}/posts/")
async def create_post_without_id(author_id: str, post: Post):
    '''Create a new post'''
    if SocialDatabase().create_post(author_id, post):
        return encode_post(post)

    raise HTTPException(status_code=400, detail="Could not create post")
    
@router.post("/{author_id}/posts/{post_id}")
async def update_post(author_id: str, post_id: str, post: Post):
    '''Update a post'''
    if post.id != post_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Post ids do not match")

    if SocialDatabase().update_post(author_id, post_id, post):
        return encode_post(post)

    raise HTTPException(status_code=400, detail="Failed to update post")

@router.delete("/{author_id}/posts/{post_id}")
async def delete_post(author_id: str, post_id: str):
    '''Delete a post'''
    if SocialDatabase().delete_post(author_id, post_id):
        return

    raise HTTPException(status_code=404, detail="Post not found")

@router.put("/{author_id}/posts/{post_id}")
async def put_post(author_id: str, post_id: str, post: Post):
    '''Create a new post with given post_id'''
    post.id = post_id
    if SocialDatabase().create_post(author_id, post):
        return encode_post(post)

    raise HTTPException(status_code=400, detail="Could not create post")
