#!/usr/bin/env python3
import uvicorn
from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pymongo import MongoClient
from re import template
from urllib import request

# Local imports
from routers import authors, posts

app = FastAPI()

static_dir = f"{Path.cwd()}/static"
templates = Jinja2Templates(directory=f"{static_dir}/templates")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(authors.router)
app.include_router(posts.router)


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


@app.get("/post", response_class=HTMLResponse)
async def get_post(request: Request):
    foundPosts = request.app.database["post"].find({})
    return templates.TemplateResponse("post.html", {"request": request, "post": foundPosts[5]})


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
