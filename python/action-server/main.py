import time
import json
import itertools
import zenoh
from zenoh import Query
from pydantic import BaseModel
import asyncio
import yaml
import state_machine

# describe settings for parsing values.
class ActionSettings(BaseModel):
    mode: str = ""
    connect: str = ""
    listen: str = ""
    config: str = ""
    base_key_expr: str

class Handlers:
    '''
    handler functions are going to use by session declarables.
    1. query_handler method replies of every query which get function asks.
    '''

    def trigger_query_handler(self, query: Query) -> None:
        print(">> [Queryable ] Received Query '{}'".format(query.selector))
        event = json.loads(query)['event']
        '''
            check if event is possible or not from state machine for that you need to import statemachine states and transitions.
            needs to make a function in statemachine that will trigger the queried event and give msg if event is accepted or not. If error comes then it will give error.
        '''
        try: 
            value = self.session_state.triggered_event(event)
            if value:
                payload = {'reponse_code':'accepted', 'message':'trigger is accepted'}
                query.reply(payload)
            else:
                payload = {'response_code':'rejected', 'message':value}
                query.reply(payload)
        except Exception as e:
            print(e)
    
    def statechart_query_handler(self, query: Query):
        try:
            statechart = self.session_state.statechart()
            query.reply(statechart)
        except Exception as e:
            query.reply({'Error': e})            

class Session(Handlers):
    '''
    1. __init__ method creates self.session and perform self.session related tasks. Takes an object of settings.
    2. configuration method - configures the zenoh configuration from settings variables and returns a configuration object.
    3. setup_action_server method - 
        - creates session for zenohd, 
        - declares two queryables
            - for statechart
            - for trigger
        - declares a publisher
    '''
    def __init__(self, settings, session_state: Session_state) -> None:
        self.setting = settings
        self.session = None
        self.pub = None
        self.trigger_queryable = None
        self.statechart_queryable = None

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
        
        self.trigger_queryable = self.session.declare_queryable(self.setting.base_key_expr+'/trigger', self.trigger_query_handler)
        self.statechart_queryable = self.session.declare_queryable(self.setting.base_key_expr+'/statechart', self.statechart_query_handler)
        self.pub = self.session.declare_publisher(self.setting.base_key_expr+'/state')
