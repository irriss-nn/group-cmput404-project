from fastapi import APIRouter, HTTPException, Request, status, Cookie
from fastapi.templating import Jinja2Templates
from pathlib import Path
import uuid
from database import SocialDatabase
from models.post import Post
from jose import JWTError, jwt

SECRET_KEY = 'f015cb10b5caa9dd69ebeb340d580f0ad37f1dfcac30aef8b713526cc9191fa3'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(
    prefix="/service/authors",
    tags=["posts"],
    responses={404: {"description": "Not found"}},
)

static_dir = f"{Path.cwd()}/static"
templates = Jinja2Templates(directory=f"{static_dir}/templates")


async def get_userId_from_token(token: str):
    try:
        if (token == None):
            raise HTTPException(status_code=401, detail="Unauthorized")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userId: str = payload.get("_id")
        return userId
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/{author_id}/posts/{post_id}/view")
async def read_post(request: Request, author_id: str, post_id: str, session: str = Cookie(None)):
    '''Method to view post form template'''
    try:
        # fetch author of the post
        author = SocialDatabase().get_author(author_id)
        author_manager = request.app.database["authorManagers"].find_one({
                                                                         "_id": author_id})

        # fetch the post with post_id within this user's post
        post = author_manager["posts"][post_id]
        post["author"] = author

    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    try:
        # current user
        our_profile_id = await get_userId_from_token(session)
        our_profile = SocialDatabase().get_author(our_profile_id)
    except HTTPException as e:
        # Should we redirect to /home if session is token expires?
        print("Error getting profile from session, in method read_post: ")
        print(e)
        our_profile = author

    if post:
        return templates.TemplateResponse("post.html", {"request": request, "post": post, "user": our_profile, "myuser": our_profile})

    raise HTTPException(status_code=404, detail="Post not found")


@router.get("/share/{post_id}/{author_id}/{origin_author_id}")
async def share_post_to_author(request: Request, post_id: str, author_id: str, origin_author_id: str, session: str = Cookie(None)):
    try:
        our_profile = SocialDatabase().get_author(origin_author_id)
    except HTTPException as e:
        # Should we redirect to /home if session is token expires?
        print("Error getting profile from session, in method read_post:")
        return False

    # our_profile = SocialDatabase().get_author(
    #     "44fd0233-380f-40ba-82ae-d8f60dfe1cad")
    return SocialDatabase().create_share_post_notification(author_id, post_id, our_profile.displayName)
    # return True


@router.get("/{author_id}/posts/{post_id}")
async def read_post(author_id: str, post_id: str):
    '''Return a post belonging to an author'''
    post = SocialDatabase().get_post(author_id, post_id)
    if post:
        return post.json()

    raise HTTPException(status_code=404, detail="Post not found")


@router.get("/{author_id}/posts/")
async def read_posts(author_id: str) -> list[dict]:
    '''Return all posts belonging to an author'''
    db = SocialDatabase()
    if not db.get_author(author_id):
        raise HTTPException(status_code=404, detail="Author does not exist")

    posts = db.get_posts(author_id)
    if posts:
        # return [post.json() for post in posts.values()]
        return posts

    return []


@router.post("/{author_id}/posts/")
async def create_post_without_id(request: Request, author_id: str, post: Post):
    '''Create a new post'''
    while True:
        post.id = str(uuid.uuid4())
        if not SocialDatabase().get_post_by_id(post.id):
            break

    if SocialDatabase().create_post(author_id, post):
        return post.json()

    raise HTTPException(status_code=400, detail="Could not create post")


@router.post("/{author_id}/posts/{post_id}")
async def update_post(author_id: str, post_id: str, post: Post):
    '''Update a post'''
    if post.id != post_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Post ids do not match")

    if SocialDatabase().update_post(author_id, post_id, post):
        return post.json()

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
        return post.json()

    raise HTTPException(status_code=400, detail="Could not create post")
