from genericpath import exists
from tempfile import tempdir
from connection import db, users, files, fs, messages, shares
from flask import Flask, render_template, request, redirect, url_for
import smtplib
import math, random
from bson.objectid import ObjectId
import os

uid = ""
currPID = ''
umail = ''
uname = ''
upass = ''
otp = ''
currFile = ''

print(db)

app = Flask(__name__)

# to verify repeating emails
def checkuser(mail):
    if(users.find_one({'email':mail})):
        return True
    else:
        return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    global currPID
    print(request.method)
    if request.method == 'POST':
        mail =  request.form.get('email')
        print(mail)
        # TODO: Add a no such email found for login.
        if(checkuser(mail)): #Check if user is present in the db 
            passw = request.form.get('upass')
            udata = users.find_one({'email': mail})
            print(udata)
            if(udata):
                if(udata['password'] == passw):
                    currPID = udata['_id']
                    return render_template('home.html')
                else:
                    err = 'wrong password'
                    return render_template('login.html', logerr = err)
            else:
                return render_template('login.html', uerr = 'No such email found!')
    return render_template('login.html')

def generateOTP() :
 
    # Declare a string variable 
    # which stores all string
    string = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    OTP = ""
    length = len(string)
    for i in range(6) :
        OTP += string[math.floor(random.random() * length)]
 
    return OTP

@app.route('/sendMail', methods=['GET', 'POST'])
def sendMail():
    global otp
    server = smtplib.SMTP_SSL('smtp.gmail.com')
    server.login("vaprohit707@gmail.com", "yrxbmclscuqibiyl") #Make a formal email later
    otp = generateOTP()
    print(otp)
    message = f"{otp}" #add a formal message
    server.sendmail("vaprohit707@gmail.com", umail, message)
    server.quit()
    return redirect(url_for("verify"))

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    global currPID
    if request.method=='POST':
        totp =  request.form.get("otp")
        print(totp)
        if(otp == totp):
            doc = users.insert_one({
                'name': uname,
                'email': umail,
                'password': upass,
            })
            currPID = doc.inserted_id
            # files  =  files.find()
            return render_template('home.html')
        else:
            err = 'Incorrect OTP!'
            return render_template('signup.html', oterr = err)
    return render_template("otp.html", name = uname)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    global umail
    global uname
    global upass
    email= request.form.get('umail')
    pass1 = request.form.get('upass')
    pass2 = request.form.get('upass1')
    print(f"email:{email}")
    print(pass1)
    if request.method=='POST':
        if(not checkuser(email)):
            if(pass1==pass2):
                uname = request.form.get('uname')
                umail = email
                upass = pass1
                return redirect(url_for("sendMail"))
            else:
                wrongpass = 'The password do not match! Please enter again!'
                return render_template('signup.html', perr = wrongpass)
        else:
            exist='User with that email already exists!'
            return render_template('signup.html', exist = exist)
        
    return render_template('signup.html')

@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/insert', methods=['GET', 'POST'])
def insert():
    global uid
    print(request.method)
    if request.method == 'POST':
        fi = request.files['text_f']
        print(fi)
        uid = fs.put(fi)
        foo = fi.filename
        doc = {
            "user" : currPID,
            "filename": foo,
            "file_id": uid
        }
        files.insert_one(doc)
    return render_template('home.html')

@app.route('/download', methods=['GET','POST'])
def download():
    if request.method == 'POST':
        global uid
        print(request.form.get("file"))
        uid = request.form.get('file')
        uid  = ObjectId(uid)
        print(uid)
        target = files.find_one({"file_id": ObjectId(uid)})
        out = fs.get(uid).read()
        
        # path = os.path.join('C:/secur-e-share', target["filename"])
        if not os.path.exists('C:/secur-e-share'):
            os.makedirs('C:/secur-e-share')

        path = os.path.join('C:/secur-e-share', target["filename"])
        output = open(path, "wb")

        output.write(out)
        output.close()

        return render_template("home.html")
    return render_template("home.html")

# a page to show files of current user
@app.route('/My-files', methods=['GET', 'POST'])
def myFiles():
    print(currPID)
    f = files.find({'user': currPID})
    return render_template('myFiles.html', data = f)

@app.route('/routeFetch', methods=['GET', 'POST'])
def routeFetch():
    fileID = request.args.get('fileID')
    return redirect(url_for('fetchFile', fileID=fileID)) #find the file id and show it to the user

@app.route('/fetchFile/<fileID>', methods=['GET', 'POST'])
def fetchFile(fileID):
    # this function should be associated with a small button below the file name.
    # TODO: get file id from the file cluster, use it to download the file 
    #       using the download() function.
    # First try without using form, use form if it doesn't work.
    global currFile
    print(fileID)
    if(fileID):
        currFile = fileID
        print(currPID)
        f = files.find({'user': currPID})
        return render_template('myFiles.html', code = fileID, data = f)
    
    return render_template('myFiles.html')

@app.route('/send-files')
def findFile():
    file = request.args.get('fileID')
    return redirect(url_for('search_user', file = file))


@app.route('/search_user/<file>', methods=['GET', 'POST'])
def search_user(file):
    # data = users.find({ "_id": { "$nin" :{'currPID'} }})
    # TODO: EXCLUDE THE CURRECT USER AND FIX SEARCH BAR
    data = users.find()
    return render_template('users.html', data = data, file = file)

@app.route('/route-code')
def route_code():
    receiver = request.args.get('user')
    file = request.args.get('file')
    print(receiver)
    return redirect(url_for('send_code', receiver= receiver, file = file))

@app.route('/send_code/<receiver>/<file>')
def send_code(receiver, file):
    code = generateOTP()
    doc  = messages.insert_one({
        'file_id': file,
        'from' : currPID,
        'to' : receiver,
        'code': code
    })
    if(doc.inserted_id):
        msg = "Code successfully sent!"
    data = users.find()
    return render_template('users.html', msg = msg, data = data)


@app.route('/messages')
def showMessages():
    print(currPID)
    print(type(currPID))
    print(messages.find({'to':currPID}))
    if(messages.find({'to': currPID})):
        # query = { "to": {"$eq": currPID} }
        data = messages.find({'to': str(currPID)})
        return render_template('messages.html', data = data)

@app.route('/get_file')
def get_file():
    file = request.args.get('fid')
    return redirect(url_for('download_file', fid = file))

@app.route('/download_file/<fid>')
def download_file(fid):
    target = files.find_one({"file_id": ObjectId(fid)})
    out = fs.get(ObjectId(fid)).read()
        
    if not os.path.exists('C:/secur-e-share'):
        os.makedirs('C:/secur-e-share')

    path = os.path.join('C:/secur-e-share', target["filename"])
    output = open(path, "wb")

    output.write(out)
    output.close()
    return redirect(url_for('showMessages'))

if __name__=="__main__":
    app.run(debug = True)