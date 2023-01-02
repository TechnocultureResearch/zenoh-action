import zenoh
from zenoh import Query, Sample
from pydantic import ValidationError
from contextlib import contextmanager
import logging
from transitions import MachineError
from typing import Type, Iterator
import time
from stateMachine import BaseStateMachine, Publisher
from config import ZenohConfig, ZenohSettings
from eventTypes import Event, Trigger

logging.getLogger().setLevel(logging.DEBUG)

class QueryableCallback:
    def __init__(self, statemachine: Type, settings: ZenohSettings) -> None:
        self.statemachine: Type = statemachine
        self.settings = settings

    def statechart(self) -> dict:
        '''
        Returns the statechart in json format.
        '''
        return self.statemachine.markup

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
            jsonstatechart = self.statechart()
            event = query.selector.decode_parameters()
            events = Event(jsonStateMachine=jsonstatechart, **event)
            trigger = Trigger(events.event, self.statemachine)
            trigger()
            payload = {'response_code': 'accepted',
                       'message': 'Trigger is Valid and it is triggered.'}
            query.reply(Sample(self.settings.base_key_expr+"/trigger", payload))
        except (ValidationError, ValueError, MachineError, AttributeError) as error:
            payload = {"response_code": "rejected",
                       "message": "{}".format(error)}
            query.reply(Sample(self.settings.base_key_expr+"/trigger", payload))

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
            jsonStateMachine = self.statemachine.markup
            payload = {'response_code': 'accepted',
                       'message': jsonStateMachine}
            query.reply(Sample(self.settings.base_key_expr +
                        "/statechart", payload))
        except (ValueError, AttributeError) as error:
            payload = {'response_code': 'rejected',
                       'message': "{}".format(error)}
            query.reply(Sample(self.settings.base_key_expr+"/statechart", payload))

class Session:
    def __init__(self, settings: ZenohSettings, statemachine: Type, handlers: QueryableCallback) -> None:
        '''
        Initializes the variables.
        settings: object of the ZenohConfig class which validates zenoh configuration variables.
        statemachine: object statemachine to coordinate with statechart and trigger endpoint. 
        '''
        self.settings: ZenohSettings = settings
        self.statemachine: Type = statemachine
        self.handler: QueryableCallback = handlers
        self.open()
    
    def open(self) -> None:
        '''
        Creates a zenoh session and registers queryables.
        session: creates zenoh session.
        trigger_queryable: object of queryable for trigger endpoint.
        statechart_queryable: object of queryable for statechart endpoint.
        '''

        zenohConfig: ZenohConfig = ZenohConfig(self.settings)
        self.conf: zenoh.Config = zenohConfig.zenohconfig()

        self.session: zenoh.Session = zenoh.open(self.conf)
        self.trigger_queryable: zenoh.Queryable = self.session.declare_queryable(self.settings.base_key_expr+"/trigger", self.handler.trigger_query_handler)
        self.statechart_queryable: zenoh.Queryable = self.session.declare_queryable(self.settings.base_key_expr+"/statechart", self.handler.statechart_query_handler)

    def close(self) -> None:
        '''
        Closes the zenoh session.
        '''
        self.trigger_queryable.undeclare()
        self.statechart_queryable.undeclare()
        self.session.close()

@contextmanager
def session_manager(settings: ZenohSettings, statemachine: Type, handlers: QueryableCallback) -> Iterator[Session]:
    '''
    This function creates a session object and closes it when the context is exited.
    '''
    try:
        session: Session = Session(settings = settings, statemachine=statemachine, handlers=handlers)
        yield session
    except KeyboardInterrupt:
        logging.error("Interrupted by user")
    finally:
        session.close()
        logging.debug("server closed")
    
if __name__ == "__main__":

    zenoh.init_logger()

    settings: ZenohSettings = ZenohSettings()
    pub = Publisher(settings=settings)
    pub.createZenohPublisher()
    statemachine = BaseStateMachine()
    handlers: QueryableCallback = QueryableCallback(statemachine=statemachine, settings=settings)

    with session_manager(settings=settings, statemachine=statemachine, handlers=handlers) as session:     
        logging.debug("server started")
        while True:
            time.sleep(1)