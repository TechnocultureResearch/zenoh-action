from transitions.extensions.markup import MarkupMachine
import json
import pytest
import requests
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

assert model.is_idle()  # the model state was preserve
resp= requests.get("http://localhost:7447/Genotyper/1/DNAsensor/1/** ") # >>>>> State is busy
print(resp.status_code)