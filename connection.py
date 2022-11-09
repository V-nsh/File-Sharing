import pymongo
import gridfs

client = pymongo.MongoClient("mongodb+srv://Vansh:vriHNFIOd3TuANV5@cluster0.6qxzk0f.mongodb.net/test")
db = client.get_database('files')
fs = gridfs.GridFS(db)


users = db['users']
files = db['files']
messages = db['messages']
shares = db['shares']