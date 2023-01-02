from stateMachine import BaseStateMachine
import pytest

@pytest.fixture
def statemachine() -> BaseStateMachine:
    statemachine = BaseStateMachine()
    return statemachine

@pytest.mark.parametrize("test_input, expected", 
                            [
                                ('start', 'healthy_busy'),
                                pytest.param('clearancetimeout', 'unhealthy_awaitingclearanceerr', marks=pytest.mark.xfail)
                            ])
def test_statemachine(statemachine, test_input, expected) -> None:
    _statemachine = statemachine()
    _statemachine.trigger(test_input)
    assert statemachine.state == expected

