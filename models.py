from . import db

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