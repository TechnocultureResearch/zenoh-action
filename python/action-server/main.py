import json
import zenoh
from zenoh import Query, Sample, Timestamp
import asyncio
from state_machine import Session_state
from validators import ZenohValidator, EventModel
from pydantic import ValidationError

class Handlers:
    '''
    Handlers class contains callback methods for queryables.
    Args:
        takes 0 arguments.
    Methods:
        trigger_query_handler: method replies of every query related to the keyexpression `/trigger`.
        statechart_query_handler: method replies to `/statechart` related query.
    '''
    def __init__(self) -> None:
        self.publisher = None
        self.zenohConfig = ZenohValidator()

    def trigger_query_handler(self, query: Query) -> None:
        '''
        A query handler for `**/trigger` queryable. It checks if an event is possible or not from state machine for that you need to import statemachine states and transitions.
        Args:
            query: a string which describes query in the form of keyexpr
        Replies:
            Replies to a query with a keyexpression and a payload in json format.
        Raises:
            ValueError if any ValidationError or ValueError arises.
        '''
        try: 
            print(">> [Queryable ] Received Query '{}'".format(query.selector))
            validator = EventModel(query.selector.decode_parameters())
            value = self.session_state.triggered_event(validator.event)
            payload = {'reponse_code':'accepted', 'message':'Trigger is accepted and triggered'}
            query.reply(Sample(self.zenohConfig.base_key_expr+"/trigger", payload))
        except (ValidationError, ValueError) as error:
            payload = {'response_code':'rejected', 'message': error}
            query.reply(Sample(self.zenohConfig.base_key_expr+'/trigger', payload))
            raise
    
    def statechart_query_handler(self, query: Query):
        '''
        Query handle to reply the queries on the key_expr `**/statechart`.
        Args:
            query: a string which describes query in the form of keyexpr.
        Replies:
            Replies to a query with a keyexpression and a payload in json format.
        Raises:
            ValueError if any ValueError arises.
        '''
        try:
            session_state = Session_state(pub=self.publisher)
            statechart = session_state.statechart()
            query.reply(Sample(self.zenohConfig.base_key_expr+"/statechart", statechart))
        except ValueError as error:
            payload = {'Error': error}
            query.reply(Sample(self.zenohConfig.base_key_expr+"/statechart", payload))
            raise

class Session(Handlers):
    '''
    This class performs tasks on zenohd.
    Args:
        Takes 0 arguments.
    Methods:
        setup_action_server method:
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
        self.zenohConfig = ZenohValidator()

    def setup_action_server(self) -> None:
        '''
        To perform tasks on zenohd we need to open session and declare queryables for `/trigger` & `/statechart` and publisher for publishing `/state`.
        Args: 
            Takes 0 arguments.
        Raises:
            RuntimeError, if any exception arises.
        '''
        try:
            conf = zenoh.Config.from_file(
                self.zenohConfig.config) if self.zenohConfig.config != "" else zenoh.Config()
            if self.zenohConfig.mode != "":
                conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(self.zenohConfig.mode))
            if self.zenohConfig.connect != "":
                conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(self.zenohConfig.connect))
            if self.zenohConfig.listen != "":
                conf.insert_json5(zenoh.config.LISTEN_KEY, json.dumps(self.zenohConfig.listen))
            zenoh.init_logger()
            self.session = zenoh.open(conf)
            
            self.trigger_queryable = self.session.declare_queryable(self.zenohConfig.base_key_expr+'/trigger', self.trigger_query_handler)
            self.statechart_queryable = self.session.declare_queryable(self.zenohConfig.base_key_expr+'/statechart', self.statechart_query_handler)
            self.pub = self.session.declare_publisher(self.zenohConfig.base_key_expr+'/state')
            self.publisher = self.pub

        except Exception as error:
            raise RuntimeError("Error encountered while opening session: {}. \n Hint: Please restart the server.".format(error))
