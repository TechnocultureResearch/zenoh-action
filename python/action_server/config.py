from confz import ConfZ, ConfZFileSource
from pydantic import BaseModel, validator, Field
from pathlib import Path
from datetime import datetime
import zenoh
import json

zenoh.init_logger()

class ZenohValidator(ConfZ):
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
    mode: str = Field(dest="mode", choices=["peer", "client"], default="peer", description="The zenoh session mode.")
    connect: str = Field(dest="connect",metavar="ENDPOINT", action="append", default="", description="Endpoints to connect to.")
    listen: str = Field(dest="listen", metavar="ENDPOINT", action="append", default="", description="Endpoints to listen on.")
    config: str = Field(dest="config", metavar="FILE", default="", description="A configuration file.")
    base_key_expr: str = "Genotyper/1/DNASensor/1"
    complete: bool = Field(dest="complete", default=False, action="store_true", description="Declare the storage as complete w.r.t. the key expression.")

    '''
    if config != "":
        CONFIG_SOURCES = ConfZFileSource(folder=Path(config))'''

class ZenohConfig:
    '''
    Class creates zenoh configuration object and validates tha configuration variables.
    '''
    def __init__(self, **kwargs):
        '''
        init takes a dict of arguments verifies them and creates a zenoh configuration object.
        Args:
            A dict of arguments.
        '''
        self.args = ZenohValidator(**kwargs)
        self.conf = zenoh.Config.from_file(
        self.args.config) if self.args.config != "" else zenoh.Config()
        if self.args.mode != "":
            self.conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(self.args.mode))
        if self.args.connect != "":
            self.conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(self.args.connect))
        if self.args.listen != "":
            self.conf.insert_json5(zenoh.config.LISTEN_KEY, json.dumps(self.args.listen))
    def zenohconfig(self):
        '''
        Returns the zenoh configuration object and validated arguments.
        Args:
            None
        Returns:
            A tuple of zenoh configuration object and validated arguments.
        '''
        return self.conf, self.args

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
