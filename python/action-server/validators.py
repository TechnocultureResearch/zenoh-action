from confz import ConfZ, ConfZFileSource
from pydantic import BaseModel, validator
from pathlib import Path
from datetime import datetime


class ZenohValidator(ConfZ):
    '''
    Config module for zenoh configuration. Validates the configuration variables using ConfZ by pydantic module.
    Args:
        - mode: two choices were there:
            - peer
            - client
        - connect: the endpoint to connect
        - listen: the endpoint to listen 
       - config: a configuration file for zenoh variables.
    '''
    mode: str = 'peer'
    connect: str = ""
    listen: str = ""
    config: str = ""
    base_key_expr: str = "Genotyper/1/DNAsensor/1"
    
    if config != "":
        CONFIG_SOURCES = ConfZFileSource(folder=Path(config))

class EventModel(BaseModel):
    timestamp: str
    event: str

    @validator('timestamp')
    def must_be_a_timestamp(cls, v):
        try:
            datetime.fromtimestamp(v)
        except ValueError:
            raise ValueError("Timestamp is not valid.")
        return v
    
    @validator('event')
    def must_be_a_valid_event(cls, v):
        event_list = ['start', 'stop']
        if v not in event_list:
            raise ValueError('Event is not valid or you are not allowed to trigger event.')
        return v