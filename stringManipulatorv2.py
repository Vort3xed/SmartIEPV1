import json
MAX_GOALS = 50

#tasks = '{"Type": 0, "Index": 0, "Task": "No data math goal at index 0", "Progress": 0, "Category": "Math"}|{"Type": 1, "Index": 0, "Task": "in progress objective for index 0", "Progress": 1}|{"Type": 1, "Index": 1, "Task": "completed english goal at index 1", "Progress": 2, "Category": "English"}|'
# tasksv2 = '{"Type": 0, "Index": "0", "Task": "tset", "Progress": 0, "Category": "Math"}|{"Type": 1, "Index": "0", "Task": "test", "Progress": 0}|{"Type": 1, "Index": 0, "Task": "dsfsdf", "Progress": 1}|{"Type": 1, "Index": "0", "Task": "dddd", "Progress": 0}|{"Type": 1, "Index": 0, "Task": "rwrefs", "Progress": 1}|{"Type": 0, "Index": "1", "Task": "vsdvsdfadsf", "Progress": 0, "Category": "Math"}|{"Type": 0, "Index": 2, "Task": "asdfasdf", "Progress": 2}|{"Type": 1, "Index": "2", "Task": "bcvxcxvb", "Progress": 0}|'

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

# def remove_goalv2(goal,task_list):
#     if (task_list != ""):
#         parts = task_list[:-1].split("|")
#         for part in parts:
#             if json.loads(part)["Task"] == goal and json.loads(part)["Type"] == 0:
#                 index = json.loads(part)["Index"]
#                 parts.remove(part)
#         for part2 in parts:
#             if json.loads(part2)["Index"] == index and json.loads(part2)["Type"] == 1:
#                 parts.remove(part2)
#         if len(parts) == 0:
#             return ""
#         return "|".join(parts) + "|"
#     return task_list

def remove_goalv2(goal, task_list):
    if task_list != "":
        parts = task_list[:-1].split("|")
        remaining_parts = []
        index_to_remove = None

        for part in parts:
            part_dict = json.loads(part)
            if part_dict["Task"] == goal and part_dict["Type"] == 0:
                index_to_remove = int(part_dict["Index"])
            else:
                remaining_parts.append(part)

        if index_to_remove is not None:
            final_parts = []
            for part in remaining_parts:
                part_dict = json.loads(part)
                if int(part_dict["Index"]) != index_to_remove or part_dict["Type"] != 1:
                    final_parts.append(part)

            if len(final_parts) == 0:
                return ""
            return "|".join(final_parts) + "|"

    return task_list

def set_progressv2(task,progress,task_list):
    if (task_list != ""):
        parts = task_list[:-1].split("|")
        finalarray = []
        for part in parts:
            if json.loads(part)["Task"] == task:
                if (json.loads(part)["Type"] == 0):
                    newPart = '{"Type": ' + str(json.loads(part)["Type"]) + ', "Index": ' + str(json.loads(part)["Index"]) + ', "Task": "' + str(json.loads(part)["Task"]) + '", "Progress": ' + str(progress) + ', "Category": "' + str(json.loads(part)["Category"]) + '"}'
                else:
                    newPart = '{"Type": ' + str(json.loads(part)["Type"]) + ', "Index": ' + str(json.loads(part)["Index"]) + ', "Task": "' + str(json.loads(part)["Task"]) + '", "Progress": ' + str(progress) + '}'
                finalarray.append(newPart)
            else:
                finalarray.append(part)
        return "|".join(finalarray) + "|"
    return task_list

        
# print(tasksv2)
# print()
# tasksv2 = remove_goalv3("tset",tasksv2)
# print()
# print(tasksv2)

# print(parse_student_tasks(tasks))
# print()
# print(remove_objective("completed english goal at index 1",tasks))
# print(remove_objective("in progress objective for index 0",tasks))
# print(remove_goal("No data math goal at index 0",tasks))