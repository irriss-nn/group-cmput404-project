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
    
    return author_id
    # if "id" in comment.keys() and comment["id"] != author_id:
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Updating comment id is not the same as url comment id")
    # comment["_id"] = comment["id"]
    # comment.pop('id', None)
    # if request.app.database["comments"].find_one({"_id": comment_id}):
    #     request.app.database["comments"].update_one({"_id": comment_id}, {"$set": comment})
    # else:
    #     request.app.database["comments"].insert_one(comment)
    # return request.app.database["comments"].find_one({"_id": comment["_id"]})

@router.get("/{author_id}/posts/{post_id}/comments")
async def read_comments(request: Request, author_id:str, post_id:str):
    return_list = []
    comment_list =  request.app.database["authorManagers"].find_one({"owner": author_id})
    if comment_list is None:
        return { "type": "followers", "items": return_list }
    for objId in comment_list["followers"]:
        return_list.append(request.app.database["authors"].find_one({"_id": objId}))
    return { "type": "followers", "items": return_list }
