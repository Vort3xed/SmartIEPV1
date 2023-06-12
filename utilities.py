import re
import json

MAX_GOALS = 100

def find_next_empty_array(arr):
    for i in range(len(arr)):
        if not arr[i]:
            return i
    return -1
# Returns the index of the first empty array in the array of arrays

def find_empty_array(arr):
    index = 0
    for array in arr:
        if array == []:
            return index
        index += 1
    return -1

def remove_string(s, substring):
    index = s.find(substring)
    if index != -1:
        s = s[:index-4] + s[index+len(substring)+1:]
    return s
# Removes a string from a string

def is_goal(DATA, SPECIFICATION):
    start = DATA.find(SPECIFICATION)
    if start == -1:
        return False
    if start == 0:
        return False
    previous_char = DATA[start-1]
    return previous_char == ']'
# Checks if a string is a goal

def is_obj(DATA, SPECIFICATION):
    start = DATA.find(SPECIFICATION)
    if start == -1:
        return False
    if start == 0:
        return False
    previous_char = DATA[start-1]
    return previous_char == ')'
# Checks if a string is an objective

def find_number_in_brackets(DATA, SPECIFICATION):
    start = DATA.find(SPECIFICATION)
    if start == -1:
        return None
    start_bracket = DATA.rfind('[', 0, start)
    end_bracket = DATA.find(']', start_bracket)
    if start_bracket == -1 or end_bracket == -1:
        return None
    return DATA[start_bracket+1:end_bracket]
# Finds the number in brackets before a string

def remove_strings_with_value(number, data):
    chunks = re.split(r';', data)
    #Split the string into chunks using a semicolon as a delimiter

    modified_chunks = []
    for chunk in chunks:
        matches = re.findall(r'\((.*?)\)', chunk)
        found = False
        for match in matches:
            if str(number) in match:
                found = True
                break
        #Find all the substrings in brackets in the chunk and check if the number is in any of them
        
        if not found:
            modified_chunks.append(chunk)
        #If the number is not in any of the substrings in brackets, add the chunk to the modified chunks
    
    modified_data = ';'.join(modified_chunks)
    #Join the modified chunks into a string using a semicolon as a delimiter

    return modified_data


def poachGoal(data,findString):
    return remove_strings_with_value(find_number_in_brackets(data,findString),remove_string(data,findString))

def remove_log(alllogs,specific_log_id):
	logs = alllogs[:-1].split("|")
	new_logs = ""
	for log in logs:
		if (json.loads(log)['ID'] != int(specific_log_id)):
			new_logs = new_logs + log + "|"
	return new_logs

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
# Removes a goal from a string 