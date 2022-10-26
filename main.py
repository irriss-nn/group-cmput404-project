#!/usr/bin/env python3
import uvicorn
from fastapi import FastAPI, APIRouter, Request, Form, Response, HTTPException, Cookie
from datetime import datetime, timedelta
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pymongo import MongoClient
from re import template
from urllib import request
from jose import JWTError, jwt
from passlib.context import CryptContext

# Local imports
from routers import authors, posts, comments_router
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
            raise HTTPException(
                status_code=404, detail="User not found or Password Incorrect")
    else:
        raise HTTPException(
            status_code=404, detail="User not found or Password Incorrect")


def create_jwt(ecodeddata: dict):
    to_encode = ecodeddata.copy()
    expire = datetime.utcnow() + timedelta(minutes=45)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Use This function to get userId from jwt token
async def get_userId_from_token( token: str):
    try:
        if(token == None):
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
    app.mongodb_client = MongoClient("mongodb://localhost:27017")
    app.database = app.mongodb_client["socialnetwork"]
    print("Connected to MongoDB")


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


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
async def register_author(request: Request):
    return {"message": "register"}


@app.get("/posts", response_class=HTMLResponse)
async def get_all_posts(request: Request):
    post_cursor = app.database["post"].find({})
    all_posts = []
    for items in post_cursor:
        all_posts.append(items)
    return templates.TemplateResponse("all-posts.html", {"request": request, "posts": all_posts})

# To Do For Login:
# 1. Redirect User to proper page after login !!
# 2. Make use of hashing for passwords
# 3. Make sure that the user is not already logged in


@app.post("/login")
async def read_item(request: Request, response: Response, username: str = Form(), password: str = Form()):
    found_user = get_user(request, username, password)
    found_user.pop("hashedPassword", None)
    madeJWT = create_jwt(found_user)
    # store session cookie in key for future verification
    response = RedirectResponse(url="/current") # We need to delcare redirect before cookies and return response all totghet
    response.status_code = 302
    response.set_cookie(key="session", value=madeJWT)
    # We need to redirect to the user's page
    return response

@app.get("/current")
async def get_current_user(request: Request, session: str = Cookie(None)):
    if(session == None):
        return RedirectResponse(url="/login")
    sessionUserId = await get_userId_from_token(session) # must await for this!!
    found_user = app.database["authors"].find_one({"_id": sessionUserId})
    return templates.TemplateResponse("author.html", {"request": request, "post": found_user})


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
@app.get("/post", response_class=HTMLResponse)
async def get_post(request: Request):
    foundPosts = request.app.database["post"].find({})
    return templates.TemplateResponse("post.html", {"request": request, "post": foundPosts[2]})


@app.get("/authors/{author_id}")
async def display_author(request: Request, response: Response, author_id: str):
    author = authors.read_item(author_id, request)
    response.set_cookie(key="author_id", value=author)
    return templates.TemplateResponse("user-feed.html", {"request": request})


@app.get("/author", response_class=HTMLResponse)
async def get_post(request: Request):
    foundAuthor = request.app.database["authors"].find({})
    return templates.TemplateResponse("author.html", {"request": request, "post": foundAuthor[2]})


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
