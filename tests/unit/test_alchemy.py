import unittest
from unittest import mock

from honestnft_utils import alchemy
from tests import constants


class TestCase(unittest.TestCase):
    def test_get_all_token_ids(self):
        self.assertEqual(
            alchemy.get_all_token_ids(contract_address=constants.DOODLES_ADDRESS),
            constants.DOODLES_TOKEN_IDS,
        )

    @mock.patch("honestnft_utils.config.ALCHEMY_API_KEY", None)
    def test_without_api_key(self):
        self.assertRaises(
            Exception,
            alchemy.get_all_token_ids,
            contract_address=constants.DOODLES_ADDRESS,
        )
