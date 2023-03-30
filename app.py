import bcrypt
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import Accounts, Students
from __init__ import app

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
			return redirect(url_for('auth.signup'))

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