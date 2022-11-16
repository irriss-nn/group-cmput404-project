from fastapi import APIRouter, HTTPException, Request, status, Body
from models.comments import Comment
from models.inbox import InboxItem
from models.like import Like
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from pathlib import Path
from database import SocialDatabase
from pprint import pprint
import json

static_dir = f"{Path.cwd()}/static"
templates = Jinja2Templates(directory=f"{static_dir}/templates")

router = APIRouter(
    prefix="/service/authors/likes",
    tags=["likes"],
    responses={404: {"description": "Not found method"}},
)

@router.post("/create/{author_id}/post/{post_id}")
async def create_like_and_send_to_author_inbox(request: Request, author_id: str, post_id: str):
    status = SocialDatabase().like_post( post_id, author_id)
    
    return status
    
@router.post("/create/{author_id}/comment/{comment_id}")
async def create_like_and_send_to_author_inbox_comment(request: Request, author_id: str, comment_id: str):
    status = SocialDatabase().like_comment(comment_id, author_id)
    return status
