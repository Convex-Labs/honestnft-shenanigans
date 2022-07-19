import argparse
import base64
import concurrent.futures
import json
import os
from typing import Union


import pandas as pd
from web3.contract import Contract
from web3.exceptions import ContractLogicError

from honestnft_utils import chain
from honestnft_utils import config
from honestnft_utils import ipfs
from honestnft_utils import misc

"""
Metadata helper methods
"""


def fetch(token_id: int, metadata_uri: str, filename: str) -> None:
    try:
        # Try to get metadata file from server
        if metadata_uri.startswith("data:application/json;base64"):
            try:
                encoded_metadata = metadata_uri.split(",")[1]
                decoded_metadata = base64.b64decode(encoded_metadata).decode("utf-8")
                response_json = json.loads(decoded_metadata)
            except Exception as err:
                print(err)
                raise Exception(f"Failed to decode on-chain metadata: {metadata_uri}")
        else:
            _session = misc.mount_session()
            # Fetch metadata from server
            uri_response = _session.get(metadata_uri, timeout=3.05)
            try:
                response_json = uri_response.json()
            except Exception as err:
                print(err)
                raise Exception(
                    f"Failed to get metadata from server using {metadata_uri}. Got {uri_response}."
                )

        # Write raw metadata json file to disk
        with open(filename, "w") as destination_file:
            json.dump(response_json, destination_file)

    except Exception as err:
        print(
            f"Got below error when trying to get metadata for token id {token_id}.\n{err}"
        )


def fetch_all_metadata(
    token_ids: Union[list, range],
    collection: str,
    uri_func: str,
    contract: Contract,
    abi: list,
    uri_base: str,
    uri_suffix: str,
    blockchain: str,
    threads: int,
) -> list:

    # Create raw attribute folder for collection if it doesnt already exist
    folder = f"{config.ATTRIBUTES_FOLDER}/{collection}/"
    if not os.path.exists(folder):
        os.mkdir(folder)

    # Initiate list of dicts that will be converted to DataFrame
    dictionary_list = []
    file_suffix = ""
    bulk_ipfs_success = False
    uri = ""
    if uri_base is None:
        for token_id in [0, 1]:
            try:
                # Fetch the metadata url from the contract
                uri = chain.get_token_uri_from_contract(
                    contract, token_id, uri_func, abi
                )
                break
            except Exception as err:
                pass
        cid = ipfs.infer_cid_from_uri(uri)
        if cid is not None:
            uri_base = config.IPFS_GATEWAY + cid + "/"

    # First try to get all metadata files from ipfs in bulk
    if uri_base is not None and ipfs.is_valid_ipfs_uri(uri_base):
        folder_walk = os.walk(folder, topdown=True, onerror=None, followlinks=False)
        _files = next(folder_walk)[2]

        if len(_files) == 0:
            cid = ipfs.infer_cid_from_uri(uri_base)
            try:
                ipfs.fetch_ipfs_folder(
                    collection_name=collection,
                    cid=cid,  # type: ignore
                    parent_folder=config.ATTRIBUTES_FOLDER,
                    timeout=60,
                )
                folder_walk = os.walk(
                    folder, topdown=True, onerror=None, followlinks=False
                )
                _files = next(folder_walk)[2]
                first_file = _files[0]
                file_suffix = ipfs.get_file_suffix(first_file)
                bulk_ipfs_success = True
            except Exception:
                print("Falling back to individual file downloads...")
                file_suffix = ".json"
                pass
    else:
        file_suffix = ".json"

    if (
        bulk_ipfs_success is not True
        and uri_func is not None
        and contract is not None
        and abi is not None
    ):
        try:
            function_signature = chain.get_function_signature(uri_func, abi)
            # Fetch token URI from on-chain
            BATCH_SIZE = 50
            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
                for i in range(0, len(token_ids), BATCH_SIZE):
                    token_ids_batch = token_ids[i : i + BATCH_SIZE]
                    # Skip on-chain fetch if we already have the metadata
                    token_ids_batch = list(
                        filter(
                            lambda token_id: not os.path.exists(
                                f"{folder}/{token_id}.json"
                            ),
                            token_ids_batch,
                        )
                    )
                    for (
                        token_id,
                        metadata_uri,
                    ) in chain.get_token_uri_from_contract_batch(
                        contract,
                        token_ids_batch,
                        function_signature,
                        abi,
                        blockchain=blockchain,
                    ).items():
                        executor.submit(
                            fetch,
                            token_id,
                            metadata_uri,
                            filename="{folder}{token_id}{file_extension}".format(
                                folder=folder,
                                token_id=token_id,
                                file_extension=file_suffix,
                            ),
                        )
        except Exception as err:
            print(err)

    # Fetch metadata for all token ids
    for token_id in token_ids:
        # Initiate json result
        result_json = None

        # Check if metadata file already exists
        filename = "{folder}{token_id}{file_extension}".format(
            folder=folder, token_id=token_id, file_extension=file_suffix
        )
        if os.path.exists(filename):
            # Load existing file from disk
            with open(filename, "r") as f:
                result_json = json.load(f)

        else:

            # Get the metadata URI
            if uri_base is not None:
                # Build URI from base URI and URI suffix provided
                uri_base = ipfs.format_ipfs_uri(uri_base)
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
                metadata_uri = chain.get_token_uri_from_contract(
                    contract, token_id, uri_func, abi
                )

                if isinstance(metadata_uri, ContractLogicError):
                    print(f"{metadata_uri} {token_id}")
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
            elif "properties" in result_json:
                attribute_key = "properties"
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


"""
Main method
"""


def pull_metadata(args: argparse.Namespace) -> None:

    if args.contract is not None:
        # Get Ethereum contract object
        abi = chain.get_contract_abi(address=args.contract, blockchain=args.blockchain)
        abi, contract = chain.get_contract(
            address=args.contract, abi=abi, blockchain=args.blockchain
        )
    else:
        contract = None
        abi = None

    # Get the max supply of the contract
    if args.max_supply is None and contract is not None and abi is not None:
        # Supply function not provided so will infer max supply from the contract object
        supply_func = chain.get_contract_function(
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
        lower_id = chain.get_lower_token_id(
            contract=contract, uri_func=args.uri_func, abi=abi
        )
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
        name_func = chain.get_contract_function(
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
    token_ids = range(lower_id, upper_id + 1)

    records = fetch_all_metadata(
        token_ids=token_ids,
        collection=collection,
        uri_func=args.uri_func,
        contract=contract,  # type: ignore
        abi=abi,
        uri_base=args.uri_base,
        uri_suffix=args.uri_suffix,
        blockchain=args.blockchain,
        threads=args.threads,
    )

    # Generate traits DataFrame and save to disk as csv
    trait_db = pd.DataFrame.from_records(records)
    trait_db = trait_db.set_index("TOKEN_ID")
    print(trait_db.head())
    trait_db.to_csv(f"{config.ATTRIBUTES_FOLDER}/{collection}.csv")


def _cli_parser() -> argparse.ArgumentParser:
    """
    Create the command line argument parser
    """

    parser = argparse.ArgumentParser(description="CLI for pulling NFT metadata.")
    parser.add_argument(
        "-c",
        "--contract",
        type=str,
        default=None,
        help="Collection contract address (use if want to infer params from contract).",
    )
    parser.add_argument(
        "--uri_base",
        type=str,
        default=None,
        help="URI base. Not used if contract is provided. (use if want to pull direct from URL).",
    )
    parser.add_argument(
        "--uri_suffix",
        type=str,
        default=None,
        help="URI suffix. Not used if contract is provided. (default: No suffix).",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default=None,
        help="Collection name. (Required if pulling direct from URL. Otherwise will infer if not provided).",
    )
    parser.add_argument(
        "--supply_func",
        type=str,
        default="totalSupply",
        help='Total supply contract function. Not used if pulling direct from URL. (default: "totalSupply").',
    )
    parser.add_argument(
        "--name_func",
        type=str,
        default="name",
        help='Collection name contract function. Not used if pulling direct from URL. (default: "name").',
    )
    parser.add_argument(
        "--uri_func",
        type=str,
        default="tokenURI",
        help='URI contract function. Not used if pulling direct from URL. (default: "tokenURI").',
    )
    parser.add_argument(
        "--lower_id",
        type=int,
        default=None,
        help="Lower bound token id. (Required if pulling direct from URL. Otherwise will infer if not provided).",
    )
    parser.add_argument(
        "--upper_id",
        type=int,
        default=None,
        help="Upper bound token id. (Required if pulling direct from URL. Otherwise will infer if not provided).",
    )
    parser.add_argument(
        "--max_supply",
        type=int,
        default=None,
        help="Max token supply. (Required if pulling direct from URL. Otherwise will infer if not provided).",
    )
    parser.add_argument(
        "--ipfs_gateway",
        type=str,
        default=None,
        help=f"IPFS gateway. (default: {config.IPFS_GATEWAY}).",
    )
    parser.add_argument(
        "--web3_provider",
        type=str,
        default=None,
        help="Web3 Provider. (Recommended provider is alchemy.com. See Discord for additional details)",
    )
    parser.add_argument(
        "-b",
        "--blockchain",
        type=str,
        choices=[
            "arbitrum",
            "avalanche",
            "binance",
            "ethereum",
            "fantom",
            "optimism",
            "polygon",
        ],
        default="ethereum",
        help="Blockchain where the contract is located. (default: ethereum)",
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=None,
        help=f"Number of threads to use for downloading metadata. (default: {min(32, os.cpu_count() + 4)})",  # type: ignore
    )

    return parser


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

    ARGS = _cli_parser().parse_args()

    if ARGS.ipfs_gateway is not None:
        config.IPFS_GATEWAY = ARGS.ipfs_gateway
    if ARGS.blockchain == "arbitrum":
        if ARGS.web3_provider is not None:
            config.ARBITRUM_ENDPOINT = ARGS.web3_provider
    elif ARGS.blockchain == "avalanche":
        if ARGS.web3_provider is not None:
            config.AVALANCHE_ENDPOINT = ARGS.web3_provider
    elif ARGS.blockchain == "binance":
        if ARGS.web3_provider is not None:
            config.BINANCE_ENDPOINT = ARGS.web3_provider
    elif ARGS.blockchain == "fantom":
        if ARGS.web3_provider is not None:
            config.FANTOM_ENDPOINT = ARGS.web3_provider
    elif ARGS.blockchain == "optimism":
        if ARGS.web3_provider is not None:
            config.OPTIMISM_ENDPOINT = ARGS.web3_provider
    elif ARGS.blockchain == "polygon":
        if ARGS.web3_provider is not None:
            config.POLYGON_ENDPOINT = ARGS.web3_provider
    else:
        if ARGS.web3_provider is not None:
            config.ENDPOINT = ARGS.web3_provider

    pull_metadata(ARGS)
