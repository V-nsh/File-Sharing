import pymongo
import gridfs

client = pymongo.MongoClient("mongodb+srv://Vansh:vriHNFIOd3TuANV5@cluster0.6qxzk0f.mongodb.net/test")
db = client.get_database('files')
fs = gridfs.GridFS(db)

client1 =  pymongo.MongoClient('mongodb+srv://psi:8008@cluster0.vxiaxuw.mongodb.net/test')
db1 = client1.get_database('files1')
fs1 = gridfs.GridFS(db1)

files1 = db1['files1']

users = db['users']
files = db['files']
messages = db['messages']
codeReq = db['codeReq']
grants = db['codeGrant']
judge = db['judgement']