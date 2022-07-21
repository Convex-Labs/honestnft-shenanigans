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


class BlockStatementPrinting:
    """
    Used to block printing to the console by wrapping the statements in a with statement.
    usage:
    with.BlockStatementPrinting():
        ...
    """

    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


TESTS_ROOT_DIR = Path(config.ROOT_DIR).joinpath("tests")
