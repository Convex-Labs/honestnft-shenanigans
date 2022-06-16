import os
import sys

from pathlib import Path

from honestnft_utils import config


def blockPrinting(func):
    """
    Decorator used to block function printing to the console
    """

    def func_wrapper(*args, **kwargs):
        with open(os.devnull, "w") as devnull:
            old_stdout = sys.stdout
            sys.stdout = devnull
            func(*args, **kwargs)
            sys.stdout = old_stdout

    return func_wrapper


TESTS_ROOT_DIR = Path(config.ROOT_DIR).joinpath("tests")
