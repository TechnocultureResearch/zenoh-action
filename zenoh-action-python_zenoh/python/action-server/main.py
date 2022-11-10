import time
import json
import itertools
import zenoh
from zenoh import Reliability, SampleKind, Query, Sample, KeyExpr, QueryTarget, Value
from typing import Optional
from pydantic import BaseModel
import logging
from transitions import Machine
from transitions.extensions.asyncio import AsyncMachine
import asyncio
import yaml
log = logging.getLogger(__name__)

# describe settings for parsing values.
class ActionSettings(BaseModel):
    mode: str = None
    connect: str = None
    listen: str = None
    config: str = None
    start: str
    stop: str
    status: str
    health: str
    busy: str
    done: str
    base_key_expr: str
    iter: int
    target: str
    base_key_expr: str
    declare_key_expr: str

store = {}
session = None
sub = None
pub = None
queryable = None
class Handlers():
    # handler functions which are going to ussession declarables.
    # listens all the data which publisher puts on reciever.
    def listener(self, sample: Sample):
        print(">> [Subscriber] Received {} ('{}': '{}')"
            .format(sample.kind, sample.key_expr, sample.payload.decode("utf-8")))
        if sample.kind == SampleKind.DELETE():
            store.pop(sample.key_expr, None)
        else:
            store[sample.key_expr] = sample

    # replies of every query which get function asks.
    def query_handler(self, query: Query):
        print(">> [Queryable ] Received Query '{}'".format(query.selector))
        replies = []
        for stored_name, sample in store.items():
            if query.key_expr.intersects(stored_name):
                query.reply(sample)

    # for publishing the data on subscriber or can be said that the to take the feedback
    def publisher(self, key, iter):
        print(iter)
        print(pub)
        print(sub)
        for idx in itertools.count() if iter is None else range(int(iter)):
            time.sleep(1)
            buf = (idx % 100) 
            print(f"Putting Data ('{key}': '{buf}')...")
            pub.put(buf)
        

class Session(Handlers):
    # creates session and perform session related tasks. Takes an object of settings.
    def __init__(self, settings):
        self.setting = settings
        #session = None
        #self.sub = None
        #pub = None
        #queryable = None

    # configures the zenoh configuration from settings variables and returns a configuration object.
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

    # defines target ofqueryable.
    def target(self):
        target = {
            'ALL': QueryTarget.ALL(),
            'BEST_MATCHING': QueryTarget.BEST_MATCHING(),
            'ALL_COMPLETE': QueryTarget.ALL_COMPLETE(),}.get(self.setting.target)
        return target

    # sends the query toqueryable and print its output and returns a value of the sent keyexpr.
    def get(self, end_expr):
        result = session.get(self.setting.base_key_expr+end_expr, zenoh.ListCollector(), target=self.target())
        for reply in result():
            try:
                key= reply.ok.key_expr
                value =reply.ok.payload.decode("utf-8")
            except:
                raise_error(reply.err.payload.decode("utf-8"))
        return value

    def raise_error(self, error):
        print(">> Received (ERROR: '{}')"
                .format(error))
        

    # starts the action server and declares subscriqueryable and publisher.
    def setup_action_server(self):
        # initiate logging
        log.info('Starting Action Server....')
        zenoh.init_logger()
        session = zenoh.open(self.configuration())
        
        sub = session.declare_subscriber(self.setting.declare_key_expr, self.listener, reliability=Reliability.RELIABLE())
        
        queryable = session.declare_queryable(self.setting.declare_key_expr, self.query_handler)
        
        pub = session.declare_publisher(self.setting.base_key_expr+self.setting.done)
        
        session.put(self.setting.base_key_expr+self.setting.start, 'Started')
        session.put(self.setting.base_key_expr+self.setting.health, 'Alive')
        session.put(self.setting.base_key_expr+self.setting.status, 'Busy')
    
    # publish the data on subscriber through publisher.
    def publish_data(self):
        self.publisher(self.setting.base_key_expr+self.setting.done, self.setting.iter)
        #self.put(self.setting.status, 'Completed')

    # closes the server and undeclares the declared variables.
    def close_action_server(self):
        log.warning('Stopping Session.....')
        self.put(self.setting.stop, 'Stopped')
        self.put(self.setting.start, None)
        self.put(self.setting.health, None)
        self.put(self.setting.status, None)
        self.sub.undeclare()
        queryable.undeclare()
        pub.undeclare()
        session.close()

class State_machine:
    #   States: Idle, Start, Busy, Stop, Error
    #   Events: Start, Stop

    # State: OnEntry, OnExit

    #   Monitor: Status ---> Publishing udates on our own regular OR irregular frequency

    states = ['Idle', 'Start', 'Busy', 'Stop', 'Error']
    transitions = [['start', 'Idle','Start'],
                    ['status', 'Start', 'Busy'],
                    ['status', 'Busy', 'Busy'],
                    ['stop', 'Busy', 'Stop'],
                    ['status', 'Stop', 'Idle'],
                    ['raise_error', '*', 'Error']]

    def __init__(self, obj, setting):
        self.obj = obj
        self.machine = Machine(model=self, states=State_machine.states,
                               transitions=State_machine.transitions, on_exception='raise_error', initial='Idle')
        self.setting = setting

    # trigger functions
    def OnEntry(self) -> bool:
        # monitor status continuously
        if self.obj.get(self.setting.status) == 'Completed':
            print('hello')
            return True
        print('false')
        return False
        
    def start(self):
        # startsession, make status busy, and publisher starts publishing on subscriber.
        self.obj.setup_action_server()
        self.obj.publish_data()
        #if self.OnEntry:
            #self.stop()
        
    def stop(self):
        # stopssession, undeclares all variables, and print the status value.
        self.status()
        self.obj.close_action_server()

    def status(self):
        # make status busy until the stop triggers.
        #await asyncio.sleep(60)
        print(self.obj.get('/status'))
    
    def raise_error(self):
        print('error')
    
    # State remains idle until start triggers
    # When start triggers state will be busy and remains busy until the event stop triggers
    # when stop triggers then the state will be Idle 
    # start -> busy, condition 
    # busy -> idle , condition


if __name__ == '__main__':
    # script goes here
    with open('action.yml') as file:
        try:
            databaseConfig = yaml.safe_load(file)  
        except yaml.YAMLError as exc:
            print(exc)

    settings = ActionSettings(**databaseConfig)
    session = Session(settings)
    # 1. Start the action sersession = Session(settings)
    # 2. wait for events
    events = State_machine(session, settings)
    print(events.state)
    events.start()
    print(events.state)
    


    '''
        0. Remove the CLI realted things
        1. Use a `action.yml` file to co-ordinate shared data [This is very similar to how ROS 2 works: You also declare data type]: PYDANTIC
        2. Use a state chart library to define the action server systematically: PYTRANSITIONS
        3. Encapsulate individual transitions or conditions into functions (Refere to Pytransitions)
        4. Write functions that provide higher level abstractions
    '''