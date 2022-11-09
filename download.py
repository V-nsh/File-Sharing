import pymongo
import gridfs
from bson.objectid import ObjectId

client = pymongo.MongoClient("mongodb+srv://Vansh:vriHNFIOd3TuANV5@cluster0.6qxzk0f.mongodb.net/test")
db = client.get_database('files')

users = db['users']
files = db['files']
# grid = db['grid']

# upload
fs = gridfs.GridFS(db)
id = ObjectId('633d558dae7311a271a7f1bb')
out = fs.get(id).read()
outf ="CC-lion.png"
output = open(outf, "wb")

output.write(out)
output.close()

print(id)