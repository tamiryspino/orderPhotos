import os
from datetime import datetime
import logging
import pandas as pd
from os.path import join, exists, isfile


def create_dir(final_path):
    '''Creates a new directory if it don't already exists.
    '''

    if not exists(final_path):
        os.makedirs(final_path)
        logging.info("Created new dir: " + final_path)
    else:
        logging.info("Directory " + final_path + " already exists!")


def group_by_date(pd_files):
    '''Group the files on the data frame based on the first 10 characters.
    '''

    return pd_files['Name'].str.replace(r'(.{10})(.*)', lambda m: m.group(1))


def do_dict_by_date(images):
    '''Returns a data frame with keys Name (the name of the file)
    and Date (the prefix date of the file).
    '''

    photos = pd.DataFrame(images, columns=['Name'])
    photos['Date'] = group_by_date(photos)
    # TODO Return just groups with more than given qnt_files
    return photos


def move_files(files, directory, new_dir, ignored_dir):
    '''Move the given list of files of the given directory to a new directory,
    If a file with the same name already exists in the new directory than the
    file goes to a ignored_dir.
    '''

    success = 0
    ignored_files = 0
    total_not_moved = 0

    for file in files:
        path_file = join(directory, file)
        if (isfile(path_file)):
            try:
                new_path_file = join(new_dir, file)
                if not (os.path.exists(new_path_file)):
                    os.rename(path_file, new_path_file)
                    success += 1
                else:
                    logging.error("File " + file + " already exists in"
                                  + " directory. Moving to ignored directory.")
                    create_dir(ignored_dir)
                    os.rename(path_file, join(ignored_dir, file))
                    ignored_files += 1
            except Exception as e:
                logging.error(e)
                total_not_moved += 1

    logging.info(str(success) + "/" + str(len(files))
                 + " files moved to " + new_dir)

    if ignored_files > 0:
        logging.info(str(ignored_files) + " already exists in directory, "
                     + "moved to ignored path.")
    if total_not_moved > 0:
        logging.info("An error ocurred moving " + str(total_not_moved)
                     + " files.")

    return success


def create_dirs_and_move(qnt_files, images, directory):
    '''Create a dirs if a group of qnt_files exists with the same prefix.
    The name of the dir is the prefix. After that, move the files to that dir.
    Files that have the same of other existing in the destiny directory go to
    a dir named '(today) ignored'.
    '''

    logging.info("Creating dict by date...")
    photos = do_dict_by_date(images)
    photos['Date'] = group_by_date(photos)
    date_dict = photos['Date'].value_counts().to_dict()

    logging.info(photos['Date'].value_counts().to_string())

    total_moved = 0
    total_not_moved = 0

    logging.info("Moving files to a specific directory by file prefix...")
    ignored_dir = join(directory, str(datetime.now()) + " Ignored")
    for key in date_dict:
        new_dir = join(directory, key)

        if date_dict[key] >= qnt_files:
            create_dir(new_dir)
            files = photos.loc[photos['Date'] == key]

            success = move_files(files['Name'],
                                 directory,
                                 new_dir,
                                 ignored_dir)

            total_moved += success
        else:
            total_not_moved += date_dict[key]

    logging.info(str(total_moved) + " files moved to a directory.")
    logging.info(str(total_not_moved) + " files not moved to a directory.")
