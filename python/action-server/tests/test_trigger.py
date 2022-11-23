from transitions.extensions.markup import MarkupMachine
import json
import pytest
import requests
import yaml
import state_machine
import main

url = 'https://localhost:7447'

def test_statechart():
    with open('action.yml') as file:
        try:
            settingConfig = yaml.safe_load(file)  
        except yaml.YAMLError as err:
            print(err)

    settings = main.ActionSettings(**settingConfig)
    session = main.Session(settings)
    model = state_machine.StateMachine(session)
    test_json = json.loads(model.json_create())
    response = requests.post(url, test_json['trigger'])
    assert response.status_code == 201

