from transitions.extensions.markup import MarkupMachine
from transitions.extensions.factory import HierarchicalMachine
import json

'''
Global variables:
    QUEUED(bool): To process the tranisitions in a queue.
    publisher(object): it is needed to use same publisher object in the entire statemachine to put data on zenohd.
'''
QUEUED = False
publisher = None

class Session_state:
    '''
    This class contains the methods used to be used by server to manage statemachine.
    Args:
        pub(object): an optional publisher object of session class to put the current executing state on zenohd.
        statemachine(object): an object of the state machine. Bydefault, It is taking an object of the statemachine declared in this module.
    '''

    def __init__(self,statemachine, pub = None)-> None:
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
        '''
        Publishes the current executing state on zenohd. Calls a global variable publisher, if it set to none then assigns it with a 
        pub object to put state of machine on zenoh.
        Args:
            Takes 0 arguments.
        Publishes:
            Publish the current executing state on zenohd.
        Raises:
            ValueError if any exception arises.
        '''
        try:
            global publisher
            if publisher == None:
                publisher = self.pub
            publisher.put(self.statemachine.state)
        except Exception as error:
            raise ValueError(error)
    
    def triggered_event(self, event):
        '''
        Triggers an event on the state machine. Calls a global variable publisher, if it set to none then assigns it with a 
        pub object to put state of machine on zenoh.
        Args:
            event(str): a state which is going to trigger on statemachine.
        Raises:
            ValueError, if any exception arises.
        Returns:
            True, if event triggered successfully.
        '''
        try:
            global publisher
            if publisher == None:
                publisher = self.pub
            callable_event = getattr(self.statemachine, event)
            callable_event()
        except Exception as error:
            raise ValueError(error)
        return True
        

class Unhealthy(HierarchicalMachine):
    '''
    Heathy state machine which triggers states which are healthy for the machine.
    Inherited with HierarchicalMachine.
    '''
    def __init__(self):
        session_state = Session_state(self.machine)
        states = [{"name":'aborted', "on_enter":[session_state.state_, "aborted"]},
                    {"name":'clearancetimeouterr', "on_enter":[session_state.state_, "clearancetimeouterr"]},
                    {"name":"awaitingclearanceerr", 'on_enter':[session_state.state_, 'cleared']},
                    {"name":"cleared", 'on_enter':[session_state.state_, 'brokenwithoutholdings']},
                    {"name":"brokenwithholdings", 'on_enter':[session_state.state_, 'dead']},
                    {"name":"brokenwithoutholdings", 'on_enter':[session_state.state_, 'dead']},
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
    Heathy state machine which triggers states which are healthy for the machine. 
    Creates object of unhealthy state machine to transit when forced aborted triggered or clerance_timeout.
    Inherited with HierarchicalMachine
    '''
    def __init__(self):
        unhealthy = Unhealthy()
        session_state = Session_state()
        states = [{"name":'idle', 'on_enter':[session_state.state_, 'start']},
                    {"name":"busy", 'on_enter':[session_state.state_]},
                    {"name":"aborted", "children": unhealthy},
                    {"name":"done", 'on_enter':[session_state.state_]},
                    {"name":"clearancetimeout", "children": unhealthy},
                    {"name":"awaitingclearance", 'on_enter':[session_state.state_]}]

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
