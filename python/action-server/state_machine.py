from transitions.extensions.markup import MarkupMachine
from transitions.extensions.factory import HierarchicalMachine
from transitions.extensions import GraphMachine
import json
from validators import ZenohConfig
import zenoh

args = ZenohConfig()
conf = zenoh.Config.from_file(
    args.config) if args.config != "" else zenoh.Config()
if args.mode != "":
    conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(args.mode))
if args.connect != "":
    conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(args.connect))
if args.listen != "":
    conf.insert_json5(zenoh.config.LISTEN_KEY, json.dumps(args.listen))

zenoh.init_logger()
session = zenoh.open(conf) 
pub = session.declare_publisher(args.base_key_expr+"/state")
'''
Global variables:
    QUEUED(bool): To process the tranisitions in a queue.
    publisher(object): it is needed to use same publisher object in the entire statemachine to put data on zenohd.
'''
QUEUED = False

class Unhealthy(HierarchicalMachine):
    '''
    Heathy state machine which triggers states which are healthy for the machine.
    Inherited with HierarchicalMachine.
    '''
    def __init__(self):
        states = [
                    {"name":"awaitingclearanceerr", 'on_enter':[]},
                    {"name":"cleared", 'on_enter':[]},
                    {"name":"brokenwithholdings", 'on_enter':[]},
                    {"name":"brokenwithoutholdings", 'on_enter':[]},
                    {"name":"dead"}
                    ]
        transitions = [
                        {"trigger":"cleared", "source":"awaitingclearanceerr", "dest":"cleared"},
                        {"trigger":"brokenwithoutholdings", "source":"cleared", "dest":"brokenwithoutholdings"},
                        {"trigger":"brokenwithholdings", "source":"awaitingclearanceerr", "dest":"brokenwithholdings"},
                        {"trigger":"dead", "source":"brokenwithholdings", "dest":"dead"},
                        {"trigger":"dead", "source":"brokenwithoutholdings", "dest":"dead"}]
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
        unhealthy = Unhealthy()
        states = [{"name":"busy", 'on_enter':[]},
                    {"name":"done", 'on_enter':[]},
                    {"name":"awaitingclearance", 'on_enter':[]}, 
                    {"name":"unhealthy", "children":unhealthy}]

        transitions = [{"trigger":"done", "source":"busy", "dest":"done"},
                        {"trigger":"awaitingclearance", "source":"done", "dest":"awaitingclearance"},
                        {"trigger":"idle", "source":"awaitingclearance", "dest":"idle"}]
        super().__init__(model=self, states=states, transitions=transitions, initial="busy", queued=QUEUED, after_state_change='publish_state', send_event=True)
    def publish_state(self, event_data):
        pub.put(event_data.model.state)

class BaseStateMachine(HierarchicalMachine,MarkupMachine):
    def __init__(self):
        unhealthy= Unhealthy()
        healthy = Healthy()
        states = [{'name':"idle"}, {"name":'healthy', 'children':healthy}, {"name":"unhealthy", "children":unhealthy}]
        super().__init__(model=self, states=states, initial="idle", queued=QUEUED, after_state_change='publish_state', send_event=True)
        self.add_transition("start", "idle", "healthy")
        self.add_transition('abort', 'healthy', 'unhealthy')
        self.add_transition('clearancetimeout', 'healthy', 'unhealthy')

    def publish_state(self, event_data):
        pub.put(event_data.model.state)

class StateMachineModel:
    def __init__(self,statemachine=BaseStateMachine()):
        self.statemachine=statemachine

    def statechart(self):
        statechart = json.dumps(self.statemachine.markup, indent=3)
        return statechart

    def event_trigger(self, event: str):
        try:
            event_trigger = getattr(self.statemachine, event)
            event_trigger()
            #session.put('Genotyper/1/DNAsensor/1/state', self.statemachine.state)
        except AttributeError as error:
            raise AttributeError(error)
    