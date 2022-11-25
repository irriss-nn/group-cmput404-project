from fastapi import APIRouter, HTTPException, Request, status, Body, Cookie
from models.comments import Comment
from models.inbox import InboxItem
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from pathlib import Path
from database import SocialDatabase
import json
from jose import JWTError, jwt
static_dir = f"{Path.cwd()}/static"
templates = Jinja2Templates(directory=f"{static_dir}/templates")

router = APIRouter(
    prefix="/service/authors",
    tags=["posts"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{author_id}/posts/{post_id}/comments/view")
async def show_comment(author_id: str, post_id: str, request: Request, page: int | None = None, size: int | None = None, session: str = Cookie(None)):
    comments = await read_comments(request, author_id, post_id, page, size)
    found_user = SocialDatabase().get_author(author_id)
    try:
        our_profile_id = await get_userId_from_token(session)
        our_profile = SocialDatabase().get_author(our_profile_id)
    except HTTPException:
        our_profile = found_user
    return templates.TemplateResponse("comments.html", {"request": request, "comments": comments, "user": our_profile, "myuser": our_profile})


@router.post("/{author_id}/posts/{post_id}/comments")
async def create_comment(author_id: str, post_id: str, request: Request, comment: Comment = Body(...)):
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
        if (author == None or post == None):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Author or post not found")
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post or author not found")
    try:
        comment = jsonable_encoder(comment)
        comment['author'] = author_id
        comment['post'] = post_id
        comment["_id"] = comment["id"]
        comment.pop('id', None)
        comment_id = comment["_id"]
        # inserting comment into database
        request.app.database["comments"].insert_one(comment)
        # Create inbox notification on comment creation and put it in the author's inbox
        inbox_item = InboxItem(
            action="Comment Notification",
            actionDescription="{} commented: {}".format(
                author.displayName, comment["comment"]),
            actionReference=comment_id,
        )
        inbox_item = jsonable_encoder(inbox_item)
        request.app.database["authorManagers"].update_one({"_id": manager.id}, {
                                                          "$push": {"inbox": inbox_item}})
        # Adding comment to post
        return request.app.database["comments"].find_one({"_id": comment_id})
    except:
        raise HTTPException(status_code=404, detail="Invalid Comment")


@router.get("/{author_id}/posts/{post_id}/comments")
async def read_comments(request: Request, author_id: str, post_id: str, page: int | None = None, size: int | None = None):
    url = request.url._url
    print(url)
    if SocialDatabase().get_author(author_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")

    if (page is None or size is None):
        page = 1
        size = 5
        comments = list(request.app.database["comments"].find({"post": post_id}).sort(
            "_id", 1).skip(((page - 1) * size) if page > 0 else 0).limit(size))
        for i in range(len(comments)):
            author = SocialDatabase().get_author(
                comments[i]["author"])  # get comment's author
            author.hashedPassword = None  # clear password before return author object

            # convert author into a dictionary
            comments[i]["author"] = {
                "displayName": author.displayName,
                "type": "author",
                "url": author.url,
                "github": author.github,
                "profileImage": author.profileImage,
                "host": author.host,
                "id": author.id
            }
            
        # TODO: change hardcoded url to actual url
        return {"type": "comments", "page": page, "size": size, "post": "http://127.0.0.1:5454/authors/{}/posts/{}".format(author_id, post_id), "id": "http://127.0.0.1:5454/authors/{}/posts/{}/comments".format(author_id, post_id), "comments": comments}
    else:
        comments = list(request.app.database["comments"].find({"post": post_id}).sort(
            "_id", 1).skip(((page - 1) * size) if page > 0 else 0).limit(size))
        return {"type": "comments", "page": page, "size": size, "post": "http://127.0.0.1:5454/authors/{}/posts/{}".format(author_id, post_id), "id": "http://127.0.0.1:5454/authors/{}/posts/{}/comments".format(author_id, post_id), "comments": comments}


SECRET_KEY = 'f015cb10b5caa9dd69ebeb340d580f0ad37f1dfcac30aef8b713526cc9191fa3'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def get_userId_from_token(token: str):
    try:
        if (token == None):
            raise HTTPException(status_code=401, detail="Unauthorized")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userId: str = payload.get("_id")
        return userId
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
