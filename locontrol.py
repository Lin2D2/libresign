# Version: MPL 1.1/LGPL 2.1
#
# This file is part of the LibreOffice project.
#
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# Contributor(s):
# Rasmus P J <wasmus@zom.bi>
#
# Alternatively, the contents of this file may be used under the terms of
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL or the LGPL.
#
#
# purpose:
# Connect to SD remote server and control LibreOffice instance
# 

import time, logging

from xdo import Xdo
xdo = Xdo()

from request import Request
import infoscreen, config, web
import unoremote 
import config as Config

# temp
SLIDE_TIME = 2

class LibreOfficeController():
    def __init__ (self, signd):
        self.signd              = signd
        self.libo_running       = False
        self.info_showing       = True
        self.paused             = False
        # name of file currently playing
        self.current_filename   = ""

        self.last_transition    = 0
        self.slideshow_running  = False

    def start_libreoffice (self):
        self.client = unoremote.UNOClient(self)

        if not Config.NO_LIBREOFFICE:
            self.client.start()

    def run (self):
        if Config.NO_LIBREOFFICE:
            return

        secs = time.time()

        # no slideshow running, try to play a file
        if (self.client.connected and 
                not self.slideshow_running and
                not self.paused):
            filename = self.signd.playlist.get_current()

            if filename:
                filename = 'presentations/' + filename
                self.client.play_file(filename)
                self.current_filename = filename

            logging.debug("locontrol.py: try play file")

        # slideshow is up, transition
        if (self.slideshow_running and 
                secs > self.last_transition + SLIDE_TIME and
                not self.paused):
            self.client.transition_next()
            self.last_transition = secs

            logging.debug("locontrol.py: try transition slide")

    def on_slideshow_started (self):
        self.slideshow_running = True
        self.last_transition = time.time()
#        self.stop_info_screen()

    def on_slideshow_ended (self):
        self.slideshow_running = False
        self.signd.playlist.next()
        self.focus_info_screen()
#        self.start_info_screen()

    # force screen to front
    def focus_info_screen (self):
        # TODO rename the window to something more likely to be unique,
        #      like 13827218231683163
        win_id = None

        # try:
        #     win_id = xdo.search_windows(b'tk')
        # except:
        #     pass

        if win_id and len(win_id):
            win_id = win_id[0]

            # try:
            #     xdo.raise_window(win_id)
            # # TODO this happens when i alt-tab while running, i think.
            # #      don't know, but it does happen
            # except:
            #     pass

    def start_info_screen (self):
        if config.SHOW_INFO_SCREEN:
            self.info_showing = True
            addr = web.get_address()
            infoscreen.start_info(addr)

    def stop_info_screen (self):
        if config.SHOW_INFO_SCREEN:
            self.info_showing = False
            infoscreen.stop_info()

    # trigger stopping and starting a presentation
    def reload_presentation (self):
        self.slideshow_running = False
        self.client.close_file()

    def resume (self):
        self.paused = False

    def pause (self):
        self.paused = True
        self.client.close_file()
        self.slideshow_running = False

    def handle_web_request(self, msg):
        mtype = msg.get('type')

        if Request.PLAY_FILE == mtype:
            filename = msg.get('file')

            if filename != self.current_filename:
                self.reload_presentation()

        if Request.PLAY == mtype:
            self.resume()

        if Request.PAUSE == mtype:
            self.pause()

