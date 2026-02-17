'''
    dlfoto.py

    Clear Creek Scientific data collection plugin for Raspberry Pi Camera

    Copyright (c) 2025 Clear Creek Scientific

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import os
import time
import datetime
from ccs_base import CCS_PHOTOGRAPH_UUID
from picamera2 import Picamera2
from libcamera import controls
from ccs_dlconfig import config
import xml.etree.ElementTree as et

NAME                              = 'dlfoto'

COLLECT_SUFFIX                    = '_dlfoto.jpg'
LABEL                             = 'ccs_dlfoto'
DESCRIPTION                       = 'photograph'

TAG_BURST_COUNT                   =  'burst-count'
TAG_BURST_DELAY                   =  'burst-delay'
TAG_PHOTO_DIR                     =  'photo-dir'


class FotoLogger(object):

    def __init__(self):
        self.burst_count = 1
        self.burst_delay = 0
        self.photo_dir = './photos'
        self.cam = Picamera2()
        self.cam.configure(self.cam.create_still_configuration())
        self.cam.start()

    def logmsg(self,msg):
        if None is not self.log_callback:
            self.log_callback(NAME,msg)

    def make_new_photo(self):
        ts = datetime.datetime.now(datetime.UTC)
        name = ts.strftime('%Y%m%d%I%M%S') + COLLECT_SUFFIX
        rv = os.path.join(self.photo_dir,name)
        self.cam.set_controls({"AfMode":controls.AfModeEnum.Continuous})
        self.cam.capture_file(rv)
        return rv

    # The following functions implement the interface for a sensor plugin module
    def get_label(self):
        return LABEL 

    def get_description(self):
        return DESCRIPTION 

    def get_uuids(self):
        return (CCS_PHOTOGRAPH_UUID,)

    def set_config(self,xml):
        try:
            root = et.fromstring(xml)
            self.burst_count = int(root.find(TAG_BURST_COUNT).text.strip())
            self.burst_delay = int(root.find(TAG_BURST_DELAY).text.strip())
            self.photo_dir = root.find(TAG_PHOTO_DIR).text.strip()

        except Exception as ex:
            self.logmsg('Error parsing config: ' + str(ex))

    def set_log_callback(self,callback):
        self.log_callback = callback

    # Returns a tuple containing the photograph uuid and the path to the graphics
    # file created for each photo event
    def get_current_values(self):
        photos = list()
        for x in range(self.burst_count):
            photos.append((CCS_PHOTOGRAPH_UUID,self.make_new_photo()))
            time.sleep(self.burst_delay)
        return tuple(photos) 


def load():
    return FotoLogger()

