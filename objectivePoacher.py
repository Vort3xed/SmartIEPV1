import re

testString = "0[0]get better at english;1(0)study more;0(0)do more practice quizzes;1[1]get better at math;1(1)use khan academy;1(1)study multiplication;0(0)do a lot more reading;1(1)learn about exponents;1[2]learn about roots;"

def is_goal(DATA, SPECIFICATION):
    start = DATA.find(SPECIFICATION)
    if start == -1:
        return False
    if start == 0:
        return False
    previous_char = DATA[start-1]
    return previous_char == ']'

def find_number_in_brackets(DATA, SPECIFICATION):
    start = DATA.find(SPECIFICATION)
    if start == -1:
        return None
    start_bracket = DATA.rfind('[', 0, start)
    end_bracket = DATA.find(']', start_bracket)
    if start_bracket == -1 or end_bracket == -1:
        return None
    return DATA[start_bracket+1:end_bracket]

def remove_string(s, substring):
    index = s.find(substring)
    if index != -1:
        s = s[:index-4] + s[index+len(substring)+1:]
    return s

def remove_strings_with_value(number, data):
    chunks = re.split(r';', data)
    modified_chunks = []
    for chunk in chunks:
        matches = re.findall(r'\((.*?)\)', chunk)
        
        found = False
        for match in matches:
            if str(number) in match:
                found = True
                break
        
        if not found:
            modified_chunks.append(chunk)
    
    modified_data = ';'.join(modified_chunks)
    
    return modified_data

def poachGoal(data,findString):
    if findString in data and is_goal(data,findString):
        return remove_strings_with_value(find_number_in_brackets(data,findString),remove_string(data,findString))

print(poachGoal(testString,"get better at english"))
