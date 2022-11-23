#export
from transitions.extensions.markup import MarkupMachine
import json
import time

m = MarkupMachine(name="ExportedMachine")
m.add_state('A')
m.initial = 'A'

with open('statechart.json', 'r') as j:
     contents = json.loads(j.read())

new=[x for x in contents['transitions'] if x["trigger"] == "cleared"]
for i in new:
    m.add_transition(i['trigger'], i['source'], i['dest'])

a = m.markup
trigger = list()
def func(timest):
    empty = {}
    print(empty)
    empty['timestamp'] = timest
    empty['c'] = 'd'
    trigger.append(empty)

func(time.time())
func(time.time())
print(json.dumps({'trigger':trigger}, indent=2))