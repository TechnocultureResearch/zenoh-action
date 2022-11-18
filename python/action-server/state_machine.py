from transitions.extensions.factory import HierarchicalMachine
from transitions.extensions.states import Timeout, Tags, add_state_features

@add_state_features(Timeout, Tags)
class HealthyStateMachine(HierarchicalMachine):

    def __init__(self):
        states = [{'name':'idle', 'on_enter':'idle'},
                    {'name':'busy', 'on_enter':'busy'},
                    {'name':'aborted', 'on_enter':'abort'},
                    {'name':'awaiting_clearance', 'tags':['timeout_clearance', 'clear_done'], 'timeout':10, 'on_timeout':self.clearance_timeout}]

        transitions = [{'trigger':'start', 'source':'idle', 'dest':'busy', 'conditions':'done', 'unless':'abort'},
                        {'trigger':'abort', 'source':'busy', 'dest':'aborted'},
                        {'trigger':'done', 'source':'busy', 'dest':'done'},
                        {'trigger':'awaiting_clearance', 'source':'done', 'dest':'awaiting_clearance'},
                        {'trigger':'clearance_timeout', 'source':'awaiting_clearance', 'dest':'clearance_timeout'},
                        {'trigger':'', 'source':'awaiting_clearance', 'dest':'idle'}]

        super().__init__(states=states, transitions=transitions, initial='idle')

add_state_features(Timeout, Tags)
class UnhealthyStateMachine(HierarchicalMachine):

    def __init__(self):
        states = [{'name':'awaiting_clearance_err', 'tags':['timeout_clearance', 'clear_done'], 'timeout':10, 'on_timeout':'broken_with_holdings'},
                    {'name':'cleared', 'on_enter':'cleared'},
                    {'name':'broken_with_holdings', 'on_enter':'broken_with_holdings'},
                    {'name':'broken_without_holdings', 'on_enter':'broken_without_holdings'},
                    {'name':'dead', 'on_enter':'dead'}]

        transitions = [{'trigger':'awaiting_clearance_err', 'source':'aborted', 'dest':'awaiting_clearance_err'},
                        {'trigger':'awaiting_clearance_err', 'source':'clearance_timeout', 'dest':'awaiting_clearance_err'},
                        {'trigger':'cleared', 'source':'awaiting_clearance_err', 'dest':'cleared'},
                        {'trigger':'broken_without_holdings', 'source':'awaiting_clearance_err', 'dest':'broken_without_holdings'},
                        {'trigger':'broken_with_holdings', 'source':'awaiting_clearance_err', 'dest':'broken_with_holdings'},
                        ]
        super().__init__(states=states, transitions=transitions)

class StateMachine:

    def __init__(self, session):
        self.session = session
        self.machine = UnhealthyStateMachine()

    async def idle(self):
        print('I am idle. Waiting for Command.')

    async def start(self):
        self.session.publish_data()

    async def progress(self):
        self.session.get('/done')

    def abort(self):
        self.session.stop_action_server()

    def done(self):
        pass

    def awaiting_clearance(self):
        pass

    def clearance_timeout(self):
        pass

    def awaiting_clearance_err(self):
        pass

    def cleared(self):
        pass

    def broken_With_holdinngs(self):
        pass

    def broken_without_holdings(self):
        pass

    def dead(self):
        print('Machine is broken. Please switched it off.')

