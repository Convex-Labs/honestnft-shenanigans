import json
import time
import unittest

from tests import helpers
from honestnft_utils import chain


class TestCase(unittest.TestCase):
    def setUp(self):
        # Load test data
        with open(
            f"{helpers.TESTS_ROOT_DIR}/fixtures/test_data.json",
            "r",
        ) as f:
            self.test_data = json.load(f)

    def test_various_chains(self):
        for key, value in self.test_data.items():
            print(f"testing {key}")
            # Iterate over contract types (regular and proxy)
            for _key, _value in value["test_contracts"].items():
                # Iterate over test contracts
                for contract_key, contract_value in _value.items():

                    ctr_address = contract_value["address"]
                    ctr_abi = contract_value["abi"]
                    ctr_standard = contract_value["standard"]
                    ctr_blockchain = value["chain_name"]
                    ctr_token_ids = contract_value["token_ids"]

                    with self.subTest("Test get_contract_abi"):
                        result_abi = chain.get_contract_abi(
                            address=ctr_address, blockchain=ctr_blockchain
                        )
                        if len(ctr_abi) > 0:
                            self.assertEqual(result_abi, ctr_abi)
                        time.sleep(5)

                    with self.subTest("Test get_contract"):

                        get_contract_result = chain.get_contract(
                            address=ctr_address,
                            abi=result_abi,
                            blockchain=ctr_blockchain,
                        )
                        result_abi, result_contract = get_contract_result
                        self.assertIs(
                            type(get_contract_result),
                            tuple,
                        )
                        self.assertEqual(
                            result_contract.address.lower(), ctr_address.lower()
                        )
                    if _key == "regular":
                        if len(ctr_abi) > 0:
                            self.assertEqual(result_abi, ctr_abi)

                    elif _key == "proxy":
                        ctr_impl_abi = contract_value["implementation_abi"]
                        self.assertEqual(result_abi, ctr_impl_abi)

                with self.subTest("Test get_token_standard"):
                    if len(result_abi) > 0:
                        self.assertEqual(
                            chain.get_token_standard(result_contract),
                            ctr_standard,
                        )
                    else:
                        self.assertRaises(
                            ValueError, chain.get_token_standard, result_contract
                        )

                with self.subTest("Test get_token_uri_from_contract_batch"):
                    uri_func = chain.get_function_signature("tokenURI", result_abi)

                    if ctr_blockchain in [
                        "arbitrum",
                        "avalanche",
                        "binance",
                        "ethereum",
                        "fantom",
                        "optimism",
                        "polygon",
                    ]:
                        token_uris = chain.get_token_uri_from_contract_batch(
                            contract=result_contract,
                            token_ids=ctr_token_ids,
                            function_signature=uri_func,
                            abi=result_abi,
                            blockchain=ctr_blockchain,
                        )
                        self.assertEqual(type(token_uris), dict)
                        self.assertEqual(len(ctr_token_ids), len(token_uris))
                        self.assertEqual(type(next(iter(token_uris.values()))), str)
                    else:
                        self.assertRaises(
                            ValueError,
                            chain.get_token_uri_from_contract_batch,
                            contract=result_contract,
                            token_ids=ctr_token_ids,
                            function_signature=uri_func,
                            abi=result_abi,
                            blockchain=ctr_blockchain,
                        )
                time.sleep(5)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
