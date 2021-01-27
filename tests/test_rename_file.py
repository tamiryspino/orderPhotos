import unittest
from datetime import datetime, timedelta
from rename_file import format_name, validate_date_prefix, preview_rename_all


class Test_MatchFiles(unittest.TestCase):
    def setUp(self):
        self.present = datetime.now()
        self.date_hour_formats = ['%Y-%m-%d_%H-%M-%S',
                                  '%Y-%m-%d-%H-%M-%S',
                                  '%Y-%m-%d %H-%M-%S']

    def test_match_img_date(self):  # WA0024 should stay
        self.assertEqual(format_name('IMG-20181209-WA0024', self.present),
                         '2018-12-09-WA0024')

    def test_match_vid_date(self):  # WA0021 should stay
        self.assertEqual(format_name('VID-20181211_WA0021', self.present),
                         '2018-12-11_WA0021')

    def test_match_img_datetime(self):
        self.assertEqual(format_name('IMG_20190621_234458', self.present),
                         '2019-06-21_23-44-58')

    def test_match_vid_datetime(self):
        self.assertEqual(format_name('VID_20200316-115501', self.present),
                         '2020-03-16_11-55-01')

    def test_match_screenshot_datetime(self):
        self.assertEqual(format_name('Screenshot_20191021-132842',
                                     self.present),
                         '2019-10-21_13-28-42')

    def test_match_pano_datetime(self):
        self.assertEqual(format_name('PANO-20200316 115501', self.present),
                         '2020-03-16_11-55-01')

    def test_match_vid_datetimesec(self):  # 009 should stay
        self.assertEqual(format_name('VID_20170811_014054_009', self.present),
                         '2017-08-11_01-40-54_009')

    def test_match_img_datetimesec(self):  # 096 should leave (BURST)
        self.assertEqual(format_name('IMG-20181227_194407_096', self.present),
                         '2018-12-27_19-44-07_096')

    def test_match_no_prefix_datetime(self):
        self.assertEqual(format_name('20200316_115501', self.present),
                         '2020-03-16_11-55-01')

    def test_match_no_prefix_date(self):  # WA0024 should leave
        self.assertEqual(format_name('20181209-WA0024', self.present),
                         '2018-12-09-WA0024')

    def test_match_no_prefix_datetime_hifen(self):
        self.assertEqual(format_name('20191021-132842', self.present),
                         '2019-10-21_13-28-42')

    def test_dont_match_prefix(self):
        self.assertIsNone(format_name('Haha_20181011', self.present))

    def test_without_date(self):
        self.assertIsNone(format_name('Something', self.present))

    def test_validate_date_prefix(self):
        tomorrow = self.present + timedelta(days=1)  # future
        file_name = 'IMG_' + tomorrow.strftime("%Y%m%d_%H%M%S")
        self.assertFalse(validate_date_prefix(file_name,
                                              self.date_hour_formats,
                                              self.present))
        file_name = 'VID_' + tomorrow.strftime("%Y%m%d-%H%M%S")
        self.assertFalse(validate_date_prefix(file_name,
                                              self.date_hour_formats,
                                              self.present))
        file_name = tomorrow.strftime("%Y%m%d %H%M%S")
        self.assertFalse(validate_date_prefix(file_name,
                                              self.date_hour_formats,
                                              self.present))


class Test_RenameFiles(unittest.TestCase):
    def test_rename_already_exists(self):
        self.maxDiff = None
        self.assertEqual(preview_rename_all(
            ['IMG_20200614_105409_BURST1.jpg',
             'IMG_20200614_105409_BURST2.jpg',
             'IMG-20200614_105409_BURST2.jpg',
             'VID_20200614_105409_BURST1.jpg']),
            ([['IMG-20200614_105409_BURST2.jpg',
               '2020-06-14_10-54-09_BURST2.jpg'],
             ['IMG_20200614_105409_BURST1.jpg',
             '2020-06-14_10-54-09_BURST1.jpg']],
             [['IMG_20200614_105409_BURST2.jpg',
              '2020-06-14_10-54-09_BURST2.jpg'],
             ['VID_20200614_105409_BURST1.jpg',
              '2020-06-14_10-54-09_BURST1.jpg']]))


if __name__ == '__main__':
    unittest.main()


'''
Only should rename images or videos, not documents or others
'''


'''
Create dir if have 3 or more files with same prefix
This number in future could be a parameter
'''
