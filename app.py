import bcrypt
from flask import Flask, render_template, request, redirect, url_for, flash
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
def login():
	return render_template("login.html")

@app.route("/register", methods=('GET', 'POST'))
def register():
	if request.method == 'POST':
		username = request.form["username"]
		password = request.form["password"]

		user = Accounts.query.filter_by(username=username).first() # if this returns a user, then the email already exists in database
		
		if user: # if a user is found, we want to redirect back to signup page so user can try again
			flash('Email address already exists')
			return render_template("register.html")

		account_user = Accounts(username=username, password=password)

		db.session.add(account_user)
		db.session.commit()
		#return redirect(url_for('index'))
	return render_template("register.html")

@app.route("/accounts")
def account():
	accounts = Accounts.query.all()
	return render_template('accounts.html',accounts=accounts)

@app.route("/", methods=('GET', 'POST'))
def signin():
	accountData = Accounts.query.all()
	if request.method == 'POST':
		if Accounts.password.verify_password(request.form["password"]) and request.form["username"] == Accounts.username:
			return render_template('accounts.html',accounts=accountData)

def verify_password(self, password):
    pwhash = bcrypt.hashpw(password, self.password)
    return self.password == pwhash

if __name__ == '__main__':
	app.run(debug=True)