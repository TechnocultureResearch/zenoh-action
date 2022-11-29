from transitions.extensions.markup import MarkupMachine
from transitions.extensions.factory import HierarchicalMachine
from transitions.extensions.asyncio import AsyncMachine
import json

'''
Global variables:
    QUEUED(bool): To process the tranisitions in a queue.
    publisher(object): it is needed to use same publisher object in the entire statemachine to put data on zenohd.
'''
QUEUED = False
publisher = None

class Unhealthy(HierarchicalMachine):
    '''
    Heathy state machine which triggers states which are healthy for the machine.
    Inherited with HierarchicalMachine.
    '''
    def __init__(self):
        states = [{"name":'aborted', "on_enter":[]},
                    {"name":'clearancetimeouterr', "on_enter":[]},
                    {"name":"awaitingclearanceerr", 'on_enter':[]},
                    {"name":"cleared", 'on_enter':[]},
                    {"name":"brokenwithholdings", 'on_enter':[]},
                    {"name":"brokenwithoutholdings", 'on_enter':[]},
                    {"name":"dead"}
                    ]
        transitions = [{"trigger":"abort", "source":"aborted", "dest":"awaitingclearanceerr"},
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
        states = [{"name":'idle', 'on_enter':[]},
                    {"name":"busy", 'on_enter':[]},
                    {"name":"done", 'on_enter':[]},
                    {"name":"awaitingclearance", 'on_enter':[]}]

        transitions = [{'trigger':'start', 'source':'idle', 'dest':'busy'},
                        {"trigger":"done", "source":"busy", "dest":"done"},
                        {"trigger":"awaitingclearance", "source":"done", "dest":"awaitingclearance"},
                        {"trigger":"clearancetimeout", "source":"awaitingclearance", "dest":"clearancetimeout"},
                        {"trigger":"idle", "source":"awaiting_clearance", "dest":"idle"}]
        super().__init__(states=states, transitions=transitions, initial="idle", queued=QUEUED)



class StateMachine(HierarchicalMachine, MarkupMachine, AsyncMachine):
    def __init__(self):
        unhealthy= Unhealthy()
        healthy = Healthy()
        states = [{'name':"idle"}, {"name":'healthy', 'children':healthy}, {"name":"unhealthy", "children":unhealthy}]
        super().__init__(states=states, initial="idle", queued=QUEUED)
        self.add_transition("start_machine", "idle", "healthy")
        self.add_transition('abort', 'healthy', 'unhealthy')
        self.add_transition('clearancetimeout', 'healthy', 'unhealthy')

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
        statechart = json.dumps(self.markup, indent=3)
        return statechart