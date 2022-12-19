import asyncio
import logging

from trezorlib.exceptions import PinException

from trezorpass.store import StoreLoadError, StoreDecryptError, StoreDecodeError, get_store_manager
from trezorpass.store.sources import Source, DropboxSource, FileSource
from trezorpass.utils import prompt_print, welcome, goodbye
from trezorpass.appdata import clear_data
from trezorpass.helpers import get_client, select_entry, manage_entry


async def cli(store_source: Source):
    welcome()
    try:
        with await get_client() as client:
            async with get_store_manager(client, store_source) as store:
                while True:
                    entry = await select_entry(store.entries)
                    await manage_entry(entry, client)
    except KeyboardInterrupt:
        pass
    except asyncio.CancelledError:
        pass
    except PinException:
        prompt_print("Trezor pin was not valid")
    except (StoreLoadError, StoreDecryptError, StoreDecodeError):
        prompt_print("Failed to load the password store")
    except BaseException as e:
        logging.exception("CLI failed", exc_info=e)
    finally:
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
