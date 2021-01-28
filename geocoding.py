from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
from search_files import search_images
from os.path import join
from datetime import datetime
import logging


def get_exif(filename):
    try:
        image = Image.open(filename)
        image.verify()
        return image._getexif()
    except Exception as e:
        logging.error(e)


def get_labeled_exif(exif):
    try:
        labeled = {}
        for (key, val) in exif.items():
            labeled[TAGS.get(key)] = val
        return labeled
    except Exception as e:
        logging.error(e)


def get_gps_info(exif):
    try:
        return get_labeled_exif(exif)['GPSInfo']
    except Exception as e:
        logging.error(e)


def get_geotagging(gps_info):
    geotagging = {}
    if not gps_info:
        logging.error("No EXIF geotagging found.")
        return geotagging

    for (key, val) in GPSTAGS.items():
        if key in gps_info:
            geotagging[val] = gps_info[key]

    return geotagging


def get_decimal_from_dms(dms, ref):
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1] / 60.0
    seconds = dms[2][0] / dms[2][1] / 3600.0

    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return round(degrees + minutes + seconds, 5)


def get_coordinates(geotags):
    valid_tags = ['GPSLatitude', 'GPSLatitudeRef',
                  'GPSLongitude', 'GPSLongitudeRef']
    if not all(key in geotags.keys() for key in valid_tags):
        # logging.info("Necessary geotag not found.")
        return

    lat = get_decimal_from_dms(geotags['GPSLatitude'],
                               geotags['GPSLatitudeRef'])
    lon = get_decimal_from_dms(geotags['GPSLongitude'],
                               geotags['GPSLongitudeRef'])

    return str(lat) + ", " + str(lon)


def get_coordinates_from_exif(file):
    logging.info('Analising ' + file)
    exif = get_exif(file)
    if exif:
        gps_info = get_gps_info(exif)
        geotags = get_geotagging(gps_info)
        return get_coordinates(geotags)


def reverse_geocoding(coordinates):
    locator = Nominatim(user_agent="myGeocoder")
    try:
        location = locator.reverse(coordinates, timeout=None, language='en')
        address = location.raw['address']
        return address
    except Exception as e:
        logging.error(e, coordinates)


def get_remove_key(key, the_dict):
    value = ''
    if key in the_dict.keys():
        value += the_dict.get(key) + ', '
        del the_dict[key]
    return value[:-2], the_dict


def remove_words(final_name):
    return final_name.replace(' kommun', '').replace(' County', '')


def format_address(address):
    # TODO Configure
    initial_address = ''
    initial_entries = [['country'],
                       ['county', 'state'],
                       ['city', 'town', 'city_district', 'municipality']]

    keys = address.keys()
    for entry in initial_entries:
        for division in entry:
            if division in keys:
                initial_address += address[division] + ', '
                break

    initial_address = remove_words(initial_address)
    secondary_entries = ['amenity', 'historic', 'tourism', 'highway',
                         'railway', 'shop', 'office', 'village', 'hamlet',
                         'building', 'leisure', 'farm', 'road']

    place_name = ''
    for entry in secondary_entries:
        if entry in keys:
            place_name += address[entry]
            break

    if place_name != '':
        return initial_address + place_name
    return rreplace(initial_address, ', ', '', 1)


def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def get_file_address(file, directory):
    coord = get_coordinates_from_exif(join(directory, file))
    if coord:
        address = reverse_geocoding(coord)
        if address:
            address = format_address(address)
        return address


def get_multiple_addresses(directory, files):
    addresses = {}
    for file in sorted(files):
        file_address = get_file_address(directory, file)
        addresses[file_address] = addresses.get(file_address, 0) + 1
    return sorted(addresses.items(), key=lambda item: item[1], reverse=True)


if __name__ == "__main__":
    directory = input("Type the path to be evaluated. Ex.: "
                      + "/home/user/Camera\n")
    if not directory:
        directory = "/home/xxxx/Images/Camera"

    logging.basicConfig(filename=join(directory,
                                      datetime.now().
                                      strftime("%Y-%m-%d_%H-%M-%S")
                                      + '_geocoding.csv'),
                        format='%(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)

    # TODO only images?
    images = search_images(directory)
    if images:
        get_multiple_addresses(directory, images)
