from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from os import environ

load_dotenv()


try:
    mongo_url = environ.get("MONGODB_URL")
    mongo_client = MongoClient(mongo_url) if mongo_url else MongoClient()
    db = mongo_client["state-sponsored"]
except Exception as e:
    print(e)
    print("Could not connect to database")
    exit()


def get_collection(name: str) -> Collection:
    return db[name]
