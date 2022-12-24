from pydantic import BaseModel
import zenoh
import json
from typing import Tuple

zenoh.init_logger()

class ZenohValidator(BaseModel):
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
    mode: str
    connect: str
    listen: str
    base_key_expr: str
    complete: bool

class ZenohConfig:
    '''
    Class creates zenoh configuration object and validates tha configuration variables.
    '''
    def __init__(self,
                mode: str = "peer",
                connect: str = "",
                listen: str = "",
                config: str = "",
                base_key_expr: str = "Genotyper/1/DNASensor/1",
                complete: bool = False) -> None:
        '''
        init takes a dict of arguments verifies them and creates a zenoh configuration object.
        Args:
            mode(str): two choices were there:
                - peer
                - client
            connect(str): the endpoint to connect
            listen(str): the endpoint to listen 
            config(str): a configuration file for zenoh variables.
            base_key_expr(str): a common keyexpression to use. 
        '''
        self.args = ZenohValidator(mode=mode, connect=connect, listen=listen, base_key_expr=base_key_expr, complete=complete)
        self.conf = zenoh.Config.from_file(
        config) if config != "" else zenoh.Config()
        if self.args.mode != "":
            self.conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(self.args.mode))
        if self.args.connect != "":
            self.conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(self.args.connect))
        if self.args.listen != "":
            self.conf.insert_json5(zenoh.config.LISTEN_KEY, json.dumps(self.args.listen))
    
    def zenohconfig(self) -> Tuple:
        '''
        Returns the zenoh configuration object and validated arguments.
        Args:
            None
        Returns:
            A tuple of zenoh configuration object and validated arguments.
        '''
        return self.conf, self.args