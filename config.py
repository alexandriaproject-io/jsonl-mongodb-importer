from dotenv import load_dotenv
import os
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
RAW_COLLECTION = os.getenv("RAW_COLLECTION")
MAPPED_COLLECTION = os.getenv("MAPPED_COLLECTION")
