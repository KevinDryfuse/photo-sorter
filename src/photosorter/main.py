__author__ = 'github.com/kevindryfuse'
import sys
import os
from PIL import Image
from datetime import datetime
from src.photosorter.enums.file_of_type import *

def get_exif_date_time_original(file):
    try:
        date_time_original = Image.open(file.path)._getexif()[36867]
    except KeyError:
        date_time_original = None

    return date_time_original


def get_directories_to_scan(root_directory):
    child_directories = [os.path.join(root_directory, name) for name in os.listdir(root_directory)
                         if os.path.isdir(os.path.join(root_directory, name))]
    child_directories.append(root_directory)
    return child_directories


# TODO: Allow user to pass in a tuple of "image" extensions instead of hard-coding
# TODO: There has to be a way to not need to have basically the same exact code three times?!
def get_files_in_directory(scan_directory, files_of_type = FilesOfType.IMAGES):
    if files_of_type is FilesOfType.NON_IMAGES:
        files = [f for f in os.scandir(scan_directory)
                 if (not f.name.lower().endswith('.jpg') and f.is_dir() is False)]
    elif files_of_type is FilesOfType.IMAGES:
        files = [f for f in os.scandir(scan_directory)
                 if (f.name.lower().endswith('.jpg') and f.is_dir() is False)]
    else:
        files = [f for f in os.scandir(scan_directory)
                 if (f.is_dir() is False)]

    return files


def get_date_taken(file):
    exif_date_time_original = get_exif_date_time_original(file)

    if exif_date_time_original is None:
        date_photo_taken = datetime.fromtimestamp(os.path.getctime(file.path)).date()
    else:
        date_photo_taken = datetime.strptime(exif_date_time_original, '%Y:%m:%d %H:%M:%S').date()

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


def process_images(root_dir):
    dirs_to_scan = get_directories_to_scan(root_dir)

    for current_dir in dirs_to_scan:

        print("Scanning for images in: " + current_dir)

        images = get_files_in_directory(current_dir)

        for image in images:

            date_photo_taken = get_date_taken(image)

            target_directory = root_dir + '\\' + str(date_photo_taken.date())

            create_target_directory(target_directory)

            move_file(target_directory, image)


def process_junk(root_dir):
    dirs_to_scan = get_directories_to_scan(root_dir)

    for current_dir in dirs_to_scan:

        print("Scanning for images in: " + current_dir)

        files = get_files_in_directory(current_dir, False)

        for file in files:

            date_file_created = get_date_taken(file)

            target_directory = root_dir + 'JUNK\\' + str(date_file_created.date())

            create_target_directory(target_directory)

            move_file(target_directory, file)


def cleanup(root_directory):
    return False


if __name__ == "__main__":
    root_dir = sys.argv[1]

    print("Root directory to scan: " + str(root_dir))

    process_images()

    process_junk()

    cleanup()

    # TODO: If directory is empty after file is moved, delete the directory (maybe a post run cleanup?)
