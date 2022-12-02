import pytest
import zenoh
from zenoh import QueryTarget
from config import ZenohValidator, ZenohConfig
import json
from server import Session
from state_machine import BaseStateMachine
from pydantic import ValidationError

model = Session()

zenoh_config = ZenohConfig()
conf_obj, args = zenoh_config.zenohconfig()
target = {
    'ALL': QueryTarget.ALL(),
    'BEST_MATCHING': QueryTarget.BEST_MATCHING(),
    'ALL_COMPLETE': QueryTarget.ALL_COMPLETE(),}.get('ALL')

zenoh.init_logger()
session = zenoh.open(conf_obj)    
statemachine = BaseStateMachine()

@pytest.mark.parametrize("test_input, expected", 
                            [
                                ("/statechart", json.dumps(statemachine.markup, indent=3))
                            ])
def test_server_endpoint_statechart(test_input, expected):
    replies = session.get(args.base_key_expr+test_input, zenoh.ListCollector(), target=target)
    for reply in replies():
        try:
            value = reply.ok.payload.decode('utf-8')
        except:
            print(reply.err.payload.decode('utf-8'))
    assert value == expected

@pytest.mark.parametrize("test_input, expected", 
                            [
                                ('/trigger?timestamp=1669897025.0759895&event=start', json.dumps({'reponse_code':'accepted', 'message':'Trigger is accepted and triggered'})),
                                ('/trigger?timestamp=1669897025.0759895&event=abort', json.dumps({'reponse_code':'accepted', 'message':'Trigger is accepted and triggered'})),
                                ('/trigger?timestamp=1669899025.0759895&event=done', json.dumps({"reponse_code": "rejected", "message": "1 validation error for EventModel\nevent\n  Event is not valid or you are not allowed to trigger event. (type=value_error)"})),
                                ('/trigger?timestamp=1669899025.0759895&event=clearancetimeout', json.dumps({"reponse_code": "rejected", "message": "1 validation error for EventModel\nevent\n  Event is not valid or you are not allowed to trigger event. (type=value_error)"}))
                            ])
def test_server_endpoints_trigger(test_input, expected):
    replies = session.get(args.base_key_expr+test_input, zenoh.ListCollector(), target=target)
    for reply in replies():
        try:
            value = reply.ok.payload.decode('utf-8')
        except ValidationError:
            value = reply.err.payload.decode('utf-8')
        except ValueError:
            value = reply.err.payload.decode('utf-8')
    assert value == expected