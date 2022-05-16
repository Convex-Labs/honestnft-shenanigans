import unittest
import unittest.mock as mock
from utils import config
from utils import ipfs

VALID_URIS = {
    "/ipfs/QmUCseQWXCSrhf9edzVKTvoj8o8Ts5aXFGNPameZRPJ6uR": "QmUCseQWXCSrhf9edzVKTvoj8o8Ts5aXFGNPameZRPJ6uR",
    "ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG": "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG",
    "ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG/test.txt": "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG",
    "https://ipfs.io/ipfs/QmP5zQxwHXUYKNCfyXXeJ8K5YUUW5bGWiFRTguczmj491N/0.txt": "QmP5zQxwHXUYKNCfyXXeJ8K5YUUW5bGWiFRTguczmj491N",
}

INVALID_URIS = {
    "ipfs://1264/test.txt": None,
    "https://ipfs.io/ipfsqmUCseQWXCSrhf9edzVKTvoj8o8Ts5aXFGNPameZRPJ6u/test.txt": None,
}


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

        self.assertEqual(
            ipfs.format_ipfs_uri(
                "https://ipfs.io/ipfs/QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
            ),
            f"{config.IPFS_GATEWAY}QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG",
        )

    def test_infer_cid_from_uri(self):
        for uri, cid in VALID_URIS.items():
            self.assertEqual(ipfs.infer_cid_from_uri(uri), cid)
            self.assertIs(type(ipfs.infer_cid_from_uri(uri)), str)

        for uri, cid in INVALID_URIS.items():
            self.assertEqual(ipfs.infer_cid_from_uri(uri), cid)

    def test_is_valid_ipfs_uri(self):
        for uri, cid in VALID_URIS.items():
            self.assertTrue(ipfs.is_valid_ipfs_uri(uri))
        for uri, cid in INVALID_URIS.items():
            self.assertFalse(ipfs.is_valid_ipfs_uri(uri))

    @mock.patch("utils.config.IPFS_GATEWAY", "")
    def test_mock_with_empty_gateway(self):
        self.assertEqual(
            ipfs.format_ipfs_uri(
                "ipfs://QmUCseQWXCSrhf9edzVKTvoj8o8Ts5aXFGNPameZRPJ6uR"
            ),
            "https://ipfs.io/ipfs/QmUCseQWXCSrhf9edzVKTvoj8o8Ts5aXFGNPameZRPJ6uR",
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
