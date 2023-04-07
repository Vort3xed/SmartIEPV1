import bcrypt
from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fa1(0nwar3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///people.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.signin'
login_manager.init_app(app)

class Accounts(UserMixin, db.Model):
	__tablename__ = 'accounts'
	account_id = db.Column(db.Integer, primary_key=True)
	callname = db.Column(db.String(200),nullable=False)
	username = db.Column(db.String(200),nullable=False)
	password = db.Column(db.String(200),nullable=False)

	def get_id(self):
		return (self.account_id)

class Students(db.Model):
	__tablename__ = 'students'
	student_id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200),nullable=False)
	grade = db.Column(db.Integer)
	dateofbirth = db.Column(db.String(200),nullable=False)
	tasks = db.Column(db.String(500),nullable=False)

@login_manager.user_loader
def load_user(account_id):
    return Accounts.query.get(int(account_id))

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

@main.route("/")
def home():
	return render_template("login.html")

@main.route("/contactus")
def contactus():
	return render_template("contactus.html")

@main.route("/accounts")
@login_required
def account():
	accounts = Accounts.query.all()
	return render_template('accounts.html',accounts=accounts)

@auth.route("/signin", methods=('GET', 'POST'))
def signin():
	if request.method == 'POST':
		username = request.form["logusername"]
		password = request.form["logpassword"]

		user = Accounts.query.filter_by(username=username).first()

		if not user or not check_password_hash(user.password, password):
			flash('Please check your login details and try again.')
			return render_template("login.html")
		else:
			login_user(user)
			accounts = Accounts.query.all()
			return redirect(url_for('main.account'))

	return render_template("login.html")

@auth.route("/register", methods=('GET', 'POST'))
def register():
	if request.method == 'POST':
		callname = request.form["regcallname"]
		username = request.form["regusername"]
		password = request.form["regpassword"]

		user = Accounts.query.filter_by(username=username).first()
		
		if user:
			flash('Email address already exists')
			return render_template("register.html")
		account_user = Accounts(callname=callname, username=username, password=generate_password_hash(password, method='sha256'))

		db.session.add(account_user)
		db.session.commit()
	return render_template("register.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

app.register_blueprint(auth)
app.register_blueprint(main)

if __name__ == '__main__':
	app.run(debug=True)