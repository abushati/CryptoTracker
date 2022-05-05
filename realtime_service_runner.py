from realtime_updater.realtime_service_init import run
import argparse

parser = argparse.ArgumentParser(description='Start a realtime service')
parser.add_argument('-s', '--service', help="Service name [websocket,updater]", required=True)
args = parser.parse_args()
print(args.service)
run(args.service)