from fastapi import APIRouter, HTTPException, Request, status
from models import post
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/service/authors",
    tags=["posts"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{author_id}/posts/{post_id}")
async def read_post(request: Request, author_id:str, post_id:str):
    document = request.app.database["post"].find_one({"_id":post_id})
    if document:
        return document
    raise HTTPException(status_code=404, detail="Post_not_found")

@router.post("/{author_id}/posts/{post_id}")
async def update_post(request: Request, author_id:str, post_id:str, post: post.Post):
    post = jsonable_encoder(post)
    existed_post = request.app.database["post"].find_one({"_id":post["id"]})
    if existed_post: # the post to be modified exists:
        for key in post.keys():
            if post[key] != type(existed_post[key]): # if new data has different type on the same parameter except commentSrc:
                if not (key=="commentSrc" and (post[key] == None or type(post[key]) == str)):
                    raise HTTPException(status_code=405, detail="Method_not_allowed")
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
