from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import os.path
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from random import randint
from flask import Flask,render_template,request
from datetime import datetime
from datetime import date
import sqlite3

import socket    
hostname = socket.gethostname()    
IPAddr = socket.gethostbyname(hostname)    


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

db_path = os.path.join(os.path.dirname(__file__),'database.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager() 
login_manager.init_app(app)
login_manager.login_view = 'login'


today = date.today()
now=datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class LoginForm(FlaskForm):
	username = StringField('username', validators=[InputRequired(), Length(min=4,max=15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8,max=80)])
	remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    

@app.route('/',methods=['GET', 'POST'])


def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user:
			login_user(user, remember=form.remember.data)
			if check_password_hash(user.password, form.password.data):
				return redirect(url_for('welcome'))
		return render_template('invalid.html',form = form,inc="Invalid Credential!! Try again...")

		# flash("Invalid Username or Password")

    

	return render_template('game.html',form = form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/')
    return render_template('signup.html',form=form)

@app.route('/welcome')
@login_required
def welcome():
    return render_template('playGame.html',ds=dt_string,ip=IPAddr)
@app.route('/withdraw')
def withdraw():
    return render_template('withdraw.html')


@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

@app.route('/game',methods=["GET","POST"])
def game():
    mon=5
    if request.method=="POST":
        new_str=dt_string
        r = randint(0,1) #generates either 0 or 1.  1 = 'heads'; 0 = 'tails'
        bet = int(request.form['bet'])
        if bet > mon:
            print ("\n[!] You don't have that much money!")  
        elif mon == 0:
            print ('\n[!] You are out of money!\n')
        else:
            hd = request.form['hd']
            print(hd)
            if (hd == 'heads' and r == 1) or (hd == 'tails' and r == 0):
                s='WON'
                print ('\n[!] You won!\n')
                mon += bet 
                new=mon
                print ('> You now have %s!\n' % (mon))
                print(new)

            elif (hd == 'heads' and r == 0) or (hd == 'tails' and r == 1):
                print ('\n[!] You lost...\n')
                s='LOSS'
                mon -= bet
                new=mon
                print ('> You now have %s!\n' % (mon))
                print(new)

            else:
                print ('\n[!] Please choose HEADS or TAILS\n')
    
            conn = sqlite3.connect('information.db')
            new_str=dt_string
            
            conn.execute('''CREATE TABLE IF NOT EXISTS stats
                            ( ID INTEGER PRIMARY KEY AUTOINCREMENT,AMOUNT INTEGER  NOT NULL,Date TEXT NOT NULL,FLIPPING INTEGER NOT NULL,RESULT TEXT NOT NULL,WALLET INTEGER NOT NULL)''')  
            
            
            conn.execute('INSERT or Ignore into stats(AMOUNT,Date,FLIPPING,RESULT,WALLET) VALUES(?,?,?,?,?)', (bet,dt_string,hd,s,new))
            conn.commit()  
            cursor = conn.execute("SELECT ID,AMOUNT,Date,FLIPPING,RESULT from stats") 
    
      
        return render_template('new.html',res=mon,ds=new_str,ip=IPAddr)
    return render_template('playGame.html',res=mon)

@app.route('/home')
def home_page():
    conn = sqlite3.connect('information.db')
    conn.row_factory = sqlite3.Row 
    cur = conn.cursor() 
    cursor = cur.execute("SELECT ID,AMOUNT,Date,FLIPPING,RESULT from stats") 
    rows=cur.fetchall()
    return render_template('form3.html',rows=rows)

if __name__=='__main__':
	app.run(debug=True)