import json
import pytest
import yaml
import state_machine
import main
'''
class StateMachine:
    def idle(self):
        print('State is busy')
'''
with open('statechart.json', 'r') as j:
     contents = json.loads(j.read())
with open('action.yml') as file:
    try:
        settingConfig = yaml.safe_load(file)  
    except yaml.YAMLError as err:
        print(err)

settings = main.ActionSettings(**settingConfig)

# 1. Start the action server session = Session(settings)
session = main.Session(settings)
session.setup_action_server()

model = state_machine.StateMachine(session)

json_file = json.loads(model.json_create())
test_json_format = json.loads(json.dumps({'statechart':{}, 'state':{}, 'trigger':{}})).keys()
assert json_file.keys() == test_json_format