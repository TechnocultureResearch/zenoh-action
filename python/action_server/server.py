import zenoh
import time
from zenoh import Query, Sample
from stateMachine import BaseStateMachine
from config import ZenohConfig
from eventTypes import EventModel, Trigger, MarkupStatechart
from pydantic import ValidationError
from contextlib import contextmanager
import logging
from transitions import MachineError

logging.getLogger().setLevel(logging.DEBUG)

@contextmanager
def session_manager(statemachine: object):
    '''
    This function creates a session object and closes it when the context is exited.
    '''
    try:
        session = Session(statemachine=statemachine)
        yield session
    except KeyboardInterrupt:
        logging.error("Interrupted by user")
    finally:
        session.close()
        logging.debug("server closed")

class Session:
    '''
    This class performs tasks on zenohd on two endpoints i.e. `/trigger` and `/statechart`.
    '''
    def __init__(self,
                statemachine: object,
                mode: str = "peer",
                connect: str = "",
                listen: str = "",
                config: str = "",
                base_key_expr: str = "Genotyper/1/DNASensor/1",
                complete: bool = False) -> None:
        '''
        Initializes the variables.
        args: object of the ZenohConfig class which validates zenoh configuration variables.
        statemachine: object statemachine to coordinate with statechart and trigger endpoint. 
        '''
        zenohConfig = ZenohConfig(mode=mode, connect=connect, listen=listen, config=config, base_key_expr=base_key_expr, complete=complete)
        self.conf, self.args = zenohConfig.zenohconfig()
        self.statemachine = statemachine
        self.open()

    def open(self):
        '''
        Creates a zenoh session and registers queryables.
        session: creates zenoh session.
        trigger_queryable: object of queryable for trigger endpoint.
        statechart_queryable: object of queryable for statechart endpoint.
        '''
        self.session = zenoh.open(self.conf)
        self.trigger_queryable = self.session.declare_queryable(self.args.base_key_expr+"/trigger", self.trigger_query_handler, self.args.complete)
        self.statechart_queryable = self.session.declare_queryable(self.args.base_key_expr+"/statechart", self.statechart_query_handler, self.args.complete)

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
        Reply:
            Replies query with payload in json format with keys response_code and message that trigger is accepted, if no error arises.
        Reply:
            Replies query with payload in json format with keys response_code and message containing error, if any err arises.
        '''
        try:
            logging.debug(">> [Queryable ] Received Query '{}'".format(query.selector))
            validator = EventModel(**query.selector.decode_parameters())
            trigger = Trigger(validator.event, self.statemachine)
            trigger()
            payload = {'response_code': 'accepted',
                       'message': 'Trigger is Valid and it is triggered.'}
            query.reply(Sample(self.args.base_key_expr+"/trigger", payload))
        except (ValidationError, ValueError, MachineError, AttributeError) as error:
            payload = {"response_code": "rejected",
                       "message": "{}".format(error)}
            query.reply(Sample(self.args.base_key_expr+"/trigger", payload))

    def statechart_query_handler(self, query: Query):
        '''
        Query handle to reply the queries on the key_expr `**/statechart`.
        Args:
            query: a string which describes query in the form of keyexpr.
        Reply:
            Replies query with complete statemachine in serialized json format, if no error arises.
        Reply:
            Replies query with payload in json format containing error, if any err arises.
        '''
        try:
            logging.debug(">> [Queryable ] Received Query '{}'".format(query.selector))
            markup_statechart = self.statemachine.markup
            payload = {'response_code': 'accepted',
                       'message': markup_statechart}
            query.reply(Sample(self.args.base_key_expr +
                        "/statechart", payload))
        except (ValueError, AttributeError) as error:
            payload = {'response_code': 'rejected',
                       'message': "{}".format(error)}
            query.reply(Sample(self.args.base_key_expr+"/statechart", payload))

if __name__ == "__main__":
    """
    Creates session object and runs the session.
    """
    zenoh.init_logger()
    statemachine = BaseStateMachine()
    with session_manager(statemachine) as session:
        logging.debug("server started")
        while True:
            time.sleep(1)

