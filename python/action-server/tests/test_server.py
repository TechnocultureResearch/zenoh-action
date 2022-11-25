
from main import Session
from state_machine import Session_state
import zenoh
from zenoh import QueryTarget
import json

def get(endpoint):
    target = {
    'ALL': QueryTarget.ALL(),
    'BEST_MATCHING': QueryTarget.BEST_MATCHING(),
    'ALL_COMPLETE': QueryTarget.ALL_COMPLETE(),}.get("ALL")

    session_obj = Session()
    session_obj.setup_action_server()
    statechart=session_obj.session.get("Genotyper/1/DNAsensor/1"+endpoint, zenoh.ListCollector(), target=target)
    for reply in statechart():
        try:
            value = reply.ok.payload.decode("utf-8")
        except:
            print(">> Received (ERROR: '{}')"
                .format(reply.err.payload.decode("utf-8")))
    return value

def test_statechart():
    value = get("/statechart")
    assert json.loads(value) == json.loads(Session_state().statechart())

def test_state():
    value = get("/state")

def test_trigger():
    value = get("/trigger")
    
