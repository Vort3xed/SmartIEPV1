import re
import json
from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, send_file
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.local import LocalProxy
from flask_sqlalchemy import SQLAlchemy
from utilities import *
from openpyxl import Workbook
from io import BytesIO
from openpyxl.styles import Alignment, Font
from flask_toastr import Toastr
import psycopg2
import os
#Import wastelands

db = SQLAlchemy()
#Define SQL Alchemy object

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fa1(0nwar3'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///people.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgressql://xmvleqgwilzadg:ec90bb70ab8ad3961a80cc29cab40682fb878bf219e176082f11dcfe8cfcd2df@ec2-3-208-74-199.compute-1.amazonaws.com:5432/dchctetf9iqttn'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://wzfngjfstkfzln:e38ae9c20d8874b1022fdf58b53afed4de288636a274b641a0e89452064ba7b7@ec2-44-215-40-87.compute-1.amazonaws.com:5432/d3749ss0lqr8hm'
# SQLALCHEMY_DATABASE_URI = os.environ.get('postgres://xmvleqgwilzadg:ec90bb70ab8ad3961a80cc29cab40682fb878bf219e176082f11dcfe8cfcd2df@ec2-3-208-74-199.compute-1.amazonaws.com:5432/dchctetf9iqttn').replace("://", "ql://", 1)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('postgres://xmvleqgwilzadg:ec90bb70ab8ad3961a80cc29cab40682fb878bf219e176082f11dcfe8cfcd2df@ec2-3-208-74-199.compute-1.amazonaws.com:5432/dchctetf9iqttn').replace("://", "ql://", 1)
#Create and configure flask app

db.init_app(app)
#Initialize the flask app with the database

login_manager = LoginManager()
login_manager.login_view = 'auth.signin'
login_manager.init_app(app)
#Create a login manager and set the login view to the sign in page. Then initialize the flask app with the login manager

toastr = Toastr(app)
#Create a toastr object and initialize the flask app with it

MAX_GOALS = 100
#Maximum possible amount of goals that can be created

STUDENT_LOG_NAME = ""
STUDENT_LOG_ID = 1
#The ID of the student that is currently being logged

STUDENT_TASK_NAME = ""
STUDENT_TASK_ID = 1
CURRENT_PAGE = 'students'

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
#Table of all students

# class Logs(db.Model):
# 	__tablename__ = 'logs'
# 	student_id = db.Column(db.Integer, primary_key=True)
# 	date = db.Column(db.String(200),nullable=False)
# 	log = db.Column(db.String(500),nullable=False)
# #Table of progress logs for each student

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
#Route 3: Accounts page

@main.route("/students", methods=('GET', 'POST'))
@login_required
def students():
	global CURRENT_PAGE
	CURRENT_PAGE = 'students'
	if request.method == 'POST':
		# global CURRENT_PAGE
		CURRENT_PAGE = 'students'
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
			query_student.name = name
			query_student.school_id = school_id
			query_student.grade = grade
			query_student.dateofbirth = dob
			query_student.disability = disability
			query_student.casemanager = casemanager
			query_student.last_annual_review = last_annual_review
			#Set the query_student's fields to the values in the text boxes

			db.session.commit()
			students = Students.query.all()
			accounts = Accounts.query.all()
			# return render_template('students.html',students=students,accounts=accounts)
			return redirect(url_for("main.students"))
			#Commit the changes to the database and render the students page
		else:
			# flash("Cannot Modify Student!")
			flash({'title': "SmartIEP:", 'message': "Cannot modify student!"}, 'error')
	accounts = Accounts.query.all()
	students = Students.query.all()
	return render_template('students.html',students=studentsByFilter(),accounts=accounts)
#Route 4: Students page

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
	if (CASE_MANAGER_FILTER != "NO FILTER" and GRADE_LEVEL_FILTER == "NO FILTER"):
		for student in all_students:
			if student.casemanager == CASE_MANAGER_FILTER:
				students_to_display.append(student)
	elif (GRADE_LEVEL_FILTER != "NO FILTER" and CASE_MANAGER_FILTER == "NO FILTER"):
		for student in all_students:
			if student.grade == int(GRADE_LEVEL_FILTER):
				students_to_display.append(student)
	elif (CASE_MANAGER_FILTER != "NO FILTER" and GRADE_LEVEL_FILTER != "NO FILTER"):
		for student in all_students:
			if student.casemanager == CASE_MANAGER_FILTER and student.grade == int(GRADE_LEVEL_FILTER):
				students_to_display.append(student)
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

		task_to_alternate = request.form.get(element_id+"alternate"+modify_student)
		print(task_to_alternate)
		query_student = Students.query.filter_by(student_id=modify_student).first()

		if (query_student.tasks.find(task_to_alternate[1:]) > -1):
			print(task_to_alternate[0])
			match task_to_alternate[0]:
				case "0":
					print("case entered")
					set_progress = query_student.tasks[:query_student.tasks.find(task_to_alternate[1:]) - 4] + "1" + query_student.tasks[query_student.tasks.find(task_to_alternate[1:]) - 4 + 1:]
					query_student.tasks = set_progress
					db.session.commit()
					if (CURRENT_PAGE == 'students'):
						return redirect(url_for('main.students'))
					elif (CURRENT_PAGE == 'tasks'):
						return redirect(url_for('main.expandtasks'))
					return redirect(url_for('main.students'))
				case "1":
					set_progress = query_student.tasks[:query_student.tasks.find(task_to_alternate[1:]) - 4] + "2" + query_student.tasks[query_student.tasks.find(task_to_alternate[1:]) - 4 + 1:]
					query_student.tasks = set_progress
					db.session.commit()
					if (CURRENT_PAGE == 'students'):
						return redirect(url_for('main.students'))
					elif (CURRENT_PAGE == 'tasks'):
						return redirect(url_for('main.expandtasks'))
					return redirect(url_for('main.students'))
				case "2":
					set_progress = query_student.tasks[:query_student.tasks.find(task_to_alternate[1:]) - 4] + "0" + query_student.tasks[query_student.tasks.find(task_to_alternate[1:]) - 4 + 1:]
					query_student.tasks = set_progress
					db.session.commit()
					if (CURRENT_PAGE == 'students'):
						return redirect(url_for('main.students'))
					elif (CURRENT_PAGE == 'tasks'):
						return redirect(url_for('main.expandtasks'))
					return redirect(url_for('main.students'))
				case _:
					flash({'title': "SmartIEP:", 'message': "Task does not exist!"}, 'error')
	if (CURRENT_PAGE == 'students'):
		return redirect(url_for('main.students'))
	elif (CURRENT_PAGE == 'tasks'):
		return redirect(url_for('main.expandtasks'))
	return redirect(url_for('main.students'))


@main.route("/setnodata", methods=('GET','POST'))
@login_required
def setnodata():
	if request.method == 'POST':
		button_value = request.form["setnodata"]
		modify_student = re.sub("\D", "", button_value)

		user_input = request.form["set_progress" + modify_student]

		query_student = Students.query.filter_by(student_id=modify_student).first()

		if (query_student.tasks.find(user_input) > -1):
			set_progress = query_student.tasks[:query_student.tasks.find(user_input) - 4] + "0" + query_student.tasks[query_student.tasks.find(user_input) - 4 + 1:]
			query_student.tasks = set_progress
			db.session.commit()
		else:
			flash({'title': "SmartIEP:", 'message': "Task does not exist!"}, 'error')

		return redirect(url_for('main.students'))

@main.route("/setinprogress", methods=('GET','POST'))
@login_required
def setinprogress():
	if request.method == 'POST':
		button_value = request.form["setinprogress"]
		modify_student = re.sub("\D", "", button_value)

		user_input = request.form["set_progress" + modify_student]

		query_student = Students.query.filter_by(student_id=modify_student).first()

		if (query_student.tasks.find(user_input) > -1):
			set_progress = query_student.tasks[:query_student.tasks.find(user_input) - 4] + "1" + query_student.tasks[query_student.tasks.find(user_input) - 4 + 1:]
			query_student.tasks = set_progress
			db.session.commit()
		else:
			flash({'title': "SmartIEP:", 'message': "Task does not exist!"}, 'error')

		return redirect(url_for('main.students'))
	
@main.route("/setcomplete", methods=('GET','POST'))
@login_required
def setcomplete():
	if request.method == 'POST':
		button_value = request.form["setcomplete"]
		modify_student = re.sub("\D", "", button_value)

		user_input = request.form["set_progress" + modify_student]

		query_student = Students.query.filter_by(student_id=modify_student).first()

		if (query_student.tasks.find(user_input) > -1):
			set_progress = query_student.tasks[:query_student.tasks.find(user_input) - 4] + "2" + query_student.tasks[query_student.tasks.find(user_input) - 4 + 1:]
			query_student.tasks = set_progress
			db.session.commit()
		else:
			flash({'title': "SmartIEP:", 'message': "Task does not exist!"}, 'error')

		return redirect(url_for('main.students'))

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
#Route 5: Export student data. This method does not render its own page.

@main.route("/addgoal", methods=('GET', 'POST'))
@login_required
def addGoals():
	if request.method == 'POST':
		button_value = request.form["submit_goal"]
		modify_student = re.sub("\D", "", button_value)
		#Remove all non-numeric characters from the button value to get the student ID. Student ID is linked to the number found in the button value.

		goal_to_append = request.form["add_goal"+modify_student]
		#Get the value in the text box for the goal to be added. Each text box is linked to each student by the student ID.

		query_student = Students.query.filter_by(student_id=modify_student).first()
		#Query the student to be modified

		if query_student:
			array_index = find_empty_array(parse_student_tasks(query_student.tasks))
			formatted_task = "0" + "["+str(array_index)+"]" + goal_to_append + ";"
			#Format the goal to be added to the student's tasks field

			query_student.tasks = query_student.tasks + formatted_task
			db.session.commit()
			#Add the formatted task to the student's tasks and commit the changes to the database

			if (CURRENT_PAGE == 'students'):
				return redirect(url_for('main.students'))
			elif (CURRENT_PAGE == 'tasks'):
				return redirect(url_for('main.expandtasks'))
			return redirect(url_for('main.students'))
		else:
			flash({'title': "SmartIEP:", 'message': "Cannot modify student!"}, 'error')
#Route 5: Add goal to student. This method does not render its own page. 

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
			formatted_task = "0("+str(int(goal_key)-1)+")"+objective_to_add+";"
			query_student.tasks = query_student.tasks + formatted_task
			#Format the objective to be added to the student's tasks field

			db.session.commit()
			if (CURRENT_PAGE == 'students'):
				return redirect(url_for('main.students'))
			elif (CURRENT_PAGE == 'tasks'):
				return redirect(url_for('main.expandtasks'))
			return redirect(url_for('main.students'))
			#Add the formatted objective to the student's tasks and commit the changes to the database
		else:
			flash({'title': "SmartIEP:", 'message': "Cannot remove objective!"}, 'error')
			if (CURRENT_PAGE == 'students'):
				return redirect(url_for('main.students'))
			elif (CURRENT_PAGE == 'tasks'):
				return redirect(url_for('main.expandtasks'))
			return redirect(url_for('main.students'))
#Route 6: Add objective to goal. This method does not render its own page.

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
		print(element_id+"remove_goal"+modify_student)
		print(goal_to_remove)
		#Get the value in the text box for the goal to be removed. Each text box is linked to each student by the student ID.

		query_student = Students.query.filter_by(student_id=modify_student).first()
		#Query the student to be modified

		if goal_to_remove in query_student.tasks and is_goal(query_student.tasks, goal_to_remove):
			#Check if the goal to be removed exists in the student's tasks and if it is a goal
			if query_student:
				clean_tasks = poachGoal(query_student.tasks,goal_to_remove)
				#Remove the goal and the objectives associated with it from the student's tasks

				query_student.tasks = clean_tasks
				#Set the student's tasks to equal the cleaned tasks

				db.session.commit()
				#return redirect(url_for('main.students'))
				accounts = Accounts.query.all()
				# return render_template('students.html',students=Students.query.all(),accounts=accounts)

				if (CURRENT_PAGE == 'students'):
					return redirect(url_for('main.students'))
				elif (CURRENT_PAGE == 'tasks'):
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
#Route 7: Remove goal from student. This method does not render its own page.

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

		if query_student and obj_to_remove in query_student.tasks and is_obj(query_student.tasks,obj_to_remove):
			#Check if the objective to be removed exists in the student's tasks and if it is an objective
			query_student.tasks = remove_string(query_student.tasks,obj_to_remove)

			#Remove the objective from the student's tasks
			db.session.commit()
			if (CURRENT_PAGE == 'students'):
				return redirect(url_for('main.students'))
			elif (CURRENT_PAGE == 'tasks'):
				return redirect(url_for('main.expandtasks'))
			return redirect(url_for('main.students'))
			#Commit the changes to the database and render the students page
		else:
			flash({'title': "SmartIEP:", 'message': "Objective to remove does not exist!"}, 'error')
			if (CURRENT_PAGE == 'students'):
				return redirect(url_for('main.students'))
			elif (CURRENT_PAGE == 'tasks'):
				return redirect(url_for('main.expandtasks'))
			return redirect(url_for('main.students'))
#Route 8: Remove objective from student. This method does not render its own page.

@main.route("/logs", methods=('GET', 'POST'))
@login_required
def logs():
	if request.method == 'POST':
		student_selected = request.form["selectstudent"]

		global STUDENT_LOG_NAME
		global STUDENT_LOG_ID
		#Get the student selected from the drop down menu and set the global variable STUDENT_LOG_NAME to the student selected
		STUDENT_LOG_NAME = student_selected

		student_selected_obj = Students.query.filter_by(name=student_selected).first()
		#Query the student selected to get the student ID

		STUDENT_LOG_ID = student_selected_obj.student_id
		# print(STUDENT_LOG_ID)

		#Set the global variable STUDENT_LOG_ID to the student ID of the student selected
		students = Students.query.all()
		return(render_template("progresslogs.html", students=students, student_log_id=STUDENT_LOG_ID))
		#Render the progress logs page with the student selected and the student ID of the student selected
	else:
		students = Students.query.all()
		# STUDENT_LOG_ID = students[0].student_id
		return(render_template("progresslogs.html", students=students, student_log_id=STUDENT_LOG_ID))
#Route 9: Progress logs. This method renders its own page.

@main.route("/expandtasks", methods=('GET', 'POST'))
@login_required
def expandtasks():
	global CURRENT_PAGE
	CURRENT_PAGE = 'tasks'
	if request.method == 'POST':
		CURRENT_PAGE = 'tasks'
		button_value = request.form["expandtasks"]
		modify_student = re.sub("\D", "", button_value)
		#Remove all non-numeric characters from the button value to get the student ID. Student ID is linked to the number found in the button value.

		query_student = Students.query.filter_by(student_id=modify_student).first()
		#Query the student to be modified

		if query_student:
			global STUDENT_TASK_ID
			STUDENT_TASK_ID = query_student.student_id

			students = Students.query.all()
			CURRENT_PAGE = 'tasks'
			print(CURRENT_PAGE)
			return(render_template("tasks.html", students=students, student_task_id=STUDENT_TASK_ID))
		else:
			flash({'title': "SmartIEP:", 'message': "Cannot expand tasks!"}, 'error')
			CURRENT_PAGE = 'students'
			return redirect(url_for('main.students'))
	print(CURRENT_PAGE)
	students = Students.query.all()
	return(render_template("tasks.html", students=students, student_task_id=STUDENT_TASK_ID))

@main.route("/modifylogs", methods=('GET', 'POST'))
@login_required
def modifylogs():
	if request.method == 'POST':
		log_date = request.form["logdate"]
		log_text = request.form["logtext"]

		modify_student = Students.query.filter_by(student_id=STUDENT_LOG_ID).first()
		#Query the student to be modified
		
		log_units = len(modify_student.logs[:-1].split("|"))
		#Get the amount of logs the student has

		json_parcel = '{"ID": ' + str(log_units + 1) + ', "Date": "' + log_date + '", "Log": "' + log_text + '"}'
		#Format the log to be added to the student's logs field

		modify_student.logs = modify_student.logs + json_parcel + "|"
		# print(modify_student.logs)
		db.session.commit()
		return(redirect(url_for("main.logs")))
	
@main.route("/viewlogs", methods=('GET', 'POST'))
@login_required
def viewlogs():
	if request.method == 'POST':
		button_value = request.form["viewlog"]
		student_key = re.sub("\D", "", button_value)
		#Remove all non-numeric characters from the button value to get the student ID. Student ID is linked to the number found in the button value.

		student = Students.query.filter_by(student_id=student_key).first()

		global STUDENT_LOG_ID
		STUDENT_LOG_ID = student.student_id
		# print(STUDENT_LOG_ID)

		return(redirect(url_for("main.logs")))

@main.route("/terminatestudent", methods=('GET', 'POST'))
@login_required
def terminatestudent():
	if request.method == 'POST':
		student_id = request.form["modid"]
		student = Students.query.filter_by(student_id=student_id).first()
		#Query the student to be terminated

		if student:
			db.session.delete(student)
			db.session.commit()
			
			all_students = Students.query.all()
			if len(all_students) > 0:
				global STUDENT_LOG_ID
				STUDENT_LOG_ID = all_students[0].student_id
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
	global STUDENT_LOG_ID
	STUDENT_LOG_ID = all_students[0].student_id
	# flash(STUDENT_LOG_ID)
	flash({'title': "SmartIEP:", 'message': STUDENT_LOG_ID}, 'error')
	return(redirect(url_for("main.terminatestudent")))

@main.route("/debugstudent", methods=('GET', 'POST'))
@login_required
def debugstudent():
	if request.method == 'POST':
		student_id = request.form["debugid"]
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
		student_id = request.form["wipeid"]
		student = Students.query.filter_by(student_id=student_id).first()
		#Query the student to have their data wiped

		if student:
			student.tasks = ""
			student.logs = '{"ID": 1, "Date": "Student Creation Date", "Log": "Initial Log"}|'
			db.session.commit()
			#Set the student's tasks to an empty string and commit the changes

			return(render_template("terminatestudent.html"))
		else:
			flash({'title': "SmartIEP:", 'message': "Student ID does not exist!"}, 'error')
	return(render_template("terminatestudent.html"))
#Route 11: Wipe student data. This method renders its own page.

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
			return(render_template("createstudent.html"))
		created_student = Students(name=name,school_id=school_id,grade=grade,dateofbirth=dateofbirth,casemanager=casemanager,disability=disability,last_annual_review=last_annual_review,tasks="",logs='{"ID": 1, "Date": "Student Creation Date", "Log": "Student Created"}|')
		#Create the student

		db.session.add(created_student)
		db.session.commit()

		# students = Students.query.all()
		# global STUDENT_LOG_ID
		# STUDENT_LOG_ID = students[0].student_id
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
			#If the user exists and the password is correct, log the user in and redirect them to the accounts page
			return redirect(url_for('main.accounts'))

	return render_template("login.html")
#Route 13: Sign in. This method renders its own page.

@auth.route("/register", methods=('GET', 'POST'))
@login_required
def register():
	if request.method == 'POST':
		callname = request.form["regcallname"]
		username = request.form["regusername"]
		password = request.form["regpassword"]
		#Get the values from the form

		user = Accounts.query.filter_by(username=username).first()
		#Query the user to be registered
		
		if user:
			flash({'title': "SmartIEP:", 'message': "Email already exists!"}, 'error')
			return render_template("register.html")
		account_user = Accounts(callname=callname, username=username, password=generate_password_hash(password, method='sha256'))
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
	for array in parse_student_tasks(student.tasks):
		if (array != []):
			if (array[0][0] == "0"):
				sheet['B' + str(opencell)] = "- Not Measureable: " + array[0][1:]
				sheet['B' + str(opencell)].alignment = Alignment(wrapText=True)
			elif (array[0][0] == "1"):
				sheet['B' + str(opencell)] = "- In Progress: " + array[0][1:]
				sheet['B' + str(opencell)].alignment = Alignment(wrapText=True)
			else:
				sheet['B' + str(opencell)] = "- Complete: " + array[0][1:]
				sheet['B' + str(opencell)].alignment = Alignment(wrapText=True)
			opencell = opencell + 1
	
			for task in array[1:]:
				if (task != ""):
					if (task[0] == "0"):
						sheet['B' + str(opencell)] = "- - Not Measureable: " + task[1:]
						sheet['B' + str(opencell)].alignment = Alignment(wrapText=True)
					elif (task[0] == "1"):
						sheet['B' + str(opencell)] = "- - In Progress: " + task[1:]
						sheet['B' + str(opencell)].alignment = Alignment(wrapText=True)
					else:
						sheet['B' + str(opencell)] = "- - Complete: " + task[1:]
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

	sheet.column_dimensions['C'].width = 10
	sheet.column_dimensions['D'].width = 20
	sheet.column_dimensions['E'].width = 50

	progressOpenCell = 3
	for log in student.logs[:-1].split("|"):
		log = json.loads(log)
		sheet['C' + str(progressOpenCell)] = str(log["ID"])
		sheet['D' + str(progressOpenCell)] = log["Date"]
		sheet['E' + str(progressOpenCell)] = log["Log"]
		sheet['E' + str(progressOpenCell)].alignment = Alignment(wrapText=True)
		progressOpenCell = progressOpenCell + 1
	
	student_iep = BytesIO()
	workbook.save(student_iep)
	student_iep.seek(0)
	return send_file(student_iep, download_name="Student IEP Data.xlsx", as_attachment=True)

if __name__ == '__main__':
	app.run(debug=True)
#Launch the app in debug mode