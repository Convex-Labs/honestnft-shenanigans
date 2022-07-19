import argparse
import json
import os
import shutil
from typing import Optional

import pandas as pd
import requests

from honestnft_utils import config, misc


def download(
    contract_address: str,
    normalize_traits: bool = True,
    trait_count: bool = True,
    save_raw_data: bool = False,
    compress_raw_data: bool = False,
    collection: Optional[str] = None,
):
    url = "https://raritysniffer.com/api/index.php"

    params = {
        "query": "fetch",
        "collection": contract_address,
        "taskId": "any",
        "norm": str(normalize_traits).lower(),
        "partial": str(False).lower(),
        "traitCount": str(trait_count).lower(),
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
    }

    response = requests.request("GET", url, headers=headers, params=params)
    response_data = response.json()

    # list to make completeness checks
    token_ids = []

    if response.status_code == 200:
        raw_metadata = []  # Initiate list of dicts that will be converted to DataFrame
        rarity_data = []
        if collection:
            COLLECTION_NAME = collection
        else:
            COLLECTION_NAME = response_data["name"].replace(" ", "")
        print(f"Received data for {COLLECTION_NAME}")
        print(f"{len(response_data['data'])} tokens in the collection")

        # Create folder to store metadata
        if save_raw_data:
            folder = f"{config.ATTRIBUTES_FOLDER}/{COLLECTION_NAME}/"
            print(f"Saving metadata to {folder}")
            if not os.path.exists(folder):
                os.mkdir(folder)

        for i, token in enumerate(response_data["data"]):

            token_ids.append(token["id"])
            # Add token name and token URI traits to the trait dictionary
            traits = dict()
            traits["TOKEN_ID"] = token["id"]
            traits["TOKEN_NAME"] = token["name"]

            # token['attributes'] = token.pop('traits')
            for atr in token["traits"]:
                if not atr["c"] == "Trait Count":
                    traits[atr["c"]] = atr["n"]

            # add this token to dictionary list
            raw_metadata.append(traits)

            rarity_traits = traits.copy()
            # Now we will form the rarity data
            rarity_traits["RARITY_SCORE"] = token["score"]
            rarity_traits["Rank"] = token["positionId"]
            for atr in token["traits"]:
                rarity_traits[atr["c"]] = atr["r"]

            rarity_data.append(rarity_traits)

            if save_raw_data:
                # print(f"Saving raw attributes to disk...")
                PATH = (
                    f"{config.ATTRIBUTES_FOLDER}/{COLLECTION_NAME}/{token['id']}.json"
                )
                with open(PATH, "w") as destination_file:
                    json.dump(token, destination_file)
    else:
        print(response.text)
        raise Exception(f"Error: {response.status_code}")

    print(f"tokens in the list {len(token_ids)}")
    print(f"lower_id: {min(token_ids)}")
    print(f"upper_id: {max(token_ids)}")

    if min(token_ids) == 0:
        max_supply = max(token_ids) + 1
        print(f"max supply: {max(token_ids) + 1}")
    else:
        max_supply = max(token_ids)
        print(f"max supply: {max(token_ids)}")

    # warn if raritysniffer doesn't have the full collection
    # TODO: print a list of missing token ids
    if len(token_ids) != max_supply:
        print(f"{max_supply - len(token_ids)} tokens with missing metadata")

    # Generate traits DataFrame and save to disk as csv
    trait_db = pd.DataFrame.from_records(raw_metadata)
    trait_db = trait_db.set_index("TOKEN_ID")
    trait_db = trait_db.sort_index()

    trait_db.to_csv(f"{config.ATTRIBUTES_FOLDER}/{COLLECTION_NAME}.csv")

    # Generate rarity DataFrame and save to disk as csv
    rarity_db = pd.DataFrame.from_records(rarity_data)
    rarity_db = rarity_db.sort_values(["Rank"], ascending=True)

    if rarity_db.columns[-1] != "Rank":
        rank_column = rarity_db.pop("Rank")
        rarity_db.insert(len(rarity_db.columns), "Rank", rank_column)

    if rarity_db.columns[-1] != "RARITY_SCORE":
        rarity_score_column = rarity_db.pop("RARITY_SCORE")
        rarity_db.insert(
            len(rarity_db.columns) - 1, "RARITY_SCORE", rarity_score_column
        )

    rarity_db = rarity_db.set_index("TOKEN_ID")

    rarity_db.to_csv(f"{config.RARITY_FOLDER}/{COLLECTION_NAME}_raritytools.csv")

    # Compress raw data and delete folder
    if compress_raw_data:
        # print("Compressing raw metadata")
        dir_name = f"{config.ATTRIBUTES_FOLDER}/{COLLECTION_NAME}"
        shutil.make_archive(dir_name, "zip", dir_name)
        shutil.rmtree(dir_name)

    print("finished.")


def _cli_parser() -> argparse.ArgumentParser:
    """
    Create the command line argument parser
    """
    parser = argparse.ArgumentParser(
        description="CLI for pulling NFT attribute metadata and rarity data from raritysniffer.com"
    )
    parser.add_argument(
        "-c",
        "--contract",
        type=str,
        default=None,
        help="Collection contract address.",
        required=True,
    )
    parser.add_argument(
        "--normalize_traits",
        help="Trait Normalization (Default: True)",
        type=misc.strtobool,
        nargs="?",
        const=True,
        default=True,
        choices=[True, False],
    )
    parser.add_argument(
        "--trait_count",
        help="Trait Count Weight (Default: True)",
        type=misc.strtobool,
        nargs="?",
        const=True,
        default=True,
        choices=[True, False],
    )

    parser.add_argument(
        "--save_raw_data",
        help="Set to 'True' to keep raw metadata for each individual token_id. (Default: False)",
        type=misc.strtobool,
        nargs="?",
        const=True,
        default=False,
        choices=[True, False],
    )

    parser.add_argument(
        "--compress_raw_data",
        help="Set to 'True' to zip raw metadata to save disk space. (Default: False)",
        type=misc.strtobool,
        nargs="?",
        const=True,
        default=False,
        choices=[True, False],
    )
    parser.add_argument(
        "--collection",
        type=str,
        default=None,
        help="Collection name. If not provided, will be derived from API response.",
    )
    return parser


if __name__ == "__main__":
    args = _cli_parser().parse_args()

    download(
        contract_address=args.contract,
        normalize_traits=args.normalize_traits,
        trait_count=args.trait_count,
        save_raw_data=args.save_raw_data,
        compress_raw_data=args.compress_raw_data,
        collection=args.collection,
    )
