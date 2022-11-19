from pathlib import Path
from typing import List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def strtobool(val: str) -> bool:
    """Convert a string representation of truth to True or False.

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.

    :param val: string representation of truth
    :raises ValueError: if val can't be converted to a truthish value
    :return: True or False
    """
    try:
        val = val.lower()
        if val in ("y", "yes", "t", "true", "on", "1"):
            return True
        elif val in ("n", "no", "f", "false", "off", "0"):
            return False
        else:
            raise ValueError("invalid truth value %r" % (val,))
    except Exception:
        raise ValueError("invalid truth value %r" % (val,))


def mount_session(
    allowed_methods: List[str] = ["GET"],
    total_retries: int = 5,
    backoff_factor: float = 0.5,
    raise_on_status: bool = True,
    user_agent: Optional[str] = None,
) -> requests.Session:
    """Create a requests.session() with optimised strategy for retrying and respecting errors

    :param allowed_methods: List of uppercased HTTP method verbs that we should retry on.
    :param total_retries: Total number of retries to allow.
    :param backoff_factor: A backoff factor to apply between attempts after the second try.
    :param raise_on_status: Whether we should raise an exception, or return a response, if status falls in status_forcelist range and retries have been exhausted.
    :param user_agent: The user agent to use for the session
    :return: A requests session with retry and error handling
    """
    retry_strategy = Retry(
        total=total_retries,
        respect_retry_after_header=True,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504, 520],
        allowed_methods=allowed_methods,
        raise_on_status=raise_on_status,
    )
    retry_strategy.DEFAULT_BACKOFF_MAX = 5  # type: ignore
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()

    if user_agent is not None:
        session.headers.update({"User-Agent": user_agent})

    session.mount(prefix="https://", adapter=adapter)
    session.mount(prefix="http://", adapter=adapter)

    return session


def get_first_filename_in_dir(dir_path: Path) -> str:
    """Get the first filename in a directory

    :param dir_path: The path to the directory
    :raises FileNotFoundError: if the directory is empty
    :return: The name of the first file in the directory
    """
    for file_path in dir_path.iterdir():
        if file_path.is_file():
            return file_path.name
    raise FileNotFoundError("No files found in directory")
