from test.PseudoDirEntry import PseudoDirEntry
from src.photosorter.main import *
from unittest.mock import call, MagicMock
from datetime import date
import pytest


class TestPhotoSorter:

    def test_get_create_date__image_has_exif_information__return_valid_date(self, mocker):
        mocker.patch('src.photosorter.main.get_jpg_create_date', MagicMock(return_value=date(2018, 11, 14)))
        mocker.patch('magic.from_file', MagicMock(return_value='image/jpeg'))

        pseudo_dir_entry = PseudoDirEntry('FILENAME.JPG', '/filepath/FILENAME.JPG', False, None)
        result = get_create_date(pseudo_dir_entry)
        assert result == date(2018, 11, 14)

    def test_get_create_date__image_does_not_have_exif_information__return_valid_date(self, mocker):
        mocked_get_jpg_create_date = mocker.patch('src.photosorter.main.get_jpg_create_date')
        mocked_get_jpg_create_date.side_effect = KeyError()
        mocker.patch('src.photosorter.main.get_generic_create_date', MagicMock(return_value=date(2018, 12, 15)))
        mocker.patch('magic.from_file', MagicMock(return_value='image/jpeg'))

        pseudo_dir_entry = PseudoDirEntry('FILENAME.JPG', '/filepath/FILENAME.JPG', False, None)
        result = get_create_date(pseudo_dir_entry)
        assert result == date(2018, 12, 15)

    def test_listdir_nohidden__hidden_files_found__hidden_files_not_returned(self, mocker):
        mocker.patch('os.listdir', MagicMock(return_value=['dir1', '.hidden_dir', 'dir2']))
        root_directory = 'X:/dirname/test/'
        result = listdir_nohidden(root_directory)
        assert result == ['dir1', 'dir2']

    def test_get_directories_to_scan__add_root_directory__directories_are_found__return_list_of_directories(self,
                                                                                                            mocker):
        mocker.patch('os.path.isdir', MagicMock(return_value=True))
        mocker.patch('src.photosorter.main.listdir_nohidden', MagicMock(return_value=['dir1', 'dir1', 'dir3']))
        root_directory = 'X:/dirname/test/'

        result = get_directories_to_scan(root_directory, True)
        assert result == ['X:/dirname/test/dir1', 'X:/dirname/test/dir1', 'X:/dirname/test/dir3', root_directory]

    def test_get_directories_to_scan__add_root_directory__no_directories_found__return_only_root_directory(self,
                                                                                                           mocker):
        mocker.patch('os.path.isdir', MagicMock(return_value=False))
        mocker.patch('src.photosorter.main.listdir_nohidden', MagicMock(return_value=['dir1', 'dir1', 'dir3']))
        root_directory = 'X:/dirname/test/'

        result = get_directories_to_scan(root_directory, True)
        assert result == [root_directory]

    def test_get_directories_to_scan__do_not_add_root_directory__directories_are_found__return_list_of_directories_except_root_dir(
            self, mocker):
        mocker.patch('os.path.isdir', MagicMock(return_value=True))
        mocker.patch('src.photosorter.main.listdir_nohidden', MagicMock(return_value=['dir1', 'dir1', 'dir3']))

        result = get_directories_to_scan('X:/dirname/test/')
        assert result == ['X:/dirname/test/dir1', 'X:/dirname/test/dir1', 'X:/dirname/test/dir3']

    def test_get_directories_to_scan__do_not_add_root_directory__no_directories_found__return_empty_list(self, mocker):
        mocker.patch('os.path.isdir', MagicMock(return_value=False))
        mocker.patch('src.photosorter.main.listdir_nohidden', MagicMock(return_value=['dir1', 'dir1', 'dir3']))

        result = get_directories_to_scan('X:/dirname/test/')
        assert result == []

    def test_get_files_in_directory__valid_media__images_exist__return_list_of_images_only(self, mocker):
        file_list = [
            PseudoDirEntry('FILE1.JPG', '/filepath\\FILE1.JPG', False, None),
            PseudoDirEntry('DIRECTORY', '/filepath/', True, None),
            PseudoDirEntry('FILE2.JPG', '/filepath/', False, None),
            PseudoDirEntry('file3.jpg', '/filepath/', False, None),
            PseudoDirEntry('file4.jpg', '/filepath\\FILE6.JPG', True, None)
        ]
        mocker.patch('os.scandir', MagicMock(return_value=file_list))
        mocker.patch('magic.from_file', MagicMock(return_value='image/jpeg'))

        result = get_files_in_directory('directory_name')
        assert (result.__len__() == 3)
        for file in result:
            assert (file.name.lower().endswith('.jpg'))
            assert (not file.is_dir())

    def test_get_files_in_directory__valid_media__images_do_not_exist__return_empty_list(self, mocker):
        mocker.patch('os.scandir', MagicMock(return_value=[PseudoDirEntry('DIRECTORY', '/filepath/', True, None)]))
        mocker.patch('magic.from_file', MagicMock(return_value='image/jpeg'))

        result = get_files_in_directory('directory_name')
        assert (result.__len__() == 0)

    def test_get_files_in_directory__non_valid_media__non_valid_media_files_exist__return_list_of_non_images_only(self,
                                                                                                                  mocker):
        file_list = [
            PseudoDirEntry('FILE1.JPG', '/filepath\\FILE1.JPG', True, None),
            PseudoDirEntry('DIRECTORY', '/filepath/', True, None),
            PseudoDirEntry('FILE2.PNG', '/filepath\\FILE2.PNG', False, None)
        ]
        mocker.patch('os.scandir', MagicMock(return_value=file_list))
        mocker.patch('magic.from_file', MagicMock(return_value='image/png'))

        result = get_files_in_directory('directory_name', FilesOfType.NON_VALID_MEDIA)
        assert (result.__len__() == 1)
        for file in result:
            assert (file.name.lower().endswith('.png'))
            assert (not file.is_dir())

    def test_get_files_in_directory__non_valid_media__non_valid_media_files_do_not_exist__return_empty_list(self,
                                                                                                            mocker):
        mocker.patch('os.scandir', MagicMock(return_value=[PseudoDirEntry('DIRECTORY', '/filepath/', True, None)]))
        mocker.patch('magic.from_file', MagicMock(return_value='image/png'))

        result = get_files_in_directory('directory_name', FilesOfType.NON_VALID_MEDIA)
        assert (result.__len__() == 0)

    def test_get_files_in_directory__all_files__files_exist__return_list_of_non_images_only(self, mocker):
        file_list = [
            PseudoDirEntry('FILE1.JPG', '/filepath\\FILE1.JPG', False, None),
            PseudoDirEntry('FILE2.TXT', '/filepath/', False, None),
            PseudoDirEntry('DIRECTORY', '/filepath/', True, None),
            PseudoDirEntry('FILE3.JPG', '/filepath/', False, None),
            PseudoDirEntry('file4.png', '/filepath/', False, None),
            PseudoDirEntry('file5.jpg', '/filepath/', False, None),
            PseudoDirEntry('file6.jpg', '/filepath\\FILE6.JPG', True, None)
        ]
        mocker.patch('os.scandir', MagicMock(return_value=file_list))

        result = get_files_in_directory('directory_name', FilesOfType.ALL_FILES)
        assert (result.__len__() == 5)
        for file in result:
            assert (file.name.lower().endswith(('.png', '.txt', '.jpg')))
            assert (not file.is_dir())

    def test_get_files_in_directory__all_files__files_do_not_exist__return_empty_list(self, mocker):
        mocker.patch('os.scandir', MagicMock(return_value=[PseudoDirEntry('DIRECTORY', '/filepath/', True, None)]))

        result = get_files_in_directory('directory_name', FilesOfType.ALL_FILES)
        assert (result.__len__() == 0)

    def test_get_files_in_directory__all_files_and_directories__files_exist__return_list_of_non_images_only(self,
                                                                                                            mocker):
        file_list = [
            PseudoDirEntry('FILE1.JPG', '/filepath\\FILE1.JPG', False, None),
            PseudoDirEntry('FILE2.TXT', '/filepath/', False, None),
            PseudoDirEntry('DIRECTORY', '/filepath/', True, None),
            PseudoDirEntry('FILE3.JPG', '/filepath/', False, None),
            PseudoDirEntry('file4.png', '/filepath/', False, None),
            PseudoDirEntry('file5.jpg', '/filepath/', False, None),
            PseudoDirEntry('file6.jpg', '/filepath\\FILE6.JPG', True, None)
        ]
        mocker.patch('os.scandir', MagicMock(return_value=file_list))

        result = get_files_in_directory('directory_name', FilesOfType.FILES_AND_DIRECTORIES)
        assert (result.__len__() == 7)

    def test_create_target_directory__directory_does_not_exist__directory_created(self, mocker):
        mocker.patch('os.path.isdir', MagicMock(return_value=0))
        mocked_mkdir = mocker.patch('os.mkdir', MagicMock(return_value=True))

        directory_name = 'directory_name'

        create_target_directory(directory_name)
        assert (mocked_mkdir.call_count == 1)
        mocked_mkdir.assert_called_once_with(directory_name)

    def test_create_target_directory__directory_already_exists__directory_not_created(self, mocker):
        mocker.patch('os.path.isdir', MagicMock(return_value=1))
        mocked_mkdir = mocker.patch('os.mkdir', MagicMock(return_value=False))

        directory_name = 'directory_name'

        create_target_directory(directory_name)
        assert (mocked_mkdir.call_count == 0)

    def test_move_file__file_does_not_exist_in_target_directory__file_moved(self, mocker):
        mocker.patch('os.path.isfile', MagicMock(return_value=False))
        mocked_rename = mocker.patch('os.rename', MagicMock(return_value=True))

        file_path = '/filepath/FILE1.JPG'
        file_name = 'FILE1.JPG'
        file = PseudoDirEntry(file_name, file_path, False, None)
        directory_name = 'directory_name'

        move_file(directory_name, file)

        assert (mocked_rename.call_count == 1)
        mocked_rename.assert_called_once_with(file_path, directory_name + '\\' + file_name)

    def test_move_file__file_already_exists_in_target_directory__file_not_moved(self, mocker):
        mocker.patch('os.path.isfile', MagicMock(return_value=True))
        mocked_rename = mocker.patch('os.rename', MagicMock(return_value=True))

        file_path = '/filepath/FILE1.JPG'
        file_name = 'FILE1.JPG'
        file = PseudoDirEntry(file_name, file_path, False, None)
        directory_name = 'directory_name'

        move_file(directory_name, file)

        assert (mocked_rename.call_count == 0)

    def test_cleanup__empty_directories_are_found__directories_are_deleted(self, mocker):
        root_directory = 'X:/dirname/test/'
        directory_1 = 'X:/dirname/test/dir1/'
        directory_2 = 'X:/dirname/test/dir2/'
        directory_3 = 'X:/dirname/test/dir3/'

        directories = [directory_1, directory_2, directory_3, root_directory]
        mocker.patch('src.photosorter.main.get_directories_to_scan', MagicMock(return_value=directories))
        mocker.patch('src.photosorter.main.get_files_in_directory', MagicMock(return_value=[]))
        mocked_rmdir = mocker.patch('os.rmdir', MagicMock(return_value=True))
        calls = [call(directory_1), call(directory_2), call(directory_3), call(root_directory)]

        cleanup(root_directory)

        assert (mocked_rmdir.call_count == 4)
        mocked_rmdir.assert_has_calls(calls, any_order=True)

    def test_cleanup__no_empty_directories_are_found__no_directories_are_deleted(self, mocker):
        root_directory = 'X:/dirname/test/'
        directory_1 = 'X:/dirname/test/dir1/'
        directory_2 = 'X:/dirname/test/dir2/'
        directory_3 = 'X:/dirname/test/dir3/'

        directories = [directory_1, directory_2, directory_3, root_directory]
        mocker.patch('src.photosorter.main.get_directories_to_scan', MagicMock(return_value=directories))
        mocker.patch('src.photosorter.main.get_files_in_directory',
                     MagicMock(return_value=[PseudoDirEntry('DIRECTORY', '/filepath/', True, None)]))
        mocked_rmdir = mocker.patch('os.rmdir', MagicMock(return_value=True))

        cleanup(root_directory)

        assert mocked_rmdir.call_count == 0

    def test_get_directories__both_parameters_supplied__both_returned(self):
        arg1 = 'root_directory'
        arg2 = 'target_root_directory'
        root_directory, target_root_directory = get_directories(arg1, arg2)

        assert root_directory == arg1
        assert target_root_directory == arg2

    def test_get_directories__no_target_supplied__root_and_target_are_the_same(self):
        arg1 = 'root_directory'
        arg2 = None
        root_directory, target_root_directory = get_directories(arg1, arg2)

        assert root_directory == arg1
        assert target_root_directory == arg1

    def test_validate_directories_exist__root_directory_invalid__exception_thrown(self, mocker):
        mocker.patch('os.path.isdir', MagicMock(side_effect=[False, False]))
        root_directory = 'tst1'
        target_root_directory = 'tst2'
        with pytest.raises(Exception) as excinfo:
            validate_directories_exist(root_directory, target_root_directory)
        assert excinfo.value.args[0] == 'Source directory {0} does not exist!'.format(root_directory)

    def test_validate_directories_exist__target_root_directory_invalid__exception_thrown(self, mocker):
        mocker.patch('os.path.isdir', MagicMock(side_effect=[True, False]))
        root_directory = 'tst1'
        target_root_directory = 'tst2'
        with pytest.raises(Exception) as excinfo:
            validate_directories_exist(root_directory, target_root_directory)
        assert excinfo.value.args[0] == 'Target directory {0} does not exist!'.format(target_root_directory)

    def test_validate_directories_exist__all_directories_valied__exception_thrown(self, mocker):
        mocker.patch('os.path.isdir', MagicMock(side_effect=[True, True]))
        root_directory = 'tst1'
        target_root_directory = 'tst2'
        assert validate_directories_exist(root_directory, target_root_directory)

    def test_determine_target_directory_location__junk_flag_is_none__standard_directory_created(self):
        target_root_directory = 'X:/test'
        target_directory = determine_target_directory_location(target_root_directory, date(2007, 6, 16))
        assert (target_directory == 'X:/test\\2007-06-16')

    def test_determine_target_directory_location__junk_flag_is_true__junk_directory_created(self, mocker):
        mocker.patch('src.photosorter.main.create_target_directory', MagicMock(return_value=True))
        target_root_directory = 'X:/test'
        target_directory = determine_target_directory_location(target_root_directory, date(2007, 6, 16), True)
        assert (target_directory == 'X:/test\\JUNK/\\2007-06-16')

    # TODO: Tests needed for process_images() and process_junk()
    # TODO: What video format does our digital camera produce by default?  might be helpful to know.
