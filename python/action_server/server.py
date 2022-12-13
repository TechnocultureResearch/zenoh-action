import zenoh
import sys
import time
from zenoh import Query, Sample
from state_machine import StateMachineModel
from config import ZenohConfig, EventModel
from pydantic import ValidationError
from result import Ok, Err
from contextlib import contextmanager
from typing import Self
import logging

logging.getLogger().setLevel(logging.DEBUG)

@contextmanager
def session_manager():
    '''
    This function creates a session object and closes it when the context is exited.
    '''
    try:
        session = Session()
        yield session
    except KeyboardInterrupt:
        print("Interrupted by user")
        sys.exit(0)
    finally:
        session.close()
        print("server closed")

class Session:
    '''
    This class performs tasks on zenohd on two endpoints i.e. `/trigger` and `/statechart`.
    '''
    def __init__(self, **kwargs) -> 'Self':
        '''
        Initializes the variables.
        args: object of the ZenohConfig class which validates zenoh configuration variables.
        session: creates zenoh session.
        trigger_queryable: object of queryable for trigger endpoint.
        statechart_queryable: object of queryable for statechart endpoint.
        statemachine: object statemachine to coordinate with statechart and trigger endpoint. 
        '''
        zenoh_config = ZenohConfig(**kwargs)
        self.conf, self.args = zenoh_config.zenohconfig()
        self.statemachine = StateMachineModel()
        self.open()

    def open(self):
        '''
        Creates a zenoh session and registers queryables.
        '''
        self.session = zenoh.open(self.conf)
        self.trigger_queryable = self.session.declare_queryable(self.args.base_key_expr+"/trigger", self.trigger_query_handler)
        self.statechart_queryable = self.session.declare_queryable(self.args.base_key_expr+"/statechart", self.statechart_query_handler)

    def close(self):
        '''
        Closes the zenoh session.
        '''
        self.trigger_queryable.undeclare()
        self.statechart_queryable.undeclare()
        self.session.close()

    def trigger_query_handler(self, query: Query) -> None:
        '''
        A query handler for `**/trigger` queryable. It checks if an event is possible or not from state machine for that you need to import statemachine states and transitions.
        Args:
            query: a string which describes query in the form of keyexpr
        Reply(Ok):
            Replies to a query with payload in json format with keys response_code and message that trigger is accepted, if no error arises.
        Reply(Err):
            Replies a err query with payload in json format with keys response_code and message containing error, if any err arises.
        '''
        try: 
            print(">> [Queryable ] Received Query '{}'".format(query.selector))
            validator = EventModel(**query.selector.decode_parameters())
            self.statemachine.event_trigger(validator.event)
            payload = {'reponse_code':'accepted', 'message':'Trigger is accepted and triggered'}
            Ok(query.reply(Sample(self.args.base_key_expr+"/trigger", payload)))
        except (ValidationError, ValueError) as error:
            payload = {"reponse_code":"rejected", "message":"{}".format(error)}
            Err(query.reply((Sample(self.args.base_key_expr+"/trigger", payload))))
            
    def statechart_query_handler(self, query: Query):
        '''
        Query handle to reply the queries on the key_expr `**/statechart`.
        Args:
            query: a string which describes query in the form of keyexpr.
        Reply(Ok):
            Replies to a query with complete statemachine in serialized json format, if no error arises.
        Reply(Err):
            Replies a err query with payload in json format containing error, if any err arises.
        '''
        try:
            markup_statechart = self.statemachine.statechart()
            Ok(query.reply(Sample(self.args.base_key_expr+"/statechart", markup_statechart)))
        except ValueError as error:
            payload = {'Error': "{}".format(error)}
            Err(query.reply(Sample(self.args.base_key_expr+"/statechart", payload)))

if __name__ == "__main__":
    """
    Creates session object and runs the session.
    """
    with session_manager() as session:
        logging.debug("server open")
        while True:
            # logging.debug("server running")
            time.sleep(1)
