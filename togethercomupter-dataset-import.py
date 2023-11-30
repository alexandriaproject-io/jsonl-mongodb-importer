from dotenv import load_dotenv
import os
from pymongo import MongoClient
# Load environment variables from .env file
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

print("Connecting to mongodb...")
client = MongoClient(MONGODB_URI)
db = client.get_default_database()

print("Connected to mongoDB and ready to work!")
