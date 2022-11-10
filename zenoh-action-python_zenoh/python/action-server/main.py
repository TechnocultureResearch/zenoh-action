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
    def publisher(self, key,pub, iter):
        for idx in itertools.count() if iter is None else range(int(iter)):
            time.sleep(1)
            buf = (idx % 100) 
            print(f"Putting Data ('{key}': '{buf}')...")
            pub.put(buf)
        

class Session(Handlers):
    # creates self.session and perform self.session related tasks. Takes an object of settings.
    def __init__(self, settings):
        self.setting = settings
        #self.session = None
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
        result = self.session.get(self.setting.base_key_expr+end_expr, zenoh.ListCollector(), target=self.target())
        for reply in result():
            try:
                key= reply.ok.key_expr
                value =reply.ok.payload.decode("utf-8")
            except:
                raise_error(reply.err.payload.decode("utf-8"))
        return value

    # starts the action server and declares subscriqueryable and publisher.
    def setup_action_server(self):
        # initiate logging
        log.info('Starting Action Server....')
        zenoh.init_logger()
        self.session = zenoh.open(self.configuration())
        
        self.sub = self.session.declare_subscriber(self.setting.declare_key_expr, self.listener, reliability=Reliability.RELIABLE())
        
        self.queryable = self.session.declare_queryable(self.setting.declare_key_expr, self.query_handler)
        
        self.pub = self.session.declare_publisher(self.setting.base_key_expr+self.setting.done)
        
        self.session.put(self.setting.base_key_expr+self.setting.start, 'Started')
        self.session.put(self.setting.base_key_expr+self.setting.health, 'Alive')
        self.session.put(self.setting.base_key_expr+self.setting.status, 'Busy')
        self.publish_data()
    
    # publish the data on subscriber through publisher.
    def publish_data(self):
        self.publisher(self.setting.base_key_expr+self.setting.done, self.setting.iter)
        self.put(self.setting.status, 'Completed')

    # closes the server and undeclares the declared variables.
    def close_action_server(self):
        log.warning('Stopping Session.....')
        self.session.put(self.setting.stop, 'Stopped')
        self.session.put(self.setting.start, None)
        self.session.put(self.setting.health, None)
        self.session.put(self.setting.status, None)
        self.sub.undeclare()
        self.queryable.undeclare()
        self.pub.undeclare()
        self.session.close()

class State_machine:

    states = ['Idle', 'Start', 'Busy', 'Stop', 'Error']
    transitions = [['start', 'Idle','Start'],
                    ['status', 'Start', 'Busy'],
                    ['status', 'Busy', 'Busy'],
                    ['stop', 'Busy', 'Stop'],
                    ['status', 'Stop', 'Idle'],
                    ['raise_error', '*', 'Error']]

    def __init__(self, self.session, setting):
        self.self.session = self.session
        self.machine = Machine(model=self, states=State_machine.states,
                               transitions=State_machine.transitions, on_exception='raise_error', initial='Idle')
        self.setting = setting

    # trigger functions
    def OnEntry(self) -> bool:
        # monitor status continuously
        if self.self.session.get(self.setting.status) == 'Completed':
            print('hello')
            return True
        print('false')
        return False
        
    def start(self):
        # startsession, make status busy, and publisher starts publishing on subscriber.
        self.self.session.setup_action_server()
        if self.OnEntry:
            self.stop()
        
    def stop(self):
        # stops session, undeclares all variables, and print the status value.
        self.status()
        self.self.session.close_action_server()

    def status(self):
        # make status busy until the stop triggers.
        #await asyncio.sleep(60)
        print(self.self.session.get('/status'))
    
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
            settingConfig = yaml.safe_load(file)  
        except yaml.YAMLError as exc:
            print(exc)

    settings = ActionSettings(**settingConfig)
    # 1. Start the action server session = Session(settings)
    session = Session(settings)
    # 2. wait for events
    events = State_machine(session, settings)
    events.start()

    c = '\0'
    while c != 'q':
        c = sys.stdin.read(1)
        if c == '':
            time.sleep(1)