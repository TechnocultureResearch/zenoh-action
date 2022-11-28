from confz import ConfZ, ConfZFileSource
from pydantic import BaseModel, validator
from pathlib import Path
from datetime import datetime

'''
    Config module for zenoh configuration. Validates the configuration variables using ConfZ by pydantic module.
    It validates 4 variables:
        - mode: two choices were there:
            - peer
            - client
        - connect: the endpoint to connect
        - listen: the endpoint to listen 
        - config: a configuration file for zenoh variables.
'''

class ZenohConfig(ConfZ):
    mode: str = 'peer'
    connect: str = ""
    listen: str = ""
    config: str = ""
     
#    CONFIG_SOURCES = ConfZFileSource(folder=Path('action.yml'))

class ValidatorModel(BaseModel):
    timestamp: str
    event: str

    @validator('timestamp')
    def must_be_a_timestamp(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            raise ValueError("Timestamp is not valid.")
        return v
    
    @validator('event')
    def must_be_a_valid_event(cls, v):
        event_list = ['start', 'stop']
        if v not in event_list:
            raise ValueError('Event is not valid or you are not allowed to trigger event.')
        return v