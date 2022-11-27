from fastapi import APIRouter, HTTPException, Request, status, Body, Cookie
from models.comments import Comment
from models.inbox import InboxItem
from models.like import Like
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from pathlib import Path
from database import SocialDatabase
from pprint import pprint
import json
from jose import JWTError, jwt

SECRET_KEY = 'f015cb10b5caa9dd69ebeb340d580f0ad37f1dfcac30aef8b713526cc9191fa3'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

static_dir = f"{Path.cwd()}/static"
templates = Jinja2Templates(directory=f"{static_dir}/templates")
router = APIRouter(
    prefix="/service/authors/likes",
    tags=["likes"],
    responses={404: {"description": "Not found method"}},
)

async def get_userId_from_token(token: str):
    try:
        if (token == None):
            raise HTTPException(status_code=401, detail="Unauthorized")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userId: str = payload.get("_id")
        return userId
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/create/{author_id}/post/{post_id}")
async def create_like_and_send_to_author_inbox(request: Request, author_id: str, post_id: str):
    status = SocialDatabase().like_post(post_id, author_id)

    return status

@router.post("/create/{author_id}/comment/{comment_id}")
async def create_like_and_send_to_author_inbox_comment(request: Request, author_id: str, comment_id: str):
    status = SocialDatabase().like_comment(comment_id, author_id)
    return status

@router.post("/create/post/{post_id}")
async def create_like_and_send_to_author_inbox(request: Request, post_id: str, session: str = Cookie(None)):

    try:
        author_id = await get_userId_from_token(session)
    except HTTPException:
        return RedirectResponse(url='/login', status_code=307)
    status = SocialDatabase().like_post(post_id, author_id)
    return status

@router.post("/create/comment/{comment_id}")
async def create_like_and_send_to_author_inbox(request: Request, comment_id: str, session: str = Cookie(None)):

    try:
        author_id = await get_userId_from_token(session)
    except HTTPException:
        return RedirectResponse(url='/login', status_code=307)
    status = SocialDatabase().like_comment(comment_id, author_id)
    return status
