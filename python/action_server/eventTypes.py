from pydantic import BaseModel, validator
from datetime import datetime
from transitions import MachineError, Machine
from dataclasses import dataclass
from typing import Any

@dataclass
class Trigger:
    def __init__(self, event: str, statemachine: Any) -> None:
        self.event = event
        self.statemachine = statemachine
    
    def __call__(self) -> Any:
        try:
            return self.statemachine.trigger(self.event)
        except MachineError as error:
            raise MachineError("Event is recognised but {}".format(error))
        except AttributeError as error:
            raise AttributeError("Event is not recognised or valid. {}".format(error))
@dataclass
class Event(BaseModel):
    '''
    Validates the parameters given to trigger an event.
    Args:
        timestamp(datetime): the time of occurrence of requesting query.
        event(str): an event which user want to trigger.
    '''
    timestamp: str
    event: str
    
    @validator('timestamp')
    def must_be_a_timestamp(cls, v: str) -> Any:
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
            datetime.fromtimestamp(float(v))
        except ValueError:
            raise ValueError("Timestamp is not valid.")
        return v
    
    @validator('event')
    def must_be_a_valid_event(cls, v: str) -> Any:
        '''
        Custom validator to check if event is valid and checks if user can trigger that event.
        Args:
            v(str): an event which user want to trigger.
        Raises:
            ValueError, if client gives an event which he is not allowed to trigger..
        Returns:
            event
        '''
        event_list = ['start', 'stop']
        if v not in event_list:
            raise ValueError('Event is not valid or you are not allowed to trigger event.')
        return v

    