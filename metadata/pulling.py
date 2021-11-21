import os
import pandas as pd
import requests
import time
import json
import argparse
import sys
import base64
from web3 import Web3
from web3.exceptions import ContractLogicError
from web3_multicall import Multicall
import ipfshttpclient
import re

ABI_ENDPOINT = "https://api.etherscan.io/api?module=contract&action=getabi&address="
ENDPOINT = ""
ATTRIBUTES_FOLDER = "raw_attributes"
IMPLEMENTATION_SLOT = (
    "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
)
IPFS_GATEWAY = ""


"""
Smart contract helper methods
"""


def get_contract_abi(address):
    # Get contract ABI
    abi_url = f"{ABI_ENDPOINT}{address}"
    response = requests.get(abi_url)
    try:
        abi = json.loads(response.json()["result"])
        return abi
    except Exception as err:
        print(f'Failed to get contract ABI from Etherscan: {err}')
        print(f'Falling back to direct ABI checking')
        if ENDPOINT != "":
            # We can check the ABI of non-verified Etherscan contracts
            # if they support ERC165 (which most of them do)
            erc165_abi = [
                {
                    "inputs": [{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],
                    "name": "supportsInterface",
                    "outputs": [{"internalType":"bool","name":"","type":"bool"}],
                    "stateMutability": "view",
                    "type": "function"
                }
            ]

            w3 = Web3(Web3.HTTPProvider(ENDPOINT))
            contract = w3.eth.contract(Web3.toChecksumAddress(address), abi=erc165_abi)

            # Array of contract methods that were verified via ERC165
            contract_abi = []

            # List of common ERC721 methods to check
            common_abis = {}
            # ERC721 metadata interface id
            common_abis["0x5b5e139f"] = [
                {
                    "inputs": [],
                    "name": "name",
                    "outputs": [{"internalType":"string","name":"","type":"string"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType":"uint256","name":"tokenId","type":"uint256"}],
                    "name": "tokenURI",
                    "outputs": [{"internalType":"string","name":"","type":"string"}],
                    "stateMutability": "view",
                    "type": "function"
                }
            ]
            # ERC721 enumerable interface id
            common_abis["0x780e9d63"] = [{
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"internalType":"uint256","name":"","type":"uint256"}],
                "stateMutability": "view",
                "type": "function"
            }]

            for selector, abi in common_abis.items():
                try:
                    supports_abi = contract.functions.supportsInterface(selector).call()
                    if supports_abi:
                        contract_abi += abi
                except Exception as err:
                    print(f'Could not check selector {selector}')

            if len(contract_abi) > 0:
                return contract_abi

        raise Exception(f'Failed to get contract ABI.\nURL: {abi_url}\nResponse: {response.json()}')


def get_contract(address, abi):
    # Connect to web3
    if ENDPOINT == "":
        print("\nMust enter a Web3 provider. Open this file and set the ENDPOINT and IPFS_GATEWAY constants. See: https://ipfs.github.io/public-gateway-checker/\n")
        print("Optional: Use -web3_provider as a command line argument")
        sys.exit()

    w3 = Web3(Web3.HTTPProvider(ENDPOINT))

    # Check if abi contains the tokenURI function
    contract_functions = [func["name"] for func in abi if "name" in func]

    if "implementation" in contract_functions:
        # Handle case where the contract is a proxy contract
        # Fetch address for the implementation contract
        impl_contract = w3.toHex(w3.eth.get_storage_at(address, IMPLEMENTATION_SLOT))

        # Strip the padded zeros from the implementation contract address
        impl_address = "0x" + impl_contract[-40:]
        print(
            f"Contract is a proxy contract. Using implementation address: {impl_address}"
        )

        # Sleep to respect etherscan API limit
        time.sleep(5)

        # Get the implementation contract ABI
        impl_abi = get_contract_abi(address=impl_address)

        # Return the implementation contract object instead
        return get_contract(impl_contract, abi=impl_abi)

    # Get contract checksum address
    contract_checksum = Web3.toChecksumAddress(address)

    # Build the Ethereum contract object
    collection_contract = w3.eth.contract(contract_checksum, abi=abi)

    # Return the contract ABI and Ethereum contract object
    return abi, collection_contract


def get_contract_function(contract, func_name, abi):
    if func_name in dir(contract.functions):
        # The function name given is a valid function in the ABI, so return that function
        return getattr(contract.functions, func_name)
    else:
        # The function name provided is not in the contract ABI, so throw an error
        func_names = [f["name"] for f in abi if "name" in f]
        raise ValueError(
            f"{func_name} is not in the contract ABI. Inspect the following function names "
            f"for candidates and pass to the command line arguments: {func_names}"
        )


def format_ipfs_uri(uri):
    # Reformat IPFS gateway
    ipfs_1 = "ipfs://"
    ipfs_2 = "https://ipfs.io/ipfs/"
    ipfs_3 = "https://gateway.pinata.cloud/ipfs/"
    ipfs_hash_identifier = "Qm"

    if IPFS_GATEWAY == "":
        if uri.startswith(ipfs_1):
            uri = ipfs_2 + uri[len(ipfs_1) :]
    else:
        if uri.startswith(ipfs_1):
            uri = IPFS_GATEWAY + uri[len(ipfs_1) :]
        elif uri.startswith(ipfs_2):
            uri = IPFS_GATEWAY + uri[len(ipfs_2) :]
        elif uri.startswith(ipfs_3):
            uri = IPFS_GATEWAY + uri[len(ipfs_3) :]
        elif "pinata" in uri:
            starting_index_of_hash = uri.find(ipfs_hash_identifier)
            uri = IPFS_GATEWAY + uri[starting_index_of_hash:]

    return uri


def get_contract_uri(contract, token_id, uri_func, abi):
    # Fetch URI from contract
    uri_contract_func = get_contract_function(contract, uri_func, abi)

    try:
        uri = uri_contract_func(token_id).call()
        uri = format_ipfs_uri(uri)
        return uri
    except ContractLogicError as err:
        raise Exception(err)


def get_contract_uri_batch(contract, token_ids, uri_func, abi):
    if len(token_ids) > 0:
        if ENDPOINT == "":
            print(
                "You must enter a Web3 provider. This is currently not a command line option. You must open this file and assign a valid provider to the ENDPOINT and IPFS_GATEWAY constants. See: https://ipfs.github.io/public-gateway-checker/"
            )
            sys.exit()

        def get_func(token_id):
            uri_contract_func = get_contract_function(contract, uri_func, abi)
            return uri_contract_func(token_id)

        w3 = Web3(Web3.HTTPProvider(ENDPOINT))
        multicall = Multicall(w3.eth)
        multicall_result = multicall.aggregate(list(map(get_func, token_ids)))
        return {
            x["inputs"][0]["value"]: format_ipfs_uri(x["results"][0])
            for x in multicall_result.json["results"]
        }
    else:
        return {}


def get_lower_id(contract, uri_func, abi):
    # Initiate parameters
    lower_token_id = None

    # Search over possible lower bound ids
    for token_id in [0, 1]:
        try:
            # Fetch the metadata url from the contract
            uri = get_contract_uri(contract, token_id, uri_func, abi)
            print(f"Metadata for lower bound token id is at: {uri}")
            lower_token_id = token_id
            break
        except Exception as err:
            # Catch exception where token URI function fails because the token id is invalid
            print(err)
            pass

    # Raise exception if method fails to find the metadata url
    if lower_token_id is None:
        raise Exception("Unable to get the metadata url.")

    # Return lower id
    return lower_token_id


"""
Metadata helper methods
"""


def get_metadata(uri, destination):
    if uri.startswith("data:application/json;base64"):
        try:
            encoded_metadata = uri.split(",")[1]
            decoded_metadata = base64.b64decode(encoded_metadata).decode("utf-8")
            response_json = json.loads(decoded_metadata)
        except Exception as err:
            print(err)
            raise Exception(f'Failed to decode on-chain metadata: {uri}')
    else:
        # Fetch metadata from server
        uri_response = requests.request("GET", uri, timeout=10)
        try:
            response_json = uri_response.json()
        except Exception as err:
            print(err)
            raise Exception(f'Failed to get metadata from server using {uri}. Got {uri_response}.')


    # Write raw metadata json file to disk
    with open(destination, "w") as destination_file:
        json.dump(response_json, destination_file)

    # Return raw metadata json file
    return response_json


def fetch_all_metadata(
    token_ids, collection, sleep, uri_func, contract, abi, uri_base, uri_suffix
):

    # Create raw attribute folder for collection if it doesnt already exist
    folder = f'{ATTRIBUTES_FOLDER}/{collection}/'
    if not os.path.exists(folder):
        os.mkdir(folder)

    # Initiate list of dicts that will be converted to DataFrame
    dictionary_list = []
    file_suffix = ""
    bulk_ipfs_success = False

    # First try to get all metadata files from ipfs in bulk
    if uri_base is not None and uri_base.find("ipfs") != -1:
        folder_walk = os.walk(folder, topdown=True,
                              onerror=None, followlinks=False)
        _files = next(folder_walk)[2]

        if len(_files) == 0:
            cid = infer_cid_from_uri(uri_base)
            fetch_ipfs_folder(collection_name=collection,
                              cid=cid)
            folder_walk = os.walk(folder, topdown=True,
                                  onerror=None, followlinks=False)
            _files = next(folder_walk)[2]

        first_file = _files[0]
        file_suffix = get_file_suffix(first_file)
        bulk_ipfs_success = True

    else:
        file_suffix = ".json"

    def fetch(token_id, metadata_uri, filename):
        # Set parameters for retrying to pull from server
        max_retries = 5
        retries = 0

        # Load non- file from server
        while retries < max_retries:
            try:
                # Try to get metadata file from server
                get_metadata(uri=metadata_uri, destination=filename)
                time.sleep(sleep)
                break
            except Exception as err:
                # Handle throttling, pause and then try again up to max_retries number of times
                print(
                    f"Got below error when trying to get metadata for token id {token_id}. "
                    f"Will sleep and retry..."
                )
                print(err)
                retries += 1

                # Sleep for successively longer periods of time before restarting
                time.sleep(sleep * retries)

                # Throw an error when max retries is exceeded
                if retries >= max_retries:
                    # raise Exception('Max retries exceeded. Shutting down.')
                    print("Max retries exceeded. Moving to next...")
                    break
        return True

    if (
        bulk_ipfs_success is not True
        and uri_func is not None
        and contract is not None
        and abi is not None
    ):
        # Fetch token URI from on-chain
        BATCH_SIZE = 50
        for i in range(0, len(token_ids), BATCH_SIZE):
            print(f"Fetching [{i}, {i + BATCH_SIZE}]")
            token_ids_batch = token_ids[i: i + BATCH_SIZE]
            # Skip on-chain fetch if we already have the metadata
            token_ids_batch = list(
                filter(
                    lambda token_id: not os.path.exists(f"{folder}/{token_id}.json"),
                    token_ids_batch,
                )
            )
            for token_id, metadata_uri in get_contract_uri_batch(
                contract, token_ids_batch, uri_func, abi
            ).items():
                fetch(
                    token_id,
                    metadata_uri,
                    filename="{folder}{token_id}{file_extension}".format(
                        folder=folder, token_id=token_id, file_extension=file_suffix
                    ),
                )

    # Fetch metadata for all token ids
    for token_id in token_ids:
        # Initiate json result
        result_json = None

        # Check if metadata file already exists
        filename = "{folder}{token_id}{file_extension}".format(folder=folder,
                                                               token_id=token_id,
                                                               file_extension=file_suffix)
        if os.path.exists(filename):
            # Load existing file from disk
            with open(filename, "r") as f:
                result_json = json.load(f)

        else:

            # Get the metadata URI
            if uri_base is not None:
                # Build URI from base URI and URI suffix provided
                uri_base = format_ipfs_uri(uri_base)
                if uri_base.endswith("/"):
                    uri_base = uri_base[:-1]
                if uri_base.endswith("="):
                    metadata_uri = f"{uri_base}{token_id}"
                else:
                    metadata_uri = f"{uri_base}/{token_id}"
                if uri_suffix is not None:
                    metadata_uri += uri_suffix
            elif uri_func is not None and contract is not None and abi is not None:
                # Fetch URI for the given token id from the contract
                metadata_uri = get_contract_uri(contract, token_id, uri_func, abi)

                if isinstance(metadata_uri, ContractLogicError):
                    print(f'{metadata_uri} {token_id}')
                    continue

            else:
                raise ValueError(
                    "Failed to get metadata URI. Must either provide a uri_base or contract"
                )

            if token_id % 50 == 0:
                print(token_id)
            fetch(token_id, metadata_uri, filename)

        if result_json is not None:

            # TODO: What are other variations of name?
            # Add token name and token URI traits to the trait dictionary
            traits = dict()
            if "name" in result_json:
                traits["TOKEN_NAME"] = result_json["name"]
            else:
                traits["TOKEN_NAME"] = f"UNKNOWN"
            traits["TOKEN_ID"] = token_id

            # Find the attribute key from the server response
            if "attributes" in result_json:
                attribute_key = "attributes"
            elif "traits" in result_json:
                attribute_key = "traits"
            else:
                raise ValueError(
                    f"Failed to find the attribute key in the token {token_id} "
                    f'metadata result. Tried "attributes" and "traits".\nAvailable '
                    f"keys: {result_json.keys()}"
                )

            # Add traits from the server response JSON to the traits dictionary
            try:
                for attribute in result_json[attribute_key]:
                    if "value" in attribute and "trait_type" in attribute:
                        traits[attribute["trait_type"]] = attribute["value"]
                    elif "value" not in attribute and isinstance(attribute, dict):
                        if len(attribute.keys()) == 1:
                            traits[attribute["trait_type"]] = "None"
                    elif isinstance(attribute, str):
                        traits[attribute] = result_json[attribute_key][attribute]
                dictionary_list.append(traits)
            # Handle exceptions result from URI does not contain attributes
            except Exception as err:
                print(err)
                print(
                    f"Failed to get metadata for id {token_id}. Url response was {result_json}."
                )

    return dictionary_list


def fetch_ipfs_folder(collection_name, cid, timeout=3600):
    """
    Given a collection name, a cid and an optional timeout, this function downloads the entire metadata folder from IPFS.

    :param collection_name
    :type collection_name: str
    :param cid:
    :type cid: str
    :param timeout:
    :type timeout: int | None
    """
    folder = f'{ATTRIBUTES_FOLDER}/{collection_name}/'
    if not os.path.exists(folder):
        os.mkdir(folder)
    infura = "/dns/infura-ipfs.io/tcp/5001/https"
    ipfs_io = "/dns/ipfs.io/tcp/443/https"
    ipfs_gateway_io = "/dns/gateway.ipfs.io/tcp/443/https"
    client = ipfshttpclient.connect(addr=ipfs_gateway_io, timeout=timeout)
    client.get(f"/ipfs/{cid}/", target="./raw_attributes/")
    os.rename(
        f"./raw_attributes/{cid}", f"./raw_attributes/{collection_name}")


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


"""
Main method
"""


def pull_metadata(args):

    if args.contract is not None:
        # Get Ethereum contract object
        abi = get_contract_abi(address=args.contract)
        abi, contract = get_contract(address=args.contract, abi=abi)
    else:
        contract = None
        abi = None

    # Get the max supply of the contract
    if args.max_supply is None and contract is not None and abi is not None:
        # Supply function not provided so will infer max supply from the contract object
        supply_func = get_contract_function(
            contract=contract, func_name=args.supply_func, abi=abi
        )
        max_supply = supply_func().call()
    elif args.max_supply is not None:
        # Setting max supply as provided
        max_supply = args.max_supply
    else:
        raise ValueError(
            "Failed to get max supply. Must either provide contract or max_supply."
        )

    # Get the lower bound token id of the contract
    if args.lower_id is None and contract is not None and abi is not None:
        # Lower id not provided so will infer it from the contract object
        lower_id = get_lower_id(contract=contract, uri_func=args.uri_func, abi=abi)
    elif args.lower_id is not None:
        # Setting lower id as provided
        lower_id = args.lower_id
    else:
        raise ValueError(
            "Failed to get lower id. Must either provide contract or lower_id."
        )

    # Get the upper bound token id of the contract
    if args.upper_id is None and contract is not None and abi is not None:
        # upper id not provided so will infer it from the contract object
        upper_id = max_supply + lower_id - 1
    elif args.upper_id is not None:
        # Setting upper id as provided
        upper_id = args.upper_id
    else:
        upper_id = max_supply

    # Get collection name
    if args.collection is None and contract is not None and abi is not None:
        name_func = get_contract_function(
            contract=contract, func_name=args.name_func, abi=abi
        )
        collection = name_func().call()
    elif args.collection is not None:
        collection = args.collection
    else:
        raise ValueError(
            "Failed to get collection. Must either provide contract or collection."
        )
    collection = collection.replace(" ", "_")

    # Print configuration
    print(f"Fetching data for {collection}")
    print(f"Lower ID: {lower_id}")
    print(f"Upper ID: {upper_id}")
    print(f"Max supply: {max_supply}")

    # Fetch all attribute records from the remote server
    token_ids = range(lower_id, upper_id)  # for 0-indexed collections

    records = fetch_all_metadata(
        token_ids=token_ids,
        collection=collection,
        uri_func=args.uri_func,
        contract=contract,
        abi=abi,
        sleep=args.sleep,
        uri_base=args.uri_base,
        uri_suffix=args.uri_suffix,
    )

    # Generate traits DataFrame and save to disk as csv
    trait_db = pd.DataFrame.from_records(records)
    trait_db = trait_db.set_index("TOKEN_ID")
    print(trait_db.head())
    trait_db.to_csv(f"{ATTRIBUTES_FOLDER}/{collection}.csv")


if __name__ == "__main__":

    """
    There are some cases we have found that are not covered by this script:
    https://etherscan.io/token/0xff9c1b15b16263c61d017ee9f65c50e4ae0113d7
    https://etherscan.io/address/0x743f80dc76f862a27598140196cc610006b2be68
    https://etherscan.io/address/0x8197c9d748287dc1ce7b35ad8dfff4a79a54a1c4
    """

    """
    Retrieve NFT metadata from remote server. A couple configurations are available.

    1) Provide a contract address and infer all underlying parameters
    python3 pulling.py -contract 0x09eqhc0iqy80eychq8hn8dhqwc

    2) Provide a URI base, collection name, lower_id, and max_supply
    python3 pulling.py -uri_base https://punks.com/api/ -collection punks -lower_id 0 -max_supply 10000

    When retrieving metadata by inferring the URI directly from the contract function,  we assume:
    1) Contract ABI is posted publicly on etherscan.
    2) Contract address points to either an NFT contract or an associated proxy contract that
       has an NFT contract as an implementation contract. Note that get_contract is called
       recursively if the provided contract address yields and ABI that contains a function 
       called 'implementation'
    """

    # Parse command line arguments
    ARG_PARSER = argparse.ArgumentParser(description='CLI for pulling NFT metadata.')
    ARG_PARSER.add_argument('-contract', type=str, default=None, help='Collection contract id (use if want to infer params from contract).')
    ARG_PARSER.add_argument('-uri_base', type=str, default=None, help='URI base. Not used if contract is provided. (use if want to pull direct from URL).')
    ARG_PARSER.add_argument('-uri_suffix', type=str, default=None, help='URI suffix. Not used if contract is provided. (default: No suffix).')
    ARG_PARSER.add_argument('-collection', type=str, default=None, help='Collection name. (Required if pulling direct from URL. Otherwise will infer if not provided).')
    ARG_PARSER.add_argument('-supply_func', type=str, default='totalSupply', help='Total supply contract function. Not used if pulling direct from URL. (default: "totalSupply").')
    ARG_PARSER.add_argument('-name_func', type=str, default='name', help='Collection name contract function. Not used if pulling direct from URL. (default: "name").')
    ARG_PARSER.add_argument('-uri_func', type=str, default='tokenURI', help='URI contract function. Not used if pulling direct from URL. (default: "tokenURI").')
    ARG_PARSER.add_argument('-lower_id', type=int, default=None, help='Lower bound token id. (Required if pulling direct from URL. Otherwise will infer if not provided).')
    ARG_PARSER.add_argument('-upper_id', type=int, default=None, help='Upper bound token id. (Required if pulling direct from URL. Otherwise will infer if not provided).')
    ARG_PARSER.add_argument('-max_supply', type=int, default=None, help='Max token supply. (Required if pulling direct from URL. Otherwise will infer if not provided).')
    ARG_PARSER.add_argument('-ipfs_gateway', type=str, default=None, help=f'IPFS gateway. (default: {IPFS_GATEWAY}).')
    ARG_PARSER.add_argument('-sleep', type=float, default=0.05, help='Sleep time between metadata pulls. (default: 0.05).')
    ARG_PARSER.add_argument('-web3_provider', type=str, default=None, help='Web3 Provider. (Recommended provider is alchemy.com. See Discord for additional details)')
    ARGS = ARG_PARSER.parse_args()

    if ARGS.ipfs_gateway is not None:
        IPFS_GATEWAY = ARGS.ipfs_gateway
    if ARGS.web3_provider is not None:
        ENDPOINT = ARGS.web3_provider

    pull_metadata(ARGS)
