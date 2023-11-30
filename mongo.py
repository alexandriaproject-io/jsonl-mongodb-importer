from pymongo import MongoClient
from bson import ObjectId
import hashlib
import config

client = MongoClient(config.MONGODB_URI)
db = client.get_default_database()

def generate_sha256_hash(input_string):
    # Encode the string to bytes
    input_bytes = input_string.encode()

    # Create a SHA256 hash object
    sha256_hash = hashlib.sha256()

    # Update the hash object with the bytes
    sha256_hash.update(input_bytes)

    # Get the hexadecimal representation of the hash
    hex_hash = sha256_hash.hexdigest()

    return hex_hash

def insert_data(dataset_id, raw_json_string, remapped_data):
    raw_json_id = insert_raw_data(dataset_id, raw_json_string)
    # to keep sanity and ability to insert partial data we re-remap again
    return insert_mapped_data(dataset_id, raw_json_id, remapped_data)


def insert_mapped_data(dataset_id, raw_json_id, remapped_data):
    mapped_data = {
        'datasetId': ObjectId(dataset_id),
        "rawJsonId": ObjectId(raw_json_id),
        "systemMessage": remapped_data.get('systemMessage', ''),
        "contextMessages": remapped_data.get('contextMessages', []),
        "state": remapped_data.get('state', 'new'),
        "seriesPosition": remapped_data.get('seriesPosition', 0),
        "messages": []
    }

    # Iterate through messages in remapped_data, applying defaults as needed
    for message in remapped_data.get('messages', []):
        mapped_message = {
            "provider": message.get('provider', 'segment'),  # Default 'segment'
            "message": message.get('message', '')  # Default empty string
        }
        mapped_data["messages"].append(mapped_message)

    result = db[config.MAPPED_COLLECTION].insert_one(mapped_data)
    return str(result.inserted_id)


def insert_raw_data(dataset_id, raw_json_string):
    raw_data = {
        'datasetId': ObjectId(dataset_id),
        'rawJsonString': raw_json_string,
        'rawJsonHash': generate_sha256_hash(raw_json_string)
    }
    result = db[config.RAW_COLLECTION].insert_one(raw_data)

    return str(result.inserted_id)
