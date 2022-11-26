
from main import Session
from state_machine import Session_state
import zenoh
from zenoh import QueryTarget
import json
import time

def get(endpoint):
    target = {
    'ALL': QueryTarget.ALL(),
    'BEST_MATCHING': QueryTarget.BEST_MATCHING(),
    'ALL_COMPLETE': QueryTarget.ALL_COMPLETE(),}.get("ALL")

    session_obj = Session()
    session_obj.setup_action_server()
    statechart=session_obj.session.get(endpoint, zenoh.ListCollector(), target=target)
    for reply in statechart():
        try:
            value = reply.ok.payload.decode("utf-8")
        except:
            print(">> Received (ERROR: '{}')"
                .format(reply.err.payload.decode("utf-8")))
    return value

def put(endpoint):
    '''
        if user puts json file at the place of keyexpr then the server should check it but HOW?
    '''


def test_statechart():
    value = get("/statechart")
    assert json.loads(value) == json.loads(Session_state().statechart())

def test_state():
    value = get("/state")

def test_trigger():
    payload = {'timestamp':time.time(), 'event':'start'}
    "Geneotyper/1/.../trigger"
    value = get(payload)
    print(value)
