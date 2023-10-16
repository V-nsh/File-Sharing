import math
import os
import random
import smtplib

from bson.objectid import ObjectId
from flask import Flask, redirect, render_template, request, url_for

from connection import codeReq, db, files, fs, grants, judge, messages, users, fs1, files1, db1

judgement = '636cf95c1c51efab4163d475'
judgement = ObjectId(judgement)
uid = ""
currPID = ''
umail = ''
uname = ''
upass = ''
otp = ''
currFile = ''
fid = ''

app = Flask(__name__)

@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    li = list(users.find({ '_id': currPID}, {"name.$": 1}))
    li1 = list(users.find({ '_id': currPID}, {"email.$": 1}))
    name = li[0]['name']
    mail = li1[0]['email']
    return render_template('profile.html', name = name, mail = mail)

# to verify repeating emails
def checkuser(mail):
    if(users.find_one({'email':mail})):
        return True
    else:
        return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    global currPID
    if request.method == 'POST':
        mail =  request.form.get('email')
        # TODO: Add a no such email found for login.
        if(checkuser(mail)): #Check if user is present in the db 
            passw = request.form.get('upass')
            udata = users.find_one({'email': mail})
            if(udata):
                if(udata['password'] == passw):
                    currPID = udata['_id']
                    li2 = list(judge.find({ '_id': judgement}, {"success.$": 1}))
                    li3 = list(judge.find({ '_id': judgement}, {"detects.$": 1}))
                    success = li2[0]['success']
                    detects = li3[0]['detects']
                    return render_template('index.html', success = success, detects = detects)
                else:
                    err = 'wrong password'
                    return render_template('login.html', logerr = err)
            else:
                return render_template('login.html', uerr = 'No such email found!')
    return render_template('login.html')

def generateOTP() :
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
    message = f"{otp}" #add a formal message
    server.sendmail("vaprohit707@gmail.com", umail, message)
    server.quit()
    return redirect(url_for("verify"))

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    global currPID
    if request.method=='POST':
        totp =  request.form.get("otp")
        if(otp == totp):
            doc = users.insert_one({
                'name': uname,
                'email': umail,
                'password': upass,
            })
            currPID = doc.inserted_id
            return render_template('index.html')
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

@app.route('/Shared-Files')
def shared_files():
    shared = grants.find({'from': currPID})
    return render_template('shared.html', data = shared)

@app.route('/Received-Files')
def received_file():
    received = list(grants.find({'to': str(currPID)}))
    return render_template('received.html', data = received)

# generate key
hash_table = {'1': 'y23vcd&6',
              '2': 'b7*34$)-',
              '3': '*&6yr$Z0',
              '4': '#@AyU*9|',
              '5': '%43@WzK-',
              '6': '^Rv!+OQj',
              '7': '4Rw&*mL^',
              '8': 'L)[|u$E,',
              '9': '([0UIzxP',
              '0': '#iCd$4Mo',
              }


def get_alph(key):
    return hash_table[key]


def encrypt_code(otp):

    # each sentence becomes an element in the list l
    output = ''
    for i in range(0, len(otp)):
        output += get_alph(otp[i])
    return output


def getotp():
    string = '012'
    otp = ""
    length = len(string)
    for i in range(3):
        otp += string[math.floor(random.random() * length)]
    return otp


def get_key(val):
    for key, value in hash_table.items():
        if val == value:
            return key


def decrypt_key(otp):
    output=""
    l=otp
    for i in range(0,len(otp),8):
        output+=get_key(l[i:i+8])
    ans=int(output)
    return ans

def Encrypt_file(data):
    s_key=getotp()
    key=int(s_key)
    
    data = bytearray(data)
    data1 = []
    for index, value in enumerate(data):
        data1.append(value ^ key)
    e_key=encrypt_code(s_key)
    print(type(data1))
    return [data1,e_key]

@app.route('/insert', methods=['GET', 'POST'])
def insert():
    global uid
    if request.method == 'POST':
        fi = request.files['text_f']
        # data = request.files['text_f'].read()
        # new = open(fi.filename, "wb")
        # new.write(data)
        # new.close
        # li = Encrypt_file(data)
        # print(li)
        # fi IS THE FILE WE ARE TAKING AS INPUT
        # -------ENCRYPT HERE-------------------------------------------------------------
        # code1 = li[1]
        uid = fs.put(fi)
        # enc = str(li[0]) 
        # uid1 = fs1.put(enc, encoding = 'utf-8')
        foo = fi.filename
        doc = {
            "user" : currPID,
            "filename": foo,
            "file_id": uid,
            # JUST REUSING THE GENERATEOTP TEMPORARLIY
            # INSERT THE CODE HERE AFTER "code": ____,
            # INSERT THE ENCRYPTED CODE
            # --------------INSERT ENCRYPTED CODE------------------------------------------
            "code": generateOTP(),
            "flag": 1
        }
        # doc1 = {
        #     "user" : currPID,
        #     "filename": foo,
        #     "file_id": uid1,
        #     # JUST REUSING THE GENERATEOTP TEMPORARLIY
        #     # INSERT THE CODE HERE AFTER "code": ____,
        #     # INSERT THE ENCRYPTED CODE
        #     # --------------INSERT ENCRYPTED CODE------------------------------------------
        #     "code": enc,
        #     "flag": 1
        # }
        # files1.insert_one(doc1)
        files.insert_one(doc)
    return render_template('home.html')

@app.route('/request-code')
def request_code():
    user =  request.args.get('user')
    fileID = request.args.get('fid')
    li = list(files.find({ 'file_id': ObjectId(fileID)}, { "filename.$": 1}))
    filename = li[0]['filename']
    doc = codeReq.insert_one({
        'file_id': request.args.get('fid'),
        'from': user,
        'to': currPID,
        'filename': filename
    })
    if(doc.inserted_id):
        sent = 'Request sent!'
    else:
        sent = 'Oops there was some error, please try again later.'
    return render_template('messages.html', sent = sent)

@app.route('/send-code')
def sendCode():
    global code
    fileID = request.args.get('fid')
    li = list(files.find({ 'file_id': ObjectId(fileID)}, {"code.$": 1}))
    li1 = list(files.find({ 'file_id': ObjectId(fileID)}, {"filename.$": 1}))
    code = li[0]['code']
    filename = li1[0]['filename']
    grants.insert_one({
        'code': code,
        'file': fileID,
        'to': request.args.get('to'),
        'from': currPID,
        'filename': filename
    })
    existing = list(files.find({ 'file_id': ObjectId(fileID)}, {"flag.$": 1}))
    existing = int(existing[0]['flag'])
    files.update_one({'file_id': ObjectId(fileID)},
    {"$set":{
        'flag': 0
    }}, upsert=False)
    codeSent = 'Code sent to the user.'
    return render_template('messages.html', codeSent = codeSent)

@app.route('/download', methods=['GET','POST'])
def download():
    if request.method == 'POST':
        global uid
        uid = request.form.get('file')
        uid  = ObjectId(uid)
        target = files.find_one({"file_id": ObjectId(uid)})
        out = fs.get(uid).read()
        
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
    if(fileID):
        currFile = fileID
        f = files.find({'user': currPID})
        return render_template('myFiles.html', code = fileID, data = f)
    
    return render_template('myFiles.html')

@app.route('/send-files')
def findFile():
    file = request.args.get('fileID')
    return redirect(url_for('search_user', file = file))


@app.route('/search_user/<file>', methods=['GET', 'POST'])
def search_user(file):
    # TODO: EXCLUDE THE CURRENT USER AND FIX SEARCH BAR
    data = users.find()
    return render_template('users.html', data = data, file = file)

@app.route('/route-code')
def route_code():
    receiver = request.args.get('user')
    file = request.args.get('file')
    return redirect(url_for('send_code', receiver= receiver, file = file))

@app.route('/send_code/<receiver>/<file>')
def send_code(receiver, file):
    li = list(files.find({ 'file_id': ObjectId(file)}, {"filename.$": 1}))
    filename = li[0]['filename']
    doc  = messages.insert_one({
        'file_id': file,
        'from' : currPID,
        'to' : receiver,
        'filename': filename
    })
    if(doc.inserted_id):
        msg = "Code successfully sent!"
    data = users.find()
    return render_template('users.html', msg = msg, data = data)


@app.route('/messages')
def showMessages():
    if(messages.find({'to': currPID}) or codeReq.find({'from': currPID}) or grants.find({'to': currPID})):
        grs = grants.find({'to': str(currPID)})
        reqs = codeReq.find({'from': str(currPID)}) 
        data = messages.find({'to': str(currPID)})
        return render_template('messages.html', data = data, reqs = reqs, grs = grs)
    return render_template('messages.html', msg = 'No messages here!')


# THIS IS USED TO REDIRECT TO VERIFY.HTML WITH THE CURRENT FILE AS GLOBAL
# KEPT IT GLOBAL SO THAT WE CAN USE IT IN THE AUTHENTICATE FUNCTION LATER
@app.route('/redirect-auth')
def redirect_auth():
    global fid
    fid = request.args.get('fid')
    return render_template('verify.html', fid = fid)

# THIS FUNCTION IS MADE SUCH THAT IT WILL VERIFY THE INPUT CODE AND FILE'S GENERATED CODE
# IF THE VALUES DON'T MATCH OR IF THE FLAG IS STILL 1, USER IS NOT ALLOWED TO DOWNLOAD
@app.route('/authenticate', methods = ['GET', 'POST'])
def authenticate():
    if request.method == 'POST':
        inputCode = request.form.get('code')
        li = list(files.find({ 'file_id': ObjectId(fid)}, {"flag.$": 1}))
        li1 = list(files.find({ 'file_id': ObjectId(fid)}, {"code.$": 1}))
        li2 = list(judge.find({ '_id': judgement}, {"detects.$": 1}))
        # THE BELOW CODE THAT WE ARE FETCHING WILL BE ENCRYPTED
        # SO DECRYPT THE CODE HERE
        # ---------------DECRYPT CODE--------------------------
        code = li1[0]['code']
        flag = li[0]['flag']
        currentDetects = li2[0]['detects']
        currentDetects = currentDetects+1      
        if (inputCode == code):
            if (flag == 1):
                flg = 'The code was not shared!'
                judge.update_one({'_id': judgement},
                {'$set':{
                    'detects': currentDetects
                }})
                return render_template('home.html', flg = flg)
                # THIS IS WHERE WE ARE PREVENTING DATA LEAKS
                # IF THE CODE IS CORRECT BUT THE FLAG IS STILL 1, THIS IS A CASE OF DATA LEAK
                # INCREMENT THE COUNT OF DATA LEAK PREVENTED HERE
            return redirect(url_for('download_file', fid = fid))
        return render_template('home.html', msg = 'Incorrect Code!')
    return render_template('verify.html')

@app.route('/get_file')
def get_file():
    file = request.args.get('fid')
    return redirect(url_for('download_file', fid = file))

# THIS WILL DOWNLOAD THE FILE IN THE SECURESHARE FOLDER
# AND RESET THE FLAG FOR THAT FILE TO 1
# IF YOU REACH THIS STAGE, IT MEANS A SUCCESSFUL TRANSFER WAS DONE
# SO CREATE AND INCREASE THE SUCCESS COUNTER HERE
@app.route('/download_file/<fid>')
def download_file(fid):
    target = files.find_one({"file_id": ObjectId(fid)})
    li2 = list(judge.find({ '_id': judgement}, {"success.$": 1}))
    out = fs.get(ObjectId(fid)).read()
    # OUT IS THE OUTPUT FILE, DECRYPT IS BEFORE DOWNLOADING 
    # --------------------DECRYPT HERE---------------------
    if not os.path.exists('C:/file-sharing'):
        os.makedirs('C:/file-sharing')

    path = os.path.join('C:/file-sharing', target["filename"])
    output = open(path, "wb")

    output.write(out)
    output.close()
    success = li2[0]['success']
    success = success+1
    print(success)
    judge.update_one({'_id': judgement},
                {'$set':{
                    'success': success
                }})
    files.update_one({'file_id': ObjectId(fid)},
    {"$set":{
        'flag': 1
    }}, upsert=False)
    return redirect(url_for('showMessages'))

if __name__=="__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
    # app.run(debug = True)