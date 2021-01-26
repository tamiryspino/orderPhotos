import os
from datetime import datetime
import re
import logging
from os.path import join


def validate_date_prefix(date_prefix, formats, present):
    for format in formats:
        try:
            file_date = datetime.strptime(date_prefix, format)
            return file_date.date() < present.date()
        except Exception:
            pass
    logging.info(date_prefix + " is not a valid date to format "
                 + "for all formats or its in the future.")
    return False


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


def preview_rename_file(file, present):
    old_name = os.path.split(os.path.abspath(file))[1]
    new_name = format_name(old_name, present)
    return [old_name, new_name]


def preview_rename_all(files):
    present = datetime.now()
    new_names = []
    preview_renamed_files = []
    will_not_be_renamed = []
    for name in sorted(files):
        old_name, new_name = preview_rename_file(name, present)
        if new_name not in new_names:
            new_names.append(new_name)
            preview_renamed_files.append([old_name, new_name])
        else:
            will_not_be_renamed.append([old_name, new_name])
    return preview_renamed_files, will_not_be_renamed


def rename_file(file, final_path, present, old_name, new_name):
    # Only renames if the file begins with prefix+date_hour or prefix+date
    # and if a file with de same name already doesn't exists on destiny.
    try:
        formatted_path_file = os.path.join(final_path, new_name)
        if not (os.path.exists(formatted_path_file)):
            os.rename(file, formatted_path_file)
            logging.info("| " + old_name + " | " + new_name + " |")
            return new_name
        else:
            # TODO Compare metadata of files
            logging.error("Renamed file " + old_name + " already exists in destiny directory. Nothing to do.")
    except Exception as e:
        logging.info("| " + old_name + " | ERROR: " + str(e) + " |")
        logging.error(e)


def rename_all(directory, final_path, files):
    '''Renames the files, removing the prefix like "IMG_", "VID-" and
    format the new date with hyphens.
    '''
    files = sorted(files)
    preview_renamed_files, not_renamed_files = preview_rename_all(files)
    
    print('This files will not be renamed:')
    print(not_renamed_files)
    
    print('-------- This files will be renamed --------')
    print(*preview_renamed_files, sep='\n')
    answer = input('Do you like to rename this ' + str(len(preview_renamed_files)) + ' files?\
                    Type N for NO and any other for Yes.')

    if answer != 'N':
        logging.info("Renaming all files...")
        logging.info("|     Name     |      New Name     |")
        renamed_files = []

        present = datetime.now()
        for old_name, new_name in preview_renamed_files:
            renamed = rename_file(join(directory, old_name), final_path, present, old_name, new_name)
            if renamed:
                renamed_files.append(renamed)

        return renamed_files