from fastapi import APIRouter, HTTPException, Request, status,Body
from models.comments import Comment
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from pathlib import Path
from database import SocialDatabase
import json

static_dir = f"{Path.cwd()}/static"
templates = Jinja2Templates(directory=f"{static_dir}/templates")

router = APIRouter(
    prefix="/service/authors",
    tags=["posts"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{author_id}/posts/{post_id}/comments/view")
async def show_comment(author_id:str, post_id:str, request: Request, page: int|None = None, size: int|None = None):
    comments = await read_comments(request, author_id, post_id, page, size)
    print(comments)
    return templates.TemplateResponse("comments.html", {"request":request, "comments": comments})

@router.post("/{author_id}/posts/{post_id}/comments")
async def create_comment(author_id: str,post_id:str, request: Request, comment: Comment = Body(...)):
    # See if we can find the post and author to validate them first
    post = None
    try:
        # Validate post exists
        # Find post_id through all authors
        authors = SocialDatabase().get_authors()
        for author in authors:
            # This is author for post
            manager = SocialDatabase().get_author_manager(author.id)
            if post_id in manager.posts.keys():
                post = manager.posts[post_id]
                break
    
        # This is author for comment
        author = SocialDatabase().get_author(author_id)
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
        for i in range(len(comments)):
            author = SocialDatabase().get_author(comments[i]["author"]) # get comment's author 
            author.hashedPassword=None # clear password before return author object
            
            # convert author into a dictionary
            comments[i]["author"] = {
                "displayName":author.displayName, 
                "type":"author",
                "url":author.url,
                "github":author.github, 
                "profileImage":author.profileImage,
                "host":author.host,
                "id":author.id
                }

        return {"type":"comments","page":page,"size":size, "post":"http://127.0.0.1:5454/authors/{}/posts/{}".format(author_id,post_id), "id":"http://127.0.0.1:5454/authors/{}/posts/{}/comments".format(author_id,post_id),"comments": comments}
    else:
        comments = list(request.app.database["comments"].find({"post":post_id}).sort("_id",1).skip(( ( page - 1 ) * size ) if page > 0 else 0).limit(size))
        return {"type":"comments","page":page,"size":size, "post":"http://127.0.0.1:5454/authors/{}/posts/{}".format(author_id,post_id), "id":"http://127.0.0.1:5454/authors/{}/posts/{}/comments".format(author_id,post_id),"comments": comments}