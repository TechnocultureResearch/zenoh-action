import pytest
import zenoh
from stateMachine import BaseStateMachine, Publisher
from config import ZenohConfig, ZenohSettings
import json
from typing import Tuple
from server import Session, QueryableCallback

@pytest.fixture
def session():
    settings = ZenohSettings()
    zenoh_config = ZenohConfig(settings)
    pub = Publisher(settings)
    pub.createZenohPublisher()
    statemachine = BaseStateMachine()
    conf_obj= zenoh_config.zenohconfig()
    callback = QueryableCallback(settings, statemachine)
    _session = Session(settings, statemachine, callback)
    zenoh.init_logger()
    session = zenoh.open(conf_obj)
    return session, settings

def test_statechart_returns_json(session, test_input="/statechart"):
    _session, settings = session
    replies = _session.get(settings.base_key_expr+test_input, zenoh.ListCollector(), target=zenoh.QueryTarget.ALL())
    for reply in replies():
        json.loads(reply.ok.payload.decode('utf-8'))

def test_statechart_checks_if_state_exists_in_json(session, test_input="/statechart"):
    _session, settings = session
    replies = _session.get(settings.base_key_expr+test_input, zenoh.ListCollector(), target=zenoh.QueryTarget.ALL())
    for reply in replies():
        json.loads(reply.ok.payload.decode('utf-8'))["states"]

def test_statechart_checks_if_transition_exists_in_json(session, test_input="/statechart"):
    _session, settings = session
    replies = _session.get(settings.base_key_expr+test_input, zenoh.ListCollector(), target=zenoh.QueryTarget.ALL())
    for reply in replies():
        json.loads(reply.ok.payload.decode('utf-8'))["transitions"]

@pytest.mark.parametrize("test_input", 
                            [
                                ('/trigger?timestamp=1669897025.0759895&event=start')
                                ])                               
def test_trigger_accepts_timestamped_events(session, test_input):
    _session, settings = session
    replies = _session.get(settings.base_key_expr+test_input, zenoh.ListCollector(), target=zenoh.QueryTarget.ALL())
    for reply in replies():
        json.loads(reply.ok.payload.decode('utf-8'))["response_code"] == "accepted"

@pytest.mark.parametrize("test_input", 
                            [
                                ('/trigger?timestamp=1669899025.0759895&event=done'),
                                ('/trigger?timestamp=1669899025.0759895&event=clearancetimeout')])
def test_trigger_rejects_notallowed_events(session, test_input):
    _session, settings = session
    replies = _session.get(settings.base_key_expr+test_input, zenoh.ListCollector(), target=zenoh.QueryTarget.ALL())
    for reply in replies():
        json.loads(reply.ok.payload.decode('utf-8')) == "rejected"

def test_trigger_rejects_invalid_timestamp(session, test_input="/trigger?event=done"):
    _session, settings = session
    replies = _session.get(settings.base_key_expr+test_input, zenoh.ListCollector(), target=zenoh.QueryTarget.ALL())
    for reply in replies():
        json.loads(reply.ok.payload.decode('utf-8'))["response_code"] == "rejected"


@pytest.mark.parametrize("test_input",
                            [
                                ('/trigger?timestamp=1669899025.0759895&event=awaitingclearanceerr'),
                                ("/trigger?timestamp=1669899025.0759895")
                    ])
def test_trigger_rejects_invalid_event(session, test_input):
    _session, settings = session
    replies = _session.get(settings.base_key_expr+test_input, zenoh.ListCollector(), target=zenoh.QueryTarget.ALL())
    for reply in replies():
        json.loads(reply.ok.payload.decode('utf-8'))["response_code"] == "rejected"
