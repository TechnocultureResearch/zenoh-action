from confz import ConfZ, ConfZFileSource
from pydantic import BaseModel, validator
from pathlib import Path
from datetime import datetime


class ZenohConfig(ConfZ):
    '''
    Config module for zenoh configuration. Validates the configuration variables using ConfZ by pydantic module.
    Args:
        mode(str): two choices were there:
            - peer
            - client
        connect(str): the endpoint to connect
        listen(str): the endpoint to listen 
        config(str): a configuration file for zenoh variables.
        base_key_expr(str): a common keyexpression to use. 
    '''
    mode: str = 'peer'
    connect: str = ""
    listen: str = ""
    config: str = ""
    base_key_expr: str = "Genotyper/1/DNAsensor/1"
    
    if config != "":
        CONFIG_SOURCES = ConfZFileSource(folder=Path(config))

class EventModel(BaseModel):
    '''
    Validates the parameters given to trigger an event.
    Args:
        timestamp(datetime): the time of occurrence of requesting query.
        event(str): an event which user want to trigger.
    '''
    timestamp: str
    event: str
    @validator('timestamp')
    def must_be_a_timestamp(cls, v):
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
            datetime.fromtimestamp(eval(v))
        except ValueError:
            raise ValueError("Timestamp is not valid.")
        return v
    
    @validator('event')
    def must_be_a_valid_event(cls, v):
        '''
        Custom validator to check if event is valid and checks if user can trigger that event.
        Args:
            v(str): an event which user want to trigger.
        Raises:
            ValueError, if client gives an event which he is not allowed to trigger..
        Returns:
            event
        '''
        event_list = ['start', 'abort']
        if v not in event_list:
            raise ValueError('Event is not valid or you are not allowed to trigger event.')
        return v