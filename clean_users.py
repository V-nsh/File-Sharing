import pymongo

#WARNING: THIS WILL DELETE EVERY USER FROM THE DATABASE, MAKE SURE TO CLEAN FILES AFTER THIS
#          TO AVOID ANY MISMATCH IN DATA

client = pymongo.MongoClient("mongodb+srv://Vansh:vriHNFIOd3TuANV5@cluster0.6qxzk0f.mongodb.net/test")
db = client.get_database('files')
users = db['users']

users.delete_many({})