import unittest

from utils import config
from utils import ipfs


class TestCase(unittest.TestCase):
    def test_get_file_suffix(self):
        self.assertIs(type(ipfs.get_file_suffix("1456.txt")), str)
        self.assertEqual(ipfs.get_file_suffix("1456.txt"), ".txt")
        self.assertEqual(ipfs.get_file_suffix("123.json"), ".json")
        self.assertEqual(ipfs.get_file_suffix("14"), "")
        self.assertRaises(
            ValueError,
            ipfs.get_file_suffix,
            "1456.json",
            "12",
        )

    def test_format_ipfs_uri(self):
        self.assertEqual(
            ipfs.format_ipfs_uri(
                "ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
            ),
            f"{config.IPFS_GATEWAY}QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG",
        )
        self.assertEqual(
            ipfs.format_ipfs_uri(
                "ipfs://bafybeialdjathblysfa4ki6ryso7cmeiufeyvcwmeegmv53jxt3pyffzru"
            ),
            f"{config.IPFS_GATEWAY}bafybeialdjathblysfa4ki6ryso7cmeiufeyvcwmeegmv53jxt3pyffzru",
        )
        self.assertEqual(
            ipfs.format_ipfs_uri(
                "https://gateway.pinata.cloud/ipfs/bafybeialdjathblysfa4ki6ryso7cmeiufeyvcwmeegmv53jxt3pyffzru"
            ),
            f"{config.IPFS_GATEWAY}bafybeialdjathblysfa4ki6ryso7cmeiufeyvcwmeegmv53jxt3pyffzru",
        )
        self.assertEqual(
            ipfs.format_ipfs_uri(
                "https://hungrywolves.mypinata.cloud/ipfs/QmU9miGYP6wGPodb3AE7LbAyKSF9bxq9CbeKmF5U7DfCt1/4000"
            ),
            f"{config.IPFS_GATEWAY}QmU9miGYP6wGPodb3AE7LbAyKSF9bxq9CbeKmF5U7DfCt1/4000",
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
