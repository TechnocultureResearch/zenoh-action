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
                    default='Genotyper/1/DNAsensor/1/start',
                    type=str,
                    help='The key expression matching resources to store.')
parser.add_argument('--target', '-t', dest='target',
                    choices=['ALL', 'BEST_MATCHING', 'ALL_COMPLETE', 'NONE'],
                    default='ALL',
                    type=str,
                    help='The target queryables of the query.')
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

def get_selector_key(replies):
    for reply in replies():
        try:
            print(">> Received ('{}': '{}')"
            .format(reply.ok.key_expr, reply.ok.payload.decode("utf-8")))
            new_value = reply.ok.payload.decode("utf-8")
        except:
            print(">> Received (ERROR: '{}')"
            .format(reply.err.payload.decode("utf-8")))
    return new_value

# ---- zenoh code ----

zenoh.init_logger()
session = zenoh.open(conf)

if key == 'Genotyper/1/DNAsensor/1/start':
    session.put('Genotyper/1/DNAsensor/1/start', 'started')
    replies = session.get('Genotyper/1/DNAsensor/1/start', zenoh.ListCollector(), target=target)
    value = get_selector_key(replies)

if key == 'Genotyper/1/DNAsensor/1/stop':
    session.put('Genotyper/1/DNAsensor/1/stop', 'stop')
    replies = session.get('Genotyper/1/DNAsensor/1/stop', zenoh.ListCollector(), target=target)
    value = get_selector_key(replies)

elif key == 'Genotyper/1/DNAsensor/1/status':
    value = 0
    while value < 1000:
        replies = session.get('Genotyper/1/DNAsensor/1/status', zenoh.ListCollector(), target=target)
        value = get_selector_key(replies)
        time.sleep(60)
