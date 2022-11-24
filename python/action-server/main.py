import time
import json
import itertools
import zenoh
from zenoh import Reliability, SampleKind, Query, Sample, KeyExpr, QueryTarget, Value
from pydantic import BaseModel
import logging
import asyncio
import yaml
import state_machine
log = logging.getLogger(__name__)

# describe settings for parsing values.
class ActionSettings(BaseModel):
    mode: str = ""
    connect: str = ""
    listen: str = ""
    config: str = ""
    base_key_expr: str

store = {}

class Handlers():
    '''
    handler functions are going to use by session declarables.
    1. query_handler method replies of every query which get function asks.
    '''

    def query_handler(self, query: Query):
        print(">> [Queryable ] Received Query '{}'".format(query.selector))
        for stored_name, sample in store.items():
            if query.key_expr.intersects(stored_name):
                query.reply(sample)
        

class Session(Handlers):
    '''
    1. __init__ method creates self.session and perform self.session related tasks. Takes an object of settings.
    2. configuration method - configures the zenoh configuration from settings variables and returns a configuration object.
    3. setup_action_server method - 
        - starts action server, 
        - declares two queryables
            - for statechart
            - for trigger
        - declares a publisher
    '''
    def __init__(self, settings):
        self.setting = settings
        self.session = None
        self.sub = None
        self.pub = None
        self.queryable = None

    def configuration(self):
        conf = zenoh.Config.from_file(
            self.setting.config) if self.setting.config is not None else zenoh.Config()
        if self.setting.mode is not None:
            conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(self.setting.mode))
        if self.setting.connect is not None:
            conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(self.setting.connect))
        if self.setting.listen is not None:
            conf.insert_json5(zenoh.config.LISTEN_KEY, json.dumps(self.setting.listen))
        return conf

    def setup_action_server(self):

        zenoh.init_logger()
        self.session = zenoh.open(self.configuration())
        
        self.trigger_queryable = self.session.declare_queryable(self.setting.base_key_expr+'/trigger', self.query_handler)
        self.statechart_queryable = self.session.declare_queryable(self.setting.base_key_expr+'/statechart', self.query_handler)
        self.pub = self.session.declare_publisher(self.setting.base_key_expr+'/state')


if __name__ == '__main__':

    with open('action.yml') as file:
        try:
            settingConfig = yaml.safe_load(file)  
        except yaml.YAMLError as err:
            print(err)

    settings = ActionSettings(**settingConfig)

    session = Session(settings)
    session.setup_action_server()