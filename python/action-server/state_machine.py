from transitions import Machine
from transitions.extensions import GraphMachine
from functools import partial
import logging
import asyncio
log = logging.getLogger(__name__)

class HealthyStateMachine:

    states = [{'name':'idle'},
                    {'name':'busy'},
                    {'name':'aborted'},
                    {'name':'done'},
                    {'name':'clearance_timeout'},
                    {'name':'awaiting_clearance'}]
    
    transitions = [{'trigger':'start', 'source':'idle', 'dest':'busy', 'conditions':'done', 'unless':'abort'},
                        {'trigger':'abort', 'source':'busy', 'dest':'aborted'},
                        {'trigger':'done', 'source':'busy', 'dest':'done'},
                        {'trigger':'awaiting_clearance', 'source':'done', 'dest':'awaiting_clearance'},
                        {'trigger':'clearance_timeout', 'source':'awaiting_clearance', 'dest':'clearance_timeout'},
                        {'trigger':'', 'source':'awaiting_clearance', 'dest':'idle'}]

class UnhealthyStateMachine:

    ustates = [{'name':'awaiting_clearance_err'},
                    {'name':'cleared'},
                    {'name':'broken_with_holdings'},
                    {'name':'broken_without_holdings'},
                    {'name':'dead'}]

    utransitions = [{'trigger':'awaiting_clearance_err', 'source':'aborted', 'dest':'awaiting_clearance_err'},
                        {'trigger':'awaiting_clearance_err', 'source':'clearance_timeout', 'dest':'awaiting_clearance_err'},
                        {'trigger':'cleared', 'source':'awaiting_clearance_err', 'dest':'cleared'},
                        {'trigger':'broken_without_holdings', 'source':'cleared', 'dest':'broken_without_holdings'},
                        {'trigger':'broken_with_holdings', 'source':'awaiting_clearance_err', 'dest':'broken_with_holdings'},
                        {'trigger':'dead', 'source':'broken_with_holdings', 'dest':'dead'},
                        {'trigger':'dead', 'source':'broken_without_holdings', 'dest':'dead'}
                        ]

class StateMachine(HealthyStateMachine, UnhealthyStateMachine):
    states = HealthyStateMachine.states + UnhealthyStateMachine.ustates
    transitions = HealthyStateMachine.transitions + UnhealthyStateMachine.utransitions
    
    def __init__(self, session):
        self.session = session
        self.machine = Machine(model=self, states=StateMachine.states, transitions=StateMachine.transitions, initial='idle')

    async def idle(self):
        value = ''
        log.info('I am idle. Waiting for Command.')
        try:
            await asyncio.wait_for(self.wait_for_start(), timeout=1800)
            await self.start()
        except asyncio.TimeoutError:
            print('Timeout No command found.')

    async def wait_for_start(self):
        while True:
            if self.session.get('/start') == 'Started':
                break
            else:
                await asyncio.sleep(10)

    async def start(self):
        print('start')
        self.session.publish_data()
        await self.progress()
        if self.session.get('/completed') == 'completed':
            await self.done()

    async def progress(self):
        print('progress')
        await asyncio.sleep(60)
        self.session.get('/done')

    async def abort(self):
        print('abort')
        self.session.stop_action_server()
        await self.awaiting_clearance_err()

    async def done(self):
        print('done')
        await self.awaiting_clearance()

    async def awaiting_clearance(self):
        try:
            async with asyncio.timeout(60):
                self.idle()
        except asyncio.TimeoutError:
            await self.clearance_timeout()
        

    async def clearance_timeout(self):
        log.info('Timeout Clearance')
        await self.awaiting_clearance_err()

    async def awaiting_clearance_err(self):
        try:
            async with asyncio.timeout(60):
                self.cleared()
        except asyncio.TimeoutError:
            self.broken_With_holdings()
        
    def cleared(self):
        log.info('Awaiting clearance cleared')
        self.broken_without_holdings()

    def broken_With_holdings(self):
        log.info('Broken with holdings')
        self.session.put('/broken_without_holdings', 'True')
        self.dead()

    def broken_without_holdings(self):
        log.info('Broken with holdings')
        self.session.put('/broken_with_holdings', 'True')
        self.dead()

    def dead(self):
        if self.session.get('/broken_with_holdings') == 'True':
            print('Machine is broken. Please switched it off.')
        if self.session.get('/broken_without_holdings') == 'True':
            print('Machine is halted but no harm. Please switched it off.')
'''
if __name__ == '__main__':
    unhealthystatemachine =UnhealthyStateMachine()
    states = unhealthystatemachine.ustates + unhealthystatemachine.states
    transitions = unhealthystatemachine.utransitions + unhealthystatemachine.transitions

    model = StateMachine()
    machine = GraphMachine(model=model, states=states,
                        transitions=transitions,
                        initial='idle', show_conditions=True)

    model.get_graph().draw('my_state_diagram.png', prog='dot')

    statemachine = Machine(model=model, states=states, transitions=transitions, initial='idle')
    asyncio.run(model.idle())
'''