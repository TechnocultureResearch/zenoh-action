from transitions.extensions.markup import MarkupMachine
from transitions.extensions.factory import HierarchicalMachine
from config import ZenohConfig
import zenoh
import logging


logging.getLogger().setLevel(logging.DEBUG)

def session() -> zenoh.Publisher:
    conf = ZenohConfig().zenohconfig()
    session: zenoh.Session = zenoh.open(conf)
    pub = session.declare_publisher(zenohSettings.base_key_expr+"/state")
    return pub


class Unhealthy(HierarchicalMachine):
    """
    Heathy state machine which triggers states which are healthy for the machine.
    Inherited with HierarchicalMachine.
    """

    def __init__(self) -> None:
        """
        Initializes tha hierarchical state machine.
        Args:
            states: a set of valid states.
            transitions: a set of valid transitions.
            initial: the first state of statemachine.
            queued:
            after_state_change: callback to call after every state change.
            send_event: send current executing event to model.
        """
        states = [
            {"name": "awaitingclearanceerr"},
            {"name": "brokenwithholdings"},
            {"name": "brokenwithoutholdings"},
            {"name": "cleared"},
            {"name": "final"},
        ]
        transitions = [
            {
                "source": "awaitingclearanceerr",
                "dest": "cleared",
                "trigger": "icleardone",
            },
            {
                "source": "cleared",
                "dest": "brokenwithoutholdings",
                "trigger": "ibrokenwithoutholdings",
            },
            {
                "source": "awaitingclearanceerr",
                "dest": "brokenwithholdings",
                "trigger": "itimeoutclearance",
            },
            {"source": "brokenwithoutholdings",
                "dest": "final", "trigger": "error"},
            {"source": "brokenwithholdings", "dest": "final", "trigger": "error"},
        ]
        super().__init__(
            self,
            states=states,
            transitions=transitions,
            initial="awaitingclearanceerr",
            queued=False,
            after_state_change="publish_state",
            send_event=True,
        )

    def publish_state(self, event_data) -> None:
        pub = session()
        pub.put(event_data.model.state)


class Healthy(HierarchicalMachine):
    """
    Heathy state machine which triggers states which are healthy for the machine.
    Creates object of unhealthy state machine to transit when forced aborted triggered or clerance_timeout.
    Inherited with HierarchicalMachine
    """

    def __init__(self) -> None:
        """
        Initializes tha hierarchical state machine.
        Args:
            states: a set of valid states.
            transitions: a set of valid transitions.
            initial: the first state of statemachine.
            queued:
            after_state_change: callback to call after every state change.
            send_event: send current executing event to model.
        """
        states = [
            {"name": "busy"},
            {"name": "done"},
            {"name": "awaitingclearance"},
            {"name": "clearancetimeout"},
            {"name": "stopped"},
            {"name": "failed"},
            {"name": "final"},
        ]

        transitions = [
            {"source": "busy", "dest": "stopped", "trigger": "taskstop"},
            {"source": "busy", "dest": "failed", "trigger": "itaskfail"},
            {
                "source": "failed",
                "dest": "awaitingclearance",
                "trigger": "iawaitclearance",
            },
            {
                "source": "stopped",
                "dest": "awaitingclearance",
                "trigger": "iawaitclearance",
            },
            {"source": "busy", "dest": "done", "trigger": "itaskdone"},
            {
                "source": "done",
                "dest": "awaitingclearance",
                "trigger": "iawaitclearance",
            },
            {
                "source": "awaitingclearance",
                "dest": "clearancetimeout",
                "trigger": "itimeoutclearance",
            },
            {"source": "clearancetimeout", "dest": "final", "trigger": "error"},
        ]
        super().__init__(
            model=self,
            states=states,
            transitions=transitions,
            initial="busy",
            queued=False,
            after_state_change="publish_state",
            send_event=True,
        )

    def publish_state(self, event_data) -> None:
        """
        Method to publish event state on zenohd after every state change.
        Args:
            event_data: complete information of current executing event i.e. transition and state.
        """
        pub = session()
        pub.put(event_data.model.state)


class BaseStateMachine(HierarchicalMachine, MarkupMachine):
    def __init__(self) -> None:
        """
        Initializes tha hierarchical state machine. Basestatemachine calls healthy and unhealthy state machine to transit from healthy machine to unhealthy machine.
        Args:
            states: a set of valid states.
            transitions: a set of valid transitions.
            initial: the first state of statemachine.
            queued:
            after_state_change: callback to call after every state change.
            send_event: send current executing event to model.
        """
        unhealthy = Unhealthy()
        healthy = Healthy()
        states = [
            {"name": "idle"},
            {"name": "healthy", "children": healthy},
            {"name": "unhealthy", "children": unhealthy},
            {"name": "final"},
        ]
        super().__init__(
            model=self,
            states=states,
            initial="idle",
            queued=False,
            after_state_change="publish_state",
            send_event=True,
        )
        self.add_transition("start", "idle", "healthy")
        self.add_transition("err", "healthy", "unhealthy")
        self.add_transition("idead", "unhealthy", "final")

    def publish_state(self, event_data) -> None:
        """
        Method to publish event state on zenohd after every state change.
        Args:
            event_data: complete information of current executing event i.e. transition and state.
        """
        pub = session()
        pub.put(event_data.model.state)