from flask import Flask, render_template, request,flash,Response
import pandas as pd
import csv
import re
from datetime import datetime
import json
import cv2
from flask import session
from werkzeug.utils import secure_filename
import sys
import os
import io
import base64
from DBConfig import DBConnection
import shutil
from random import randint
import numpy as np
from sendemail import sendEmail
from verification import fingerprint_Matching

from Prediction import face_recognition,predict,show_prediction_labels_on_image,train

app = Flask(__name__)
app.secret_key = "abc"




@app.route('/')
def index():
    return render_template('index.html')

@app.route("/user_login")
def user_login():
    return render_template("user_login.html")


@app.route("/userhome")
def userhome():
    return render_template("userhome.html")

@app.route("/user_reg")
def user_reg():
    return render_template("user_reg.html")


@app.route("/add_password")
def add_password():
    return render_template("add_passwords.html")

@app.route("/withdraw")
def withdraw():
    return render_template("withdraw.html")


@app.route("/user_reg2", methods=["GET", "POST"])
def user_reg2():
        try:
            name = request.form.get('name')
            uid = request.form.get('uid')
            pwd = request.form.get('pwd')
            mno = request.form.get('mno')
            email = request.form.get('email')
            image_file = request.files['file']
            imgdata = image_file.read()

            session['userid'] = uid

            database = DBConnection.getConnection()
            cursor = database.cursor()

            sql = "select count(*) from register where userid='" + uid + "' "
            cursor.execute(sql)
            res = cursor.fetchone()[0]
            if res > 0:

                return render_template("user_reg.html", msg="duplicate")


            else:
                encodestring = base64.b64encode(imgdata)
                query = "insert into register values(%s,%s,%s,%s,%s,%s)"
                values = (name, uid, pwd, email,mno, encodestring)
                cursor.execute(query, values)
                database.commit()
            return render_template("image_capture.html")
        except Exception as e:
            print(e)

        return ""


@app.route("/userlogin_check",methods =["GET", "POST"])
def userlogin_check():

        uid = request.form.get("unm")
        pwd = request.form.get("pwd")

        database = DBConnection.getConnection()
        cursor = database.cursor()
        cursor2 = database.cursor()
        sql = "select count(*) from register where userid='" + uid + "' and passwrd='" + pwd + "'"
        cursor.execute(sql)
        res = cursor.fetchone()[0]
        if res > 0:
            session['uid'] = uid

            sql2 = "select email from register where userid='" + uid + "' "
            cursor2.execute(sql2)
            email = cursor2.fetchone()[0]

            import random
            otp = random.randint(100,10000)

            session["OTP"]=otp

            otp_val="OTP Code:"+str(otp)

            sendEmail(email,"User Authentication",otp_val)

            return render_template("verification_OTP.html",msg="OTP sent to Registered Email address")
        else:

            return render_template("user_login.html", msg3="Invalid Credentials")

        return ""




@app.route("/verification2", methods=["GET", "POST"])
def verification2():
        try:

            image_file = request.files['file']
            imgdata = image_file.read()

            database = DBConnection.getConnection()
            cursor = database.cursor()

            uid=session['uid']

            sql = "select fingerprint_img from register where userid='" + uid + "' "
            cursor.execute(sql)
            imgdata2 = cursor.fetchone()[0]
            imgdata3 = base64.b64decode(imgdata2)

            with open("../PasswordsSecurity/test_images/testfg2.bmp", 'wb') as f2:
                f2.write(imgdata3)

            with open("../PasswordsSecurity/test_images/testfg1.bmp", 'wb') as f:
                f.write(imgdata)

            status=fingerprint_Matching("../PasswordsSecurity/test_images/testfg1.bmp", "../PasswordsSecurity/test_images/testfg2.bmp")

            if status:

                return render_template("userhome.html")  # Directly go to user dashboard

            else:

                return render_template("verification.html", msg="invalid")

        except Exception as e:
            print(e)

        return ""



@app.route("/store_password",methods =["GET", "POST"])
def store_password():

        website = request.form.get("website")

        passwrd = request.form.get("passwrd")

        uid = session['uid']
      


        database = DBConnection.getConnection()
        cursor = database.cursor()

        query = "insert into passwords values(%s,%s,%s)"
        values = (website,passwrd,uid)
        cursor.execute(query, values)
        database.commit()

        return render_template("add_passwords.html", msg="Done.")




@app.route("/view_passwords")
def view_passwords():
    try:
        uid = session['uid']
        database = DBConnection.getConnection()
        cursor = database.cursor()
        date_time=datetime.now()
        cursor.execute("SELECT *FROM passwords where userid='"+uid+"' " )
        records = cursor.fetchall()

    except Exception as e:
        print("Error=" + e.args[0])
        tb = sys.exc_info()[2]
        print(tb.tb_lineno)

    return render_template("view_passwords.html",records=records)








@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


def gen_frames():
    global camera
    camera = cv2.VideoCapture(0)
    while camera.isOpened():
        success, frame = camera.read()  # read the camera frame
        cv2.imwrite('cameraimg.jpg', frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result




@app.route("/save_details")
def save_details():
    camera.release()
    
    class_dir=session['userid']

    imgid = class_dir+".jpg"
    path = "../PasswordsSecurity/dataset/" + class_dir+ "/"
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    imgdata = read_file("cameraimg.jpg")
    write_file(imgdata, imgid, path)

    return render_template("user_login.html",msg="successfully..!")



@app.route("/verification_OTP",methods =["GET", "POST"])
def verification_OTP():

        otp = request.form.get("otp")
        otp2=session["OTP"]
        print(otp,otp2)

        if str(otp)==str(otp2):
            return render_template("verification.html")
        else:

            return render_template("verification_OTP.html",msg="Invalid OTP")




@app.route('/video_feed2')
def video_feed2():
    return Response(gen_frames2(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames2():
    global camera2
    camera2 = cv2.VideoCapture(0)
    while camera2.isOpened():
        success, frame = camera2.read()  # read the camera frame
        cv2.imwrite('../PasswordsSecurity/captured_Img/testimg.jpg', frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result





@app.route("/face_authenticate")
def face_authenticate():

    uid=session["uid"]

    camera2.release()
    print("Training KNN classifier...")
    classifier = train("../PasswordsSecurity/dataset", model_save_path="trained_knn_model.clf", n_neighbors=1)
    print("Training complete!")

    # STEP 2: Using the trained classifier, make predictions for unknown images
    for image_file in os.listdir("../PasswordsSecurity/captured_Img"):
        full_file_path = os.path.join("../PasswordsSecurity/captured_Img", image_file)

        print("Looking for faces in {}".format(image_file))

        # Find all people in the image using a trained classifier model
        # Note: You can pass in either a classifier file name or a classifier model instance
        predictions = predict(full_file_path, model_path="trained_knn_model.clf")

        # Print results on the console
        for user_id, (top, right, bottom, left) in predictions:
            print("user_id=", user_id)

            if user_id==uid:
                return render_template("userhome.html")
            else:
                return render_template("verification_face.html", msg="invalid")

    return ""





def read_file(filename):
        with open(filename, 'rb') as f:
            img = f.read()
        return img

def write_file(data, imgid, path):
        with open(path + imgid, 'wb') as f:
            f.write(data)


import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
