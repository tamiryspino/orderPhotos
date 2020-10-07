import os
from datetime import datetime
import logging
from os.path import isfile, join
from rename_file import rename_all
from create_dirs import create_dir, create_dirs_and_move


def search(type, valid_ext, directory):
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
    valid_images_ext = [".jpeg", ".jpg", ".gif", ".exif", ".png",
                        ".tga", ".tiff", ".bmp", ".svg"]
    return search('images', valid_images_ext, directory)


def search_videos(directory):
    valid_videos_ext = [".mkv", ".flv", ".avi", ".wmv", ".rmvb",
                        ".mp4", ".mpeg", ".3gp", ".mpg"]
    return search('videos', valid_videos_ext, directory)


def do_refactoring(final_directory, files):
    logging.info('Renaming and moving files...')
    renamed_files = rename_all(final_directory, files)

    if renamed_files:
        files = sorted(renamed_files)
        create_dirs_and_move(3, files, final_directory)


if __name__ == "__main__":
    directory = input("Type a directory to be evaluated.\
                      Ex.: /home/seuNome/Images\n")
    final_directory = input("Type a directory to send the results.\
                            Ex.: /home/seuNome/Images/Organized\n")

    logging.basicConfig(filename=join(directory, str(datetime.now())
                                      + '_order_photos.md'),
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)

    create_dir(final_directory)

    logging.info('Started')

    images = search_images(directory)
    if images:
        do_refactoring(final_directory, images)

    videos = search_videos(directory)
    if videos:
        do_refactoring(final_directory, videos)

    logging.info('Finished')

    # diffDates = getDiffDateMod(regex, arquivosPasta, directory)

# TODO
# 6 - Perguntar quantidade de arquivos para poder agrupar em pasta
# 7 - Comparar metadados
