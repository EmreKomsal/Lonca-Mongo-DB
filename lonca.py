import pymongo

# Connect to the database

connection = pymongo.MongoClient("mongodb://localhost/27017")

if connection:
    print("Connected successfully!!!")
else:
    print("Could not connect to MongoDB")