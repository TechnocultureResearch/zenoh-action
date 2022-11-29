
from state_machine import StateMachine
import pytest
import asyncio
statemachine = StateMachine()

@pytest.mark.parametrize("test_input, expected", 
                            [
                                ('start_machine', 'healthy_idle'),
                                ('start', 'healthy_busy'), 
                                ('abort', 'unhealthy_awaitingclearanceerr'),
                                pytest.param('clearancetimeout', 'unhealthy_awaitingclearanceerr', marks=pytest.mark.xfail)
                            ])
def test_statechart(test_input, expected):
    trigger = getattr(statemachine, test_input)
    trigger()
    assert statemachine.state == expected

