import os
import unittest
from pathlib import Path

from honestnft_utils import misc
from tests import helpers


class TestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_path = Path(f"{helpers.TESTS_ROOT_DIR}/temp")
        self.temp_path.mkdir(parents=True, exist_ok=True)

    def test_get_first_filename_in_dir(self):
        with open(f"{self.temp_path}/testfile1.txt", "w") as f:
            f.write("GM World")
        with open(f"{self.temp_path}/testfile2.txt", "w") as f:
            f.write("GM World")

        folder_walk = os.walk(
            self.temp_path, topdown=True, onerror=None, followlinks=False
        )
        _files = next(folder_walk)[2]
        first_file = _files[0]
        self.assertEqual(misc.get_first_filename_in_dir(self.temp_path), first_file)

    def test_get_first_filename_in_dir_no_file(self):
        self.assertRaises(
            FileNotFoundError,
            misc.get_first_filename_in_dir,
            self.temp_path,
        )

    def test_strtobool(self) -> None:
        with self.subTest("Test truthy values"):
            for value in [
                "y",
                "Y",
                "yes",
                "YES",
                "yEs",
                "t",
                "T",
                "true",
                "TRUE",
                "TrUe",
                "on",
                "ON",
                "oN",
                "1",
            ]:
                self.assertTrue(misc.strtobool(value))

        with self.subTest("Test falsy values"):
            for value in [
                "n",
                "N",
                "no",
                "NO",
                "nO",
                "f",
                "F",
                "false",
                "FALSE",
                "fAlSe",
                "off",
                "OFF",
                "oFF",
                "0",
            ]:
                self.assertFalse(misc.strtobool(value))

        with self.subTest("Test with incorrect types"):
            for value in ["", "test", True, 1, False, 0]:
                self.assertRaises(ValueError, misc.strtobool, value)

    def tearDown(self) -> None:
        Path(self.temp_path, "testfile1.txt").unlink(missing_ok=True)
        Path(self.temp_path, "testfile2.txt").unlink(missing_ok=True)
        self.temp_path.rmdir()


if __name__ == "__main__":
    unittest.main()
