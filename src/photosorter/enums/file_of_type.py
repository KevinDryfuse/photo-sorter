from enum import Enum


class FilesOfType(Enum):
    ALL_FILES = 'file'
    VALID_MEDIA = 'valid_media'
    NON_VALID_MEDIA = 'non_valid_media'
    FILES_AND_DIRECTORIES = 'all'
