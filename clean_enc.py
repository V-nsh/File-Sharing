import pymongo
import gridfs

# WARNING: THIS WILL CLEAR ALL THE FILES IN OUR DATABASE, USE ONLY IN DEVELOPMENT

client = pymongo.MongoClient("mongodb+srv://psi:8008@cluster0.vxiaxuw.mongodb.net/test")
db = client.get_database('files1')
fs = gridfs.GridFS(db)

files = db['files1']

# delete everything in file cluster
files.delete_many({})

# Finds and deletes all the files in gridfs
for i in fs.find():
    fs.delete(i._id)