from stateMachine import BaseStateMachine
import pytest

@pytest.fixture
def statemachine():
    statemachine = BaseStateMachine()
    return statemachine

@pytest.mark.parametrize("test_input, expected", 
                            [
                                ('start', 'healthy_busy'),
                                pytest.param('clearancetimeout', 'unhealthy_awaitingclearanceerr', marks=pytest.mark.xfail)
                            ])
def test_statemachine(statemachine, test_input, expected):
    _statemachine = statemachine()
    _statemachine.trigger(test_input)
    assert statemachine.state == expected

