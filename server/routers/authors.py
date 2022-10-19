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
        authors = list(request.app.database["authors"].find(limit=size,skip=page*size))
    print(author.Author)
    return authors

@router.post("/",status_code=status.HTTP_201_CREATED, response_model=author.Author)
async def create_author(request: Request, author: author.Author = Body(...)):
    author = jsonable_encoder(author)
    new_author = request.app.database["authors"].insert_one(author)
    created_author = request.app.database["authors"].find_one(
        {"_id": new_author.inserted_id}
    )
    return create_author


@router.get("/{author_id}")
async def read_item(author_id: str, request: Request):
    request.app.database["authors"].find_one({"id": author_id})
    return { "author_id": author_id}
