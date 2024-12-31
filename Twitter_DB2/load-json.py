import json
import sys
from pymongo import MongoClient, InsertOne

if len(sys.argv) != 3:
    # input must be in the form python3 load-json.py <json file> <port number>
    print("Missing arguments: json-file port-number!")
    sys.exit(1)

json_file_path = sys.argv[1] # first argument = json file path
 
mongo_port = int(sys.argv[2]) # second argument = port number

client = MongoClient(f"mongodb://localhost:{mongo_port}")
database_name = "291db"
collection_name = "tweets"
database = client[database_name] #creating the database by the name 291db

if collection_name in database.list_collection_names(): 
    # if it is already there, then drop
    database.drop_collection(collection_name)


collection = database[collection_name]

collection.create_index([("content", "text")])

# Creating indexes for 'user.displayname' and 'user.location' fields
collection.create_index([("user.displayname", 1)])
collection.create_index([("user.location", 1)])
# Creating indexes for the collection
# collection.create_index([("id", 1)], unique=True)
# collection.create_index([("user.id", 1)])

batch_size = 10000
bulk_operations = []

with open(json_file_path, 'r') as file:
    for line in file:
        try:
            data = json.loads(line)
            bulk_operations.append(InsertOne(data))

            # Execute bulk write when the batch size is reached
            if len(bulk_operations) == batch_size:
                collection.bulk_write(bulk_operations)
                bulk_operations = []  # Clear the bulk operations

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

# Perform the final bulk write for any remaining documents
if bulk_operations:
    collection.bulk_write(bulk_operations)

client.close()
