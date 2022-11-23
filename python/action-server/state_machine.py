#from transitions.extensions import GraphMachine
#from functools import partial
from transitions.extensions.markup import MarkupMachine
from transitions.extensions.factory import HierarchicalMachine
import logging
import json
import time

log = logging.getLogger(__name__)

QUEUED = False

class Healty(HierarchicalMachine):
    def __init__(self):
        states = [{"name":"busy", 'on_enter':'start'},
                    {"name":"aborted",'on_enter':'abort'},
                    {"name":"done",'on_enter':'done'},
                    {"name":"clearance_timeout",'on_enter':'clearance_timeout'},
                    {"name":"awaiting_clearance",'on_enter':'awaiting_clearance'}]

        transitions = [{"trigger":"abort", "source":"busy", "dest":"aborted"},
                        {"trigger":"done", "source":"busy", "dest":"done"},
                        {"trigger":"awaiting_clearance", "source":"done", "dest":"awaiting_clearance"},
                        {"trigger":"clearance_timeout", "source":"awaiting_clearance", "dest":"clearance_timeout"},
                        {"trigger":"idle", "source":"awaiting_clearance", "dest":"idle"}]
        super().__init__(states=states, transitions=transitions, initial="idle", queued=QUEUED)

class Unhealthy(HierarchicalMachine):
    def __init__(self):
        states = [{"name":"awaiting_clearance_err", 'on_enter':'awaiting_clearance_err'},
                    {"name":"cleared", 'on_enter':'cleared'},
                    {"name":"broken_with_holdings", 'on_enter':'broken_with_holdings'},
                    {"name":"broken_without_holdings", 'on_enter':'broken_without_holdings'},
                    {"name":"dead", 'on_enter':'dead'}
                    ]
        transitions = [{"trigger":"awaiting_clearance_err", "source":"aborted", "dest":"awaiting_clearance_err"},
                        {"trigger":"awaiting_clearance_err", "source":"clearance_timeout", "dest":"awaiting_clearance_err"},
                        {"trigger":"cleared", "source":"awaiting_clearance_err", "dest":"cleared"},
                        {"trigger":"broken_without_holdings", "source":"cleared", "dest":"broken_without_holdings"},
                        {"trigger":"broken_with_holdings", "source":"awaiting_clearance_err", "dest":"broken_with_holdings"},
                        {"trigger":"dead", "source":"broken_with_holdings", "dest":"dead"},
                        {"trigger":"dead", "source":"broken_without_holdings", "dest":"dead"}]
        super().__init__(states=states, transitions=transitions, initial="idle", queued=QUEUED)

class StateMachine(HierarchicalMachine):
    def __init__(self, session: Session):
        self.healthy = Healty()
        self.unhealthy = Unhealthy()
        self.session=session
        states = ["idle", {"name": "statemachine", "children": [self.healthy, self.unhealthy]}]
        transitions = [{"start", "idle", "healthy"}, 
                        {"abort", "busy", "unhealthy"}]
        super().__init__(states=states, transitions = transitions, initial="idle", queued=QUEUED)
        self.markup = MarkupMachine(model=self  , states=states, transitions=transitions, initial='idle')
    
    def statechart(self):
        statechart = json.dumps(self.markup.markup)
        return statechart

    def state(self):
        return self.state

    def trigger(self, trigger_method):
        try:
            self.session.put("Genotyper/1/DNAsensor/1/trigger", {'timestamp':time.time(), 'triggered':trigger_method})
        except Exception as e:
            if e is MachineError:
                print("State is recognised but can't trigger.")
            else:
                print('State is not recognised')
