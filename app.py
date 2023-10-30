import re
import json
from flask_wtf.csrf import CSRFProtect
from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, send_file, session
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from utilities import *
from openpyxl import Workbook
from io import BytesIO
from openpyxl.styles import Alignment, Font
from flask_toastr import Toastr
import psycopg2
import os
from datetime import date
#Import wastelands

db = SQLAlchemy()
#Define SQL Alchemy object

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fa1(0nwar3'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db.init_app(app)
#Initialize the flask app with the database

login_manager = LoginManager()
login_manager.login_view = 'auth.signin'
login_manager.init_app(app)
#Create a login manager and set the login view to the sign in page. Then initialize the flask app with the login manager

CSRFProtect(app)
#Create a CSRF object and initialize the flask app with it. This will be used to defend against CSFR attacks

toastr = Toastr(app)
#Create a toastr object and initialize the flask app with it

MAX_GOALS = 100
PERMANENT_COUNTER = 0
#Maximum possible amount of goals that can be created

# STUDENT_LOG_NAME = ""
# STUDENT_LOG_ID = 1
#The ID of the student that is currently being logged

# STUDENT_TASK_ID = 1
# CURRENT_PAGE = 'students'

# Enabled Autoescape for Jinja2, should prevent against XSS attacks
app.jinja_env.autoescape = True


CASE_MANAGER_FILTER = "NO FILTER"
GRADE_LEVEL_FILTER = "NO FILTER"

class Accounts(UserMixin, db.Model):
	__tablename__ = 'accounts'
	account_id = db.Column(db.Integer, primary_key=True)
	callname = db.Column(db.String(200),nullable=False)
	username = db.Column(db.String(200),nullable=False)
	password = db.Column(db.String(200),nullable=False)

	def get_id(self):
		return (self.account_id)
	#Return the signed in account's ID for the login manager
#Table of accounts

class Students(db.Model):
	__tablename__ = 'students'
	student_id = db.Column(db.Integer, primary_key=True)
	school_id = db.Column(db.Integer)
	name = db.Column(db.String(200),nullable=False)
	grade = db.Column(db.Integer)
	dateofbirth = db.Column(db.String(200),nullable=False)
	casemanager = db.Column(db.String(200),nullable=False)

	disability = db.Column(db.String(200),nullable=False)
	last_annual_review = db.Column(db.String(200),nullable=False)

	tasks = db.Column(db.String(50000),nullable=False)
	logs = db.Column(db.String(50000),nullable=False)

@login_manager.user_loader
def load_user(account_id):
    return Accounts.query.get(int(account_id))
#Load the user for the login manager

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)
#Define routing blueprints

@main.route("/")
def home():
	return render_template("login.html")
#Route 1: Login page

@main.route("/contactus")
def contactus():
	return render_template("contactus.html")
#Route 2: Contact us page

@main.route("/accounts")
@login_required
def accounts():
	accounts = Accounts.query.all()
	return render_template('accounts.html',accounts=accounts)
	#Query all students and render the accounts page with the accounts queried

@main.route("/accountmods", methods=('GET', 'POST'))
@login_required
def accountmods():
	if request.method == 'POST':
		account_id = request.form["account_id"]
		#Get the account ID of the account to be modified

		account = Accounts.query.filter_by(account_id=account_id).first()
		#Query the account to be modified
		
		if account:
			db.session.delete(account)
			db.session.commit()
			return redirect(url_for('main.settings'))
			#Delete the account and redirect back to settings page
		else:
			flash({'title': "SmartIEP:", 'message': "Cannot delete account!"}, 'error')
			return redirect(url_for('main.settings'))
	return redirect(url_for('main.settings'))

@main.route("/changepasswd", methods=('GET', 'POST'))
@login_required
def changepasswd():
	if request.method == 'POST':
		# account_id = request.form["account_id"]
		#Get the account ID of the account to be modified

		account = Accounts.query.filter_by(account_id=current_user.account_id).first()
		#Query the account to be modified

		if account:
			new_password = request.form["accountpass"]
			#Get the new password to be set for the account

			account.password = generate_password_hash(new_password, method='sha256')
			db.session.commit()
			#Set the account's password to the new password and commit the changes to the database

			return redirect(url_for('main.settings'))
		else:
			flash({'title': "SmartIEP:", 'message': "Cannot change password!"}, 'error')
			return redirect(url_for('main.settings'))

@main.route("/students", methods=('GET', 'POST'))
@login_required
def students():
	if request.method == 'POST':
		button_value = request.form["submit_button"]
		#Get the value of the button that was pressed

		modify_student = re.sub("\D", "", button_value)
		#Remove all non-numeric characters from the button value to get the student ID. Student ID is linked to the number found in the button value.
		
		name = request.form["boxmodname"+modify_student]
		school_id = request.form["boxmodschoolid"+modify_student]
		grade = request.form["boxmodgrade"+modify_student]
		dob = request.form["boxmoddob"+modify_student]
		disability = request.form["boxmoddisability"+modify_student]
		casemanager = request.form["boxmodmanager"+modify_student]
		last_annual_review = request.form["boxmodlastreview"+modify_student]
		#Get the values in the text boxes for the student to be modified
		
		query_student = Students.query.filter_by(student_id=modify_student).first()
		#Query the student to be modified

		if query_student:
			if name:
				query_student.name = name
			if school_id:
				query_student.school_id = school_id
			if grade:
				query_student.grade = grade
			if dob:
				query_student.dateofbirth = dob
			if disability:
				query_student.disability = disability
			if casemanager:
				query_student.casemanager = casemanager
			if last_annual_review:
				query_student.last_annual_review = last_annual_review
			#Set the query_student's fields to the values in the text boxes. If no value is found, do nothing.

			db.session.commit()
			accounts = Accounts.query.all()
			# return render_template('students.html',students=students,accounts=accounts)
			if session['page'] == 'students':
				return redirect(url_for("main.students"))
			elif session['page'] == 'studentinfo':
				return redirect(url_for("main.studentinfo"))
			#Commit the changes to the database and render the students page
		else:
			# flash("Cannot Modify Student!")
			flash({'title': "SmartIEP:", 'message': "Cannot modify student!"}, 'error')
	session['page'] = 'students'
	accounts = Accounts.query.all()
	return render_template('students.html',students=studentsByFilter(),accounts=accounts)

@main.route("/studentinfo", methods=('GET', 'POST'))
@login_required
def studentinfo():
	session['page'] = 'studentinfo'
	students = Students.query.all()
	accounts = Accounts.query.all()
	return(render_template("studentinfo.html",students=students,accounts=accounts))
	#Render the student info page with all students and all accounts for the drop down menu

@main.route("/setfilter", methods=('GET', 'POST'))
@login_required
def setfilter():
	if request.method == 'POST':
		case_manager = request.form["case_manager"]
		global CASE_MANAGER_FILTER
		CASE_MANAGER_FILTER = case_manager

		grade_level = request.form["grade_level"]
		global GRADE_LEVEL_FILTER
		GRADE_LEVEL_FILTER = grade_level

		return redirect(url_for('main.students'))
	return redirect(url_for('main.students'))

def studentsByFilter():
	all_students = Students.query.all()
	students_to_display = []

	#If case manager filter is not set to no filter, but the grade level filter is, use only the case manager filter
	if (CASE_MANAGER_FILTER != "NO FILTER" and GRADE_LEVEL_FILTER == "NO FILTER"):
		for student in all_students:
			if student.casemanager == CASE_MANAGER_FILTER:
				students_to_display.append(student)
	#If grade level filter is not set to no filter, but the case manager filter is, use only the grade level filter
	elif (GRADE_LEVEL_FILTER != "NO FILTER" and CASE_MANAGER_FILTER == "NO FILTER"):
		for student in all_students:
			if student.grade == int(GRADE_LEVEL_FILTER):
				students_to_display.append(student)
	#If both filters are set to no filter, use all students
	elif (CASE_MANAGER_FILTER != "NO FILTER" and GRADE_LEVEL_FILTER != "NO FILTER"):
		for student in all_students:
			if student.casemanager == CASE_MANAGER_FILTER and student.grade == int(GRADE_LEVEL_FILTER):
				students_to_display.append(student)
	#If both filters are active, only display students that match both filters
	elif (CASE_MANAGER_FILTER == "NO FILTER" and GRADE_LEVEL_FILTER == "NO FILTER"):
		students_to_display = all_students

	return students_to_display

@main.route("/alternateprogress", methods=('GET', 'POST'))
@login_required
def alternateprogress():
	if request.method == 'POST':
		button_value = request.form["alternate_button"]
		data = button_value.split("alternate")
		element_id = data[0]
		modify_student = data[1]
		#Get the student ID of the student to be modified and the task key of the task to be modified

		task_to_alternate = request.form.get(element_id+"alternate"+modify_student)
		#Retrieve the text box value for the task to be modified

		query_student = Students.query.filter_by(student_id=modify_student).first()

		if (query_student.tasks.find(task_to_alternate[1:]) > -1):
			match task_to_alternate[0]:
				case "0":
					query_student.tasks = set_progressv2(task_to_alternate[1:],1,query_student.tasks)
					db.session.commit()
					if (session['page'] == 'students'):
						return redirect(url_for('main.students'))
					elif (session['page'] == 'tasks'):
						return redirect(url_for('main.expandtasks'))
					return redirect(url_for('main.students'))
				case "1":
					query_student.tasks = set_progressv2(task_to_alternate[1:],2,query_student.tasks)
					db.session.commit()
					if (session['page'] == 'students'):
						return redirect(url_for('main.students'))
					elif (session['page'] == 'tasks'):
						return redirect(url_for('main.expandtasks'))
					return redirect(url_for('main.students'))
				case "2":
					query_student.tasks = set_progressv2(task_to_alternate[1:],0,query_student.tasks)
					db.session.commit()
					if (session['page'] == 'students'):
						return redirect(url_for('main.students'))
					elif (session['page'] == 'tasks'):
						return redirect(url_for('main.expandtasks'))
					return redirect(url_for('main.students'))
				case _:
					flash({'title': "SmartIEP:", 'message': "Task does not exist!"}, 'error')
	if (session['page'] == 'students'):
		return redirect(url_for('main.students'))
	elif (session['page'] == 'tasks'):
		return redirect(url_for('main.expandtasks'))
	return redirect(url_for('main.students'))

# @main.route("/setnodata", methods=('GET','POST'))
# @login_required
# def setnodata():
# 	if request.method == 'POST':
# 		button_value = request.form["setnodata"]
# 		modify_student = re.sub("\D", "", button_value)

# 		user_input = request.form["set_progress" + modify_student]

# 		query_student = Students.query.filter_by(student_id=modify_student).first()

# 		if (query_student.tasks.find(user_input) > -1):
# 			set_progress = query_student.tasks[:query_student.tasks.find(user_input) - 4] + "0" + query_student.tasks[query_student.tasks.find(user_input) - 4 + 1:]
# 			query_student.tasks = set_progress
# 			db.session.commit()
# 		else:
# 			flash({'title': "SmartIEP:", 'message': "Task does not exist!"}, 'error')

# 		return redirect(url_for('main.students'))

# @main.route("/setinprogress", methods=('GET','POST'))
# @login_required
# def setinprogress():
# 	if request.method == 'POST':
# 		button_value = request.form["setinprogress"]
# 		modify_student = re.sub("\D", "", button_value)

# 		user_input = request.form["set_progress" + modify_student]

# 		query_student = Students.query.filter_by(student_id=modify_student).first()

# 		if (query_student.tasks.find(user_input) > -1):
# 			set_progress = query_student.tasks[:query_student.tasks.find(user_input) - 4] + "1" + query_student.tasks[query_student.tasks.find(user_input) - 4 + 1:]
# 			query_student.tasks = set_progress
# 			db.session.commit()
# 		else:
# 			flash({'title': "SmartIEP:", 'message': "Task does not exist!"}, 'error')

# 		return redirect(url_for('main.students'))
	
# @main.route("/setcomplete", methods=('GET','POST'))
# @login_required
# def setcomplete():
# 	if request.method == 'POST':
# 		button_value = request.form["setcomplete"]
# 		modify_student = re.sub("\D", "", button_value)
# 		#Retrieve student ID and task key from the button value. The button value is formatted as "studentID;taskKey"

# 		user_input = request.form["set_progress" + modify_student]
# 		#Get the value in the text box for the task to be set to complete. Each text box is linked to each student by the student ID.

# 		query_student = Students.query.filter_by(student_id=modify_student).first()

# 		if (query_student.tasks.find(user_input) > -1):
# 			set_progress = query_student.tasks[:query_student.tasks.find(user_input) - 4] + "2" + query_student.tasks[query_student.tasks.find(user_input) - 4 + 1:]
# 			query_student.tasks = set_progress
# 			db.session.commit()
# 			#Update tasks field in the database with the new task progress
# 		else:
# 			flash({'title': "SmartIEP:", 'message': "Task does not exist!"}, 'error')

# 		return redirect(url_for('main.students'))

@main.route("/exportstudent", methods=('GET', 'POST'))
@login_required
def exportstudent():
	if request.method == 'POST':
		button_value = request.form["export_button"]
		modify_student = re.sub("\D", "", button_value)
		#Remove all non-numeric characters from the button value to get the student ID. Student ID is linked to the number found in the button value.

		query_student = Students.query.filter_by(student_id=modify_student).first()
		#Query the student to be modified

		return generate_spreadsheet(query_student)

@main.route("/addgoal", methods=('GET', 'POST'))
@login_required
def addGoals():
	if request.method == 'POST':
		button_value = request.form["submit_goal"]
		modify_student = re.sub("\D", "", button_value)
		#Remove all non-numeric characters from the button value to get the student ID. Student ID is linked to the number found in the button value.

		goal_to_append = request.form["add_goal"+modify_student]
		category = request.form["goalcategory"+modify_student]
		#Get the value in the text box for the goal to be added. Each text box is linked to each student by the student ID.

		query_student = Students.query.filter_by(student_id=modify_student).first()
		#Query the student to be modified

		if query_student:
			array_index = find_empty_array(parse_student_tasksv2(query_student.tasks))
			json_parcel = '{"Type": 0, "Index": "' + str(array_index) + '", "Task": "' + goal_to_append + '", "Progress": 0, "Category": "' + category + '"}|'
			# {"Type": 0, "Index": 0, "Task": "No data math goal at index 0", "Progress": 0, "Category": "Math"}

			#Format the goal to be added to the student's tasks field

			query_student.tasks = query_student.tasks + json_parcel
			db.session.commit()
			#Add the formatted task to the student's tasks and commit the changes to the database

			if (session['page'] == 'students'):
				return redirect(url_for('main.students'))
			elif (session['page'] == 'tasks'):
				return redirect(url_for('main.expandtasks'))
			return redirect(url_for('main.students'))
			#Redirect to the page found in the session variable
		else:
			flash({'title': "SmartIEP:", 'message': "Cannot modify student!"}, 'error')

@main.route("/addobjectives", methods=('GET', 'POST'))
@login_required
def addObjectives():
	if request.method == 'POST':
		button_value = request.form["add_objective"]
		student_and_goal = button_value.split(";")
		#Collect student ID and goal key from the button value. The button value is formatted as "studentID;goalKey"

		modify_student = student_and_goal[0]
		goal_key = student_and_goal[1]
		#Split the button value into the student ID and goal key

		objective_to_add = request.form[modify_student+"obj"+goal_key]
		#Get the value in the text box for the objective to be added. Each text box is linked to each student by the student ID and each goal by the goal key.

		query_student = Students.query.filter_by(student_id=modify_student).first()
		#Query the student to be modified

		if query_student:
			# formatted_task = "0("+str(int(goal_key)-1)+")"+objective_to_add+";"
			json_parcel = '{"Type": 1, "Index": "' + str(int(goal_key) - 1) + '", "Task": "' + objective_to_add + '", "Progress": 0}|'
			#{"Type": 1, "Index": 0, "Task": "in progress objective for index 0", "Progress": 1}
			query_student.tasks = query_student.tasks + json_parcel
			#Format the objective to be added to the student's tasks field

			db.session.commit()
			if (session['page'] == 'students'):
				return redirect(url_for('main.students'))
			elif (session['page'] == 'tasks'):
				return redirect(url_for('main.expandtasks'))
			return redirect(url_for('main.students'))
			#Add the formatted objective to the student's tasks and commit the changes to the database
		else:
			flash({'title': "SmartIEP:", 'message': "Cannot remove objective!"}, 'error')
			if (session['page'] == 'students'):
				return redirect(url_for('main.students'))
			elif (session['page'] == 'tasks'):
				return redirect(url_for('main.expandtasks'))
			return redirect(url_for('main.students'))
			#Render a page based on what page is found in the session variable

@main.route("/removegoal", methods=('GET', 'POST'))
@login_required
def removeGoals():
	if request.method == 'POST':
		button_value = request.form["remove_goal"]
		data = button_value.split("remove")
		element_id = data[0]
		modify_student = data[1]
		# modify_student = re.sub("\D", "", button_value)
		#Remove all non-numeric characters from the button value to get the student ID. Student ID is linked to the number found in the button value.

		# goal_to_remove = request.form["remove_goal"+modify_student]
		goal_to_remove = request.form.get(element_id+"remove_goal"+modify_student)
		#Get the value in the text box for the goal to be removed. Each text box is linked to each student by the student ID.

		query_student = Students.query.filter_by(student_id=modify_student).first()
		#Query the student to be modified

		if goal_to_remove in query_student.tasks:
			#Check if the goal to be removed exists in the student's tasks and if it is a goal
			if query_student:
				clean_tasks = remove_goalv2(goal_to_remove, query_student.tasks)
				#Remove the goal and the objectives associated with it from the student's tasks

				query_student.tasks = clean_tasks
				#Set the student's tasks to equal the cleaned tasks

				db.session.commit()
				#return redirect(url_for('main.students'))
				accounts = Accounts.query.all()
				# return render_template('students.html',students=Students.query.all(),accounts=accounts)

				if (session['page'] == 'students'):
					return redirect(url_for('main.students'))
				elif (session['page'] == 'tasks'):
					return redirect(url_for('main.expandtasks'))
				return redirect(url_for('main.students'))	
				#Commit the changes to the database and render the students page
			else:
				flash({'title': "SmartIEP:", 'message': "Cannot remove goal!"}, 'error')
		else:
			flash({'title': "SmartIEP:", 'message': "Goal to remove does not exist!"}, 'error')
			return redirect(url_for('main.students'))
		
	accounts = Accounts.query.all()
	return render_template('students.html',students=Students.query.all(),accounts=accounts)

@main.route("/removeobjective", methods=('GET', 'POST'))
@login_required
def removeobjective():
	if request.method == 'POST':
		button_value = request.form["remove_obj"]

		data = button_value.split("remove")
		
		modify_student = data[1]
		student_key = data[0]
		goal_key = data[2]
		# modify_student = re.sub("\D", "", button_value)
		#Remove all non-numeric characters from the button value to get the student ID. Student ID is linked to the number found in the button value.

		obj_to_remove = request.form[student_key+"remove_obj"+modify_student+"remove_obj"+goal_key]
		#Get the value in the text box for the objective to be removed. Each text box is linked to each student by the student ID.

		query_student = Students.query.filter_by(student_id=modify_student).first()
		#Query the student to be modified

		if query_student and obj_to_remove in query_student.tasks:
			#Check if the objective to be removed exists in the student's tasks and if it is an objective
			query_student.tasks = remove_objectivev2(obj_to_remove, query_student.tasks)

			#Remove the objective from the student's tasks
			db.session.commit()
			if (session['page'] == 'students'):
				return redirect(url_for('main.students'))
			elif (session['page'] == 'tasks'):
				return redirect(url_for('main.expandtasks'))
			return redirect(url_for('main.students'))
			#Commit the changes to the database and render the students page
		else:
			flash({'title': "SmartIEP:", 'message': "Objective to remove does not exist!"}, 'error')
			if (session['page'] == 'students'):
				return redirect(url_for('main.students'))
			elif (session['page'] == 'tasks'):
				return redirect(url_for('main.expandtasks'))
			return redirect(url_for('main.students'))
			#Redirect a page based on what the current page in the session variable is

@main.route("/logs", methods=('GET', 'POST'))
@login_required
def logs():
	if request.method == 'POST':
		student_selected = request.form["selectstudent"]

		#Get the student selected from the drop down menu and set the global variable STUDENT_LOG_NAME to the student selected
		session['log_name'] = student_selected

		student_selected_obj = Students.query.filter_by(name=student_selected).first()
		#Query the student selected to get the student ID

		session['log_id'] = student_selected_obj.student_id

		#Set the global variable STUDENT_LOG_ID to the student ID of the student selected
		students = Students.query.all()
		data = genGraphParams(session.get('log_id'))
		labels = [row[0] for row in data]
		values = [row[1] for row in data]
		return(render_template("progresslogs.html", students=students, student_log_id=session.get('log_id'), labels=labels, values=values))
		#Render the progress logs page with the student selected and the student ID of the student selected
	else:
		students = Students.query.all()
		data = genGraphParams(session.get('log_id'))
		labels = [row[0] for row in data]
		values = [row[1] for row in data]
		return(render_template("progresslogs.html", students=students, student_log_id=session.get('log_id'), labels=labels, values=values))

def genGraphParams(student_log_id):
	student = Students.query.filter_by(student_id=student_log_id).first()
	data = []
	if (student):
		json_parcels = student.logs[:-1].split("|")
		for json_unit in json_parcels:
			if (json_unit != "" and json.loads(json_unit)['Data'] != ""):
				data.append((json.loads(json_unit)['Date'],json.loads(json_unit)['Data']))
	return data
	#Generate labels and data then parse that to logs page and render graphs 

@main.route("/expandtasks", methods=('GET', 'POST'))
@login_required
def expandtasks():
	session['page'] = 'tasks'
	if request.method == 'POST':
		session['page'] = 'tasks'
		button_value = request.form["expandtasks"]
		modify_student = re.sub("\D", "", button_value)
		#Remove all non-numeric characters from the button value to get the student ID. Student ID is linked to the number found in the button value.

		query_student = Students.query.filter_by(student_id=modify_student).first()
		#Query the student to be modified

		if query_student:
			session['task_id'] = query_student.student_id
			session['page'] = 'tasks'
			#Set session task id and page to the queried student's id and tasks page

			students = Students.query.all()
			return(render_template("tasks.html", students=students, student_task_id=session.get('task_id')))
		else:
			flash({'title': "SmartIEP:", 'message': "Cannot expand tasks!"}, 'error')
			session['page'] = 'students'
			#Set session page to students page if the student cannot be queried

			return redirect(url_for('main.students'))
	students = Students.query.all()
	return(render_template("tasks.html", students=students, student_task_id=session.get('task_id')))

@main.route("/settaskstudentid", methods=('GET', 'POST'))
@login_required
def settaskstudentid():
	if request.method == 'POST':
		button_value = request.form["selectstudent"]
		#Get the student selected from the drop down menu and set the global variable STUDENT_TASK_NAME to the student selected
		
		student = Students.query.filter_by(name=button_value).first()

		session['task_id'] = student.student_id
		#Set the session task id to the queried student's id

		return redirect(url_for('main.expandtasks'))
	
@main.route("/modifylogs", methods=('GET', 'POST'))
@login_required
def modifylogs():
	global PERMANENT_COUNTER
	if request.method == 'POST':
		log_date = request.form["logdate"]
		log_text = request.form["logtext"]
		log_future = request.form["logfuture"]
		log_data = request.form["logdata"]
		#Pull log information from front-end

		modify_student = Students.query.filter_by(student_id=session.get('log_id')).first()
		#Query the student to be modified
		
		log_units = len(modify_student.logs[:-1].split("|"))
		#Get the amount of logs the student has

		# json_parcel = '{"ID": ' + str(log_units + 1) + ', "Date": "' + log_date + '", "Log": "' + log_text + '", "Data": "' + log_data + '"}'
		# json_parcel = '{"ID": ' + str(PERMANENT_COUNTER) + ', "Date": "' + log_date + '", "Log": "' + log_text + '", "Data": "' + log_data + '"}'
		json_parcel = '{"ID": ' + str(PERMANENT_COUNTER) + ', "Date": "' + log_date + '", "Log": "' + log_text + '", "Future": "' + log_future + '", "Data": "' + log_data + '"}'

		#Format the log to be added to the student's logs field

		modify_student.logs = modify_student.logs + json_parcel + "|"
		# print(modify_student.logs)
		db.session.commit()
		
		PERMANENT_COUNTER = PERMANENT_COUNTER + 1
		return(redirect(url_for("main.logs")))

@main.route("/removelogs", methods=('GET', 'POST'))
@login_required
def removelogs():
	if request.method == 'POST':
		button_value = request.form["removelog"]
		log_id = re.sub("\D", "", button_value)
		# data = button_value.split("removelog")
		# specific_log_id = data[0]
		# log_id = data[1]
		#Remove all non-numeric characters from the button value to get the log ID. Log ID is linked to the number found in the button value.

		#log_text = request.form["removelogtext" + log_id]
		modify_student = Students.query.filter_by(student_id=session.get('log_id')).first()
		#Query the student to be modified

		if modify_student:
			modify_student.logs = remove_log(modify_student.logs, log_id)
			#Remove the log from the student's logs field

			db.session.commit()
			return(redirect(url_for("main.logs")))
		else:
			flash({'title': "SmartIEP:", 'message': "Cannot remove log!"}, 'error')
			return(redirect(url_for("main.logs")))
		
@main.route("/editlogs", methods=('GET', 'POST'))
@login_required
def editlogs():
	if request.method == 'POST':
		button_value = request.form["editlog"]
		log_id = re.sub("\D", "", button_value)
		#Remove all non-numeric characters from the button value to get the log ID. Log ID is linked to the number found in the button value.

		log_text = request.form["logmodlog" + log_id]
		log_date = request.form["logmoddob" + log_id]
		log_future = request.form["logmodfuture" + log_id]
		log_data = request.form["logmoddata" + log_id]
		#Pull log information from front-end

		modify_student = Students.query.filter_by(student_id=session.get('log_id')).first()
		#Query the student to be modified

		if modify_student:
			modify_student.logs = edit_log(modify_student.logs, log_id, log_date, log_text, log_future, log_data)
			#Edit the log in the student's logs field

			db.session.commit()
			return(redirect(url_for("main.logs")))
		else:
			flash({'title': "SmartIEP:", 'message': "Cannot edit log!"}, 'error')
			return(redirect(url_for("main.logs")))

def edit_log(logs, log_id, log_date, log_text, log_future, log_data):
	logs = logs[:-1].split("|")
	#Split the logs into an array of logs
	newlogs = []
	for log in logs:
		if json.loads(log)['ID'] == int(log_id):
			# new_log = '{"ID": ' + str(log_id) + ', "Date": "' + log_date + '", "Log": "' + log_text + '", "Data": "' + log_data + '"}'
			new_log = '{"ID": ' + str(log_id) + ', "Date": "' + log_date + '", "Log": "' + log_text + '", "Future": "' + log_future + '", "Data": "' + log_data + '"}'
			newlogs.append(new_log)
		else:
			newlogs.append(log)
			
	# logs[int(log_id) - 1] = '{"ID": ' + str(log_id) + ', "Date": "' + log_date + '", "Log": "' + log_text + '", "Future": "' + log_future + '", "Data": "' + log_data + '"}'
	#Edit the log in the array of logs

	logs = "|".join(newlogs) + "|"
	#Join the array of logs into a string of logs
	return logs
	
	#Return the string of logs
	
@main.route("/viewlogs", methods=('GET', 'POST'))
@login_required
def viewlogs():
	if request.method == 'POST':
		button_value = request.form["viewlog"]
		student_key = re.sub("\D", "", button_value)
		#Remove all non-numeric characters from the button value to get the student ID. Student ID is linked to the number found in the button value.

		student = Students.query.filter_by(student_id=student_key).first()

		session['log_id'] = student.student_id
		#Set session log id to the selected student's id

		return(redirect(url_for("main.logs")))

@main.route("/settings", methods=('GET', 'POST'))
@login_required
def settings():
	if request.method == 'POST':
		student_id = request.form["modid"]
		student = Students.query.filter_by(student_id=student_id).first()
		#Query the student to be terminated

		if student:
			db.session.delete(student)
			db.session.commit()
			
			all_students = Students.query.all()
			if len(all_students) > 0:
				session['log_id'] = all_students[0].student_id
			#Delete the student from the database and commit the changes
			return(render_template("terminatestudent.html"))
		else:
			flash({'title': "SmartIEP:", 'message': "Student ID does not exist!"}, 'error')
	return(render_template("terminatestudent.html"))
#Route 9: Terminate student. This method renders its own page.

@main.route("/determineavaliablestudent", methods=('GET', 'POST'))
@login_required
def determineavaliablestudent():
	# print("determineavaliablestudent")
	all_students = Students.query.all()
	session['log_id'] = all_students[0].student_id
	flash({'title': "SmartIEP:", 'message': session.get('log_id')}, 'error')
	return(redirect(url_for("main.terminatestudent")))

@main.route("/debugstudent", methods=('GET', 'POST'))
@login_required
def debugstudent():
	if request.method == 'POST':
		student_id = request.form["modid"]
		student = Students.query.filter_by(student_id=student_id).first()
		#Query the student to be debugged
		if student:
			# flash(student.tasks + " LOGS:" + student.logs)
			flash({'title': "SmartIEP:", 'message': student.tasks + " LOGS:" + student.logs}, 'error')

			#Flash the student's tasks
		else:
			flash({'title': "SmartIEP:", 'message': "Student ID does not exist!"}, 'error')
	return(render_template("terminatestudent.html"))
#Route 10: Debug student. This method renders its own page.

@main.route("/wipedata", methods=('GET', 'POST'))
@login_required
def wipedata():
	if request.method == 'POST':
		student_id = request.form["modid"]
		student = Students.query.filter_by(student_id=student_id).first()
		#Query the student to have their data wiped

		if student:
			student.tasks = ""
			student.logs = '{"ID": 1, "Date": "Year-Month-Date", "Log": "Student Created", "Future": "", "Data": ""}|'
			db.session.commit()
			#Set the student's tasks to an empty string and commit the changes

			return(render_template("terminatestudent.html"))
		else:
			flash({'title': "SmartIEP:", 'message': "Student ID does not exist!"}, 'error')
	return(render_template("terminatestudent.html"))
#Route 11: Wipe student data. This method renders its own page.

@main.route("/graph")
def graph():
    # data = [
    #     ("2023-01-01", 30/100),
    #     ("2023-01-02", 36/46),
    #     ("2023-01-03", 2/5),
    #     ("2023-01-04", 4/5),
    #     ("2023-02-02", 5/5),
    #     ("2023-03-01", 5/5),
    #     ("2024-01-07", 8/10),
    #     # ("08-01-2019", 9/10),
    # ]
	data = genGraphParams(session.get('log_id'))
	labels = [row[0] for row in data]
	values = [row[1] for row in data]
	return render_template("graph.html", labels=labels,values=values)

@main.route("/createstudent", methods=('GET', 'POST'))
@login_required
def createstudent():
	if request.method == 'POST':
		name = request.form["stuname"]
		school_id = request.form["stuschoolid"]
		grade = request.form["stugrade"]
		dateofbirth = request.form["studob"]
		disability = request.form["studisability"]
		casemanager = request.form["stumanager"]
		last_annual_review = request.form["stulastreview"]

		#Get the values from the form

		user = Students.query.filter_by(name=name).first()
		#Query the student to be created
		if user:
			flash({'title': "SmartIEP:", 'message': "Student already exists!"}, 'error')
			#If the student already exists, flash a message and render the create student page again
			return redirect(url_for('main.students'))
		created_student = Students(name=name,school_id=school_id,grade=grade,dateofbirth=dateofbirth,casemanager=casemanager,disability=disability,last_annual_review=last_annual_review,tasks="",logs='{"ID": 1, "Date": "Year-Month-Date", "Log": "Student Created", "Future": "", "Data": ""}|')
		#Create the student

		db.session.add(created_student)
		db.session.commit()

	return redirect(url_for('main.students'))
#Route 12: Create student. This method renders its own page.


@auth.route("/signin", methods=('GET', 'POST'))
def signin():
	if request.method == 'POST':
		username = request.form["logusername"]
		password = request.form["logpassword"]
		#Get the values from the form

		user = Accounts.query.filter_by(username=username).first()
		#Query the user to be signed in

		if not user or not check_password_hash(user.password, password):
			#If the user does not exist or the password is incorrect, flash a message and render the login page again
			flash({'title': "SmartIEP:", 'message': "Please check your login credentials and try again!"}, 'error')
			return render_template("login.html")
		else:
			login_user(user)
			current_user.account_id = user.account_id
			#If the user exists and the password is correct, log the user in and redirect them to the accounts page
			return redirect(url_for('main.students'))

	return render_template("login.html")
#Route 13: Sign in. This method renders its own page.

@auth.route("/register", methods=('GET', 'POST'))
@login_required
def register():
	if request.method == 'POST':
		callname = request.form["regcallname"]
		teacher_type = request.form["regtype"]
		username = request.form["regusername"]
		password = request.form["regpassword"]
		#Get the values from the form

		user = Accounts.query.filter_by(username=username).first()
		#Query the user to be registered
		
		if user:
			flash({'title': "SmartIEP:", 'message': "Email already exists!"}, 'error')
			return render_template("register.html")
		account_user = Accounts(callname=teacher_type + " " + callname, username=username, password=generate_password_hash(password, method='sha256'))
		#Create the user using the values from the form

		db.session.add(account_user)
		db.session.commit()
	return render_template("register.html")
#Route 14: Register an account. This method renders its own page.

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    #Log the user out
    return redirect(url_for('main.home'))
#Route 15: Logout. This method does not render its own page.

app.register_blueprint(auth)
app.register_blueprint(main)
#Register the blueprints

@app.context_processor
def student_retriever():
	def retrieve_student(student_id):
		student = Students.query.filter_by(student_id=student_id).first()
		return student
	return dict(retrieve_student=retrieve_student)

@app.context_processor
def attribute_identifier():
	return dict(hasattr=hasattr)

@app.context_processor
def utility_processor():
	#This function is set as a utility processor so that the front end can use it.
	def parse_tasks(newData):
		if (newData != ""):
			goalArrays = []
			for i in range(MAX_GOALS):
				goalArrays.append([])
			#Create an array of arrays to store the goals

			parts = newData[:-1].split(";")
			#Split the data into parts

			counter = 0
			for part in parts:
				if part[1] == "[":
					goalKey2 = int(part[part.find("[")+1:part.find("]")])
					part = re.sub("\[.*?\]","[]",part)
					part = part.replace("[","").replace("]","")
					# goalArrays[counter].append(part)
					goalArrays[goalKey2].append(part)
					counter = counter + 1
				#Check if each part in the string is a goal, and if it is, add it to the first index of every goal array.
			for part in parts:
				if part[1] == "(":
					goalKey = int(part[part.find("(")+1:part.find(")")])
					part = re.sub("\(.*?\)","()",part)
					part = part.replace("(","").replace(")","")
					goalArrays[goalKey].append(part)
				#Check if each part in the string is a task, and if it is, add it to the goal array with the same ID as the goal.          
			return goalArrays
		else:
			return []
	return dict(parse_tasks=parse_tasks)
#This method is used to parse the tasks from the database into a format that can be used by the HTML page.

@app.context_processor
def add_imports():
    #Allowing JSON library to be used in the HTML page
    return dict(json=json)

@app.context_processor
def add_imports2():
	return dict(parse_student_tasksv2=parse_student_tasksv2)

@app.context_processor
def auto_date():
	def get_date():
		return date.today()
	return dict(get_date=get_date)

def parse_student_tasks(newData):
    if (newData != ""):
        goalArrays = []
        for i in range(MAX_GOALS):
            goalArrays.append([])
        parts = newData[:-1].split(";")
        counter = 0
        for part in parts:
            if part[1] == "[":
                goalKey2 = int(part[part.find("[")+1:part.find("]")])
                part = re.sub("\[.*?\]","[]",part)
                part = part.replace("[","").replace("]","")
                goalArrays[goalKey2].append(part)
				# goalArrays[counter].append(part)
                counter = counter + 1
        for part in parts:
            if part[1] == "(":
                goalKey = int(part[part.find("(")+1:part.find(")")])
                part = re.sub("\(.*?\)","()",part)
                part = part.replace("(","").replace(")","")
                goalArrays[goalKey].append(part)            
        return goalArrays
    else:
        return [[]]
#This is the same method as above, but it is used for the back end on the student page.

def generate_spreadsheet(student):
	workbook = Workbook()
	sheet = workbook.active

	sheet.column_dimensions['A'].width = 30
	sheet.column_dimensions['B'].width = 50

	sheet.title = "Student IEP Data"
	sheet['A1'] = "Student IEP Data"
	sheet['A1'].font = Font(size=20, bold=True)
	sheet['A2'] = "School ID: " + str(student.school_id)
	sheet['A3'] = "Name: " + student.name
	sheet['A4'] = "Grade: " + str(student.grade)
	sheet['A5'] = "Date of Birth: " + student.dateofbirth
	sheet['A6'] = "Disability: " + student.disability
	sheet['A7'] = "Case Manager: " + student.casemanager
	sheet['A8'] = "Last Annual Review: " + student.last_annual_review

	sheet['B2'] = "Goals with Objectives:"
	sheet['B2'].font = Font(bold=True)
	
	opencell = 3
	for array in parse_student_tasksv2(student.tasks):
		if (array != []):
			if (json.loads(array[0])["Progress"] == 0):
				sheet['B' + str(opencell)] = "- ("+json.loads(array[0])["Category"]+") Not Measureable: " + json.loads(array[0])["Task"]
				sheet['B' + str(opencell)].alignment = Alignment(wrapText=True)
			elif (json.loads(array[0])["Progress"] == 1):
				sheet['B' + str(opencell)] = "- ("+json.loads(array[0])["Category"]+") In Progress: " + json.loads(array[0])["Task"]
				sheet['B' + str(opencell)].alignment = Alignment(wrapText=True)
			else:
				sheet['B' + str(opencell)] = "- ("+json.loads(array[0])["Category"]+") Complete: " + json.loads(array[0])["Task"]
				sheet['B' + str(opencell)].alignment = Alignment(wrapText=True)
			opencell = opencell + 1
	
			for task in array[1:]:
				if (task != ""):
					if (json.loads(task)["Progress"] == 0):
						sheet['B' + str(opencell)] = "- - Not Measureable: " + json.loads(task)["Task"]
						sheet['B' + str(opencell)].alignment = Alignment(wrapText=True)
					elif (json.loads(task)["Progress"] == 1):
						sheet['B' + str(opencell)] = "- - In Progress: " + json.loads(task)["Task"]
						sheet['B' + str(opencell)].alignment = Alignment(wrapText=True)
					else:
						sheet['B' + str(opencell)] = "- - Complete: " + json.loads(task)["Task"]
						sheet['B' + str(opencell)].alignment = Alignment(wrapText=True)
					opencell = opencell + 1
	
	sheet['C1'] = "Progress Logs:"
	sheet['C1'].font = Font(size=20, bold=True)

	sheet['C2'] = "Log ID:"
	sheet['C2'].font = Font(bold=True)

	sheet['D2'] = "Date:"
	sheet['D2'].font = Font(bold=True)

	sheet['E2'] = "Log:"
	sheet['E2'].font = Font(bold=True)

	sheet['F2'] = "Future Plans:"
	sheet['F2'].font = Font(bold=True)

	sheet['G2'] = "Data:"
	sheet['G2'].font = Font(bold=True)

	sheet.column_dimensions['C'].width = 10
	sheet.column_dimensions['D'].width = 20
	sheet.column_dimensions['E'].width = 50
	sheet.column_dimensions['F'].width = 50

	progressOpenCell = 3
	for log in student.logs[:-1].split("|"):
		log = json.loads(log)
		sheet['C' + str(progressOpenCell)] = str(log["ID"])
		sheet['D' + str(progressOpenCell)] = log["Date"]
		sheet['E' + str(progressOpenCell)] = log["Log"]
		sheet['E' + str(progressOpenCell)].alignment = Alignment(wrapText=True)
		sheet['F' + str(progressOpenCell)] = log["Future"]
		sheet['F' + str(progressOpenCell)].alignment = Alignment(wrapText=True)
		sheet['G' + str(progressOpenCell)] = log["Data"]
		progressOpenCell = progressOpenCell + 1
	
	student_iep = BytesIO()
	workbook.save(student_iep)
	student_iep.seek(0)
	return send_file(student_iep, download_name=student.name+"'s IEP Data.xlsx", as_attachment=True)

if __name__ == '__main__':
	app.run(debug=True)
#Launch the app in debug mode