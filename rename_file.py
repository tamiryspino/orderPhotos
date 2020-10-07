import os
from datetime import datetime
import re
import logging


def validate_date_prefix(date_prefix, formats, present):
    for format in formats:
        try:
            file_date = datetime.strptime(date_prefix, format)
            return file_date.date() < present.date()
        except Exception:
            logging.error(date_prefix + " is not a valid date to format "
                          + format)
    logging.info(date_prefix + " is not a valid date to format "
                 + "for all formats or its in the future.")


def match_to_rename(reg, re_subs, re_date, file_name, formats, present):
    if re.match(reg, file_name):
        date_prefix = re.sub(reg, re_date, file_name)
        if validate_date_prefix(date_prefix, formats, present):
            return re.sub(reg, re_subs, file_name)


def format_name(file_name, present):
    '''Returns formated name if matches to a date or None

    Parameters:
        file_name (str): The name of the file to be renamed
        present (datetime): The date on which the name cannot pass. Ex.: today

    Returns:
        formatted_name (str): A new str, formatted like '%Y-%m-%d_%H-%M-%S' if
        the initial name contains date and hour or '%Y-%m-%d' if it just
        constains date or None if does not match
    '''

    # File name can contain prefix (ex: IMG, VID_)
    prefix = r"^(IMG|VID|Screenshot(\ from)?|InShot|PANO)?"
    # File name should have a valid date (%Y-%m-%d or %Y%m%d)
    date = r"(_|-|\ )?(\d{4})-?(\d{2})-?(\d{2})"
    # File name can contain suffix for date hours (ex: _293823)
    hour = r"(_|-|\ )?(\d{2})-?(\d{2})-?(\d{2})"
    # Suffix of file name and ext.
    suffix = r"(.*)?"

    date_hour_formats = ['%Y-%m-%d_%H-%M-%S',
                         '%Y-%m-%d-%H-%M-%S',
                         '%Y-%m-%d %H-%M-%S']
    formatted_name = match_to_rename(reg=prefix+date+hour+suffix,
                                     re_subs=r"\4-\5-\6_\8-\9-\10\11",
                                     re_date=r"\4-\5-\6_\8-\9-\10",
                                     file_name=file_name,
                                     formats=date_hour_formats,
                                     present=present)

    # If the file name don't contain date and hour, it can contain only date
    if not formatted_name:
        formatted_name = match_to_rename(reg=prefix+date+suffix,
                                         re_subs=r"\4-\5-\6\7",
                                         re_date=r"\4-\5-\6",
                                         file_name=file_name,
                                         formats=['%Y-%m-%d'],
                                         present=present)

    # If not formatted both on date and hour or just date, it will be None
    return formatted_name


def rename_file(file, final_path, present):
    file_name = os.path.split(os.path.abspath(file))[1]

    formatted_name = format_name(file_name, present)

    # Only renames if the file begins with prefix+date_hour or prefix+date
    # and if a file with de same name already doesn't exists on destiny.
    if formatted_name:
        # TODO extract to method
        try:
            formatted_path_file = os.path.join(final_path, formatted_name)
            if not (os.path.exists(formatted_path_file)):
                os.rename(file, formatted_path_file)
                logging.info("| " + file_name + " | " + formatted_name + " |")
                return formatted_name
            else:
                # TODO Compare metadata of files
                logging.error("Renamed file " + file_name
                              + " already exists in destiny directory.\
                              Nothing to do.")
        except Exception as e:
            logging.info("| " + file_name + " | ERROR: " + e + " |")
            logging.error(e)


def rename_all(path, files):
    '''Renames the files, removing the prefix like "IMG_", "VID-" and
    format the new date with hyphens.
    '''
    logging.info("Renaming all files...")
    logging.info("|     Name     |      New Name     |")
    renamed_files = []

    present = datetime.now()
    for name in sorted(files):
        new_name = rename_file(name, path, present)
        if new_name:
            renamed_files.append(new_name)

    return renamed_files
