from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_ 
from passlib.hash import pbkdf2_sha256
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = os.urandom(24)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(32), nullable=False)

class Flights(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(60), nullable=False)
    destination = db.Column(db.String(60), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    passenger = db.Column(db.String(80), db.ForeignKey(Users.fullname))
    
    
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        getEmail = request.form.get('email')
        getPassword = request.form.get('password')
        session["user"] = getEmail
        checkDB = Users.query.filter(Users.email==getEmail).first()
        if(getEmail=='' or getPassword==''):
            getEmail = None
            getPassword = None
            return 'All fields are required'
        if checkDB:
            if pbkdf2_sha256.verify(getPassword, checkDB.password):
                return redirect('/booking')
            else:
                return 'Incorrect Password'
        elif not checkDB:
            return 'User does not exist'
    return render_template('index.html', title='Trvlr')

@app.route('/booking')
def booking():
    if "user" in session:
        user = session["user"]
        return render_template('booking.html', title='Booking', logout='Log Out')
    else:
        return redirect('/')
@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/support')
def support():
    return render_template('support.html', title='Support')

@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        getFullname = request.form.get('fullname')
        getUsername = request.form.get('username')
        getEmail = request.form.get('email')
        getPassword = request.form.get('password')
        getCpassword = request.form.get('cpassword')
        checkDB = Users.query.filter(or_(Users.email==getEmail, Users.username==getUsername))
        if getPassword == getCpassword:
            hashed = pbkdf2_sha256.hash(getPassword)
        else:
            return 'Password do not match'
        if(getFullname=='' or getUsername=='' or getEmail =='' or getPassword =='' or getCpassword ==''):
            getFullname = None
            getUsername = None
            getEmail = None
            getPassword = None
            getCpassword = None
            return 'All fields are required'
        elif(checkDB):
            return 'User already exists'
        else:
            newUser = Users(fullname=getFullname, username=getUsername,
                            email=getEmail, password=hashed)
            db.session.add(newUser)
            db.session.commit()
    return render_template('signup.html', title='Sign Up')

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect('/')

if __name__=='__main__':
    app.run(debug=True)
