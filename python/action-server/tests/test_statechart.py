import json
import yaml
from state_machine import StateMachine
import main
import settings

def test_statechart():
    with open('action.yml') as file:
        try:
            settingConfig = yaml.safe_load(file)  
        except yaml.YAMLError as err:
            print(err)

    setting = settings.ActionSettings(**settingConfig)
    session_obj = main.Session(setting)
    session_obj.setup_action_server()
    model = StateMachine()
    model.init_session(session_obj)
    model.statechart()
    value = session_obj.get('/statechart')
    assert json.loads(value) == model.markup

test_statechart()

