import time
import json
import zenoh
from zenoh import QueryTarget, Value
from typing import Optional
from pydantic import BaseModel
import yaml

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
    iter: int
    value: str = None
    target: str
    declare_key_expr: str

class Client:
    def __init__(self, settings):
        self.settings = settings
        self.session = None

    def configuration(self):
        conf = zenoh.Config.from_file(
            self.settings.config) if self.settings.config is not None else zenoh.Config()
        if self.settings.mode is not None:
            conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(self.settings.mode))
        if self.settings.connect is not None:
            conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(self.settings.connect))
        if self.settings.listen is not None:
            conf.insert_json5(zenoh.config.LISTEN_KEY, json.dumps(self.settings.listen))
        return conf

    def target(self):
        target = {
            'ALL': QueryTarget.ALL(),
            'BEST_MATCHING': QueryTarget.BEST_MATCHING(),
            'ALL_COMPLETE': QueryTarget.ALL_COMPLETE(),}.get(self.settings.target)
        return target

    def get_selector_key(self, end_keyexpr):
        replies = self.session.get(self.settings.base_key_expr+end_keyexpr, zenoh.ListCollector(), target=self.target())
        for reply in replies():
            try:
                print(">> Received ('{}': '{}')"
                .format(reply.ok.key_expr, reply.ok.payload.decode("utf-8")))
                new_value = reply.ok.payload.decode("utf-8")
            except:
                print(">> Received (ERROR: '{}')"
                .format(reply.err.payload.decode("utf-8")))
        return new_value

    def setup_session(self):
        zenoh.init_logger()
        self.session = zenoh.open(self.configuration())

    def put(self, end_keyexpr, value):
        self.session.put(self.settings.base_key_expr+self.settings.end_keyexpr, value)

    def stop_session():
        self.put(self.settings.stop, 'Stopped')

    def get_status(self):
        self.get_selector_key(self.settings.status)


if __name__ == '__main__':
    with open('action.yml') as file:
        try:
            settingConfig = yaml.safe_load(file)  
        except yaml.YAMLError as exc:
            print(exc)

    settings = ActionSettings(**settingConfig)
    session = Client(settings)
    session.setup_session()
    session.get_status()
    
    
