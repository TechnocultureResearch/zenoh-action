from confz import ConfZ, ConfZFileSource
from pathlib import Path

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