import unittest
from unittest import mock

import web3

from honestnft_utils import chain, config
from tests import constants, helpers


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
        self.assertEqual(
            chain.get_contract_abi(
                self.doodles_contract_address, blockchain="ethereum"
            ),
            constants.DOODLES_ABI,
        )

        self.assertRaises(
            ValueError,
            chain.get_contract_abi,
            address=self.doodles_contract_address,
            blockchain="lorem_ipsum",
        )

        with self.subTest("Test with invalid ABI_ENDPOINT"):
            with mock.patch("honestnft_utils.config.ABI_ENDPOINT", "localhost"):
                self.assertRaises(
                    Exception,
                    chain.get_contract_abi,
                    self.doodles_contract_address,
                    blockchain="ethereum",
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

        with mock.patch("honestnft_utils.config.ENDPOINT", ""):
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
                format_uri=False,
            )
            self.assertEqual(
                token_uri, "ipfs://QmPMc4tcBsMqLRuCQtPmPe84bpSjrC3Ky7t3JWuHXYB4aS/1"
            )

        with self.subTest("Test with format_uri=True"):
            token_uri = chain.get_token_uri_from_contract(
                contract=self.doodles_contract,
                token_id=1,
                uri_func="tokenURI",
                abi=self.doodles_abi,
                format_uri=True,
            )
            self.assertEqual(
                token_uri,
                f"{config.IPFS_GATEWAY}QmPMc4tcBsMqLRuCQtPmPe84bpSjrC3Ky7t3JWuHXYB4aS/1",
            )

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
            self.assertEqual(token_uris, constants.DOODLES_TOKEN_URIS_BATCH)
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

        with mock.patch("honestnft_utils.config.ENDPOINT", ""):
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
        with self.subTest("Test with tokenID starting at 0"):

            self.assertEqual(
                chain.get_lower_token_id(
                    self.doodles_contract, "tokenURI", self.doodles_abi
                ),
                0,
            )
        with self.subTest("Test with tokenID starting at 1"):
            contract_address = "0x7bd29408f11d2bfc23c34f18275bbf23bb716bc7"
            abi = chain.get_contract_abi(contract_address, blockchain="ethereum")
            abi, contract = chain.get_contract(
                contract_address, abi, blockchain="ethereum"
            )
            self.assertEqual(
                chain.get_lower_token_id(contract, "tokenURI", abi),
                1,
            )

        with self.subTest("test with tokenID starting at 160"):
            contract_address = "0x42069abfe407c60cf4ae4112bedead391dba1cdb"
            abi = chain.get_contract_abi(contract_address, blockchain="ethereum")
            abi, contract = chain.get_contract(
                contract_address, abi, blockchain="ethereum"
            )
            self.assertRaises(
                Exception, chain.get_lower_token_id, contract, "tokenURI", abi
            )

    #   TODO "Test with non sequential integers"

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
            self.assertEqual(
                base_uri, "ipfs://QmeN7ZdrTGpbGoo8URqzvyiDtcgJxwoxULbQowaTGhTeZc/"
            )

    def test_get_token_standard(self):
        self.assertEqual(
            chain.get_token_standard(self.doodles_contract),
            "ERC-721",
        )

    def test_format_metadata_uri(self):
        self.assertEqual(
            chain.format_metadata_uri(
                "ipfs://QmTUNnsrqLAGouRPqDFjqR2W6iAziAqNVTc2BdW5EaBrRX/1",
            ),
            f"{config.IPFS_GATEWAY}QmTUNnsrqLAGouRPqDFjqR2W6iAziAqNVTc2BdW5EaBrRX/1",
        )

        self.assertEqual(
            chain.format_metadata_uri(
                "https://ipfs.io/ipfs/QmTUNnsrqLAGouRPqDFjqR2W6iAziAqNVTc2BdW5EaBrRX/1",
            ),
            f"{config.IPFS_GATEWAY}QmTUNnsrqLAGouRPqDFjqR2W6iAziAqNVTc2BdW5EaBrRX/1",
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
