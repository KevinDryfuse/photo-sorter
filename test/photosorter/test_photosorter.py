from test.PseudoDirEntry import PseudoDirEntry
from src.photosorter.main import *
from unittest.mock import patch, MagicMock
from datetime import date


class TestPhotoSorter:

    def test_get_date_taken__image_has_exif_information__return_valid_date(self, mocker):
        mocker.patch('src.photosorter.main.get_exif_date_time_original', MagicMock(return_value='2018:11:14 13:42:07'))

        pseudo_dir_entry = PseudoDirEntry('FILENAME.JPG', '/filepath/', False, None)
        result = get_date_taken(pseudo_dir_entry)
        assert result == date(2018, 11, 14)

    def test_get_date_taken__image_does_not_have_exif_information__return_valid_date(self, mocker):
        mocker.patch('src.photosorter.main.get_exif_date_time_original', MagicMock(return_value=None))
        mocker.patch('os.path.getctime', MagicMock(return_value=1544906140.43639))

        pseudo_dir_entry = PseudoDirEntry('FILENAME.JPG', '/filepath/', False, None)
        result = get_date_taken(pseudo_dir_entry)
        assert result == date(2018, 12, 15)

    def test_get_directories_to_scan__directories_are_found__return_list_of_directories(self, mocker):
        mocker.patch('os.path.isdir', MagicMock(return_value=True))
        mocker.patch('os.listdir', MagicMock(return_value=['dir1', 'dir1', 'dir3']))

        result = get_directories_to_scan('X:/dirname/test/')
        assert result == ['X:/dirname/test/dir1', 'X:/dirname/test/dir1', 'X:/dirname/test/dir3', 'X:/dirname/test/']

    def test_get_directories_to_scan__no_directories_found__return_only_root_directory(self, mocker):
        mocker.patch('os.path.isdir', MagicMock(return_value=False))
        mocker.patch('os.listdir', MagicMock(return_value=['dir1', 'dir1', 'dir3']))

        result = get_directories_to_scan('X:/dirname/test/')
        assert result == ['X:/dirname/test/']

    def test_get_files_in_directory__files_found__return_list_of_jpg_images_only(self, mocker):
        file_list = [
            PseudoDirEntry('FILE1.JPG', '/filepath\\FILE1.JPG', False, None),
            PseudoDirEntry('FILE2.TXT', '/filepath/', False, None),
            PseudoDirEntry('DIRECTORY', '/filepath/', True, None),
            PseudoDirEntry('FILE3.JPG', '/filepath/', False, None),
            PseudoDirEntry('file4.png', '/filepath/', False, None),
            PseudoDirEntry('file5.jpg', '/filepath/', False, None)
        ]
        mocker.patch('os.scandir', MagicMock(return_value=file_list))

        result = get_files_in_directory("directory_name")
        assert (result.__len__() == 3)
        for file in result:
            assert (file.name.lower().endswith('.jpg'))
            assert (not file.is_dir())

    def test_get_files_in_directory__no_files_found__return_empty_list(self, mocker):
        mocker.patch('os.scandir', MagicMock(return_value=[PseudoDirEntry('DIRECTORY', '/filepath/', True, None)]))

        result = get_files_in_directory("directory_name")
        assert (result.__len__() == 0)

    def test_create_target_directory__directory_does_not_exist__directory_created(self, mocker):
        mocker.patch('os.path.isdir', MagicMock(return_value=0))
        mocked_mkdir = mocker.patch("os.mkdir", MagicMock(return_value=True))

        directory_name = 'directory_name'

        create_target_directory(directory_name)
        assert(mocked_mkdir.call_count == 1)
        mocked_mkdir.assert_called_once_with(directory_name)

    def test_create_target_directory__directory_already_exists__directory_not_created(self, mocker):
        mocker.patch('os.path.isdir', MagicMock(return_value=1))
        mocked_mkdir = mocker.patch("os.mkdir", MagicMock(return_value=False))

        directory_name = 'directory_name'

        create_target_directory(directory_name)
        assert(mocked_mkdir.call_count == 0)

    def test_move_file__file_does_not_exist_in_target_directory__file_moved(self, mocker):
        mocker.patch('os.path.isfile', MagicMock(return_value=False))
        mocked_rename = mocker.patch("os.rename", MagicMock(return_value=True))

        file_path = '/filepath/FILE1.JPG'
        file_name = 'FILE1.JPG'
        file = PseudoDirEntry(file_name, file_path, False, None)
        directory_name = 'directory_name'

        move_file(directory_name, file)

        assert(mocked_rename.call_count == 1)
        mocked_rename.assert_called_once_with(file_path, directory_name + '\\' + file_name)

    def test_move_file__file_already_exists_in_target_directory__file_not_moved(self, mocker):
        mocker.patch('os.path.isfile', MagicMock(return_value=True))
        mocked_rename = mocker.patch("os.rename", MagicMock(return_value=True))

        file_path = '/filepath/FILE1.JPG'
        file_name = 'FILE1.JPG'
        file = PseudoDirEntry(file_name, file_path, False, None)
        directory_name = 'directory_name'

        move_file(directory_name, file)

        assert(mocked_rename.call_count == 0)
