import unittest
from unittest import mock

import web3

from tests import constants
from tests import helpers
from utils import chain


class TestCase(unittest.TestCase):
    def setUp(self):
        self.doodles_contract_address = constants.DOODLES_ADDRESS
        self.doodles_abi = constants.DOODLES_ABI

        self.doodles_abi, self.doodles_contract = chain.get_contract(
            address=self.doodles_contract_address,
            abi=self.doodles_abi,
            blockchain="ethereum",
        )

        self.tubbycats_contract_address = constants.TUBBYCATS_ADDRESS
        self.tubbycats_abi = constants.TUBBYCATS_ABI
        self.tubbycats_abi, self.tubbycats_contract = chain.get_contract(
            address=self.tubbycats_contract_address,
            abi=self.tubbycats_abi,
            blockchain="ethereum",
        )

    def test_get_function_signature(self):

        self.assertIs(
            type(chain.get_function_signature("tokenURI", self.doodles_abi)), str
        )
        self.assertEqual(
            chain.get_function_signature("tokenURI", self.doodles_abi),
            "tokenURI(uint256)(string)",
        )
        self.assertEqual(
            chain.get_function_signature("totalSupply", self.doodles_abi),
            "totalSupply()(uint256)",
        )
        self.assertEqual(
            chain.get_function_signature("name", self.doodles_abi),
            "name()(string)",
        )
        self.assertEqual(
            chain.get_function_signature("owner", self.doodles_abi),
            "owner()(address)",
        )
        self.assertEqual(
            chain.get_function_signature("ownerOf", self.doodles_abi),
            "ownerOf(uint256)(address)",
        )
        self.assertEqual(
            chain.get_function_signature("balanceOf", self.doodles_abi),
            "balanceOf(address)(uint256)",
        )
        self.assertRaises(
            ValueError,
            chain.get_function_signature,
            "loremIpsum",
            self.doodles_abi,
        )

    def test_get_contract_abi(self):
        contract_abi = chain.get_contract_abi(
            self.doodles_contract_address, blockchain="ethereum"
        )

        self.assertEqual(type(contract_abi), list)

        self.assertEqual(
            contract_abi,
            self.doodles_abi,
        )

        self.assertRaises(
            ValueError,
            chain.get_contract_abi,
            address=self.doodles_contract_address,
            blockchain="lorem_ipsum",
        )

    def test_get_contract(self):

        self.assertIs(
            type(
                chain.get_contract(
                    address=self.doodles_contract_address,
                    abi=self.doodles_abi,
                    blockchain="ethereum",
                )
            ),
            tuple,
        )

        self.assertRaises(
            ValueError,
            chain.get_contract,
            address=self.doodles_contract_address,
            abi=self.doodles_abi,
            blockchain="lorem_ipsum",
        )

        with mock.patch("utils.config.ENDPOINT", ""):
            with self.subTest("Test with missing web3 provider"):
                self.assertRaises(
                    ValueError,
                    chain.get_contract,
                    address=self.doodles_contract_address,
                    abi=self.doodles_abi,
                    blockchain="ethereum",
                )

    def test_get_contract_function(self):

        isinstance(
            chain.get_contract_function(
                self.doodles_contract, "totalSupply", self.doodles_abi
            ),
            web3.contract.ContractFunction,
        )

    def test_get_token_uri_from_contract(self):

        with self.subTest("Test with valid tokenID"):
            token_uri = chain.get_token_uri_from_contract(
                contract=self.doodles_contract,
                token_id=1,
                uri_func="tokenURI",
                abi=self.doodles_abi,
            )
            self.assertEqual(type(token_uri), str)
            # Test if the URI is modified according to our ipfs gateway?

        with self.subTest("Test with invalid tokenID"):
            self.assertRaises(
                Exception,
                chain.get_token_uri_from_contract,
                contract=self.doodles_contract,
                token_id=123456,
                uri_func="tokenURI",
                abi=self.doodles_abi,
            )

    def test_get_token_uri_from_contract_batch(self):
        uri_func = chain.get_function_signature("tokenURI", self.doodles_abi)

        with self.subTest("Test with all valid tokenID"):
            token_ids = [0, 1, 2, 3, 4]
            token_uris = chain.get_token_uri_from_contract_batch(
                contract=self.doodles_contract,
                token_ids=token_ids,
                function_signature=uri_func,
                abi=self.doodles_abi,
                blockchain="ethereum",
            )
            self.assertEqual(type(token_uris), dict)
            self.assertEqual(len(token_ids), len(token_uris))
            self.assertEqual(type(token_uris[0]), str)

        with self.subTest("Test with an invalid tokenID"):
            token_ids = [0, 1, 234569, 3, 4]

            self.assertRaises(
                web3.exceptions.ContractLogicError,
                chain.get_token_uri_from_contract_batch,
                contract=self.doodles_contract,
                token_ids=token_ids,
                function_signature=uri_func,
                abi=self.doodles_abi,
                blockchain="ethereum",
            )

        with self.subTest("Test with empty token list"):
            token_ids = []
            self.assertEqual(
                chain.get_token_uri_from_contract_batch(
                    contract=self.doodles_contract,
                    token_ids=token_ids,
                    function_signature=uri_func,
                    abi=self.doodles_abi,
                    blockchain="ethereum",
                ),
                {},
            )

        with mock.patch("utils.config.ENDPOINT", ""):
            with self.subTest("Test with missing web3 provider"):
                token_ids = [0, 1, 2, 3, 4]
                self.assertRaises(
                    ValueError,
                    chain.get_token_uri_from_contract_batch,
                    contract=self.doodles_contract,
                    token_ids=token_ids,
                    function_signature=uri_func,
                    abi=self.doodles_abi,
                    blockchain="ethereum",
                )

    @helpers.blockPrinting
    def test_get_lower_token_id(self):
        lower_token_id = chain.get_lower_token_id(
            self.doodles_contract, "tokenURI", self.doodles_abi
        )
        self.assertEqual(type(lower_token_id), int)

    def test_get_base_uri(self):
        with self.subTest("Test without baseURI in ABI"):

            self.assertRaises(
                ValueError,
                chain.get_base_uri,
                contract=self.doodles_contract,
                abi=self.doodles_abi,
            )

        with self.subTest("Test ABI with baseURI"):

            base_uri = chain.get_base_uri(
                contract=self.tubbycats_contract, abi=self.tubbycats_abi
            )
            self.assertEqual(type(base_uri), str)
            self.assertEqual(
                base_uri, "ipfs://QmeN7ZdrTGpbGoo8URqzvyiDtcgJxwoxULbQowaTGhTeZc/"
            )

    def test_get_token_standard(self):
        token_standard = chain.get_token_standard(self.doodles_contract)
        self.assertEqual(
            token_standard,
            "ERC-721",
        )
        self.assertEqual(type(token_standard), str)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
