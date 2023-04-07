import re

newData = "0[0]get better at english;1(0)study more;0(0)do more practice quizzes;1[1]get better at math;1(1)use khan academy;1(1)study multiplication;0(0)do a shit more reading;1(1)learn about exponents;"
def parse_goals(newData):
    tasks1 = []
    tasks2 = []
    tasks3 = []
    tasks4 = []
    tasks5 = []
    goalArrays = [tasks1,tasks2,tasks3,tasks4,tasks5]
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
print(parse_goals(newData))