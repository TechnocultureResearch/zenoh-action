from transitions.extensions.markup import MarkupMachine
from transitions.extensions.factory import HierarchicalMachine
import json

QUEUED = True

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
    '''
        Heathy state machine which triggers states which are healthy for the machine. Creates object of unhealthy state machine to transit when forced aborted triggered or clerance_timeout
    '''
    def __init__(self):
        unhealthy = Unhealthy()
        states = [{"name":'idle', 'on_enter':['start']},
                    {"name":"busy"},
                    {"name":"aborted", "children": unhealthy},
                    {"name":"done"},
                    {"name":"clearancetimeout", "children": unhealthy},
                    {"name":"awaitingclearance"}]

        transitions = [{'trigger':'start', 'source':'idle', 'dest':'busy'},
                        {"trigger":"abort", "source":"busy", "dest":"aborted"},
                        {"trigger":"done", "source":"busy", "dest":"done"},
                        {"trigger":"awaitingclearance", "source":"done", "dest":"awaitingclearance"},
                        {"trigger":"clearancetimeout", "source":"awaitingclearance", "dest":"clearancetimeout"},
                        {"trigger":"idle", "source":"awaiting_clearance", "dest":"idle"}]
        super().__init__(states=states, transitions=transitions, initial="idle", queued=QUEUED)



class StateMachine(HierarchicalMachine, MarkupMachine):
    def __init__(self):
        healthy = Healthy()
        states = ["idle", {"name":'healthy', 'children':healthy}]
        super().__init__(states=states, initial="idle", queued=QUEUED)
        self.add_transition("start_machine", "idle", "healthy")


class Session_state:
    '''
       This class contains the methods used to be used by server to manage statemachine.
       Args:
            pub- a publisher object of session class to put state on zenoh session.
            statemachine- an object of the state machine.
        Returns:
            Returns Nothing.
    '''

    def __init__(self, pub = None, statemachine = StateMachine())-> None:
        self.statemachine = statemachine
        self.pub = pub

    def statechart(self):
        '''
            Converts the complete statemachine to a serialized json format.
            Args:
                Takes 0 arguments.
            Returns:
                statechart variable which is complete statemachine in a serialized json format.
            Raises:
                ValueError if any exception arises.
        '''
        statechart = json.dumps(self.statemachine.markup, indent=3)
        return statechart

    def state_(self):
        try:
            self.pub.put(self.statemachine.state)
        except Exception as error:
            raise ValueError(error)
    
    def triggered_event(self, event):
        try:
            callable_event = getattr(self.statemachine, event)
            callable_event()
        except Exception as error:
            raise ValueError(error)
        return True
        