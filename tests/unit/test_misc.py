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

    def tearDown(self) -> None:
        Path(self.temp_path, "testfile1.txt").unlink(missing_ok=True)
        Path(self.temp_path, "testfile2.txt").unlink(missing_ok=True)
        self.temp_path.rmdir()


if __name__ == "__main__":
    unittest.main()
