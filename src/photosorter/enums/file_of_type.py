from enum import Enum


class FilesOfType(Enum):
    ALL_FILES = 'file'
    IMAGES = 'images'
    NON_IMAGES = 'non'
    FILES_AND_DIRECTORIES = 'all'
