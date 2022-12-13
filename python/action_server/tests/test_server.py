import pytest
import zenoh
from zenoh import QueryTarget
from config import ZenohConfig
import json
from server import Session

model = Session()
zenoh_config = ZenohConfig()
conf_obj, args = zenoh_config.zenohconfig()
target = {
    'ALL': QueryTarget.ALL(),
    'BEST_MATCHING': QueryTarget.BEST_MATCHING(),
    'ALL_COMPLETE': QueryTarget.ALL_COMPLETE(),}.get('ALL')

zenoh.init_logger()
session = zenoh.open(conf_obj)

def test_statechart_returns_json(test_input="/statechart"):
    replies = session.get(args.base_key_expr+test_input, zenoh.ListCollector(), target=target)
    for reply in replies():
        json.loads(reply.ok.payload.decode('utf-8'))

def test_statechart_checks_if_state_exists_in_json(test_input="/statechart"):
    replies = session.get(args.base_key_expr+test_input, zenoh.ListCollector(), target=target)
    for reply in replies():
        json.loads(reply.ok.payload.decode('utf-8'))["states"]

def test_statechart_checks_if_transition_exists_in_json(test_input="/statechart"):
    replies = session.get(args.base_key_expr+test_input, zenoh.ListCollector(), target=target)
    for reply in replies():
        json.loads(reply.ok.payload.decode('utf-8'))["transitions"]

@pytest.mark.parametrize("test_input", 
                            [
                                ('/trigger?timestamp=1669897025.0759895&event=start'),
                                ('/trigger?timestamp=1669897025.0759895&event=abort')
                                ])                               
def test_trigger_accepts_timestamped_events(test_input):
    replies = session.get(args.base_key_expr+test_input, zenoh.ListCollector(), target=target)
    for reply in replies():
        json.loads(reply.ok.payload.decode('utf-8'))["response_code"] == "accepted"

@pytest.mark.parametrize("test_input", 
                            [
                                ('/trigger?timestamp=1669899025.0759895&event=done'),
                                ('/trigger?timestamp=1669899025.0759895&event=clearancetimeout')])
def test_trigger_rejects_notallowed_events(test_input):
    replies = session.get(args.base_key_expr+test_input, zenoh.ListCollector(), target=target)
    for reply in replies():
        json.loads(reply.ok.payload.decode('utf-8')) == "rejected"

def test_trigger_rejects_invalid_timestamp(test_input="/trigger?event=done"):
    replies = session.get(args.base_key_expr+test_input, zenoh.ListCollector(), target=target)
    for reply in replies():
        json.loads(reply.ok.payload.decode('utf-8'))["response_code"] == "rejected"


@pytest.mark.parametrize("test_input",
                            [
                                ('/trigger?timestamp=1669899025.0759895&event=awaitingclearanceerr'),
                                ("/trigger?timestamp=1669899025.0759895")
                    ])
def test_trigger_rejects_invalid_event(test_input):
    replies = session.get(args.base_key_expr+test_input, zenoh.ListCollector(), target=target)
    for reply in replies():
        json.loads(reply.ok.payload.decode('utf-8'))["response_code"] == "rejected"