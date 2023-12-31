from dotenv import load_dotenv
import os
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
RAW_COLLECTION = os.getenv("RAW_COLLECTION")
MAPPED_COLLECTION = os.getenv("MAPPED_COLLECTION")
JOBS_COLLECTION = os.getenv("JOBS_COLLECTION")


RABBIT_QUEUE_NAME = os.getenv("RABBIT_QUEUE_NAME")
RABBIT_USERNAME = os.getenv("RABBIT_USERNAME")
RABBIT_PASSWORD = os.getenv("RABBIT_PASSWORD")
RABBIT_HOST = os.getenv("RABBIT_HOST")
RABBIT_PORT = os.getenv("RABBIT_PORT")
RABBIT_QUEUE_EXCHANGE = os.getenv("RABBIT_QUEUE_EXCHANGE")
