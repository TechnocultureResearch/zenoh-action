import zenoh
import time
from zenoh import Query, Sample
from stateMachine import BaseStateMachine
from config import ZenohConfig, ZenohSettings
from eventTypes import Event, Trigger
from pydantic import ValidationError
from contextlib import contextmanager
import logging
from transitions import MachineError
from typing import Any

logging.getLogger().setLevel(logging.DEBUG)

@contextmanager
def session_manager(settings: ZenohSettings, statemachine: Any):
    '''
    This function creates a session object and closes it when the context is exited.
    '''
    try:
        session: Session = Session(settings = settings, statemachine=statemachine)
        yield session
    except KeyboardInterrupt:
        logging.error("Interrupted by user")
    finally:
        session.close()
        logging.debug("server closed")

class CallbackMethod:
    def __init__(self) -> None:
        pass

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
            validator = Event(**query.selector.decode_parameters())
            trigger = Trigger(validator.event, self.statemachine)
            trigger()
            payload = {'response_code': 'accepted',
                       'message': 'Trigger is Valid and it is triggered.'}
            query.reply(Sample(self.args.base_key_expr+"/trigger", payload))
        except (ValidationError, ValueError, MachineError, AttributeError) as error:
            payload = {"response_code": "rejected",
                       "message": "{}".format(error)}
            query.reply(Sample(self.args.base_key_expr+"/trigger", payload))

    def statechart_query_handler(self, query: Query) -> None:
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



class Session:
    '''
    This class performs tasks on zenohd on two endpoints i.e. `/trigger` and `/statechart`.
    '''
    def __init__(self,settings: ZenohSettings, statemachine: Any, callback: CallbackMethod) -> None:
        '''
        Initializes the variables.
        args: object of the ZenohConfig class which validates zenoh configuration variables.
        statemachine: object statemachine to coordinate with statechart and trigger endpoint. 
        '''
        zenohConfig: ZenohConfig = ZenohConfig(settings)
        self.conf: zenoh.Configuration = zenohConfig.zenohconfig()
        self.statemachine: Any = statemachine
        self.callback: CallbackMethod = callback
        self.open()

    def open(self) -> None:
        '''
        Creates a zenoh session and registers queryables.
        session: creates zenoh session.
        trigger_queryable: object of queryable for trigger endpoint.
        statechart_queryable: object of queryable for statechart endpoint.
        '''
        self.session: zenoh.Session = zenoh.open(self.conf)
        self.trigger_queryable: zenoh.Queryable = self.session.declare_queryable(self.args.base_key_expr+"/trigger", self.callback.trigger_query_handler)
        self.statechart_queryable: zenoh.Queryable = self.session.declare_queryable(self.args.base_key_expr+"/statechart", self.callback.statechart_query_handler)

    def close(self) -> None:
        '''
        Closes the zenoh session.
        '''
        self.trigger_queryable.undeclare()
        self.statechart_queryable.undeclare()
        self.session.close()
if __name__ == "__main__":
    """
    Creates session object and runs the session.
    """
    zenoh.init_logger()
    statemachine = BaseStateMachine()
    callback = CallbackMethod()
    with session_manager(statemachine) as session:
        logging.debug("server started")
        while True:
            time.sleep(1)

