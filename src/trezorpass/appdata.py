import logging
import shutil
from pathlib import Path

import appdirs

APP_DIR = appdirs.user_data_dir('trezor-pass')


def init_data():
    try:
        Path(APP_DIR).mkdir(parents=True, exist_ok=True)
    except:
        logging.exception("Unable to initialize application data directory")


def clear_data():
    """Clears stored application data"""
    shutil.rmtree(APP_DIR, ignore_errors=True)


init_data()
