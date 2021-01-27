from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
from search_files import search_images
from os.path import join
from datetime import datetime
import logging


def get_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image._getexif()


def get_labeled_exif(exif):
    labeled = {}
    for (key, val) in exif.items():
        labeled[TAGS.get(key)] = val

    return labeled


def get_gps_info(exif):
    return get_labeled_exif(exif)['GPSInfo']


def get_geotagging(gps_info):
    if not gps_info:
        raise ValueError("No EXIF geotagging found.")

    geotagging = {}
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
    exif = get_exif(file)
    print(file)
    gps_info = get_gps_info(exif)
    geotags = get_geotagging(gps_info)
    return get_coordinates(geotags)


def remove_entries(the_dict):
    # TODO Move this entries to a configuration file
    entries = ['quarter', 'town', 'suburb', 'city', 'city_district',
               'municipality', 'county', 'region', 'postcode', 'country',
               'country_code', 'city_district', 'city_block', 'neighborhood',
               'state', 'state_district', 'residential', 'village']

    SKIP_CITIES = [{'country': 'Sverige', 'town': 'Sollentuna'},
                   {'country': 'Brasil', 'state': 'Alagoas', 'city': 'Maceió'}]

    for city in SKIP_CITIES:
        if not all(item in the_dict.items() for item in city.items()):
            for key in city.keys():
                entries.remove(key)

    for key in entries:
        if key in the_dict:
            del the_dict[key]

    return the_dict


def reverse_geocoding(coordinates):
    locator = Nominatim(user_agent="myGeocoder")
    try:
        location = locator.reverse(coordinates)
        address = location.raw['address']
        return remove_entries(address)
    except Exception as e:
        logging.error(e, coordinates)


def get_remove_key(key, the_dict):
    value = ''
    if key in the_dict.keys():
        value += the_dict.get(key) + ', '
        del the_dict[key]
    return value[:-2], the_dict


def format_address(address):
    # TODO Configure
    initial_address = ''
    initial_entries = ['country', 'state', 'city', 'town']
    for entry in initial_entries:
        part_address, address = get_remove_key(entry, address)
        initial_address += part_address

    road = ''
    final_entries = ['road', 'house_number']
    for entry in final_entries:
        part_address, address = get_remove_key(entry, address)
        road += part_address

    place_name = ''
    for key, value in address.items():
        place_name += value + ', '

    final_address = ''
    if initial_address != '':
        final_address += initial_address + ' - '

    if place_name != '':
        final_address += place_name[:-2]
    else:
        final_address += road
    return final_address


if __name__ == "__main__":
    directory = input("Type the path to be evaluated. Ex.: /home/"
                      + "yourName/Images/Camera\n")
    if not directory:
        directory = "/home/xxxx/Images/Camera"

    logging.basicConfig(filename=join(directory, str(datetime.now())
                                      + '_geocoding.csv'),
                        format='%(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)

    images = search_images(directory)
    if images:
        for image in sorted(images):
            # logging.info(image + ",")
            coord = get_coordinates_from_exif(join(directory, image))
            if coord:
                address = reverse_geocoding(coord)
                if address:
                    address = format_address(address)
                logging.info(address)
