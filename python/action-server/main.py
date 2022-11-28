import json
import zenoh
from zenoh import Query, Sample
import asyncio
from state_machine import Session_state
from config import ZenohConfig, ValidatorModel
from pydantic import ValidationError

base_key_expr = "Genotyper/1/DNAsensor/1"

class Handlers:
    '''
    Handlers class contains callback methods for queryables.
        trigger_query_handler: method replies of every query related to the keyexpression `/trigger`.
        statechart_query_handler: method replies to `/statechart` related query.
    '''

    def trigger_query_handler(self, query: Query) -> None:
        '''
            check if event is possible or not from state machine for that you need to import statemachine states and transitions.
            Args:
                query: a string which describes query in the form of keyexpr
            Returns:
                It returns nothing but replies of queries.
        '''
        try: 
            print(">> [Queryable ] Received Query '{}'".format(query.selector))
            validator = ValidatorModel(query.selector.decode_parameters())
            value = self.session_state.triggered_event(validator.event)
            payload = {'reponse_code':'accepted', 'message':'trigger is accepted'}
            query.reply(Sample(base_key_expr+"/trigger", payload))
        except (ValidationError, ValueError) as error:
            payload = {'response_code':'rejected', 'message': error}
            query.reply(Sample(base_key_expr+'/trigger', payload))
    
    def statechart_query_handler(self, query):
        try:
            session_state = Session_state()
            statechart = session_state.statechart()
            query.reply(Sample(base_key_expr+"/statechart", statechart))
        except Exception as e:
            payload = {'Error': e}
            query.reply(Sample(base_key_expr+"/statechart", payload))       
        

class Session():
    '''
    This class performs tasks on zenohd.
    Methods:
        - configuration method: configures the zenoh configuration from settings variables and returns a configuration object.
        - setup_action_server method:
            - creates session for zenohd, 
            - declares two queryables
                - for statechart
                - for trigger
            - declares a publisher
    '''

    def __init__(self) -> None:
        self.session = None
        self.pub = None
        self.trigger_queryable = None
        self.statechart_queryable = None

    def setup_action_server(self):
        '''
            To perform tasks on zenohd we need to open session and declare queryables and publisher.
        '''
        zenohConfig = ZenohConfig()
        conf = zenoh.Config.from_file(
            zenohConfig.config) if zenohConfig.config != "" else zenoh.Config()
        if zenohConfig.mode != "":
            conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(zenohConfig.mode))
        if zenohConfig.connect != "":
            conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(zenohConfig.connect))
        if zenohConfig.listen != "":
            conf.insert_json5(zenoh.config.LISTEN_KEY, json.dumps(zenohConfig.listen))
        zenoh.init_logger()
        self.session = zenoh.open(conf)
        
        self.trigger_queryable = self.session.declare_queryable(base_key_expr+'/trigger', self.trigger_query_handler)
        self.statechart_queryable = self.session.declare_queryable(base_key_expr+'/statechart', self.statechart_query_handler)
        self.pub = self.session.declare_publisher(base_key_expr+'/state')
