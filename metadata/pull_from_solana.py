import argparse
import concurrent.futures
import json
import os
import re
from typing import Dict, List, Optional, Tuple, Union
from urllib.error import HTTPError

import pandas as pd
import requests

from honestnft_utils import config, misc


def save_metadata(
    raw_metadata: dict, token_id: Union[int, str], collection: str
) -> None:
    """Transform and save metadata as json to disk.

    We transform the metadata so it conforms to the ERC-721 standard.
    This makes the files compatible with our analysis tools.

    :param raw_metadata: The raw metadata as a dict
    :param token_id: The token_id of the NFT
    :param collection: The collection name
    """

    metadata_dict = {
        "name": raw_metadata["name"],
        "description": raw_metadata["description"],
        "tokenId": token_id if token_id else None,
        "image": raw_metadata["image"],
        "external_url": raw_metadata["external_url"],
    }
    attributes = []
    for attr in raw_metadata["attributes"]:
        if (attr["trait_type"] == "sequence") and (token_id is None):
            metadata_dict["tokenId"] = attr["value"]
        else:
            attributes.append(
                {"trait_type": attr["trait_type"], "value": attr["value"]}
            )
    metadata_dict["attributes"] = attributes

    filename = f"{config.ATTRIBUTES_FOLDER}/{collection}/{token_id}.json"
    with open(filename, "w") as destination_file:
        json.dump(metadata_dict, destination_file)


def fetch_metadata_uris(contract: str) -> List[Dict[str, str]]:
    """Fetch the metadata uris for a given contract from theindex.io.

    :param contract: The NFT contract address
    :raises Exception: If the index.io API returns an error
    :raises HTTPError: If the index.io API returns a non-200 response
    :return: A list of dicts containing the token_id and metadata uri
    """
    api_url = f"https://rpc.theindex.io/mainnet-beta/{config.THE_INDEX_API_KEY}"
    payload = {
        "method": "getNFTsByCollection",
        "jsonrpc": "2.0",
        "params": [contract],
        "id": 1,
    }
    resp = requests.post(url=api_url, json=payload)
    if resp.status_code == 200:
        decoded_response = resp.json()
        if decoded_response.get("result"):
            metadata_uris = []
            for nft in decoded_response["result"]:

                matches = re.search(r"#(?P<token_id>\d+)", nft["metadata"]["name"])
                if matches.groups():  # type: ignore
                    token_id = matches.group("token_id")  # type: ignore
                else:
                    token_id = None
                metadata_uris.append(
                    {"token_id": token_id, "uri": nft["metadata"]["uri"]}
                )
            return metadata_uris

        elif decoded_response.get("error"):
            raise Exception(decoded_response["error"])
        else:
            raise Exception(f"Unknown error\n{resp.text}")
    else:
        raise HTTPError(
            url=resp.url,
            code=resp.status_code,
            msg=resp.reason,
            hdrs=resp.headers,
            fp=None,
        )


def fetch(token_id: str, metadata_uri: str) -> Tuple[str, dict]:
    """Given a token_id and a metadata_uri, download the metadata and return it.

    :param token_id: The token_id of the NFT
    :param metadata_uri: The uri of the metadata
    :return: A tuple of the token_id and the raw metadata
    """
    _session = misc.mount_session()
    uri_response = _session.get(metadata_uri, timeout=3.05)

    try:
        response_json = uri_response.json()
        return (token_id, response_json)
    except Exception as err:
        print(err)
        raise Exception(
            f"Failed to get metadata from server using {metadata_uri}. Got {uri_response}."
        )


def parse_metadata(token_id_list: List, collection: str) -> List[Dict]:
    """Given a list of token_ids and a collection name, this function reads the raw metadata from disk,
    transforms it in a similar format as pulling.py and ultimately returns a list of dicts.

    :param token_id_list: List of token_ids to iterate over
    :param collection: The collection name
    :raises FileNotFoundError: If the metadata file does not exist
    :raises ValueError: If no attribute key can be found in the metadata
    :return: List of dicts containing metadata in the same format as pulling.py
    """
    metadata_list = []

    parsed_metadata_list = []

    for token_id in token_id_list:
        # Initiate json result
        result_json = None

        # Check if metadata file already exists
        filename = f"{config.ATTRIBUTES_FOLDER}/{collection}/{token_id}.json"

        if os.path.exists(filename):
            # Load existing file from disk
            with open(filename, "r") as f:
                result_json = json.load(f)
                metadata_list.append(result_json)
        else:
            # TODO: Download individual metadata file, save metadata to disk, read it and add it to the list
            raise FileNotFoundError(filename)

    for metadata_dict in metadata_list:
        if metadata_dict is not None:

            # TODO: What are other variations of name?
            # Add token name and token URI traits to the trait dictionary
            traits = dict()
            if "name" in metadata_dict:
                traits["TOKEN_NAME"] = metadata_dict["name"]
            else:
                traits["TOKEN_NAME"] = f"UNKNOWN"
            traits["TOKEN_ID"] = metadata_dict["tokenId"]

            # Find the attribute key from the server response
            if "attributes" in metadata_dict:
                attribute_key = "attributes"
            elif "traits" in metadata_dict:
                attribute_key = "traits"
            elif "properties" in metadata_dict:
                attribute_key = "properties"
            else:
                raise ValueError(
                    f"Failed to find the attribute key in the token {metadata_dict['tokenId']} "
                    f'metadata result. Tried "attributes" and "traits".\nAvailable '
                    f"keys: {metadata_dict.keys()}"
                )

            # Add traits from the server response JSON to the traits dictionary
            try:
                for attribute in metadata_dict[attribute_key]:
                    if "value" in attribute and "trait_type" in attribute:
                        traits[attribute["trait_type"]] = attribute["value"]
                    elif "value" not in attribute and isinstance(attribute, dict):
                        if len(attribute.keys()) == 1:
                            traits[attribute["trait_type"]] = "None"
                    elif isinstance(attribute, str):
                        traits[attribute] = metadata_dict[attribute_key][attribute]
                parsed_metadata_list.append(traits)

            # Handle exceptions result from URI does not contain attributes
            except Exception as err:
                print(err)
                print(
                    f"Failed to get metadata for id {metadata_dict['tokenId']}. Url response was {metadata_dict}."
                )

    return parsed_metadata_list


def pull_metadata(collection: str, contract: str, threads: Optional[int]) -> None:
    """The main function for pulling and parsing Solana NFT metadata.
    This function takes care of downloading, parsing, and saving the metadata.

    :param collection: The collection name
    :param contract: The NFT contract address
    :param threads: The number of threads to use for concurrently downloading the metadata
    """
    folder = f"{config.ATTRIBUTES_FOLDER}/{collection}/"
    if not os.path.exists(folder):
        os.mkdir(folder)

    # Get all metadata uris for collection
    metadata_uris = fetch_metadata_uris(contract=contract)

    token_ids = []
    for entry in metadata_uris:
        token_ids.append(entry["token_id"])

    BATCH_SIZE = 50
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        for i in range(0, len(metadata_uris), BATCH_SIZE):
            token_ids_batch = metadata_uris[i : i + BATCH_SIZE]
            # Skip on-chain fetch if we already have the metadata
            token_ids_batch = list(
                filter(
                    lambda entry: not os.path.exists(
                        f"{folder}/{entry['token_id']}.json"
                    ),
                    token_ids_batch,
                )
            )
            futures = [
                executor.submit(fetch, metadata_uri["token_id"], metadata_uri["uri"])
                for metadata_uri in token_ids_batch
            ]
            for future in concurrent.futures.as_completed(futures):
                token_id = future.result()[0]
                metadata = future.result()[1]
                save_metadata(
                    raw_metadata=metadata,
                    token_id=token_id,
                    collection=collection,
                )

    parsed_metadata = parse_metadata(token_id_list=token_ids, collection=collection)

    # Generate traits DataFrame and save to disk as csv
    trait_db = pd.DataFrame.from_records(parsed_metadata)
    trait_db = trait_db.set_index("TOKEN_ID")
    print(trait_db.head())
    trait_db.to_csv(f"{config.ATTRIBUTES_FOLDER}/{collection}.csv")


def _cli_parser() -> argparse.ArgumentParser:
    """
    Create the command line argument parser
    """
    parser = argparse.ArgumentParser(description="CLI for pulling NFT metadata.")
    parser.add_argument(
        "--contract",
        type=str,
        default=None,
        required=True,
        help="Collection contract address.",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default=None,
        required=True,
        help="Collection name. Will be used as folder name.",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=None,
        help=f"Number of threads to use for downloading metadata. (default: {min(32, os.cpu_count() + 4)})",  # type: ignore
    )
    return parser


if __name__ == "__main__":
    args = _cli_parser().parse_args()

    pull_metadata(
        collection=args.collection, contract=args.contract, threads=args.threads
    )
