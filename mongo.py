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


def count_dataset_size(dataset_id):
    query = {"datasetId": ObjectId(dataset_id)}

    # Count the documents
    return db[config.MAPPED_COLLECTION].count_documents(query)


def get_dataset_cursor(dataset_id):
    query = {"datasetId": ObjectId(dataset_id)}
    return db[config.MAPPED_COLLECTION].find(query)


def create_new_job(dataset_id, dataset_row, type, target, sources, status='new', tool='default'):
    row_id = str(dataset_row.get('_id'))
    job_data = {
        'datasetId': ObjectId(dataset_id),
        'jobHash': generate_sha256_hash(f"{dataset_id}-{row_id}-{type}-{target}-{sources}"),
        'datasetRowId': ObjectId(row_id),
        'type': type,
        'target': target,
        'sources': sources,
        'status': status,
        'tool': tool
    }
    result = db[config.JOBS_COLLECTION].insert_one(job_data)

    return (
        str(result.inserted_id),
        {
            'jobId': str(result.inserted_id),
            'datasetId': dataset_id,
            'datasetRowId': row_id,
            'type': type,
            'target': target,
            'sources': sources,
            'tool': tool
        })


def delete_job(job_id):
    db[config.JOBS_COLLECTION].delete_one({"_id": ObjectId(job_id)})


def set_job_queued(job_id):
    db[config.JOBS_COLLECTION].update_one(
        {"_id": ObjectId(job_id)},  # Query to match the document
        {"$set": {"status": "queued"}}  # Update operation
    )
