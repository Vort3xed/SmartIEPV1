import bcrypt
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'fa1(0nwar3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///people.db'

db.init_app(app)

class Accounts(db.Model):
	__tablename__ = 'accounts'
	account_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(200),nullable=False)
	password = db.Column(db.String(200),nullable=False)

class Students(db.Model):
	__tablename__ = 'students'
	student_id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200),nullable=False)
	goals = db.Column(db.String(200),nullable=False)

@app.route("/")
def home():
	return render_template("login.html")

@app.route("/signin", methods=('GET', 'POST'))
def signin():
	if request.method == 'POST':
		username = request.form["logusername"]
		password = request.form["logpassword"]

		user = Accounts.query.filter_by(username=username).first()

		if not user or not check_password_hash(user.password, password):
			flash('Please check your login details and try again.')
			print(check_password_hash(user.password,password))
			return render_template("login.html")
		else:
			accounts = Accounts.query.all()
			return render_template('accounts.html',accounts=accounts)

	return render_template("login.html")

@app.route("/register", methods=('GET', 'POST'))
def register():
	if request.method == 'POST':
		username = request.form["regusername"]
		password = request.form["regpassword"]

		user = Accounts.query.filter_by(username=username).first()
		
		if user:
			flash('Email address already exists')
			return render_template("register.html")

		account_user = Accounts(username=username, password=generate_password_hash(password, method='sha256'))

		db.session.add(account_user)
		db.session.commit()
	return render_template("register.html")

@app.route("/accounts")
def account():
	accounts = Accounts.query.all()
	return render_template('accounts.html',accounts=accounts)

if __name__ == '__main__':
	app.run(debug=True)