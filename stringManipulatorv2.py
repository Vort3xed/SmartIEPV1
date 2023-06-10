import json
MAX_GOALS = 5

tasks = '{"Type": 0, "Index": 0, "Task": "No data math goal at index 0", "Progress": 0, "Category": "Math"}|{"Type": 1, "Index": 0, "Task": "in progress objective for index 0", "Progress": 1}|{"Type": 1, "Index": 1, "Task": "completed english goal at index 1", "Progress": 2, "Category": "English"}|'

def parse_student_tasksv2(tasks):
    if (tasks != ""):
        goalArrays = []
        for i in range(MAX_GOALS):
            goalArrays.append([])
        parts = tasks[:-1].split("|")
        for part in parts:
            if json.loads(part)["Type"] == 0:
                goalArrays[int(json.loads(part)["Index"])].append(part)
        for part in parts:
            if json.loads(part)["Type"] == 1:
                goalArrays[int(json.loads(part)["Index"])].append(part)
        return goalArrays
    return [[]]

def remove_objectivev2(obj,task_list):
    if (task_list != ""):
        parts = task_list[:-1].split("|")
        for part in parts:
            if json.loads(part)["Task"] == obj and json.loads(part)["Type"] == 1:
                parts.remove(part)
        if len(parts) == 0:
            return ""
        return "|".join(parts) + "|"
    return task_list

def remove_goalv2(goal,task_list):
    if (task_list != ""):
        parts = task_list[:-1].split("|")
        for part in parts:
            if json.loads(part)["Task"] == goal and json.loads(part)["Type"] == 0:
                index = json.loads(part)["Index"]
                parts.remove(part)
        for part2 in parts:
            if json.loads(part2)["Index"] == index:
                parts.remove(part2)
        if len(parts) == 0:
            return ""
        return "|".join(parts) + "|"
    return task_list

def set_progressv2(task,progress,task_list):
    if (task_list != ""):
        parts = task_list[:-1].split("|")
        finalarray = []
        for part in parts:
            if json.loads(part)["Task"] == task:

                newPart = '{"Type": ' + str(json.loads(part)["Type"]) + ', "Index": ' + str(json.loads(part)["Index"]) + ', "Task": "' + str(json.loads(part)["Task"]) + '", "Progress": ' + str(progress) + '}'
                finalarray.append(newPart)
            else:
                finalarray.append(part)
        return "|".join(finalarray) + "|"
    return task_list

        
    
# print(parse_student_tasks(tasks))
# print()
# print(remove_objective("completed english goal at index 1",tasks))
# print(remove_objective("in progress objective for index 0",tasks))
# print(remove_goal("No data math goal at index 0",tasks))