#type: ignore
from pydantic import BaseModel, validator, root_validator
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable
from transitions import MachineError
import json

@dataclass
class Trigger:
    def __init__(self, event: str, statemachine: Any) -> None:
        self.event = event
        self.statemachine = statemachine
    
    def __call__(self) -> Callable:
        try:
            return self.statemachine.trigger(self.event)
        except MachineError as error:
            raise MachineError("Event is recognised but {}".format(error))
        except AttributeError as error:
            raise AttributeError("Event is not recognised or valid. {}".format(error))

def extract_states_fron_jsonStateMachine(jsonStateMachine: dict) -> list:
    '''
    Extracts states from jsonStateMachine.
    Args:
        jsonStateMachine(dict): a dict of states and transitions.
    Returns:
        A list of states.
    '''
    trigger = []
    valid_trigger = []
    for transition in jsonStateMachine['transitions']:
        if transition['trigger'] not in trigger:
            trigger.append(transition['trigger'])
    
    for state in jsonStateMachine['states']:
        if state.children:
            for child in state.transitions:
                if child.trigger not in trigger:
                    trigger.append(child)
    for _trigger in trigger:
        if _trigger[0] != 'i':
            valid_trigger.append(_trigger)
    return valid_trigger
    
class Event(BaseModel):
    '''
    Validates the parameters given to trigger an event.
    Args:
        timestamp(datetime): the time of occurrence of requesting query.
        event(str): an event which user want to trigger.
    '''
    jsonStateMachine: dict
    timestamp: str
    event: str
    
    @validator('timestamp')
    def must_be_a_timestamp(cls, v: str) -> datetime:
        '''
        Custom validator for timestamp to check if it is valid.
        Args:
            v(datetime): the time of occurrence of requesting query.
        Raises:
            ValueError, if ValueError arises.
        Returns:
            timestamp
        '''
        try:
            s = datetime.fromtimestamp(float(v))
        except ValueError:
            raise ValueError("Timestamp is not valid.")
        return s
    
    @validator('event')
    def must_be_a_valid_event(cls, v, values) -> str:
        '''
        Custom validator to check if event is valid and checks if user can trigger that event.
        Args:
            v(str): an event which user want to trigger.
        Raises:
            ValueError, if client gives an event which he is not allowed to trigger..
        Returns:
            event
        '''
        valid_event = extract_states_fron_jsonStateMachine(values['jsonStateMachine'])
        if v not in valid_event:
            raise ValueError('Event is not valid or you are not allowed to trigger event.')
        return v

    