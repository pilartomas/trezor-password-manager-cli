import asyncio
import logging

from trezorlib.exceptions import Cancelled, PinException

from .store.sources import Source, DropboxSource, FileSource
from .utils import welcome, goodbye
from .appdata import clear_data
from .helpers import get_client, load_store, select_entry, manage_entry


async def cli(store_manager: Source):
    welcome()
    client = None
    try:
        client = await get_client()
        store = await load_store(client, store_manager)
        while True:
            try:
                entry = await select_entry(store.entries)
                await manage_entry(entry, client)
            except Cancelled:
                print("Trezor operation has been cancelled")
            except PinException:
                print("Invalid pin")
    except KeyboardInterrupt:
        pass
    except Exception:
        logging.exception("CLI failed")
    finally:
        if client:
            try:
                client.end_session()
            except:
                pass
        goodbye()


def run():
    import argparse
    parser = argparse.ArgumentParser(description='Command line interface for interaction with Trezor password store.')
    parser.add_argument("--clear", action='store_true', help="clears saved application data")
    parser.add_argument("--store", type=str, help="specifies the store file to be used instead of remote store")
    parser.add_argument("--debug", action='store_true', help="print debug logs")
    args = parser.parse_args()

    if not args.debug:
        logging.disable()

    if args.clear:
        clear_data()
    elif args.store:
        asyncio.run(cli(FileSource(args.store)))
    else:
        asyncio.run(cli(DropboxSource()), debug=True if args.debug else False)


if __name__ == "__main__":
    run()
