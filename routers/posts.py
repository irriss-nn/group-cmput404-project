from pprint import pprint
from fastapi import APIRouter, HTTPException, Request, status
from models import post
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from pathlib import Path
import uuid
import pprint
router = APIRouter(
    prefix="/service/authors",
    tags=["posts"],
    responses={404: {"description": "Not found"}},
)

static_dir = f"{Path.cwd()}/static"
templates = Jinja2Templates(directory=f"{static_dir}/templates")

@router.get("/{author_id}/posts/{post_id}/view")
async def read_post(request: Request, author_id:str, post_id:str):
    '''
    Method to view post form template
    '''
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
async def read_post(request: Request, author_id:str, post_id:str):
    '''return one post with author_id and post_id'''
    author = request.app.database["authors"].find_one({"_id":author_id})
    if not author:
        raise HTTPException(status_code=404, detail="Author_not_found")

    if post_id not in author["posts"].keys():    
        raise HTTPException(status_code=404, detail="Post_not_found")
        
    return author["posts"][post_id]

@router.get("/{author_id}/posts/")
async def read_posts(request: Request, author_id:str):
    '''return all the posts belong to author with author_id '''
    author = request.app.database["authors"].find_one({"_id":author_id})
    if author:
        return author["posts"].items()
    raise HTTPException(status_code=404, detail="Post_not_found")

@router.post("/{author_id}/posts/")
async def create_post_without_id(request: Request, author_id:str, post: post.Post):
    '''create a new post with generated id'''
    post = jsonable_encoder(post)
    post["id"] = str(uuid.uuid4()) # generate an id
    author = request.app.database["authors"].find_one({"_id":author_id})
    if author:
        author["posts"][post["id"]] = post
        request.app.database["authors"].update_one({"_id": author_id}, {"$set": author})
    else:
        raise HTTPException(status_code=404, detail="Author_not_found")
    
@router.post("/{author_id}/posts/{post_id}")
async def update_post(request: Request, author_id:str, post_id:str, post: post.Post):
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
    '''Delete a post with post_id from author with author_id'''
    author = request.app.database["authors"].find_one({"_id":author_id})

    if not author:
        raise HTTPException(status_code=404, detail="Author_not_found")

    if post_id not in author["posts"].keys():
        raise HTTPException(status_code=404, detail="Post_not_found")

    author["posts"].pop(post_id, None) # remove post from author's dictionary
    request.app.database["authors"].update_one({"_id": author_id}, {"$set": author}) # update author

@router.put("/{author_id}/posts/{post_id}")
async def put_post(request: Request, author_id:str, post_id:str, post: post.Post):
    '''Create a new post with post_id under author with author_id'''
    post = jsonable_encoder(post)
    author = request.app.database["authors"].find_one({"_id":author_id})

    if not author:
        print(author_id)
        raise HTTPException(status_code=404, detail="Author_not_found")

    if post_id in author["posts"]:
        raise HTTPException(status_code=403, detail="Post_already_exist")

    author["posts"][post_id] = post
    request.app.database["authors"].update_one({"_id": author_id}, {"$set": author}) # update author