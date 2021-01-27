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
    degrees = dms[0]
    minutes = dms[1] / 60.0
    seconds = dms[2] / 3600.0

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
    gps_info = get_gps_info(exif)
    geotags = get_geotagging(gps_info)
    return get_coordinates(geotags)


def reverse_geocoding(coordinates):
    locator = Nominatim(user_agent="myGeocoder")
    location = locator.reverse(coordinates, timeout=None)
    return location.raw


if __name__ == "__main__":
    directory = input("Type the path to be evaluated. Ex.: /home/"
                      + "yourName/Images/Camera\n")
    if not directory:
        directory = "/home/xxxx/Imagens/Camera"


    logging.basicConfig(filename=join(directory, datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '_geocoding.csv'),
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
                logging.info(address)
