import time
import json
import zenoh
from zenoh import Reliability, SampleKind, Query, Sample, KeyExpr, QueryTarget, Value

# Replace args with yaml

# Use pydantic to parse the yaml file

#class ActionSettings:
#    mode: Str
#    connect: Str
#    lsiten: Str


#args = parser.parse_args()
#conf = zenoh.Config.from_file(
#    args.config) if args.config is not None else zenoh.Config()
#if args.mode is not None:
#    conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(args.mode))
#if args.connect is not None:
#    conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(args.connect))
#if args.listen is not None:
#    conf.insert_json5(zenoh.config.LISTEN_KEY, json.dumps(args.listen))
#key = args.key
#target = {
#    'ALL': QueryTarget.ALL(),
#    'BEST_MATCHING': QueryTarget.BEST_MATCHING(),
#    'ALL_COMPLETE': QueryTarget.ALL_COMPLETE(),}.get(args.target)
## ------zenoh code -----

store = {}


def listener(sample: Sample):
    print(">> [Subscriber] Received {} ('{}': '{}')"
          .format(sample.kind, sample.key_expr, sample.payload.decode("utf-8")))
    if sample.kind == SampleKind.DELETE():
        store.pop(sample.key_expr, None)
    else:
        store[sample.key_expr] = sample


def query_handler(query: Query):
    print(">> [Queryable ] Received Query '{}'".format(query.selector))
    replies = []
    for stored_name, sample in store.items():
        if query.key_expr.intersects(stored_name):
            query.reply(sample)

def get_selector_key(replies):
    for reply in replies():
        try:
            key= reply.ok.key_expr
            value =reply.ok.payload.decode("utf-8")
        except:
            print(">> Received (ERROR: '{}')"
            .format(reply.err.payload.decode("utf-8")))
            return None
    return value

def feedback(key, pub):
    for idx in itertools.count() if args.iter is None else range(args.iter):
        replies = session.get('Genotyper/1/DNAsensor/1/stop', zenoh.ListCollector(), target=target)
        new_key = get_selector_key(replies)
        if new_key != 'stop':
            time.sleep(1)
            if idx == 35:
                break
            buf = (idx % 100) 
            print(f"Putting Data ('{key}': '{buf}')...")
            pub.put(buf)
        else:
            break
    stop_session()

def setup_action_server():
# # initiate logging
# zenoh.init_logger()
# 
# print("Opening session...")
# session = zenoh.open(conf)
# 
# print("Declaring Subscriber on '{}'...".format(key))
# sub = session.declare_subscriber(key, listener, reliability=Reliability.RELIABLE())
# 
# print("Declaring Queryable on '{}'...".format(key))
# queryable = session.declare_queryable(key, query_handler)
# 
# print("Declaring publisher on '{}'...".format(key))
# pub = session.declare_publisher(key)
# 
# session.put('Genotyper/1/DNAsensor/1/start', 'started')
# session.put('Genotyper/1/DNAsensor/1/health', 'alive')
# session.put('Genotyper/1/DNAsensor/1/stop', None)
    pass

def stop(session: Session, key: Str = 'Genotyper/1/DNAsensor/1/stop'):
    session.put(key, 'Stopped')


replies = session.get('Genotyper/1/DNAsensor/1/health', zenoh.ListCollector(), target=target)
new_key = get_selector_key(replies)
def stop_session():
    stop()
    result = session.get('Genotyper/1/DNAsensor/1/stop', zenoh.ListCollector(), target=target)
    print(get_selector_key(result))
    session.put('Genotypre/1/DNAsensor/1/health', 'None')
    sub.undeclare()
    queryable.undeclare()
    pub.undeclare()
    session.close()

if new_key != 'stop':
    feedback('Genotyper/1/DNAsensor/1/status', pub)


if __name__ == '__main__':
    # script goes here

    #settings = ActionSettings("action.yaml")
    #settings["key"] # ---> Over time you have to worry about "Validation Errors" -> Is this the right type? Is Empty? 

    # settings.key # <----- GuARANTEE! that parsing has checked for various validation errors

    # 1. Start the action server
    session = setup_action_server(settings)

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