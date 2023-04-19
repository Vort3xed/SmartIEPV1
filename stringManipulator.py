import re

newData = "0[0]get better at english;1(0)study more;0(0)do more practice quizzes;1[1]get better at math;1(1)use khan academy;1(1)study multiplication;0(0)do a lot more reading;1(1)learn about exponents;"
MAX_GOALS = 5
noDataString = ""
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
print(parse_student_tasks(noDataString))