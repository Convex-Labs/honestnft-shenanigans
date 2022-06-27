import unittest
import unittest.mock as mock

from honestnft_utils import config
from honestnft_utils import ipfs

VALID_URIS = [
    {
        "uri": "ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG",
        "cid": "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG",
        "suffix": "",
    },
    {
        "uri": "/ipfs/bafybcfcqbwlhwbfq2k3ne2ysffcdoc4pmmsengy",
        "cid": "bafybcfcqbwlhwbfq2k3ne2ysffcdoc4pmmsengy",
        "suffix": "",
    },
    {
        "uri": "ipfs://bafybeialdjathblysfa4ki6ryso7cmeiufeyvcwmeegmv53jxt3pyffzru/0.txt",
        "cid": "bafybeialdjathblysfa4ki6ryso7cmeiufeyvcwmeegmv53jxt3pyffzru",
        "suffix": "/0.txt",
    },
    {
        "uri": "/ipfs/QmUCseQWXCSrhf9edzVKTvoj8o8Ts5aXFGNPameZRPJ6uR",
        "cid": "QmUCseQWXCSrhf9edzVKTvoj8o8Ts5aXFGNPameZRPJ6uR",
        "suffix": "",
    },
    {
        "uri": "https://ipfs.io/ipfs/QmP5zQxwHXUYKNCfyXXeJ8K5YUUW5bGWiFRTguczmj491N/0.txt",
        "cid": "QmP5zQxwHXUYKNCfyXXeJ8K5YUUW5bGWiFRTguczmj491N",
        "suffix": "/0.txt",
    },
    {
        "uri": "https://bafybeialdjathblysfa4ki6ryso7cmeiufeyvcwmeegmv53jxt3pyffzru.ipfs.dweb.link/0.txt?loc=123",
        "cid": "bafybeialdjathblysfa4ki6ryso7cmeiufeyvcwmeegmv53jxt3pyffzru",
        "suffix": "/0.txt?loc=123",
    },
    {
        "uri": "ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG",
        "cid": "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG",
        "suffix": "",
    },
    {
        "uri": "ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG/test.txt",
        "cid": "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG",
        "suffix": "/test.txt",
    },
    {
        "uri": "https://ipfs.io/ipfs/bafybeialdjathblysfa4ki6ryso7cmeiufeyvcwmeegmv53jxt3pyffzru/0.txt",
        "cid": "bafybeialdjathblysfa4ki6ryso7cmeiufeyvcwmeegmv53jxt3pyffzru",
        "suffix": "/0.txt",
    },
    {
        "uri": "https://hungrywolves.mypinata.cloud/ipfs/QmU9miGYP6wGPodb3AE7LbAyKSF9bxq9CbeKmF5U7DfCt1/4000",
        "cid": "QmU9miGYP6wGPodb3AE7LbAyKSF9bxq9CbeKmF5U7DfCt1",
        "suffix": "/4000",
    },
]

INVALID_URIS = [
    "https://ipfs.io/ipfs/QmYwAPJzv5CZsnA6s3Xf2nemtYgPpHdWEz79ojWnPbdG/test.txt",
    "ipfs://1264/test.txt",
    "https://ipfs.io/ipfsqmUCseQWXCSrhf9edzVKTvoj8o8Ts5aXFGNPameZRPJ6u/test.txt",
    "https://ipfs.io/ipfs/124/test.txt",
    "/IPFS/QmNOTAVALIDCID",
    1234,
    None,
    b"19",
]


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
        with self.subTest("Testing valid URIs"):
            for entry in VALID_URIS:
                self.assertEqual(
                    ipfs.format_ipfs_uri(entry["uri"]),
                    f"{config.IPFS_GATEWAY}{entry['cid']}{entry['suffix']}",
                )

        with self.subTest("Testing invalid URIs"):
            for entry in INVALID_URIS:
                if type(entry) == str:
                    self.assertRaises(ValueError, ipfs.format_ipfs_uri, entry)
            else:
                self.assertRaises(TypeError, ipfs.format_ipfs_uri, entry)

    def test_infer_cid_from_uri(self):
        for entry in VALID_URIS:
            self.assertEqual(ipfs.infer_cid_from_uri(entry["uri"]), entry["cid"])
            self.assertIs(type(ipfs.infer_cid_from_uri(entry["uri"])), str)

        for entry in INVALID_URIS:
            if type(entry) == str:
                self.assertIsNone(ipfs.infer_cid_from_uri(entry))
            else:
                self.assertRaises(TypeError, ipfs.infer_cid_from_uri, entry)

    def test_is_valid_ipfs_uri(self):
        for entry in VALID_URIS:
            self.assertTrue(ipfs.is_valid_ipfs_uri(entry["uri"]))
        for entry in INVALID_URIS:
            self.assertFalse(ipfs.is_valid_ipfs_uri(entry))

    @mock.patch("honestnft_utils.config.IPFS_GATEWAY", None)
    def test_mock_with_empty_gateway(self):
        self.assertEqual(
            ipfs.format_ipfs_uri(
                "ipfs://QmUCseQWXCSrhf9edzVKTvoj8o8Ts5aXFGNPameZRPJ6uR"
            ),
            "https://ipfs.io/ipfs/QmUCseQWXCSrhf9edzVKTvoj8o8Ts5aXFGNPameZRPJ6uR",
        )


if __name__ == "__main__":
    unittest.main()
