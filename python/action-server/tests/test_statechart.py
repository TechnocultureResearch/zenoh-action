from main import Session
from state_machine import Session_state
import zenoh
from zenoh import QueryTarget
import json

def test_statechart():
    target = {
    'ALL': QueryTarget.ALL(),
    'BEST_MATCHING': QueryTarget.BEST_MATCHING(),
    'ALL_COMPLETE': QueryTarget.ALL_COMPLETE(),}.get("ALL")

    session_obj = Session()
    session_obj.setup_action_server()
    statechart=session_obj.session.get("Genotyper/1/DNAsensor/1/statechart", zenoh.ListCollector(), target=target)
    for reply in statechart():
        try:
            value = reply.ok.payload.decode("utf-8")
        except:
            print(">> Received (ERROR: '{}')"
                .format(reply.err.payload.decode("utf-8")))
    
    assert json.loads(value) == Session_state().statechart()
