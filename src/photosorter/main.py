__author__ = 'github.com/kevindryfuse'
import sys
import os
from PIL import Image
from datetime import datetime
from src.photosorter.enums.file_of_type import *
import magic

VALID_MIME_TYPES = ['video/quicktime', 'image/jpeg', 'application/vnd.apple.photos', 'text/xml']


def get_directories_to_scan(root_directory, add_root_directory_to_list=False):
    child_directories = [os.path.join(root_directory, name) for name in os.listdir(root_directory)
                         if os.path.isdir(os.path.join(root_directory, name))]

    if add_root_directory_to_list:
        child_directories.append(root_directory)

    return child_directories


def get_files_in_directory(scan_directory, files_of_type=FilesOfType.VALID_MEDIA):
    if files_of_type is FilesOfType.NON_VALID_MEDIA:
        files = [f for f in os.scandir(scan_directory)
                 if (not magic.from_file(f.path, mime=True) in tuple(VALID_MIME_TYPES) and f.is_dir() is False)]
    elif files_of_type is FilesOfType.VALID_MEDIA:
        files = [f for f in os.scandir(scan_directory)
                 if (magic.from_file(f.path, mime=True) in tuple(VALID_MIME_TYPES) and f.is_dir() is False)]
    elif files_of_type is FilesOfType.FILES_AND_DIRECTORIES:
        files = [f for f in os.scandir(scan_directory)]
    else:
        files = [f for f in os.scandir(scan_directory)
                 if (f.is_dir() is False)]

    return files


def get_exif_time_original(file):
    return Image.open(file.path)._getexif()[36867]


def get_jpg_create_date(file):
    try:
        exif_date_time_original = get_exif_time_original(file)
        create_date = datetime.strptime(exif_date_time_original, '%Y:%m:%d %H:%M:%S').date()
    except TypeError:
        create_date = get_generic_create_date(file)

    return create_date


def get_generic_create_date(file):
    return datetime.fromtimestamp(os.path.getmtime(file.path)).date()


def get_create_date(file):

    mime_type = magic.from_file(file.path, mime=True)

    try:
        if mime_type == 'image/jpeg':
            date_photo_taken = get_jpg_create_date(file)
        elif mime_type in VALID_MIME_TYPES:
            date_photo_taken = get_generic_create_date(file)
        else:
            print('File {0}: mime type {1} is not supported media type!').format(file.path, mime_type)
            raise NotImplementedError('Special logic not implemented for this mime type')
    except (KeyError, OSError, AttributeError, NotImplementedError):
        date_photo_taken = get_generic_create_date(file)

    return date_photo_taken


def create_target_directory(target_directory):
    if os.path.isdir(target_directory) == 0:
        os.mkdir(target_directory)
        print('Created directory: ' + target_directory)


def move_file(target_directory, file):
    if os.path.isfile(target_directory + '\\' + file.name):
        print('file ' + file.name + ' already exists')
    else:
        os.rename(file.path, target_directory + '\\' + file.name)


def process_media(root_directory, target_root_directory):
    print('Processing media files')
    directories_to_scan = get_directories_to_scan(root_directory)

    for current_directory in directories_to_scan:

        print("Scanning for images in: " + current_directory)

        images = get_files_in_directory(current_directory)

        for image in images:
            date_photo_taken = get_create_date(image)

            target_directory = target_root_directory + '\\' + str(date_photo_taken)

            create_target_directory(target_directory)

            move_file(target_directory, image)


def process_junk(root_directory, target_root_directory):
    print('Processing non media files')
    directories_to_scan = get_directories_to_scan(root_directory)

    for current_directory in directories_to_scan:

        print("Scanning for images in: " + current_directory)

        files = get_files_in_directory(current_directory, FilesOfType.NON_VALID_MEDIA)

        for file in files:
            date_file_created = get_create_date(file)

            junk_directory = target_root_directory + '\\JUNK/'

            create_target_directory(junk_directory)

            target_directory = junk_directory + '\\' + str(date_file_created)

            create_target_directory(target_directory)

            move_file(target_directory, file)


def cleanup(root_directory):
    print('Cleaning empty directories')
    directories_to_scan = get_directories_to_scan(root_directory)

    for current_directory in directories_to_scan:

        print("Attempting to clean: " + current_directory)

        files = get_files_in_directory(current_directory, FilesOfType.FILES_AND_DIRECTORIES)

        if files.__len__() == 0:
            os.rmdir(current_directory)
        else:
            print("There are still files in this directory and it cannot be cleaned!")


# Validate that the directories actually exist
def get_directories(args):

    if args.__len__() == 1:
        raise Exception('Root directory parameter not supplied.')
    elif args.__len__() == 2:
        root_directory = args[1]
        target_root_directory = root_directory
    elif args.__len__() >= 3:
        root_directory = args[1]
        target_root_directory = args[2]

    return root_directory, target_root_directory


def validate_directories_exist(root_directory, target_root_directory):
    if not os.path.isdir(root_directory):
        raise Exception('Source directory {0} does not exist!'.format(root_directory))
    if not os.path.isdir(target_root_directory):
        raise Exception('Target directory {0} does not exist!'.format(target_root_directory))

    return True


if __name__ == "__main__":

    root_directory, target_root_directory = get_directories(sys.argv)

    print("Root directory to scan: " + str(root_directory))
    print("Root directory to scan: " + str(root_directory))

    process_media(root_directory, target_root_directory)

    process_junk(root_directory, target_root_directory)

    cleanup(root_directory)

