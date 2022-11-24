from transitions.extensions.markup import MarkupMachine
from transitions.extensions.factory import HierarchicalMachine
import json

QUEUED = True
base_key_expr = 'Genotyper/1/DNAsesnsor/1'

class Session_state:
    def __init__(self, session):
        self.session=session

    def statechart(self):
        statechart = json.dumps(self.markup, indent=3)
        self.session.put("/statechart", statechart)
        return True

    def state_(self):
        self.session.put("/state", self.state)
        

class Unhealthy(HierarchicalMachine):
    def __init__(self):
        states = [{"name":'aborted', "on_enter":["aborted"]},
                    {"name":"awaitingclearanceerr", 'on_enter':['cleared']},
                    {"name":"cleared", 'on_enter':'brokenwithoutholdings'},
                    {"name":"brokenwithholdings", 'on_enter':'dead'},
                    {"name":"brokenwithoutholdings", 'on_enter':'dead'},
                    {"name":"dead"}
                    ]
        transitions = [{"trigger":"aborted", "source":"aborted", "dest":"awaitingclearanceerr"},
                        {"trigger":"awaitingclearanceerr", "source":"clearancetimeout", "dest":"awaitingclearanceerr"},
                        {"trigger":"cleared", "source":"awaitingclearanceerr", "dest":"cleared"},
                        {"trigger":"brokenwithoutholdings", "source":"cleared", "dest":"brokenwithoutholdings"},
                        {"trigger":"brokenwithholdings", "source":"awaitingclearanceerr", "dest":"brokenwithholdings"},
                        {"trigger":"dead", "source":"brokenwithholdings", "dest":"dead"},
                        {"trigger":"dead", "source":"brokenwithoutholdings", "dest":"dead"}]
        super().__init__(states=states, transitions=transitions, initial="awaitingclearanceerr", queued=QUEUED)

class Healthy(HierarchicalMachine):
    def __init__(self):
        aborted = Unhealthy()
        states = [{"name":'idle', 'on_enter':['start']},
                    {"name":"busy"},
                    {"name":"aborted", "children": aborted},
                    {"name":"done"},
                    {"name":"clearancetimeout", "children": aborted},
                    {"name":"awaitingclearance"}]

        transitions = [{'trigger':'start', 'source':'idle', 'dest':'busy'},
                        {"trigger":"abort", "source":"busy", "dest":"aborted"},
                        {"trigger":"done", "source":"busy", "dest":"done"},
                        {"trigger":"awaitingclearance", "source":"done", "dest":"awaitingclearance"},
                        {"trigger":"clearancetimeout", "source":"awaitingclearance", "dest":"clearancetimeout"},
                        {"trigger":"idle", "source":"awaiting_clearance", "dest":"idle"}]
        super().__init__(states=states, transitions=transitions, initial="idle", queued=QUEUED)



class StateMachine(HierarchicalMachine, MarkupMachine, Session_state):
    def __init__(self):
        healthy = Healthy()
        states = ["idle", {"name":'healthy', 'children':healthy}]
        super().__init__(states=states, initial="idle", queued=QUEUED)
        self.add_transition("start_machine", "idle", "healthy")
    

    
