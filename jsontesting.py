import json

LOG_STRING = '{"ID": 3, "Date": "Feburary 2nd, 2002", "Log": "lil jimmy did some math practice"}|{"ID": 4, "Date": "January 1st, 2001", "Log": "field text"}'

LOGS = LOG_STRING.split("|")

json_unit = json.loads(LOGS[0])

print(json_unit['ID'])
print(json_unit['Date'])
print(json_unit['Log'])

json_unit2 = json.loads(LOGS[1])

print(json_unit2['ID'])
print(json_unit2['Date'])
print(json_unit2['Log'])

# id = 4
# date = "January 1st, 2001"
# log = "field text"

# JSON_ADD_STRING = {
#     "ID": id,
#     "Date": date,
#     "Log": log
# }

# compiled_json = json.dumps(JSON_ADD_STRING)
# print(compiled_json)