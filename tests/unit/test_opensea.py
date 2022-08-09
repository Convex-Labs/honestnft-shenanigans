import unittest

from honestnft_utils import opensea

DELISTED_COLLECTIONS = [
    "0x2ee6af0dff3a1ce3f7e3414c52c48fd50d73691e",
]
LISTED_COLLECTIONS = [
    "0x8a90cab2b38dba80c64b7734e58ee1db38b8992e",
    "0xbd1d2ea3127587f4ecfd271e1dadfc95320b8dea",
]


class TestCase(unittest.TestCase):
    def test_is_collection_delisted(self):
        with self.subTest("Testing delisted collections"):
            for entry in DELISTED_COLLECTIONS:
                self.assertTrue(opensea.is_collection_delisted(entry), entry)

        with self.subTest("Testing listed collections"):
            for entry in LISTED_COLLECTIONS:
                self.assertFalse(opensea.is_collection_delisted(entry), entry)
