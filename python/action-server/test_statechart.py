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
    model.statechart()
    value = session.get('/statechart')
    assert json.loads(value) == model.markup

test_statechart()

