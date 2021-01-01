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
import razorpay
import socket    
hostname = socket.gethostname()    
IPAddr = socket.gethostbyname(hostname)    


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

db_path = os.path.join(os.path.dirname(__file__),'headortails.db')
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
class Withdraw(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    withdraw = db.Column(db.Integer)
    active_user=db.Column(db.String(120),nullable=False)


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
				return redirect('/welcome')
		return render_template('invalid.html',form = form,inc="Invalid Credential!! Try again...")

		# flash("Invalid Username or Password")

    

	return render_template('game.html',form = form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        email=request.form.get('email')
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/')
    return render_template('sign.html')

# @app.route('/welcome')

# def welcome():
#     new=0
#     active_user=current_user.username
#     connection = sqlite3.connect("headortails.db")
#     cursor = connection.cursor()
#     cursor.execute('SELECT sum(amount) FROM payment where active_user=?',(active_user,))
#     results = cursor.fetchall()
#     # print(results[0])
#     for pay in results:
#         my_wallet=pay[0]
        
#     return render_template('playGame.html',ds=dt_string,ip=IPAddr,res=my_wallet)
@app.route('/withdraw')
def withdraw():
    active_user=current_user.username
    connection = sqlite3.connect("headortails.db")
    cursor = connection.cursor()
    cursor.execute('SELECT withdraw FROM withdraw order by id desc limit 1')
    results=cursor.fetchall()
    for result in results:
        bet=result[0]
        print(type(bet))
    return render_template('withdraw.html',results=bet)
class Stats(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    amount=db.Column(db.Integer,nullable=False)
    date=db.Column(db.String(120),nullable=False)
    flipping=db.Column(db.String(120),nullable=False)
    active_user=db.Column(db.String(120),nullable=False)
    result=db.Column(db.String(120),nullable=False)
    wallet=db.Column(db.Integer,nullable=False)


@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

@app.route('/welcome',methods=["GET","POST"])
def game():
    active_user=current_user.username
    connection = sqlite3.connect("headortails.db")
    cursor = connection.cursor()
    cursor.execute('SELECT sum(amount) FROM payment where active_user=?',(active_user,))
    results = cursor.fetchall()
    # print(results[0])
    for pay in results:
        my_wallet=pay[0]
    bet=0
    active_user=current_user.username
    connection = sqlite3.connect("headortails.db")
    cursor = connection.cursor()
    cursor.execute('SELECT sum(amount) FROM payment where active_user=?',(active_user,))
    results = cursor.fetchall()
    for pay in results:
        my_wallet=pay[0]
        last_wallet=my_wallet
    new_str=dt_string
    if request.method=="POST" and current_user.is_authenticated: 
        
        r = randint(0,1) #generates either 0 or 1.  1 = 'heads'; 0 = 'tails'
        bet = int(request.form['bet'])
        if bet > my_wallet:
            print ("\n[!] You don't have that much money!")  
        elif my_wallet == 0:
            print ('\n[!] You are out of money!\n')
        else:
            hd = request.form['hd']
            new_bet=bet
            # print(hd)
            if (hd == 'heads' and r == 1) or (hd == 'tails' and r == 0):
                s='WON'
                # print ('\n[!] You won!\n')
                my_wallet += bet 
                bet=bet
              
            elif (hd == 'heads' and r == 0) or (hd == 'tails' and r == 1):
                print ('\n[!] You lost...\n')
                s='LOSS'
                my_wallet -= bet
                bet=-bet

            else:
                print ('\n[!] Please choose HEADS or TAILS\n')
            
            new_str=dt_string
            print(active_user)
            user=Stats(amount=bet,date=dt_string,flipping=hd,active_user=active_user,wallet=my_wallet,result=s)
            db.session.add(user)
            db.session.commit()
        return render_template('new.html',res=my_wallet,ds=new_str,ip=IPAddr,wallet=last_wallet,dg=bet,mybet=new_bet)

    active_user=current_user.username
    print(active_user)
    connection = sqlite3.connect("headortails.db")
    cursor = connection.cursor()
    cursor.execute('SELECT sum(amount) FROM stats where active_user=?',(active_user,))
    results = cursor.fetchall()
    for result in results:
        print(result[0])
    try:
        final_wallet=my_wallet+result[0]
        user=Withdraw(withdraw=final_wallet,active_user=active_user)
        db.session.add(user)
        db.session.commit()
        return render_template('playGame.html',res=final_wallet,ds=dt_string,ip=IPAddr)
    except:
        return render_template('playGame.html',res=my_wallet,ds=dt_string,ip=IPAddr)

@app.route('/home')
def home_page():
    if current_user.is_authenticated:
        conn = sqlite3.connect('headortails.db')
        conn.row_factory = sqlite3.Row 
        cur = conn.cursor() 
        cursor = cur.execute("SELECT ID,AMOUNT,Date,FLIPPING,RESULT,WALLET,active_user from stats") 
        rows=cur.fetchall()
        return render_template('form3.html',rows=rows)

class Payment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(120),nullable=False)
    username=db.Column(db.String(120),nullable=False)
    amount=db.Column(db.String(120),nullable=False)
    active_user=db.Column(db.String(120),nullable=False)
    


@app.route('/add',methods=['GET','POST'])
def hello():
    if current_user.is_authenticated:
        active_user=current_user.username
        if request.method=="POST":
            email=request.form.get('email')
            username=request.form.get('username')
            amount=request.form.get('amount')
            user=Payment(email=email,username=username,amount=amount,active_user=active_user)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('pay',id=user.id))

    return render_template('payment.html')
@app.route('/pay/<id>',methods=['GET','POST'])
def pay(id):
    user=Payment.query.filter_by(id=id).first()
    client=razorpay.Client(auth=("rzp_test_pQ6vOVhgjH2X8K","uTyrej8CdKIf6lzgll8VYAmJ"))
    payment=client.order.create({'amount': (int(user.amount)*100),'currency':'INR','payment_capture':'1'})
    return render_template('RazorPay.html',payment=payment)

@app.route('/success',methods=['GET','POST'])
def success():
    if current_user.is_authenticated:
        active_user=current_user.username
    connection = sqlite3.connect("headortails.db")
    cursor = connection.cursor()
    cursor.execute("SELECT amount FROM payment where active_user=active_user")
    results = cursor.fetchall()
    return render_template('success.html',results=results)

if __name__ == "__main__":
    app.debug=True
    db.create_all()
    app.run()
    FLASK_APP=app.py