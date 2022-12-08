from state_machine import BaseStateMachine
import pytest
statemachine = BaseStateMachine()

@pytest.mark.parametrize("test_input, expected", 
                            [
                                ('start', 'healthy_busy'), 
                                ('abort', 'healthy_abort'),
                                pytest.param('clearancetimeout', 'unhealthy_awaitingclearanceerr', marks=pytest.mark.xfail)
                            ])
def test_statemachine(test_input, expected):
    trigger = getattr(statemachine, test_input)
    trigger()
    assert statemachine.state == expected

