#from transitions.extensions import GraphMachine
#from functools import partial
from transitions.extensions.markup import MarkupMachine
import logging
import json
log = logging.getLogger(__name__)

class StateMachine:
    def idle(self):
        print('State is busy')

with open('statechart.json', 'r') as j:
     contents = json.loads(j.read())

model = StateMachine()
m = MarkupMachine(model= model, **contents)

assert model.is_idle()  # the model state was preserved
model.start() # >>>>> State is busy
assert model.state == 'busy'