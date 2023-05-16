testString = "0[0]get better at english;1(0)study more;0(0)do more practice quizzes;1[1]get better at math;1(1)use khan academy;1(1)study multiplication;0(0)do a lot more reading;1(1)learn about exponents;"

def remove_goal_and_objectives(data, task):
    # Find the index of the task in the data string
    task_index = data.find(task)

    # If the task is not found, do nothing
    if task_index == -1:
        return data

    # Find the goal identifier (number inside square brackets) for the task
    goal_identifier = data[task_index - 2]
    print(goal_identifier)

    # Remove the goal
    goal_start = data.rfind(";", 0, task_index - 4) + 1
    goal_end = task_index + len(task) + 1
    data = data[:goal_start] + data[goal_end:]

    # Remove all objectives associated with the goal
    objective_pattern = f"({goal_identifier})"
    objective_start = data.find(objective_pattern)

    while objective_start != -1:
        objective_end = data.find(";", objective_start) + 1
        data = data[:objective_start - 4] + data[objective_end:]
        objective_start = data.find(objective_pattern)

    return data

print(remove_goal_and_objectives(testString,"get better at english"))