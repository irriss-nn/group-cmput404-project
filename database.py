import pymongo
from pymongo import MongoClient

class Database:
    def __init__(self, database) -> None:
        self.database = database

    def insertAuthor(self, data):
        mycol = self.database["author"]
        
        mycol.insert_one(data)
