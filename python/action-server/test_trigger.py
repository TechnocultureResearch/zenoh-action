import json
import yaml
from state_machine import StateMachine
import main

def test_statechart():
    with open('action.yml') as file:
        try:
            settingConfig = yaml.safe_load(file)  
        except yaml.YAMLError as err:
            print(err)

    settings = main.ActionSettings(**settingConfig)
    session = main.Session(settings)
    session.setup_action_server()
    model = StateMachine()
    model.init_session(session)
    value = session.get('/trigger/start')
    print(value)

test_statechart()

