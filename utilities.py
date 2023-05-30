import re

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
# Removes a goal from a string 