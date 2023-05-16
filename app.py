import re
from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, session
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
def accounts():
	accounts = Accounts.query.all()
	return render_template('accounts.html',accounts=accounts)

@main.route("/students", methods=('GET', 'POST'))
@login_required
def students():
	if request.method == 'POST':
		button_value = request.form["submit_button"]
		modify_student = re.sub("\D", "", button_value)
		
		name = request.form["boxmodname"+modify_student]
		grade = request.form["boxmodgrade"+modify_student]
		dob = request.form["boxmoddob"+modify_student]
		
		query_student = Students.query.filter_by(student_id=modify_student).first()

		if query_student:
			query_student.name = name
			query_student.grade = grade
			query_student.dateofbirth = dob

			db.session.commit()
			students = Students.query.all()
			return render_template('students.html',students=students)
		else:
			flash("Cannot Modify Student!")

	students = Students.query.all()
	return render_template('students.html',students=students)

#make it so that the if statements happen based on the button pressed, and make it so that the identification delimeter gets removed with the string
# @main.route("/modgoals", methods=('GET', 'POST'))
# @login_required
# def modGoals():
# 	if request.method == 'POST':
# 		#the possible issue heere is that when remove goal button is clicked, it doesnt actually show up in the stack for it to be analyzed by the program
# 		# if re.sub(r'\d','',request.form["submit_goal"]) == "submit_goal":
# 		try:
# 			button_value = request.form["submit_goal"]
# 			modify_student = re.sub("\D", "", button_value)

# 			goal_to_append = request.form["modgoal"+modify_student]

# 			query_student = Students.query.filter_by(student_id=modify_student).first()

# 			if query_student:
# 				array_index = find_next_empty_array(parse_student_tasks(query_student.tasks))
# 				formatted_task = "0" + "["+str(array_index)+"]" + goal_to_append + ";"
# 				query_student.tasks = query_student.tasks + formatted_task

# 				db.session.commit()
# 				return redirect(url_for('main.students'))
# 			else:
# 				flash("Cannot add goal!")
# 		except:
# 			print("try has failed")
# 			button_value = request.form["remove_goal"]
# 			modify_student = re.sub("\D", "", button_value)

# 			goal_to_remove = request.form["modgoal"+modify_student]

# 			query_student = Students.query.filter_by(student_id=modify_student).first()

# 			if query_student:
# 				print(query_student)
# 				print("student was queried")
# 				query_student.tasks.replace(goal_to_remove,"")
# 				db.session.commit()
# 				return redirect(url_for('main.students'))
# 			else:
# 				flash("Cannot remove goal!")

@main.route("/addgoal", methods=('GET', 'POST'))
@login_required
def addGoals():
	if request.method == 'POST':
		button_value = request.form["submit_goal"]
		modify_student = re.sub("\D", "", button_value)

		goal_to_append = request.form["add_goal"+modify_student]

		query_student = Students.query.filter_by(student_id=modify_student).first()

		if query_student:
			array_index = find_next_empty_array(parse_student_tasks(query_student.tasks))
			formatted_task = "0" + "["+str(array_index)+"]" + goal_to_append + ";"
			query_student.tasks = query_student.tasks + formatted_task

			db.session.commit()
			return redirect(url_for('main.students'))
		else:
			flash("Cannot Modify Student!")

# def remove_objectives_for_goal(data, goal):
#     # Find the index of the goal in the data string
#     goal_start = data.find(f"{goal}[")
#     if goal_start == -1:
#         return data

#     # Find the value in the square bracket for the given goal
#     goal_value = int(data[goal_start+len(goal):goal_start+len(goal)+1])

#     # Find all objectives that belong to the given goal
#     objectives = []
#     i = goal_start + len(goal) + 2
#     while i < len(data):
#         if data[i] == ')':
#             objective_value = int(data[i-2])
#             if objective_value == goal_value:
#                 objective_end = data.find(';', i)
#                 objectives.append((i-4, objective_end))
#             i = objective_end
#         else:
#             i += 1

#     # Remove all objectives belonging to the given goal
#     for start, end in reversed(objectives):
#         data = data[:start] + data[end+1:]

#     return data

@main.route("/removegoal", methods=('GET', 'POST'))
@login_required
def removeGoals():
	if request.method == 'POST':
		button_value = request.form["remove_goal"]
		modify_student = re.sub("\D", "", button_value)

		goal_to_remove = request.form["remove_goal"+modify_student]

		query_student = Students.query.filter_by(student_id=modify_student).first()

		if query_student:
			print(query_student.tasks)
			if query_student.tasks.__contains__(goal_to_remove):
				updated_tasks = remove_string(query_student.tasks,goal_to_remove)
				no_objectives_for_goals = remove_objectives_for_goal(updated_tasks,goal_to_remove)
				query_student.tasks = no_objectives_for_goals
				db.session.commit()
			print(query_student.tasks)
			
			return redirect(url_for('main.students'))
		else:
			flash("Cannot Modify Student!")

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
		created_student = Students(name=name,grade=grade,dateofbirth=dateofbirth,tasks=tasks)
		db.session.add(created_student)
		db.session.commit()
	return(render_template("createstudent.html"))


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
			return redirect(url_for('main.accounts'))

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

MAX_GOALS = 10

@app.context_processor
def utility_processor():
	# def parse_tasks(newData):
	# 	goalArrays = []

	# 	for i in range(MAX_GOALS):
	# 		goalArrays.append([])

	# 	parts = newData[:-1].split(";")
	# 	counter = 0
	# 	for part in parts:
	# 		if part[1] == "[":
	# 			part = re.sub("\[.*?\]","[]",part)
	# 			part = part.replace("[","").replace("]","")
	# 			goalArrays[counter].append(part)
	# 			counter = counter + 1
	# 	for part in parts:
	# 		if part[1] == "(":
	# 			goalKey = int(part[part.find("(")+1:part.find(")")])
	# 			part = re.sub("\(.*?\)","()",part)
	# 			part = part.replace("(","").replace(")","")
	# 			goalArrays[goalKey].append(part)
	# 	return goalArrays
	def parse_tasks(newData):
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
	return dict(parse_tasks=parse_tasks)

# def parse_student_tasks(newData):
# 	goalArrays = []

# 	for i in range(MAX_GOALS):
# 		goalArrays.append([])

# 	parts = newData[:-1].split(";")
# 	counter = 0
# 	for part in parts:
# 		if part[1] == "[":
# 			part = re.sub("\[.*?\]","[]",part)
# 			part = part.replace("[","").replace("]","")
# 			goalArrays[counter].append(part)
# 			counter = counter + 1
# 	for part in parts:
# 		if part[1] == "(":
# 			goalKey = int(part[part.find("(")+1:part.find(")")])
# 			part = re.sub("\(.*?\)","()",part)
# 			part = part.replace("(","").replace(")","")
# 			goalArrays[goalKey].append(part)
# 	return goalArrays

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

def find_next_empty_array(arr):
    for i in range(len(arr)):
        if not arr[i]:
            return i
    return -1

def remove_string(s, substring):
    index = s.find(substring)
    if index != -1:
        s = s[:index-4] + s[index+len(substring)+1:]
    return s

if __name__ == '__main__':
	app.run(debug=True)