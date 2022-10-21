from fastapi import APIRouter, Depends, HTTPException, Request, Body, status
from ..models import author
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/service/authors",
    tags=["author"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def read_authors(request: Request,page: int| None = None, size: int | None = None):
    if(page is None or size is None):
        authors = list(request.app.database["authors"].find(limit=100))
    else:
        authors = list(request.app.database["authors"].find().sort("_id",1).skip(( ( page - 1 ) * size ) if page > 0 else 0).limit(size))
    return authors

@router.post("/")
async def create_author(request: Request, author: author.Author = Body(...)):
    author = jsonable_encoder(author)
    author["_id"] = author["id"]
    author.pop('id', None)
    if request.app.database["authors"].find_one({"_id": author["_id"]}):
        request.app.database["authors"].update_one({"_id": author["_id"]}, {"$set":author})
    else:
        request.app.database["authors"].insert_one(author)


@router.get("/{author_id}")
async def read_item(author_id: str, request: Request):
    request.app.database["authors"].find_one({"id": author_id})
    return { "author_id": author_id}
