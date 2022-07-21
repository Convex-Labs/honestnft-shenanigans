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

            rarity_file_method_HNFT = (
                f"{self.TEMP_FOLDER}/{collection['name']}_raritytools-from-pulling.csv"
            )
            rarity_file_method_RT = (
                f"{self.TEMP_FOLDER}/{collection['name']}_raritytools-from-rt.csv"
            )

            DF_HNFT = pd.read_csv(rarity_file_method_HNFT)
            DF_HNFT = DF_HNFT[DF_HNFT["TOKEN_ID"].duplicated() == False]

            DF_RT = pd.read_csv(rarity_file_method_RT)
            DF_RT = DF_RT[DF_RT["TOKEN_ID"].duplicated() == False]

            with self.subTest("Compare length of collections"):
                self.assertEqual(
                    len(DF_HNFT),
                    len(DF_RT),
                    f"Rarity databases length for project {collection['name']} are not equal.\nHonestNFT: {len(DF_HNFT)} vs RarityTools: {len(DF_RT)}",
                )

            with self.subTest("Compare rank based on TOKEN_ID"):

                min_token_id_HNFT = DF_HNFT["TOKEN_ID"].min()
                max_token_id_HNFT = DF_HNFT["TOKEN_ID"].max()
                token_id_range = range(min_token_id_HNFT, max_token_id_HNFT + 1)

                for token_id in token_id_range:

                    hnft_rank = DF_HNFT.loc[
                        DF_HNFT["TOKEN_ID"] == token_id, "Rank"
                    ].item()

                    rt_rank = DF_RT.loc[DF_RT["TOKEN_ID"] == token_id, "Rank"].item()
                    self.assertEqual(
                        hnft_rank,
                        rt_rank,
                        f"Ranks are not the same for {collection['name']}, token_id {token_id}.\nHonestNFT: {hnft_rank} vs RarityTools: {rt_rank}",
                    )

    @classmethod
    def tearDownClass(self):
        # Clean up test files
        shutil.rmtree(
            f"{helpers.TESTS_ROOT_DIR}/temp_compare",
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
