#!/usr/bin/env python3
from pprint import pprint
from routers import authors, posts, comments_router
import uvicorn
from datetime import datetime, timedelta
from fastapi import FastAPI, APIRouter, Cookie, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from jose import JWTError, jwt
from passlib.context import CryptContext
from models.author import Author
from models.author_manager import AuthorManager
# Local imports
from database import SocialDatabase
from routers import authors, posts, comments_router
from fastapi.encoders import jsonable_encoder
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

# Use This function to get userId from jwt token


async def get_userId_from_token(token: str):
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


@app.on_event("startup")
def startup_db_client():
    app.database = SocialDatabase().database
    print("Connected to MongoDB")


@app.on_event("shutdown")
def shutdown_db_client():
    SocialDatabase().close()


@app.get("/")
async def root():
    return RedirectResponse(url='/login')


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
    if(git == None or usnm == None or pswd == None): # Catch errors
        return RedirectResponse(url='/register')
    newUser = Author(displayName= usnm, github=git, hashedPassword = pswd) # To DO: Hash password
    # result = await SocialDatabase.add_author(newUser) # Use this when implemented
    ### TEMPORARY  MOVE TO DB FILE ###
    author = jsonable_encoder(newUser)
    author["posts"] = {}
    author["_id"] = author["id"]
    author.pop('id', None)
    if app.database["authors"].find_one({"_id": author["_id"]}):
        # return RedirectResponse(url='/login') # IF found redirect back to login
        return {"message": "User already exists"}
    app.database["authors"].insert_one(author)
    # We create a new author manager when creating a new author, assume if updating author, author manager already exists
    authm = jsonable_encoder(AuthorManager(owner=author["_id"]))
    authm["_id"] = authm["id"]
    authm.pop('id', None)
    app.database["authorManagers"].insert_one(authm)
    ### TEMPORARY ###
    return RedirectResponse('/login', status_code=status.HTTP_302_FOUND) # Automatically logs user in, maybe we want to change so they log in manually

@app.post("/login")
async def read_item(request: Request, response: Response, username: str = Form(), password: str = Form()):
    found_user = get_user(request, username, password)
    if found_user == None: # Return to login if bad password
        response = RedirectResponse(url="/login")
        response.status_code = 302
        response.delete_cookie(key="session")
        return response
    found_user.pop("hashedPassword", None)
    madeJWT = create_jwt(found_user)
    # store session cookie in key for future verification
    # We need to delcare redirect before cookies and return response all totghet
    response = RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
    response.status_code = 302
    response.set_cookie(key="session", value=madeJWT)
    # We need to redirect to the user's page
    return response

# For when we want to logout user and delete cookie
@app.post("/logout")
async def logout(request: Request, response: Response):
    response = RedirectResponse(url="/login")
    response.status_code = 302
    response.delete_cookie(key="session")
    return response

# To Do For Login:
# 1. Redirect User to proper page after login !!
# 2. Make use of hashing for passwords
# 3. Make sure that the user is not already logged in



@app.get("/current") # View current profile
async def get_current_user(request: Request, session: str = Cookie(None)):
    if (session == None):
        return RedirectResponse(url="/login")
    # must await for this!!
    sessionUserId = await get_userId_from_token(session)
    found_user = app.database["authors"].find_one({"_id": sessionUserId})
    return templates.TemplateResponse("author.html", {"request": request, "post": found_user})


 # Page user lands on
@app.get("/home")
async def get_home(request: Request, session: str = Cookie(None)):
    if (session == None):
        return RedirectResponse(url="/login")
    # must await for this!!
    sessionUserId = await get_userId_from_token(session)
    found_user = app.database["authors"].find_one({"_id": sessionUserId})
    ### TEMPORARY MOVE TO DATABASE FILE ###
    foundAuthMan = app.database["authorManagers"].find_one({"owner": sessionUserId})
    allCurrentUserFollowing = foundAuthMan["following"]
    all_feed_posts = []
    for following in allCurrentUserFollowing:
        # Get post of each following
        found_following = app.database["authors"].find_one({"_id": following})
        try:
            for post in found_following["posts"]:
                all_feed_posts.append(found_following["posts"][post])
        except:
            pass
    ### TEMPORARY ###

    pprint(all_feed_posts)
    return templates.TemplateResponse("landing.html", {"request": request, "landing": found_user,"feed": all_feed_posts})

# Example of how we would get current user from cookie to verify action being done
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
@app.get("/landing", response_class=HTMLResponse)
async def get_landing(request: Request):
    foundAuthor = request.app.database["authors"].find({})
    return templates.TemplateResponse("landing.html", {"request": request, "landing": foundAuthor[0]})


@app.get("/post", response_class=HTMLResponse)
async def get_post(request: Request):
    foundPosts = request.app.database["post"].find({})
    return templates.TemplateResponse("post.html", {"request": request, "post": foundPosts[2], "information": {"name": "USER FEED"}})

@app.get("/posts", response_class=HTMLResponse)
async def get_all_posts(request: Request):
    post_cursor = app.database["post"].find({})
    all_posts = []
    for items in post_cursor:
        all_posts.append(items)
    return templates.TemplateResponse("all-posts.html", {"request": request, "posts": all_posts, "information": {"name": "USER FEED"}})



@app.get("/authors/{author_id}")
async def display_author(request: Request, response: Response, author_id: str):
    author = authors.read_item(author_id, request)
    response.set_cookie(key="author_id", value=author)
    return templates.TemplateResponse("user-feed.html", {"request": request})


@app.get("/author", response_class=HTMLResponse)
async def get_post(request: Request):
    foundAuthor = request.app.database["authors"].find({})
    return templates.TemplateResponse("author.html", {"request": request, "post": foundAuthor[1]})


# currently everything is hardcoded. Just initial design
@app.get("/comments", response_class=HTMLResponse)
async def get_post(request: Request):
    return templates.TemplateResponse("comments.html", {"request": request})

 ## END TEST PAGES ##
if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
