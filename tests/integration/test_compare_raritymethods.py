#!venv/bin/python3
import os
import shutil
import unittest

import pandas as pd

from honestnft_utils import config
from metadata import pull_from_rt, rarity
from tests import helpers


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.test_data = [
            {
                "name": "alpacadabraz",
                "contract_address": "0x3db5463a9e2d04334192c6f2dd4b72def4751a61",
            },
            {
                "name": "swampverseofficial",
                "contract_address": "0x95784f7b5c8849b0104eaf5d13d6341d8cc40750",
            },
            {
                "name": "boredapeyachtclub",
                "contract_address": "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d",
                "comment": "exact match",
            },
            {
                "name": "pudgypenguins",
                "contract_address": "0xbd3531da5cf5857e7cfaa92426877b022e612cf8",
                "comment": "some ranks of by 1",
            },
            {
                "name": "world-of-women-nft",
                "contract_address": "0xe785e82358879f061bc3dcac6f0444462d4b5330",
            },
            {
                "name": "strangehands-official",
                "contract_address": "0xee669e0afa6de7f4bb2bff3e1e549274ad21a5dd",
            },
        ]

        if os.path.isdir(f"{helpers.TESTS_ROOT_DIR}/temp_compare"):
            pass
        else:
            os.mkdir(f"{helpers.TESTS_ROOT_DIR}/temp_compare")
        self.TEMP_FOLDER = f"{helpers.TESTS_ROOT_DIR}/temp_compare"

        for collection in self.test_data:

            ##############################################
            # download from raritytools
            with helpers.BlockStatementPrinting():
                pull_from_rt.download(collection["name"])

            os.rename(
                f"{config.RARITY_FOLDER}/{collection['name']}_raritytools.csv",
                f"{self.TEMP_FOLDER}/{collection['name']}_raritytools-from-rt.csv",
            )

            ##############################################
            # Generate rarity.py
            with helpers.BlockStatementPrinting():
                rarity.build_rarity_db(
                    collection=collection["name"],
                    attribute_file=f"{helpers.TESTS_ROOT_DIR}/fixtures/rarity_comparison/raw_attributes/{collection['name']}.csv",
                    method="raritytools",
                    trait_count=True,
                    sum_traits=None,
                    sum_trait_multiplier=35,
                )
            os.rename(
                f"{config.RARITY_FOLDER}/{collection['name']}_raritytools.csv",
                f"{self.TEMP_FOLDER}/{collection['name']}_raritytools-from-pulling.csv",
            )

    #####################
    # Compare rarity methods
    def test_compare_methods(self):
        for collection in self.test_data:

            rarity_file_method_HonestNFT = (
                f"{self.TEMP_FOLDER}/{collection['name']}_raritytools-from-pulling.csv"
            )
            rarity_file_method_RT = (
                f"{self.TEMP_FOLDER}/{collection['name']}_raritytools-from-rt.csv"
            )

            RARITY_DB_HONESTNFT = pd.read_csv(rarity_file_method_HonestNFT)
            RARITY_DB_HONESTNFT = RARITY_DB_HONESTNFT[
                RARITY_DB_HONESTNFT["TOKEN_ID"].duplicated() == False
            ]

            RARITY_DB_RT = pd.read_csv(rarity_file_method_RT)
            RARITY_DB_RT = RARITY_DB_RT[RARITY_DB_RT["TOKEN_ID"].duplicated() == False]

            with self.subTest("Compare length of collections"):
                self.assertEqual(
                    len(RARITY_DB_HONESTNFT),
                    len(RARITY_DB_RT),
                    f"Lengths of two rarity databases are not equal.\nHonestNFT: {len(RARITY_DB_HONESTNFT)} vs RarityTools: {len(RARITY_DB_RT)}",
                )

            with self.subTest("Compare rank based on TOKEN_ID"):

                min_token_id_HonestNFT = RARITY_DB_HONESTNFT["TOKEN_ID"].min()
                max_token_id_HonestNFT = RARITY_DB_HONESTNFT["TOKEN_ID"].max()
                token_id_range = range(
                    min_token_id_HonestNFT, max_token_id_HonestNFT + 1
                )

                for token_id in token_id_range:

                    honest_nft_rank = RARITY_DB_HONESTNFT.loc[
                        RARITY_DB_HONESTNFT["TOKEN_ID"] == token_id, "Rank"
                    ].item()

                    rt_rank = RARITY_DB_RT.loc[
                        RARITY_DB_RT["TOKEN_ID"] == token_id, "Rank"
                    ].item()

                    if honest_nft_rank == rt_rank:
                        # print("Ranks are the same")
                        pass
                    else:
                        # self.fail(collection["name"])
                        # Check if the rarity_score is the same for previous or next rank.

                        score_previous_rank_honestnft = RARITY_DB_HONESTNFT.loc[
                            RARITY_DB_HONESTNFT["Rank"] == honest_nft_rank - 1,
                            "RARITY_SCORE",
                        ].item()

                        score_current_rank_honestnft = RARITY_DB_HONESTNFT.loc[
                            RARITY_DB_HONESTNFT["Rank"] == honest_nft_rank,
                            "RARITY_SCORE",
                        ].item()

                        score_next_rank_honestnft = RARITY_DB_HONESTNFT.loc[
                            RARITY_DB_HONESTNFT["Rank"] == honest_nft_rank + 1,
                            "RARITY_SCORE",
                        ].item()

                        if (
                            score_current_rank_honestnft
                            == score_previous_rank_honestnft
                            or score_current_rank_honestnft == score_next_rank_honestnft
                        ):
                            pass
                        else:
                            self.fail(
                                f"Ranks are not the same for token_id {token_id}.\nHonestNFT: {honest_nft_rank} vs RarityTools: {rt_rank}"
                            )

                        score_previous_rank_raritytools = RARITY_DB_RT.loc[
                            RARITY_DB_RT["Rank"] == rt_rank - 1,
                            "RARITY_SCORE",
                        ].item()
                        score_current_rank_raritytools = RARITY_DB_RT.loc[
                            RARITY_DB_RT["Rank"] == rt_rank,
                            "RARITY_SCORE",
                        ].item()
                        score_next_rank_raritytools = RARITY_DB_RT.loc[
                            RARITY_DB_RT["Rank"] == rt_rank + 1,
                            "RARITY_SCORE",
                        ].item()

                        if (
                            score_current_rank_raritytools
                            == score_previous_rank_raritytools
                            or score_current_rank_raritytools
                            == score_next_rank_raritytools
                        ):
                            pass

                        else:
                            self.fail(
                                f"Ranks are not the same for token_id {token_id}.\nHonestNFT: {honest_nft_rank} vs RarityTools: {rt_rank}"
                            )

    @classmethod
    def tearDownClass(self):
        # Clean up test files
        shutil.rmtree(
            f"{helpers.TESTS_ROOT_DIR}/temp_compare",
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
