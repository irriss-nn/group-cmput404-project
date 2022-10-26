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
    # See if we can find the post and author to validate them first

    try:
        post = request.app.database["post"].find_one({"_id":post_id})
        author = request.app.database["authors"].find_one({"_id":author_id})
        if(author == None or post == None):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author or post not found")
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post or author not found")
    try:
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
    except:
        raise HTTPException(status_code=404, detail="Invalid Comment")

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