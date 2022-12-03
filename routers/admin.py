from fastapi import APIRouter, HTTPException, Request, status, Cookie
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from database import SocialDatabase
from models.author import Author
from models.inbox import InboxItem
import uuid
from jose import JWTError, jwt
static_dir = f"{Path.cwd()}/static"
templates = Jinja2Templates(directory=f"{static_dir}/templates")
router = APIRouter(
    prefix="/service/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def verify_admin(request: Request, session: str = Cookie(None)):
    return verify_user_is_admin_from_token(session)


@router.post("/{user_id}/approve")
async def approve_user(request: Request, user_id: str, session: str = Cookie(None)):
    # if(verify_user_is_admin_from_token(session)):
    #     SocialDatabase().approve_user(user_id)
    #     return RedirectResponse(url="/service/admin", status_code=303)
    # else:
    #     raise HTTPException(status_code=401, detail="Unauthorized")

    user = SocialDatabase().get_author(user_id)
    if (user.authLevel == "user" or user.authLevel == "admin"):
        raise HTTPException(status_code=400, detail="User is already approved")
    return SocialDatabase().approve_author(user_id)


@router.delete("/{user_id}")
async def delete_user(request: Request, user_id: str, session: str = Cookie(None)):
    # if(verify_user_is_admin_from_token(session)):
    #     SocialDatabase().delete_author(user_id)
    #     return RedirectResponse(url="/service/admin", status_code=303)
    # else:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    return SocialDatabase().delete_author(user_id)


@router.post("/modify/{user_id}")
async def modify_user(request: Request, user_id: str, session: str = Cookie(None)):
    # if(verify_user_is_admin_from_token(session)):
    #     SocialDatabase().delete_author(user_id)
    #     return RedirectResponse(url="/service/admin", status_code=303)
    # else:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    form_data = await request.form()
    form_data = dict(form_data)
    return SocialDatabase().update_author_using_fields(form_data.get("displayName"), form_data.get("github"), form_data.get("hashedPassword"), form_data.get("authLevel"), form_data.get("profileImage"), user_id)


@router.post("/modify/post/{post_id}")
async def modify_post(request: Request, post_id: str, session: str = Cookie(None)):
    # if(verify_user_is_admin_from_token(session)):
    #     SocialDatabase().delete_author(user_id)
    #     return RedirectResponse(url="/service/admin", status_code=303)
    # else:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    form_data = await request.form()
    form_data = dict(form_data)
    print(form_data)
    return SocialDatabase().update_post_using_fields(form_data.get("title"), form_data.get("content"), form_data.get("contentType"), form_data.get("description"), form_data.get("visibility"), form_data.get("unlisted"), post_id, form_data.get("authorId"))


@router.delete("/post/{post_id}/{author_id}")
async def delete_post(request: Request, post_id: str, author_id: str, session: str = Cookie(None)):
    # if(verify_user_is_admin_from_token(session)):
    #     SocialDatabase().delete_author(user_id)
    #     return RedirectResponse(url="/service/admin", status_code=303)
    # else:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    return SocialDatabase().delete_post(author_id, post_id)
SECRET_KEY = 'f015cb10b5caa9dd69ebeb340d580f0ad37f1dfcac30aef8b713526cc9191fa3'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def verify_user_is_admin_from_token(token: str):
    try:
        if (token == None):
            raise HTTPException(status_code=401, detail="Unauthorized")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userId: str = payload.get("_id")
        theUser = SocialDatabase().get_author(userId)
        if (theUser.authLevel != 'admin'):
            raise False
        return True
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
