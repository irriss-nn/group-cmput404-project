#!/usr/bin/env python3
import uvicorn
import uuid

from dataclasses import asdict
from datetime import datetime, timedelta
from fastapi import FastAPI, Cookie, Form, HTTPException, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from passlib.context import CryptContext
from pathlib import Path
from os import getenv
from pprint import pprint

# Local imports
from database import SocialDatabase
from routers import authors, posts, comments_router, likes, admin
from models.author import Author
from models.inbox import InboxItem
from extensions import t10_node

# All login and registering related fields
SECRET_KEY = 'f015cb10b5caa9dd69ebeb340d580f0ad37f1dfcac30aef8b713526cc9191fa3'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(request: Request, username: str, password: str):
    found_user = request.app.database["authors"].find_one(
        {"displayName": username})
    if (found_user):
        if (found_user["hashedPassword"] == password):  # Need to compared hashed passwords
            return found_user
        else:
            return None
    else:
        return None


def create_jwt(encoded_data: dict):
    to_encode = encoded_data.copy()
    expire = datetime.utcnow() + timedelta(minutes=45)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_userId_from_token(token: str):
    '''Get user id from JWT'''
    try:
        if (token == None):
            raise HTTPException(status_code=401, detail="Unauthorized")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userId: str = payload.get("_id")
        return userId
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


app = FastAPI()

static_dir = f"{Path.cwd()}/static"
templates = Jinja2Templates(directory=f"{static_dir}/templates")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(authors.router)
app.include_router(posts.router)
app.include_router(comments_router.router)
app.include_router(likes.router)
app.include_router(admin.router)
app.include_router(t10_node.router)


@app.on_event("startup")
def startup_db_client():
    args = {}
    host = getenv('MONGODB_ADDR')
    port = getenv('MONGODB_PORT')

    if host:
        args['host'] = host

    if port and port.isnumeric():
        args['port'] = port

    app.database = SocialDatabase(**args).database
    print("Connected to MongoDB")


@app.on_event("shutdown")
def shutdown_db_client():
    SocialDatabase().close()


@app.get("/")
async def root():
    return RedirectResponse(url='/login')

@app.get("/service/credentials/{remote_host}")
async def get_remote_credentials(remote_host: str):
    '''Return credentials needed to query a remote host'''
    # TODO: Require auth so that only users may query this endpoint
    credentials = SocialDatabase().get_credentials(remote_host)
    if credentials:
        return credentials.json()

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="No credentials for specified host")

@app.get("/login", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register_author_todb(request: Request, response: Response, username: str = Form(), password: str = Form(), github: str = Form()):

    usnm = username
    pswd = password
    git = github
    if (git == None or usnm == None or pswd == None):  # Catch errors
        return RedirectResponse(url='/register')

    while True:
        id = str(uuid.uuid4()) # author id
        if not SocialDatabase().get_author(id):
            break

    newUser = Author(id=id, displayName=usnm, github=git,
                     hashedPassword=pswd)  # TODO: Hash password
    #newUser.url = #hostname+/service/authors/id/
    #newUser.host = #hostname
    print("Creating user" + newUser.id)
    if SocialDatabase().create_author(newUser):
        return RedirectResponse('/login', status_code=status.HTTP_302_FOUND)
    return HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)


@app.post("/login")
async def read_item(request: Request, response: Response, username: str = Form(), password: str = Form()):
    found_user = get_user(request, username, password)
    if found_user == None:  # Return to login if bad password
        response = RedirectResponse(url="/login")
        response.status_code = 302
        response.delete_cookie(key="session")
        return response
    found_user.pop("hashedPassword", None)
    madeJWT = create_jwt(found_user)
    # store session cookie in key for future verification
    # We need to delcare redirect before cookies and return response all totghet
    if (SocialDatabase().is_login_user_admin(found_user["_id"])):
        response = RedirectResponse(
            url="/admin", status_code=status.HTTP_302_FOUND)
        response.status_code = 302
        response.set_cookie(key="session", value=madeJWT)
        # We need to redirect to the user's page
        return response

    response = RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
    response.status_code = 302
    response.set_cookie(key="session", value=madeJWT)
    # We need to redirect to the user's page
    return response

# For when we want to logout user and delete cookie


@app.get("/logout")
async def logout(request: Request, response: Response):
    response = RedirectResponse(url="/login")
    response.status_code = 302
    response.delete_cookie(key="session")
    return response

# To Do For Login:
# 1. Redirect User to proper page after login !!
# 2. Make use of hashing for passwords
# 3. Make sure that the user is not already logged in


@app.get("/current")  # View current profile
async def get_current_user(request: Request, session: str = Cookie(None)):
    if (session == None):
        return RedirectResponse(url="/login")
    # must await for this!!
    try:
        sessionUserId = await get_userId_from_token(session)
    except HTTPException:
        return RedirectResponse(url='/login', status_code=307)

    found_user = SocialDatabase().get_profile(sessionUserId)
    user_info = app.database["authors"].find_one({"_id": sessionUserId})
    follower_list = SocialDatabase().get_followers(sessionUserId)
    following_list = SocialDatabase().get_following(sessionUserId)
    pprint(follower_list)
    if found_user:
        return templates.TemplateResponse("my-profile.html", {"request": request, "user": user_info, "post": found_user, "followers":follower_list, "following":following_list})
    else:
        return RedirectResponse(url="/login")

 # Page user lands on


@app.get("/home")
async def get_home(request: Request, session: str = Cookie(None)):
    if (session == None):
        return RedirectResponse(url="/login")
    # must await for this!!
    try:
        sessionUserId = await get_userId_from_token(session)
    except HTTPException:
        return RedirectResponse(url='/login', status_code=307)
    all_feed_posts = SocialDatabase().get_following_feed(sessionUserId)
    all_feed_posts += SocialDatabase().get_all_public_posts()
    for post in all_feed_posts:
        post["author"] = asdict(SocialDatabase().get_author(post["author"]["id"]))
    current_user = SocialDatabase().get_author(sessionUserId)
    return templates.TemplateResponse("landing.html", {
        "request": request,
        "user": asdict(current_user),
        "feed": all_feed_posts
    })


@app.get("/inbox")
async def get_inbox(request: Request, session: str = Cookie(None)):
    if (session == None):
        return RedirectResponse(url="/login")
    # must await for this!!
    try:
        sessionUserId = await get_userId_from_token(session)
    except HTTPException:
        return RedirectResponse(url='/login', status_code=307)
    all_inbox_posts = SocialDatabase().get_inbox(sessionUserId)
    found_user = app.database["authors"].find_one({"_id": sessionUserId})
    return templates.TemplateResponse("inbox.html", {"request": request, "user": found_user, "inbox": all_inbox_posts})


@app.get("/author/{author_id}")
async def get_author(request: Request, author_id: str, session: str = Cookie(None)):
    '''Return html with selected author & this author's post'''
    if (session == None):
        return RedirectResponse(url="/login")
    try:
        sessionUserId = await get_userId_from_token(session)
    except HTTPException:
        return RedirectResponse(url='/login', status_code=307)

    me_user = app.database["authors"].find_one({"_id": sessionUserId})
    found_user = SocialDatabase().get_author(author_id)
    
    if not found_user: # if id doesn't match any author, maybe it's a search by display name
        found_user = SocialDatabase().get_author_byname(author_id)
        if not found_user:
            return RedirectResponse(url='/home')
    found_user = asdict(found_user)
    author_id = found_user["id"]
    found_user_manager = SocialDatabase().get_author_manager(author_id)
    found_user_manager = asdict(found_user_manager)

    # if user is a friend of current user:
    if me_user["_id"] in found_user_manager["followers"] :
        found_user["posts"] = found_user_manager["posts"]
    else:
        found_user["posts"] = []
        for post_id in found_user_manager["posts"].keys():
            if found_user_manager["posts"][post_id]["visibility"] == "PUBLIC":
                found_user["posts"].append(found_user_manager["posts"][post_id])

    is_following = SocialDatabase().is_following(sessionUserId, found_user["id"])
    if found_user:
        return templates.TemplateResponse("author.html", {"request": request, "user": me_user, "post": found_user, "status": {"following": is_following}})
    return RedirectResponse(url='/home')


@app.post("/followers/{foreign_author_id}/request")
async def add_follower(foreign_author_id: str, request: Request, session: str = Cookie(None)):
    '''Request a follow to the foreign author'''
    if (session == None):
        return RedirectResponse(url="/login")
    try:
        # Create inbox request
        author_id = await get_userId_from_token(session)
        inbox_item = InboxItem(action="Request", actionDescription="You have a new follow request", actionReference=author_id, actionNeeded=True, actionValues={
                               "Accept": f"/service/authors/{foreign_author_id}/accept/{author_id}", "Reject": f"/service/authors/{foreign_author_id}/reject/{author_id}"})
        inbox_item = jsonable_encoder(inbox_item)
        authorReceivingRequest = SocialDatabase().get_author_manager(foreign_author_id)
        # If alreayd sent the request
        if (author_id in authorReceivingRequest.requests or author_id in authorReceivingRequest.followers):
            # return {"message": "You have already sent a request to this author"}
            # return RedirectResponse(url='/home')  # Invalid request
            return False
        request.app.database["authorManagers"].update_one({"_id": foreign_author_id}, {
                                                          "$push": {"inbox": inbox_item, "requests": author_id}})
        # Redirect user back home after sending request
        # return RedirectResponse(url='/home')
        return True
    except:
        return False


@app.post("/dismiss/{inbox_item_id}")
async def dismiss_inbox_item(inbox_item_id: str, request: Request, session: str = Cookie(None)):
    if (session == None):
        return RedirectResponse(url="/login")
    try:
        author_id = await get_userId_from_token(session)
        request.app.database["authorManagers"].update_one({"_id": author_id}, {
                                                          "$pull": {"inbox": {"id": inbox_item_id}}})
        return True
    except:
        return False


# Admin Related Stuff

@app.get("/admin")
async def get_admin(request: Request, session: str = Cookie(None)):
    if (session == None):
        return RedirectResponse(url="/login")
    try:
        sessionUserId = await get_userId_from_token(session)
    except HTTPException:
        print("Invalid Token")
        return RedirectResponse(url='/login', status_code=307)
    if (SocialDatabase().is_login_user_admin(sessionUserId) == False):
        print("User not admin")
        return RedirectResponse(url='/login', status_code=307)
    found_user = app.database["authors"].find_one({"_id": sessionUserId})
    if found_user:
        return templates.TemplateResponse("admin-landing.html", {"request": request, "user": found_user})
    else:
        return RedirectResponse(url="/login")
# Example of how we would get current user from cookie to verify action being done


@app.get("/admin-users")
async def get_admin_users(request: Request, session: str = Cookie(None)):
    if (session == None):
        return RedirectResponse(url="/login")
    try:
        sessionUserId = await get_userId_from_token(session)
    except HTTPException:
        print("Invalid Token")
        return RedirectResponse(url='/login', status_code=307)
    if (SocialDatabase().is_login_user_admin(sessionUserId) == False):
        print("User not admin")
        return RedirectResponse(url='/login', status_code=307)
    found_user = app.database["authors"].find_one({"_id": sessionUserId})
    if found_user:
        return templates.TemplateResponse("admin-users.html", {"request": request, "user": found_user, "totalusers": SocialDatabase().get_total_users(), "users": SocialDatabase().get_all_authors_and_authormanagers_combined()})
    else:
        return RedirectResponse(url="/login")


@app.get("/admin-node")
async def get_admin_node(request: Request, session: str = Cookie(None)):
    if (session == None):
        return RedirectResponse(url="/login")
    try:
        sessionUserId = await get_userId_from_token(session)
    except HTTPException:
        print("Invalid Token")
        return RedirectResponse(url='/login', status_code=307)
    if (SocialDatabase().is_login_user_admin(sessionUserId) == False):
        print("User not admin")
        return RedirectResponse(url='/login', status_code=307)
    found_user = app.database["authors"].find_one({"_id": sessionUserId})
    if found_user:
        return templates.TemplateResponse("admin-node.html", {"request": request, "user": found_user, "current": "localhost:8000"})
    else:
        return RedirectResponse(url="/login")
# Example of how we would get current user from cookie to verify action being done


@app.get("/admin-posts")
async def get_admin_posts(request: Request, session: str = Cookie(None)):
    if (session == None):
        return RedirectResponse(url="/login")
    try:
        sessionUserId = await get_userId_from_token(session)
    except HTTPException:
        print("Invalid Token")
        return RedirectResponse(url='/login', status_code=307)
    if (SocialDatabase().is_login_user_admin(sessionUserId) == False):
        print("User not admin")
        return RedirectResponse(url='/login', status_code=307)
    found_user = app.database["authors"].find_one({"_id": sessionUserId})
    posts = SocialDatabase().get_all_posts()

    if found_user:
        return templates.TemplateResponse("admin-posts.html", {"request": request, "user": found_user, "posts": posts, "desc": "All "})
    else:
        return RedirectResponse(url="/login")


@app.get("/admin-specific-user/{user_id}")
async def get_admin_specific_user(request: Request, user_id: str, session: str = Cookie(None)):
    if (session == None):
        return RedirectResponse(url="/login")
    try:
        sessionUserId = await get_userId_from_token(session)
    except HTTPException:
        print("Invalid Token")
        return RedirectResponse(url='/login', status_code=307)
    if (SocialDatabase().is_login_user_admin(sessionUserId) == False):
        print("User not admin")
        return RedirectResponse(url='/login', status_code=307)
    found_user = app.database["authors"].find_one({"_id": sessionUserId})
    found_author = app.database["authors"].find_one({"_id": user_id})
    if found_user:
        return templates.TemplateResponse("admin-posts.html", {"request": request, "user": found_user, "posts": SocialDatabase().get_all_author_posts(user_id), "desc": "User '" + found_author["displayName"]+"' :"})
    else:
        return RedirectResponse(url="/login")


@app.get("/admin-modify-user/{user_id}")
async def get_admin_specific_user(request: Request, user_id: str, session: str = Cookie(None)):
    if (session == None):
        return RedirectResponse(url="/login")
    try:
        sessionUserId = await get_userId_from_token(session)
    except HTTPException:
        print("Invalid Token")
        return RedirectResponse(url='/login', status_code=307)
    if (SocialDatabase().is_login_user_admin(sessionUserId) == False):
        print("User not admin")
        return RedirectResponse(url='/login', status_code=307)
    found_user = app.database["authors"].find_one({"_id": sessionUserId})
    found_author = app.database["authors"].find_one({"_id": user_id})
    if found_user:
        return templates.TemplateResponse("admin-mod-user.html", {"request": request, "user": found_user, "author": found_author})
    else:
        return RedirectResponse(url="/login")


@app.get("/admin-modify-post/{post_id}")
async def get_admin_specific_user(request: Request, post_id: str, session: str = Cookie(None)):
    if (session == None):
        return RedirectResponse(url="/login")
    try:
        sessionUserId = await get_userId_from_token(session)
    except HTTPException:
        print("Invalid Token")
        return RedirectResponse(url='/login', status_code=307)
    if (SocialDatabase().is_login_user_admin(sessionUserId) == False):
        print("User not admin")
        return RedirectResponse(url='/login', status_code=307)
    found_user = app.database["authors"].find_one({"_id": sessionUserId})
    found_post = SocialDatabase().get_post_by_id(post_id)
    if found_user:
        return templates.TemplateResponse("admin-mod-post.html", {"request": request, "user": found_user, "post": found_post})
    else:
        return RedirectResponse(url="/login")
# Example of how we would get current user from cookie to verify action being done


@app.get("/test")
async def rabdintest(request: Request):
    return SocialDatabase().get_all_author_posts("405702f1-2db1-4228-9f37-9d7871de5f2d")


@app.get("/examplejwt")
async def verify_jwt(session: str | None = Cookie(default=None)):
    if (session):
        try:
            payload = jwt.decode(session, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid Token")
        return {"message": "Valid Token", "user_Id": payload["_id"]}
    else:
        raise HTTPException(status_code=401, detail="Invalid Token")

# currently using hardcoded post value

 ## Testing PAGES ##


# @app.get("/landing", response_class=HTMLResponse)
# async def get_landing(request: Request):
#     foundAuthor = request.app.database["authors"].find({})
#     return templates.TemplateResponse("landing.html", {"request": request, "landing": foundAuthor[0]})


@app.get("/post", response_class=HTMLResponse)
async def get_post(request: Request, session: str = Cookie(None)):
    foundPosts = request.app.database["post"].find({})

    try:
        sessionUserId = await get_userId_from_token(session)
    except HTTPException:
        return RedirectResponse(url='/login', status_code=307)
    found_user = app.database["authors"].find_one({"_id": sessionUserId})
    print("*****************************",
          found_user, "*****************************")
    return templates.TemplateResponse("post.html", {"request": request, "user": found_user, "post": foundPosts[2], "information": {"name": "USER FEED"}})


@app.get("/posts", response_class=HTMLResponse)
async def get_all_posts(request: Request):
    post_cursor = app.database["post"].find({})
    all_posts = []
    for items in post_cursor:
        all_posts.append(items)
    return templates.TemplateResponse("all-posts.html", {"request": request, "posts": all_posts, "information": {"name": "USER FEED"}})


# @app.get("/authors/{author_id}")
# async def display_author(request: Request, response: Response, author_id: str):
#     author = authors.read_item(author_id, request)
#     response.set_cookie(key="author_id", value=author)
#     return templates.TemplateResponse("user-feed.html", {"request": request})


# @app.get("/author", response_class=HTMLResponse)
# async def get_post(request: Request):
#     foundAuthor = request.app.database["authors"].find({})
#     return templates.TemplateResponse("author.html", {"request": request, "post": foundAuthor[1]})


# currently everything is hardcoded. Just initial design
@app.get("/comments", response_class=HTMLResponse)
async def get_post(request: Request):
    return templates.TemplateResponse("comments.html", {"request": request})

# @app.get("/search/{author_displayName}")
# async def search_user(request: Request, author_displayName: str):
#     author_foud = request.app.database["authors"].find({"displayName":f"/{author_displayName}/"})
#     return templates.TemplateResponse("user-feed.html", {"request": request})

 ## END TEST PAGES ##
if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
