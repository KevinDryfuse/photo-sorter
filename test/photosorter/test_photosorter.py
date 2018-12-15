from test.PseudoDirEntry import PseudoDirEntry
from src.photosorter.main import *
from unittest.mock import patch, MagicMock
from datetime import date


class TestPhotoSorter:

    @patch("src.photosorter.main.get_exif_date_time_original", MagicMock(return_value='2018:11:14 13:42:07'))
    def test_get_date_taken__image_has_exif_information__return_valid_date(self):
        pseudo_dir_entry = PseudoDirEntry('FILENAME.JPG', '/filepath/', False, None)
        result = get_date_taken(pseudo_dir_entry)
        assert result == date(2018, 11, 14)

    @patch("src.photosorter.main.get_exif_date_time_original", MagicMock(return_value=None))
    @patch("os.path.getctime", MagicMock(return_value=1544906140.43639))
    def test_get_date_taken__image_does_not_have_exif_information__return_valid_date(self):
        pseudo_dir_entry = PseudoDirEntry('FILENAME.JPG', '/filepath/', False, None)
        result = get_date_taken(pseudo_dir_entry)
        assert result == date(2018, 12, 15)

    @patch("os.path.isdir", MagicMock(return_value=True))
    @patch("os.listdir", MagicMock(return_value=['dir1', 'dir1', 'dir3']))
    def test_get_directories_to_scan__directories_are_found__return_list_of_directories(self):
        result = get_directories_to_scan('X:/dirname/test/')
        assert result == ['X:/dirname/test/dir1', 'X:/dirname/test/dir1', 'X:/dirname/test/dir3', 'X:/dirname/test/']

    @patch("os.path.isdir", MagicMock(return_value=False))
    @patch("os.listdir", MagicMock(return_value=['dir1', 'dir1', 'dir3']))
    def test_get_directories_to_scan__no_directories_found__return_only_root_directory(self):
        result = get_directories_to_scan('X:/dirname/test/')
        assert result == ['X:/dirname/test/']
