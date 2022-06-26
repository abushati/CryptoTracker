from realtime_updater.coin_updater import CoinHistoryUpdater
from realtime_updater.websocket_reader import RealtimeFeedReader
from realtime_updater.api_updater import ApiUpdater


def run(service_name):

    service = None
    if service_name == 'updater':
        service = CoinHistoryUpdater()
    elif service_name == 'websocket':
        service = RealtimeFeedReader()
    elif service_name == 'apiupdater':
        service = ApiUpdater()


    print(service)
    if service:
        service.run()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Start a realtime service')
    parser.add_argument('-s', '--service', help="Service name [websocket,updater]", required=True)
    args = parser.parse_args()
    print(args.service)
    run(args.service)