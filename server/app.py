from fastapi import FastAPI, APIRouter
from pymongo import MongoClient
from .routers import authors

app = FastAPI()

@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient("mongodb://localhost:27017")
    app.database = app.mongodb_client["socialnetwork"]
    print("Connected to MongoDB")

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(authors.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}



