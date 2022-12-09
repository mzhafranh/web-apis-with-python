from flask import Flask, request, render_template, redirect, jsonify, url_for
from flask_login import UserMixin, login_user, LoginManager,login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from functools import wraps
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pyotp
import datetime
import jwt
import requests

import mysql.connector
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="accidents"
)



app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/accidents'
app.config['SECRET_KEY'] = 'supersecretkey@$&*!'
# db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['JSON_SORT_KEYS'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "indexLogin"

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

class User(UserMixin):
    def __init__(self, userid, password):
        self.id = userid
        self.password = password

    @staticmethod
    def get(userid):
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM user WHERE id = %s", [userid])
        result = cursor.fetchall()
        if (len(result) > 0):
            return User(result[0][0], result[0][3])
        else:
            return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({"code" : 400, "status": "fail", "message" : "[ERROR] Token not found"})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({"code" : 400, "status": "fail", "message" : "[ERROR] Token invalid"})
        
        return f(*args, **kwargs)
    
    return decorated

class create_dict(dict): 

    # __init__ function 
    def __init__(self): 
        self = dict() 
        
    # Function to add key:value 
    def add(self, key, value): 
        self[key] = value


@app.post("/registerapi/")
def addUserAPI():
    email = request.args.get("email")
    username = request.args.get("username")
    password = request.args.get("password")
    role = request.args.get("role")

    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM user WHERE email = %s", [email])
    result = cursor.fetchall()
    if (len(result) > 0):
        return jsonify({"code" : 400, "status": "fail", "message" : "[ERROR] Email already registered!"}) 
    else:
        hashed_password = bcrypt.generate_password_hash(password)
        cursor.execute("INSERT INTO user (email, username, password, role) VALUES (%s, %s, %s, %s)", [email, username, hashed_password, role])
        mydb.commit() 
        return jsonify({"code" : 200, "status": "success", "message" : "[SUCCESS] Account succesfully created"})


@app.post("/loginapi/")
def userLoginAPI():
    email = request.args.get("email")
    password = request.args.get("password")

    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM user WHERE email = %s", [email])
    result = cursor.fetchall()
    if (len(result) > 0):
        if(bcrypt.check_password_hash(result[0][3],password)):
            token = jwt.encode({'user_id' : result[0][0], 'email' : result[0][1], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=10000)}, app.config['SECRET_KEY'])
            user = User.get(result[0][0])
            login_user(user)
            return jsonify({"code" : 200, "status": "success", "message":"[SUCCESS] Login Success", "Token" : str(token)})
        else:
            return jsonify({"code" : 400, "status": "fail", "message":"[ERROR] Invalid username or password"})
    else: 
        return jsonify({"code" : 400, "status": "fail", "message":"[ERROR] Invalid username or password"})


@app.post("/registerapiotp/")
def addUserAPIOTP():
    email = request.args.get("email")
    username = request.args.get("username")
    password = request.args.get("password")
    role = request.args.get("role")

    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM user WHERE email = %s", [email])
    result = cursor.fetchall()
    if (len(result) > 0):
        return jsonify({"code" : 400, "status": "fail", "message" : "[ERROR] Email already registered!"}) 
    else:
        hashed_password = bcrypt.generate_password_hash(password)
        cursor.execute("INSERT INTO user (email, username, password, role) VALUES (%s, %s, %s, %s)", [email, username, hashed_password, role])
        mydb.commit()
        otp_key = pyotp.random_base32()

        sender_address = "bukanjeprun@gmail.com"
        sender_pass = "ijvacbyiqhyvpobp"
        receiver_address = request.args.get("email")

        mail_content = f'''[Instructions]
Download google authenticator on your mobile
Create a new account with setup key method.
Provide the required details (name, secret key).
Select time-based authentication.
Submit this generated key in the form.
{otp_key}
'''
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'Your 2FA setup to Z-API' 

        message.attach(MIMEText(mail_content, 'plain'))

        session = smtplib.SMTP('smtp.gmail.com',587)
        session.set_debuglevel(1)
        session.starttls()
        session.login(sender_address, sender_pass)
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()

        return jsonify({"code" : 200, "status": "success", "message" : "[SUCCESS] Account succesfully created, Check your email for 2FA setup"})


@app.post("/loginapiotp/")
def userLoginAPIOTP():
    email = request.args.get("email")
    password = request.args.get("password")
    secret = request.args.get("secret")
    otp = int(request.args.get("otp"))

    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM user WHERE email = %s", [email])
    result = cursor.fetchall()
    if (len(result) > 0):
        if(bcrypt.check_password_hash(result[0][3],password)):
            if pyotp.TOTP(secret).verify(otp):
                token = jwt.encode({'user_id' : result[0][0], 'email' : result[0][1], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=20)}, app.config['SECRET_KEY'])
                user = User.get(result[0][0])
                login_user(user)        
                return jsonify({"code" : 200, "status": "success", "message":"[SUCCESS] Login success.", "Token" : str(token)})
            else:
                return jsonify({"code" : 400, "status": "fail", "message":"[ERROR] 2FA Failed"})
        else:
            return jsonify({"code" : 400, "status": "fail", "message":"[ERROR] Invalid username or password"})
    else: 
        return jsonify({"code" : 400, "status": "fail", "message":"[ERROR] Invalid username or password"})

@app.get("/email")
@login_required
def email():
    return render_template("email.html")

@app.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('indexLogin'))

@app.get("/report")
@login_required
@token_required
def searchReport():
    cursor = mydb.cursor()

    if request.args.get("startdate") and request.args.get("enddate"):

        reqstartdate = str(request.args.get("startdate"))
        reqenddate = str(request.args.get("enddate"))

        startdate = datetime.date(int(reqstartdate[:4]), int(reqstartdate[5:7]), int(reqstartdate[8:10]))
        enddate = datetime.date(int(reqenddate[:4]), int(reqenddate[5:7]), int(reqenddate[8:10]))
        enddate = enddate + datetime.timedelta(days=1)
        currdate = startdate

        statdict = create_dict()

        while (currdate != enddate):
            nextdate = currdate + datetime.timedelta(days=1)
            cursor.execute("SELECT * FROM report WHERE start_time BETWEEN %s AND %s", [currdate, nextdate])
            result = cursor.fetchall()
            severity_avg = 0
            for row in result:
                severity_avg += row[1]
            severity_avg = float(severity_avg / len(result))
            statdict.add(str(currdate), ({"date": str(currdate), "total accidents": len(result), "avg severity" : str(round(severity_avg, 2))}))
            currdate = nextdate

        cursor.execute("SELECT * FROM report WHERE start_time BETWEEN %s AND %s", [startdate, enddate])
        result = cursor.fetchall()
        datadict = create_dict()

        for row in result:
            datadict.add(row[0],({"id":row[0],"severity":row[1],"start_time":row[2],"county":row[14],"state":row[15]}))

        data = jsonify({"code":200, "status": "success", "statistic" : [statdict], "data": [datadict]})

        return (data)

    else:
        data = jsonify({"code":400, "status": "fail", "message": "Please specify startdate and enddate"})

        return (data)



@app.post("/reportadd/")
@login_required
@token_required
def addReport():
    cursor = mydb.cursor()

    id = request.args.get("id")
    severity = int(request.args.get("severity"))
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    start_lat = float(request.args.get("start_lat"))
    start_lng = float(request.args.get("start_lng"))
    end_lat = float(request.args.get("end_lat"))
    end_lng = float(request.args.get("end_lng"))

    query = ("INSERT INTO report VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
    values = (id, severity, start_time, end_time, start_lat, start_lng, end_lat, end_lng)
    
    cursor.execute(query, values)

    mydb.commit()

    return jsonify({"code" : 200, "status": "successs", "message":"[SUCCESS] Record inserted"})

@app.delete("/reportdel/")
@login_required
@token_required
def deleteReport():
    cursor = mydb.cursor()

    id = str(request.args.get("id"))

    cursor.execute("DELETE FROM report WHERE id LIKE %s", [id])

    mydb.commit()

    return jsonify({"code" : 200, "status": "successs", "message":"[SUCCESS] Record has been deleted"})

@app.put("/reportedit/")
@login_required
@token_required
def editReport():
    cursor = mydb.cursor()

    new_id = request.args.get("new_id")
    severity = int(request.args.get("severity"))
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    start_lat = float(request.args.get("start_lat"))
    start_lng = float(request.args.get("start_lng"))
    end_lat = float(request.args.get("end_lat"))
    end_lng = float(request.args.get("end_lng"))
    old_id = request.args.get("old_id")

    query = ("UPDATE report SET id = %s, severity = %s, start_time = %s, end_time = %s, start_lat = %s, start_lng = %s, end_lat = %s, end_lng = %s WHERE id = %s")
    values = (new_id, severity, start_time, end_time, start_lat, start_lng, end_lat, end_lng, old_id)
    
    cursor.execute(query, values)

    mydb.commit()

    return jsonify({"code" : 200, "status": "successs", "message":"[SUCCESS] Record updated"})

@app.post("/array/")
def testArray():
    start_lats = list((request.args.get("start_lat")).split(","))
    start_lngs = list((request.args.get("start_lng")).split(","))
    end_lats = list((request.args.get("end_lat")).split(","))
    end_lngs = list((request.args.get("end_lng")).split(","))
    coords = []
    for i in range (len(start_lats)):
        coords.append((float(start_lats[i]),float(start_lngs[i]),float(end_lats[i]),float(end_lngs[i])))
    return (coords)

# @app.get("/register")
# def indexRegister():
#     return render_template("register.html")

# @app.post("/register/")
# def addUser():
#     email = request.form.get("email")
#     username = request.form.get("username")
#     password = request.form.get("password")
#     role = request.form.get("role")

#     cursor = mydb.cursor()
#     cursor.execute("SELECT * FROM user WHERE email = %s", [email])
#     result = cursor.fetchall()
#     if (len(result) > 0):
#         return "[ERROR] Email sudah terdaftar" 
#     else:
#         hashed_password = bcrypt.generate_password_hash(password)
#         cursor.execute("INSERT INTO user (email, username, password, role) VALUES (%s, %s, %s, %s)", [email, username, hashed_password, role])
#         mydb.commit() 
#         return redirect(url_for('indexLogin'))

# @app.get("/login")
# def indexLogin():
#     return render_template("login.html")

# @app.post("/login/")
# def userLogin():
#     email = request.form.get("email")
#     password = request.form.get("password")

#     cursor = mydb.cursor()
#     cursor.execute("SELECT * FROM user WHERE email = %s", [email])
#     result = cursor.fetchall()
#     if (len(result) > 0):
#         if(bcrypt.check_password_hash(result[0][3],password)):
#             token = jwt.encode({'user_id' : result[0][0], 'email' : result[0][1], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)}, app.config['SECRET_KEY'])
#             user = User.get(result[0][0])
#             login_user(user)
#             # return redirect(f"/?token={token}")

#             sender_address = "bukanjeprun@gmail.com"
#             sender_pass = "ijvacbyiqhyvpobp"
#             receiver_address = result[0][1]

#             mail_content = f'''Hello,
# This is your access token to Z-API

# localhost:5000/?token={token}

# Thank You for using our service.
# '''
#             message = MIMEMultipart()
#             message['From'] = sender_address
#             message['To'] = receiver_address
#             message['Subject'] = 'Your token to Z-API' 

#             message.attach(MIMEText(mail_content, 'plain'))

#             try:
#                 session = smtplib.SMTP('smtp.gmail.com',587)
#                 session.set_debuglevel(1)
#                 session.starttls()
#                 session.login(sender_address, sender_pass)
#                 text = message.as_string()
#                 session.sendmail(sender_address, receiver_address, text)
#                 session.quit()
#                 print('email has been sent')
#             except:
#                 print('email could not be sent')

#             return redirect(url_for('email'))

#         else:
#             return jsonify({"code" : 400, "status": "fail", "message":"[ERROR] Invalid username or password"})
#     else: 
#         return jsonify({"code" : 400, "status": "fail", "message":"[ERROR] Invalid username or password"})


if __name__ == "__main__":
    app.run()
