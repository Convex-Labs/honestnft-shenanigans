import argparse

import numpy as np
import pandas as pd

from honestnft_utils import config


def max_variety_count(trait_db: pd.DataFrame, trait_types: list) -> int:
    # Get the number of trait values in the largest trait class
    max_size = 0
    for trait in trait_types:
        count = trait_db.groupby([str(trait)]).size()
        if len(count) > max_size:
            max_size = len(count)

    return max_size


def gen_rarity_score(
    trait_db: pd.DataFrame,
    trait_types: list,
    method: str,
    trait_count: bool,
    sum_traits: list,
    sum_trait_multiplier: int,
) -> pd.DataFrame:

    # Create copy of trait database
    rarity_db = trait_db.copy(deep=True)

    # Set list of traits that are to be summed
    if isinstance(sum_traits, str):
        sum_traits = list(sum_traits)
    if sum_traits is None:
        sum_traits = list()

    # Create list of traits that are not to be summed
    non_sum_traits = [t for t in trait_types if t not in sum_traits]

    if method == "raritytools":
        """
        Rarity.tools methodology. This computes rarity normalized by number of possible traits.
        """

        # Initiate trait value to rarity score map
        value_score_map = {}

        # Compute number of tokens in the collection
        num_tokens = len(trait_db)

        # Find the max number of trait values for a given trait across the collection
        max_size = max_variety_count(trait_db, non_sum_traits)

        if trait_count:
            # Compute trait count and add variable to the data frame
            trait_db["NUM_TRAITS"] = rarity_db.apply(
                lambda row: len(trait_types)
                - sum(row[0 : (len(rarity_db.columns))] == "None"),
                axis=1,
            )

            # Append num_traits variable to the trait type list
            trait_types.append("NUM_TRAITS")
            non_sum_traits.append("NUM_TRAITS")

        # Compute the rarity score of each trait for each item in the collection
        for trait in non_sum_traits:
            # Compute the incidence of a trait value across the collection
            value_count = trait_db.groupby([str(trait)]).size()

            # Display incidence of each trait value across the collection
            print(value_count)

            # Compute the rarity of each trait value
            count_pct = (1 / (value_count / num_tokens)) / (len(value_count) / max_size)

            # Add the value to score map of the trait to the cache
            value_score_map[str(trait)] = count_pct.to_dict()

            # Set the rarity for the trait value of each item in the collection
            rarity_db[trait] = trait_db[trait].map(value_score_map[trait])

        # Compute rarity score of sum traits
        if len(sum_traits) > 0:
            # Rescale sum traits between 0 and 1
            scaled_traits = list()
            for trait in sum_traits:
                scaled_trait = f"SCALED_{trait}"
                trait_max = rarity_db[trait].max()
                trait_min = rarity_db[trait].min()
                rarity_db[scaled_trait] = (rarity_db[trait] - trait_min) / (
                    trait_max - trait_min
                )
                scaled_traits.append(scaled_trait)

            # Compute score multiplier, Assumes contribution is half of rarity score on average
            mean_non_sum_score = rarity_db[non_sum_traits].sum(axis=1).mean()
            mean_sum_score = rarity_db[scaled_traits].sum(axis=1).mean()
            multiplier = mean_non_sum_score / mean_sum_score

            # Add sum trait variable to rarity data frame
            rarity_db["SUM_TRAIT"] = (
                rarity_db[scaled_traits].sum(axis=1) * multiplier * sum_trait_multiplier
            )

            # Add sum trait variable to the non sum trait list
            non_sum_traits.append("SUM_TRAIT")

    else:
        raise NotImplementedError(f"Method {method} is not supported. Try raritytools.")

    # Compute aggregate rarity
    rarity_db["RARITY_SCORE"] = rarity_db[non_sum_traits].sum(axis=1)

    # Set the type of column TOKEN_ID to string (for consistent sorting like Rarity.Tools)
    rarity_db["TOKEN_ID"] = rarity_db["TOKEN_ID"].astype(str)

    # Sort database and assign rank
    rarity_db = rarity_db.sort_values(
        ["RARITY_SCORE", "TOKEN_ID"], ascending=[False, True]
    )
    rarity_db["Rank"] = np.arange(1, len(rarity_db) + 1)

    # Set index as token name
    rarity_db = rarity_db.set_index("TOKEN_ID")

    return rarity_db


def build_rarity_db(
    collection: str,
    attribute_file: str,
    method: str,
    trait_count: bool,
    sum_traits: list,
    sum_trait_multiplier: int,
) -> None:
    # Load raw attribute file from disk
    trait_db = pd.read_csv(attribute_file, delimiter=",")

    # Format data frame such that null values display as 'None'
    trait_db = trait_db.fillna("None")

    # Assign list of trait names
    trait_names = list(trait_db.columns[2:])

    # Generate rarity score
    rarity_db = gen_rarity_score(
        trait_db, trait_names, method, trait_count, sum_traits, sum_trait_multiplier
    )

    # Write rarity data to disk
    rarity_db.to_csv(f"{config.RARITY_FOLDER}/{collection}_{method}.csv")

    # Print top 5 items
    print(rarity_db.head(5).T)


def _cli_parser() -> argparse.ArgumentParser:
    """
    Create the command line argument parser
    """
    parser = argparse.ArgumentParser(
        description="CLI for generating rarity score of NFT collections."
    )
    parser.add_argument(
        "--collection",
        type=str,
        default=None,
        help="Collection name.",
    )
    parser.add_argument(
        "--method",
        type=str,
        default="raritytools",
        help="Method to use to compute rarity. (default: raritytools)",
    )
    parser.add_argument(
        "--trait_count",
        type=bool,
        default=True,
        help="Toggle using trait count in computation. (default: True)",
    )
    parser.add_argument(
        "--sum_traits",
        type=str,
        nargs="+",
        help="Traits to sum instead of computing rarity. Can be one or many. (default: None)",
    )
    parser.add_argument(
        "--sum_trait_multiplier",
        type=float,
        default=35,
        help="Trait score multiplier to use for summed traits. (default: 35)",
    )
    return parser


if __name__ == "__main__":

    args = _cli_parser().parse_args()

    # Build attribute file
    attribute_file = f"{config.ATTRIBUTES_FOLDER}/{args.collection}.csv"

    # Build rarity database and save to disk
    build_rarity_db(
        args.collection,
        attribute_file,
        args.method,
        args.trait_count,
        args.sum_traits,
        args.sum_trait_multiplier,
    )
