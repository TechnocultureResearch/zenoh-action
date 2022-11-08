import time
import json
import itertools
from zenoh import Reliability, SampleKind, Query, Sample, KeyExpr, QueryTarget, Value
from typing import Optional
from pydantic import BaseModel
import logging
from transitions import Machine
log = logging.getLogger(__name__)

class ActionSettings(BaseModel):
    mode: str = None
    connect: str = None
    listen: str = None
    config: None
    start: str
    stop: str
    status: str
    health: str
    busy: str
    done: str
    base_key_expr: str
    iter = int
    value: str = None
    target: str

class handlers():
    def __init__(self):
        self.store = dict()

    def listener(self, sample: Sample):
        print(">> [Subscriber] Received {} ('{}': '{}')"
            .format(sample.kind, sample.key_expr, sample.payload.decode("utf-8")))
        if sample.kind == SampleKind.DELETE():
            self.store.pop(sample.key_expr, None)
        else:
            self.store[sample.key_expr] = sample

    def query_handler(self, query: Query):
        print(">> [Queryable ] Received Query '{}'".format(query.selector))
        replies = []
        for stored_name, sample in self.store.items():
            if query.key_expr.intersects(stored_name):
                query.reply(sample)

    def feedback(self, key, pub, iter):
        for idx in itertools.count() if iter is None else range(iter):
            time.sleep(1)
            buf = (idx % 100) 
            print(f"Putting Data ('{key}': '{buf}')...")
            pub.put(buf)

class session(handlers):
    def __init__(self, settings):
        self.setting = settings
        self.session = None
        self.sub = None
        self.pub = None
        self.queryable = None
    
    def configuration(self):
        conf = zenoh.Config.from_file(
            self.setting.config) if args.config is not None else zenoh.Config()
        if self.setting.mode is not None:
            conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(self.setting.mode))
        if self.setting.connect is not None:
            conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(self.setting.connect))
        if self.setting.listen is not None:
            conf.insert_json5(zenoh.config.LISTEN_KEY, json.dumps(self.setting.listen))
        return conf

    def put(self, end_expr, value):
        session.put(self.setting.base_key_expr+self.setting.end_expr, value)

    def target(self):
        target = {
            'ALL': QueryTarget.ALL(),
            'BEST_MATCHING': QueryTarget.BEST_MATCHING(),
            'ALL_COMPLETE': QueryTarget.ALL_COMPLETE(),}.get(self.setting.target)
        return target

    def get(self, end_expr):
        result = session.get(self.setting.base_key_expr+self.setting.end_expr, zenoh.ListCollector(), target=target())
        for reply in replies():
            try:
                key= reply.ok.key_expr
                value =reply.ok.payload.decode("utf-8")
            except:
                print(">> Received (ERROR: '{}')"
                .format(reply.err.payload.decode("utf-8")))
                return None
        return value

    def setup_action_server(self):
        # initiate logging
        log.info('Starting Action Server....')
        zenoh.init_logger()

        self.session = zenoh.open(configuration())

        self.sub = self.session.declare_subscriber(key, listener(), reliability=Reliability.RELIABLE())
        
        self.queryable = self.session.declare_queryable(key, query_handler())
        
        self.pub = self.session.declare_publisher(key)
        
        put(self.setting.start, 'Started')
        put(self.setting.health, 'Alive')
    
    def publish_data(self):
        feedback(self.setting.base_key_expr+self.setting.done, self.pub, self.setting.iter)

    def close_action_server(self):
        log.warning('Stopping Session.....')
        put(self.setting.stop, 'Stopped')
        put(self.setting.start, None)
        put(self.setting.health, None)
        self.sub.undeclare()
        self.queryable.undeclare()
        self.pub.undeclare()
        self.session.close()

class state_transitions:
    states = ['Idle', 'Start', 'Busy', 'Stop', 'Error']
    # trigger functions
    def OnEntry():
        pass
    def OnExit():
        pass
    def start():
        pass
    def stop():
        pass
    def status():
        pass

if __name__ == '__main__':
    # script goes here

    settings = ActionSettings("action.yml")

    # 1. Start the action server
    session = session(settings)
    # 2. wait for events

    #   States: Idle, Start, Busy, Stop, Error
    #   Events: Start, Stop

    # State: OnEntry, OnExit

    #   Monitor: Status ---> Publishing udates on our own regular OR irregular frequency


    '''
        0. Remove the CLI realted things
        1. Use a `action.yml` file to co-ordinate shared data [This is very similar to how ROS 2 works: You also declare data type]: PYDANTIC
        2. Use a state chart library to define the action server systematically: PYTRANSITIONS
        3. Encapsulate individual transitions or conditions into functions (Refere to Pytransitions)
        4. Write functions that provide higher level abstractions
    '''
