from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from io import BytesIO
from flask import send_file
import json
from app import parse_student_tasks

def generate_spreadsheet(student):
	workbook = Workbook()
	sheet = workbook.active

	sheet.column_dimensions['A'].width = 30
	sheet.column_dimensions['B'].width = 50

	sheet.title = student.name + "'s IEP Data"
	sheet['A1'] = "Student IEP Data"
	sheet['A1'].font = Font(size=20, bold=True)
	sheet['A2'] = "School ID: " + str(student.school_id)
	sheet['A3'] = "Name: " + student.name
	sheet['A4'] = "Grade: " + str(student.grade)
	sheet['A5'] = "Date of Birth: " + student.dateofbirth
	sheet['A6'] = "Case Manager: " + student.casemanager

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