import re
from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, session
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from utilities import *
#Import wastelands

db = SQLAlchemy()
#Define SQL Alchemy object

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fa1(0nwar3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///people.db'
#Create and configure flask app

db.init_app(app)
#Initialize the flask app with the database

login_manager = LoginManager()
login_manager.login_view = 'auth.signin'
login_manager.init_app(app)
#Create a login manager and set the login view to the sign in page. Then initialize the flask app with the login manager

MAX_GOALS = 100
#Maximum possible amount of goals that can be created

STUDENT_LOG_NAME = ""
STUDENT_LOG_ID = 1
#The ID of the student that is currently being logged

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
	name = db.Column(db.String(200),nullable=False)
	grade = db.Column(db.Integer)
	dateofbirth = db.Column(db.String(200),nullable=False)
	tasks = db.Column(db.String(500),nullable=False)
	logs = db.Column(db.String(500),nullable=False)
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
	if request.method == 'POST':
		button_value = request.form["submit_button"]
		#Get the value of the button that was pressed
		modify_student = re.sub("\D", "", button_value)
		#Remove all non-numeric characters from the button value to get the student ID. Student ID is linked to the number found in the button value.
		
		name = request.form["boxmodname"+modify_student]
		grade = request.form["boxmodgrade"+modify_student]
		dob = request.form["boxmoddob"+modify_student]
		#Get the values in the text boxes for the student to be modified
		
		query_student = Students.query.filter_by(student_id=modify_student).first()
		#Query the student to be modified

		if query_student:
			query_student.name = name
			query_student.grade = grade
			query_student.dateofbirth = dob
			#Set the query_student's fields to the values in the text boxes

			db.session.commit()
			students = Students.query.all()
			return render_template('students.html',students=students)
			#Commit the changes to the database and render the students page
		else:
			flash("Cannot Modify Student!")

	students = Students.query.all()
	return render_template('students.html',students=students)
#Route 4: Students page

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
			array_index = find_next_empty_array(parse_student_tasks(query_student.tasks))
			formatted_task = "0" + "["+str(array_index + 1)+"]" + goal_to_append + ";"
			#Format the goal to be added to the student's tasks field

			query_student.tasks = query_student.tasks + formatted_task
			db.session.commit()
			#Add the formatted task to the student's tasks and commit the changes to the database

			return redirect(url_for('main.students'))
		else:
			flash("Cannot Modify Student!")
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
			return redirect(url_for('main.students'))
			#Add the formatted objective to the student's tasks and commit the changes to the database
		else:
			flash("Cannot remove goal!")
			return redirect(url_for('main.students'))
#Route 6: Add objective to goal. This method does not render its own page.

@main.route("/removegoal", methods=('GET', 'POST'))
@login_required
def removeGoals():
	if request.method == 'POST':
		button_value = request.form["remove_goal"]
		modify_student = re.sub("\D", "", button_value)
		#Remove all non-numeric characters from the button value to get the student ID. Student ID is linked to the number found in the button value.

		goal_to_remove = request.form["remove_goal"+modify_student]
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
				return redirect(url_for('main.students'))
				#Commit the changes to the database and render the students page
			else:
				flash("Cannot remove goal!")
		else:
			flash("Goal to remove does not exist!")
			return redirect(url_for('main.students'))
#Route 7: Remove goal from student. This method does not render its own page.

@main.route("/removeobjective", methods=('GET', 'POST'))
@login_required
def removeobjective():
	if request.method == 'POST':
		button_value = request.form["remove_obj"]
		modify_student = re.sub("\D", "", button_value)
		#Remove all non-numeric characters from the button value to get the student ID. Student ID is linked to the number found in the button value.

		obj_to_remove = request.form["remove_goal"+modify_student]
		#Get the value in the text box for the objective to be removed. Each text box is linked to each student by the student ID.

		query_student = Students.query.filter_by(student_id=modify_student).first()
		#Query the student to be modified

		if query_student and obj_to_remove in query_student.tasks and is_obj(query_student.tasks,obj_to_remove):
			#Check if the objective to be removed exists in the student's tasks and if it is an objective
			query_student.tasks = remove_string(query_student.tasks,obj_to_remove)

			#Remove the objective from the student's tasks
			db.session.commit()
			return redirect(url_for('main.students'))
			#Commit the changes to the database and render the students page
		else:
			flash("Objective to remove does not exist!")
			return redirect(url_for('main.students'))
#Route 8: Remove objective from student. This method does not render its own page.

@main.route("/logs", methods=('GET', 'POST'))
@login_required
def logs():
	if request.method == 'POST':
		student_selected = request.form["selectstudent"]
		global STUDENT_LOG_NAME
		global STUDENT_LOG_ID
		STUDENT_LOG_NAME = student_selected

		student_selected_obj = Students.query.filter_by(name=student_selected).first()

		STUDENT_LOG_ID = student_selected_obj.student_id

		students = Students.query.all()
		return(render_template("progresslogs.html", students=students, student_log_id=STUDENT_LOG_ID))
	else:
		students = Students.query.all()
		return(render_template("progresslogs.html", students=students, student_log_id=STUDENT_LOG_ID))

@main.route("/terminatestudent", methods=('GET', 'POST'))
@login_required
def terminatestudent():
	if request.method == 'POST':
		student_id = request.form["modid"]
		student = Students.query.filter_by(student_id=student_id).first()
		if student:
			db.session.delete(student)
			db.session.commit()
			return(render_template("terminatestudent.html"))
		else:
			flash("Student ID does not exist!")
	return(render_template("terminatestudent.html"))
#Route 9: Terminate student. This method renders its own page.

@main.route("/debugstudent", methods=('GET', 'POST'))
@login_required
def debugstudent():
	if request.method == 'POST':
		student_id = request.form["debugid"]
		student = Students.query.filter_by(student_id=student_id).first()
		if student:
			flash(student.tasks)
		else:
			flash("Student ID does not exist!")
	return(render_template("terminatestudent.html"))
#Route 10: Debug student. This method renders its own page.

@main.route("/wipedata", methods=('GET', 'POST'))
@login_required
def wipedata():
	if request.method == 'POST':
		student_id = request.form["wipeid"]
		student = Students.query.filter_by(student_id=student_id).first()

		if student:
			student.tasks = ""
			db.session.commit()
			return(render_template("terminatestudent.html"))
		else:
			flash("Student ID does not exist!")
	return(render_template("terminatestudent.html"))
#Route 11: Wipe student data. This method renders its own page.

@main.route("/createstudent", methods=('GET', 'POST'))
@login_required
def createstudent():
	if request.method == 'POST':
		name = request.form["stuname"]
		grade = request.form["stugrade"]
		dateofbirth = request.form["studob"]
		tasks = request.form["stutasks"]

		user = Students.query.filter_by(name=name).first()
		if user:
			flash('Student already exists')
			return(render_template("createstudent.html"))
		created_student = Students(name=name,grade=grade,dateofbirth=dateofbirth,tasks=tasks,logs="")
		db.session.add(created_student)
		db.session.commit()
	return redirect(url_for('main.students'))
#Route 12: Create student. This method renders its own page.


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
			return redirect(url_for('main.accounts'))

	return render_template("login.html")
#Route 13: Sign in. This method renders its own page.

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
#Route 14: Register an account. This method renders its own page.

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))
#Route 15: Logout. This method does not render its own page.

app.register_blueprint(auth)
app.register_blueprint(main)
#Register the blueprints

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
					part = re.sub("\[.*?\]","[]",part)
					part = part.replace("[","").replace("]","")
					goalArrays[counter].append(part)
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

def parse_student_tasks(newData):
    if (newData != ""):
        goalArrays = []
        for i in range(MAX_GOALS):
            goalArrays.append([])
        parts = newData[:-1].split(";")
        counter = 0
        for part in parts:
            if part[1] == "[":
                part = re.sub("\[.*?\]","[]",part)
                part = part.replace("[","").replace("]","")
                goalArrays[counter].append(part)
                counter = counter + 1
        for part in parts:
            if part[1] == "(":
                goalKey = int(part[part.find("(")+1:part.find(")")])
                part = re.sub("\(.*?\)","()",part)
                part = part.replace("(","").replace(")","")
                goalArrays[goalKey].append(part)            
        return goalArrays
    else:
        return []
#This is the same method as above, but it is used for the back end on the student page.

# def find_next_empty_array(arr):
#     for i in range(len(arr)):
#         if not arr[i]:
#             return i
#     return -1

# def remove_string(s, substring):
#     index = s.find(substring)
#     if index != -1:
#         s = s[:index-4] + s[index+len(substring)+1:]
#     return s

# def is_goal(DATA, SPECIFICATION):
#     start = DATA.find(SPECIFICATION)
#     if start == -1:
#         return False
#     if start == 0:
#         return False
#     previous_char = DATA[start-1]
#     return previous_char == ']'

# def is_obj(DATA, SPECIFICATION):
#     start = DATA.find(SPECIFICATION)
#     if start == -1:
#         return False
#     if start == 0:
#         return False
#     previous_char = DATA[start-1]
#     return previous_char == ')'

# def find_number_in_brackets(DATA, SPECIFICATION):
#     start = DATA.find(SPECIFICATION)
#     if start == -1:
#         return None
#     start_bracket = DATA.rfind('[', 0, start)
#     end_bracket = DATA.find(']', start_bracket)
#     if start_bracket == -1 or end_bracket == -1:
#         return None
#     return DATA[start_bracket+1:end_bracket]

# def remove_string(s, substring):
#     index = s.find(substring)
#     if index != -1:
#         s = s[:index-4] + s[index+len(substring)+1:]
#     return s

# def remove_strings_with_value(number, data):
#     chunks = re.split(r';', data)
#     modified_chunks = []
#     for chunk in chunks:
#         matches = re.findall(r'\((.*?)\)', chunk)
        
#         found = False
#         for match in matches:
#             if str(number) in match:
#                 found = True
#                 break
        
#         if not found:
#             modified_chunks.append(chunk)
    
#     modified_data = ';'.join(modified_chunks)
    
#     return modified_data

# # def poachGoal(data,findString):
# #     if findString in data and is_goal(data,findString):
# # 	    return remove_strings_with_value(find_number_in_brackets(data,findString),remove_string(data,findString))

# def poachGoal(data,findString):
#     return remove_strings_with_value(find_number_in_brackets(data,findString),remove_string(data,findString))
    
if __name__ == '__main__':
	app.run(debug=True)
#Launch the app in debug mode