import pymongo
import gridfs

client = pymongo.MongoClient("mongodb+srv://Vansh:vriHNFIOd3TuANV5@cluster0.6qxzk0f.mongodb.net/test")
db = client.get_database('files')

users = db['users']
files = db['files']
# grid = db['grid']

# upload
fs = gridfs.GridFS(db)

with open(b"test_pdf.pdf", "rb") as f:
    uid = fs.put(f)


# download
out = fs.get(uid).read()
outf ="test2.pdf"
output = open(outf, "wb")

output.write(out)
output.close()

print(uid)