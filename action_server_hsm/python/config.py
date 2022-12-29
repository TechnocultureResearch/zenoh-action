from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass
import zenoh
import json
from typing import Tuple

@dataclass
class ZenohSettings(BaseModel):
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
    mode: str = Field(default="peer")
    connect: str = Field(default="")
    listen: str = Field(default="")
    base_key_expr: str = Field(default="Genotyper/1/DNASensor/1")
    config: str = Field(default="")

class ZenohConfig:
    '''
    Class creates zenoh configuration object and validates tha configuration variables.
    '''
    def __init__(self, settings: ZenohSettings) -> None:
        '''
        init takes a dict of arguments verifies them and creates a zenoh configuration object.
        Args:
            settings(dict): a dict of zenoh parameters.
        '''
        self.zenohSettings: ZenohSettings = settings
        self.conf: zenoh.Configuration = None
    def zenohconfig(self) -> zenoh.Configuration:
        '''
        Returns the zenoh configuration object and validated arguments.
        Returns:
            A tuple of zenoh configuration object and zenoh parameter.
        '''
        self.conf = zenoh.Config.from_file(
        self.zenohSettings.config) if self.zenohSettings.config != "" else zenoh.Config()
        return self.conf