import shutil
import unittest

from munge.download_data import download_extract_file


class TestDownloadExtractData(unittest.TestCase):
    def test_download_extract_file_success(self):
        year, month = 2018, 1
        res = download_extract_file(year, month)
        assert res == 0
        shutil.rmtree('2018_1')

    def test_download_extract_file_fail(self):
        year, month = 2015, 1
        res = download_extract_file(year, month)
        assert res != 0


if __name__ == '__main__':
    unittest.main()
