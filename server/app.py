from re import template
from urllib import request
from fastapi import FastAPI, APIRouter, Request
from pymongo import MongoClient
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .routers import authors, posts
from pathlib import Path

app = FastAPI()

BASE_PATH = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))

app.mount("/static", StaticFiles(directory=str(BASE_PATH.parent / "static")), name="static")
# templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient("mongodb://localhost:27017")
    app.database = app.mongodb_client["socialnetwork"]
    print("Connected to MongoDB")


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(authors.router)
app.include_router(posts.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/login", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_author(request: Request):
    
    return {"message": "register"}

@app.post("/login")
async def read_item(request: Request):
    return {"message": "login"}