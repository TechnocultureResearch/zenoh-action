from transitions.extensions.markup import MarkupMachine
from transitions.extensions.factory import HierarchicalMachine
from transitions.extensions import GraphMachine
import json
from config import ZenohConfig
import zenoh

'''
Global variables:
    QUEUED(bool): To process the tranisitions in a queue.
    args: object of the ZenohConfig class which validates zenoh configuration variables.
    conf: Zenoh configuration object from zenohd.
    session: object to create a session.
    pub: object for publisher to publish executed state on zenohd.
'''
conf, args = ZenohConfig().zenohconfig()
zenoh.init_logger()
session = zenoh.open(conf) 
pub = session.declare_publisher(args.base_key_expr+"/state")
QUEUED = False

class Unhealthy(HierarchicalMachine):
    '''
    Heathy state machine which triggers states which are healthy for the machine.
    Inherited with HierarchicalMachine.
    '''
    def __init__(self):
        '''
        Initializes tha hierarchical state machine.
        Args:
            states: a set of valid states.
            transitions: a set of valid transitions.
            initial: the first state of statemachine.
            queued: 
            after_state_change: callback to call after every state change.
            send_event: send current executing event to model.
        '''
        states = [
                    {"name":"awaitingclearanceerr", 'on_enter':[]},
                    {"name":"cleared", 'on_enter':[]},
                    {"name":"brokenwithholdings", 'on_enter':[]},
                    {"name":"brokenwithoutholdings", 'on_enter':[]},
                    {"name":"dead"}]
        transitions = [{"trigger":"iawaitingclearanceerr", "source":"abort", "dest":"awaitingclearanceerr"},
                        {"trigger":"iclearancetimeout", "source":"awaitingclearance", "dest":"awaitingclearanceerr"},
                        {"trigger":"iawaitingclearanceerr", "source":"awaitingclearanceerr", "dest":"clearancetimeout"},
                        {"trigger":"icleared", "source":"awaitingclearanceerr", "dest":"cleared"},
                        {"trigger":"ibrokenwithoutholdings", "source":"cleared", "dest":"brokenwithoutholdings"},
                        {"trigger":"ibrokenwithholdings", "source":"awaitingclearanceerr", "dest":"brokenwithholdings"}]
        super().__init__(self, states=states, transitions=transitions, initial="awaitingclearanceerr", queued=QUEUED, after_state_change='publish_state', send_event=True)
    
    def publish_state(self, event_data):
        pub.put(event_data.model.state)


class Healthy(HierarchicalMachine):
    '''
    Heathy state machine which triggers states which are healthy for the machine. 
    Creates object of unhealthy state machine to transit when forced aborted triggered or clerance_timeout.
    Inherited with HierarchicalMachine
    '''
    def __init__(self):
        '''
        Initializes tha hierarchical state machine.
        Args:
            states: a set of valid states.
            transitions: a set of valid transitions.
            initial: the first state of statemachine.
            queued: 
            after_state_change: callback to call after every state change.
            send_event: send current executing event to model.
        '''
        states = [{"name":"busy", 'on_enter':[]},
                    {"name":"done", 'on_enter':[]},
                    {"name":"awaitingclearance", 'on_enter':[]},
                    {"name":"clearncetimeout", 'on_enter':[]},
                    {"name":"abort", "on_enter":[]}]

        transitions = [{"trigger":"done", "source":"busy", "dest":"done"},
                        {"trigger":"iabort", "source":"done", "dest":"abort"},
                        {"trigger":"abort", "source":"busy", "dest":"abort"},
                        {"trigger":"iawaitingclearance", "source":"abort", "dest":"awaitingclearance"},
                        {"trigger":"idle", "source":"awaitingclearance", "dest":"idle"}]
        super().__init__(model=self, states=states, transitions=transitions, initial="busy", queued=QUEUED, after_state_change='publish_state', send_event=True)
    
    def publish_state(self, event_data):
        '''
        Method to publish event state on zenohd after every state change.
        Args:
            event_data: complete information of current executing event i.e. transition and state.
        '''
        pub.put(event_data.model.state)

class BaseStateMachine(HierarchicalMachine,MarkupMachine):
    def __init__(self):
        '''
        Initializes tha hierarchical state machine. Basestatemachine calls healthy and unhealthy state machine to transit from healthy machine to unhealthy machine.
        Args:
            states: a set of valid states.
            transitions: a set of valid transitions.
            initial: the first state of statemachine.
            queued: 
            after_state_change: callback to call after every state change.
            send_event: send current executing event to model.
        '''
        unhealthy= Unhealthy()
        healthy = Healthy()
        states = [{'name':"idle"}, {"name":'healthy', 'children':healthy}, {"name":"unhealthy", "children":unhealthy}]
        super().__init__(model=self, states=states, initial="idle", queued=QUEUED, after_state_change='publish_state', send_event=True)
        self.add_transition("start", "idle", "busy")
        self.add_transition("idead", "brokenwithholdings", "dead")
        self.add_transition("idead", "brokenwithoutholdings", "dead")

    def publish_state(self, event_data):
        '''
        Method to publish event state on zenohd after every state change.
        Args:
            event_data: complete information of current executing event i.e. transition and state.
        '''
        pub.put(event_data.model.state)

class StateMachineModel:
    """
    This class works as a intermediate between server and statemachine.
    """
    def __init__(self,statemachine=BaseStateMachine()):
        """
        Args: 
        statemachine: object for statemachine.
        """
        self.statemachine=statemachine

    def statechart(self):
        """
        Creates a markup of statemachine object if it inherited with markupmachine.
        Args:
            None
        Returns:
            complete statemachine in json serialized format.
        """
        statechart = json.dumps(self.statemachine.markup, indent=3)
        return statechart

    def event_trigger(self, event: str):
        """
        Triggers the event on the statemachine.
        Args:
            event(str): event to trigger on statemachine. 
        Raises:
            AttributeError, if any AttributeError arises with message.
        """
        try:
            event_trigger = getattr(self.statemachine, event)
            event_trigger()
        except AttributeError as error:
            raise AttributeError(error)