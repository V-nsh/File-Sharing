import pymongo
import gridfs

# WARNING: THIS WILL CLEAR ALL THE FILES IN OUR DATABASE, USE ONLY IN DEVELOPMENT

client = pymongo.MongoClient("mongodb+srv://Vansh:vriHNFIOd3TuANV5@cluster0.6qxzk0f.mongodb.net/test")
db = client.get_database('files')
fs = gridfs.GridFS(db)

files = db['files']

# delete everything in file cluster
files.delete_many({})

# Finds and deletes all the files in gridfs
for i in fs.find():
    fs.delete(i._id)