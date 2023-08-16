from __future__ import division, print_function
from flask import Flask,render_template,request,redirect,url_for
from flask_mail import Mail,Message
from flask_mysqldb import MySQL

# coding=utf-8
import sys
import os
import glob
import re
import numpy as np
import tensorflow as tf
import tensorflow as tf

from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

config = ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.2
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)
# Keras
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Flask utils
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '_root1234'
app.config['MYSQL_DB'] = 'user'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'shubhanshum154@gmail.com'
app.config['MAIL_PASSWORD'] = 'jyhluxobrfrxstfy'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

MODEL_PATH ='model.h5'

# Load your trained model
model = load_model(MODEL_PATH)
mysql = MySQL(app)



def model_predict(img_path, model):
    print(img_path)
    img = image.load_img(img_path, target_size=(224, 224))

    # Preprocessing the image
    x = image.img_to_array(img)
    # x = np.true_divide(x, 255)
    ## Scaling
    x=x/255
    x = np.expand_dims(x, axis=0)
   

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
   # x = preprocess_input(x)

    preds = model.predict(x)
    preds=np.argmax(preds, axis=1)
    if preds==0:
        preds="cat"
    elif preds==1:
        preds="dog"
    elif preds == 2:
        preds="Not identified"
    
    
    
    return preds



@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='GET':
        return render_template('base.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='GET':
        return render_template('register.html')
    else:
        Name=request.form.get('name')
        Password=request.form.get('password')
        reenter=request.form.get('re-enter')
        Email=request.form.get('email')
        
        Contact=request.form.get('contact')
        Uid = int(100)
        random="111"
        mylist = "**Required"
        if  not Name :
            return render_template('register.html',mylist = mylist)
        if  not Email :
            return render_template('register.html',mylist1 = mylist)
        if  not Password :
            return render_template('register.html',mylist2 = mylist)
        elif len(Password) < 8:
            return render_template('register.html',mylist2 = "Password Must be 8 Digit")
        if  not reenter :
            return render_template('register.html',mylist3 = mylist)
        if Password !=reenter:
            return render_template('register.html',mylist5 = mylist)
        if  not Contact :
            return render_template('register.html',mylist4 = mylist)
        else:
            try:
                Contact=int(Contact)
            except ValueError:
                return render_template('register.html',mylist4 = "Invalid")
        
        cur = mysql.connection.cursor()
        sql = 'INSERT INTO register(Uid,Name,Password,contact,Email,random) VALUES (%s,%s,%s,%s,%s,%s);'
        cur.execute(sql,(Uid,Name,Password,Contact,Email,random))
        mysql.connection.commit()
        
        return render_template('register_s.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
       return render_template('login.html')
    else:
        username=request.form.get('username')
        password=request.form.get('password')
        email=request.form.get('email')
        if not username:
            return render_template('login.html',mylist = "**Required")
        elif not username:
            return render_template('login.html',mylist1 = "**Required")
        elif not email:
            return render_template('login.html',mylist2 = "**Required")
        cur = mysql.connection.cursor()
        sql_query=f"""SELECT * FROM register WHERE Name='{username}' AND Password='{password}'"""
        cur.execute(sql_query)
        results=cur.fetchall()
        cur.close()
        if not results:
            return render_template('login.html',mylist3 = "**Invalid Credentials")
        return render_template('sucess.html',mylist=results)
        
@app.route('/login_Secure/<int:Contact>',methods=['GET','POST'])
def edit_student(Contact):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT * FROM register WHERE Contact={Contact} ")
        info_results=cur.fetchall()[0]
        cur.close()
        return render_template('image.html',mylist=info_results)
    else:
        img = request.files['my_image']
        problem=request.form.get('problem')
        if not img:
            return "Image not found"
        img.filename = str(Contact)
        img_path = "images/"+img.filename+".jpeg"
        ui='name'
        img.save(img_path)
        # f=img.filename+'1'+ui
        preds = model_predict(img_path, model)
        status1 = "ON"
        result=preds
        dict ={'status':'ON'}
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT * FROM register WHERE Contact={Contact} ")
        info_results1=cur.fetchall()[0]
        sql_query = f"""SELECT email FROM query WHERE problem='{result}' ;"""
        cur.execute(sql_query)
        email=cur.fetchall()
        cur.close()
        
        cur = mysql.connection.cursor()
        sql=f"""UPDATE query SET status='{result}'"""
        cur.execute(sql)
        result1 = cur.fetchall()
        cur.close()
        new=email[0]
        
        for i in email:
            new=i[0]
        ema = "shubhanshum154@gmail.com"
        
        msg = Message("name", sender = 'shubhanshum154@gmail.com', recipients = [new])
        
        msg.body = "Name",info_results1[1],'Contact' , str(info_results1[3]), 'Email' , (info_results1[4])
        msg.subject=str(problem)
        src=img_path
        with app.open_resource(src) as fp:
                msg.attach(src, src, fp.read())
        
        mail.send(msg)
       
        return render_template('new.html', mylist = email )
    
    return None
        
@app.route("/about/Shubhanshu_Mishra",methods=['GET'])
def about_shubhanshu():
    return render_template("/about/about_shubhanshu.html")

@app.route("/about/Sourabh",methods=['GET'])
def about_Sourabh():
    return render_template("/about/about_Sourabh.html")

@app.route("/about/Tushar",methods=['GET'])
def about_Tushar():
    return render_template("/about/about_Tushar.html")

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('base.html',mylist = "Error 404"), 404

@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('base.html',mylist = "Error 500"), 500
@app.errorhandler(401)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('base.html',mylist = "Error 401"), 401





if __name__ == "__main__":
     app.run(debug=True ,port=5000,use_reloader=False)