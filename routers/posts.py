from pprint import pprint
from fastapi import APIRouter, HTTPException, Request, status
from models import post
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from pathlib import Path
import pprint
router = APIRouter(
    prefix="/service/authors",
    tags=["posts"],
    responses={404: {"description": "Not found"}},
)

static_dir = f"{Path.cwd()}/static"
templates = Jinja2Templates(directory=f"{static_dir}/templates")

'''
Method to view post form template
'''
@router.get("/{author_id}/posts/{post_id}/view")
async def read_post(request: Request, author_id:str, post_id:str):
    try:
        document = request.app.database["post"].find_one({"_id":post_id})
        postAuthor = document["author"]["id"]
        author = request.app.database["authors"].find_one({"_id":postAuthor})
        document["author"] = author
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if document:
        return templates.TemplateResponse("post.html", {"request": request, "post": document})
    raise HTTPException(status_code=404, detail="Post not found")


@router.get("/{author_id}/posts/{post_id}")
async def read_post(request: Request, author_id:str, post_id:str):
    document = request.app.database["post"].find_one({"_id":post_id})
    if document:
        return document
    raise HTTPException(status_code=404, detail="Post_not_found")

@router.post("/{author_id}/posts/{post_id}")
async def update_post(request: Request, author_id:str, post_id:str, post: post.Post):
    post = jsonable_encoder(post)
    if post["id"] != post_id :
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Updating post id is not the same as url post id")
    post["_id"] = post["id"]
    existed_post = request.app.database["post"].find_one({"_id":post["_id"]})
    if existed_post: # the post to be modified exists:
        for key in post.keys():
            if post[key] != type(existed_post[key]): # if new data has different type on the same parameter except commentSrc:
                if not (key=="commentSrc" and (post[key] == None or type(post[key]) == str)):
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Update field type is incorrect")
    else:
        raise HTTPException(status_code=404, detail="Post_not_found")

    try:
        update_query = {"$set": post}
        request.app.database["post"].update_one({"_id":post_id}, update_query)
    except Exception:
        raise HTTPException(status_code=404, detail="Post_not_found")

@router.delete("/{author_id}/posts/{post_id}")
async def delete_post(request: Request, author_id:str, post_id:str):
    request.app.database["post"].delete_one({"_id":post_id})

@router.put("/{author_id}/posts/{post_id}")
async def put_post(request: Request, author_id:str, post_id:str, post: post.Post):
    post = jsonable_encoder(post)
    if request.app.database["post"].find_one({"_id":post["id"]}):
        raise HTTPException(status_code=403, detail="Post_already_exist")
    post["_id"] = post.pop("id")
    request.app.database["post"].insert_one(post)    
    return request.app.database["post"].find_one({"_id":post["_id"]})  
