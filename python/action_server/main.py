import sys
import time
import argparse
import json
import zenoh
import itertools
from zenoh import Reliability, SampleKind, Query, Sample, KeyExpr, QueryTarget, Value

# --- Command line argument parsing --- --- --- --- --- ---
parser = argparse.ArgumentParser(
    prog='z_storage',
    description='zenoh storage example')
parser.add_argument('--mode', '-m', dest='mode',
                    choices=['peer', 'client'],
                    type=str,
                    help='The zenoh session mode.')
parser.add_argument('--connect', '-e', dest='connect',
                    metavar='ENDPOINT',
                    action='append',
                    type=str,
                    help='Endpoints to connect to.')
parser.add_argument('--listen', '-l', dest='listen',
                    metavar='ENDPOINT',
                    action='append',
                    type=str,
                    help='Endpoints to listen on.')
parser.add_argument('--key', '-k', dest='key',
                    default='Genotyper/1/DNAsensor/**',
                    type=str,
                    help='The key expression matching resources to store.')
parser.add_argument('--value', '-v', dest='value',
                    default=None,
                    type=str,
                    help='The value to write.')
parser.add_argument("--iter", dest="iter",default=100, type=int,
                    help="How many puts to perform")
parser.add_argument('--target', '-t', dest='target',
                    choices=['ALL', 'BEST_MATCHING', 'ALL_COMPLETE', 'NONE'],
                    default='ALL',
                    type=str,
                    help='The target queryables of the query.')
parser.add_argument('--payload_size', '-p',
                    default=5,
                    type=int,
                    help='The value to write.')
parser.add_argument('--config', '-c', dest='config',
                    metavar='FILE',
                    type=str,
                    help='A configuration file.')

args = parser.parse_args()
conf = zenoh.Config.from_file(
    args.config) if args.config is not None else zenoh.Config()
if args.mode is not None:
    conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(args.mode))
if args.connect is not None:
    conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(args.connect))
if args.listen is not None:
    conf.insert_json5(zenoh.config.LISTEN_KEY, json.dumps(args.listen))
key = args.key
target = {
    'ALL': QueryTarget.ALL(),
    'BEST_MATCHING': QueryTarget.BEST_MATCHING(),
    'ALL_COMPLETE': QueryTarget.ALL_COMPLETE(),}.get(args.target)
# ------zenoh code -----

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

# initiate logging
zenoh.init_logger()

print("Opening session...")
session = zenoh.open(conf)

print("Declaring Subscriber on '{}'...".format(key))
sub = session.declare_subscriber(key, listener, reliability=Reliability.RELIABLE())

print("Declaring Queryable on '{}'...".format(key))
queryable = session.declare_queryable(key, query_handler)

print("Declaring publisher on '{}'...".format(key))
pub = session.declare_publisher(key)

session.put('Genotyper/1/DNAsensor/1/start', 'started')
session.put('Genotyper/1/DNAsensor/1/health', 'alive')
session.put('Genotyper/1/DNAsensor/1/stop', None)

replies = session.get('Genotyper/1/DNAsensor/1/health', zenoh.ListCollector(), target=target)
new_key = get_selector_key(replies)
def stop_session():
    session.put('Genotyper/1/DNAsensor/1/stop', 'Stopped')
    result = session.get('Genotyper/1/DNAsensor/1/stop', zenoh.ListCollector(), target=target)
    print(get_selector_key(result))
    session.put('Genotypre/1/DNAsensor/1/health', 'None')
    sub.undeclare()
    queryable.undeclare()
    pub.undeclare()
    session.close()

if new_key != 'stop':
    feedback('Genotyper/1/DNAsensor/1/status', pub)
