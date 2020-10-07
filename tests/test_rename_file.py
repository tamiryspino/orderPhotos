import unittest

import rename_file

'''
--- Should match
IMG_20190621_234458
VID_20200316_115501
VID_20170811_014054_009
VID_20380911_062329_067
IMG_20181227_194407_096
Screenshot_20191021-132842
IMG-20181209-WA0024
VID-20181211-WA0021
20190621_234458
20200316_115501
20181209-WA0024
20191021-132842

--- Should not match
Haha_20181011
QualquerCoisa
IMG-209302930293
img_20301010 #data maior que data atual
'''

'''
Verify if the renamed file already exists on future directory,
if exists, do nothing.
'''

'''
If renamed file already exists in a specific directory with date prefix,
then the image/video should go to a ignored dir, to posterior analysis
'''

'''
Only should rename images or videos, not documents or others
'''

'''
Prefix should be a date like '2020-10-06'
'''

'''
Create dir if have 3 or more files with same prefix
This number in future could be a parameter
'''