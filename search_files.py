import os
import logging
from os.path import isfile, join


def search(type, valid_ext, directory):
    '''Returns a list of the type of files given the list of valid extensions
    of these files in the given directory.
    '''

    logging.info('Searching for ' + type + '...')
    files = []
    for file in os.listdir(directory):
        ext = os.path.splitext(file)[1]
        if isfile(join(directory, file)):
            if ext.lower() in valid_ext:
                files.append(join(directory, file))
            else:
                logging.warning("File not added to the list: " + file)
    logging.info(str(len(files)) + " " + type + " found.")

    return files


def search_images(directory):
    '''Returns a list of images in the given directory. The images must have a
    specific extensions given a list.
    '''

    valid_images_ext = [".jpeg", ".jpg", ".gif", ".exif", ".png",
                        ".tga", ".tiff", ".bmp", ".svg"]
    return search('images', valid_images_ext, directory)


def search_videos(directory):
    '''Returns a list of videos in the given directory. The videos must have a
    specific extensions given a list.
    '''

    valid_videos_ext = [".mkv", ".flv", ".avi", ".wmv", ".rmvb",
                        ".mp4", ".mpeg", ".3gp", ".mpg"]
    return search('videos', valid_videos_ext, directory)
