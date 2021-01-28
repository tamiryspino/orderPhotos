from datetime import datetime
import logging
from os.path import join, split
from rename_file import rename_all
from create_dirs import create_dir, create_dirs_and_move
from search_files import search_images, search_videos


def do_refactoring(directory, final_directory, files, qnt_files):
    '''Renames files removing prefix and formatting with date prefix. Moves the
    renamed files to the final_directory and in that directory group the files
    with same prefix into a new path named with this prefix.
    '''

    logging.info('Renaming and moving files...')
    renamed_files = rename_all(directory, final_directory, files)

    if renamed_files:
        files = sorted(renamed_files)
        create_dirs_and_move(qnt_files, files, final_directory)
    else:
        answer = input('Theres no renamed files, \
                        do you like to create folders? Type N for NO or \
                        any other to YES.')
        if answer != 'N' or answer != 'n':
            file_names = [split(file)[1] for file in files]
            files = sorted(file_names)
            # TODO Move unnamed files to final directory
            create_dirs_and_move(qnt_files, files, directory)


if __name__ == "__main__":
    directory = input("Type a directory to be evaluated."
                      + " Ex.: /home/seuNome/Images\n")
    
    final_directory = input("Type a directory to send the results."
                            + " Ex.: /home/seuNome/Images/Organized\n")
    
    qnt_files = input("How many files must exist with the same prefix"
                      + " to group in a directory?\n")
    if not qnt_files:
        qnt_files = 3

    logging.basicConfig(filename=join(directory,
                                      datetime.now()
                                      .strftime("%Y-%m-%d_%H-%M-%S")
                                      + '_order_photos.md'),
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)

    create_dir(final_directory)

    logging.info('Started')

    images = search_images(directory)
    if images:
        do_refactoring(directory, final_directory, images, qnt_files)

    videos = search_videos(directory)
    if videos:
        do_refactoring(directory, final_directory, videos, qnt_files)

    logging.info('Finished')

# TODO
# 7 - Comparar metadados
