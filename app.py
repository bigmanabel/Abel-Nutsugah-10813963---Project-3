from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
from passlib.hash import pbkdf2_sha256
import os
from datetime import datetime
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = os.urandom(24)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return '<User {}>'.format(self.id)


class Flights(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(60), nullable=False)
    destination = db.Column(db.String(60), nullable=False)
    departing_date = db.Column(db.Date, default=datetime, nullable=False)
    returning_date = db.Column(db.Date, default=datetime)
    cabin_class = db.Column(db.String(20), nullable=False)
    ticket_type = db.Column(db.String(20), nullable=False)
    passenger = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return '<Flight {}>'.format(self.id)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        getEmail = request.form.get('email')
        getPassword = request.form.get('password')
        checkDB = Users.query.filter(Users.email == getEmail).first()
        session["user"] = checkDB.fullname
        if(getEmail == '' or getPassword == ''):
            getEmail = None
            getPassword = None
            return 'All fields are required'
        if checkDB:
            if pbkdf2_sha256.verify(getPassword, checkDB.password):
                return redirect('/user')
            else:
                return 'Incorrect Password'
        elif not checkDB:
            return 'User does not exist'
    return render_template('index.html', title='Trvlr')


@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        getFullname = request.form.get('fullname')
        getEmail = request.form.get('email')
        getPassword = request.form.get('password')
        getCpassword = request.form.get('cpassword')
        checkDB = Users.query.filter(Users.email == getEmail).first()
        if getPassword == getCpassword:
            hashed = pbkdf2_sha256.hash(getPassword)
        else:
            return 'Password do not match'
        if(getFullname == '' or getEmail == '' or getPassword == '' or getCpassword == ''):
            getFullname = None
            getEmail = None
            getPassword = None
            getCpassword = None
            return 'All fields are required'
        elif(checkDB):
            return 'User already exists'
        else:
            newUser = Users(fullname=getFullname,
                            email=getEmail, password=hashed)
            db.session.add(newUser)
            db.session.commit()
            return redirect('/')
    return render_template('signup.html', title='Sign Up')


@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        getOrigin = request.form.get('origin')
        getDestination = request.form.get('destination')
        getDeparting = datetime.strptime(
            request.form.get('departing'), '%Y-%m-%d').date()
        getReturning = datetime.strptime(
            request.form.get('returning'), '%Y-%m-%d').date()
        getCabin = request.form.get('cabin')
        getTicket = request.form.get('ticket') 
        flightID = random.randint(10000,99999)
        newBooking = Flights(id=flightID, origin=getOrigin, destination=getDestination, departing_date=getDeparting,
                             returning_date=getReturning, cabin_class=getCabin, ticket_type=getTicket, passenger=session["user"])
        db.session.add(newBooking)
        db.session.commit()
        return redirect('/user')
    return render_template('booking.html', title='Booking', logout='Log Out')

@app.route('/delete/<int:id>')
def delete(id):
    booking = Flights.query.get(id)
    try:
        db.session.delete(booking)
        db.session.commit()
        return redirect('/user')
    except:
        return 'Error'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    flight = Flights.query.get(id)

    if request.method == 'POST':
        flight.origin = request.form['origin']
        flight.destination = request.form['destination']
        flight.departing_date = datetime.strptime(request.form['departing'], '%Y-%m-%d').date()
        flight.returning_date = datetime.strptime(request.form['returning'], '%Y-%m-%d').date()
        flight.cabin_class = request.form['cabin']
        flight.ticket_type = request.form['ticket']

        db.session.commit()
        return redirect('/user')
    return render_template('update.html', flight=flight, title='Update')

@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/support')
def support():
    return render_template('support.html', title='Support')


@app.route('/user')
def user():
    if "user" in session:
        user = session["user"]
        flights = Flights.query.filter(Flights.passenger == session["user"]).all()
        return render_template('user.html', flights=flights, logout='Log Out', title=user)
    else:
        return redirect('/')



@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
