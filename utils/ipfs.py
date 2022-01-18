import os
import re
import warnings

import ipfshttpclient

import utils.config as config


def get_file_suffix(filename, token_id="\\d+"):
    """
    Given a filename and an optional token_id, this function returns the file suffix.
    If the file has no extension, an empty string is returned.

    :param filename
    :type filename: str
    :param token_id
    :type token_id: str | int | None
    :return: file_suffix
    :rtype: str
    """
    regex = rf"^{token_id}(\.(?P<extension>\w+))?$"
    matches = re.search(regex, filename)
    if matches and matches.group("extension"):
        return matches.group(1)
    return ""


def infer_cid_from_uri(uri):
    """
    Given a URI, this function returns the CID.
    Returns None if the CID is not found.

    :param uri
    :type uri: str
    :return: cid
    :rtype: str | None
    """
    cid_pattern = r"Qm[a-zA-Z0-9-_]+"
    matches = re.search(cid_pattern, uri)
    if matches:
        return matches.group(0)
    return None


def is_valid_ipfs_uri(uri):
    """
    Given a URI, this functions checks if it's a valid IPFS URI.

    :param uri
    :type uri: str
    :rtype: bool
    """
    if uri.find("ipfs") != -1 and infer_cid_from_uri(uri):
        return True
    return False


def fetch_ipfs_folder(collection_name, cid, parent_folder, timeout=60):
    # print(os.getcwd())
    # print(f"{os.getcwd()}/{parent_folder}/")
    """
    Given a collection name, a cid and an optional timeout, this function downloads the entire metadata folder from IPFS.

    :param parent_folder: The parent folder where the collection should be saved.
    :type parent_folder:  str
    :param collection_name The collection name to be used as the folder name
    :type collection_name: str
    :param cid: The IPFS CID of folder to download
    :type cid: str
    :param timeout: Connection timeout (in seconds) when connecting to the API daemon
    :type timeout: int | None
    """
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
            client.get(f"/ipfs/{cid}", target=f"{os.getcwd()}/{parent_folder}/")
            print("Successfully downloaded metadata folder from IPFS")
            os.rename(
                f"./{parent_folder}/{cid}",
                f"./{parent_folder}/{collection_name}",
            )
            client.close()
            break
        except Exception:
            if gateway < len(gateways) - 1:
                print(
                    "Failed to download metadata folder from IPFS. Trying next gateway..."
                )
            else:
                print("Failed to download metadata folder from IPFS.")
                if os.path.exists(f"./{parent_folder}/{cid}"):
                    os.rename(
                        f"./{parent_folder}/{cid}",
                        f"./{parent_folder}/{collection_name}",
                    )
            pass


def format_ipfs_uri(uri):
    # Reformat IPFS gateway
    ipfs_1 = "ipfs://"
    ipfs_2 = "https://ipfs.io/ipfs/"
    ipfs_3 = "https://gateway.pinata.cloud/ipfs/"
    ipfs_hash_identifier = "Qm"

    if config.IPFS_GATEWAY == "":
        if uri.startswith(ipfs_1):
            uri = ipfs_2 + uri[len(ipfs_1) :]
    else:
        if uri.startswith(ipfs_1):
            uri = config.IPFS_GATEWAY + uri[len(ipfs_1) :]
        elif uri.startswith(ipfs_2):
            uri = config.IPFS_GATEWAY + uri[len(ipfs_2) :]
        elif uri.startswith(ipfs_3):
            uri = config.IPFS_GATEWAY + uri[len(ipfs_3) :]
        elif "pinata" in uri:
            starting_index_of_hash = uri.find(ipfs_hash_identifier)
            uri = config.IPFS_GATEWAY + uri[starting_index_of_hash:]

    return uri
