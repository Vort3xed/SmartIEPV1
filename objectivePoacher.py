testString = "0[0]get better at english;1(0)study more;0(0)do more practice quizzes;1[1]get better at math;1(1)use khan academy;1(1)study multiplication;0(0)do a lot more reading;1(1)learn about exponents;"

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

def remove_task_by_number(data, number):
    tasks = data.split(";")
    new_data = ""
    for task in tasks:
        if f"({number})" in task:
            task_index = data.index(task)
            new_data = data[:task_index-4] + data[task_index+len(task):]
            data = new_data
    return new_data

def remove_elements(data_string, number):
    elements = data_string.split(';')  # Split the data string into individual elements
    result = []

    for element in elements:
        if '(' in element:
            element_number = int(element.split('(')[1].split(')')[0])
            if element_number == number:
                continue  # Skip elements with a number in parentheses matching the chosen number
        result.append(element)

    return ';'.join(result)

def poachGoal(data,findString):
    if findString in data and is_goal(data,findString):

        print(data)
        ownershipCodec = find_number_in_brackets(data,findString)
        print("codec:")
        print(ownershipCodec)
        goalless = remove_string(data,findString)
        print("goal removed")
        print(goalless)
        poached = remove_elements(goalless,ownershipCodec)
        print("objectives removed:")
        print(poached)

poachGoal(testString,"get better at english")
