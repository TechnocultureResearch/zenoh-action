import pytest
import zenoh
from zenoh import QueryTarget
from validators import ZenohConfig
import json
from server import Session
from state_machine import BaseStateMachine

model = Session()

args = ZenohConfig()
conf = zenoh.Config.from_file(
    args.config) if args.config != "" else zenoh.Config()
if args.mode != "":
    conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(args.mode))
if args.connect != "":
    conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(args.connect))
if args.listen != "":
    conf.insert_json5(zenoh.config.LISTEN_KEY, json.dumps(args.listen))
target = {
    'ALL': QueryTarget.ALL(),
    'BEST_MATCHING': QueryTarget.BEST_MATCHING(),
    'ALL_COMPLETE': QueryTarget.ALL_COMPLETE(),}.get('ALL')

zenoh.init_logger()
session = zenoh.open(conf)    

payload = {'reponse_code':'accepted', 'message':'Trigger is accepted and triggered'}
statemachine = BaseStateMachine()

@pytest.mark.parametrize("test_input, expected", 
                            [
                                ('/trigger?timestamp=1669897025.0759895&event=start', json.dumps(payload)),
                                ('/trigger?timestamp=1669897025.0759895&event=abort', json.dumps(payload)),
                                pytest.param("/statechart", json.dumps(statemachine.markup), marks=pytest.mark.xfail)
                            ])
def test_server_endpoints(test_input, expected):
    replies = session.get(args.base_key_expr+test_input, zenoh.ListCollector(), target=target)
    for reply in replies():
        try:
            value = reply.ok.payload.decode('utf-8')
        except:
            print('error')
    assert value == expected