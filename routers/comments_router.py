from fastapi import APIRouter, HTTPException, Request, status,Body
from models.comments import Comment
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/service/authors",
    tags=["posts"],
    responses={404: {"description": "Not found"}},
)

@router.post("/{author_id}/posts/{post_id}/comments")
async def create_comment(author_id: str,post_id:str, request: Request, comment: Comment = Body(...)):
    comment = jsonable_encoder(comment)
    comment['author']=author_id
    comment['post']=post_id
    comment["_id"] = comment["id"]
    comment.pop('id', None)
    comment_id = comment["_id"]
    # inserting comment into database
    request.app.database["comments"].insert_one(comment)
    # Adding comment to post
    return request.app.database["comments"].find_one({"_id": comment_id})

@router.get("/{author_id}/posts/{post_id}/comments")
async def read_comments(request: Request, author_id:str, post_id:str, page: int|None = None, size: int|None = None):
    return_list = []
    if (page is None or size is None):
        page = 1
        size = 5
        comments = list(request.app.database["comments"].find({"post":post_id}).sort("_id",1).skip(( ( page - 1 ) * size ) if page > 0 else 0).limit(size))
        return {"type":"comments","page":page,"size":size, "post":"http://127.0.0.1:5454/authors/{}/posts/{}".format(author_id,post_id), "id":"http://127.0.0.1:5454/authors/{}/posts/{}/comments".format(author_id,post_id),"comments": comments}
    else:
        comments = list(request.app.database["comments"].find({"post":post_id}).sort("_id",1).skip(( ( page - 1 ) * size ) if page > 0 else 0).limit(size))
        return {"type":"comments","page":page,"size":size, "post":"http://127.0.0.1:5454/authors/{}/posts/{}".format(author_id,post_id), "id":"http://127.0.0.1:5454/authors/{}/posts/{}/comments".format(author_id,post_id),"comments": comments}