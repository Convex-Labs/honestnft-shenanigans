import re
import warnings
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse

import ipfshttpclient
from is_ipfs import Validator

from honestnft_utils import config


def get_file_suffix(filename: str, token_id: Union[int, str] = "\\d+") -> str:
    """
    Given a filename and an optional token_id, this function returns the file suffix.
    If the file has no extension, an empty string is returned.

    :return: file_suffix
    """
    token_id_pattern = rf"^{token_id}"
    matches = re.search(token_id_pattern, filename)
    if matches:
        regex = rf"^{token_id}(\.(?P<extension>\w+))?$"
        matches = re.search(regex, filename)
        if matches and matches.group("extension"):
            return matches.group(1)
        return ""
    else:
        raise ValueError("Provided token_id not found in filename")


def is_valid_cid(cid: str) -> bool:
    """
    Given a CID, this function checks if it's a valid CID.
    """
    return Validator(cid)._is_cid()


def infer_cid_from_uri(URI: str) -> Optional[str]:
    """
    Given a URI, this function returns the CID.
    Returns None if the CID is not found.

    :return: cid
    """
    cid_v0_pattern = r"Qm[a-zA-Z0-9-_]+"
    # first check if we can extract a CID v0
    try:
        matches = re.search(cid_v0_pattern, URI)
        if matches:
            if is_valid_cid(matches.group(0)):
                return matches.group(0)
    except TypeError as e:
        raise TypeError(e)

    # if not, try to extract a CID v1
    parse_result = urlparse(URI)
    if parse_result.scheme == "ipfs":
        if is_valid_cid(parse_result.netloc):
            return parse_result.netloc

    # check for valid CID in path
    fragments = parse_result.path.replace("/", ";").replace(".", ";").split(";")
    for fragment in fragments:
        if is_valid_cid(fragment):
            return fragment

    # check for valid CID in netloc
    fragments = parse_result.netloc.split(".")
    for fragment in fragments:
        if is_valid_cid(fragment):
            return fragment

    return None


def is_valid_ipfs_uri(uri: str) -> bool:
    """
    Given a URI, this functions checks if it's a valid IPFS URI.
    """
    return Validator(uri).is_ipfs()


def fetch_ipfs_folder(
    collection_name: str, cid: str, parent_folder: str, timeout: Optional[int] = 60
) -> None:
    """
    Given a collection name, a cid and an optional timeout, this function downloads the entire metadata folder from IPFS.

    :param collection_name: The collection name to be used as the folder name
    :type collection_name: str
    :param cid: The IPFS CID of folder to download
    :type cid: str
    :param parent_folder: The parent folder where the collection should be saved
    :type parent_folder: str
    :param timeout: Connection timeout (in seconds) when connecting to the API daemon
    :type timeout: int
    :rtype: None
    """
    parent_path = Path(parent_folder)
    cid_path = parent_path.joinpath(cid)
    collection_path = parent_path.joinpath(collection_name)

    infura = "/dns/infura-ipfs.io/tcp/5001/https"
    ipfs_io = "/dns/ipfs.io/tcp/443/https"
    ipfs_gateway_io = "/dns/gateway.ipfs.io/tcp/443/https"
    dweb_link = "/dns/dweb.link/tcp/443/https"
    pinata = "/dns/gateway.pinata.cloud/tcp/443/https"
    warnings.filterwarnings(
        "ignore", category=ipfshttpclient.exceptions.VersionMismatch
    )
    gateways = [pinata, ipfs_gateway_io, infura, dweb_link, ipfs_io]
    print("Attempting to download metadata folder from IPFS...\nPlease wait...")

    for gateway in range(len(gateways)):
        try:
            client = ipfshttpclient.connect(addr=gateways[gateway], timeout=timeout)
            client.get(f"/ipfs/{cid}", target=parent_path)
            print("Successfully downloaded metadata folder from IPFS")
            cid_path.rename(collection_path)
            client.close()
            break
        except Exception:
            if gateway < len(gateways) - 1:
                print(
                    "Failed to download metadata folder from IPFS. Trying next gateway..."
                )
            else:
                if Path.exists(cid_path):
                    cid_path.rename(collection_path)
                raise Exception("Failed to download metadata folder from IPFS.")


def format_ipfs_uri(uri: str) -> str:
    """
    Given a IPFS URI, this function formats it with the user prefered gateway.

    :param uri: The IPFS URI to be formatted
    :return: The formatted IPFS URI
    """
    if type(uri) != str:
        raise TypeError("Provided URI is not a string")
    if config.IPFS_GATEWAY is None:
        gateway = "https://ipfs.io/ipfs/"
    else:
        gateway = config.IPFS_GATEWAY

    cid = infer_cid_from_uri(uri)
    if cid:
        if (
            Validator(uri)._is_ipfs_subdomain_url()
            or Validator(uri)._is_native_ipfs_url()
        ):
            scheme, netloc, path, params, query, fragment = urlparse(uri)
            new_uri = urlparse(gateway + cid + path)
            return new_uri._replace(
                params=params, query=query, fragment=fragment
            ).geturl()

        elif Validator(uri)._is_ipfs_path_url() or Validator(uri)._is_ipfs_path():
            url_parse_result = urlparse(uri)
            return url_parse_result._replace(
                scheme="https", netloc=urlparse(gateway).netloc
            ).geturl()
    raise ValueError("No CID found in URI")
