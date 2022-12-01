import json
import zenoh
from zenoh import Query, Sample
from state_machine import StateMachineModel
from validators import ZenohConfig, EventModel
from pydantic import ValidationError


class Session:
    '''
    This class performs tasks on zenohd on two endpoints i.e. `/trigger` and `/statechart`.
    '''
    def __init__(self) -> None:
        '''
        Initializes the variables.
        zenohConfig: object of the ZenohConfig class which validates zenoh configuration variables.
        session: creates zenoh session.
        trigger_queryable: object of queryable for trigger endpoint.
        statechart_queryable: object of queryable for statechart endpoint.
        statemachine: object statemachine to coordinate with statechart and trigger endpoint. 
        '''
        self.zenohConfig = ZenohConfig()
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
        self.statemachine = StateMachineModel()

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
            validator = EventModel(**query.selector.decode_parameters())
            self.statemachine.event_trigger(validator.event)
            payload = {'reponse_code':'accepted', 'message':'Trigger is accepted and triggered'}
            query.reply(Sample(self.zenohConfig.base_key_expr+"/trigger", payload))
        except ValueError as error:
            payload = {"reponse_code":"rejected", "message":"{}".format(error)}
            query.reply(Sample(self.zenohConfig.base_key_expr+"/trigger", payload))
            raise
        except ValidationError as error:
            payload = {"reponse_code":"rejected", "message":"{}".format(error)}
            query.reply(Sample(self.zenohConfig.base_key_expr+"/trigger", payload))
            raise
            
            
    def statechart_query_handler(self, query: Query):
        '''
        Query handle to reply the queries on the key_expr `**/statechart`.
        Args:
            query: a string which describes query in the form of keyexpr.
        Replies:
            Replies to a query with a keyexpression and a payload in json format.
        Raises:
            ValueError, if any ValueError arises.
        '''
        try:
            markup_statechart = self.statemachine.statechart()
            query.reply(Sample(self.zenohConfig.base_key_expr+"/statechart", markup_statechart))
        except ValueError as error:
            payload = {'Error': error}
            query.reply(Sample(self.zenohConfig.base_key_expr+"/statechart", payload))
            raise
            