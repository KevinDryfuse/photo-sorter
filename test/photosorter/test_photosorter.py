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
