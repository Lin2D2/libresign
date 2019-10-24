# Version: MPL 1.1
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
from sys import stderr
import os, time, sys, logging
import subprocess, base64

from multiprocessing import Process
from PIL import ImageTk
from PIL import Image as Image_
from tkinter import *
import tkinter as tk
import qrcode

import uno
import unohelper

import IPython
IR = IPython.embed

from com.sun.star.beans import PropertyValue
from com.sun.star.beans.PropertyState import DIRECT_VALUE


# This class handles communication with the running LibreOffice instance
connection_url = 'uno:pipe,name=libbo;urp;StarOffice.ComponentContext'

app = None
parent_conn = None
bg_color = "#55A555"

# This class receives messages (IRP) from the UNOClient
class LiboListener ():
    def on_slideshow_started (self, num_slides, current_slide):
        pass

    def on_slideshow_ended (self):
        pass

    def on_slide_notes (self, slide_index, html):
        pass

    def on_slide_updated (self, slide_number):
        pass

    def on_slide_preview (self, slide_number, image_):
        pass

    def focus_info_screen (self):
        pass

    def error_no_document (self):
        pass

# This is the Infoscreen

class InfoScreen(tk.Frame):
    def __init__(self, master=None, url=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.state = False
        self.master.bind("<Escape>", self.end_fullscreen)
        self.pack(fill=tk.BOTH, expand=1)
        self.url = url
        self.setup()

        # TODO add listener here for event in unoremote
    def toggle_fullscreen(self, event=None, state=None, mode=0):
        print("this event is run l.244 unoremote level 5")
        if state is None:
            self.state = not self.state
        else:
            self.state = state
        self.master.attributes('-topmost', self.state)
        if mode == 1:
            self.master.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.master.attributes("-fullscreen", self.state)
        self.master.attributes('-topmost', self.state)
        return "break"

    def setup (self):
        font        = ('Helvetica', 30)
        smallfont   = ('Helvetica', 20)
        # NOTE text height = 50 is somewhat arbitrary
        height      = '50'

        self.msg_txt = tk.Label(self.master)
        self.msg_txt['text'] = \
            'Visit the URL below to reach the control panel.'
        self.msg_txt.configure(foreground='white',
                               font=font, background=bg_color)
        self.msg_txt.place(relx='0.5', rely='0.4', anchor='center',
                           height=height)

        # show the URL to which the end-users should connect to reach
        # the control panel

        self.url_text = tk.Label(self.master)
        self.url_text["text"] = self.url
        self.url_text.configure(background=bg_color, foreground='white',
                                font=font)
        self.url_text.place(relx='0.5', rely='0.5', anchor='center',
                            height=height)

        # Qr Code !!!

        imagepath = os.getcwd()

        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=6,
            border=8
        )
        qr.add_data(self.url)
        qr.make()
        img = qr.make_image(fill_color="black", back_color=bg_color)
        img.save(imagepath + '/data_png.png')

        # import cairosvg
        #
        # cairosvg.svg2png(
        #     url="/home/linus/Documents/fresh_libresign_debug/libresign/libresign/test_png.svg",
        #     write_to="/home/linus/Documents/fresh_libresign_debug/libresign/libresign/test_png.png")
        #
        # load = Image_.open("/home/linus/Documents/fresh_libresign_debug/libresign/libresign/test_png.svg")

        load = Image_.open(imagepath + '/data_png.png')
        render = ImageTk.PhotoImage(load)
        qrcode_ = tk.Label(self, image=render)
        qrcode_.image = render
        qrcode_.place(relx='0.5', rely='0.7', anchor='center')

        # link to code repo
        code_site = tk.Label(self.master)
        code_site['text'] = 'Get the code at: https://github.com/LibreOffice/libresign'
        code_site.configure(background=bg_color, foreground='white',
                                font=smallfont)
        code_site.place(relx='0', rely='1.0', anchor='sw',
                            height=height)

        copyright = tk.Label(self.master)
        copyright['text'] = 'The Document Foundation'
        copyright.configure(background=bg_color, foreground='white',
                                font=smallfont)
        copyright.place(relx='1.0', rely='1.0', anchor='se',
                            height=height)


def info(url):
    root = tk.Tk()
    root.wm_title("Tkinter window")
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h))
    root.attributes('-fullscreen', True)
    # root.attributes('-topmost', True)

    global app
    app = InfoScreen(master=root, url=url)
    app.configure(background=bg_color)
    logging.debug(str("\napp:\n" + str(app) + "\n"))
    root.mainloop()

def start_info (url):
    global proc
    proc = Process(target=info, args=(url,))
    proc.start()
    # proc.join()

def stop_info ():
    global proc

    if proc:
        proc.terminate()


# This class handles communication with the running LibreOffice instance
class UNOClient():
    def __init__(self, locontrol, ):
        self.locontrol  = locontrol
        self.connected  = False
        self.frame      = "MyFrame"
        self.docu       = None

        self.file_open          = False
        self.current_filename   = ""
        self.previews           = []

    def play_file (self, filename, looping):
        # TODO event
        flags = 8
        # self.docu = self.desktop.loadComponentFromURL("file://"+filename, self.frame, flags, ())

        data = []
        # TODO the pixel width/height are inaccurate, the full-width
        #      image is created instead
        data.append(PropertyValue("OpenMode", 0, "open", DIRECT_VALUE))
        data.append(PropertyValue("Hidden", 0, True, DIRECT_VALUE))

        self.docu = self.desktop.loadComponentFromURL("file://"+filename, self.frame, flags, data)

        # make sure the presentation runs properly
        self.docu.Presentation.IsAlwaysOnTop        = True
        self.docu.Presentation.IsEndless            = looping
        self.docu.Presentation.IsFullScreen         = True
        self.docu.Presentation.IsMouseVisible       = False
        self.docu.Presentation.IsTransitionOnClick  = False
        self.docu.Presentation.Pause                = 1

        pages = self.docu.DrawPages.ElementNames

        # set defaults per page
        for name in pages:
            page = self.docu.DrawPages.getByName(name)
            page.HighResDuration = 99999
            page.TransitionDuration = 99999
            page.TransitionType = 0

        self.previews = self.load_previews()
        if self.previews is not None:
            print('previews', len(self.previews))

        logging.debug("play file %s" % filename)
        self.file_open = True
        self.current_filename = filename
        self.locontrol.focus_info_screen()

    def get_previews (self):
        return self.previews

    def load_previews (self):
        previews = []

        if not self.get_document():
            return

        pages = self.docu.DrawPages.ElementNames

        for name in pages:
            page = self.docu.DrawPages.getByName(name)

            filt = self.context.ServiceManager.createInstanceWithContext("com.sun.star.drawing.GraphicExportFilter", self.context)
            filt.setSourceDocument(page)

            data = []
            # TODO the pixel width/height are inaccurate, the full-width
            #      image is created instead
            data.append(PropertyValue('PixelWidth', 0, '200', DIRECT_VALUE))
            data.append(PropertyValue('PixelHeight', 0, '120', DIRECT_VALUE))
            data.append(PropertyValue('ColorMode', 0, '1', DIRECT_VALUE))

            args = []
            args.append(PropertyValue("MediaType", 0, 'image/png', DIRECT_VALUE))
            args.append(PropertyValue("URL", 0, 'file:///tmp/preview.png', DIRECT_VALUE))
            args.append(PropertyValue("FilterData", 0, data, DIRECT_VALUE))

            filt.filter(args)

            f = open('/tmp/preview.png', 'rb')
            img = f.read()
            f.close()

            b64 = base64.b64encode(img)

            previews.append('data:image/png;base64,{}'.format(b64.decode()))

        return previews

    #
    def get_notes (self):
        notes = []

        if self.get_document():
            pages = self.docu.DrawPages.ElementNames
    
            for name in pages:
                page = self.docu.DrawPages.getByName(name)
                notes.append(self.get_page_notes(page))

        return notes

    def get_page_notes (self, page):
        notes_page = page.getNotesPage()
        count = notes_page.Count
        service = notes_page.getByIndex(1)
        return service.String

    # 
    def close_file (self):
        if self.docu:
            self.docu.dispose()
            self.docu = None

        logging.debug("close file")
        self.file_open = False
        # TODO event

    #
    def is_file_open (self):
        return self.file_open

    def get_current_filename (self):
        return self.current_filename

    def get_document (self):
        self.docu = self.desktop.getCurrentComponent()

        # Presentation is not available unless we have loaded 
        # a presentation (i think)
        # Controller is not available unless we are in slideshow mode
        try:
            if (self.docu != None and
                self.docu.Presentation != None):
                return True
        except:
            return False 

        return False

    # 
    def transition_next (self):
        if not self.get_document():
            return

        if not self.docu.Presentation.isRunning():
            return

        index   = self.docu.Presentation.Controller.getCurrentSlideIndex()
        num     = self.docu.Presentation.Controller.getCount()

        # already at last page and we're not looping
        # TODO dunno if this is actually needed
        if index == num - 1 and not self.docu.Presentation.IsEndless:
            self.close_file()
            self.locontrol.on_slideshow_ended()
        else:
            self.docu.Presentation.Controller.gotoNextSlide()
            index = self.docu.Presentation.Controller.getCurrentSlideIndex()
            self.locontrol.on_slide_updated(index)

    #
    def transition_previous (self):
        if not self.get_document():
            return

        if not self.docu.Presentation.isRunning():
            return

        self.docu.Presentation.Controller.gotoPreviousSlide()
        index = self.docu.Presentation.Controller.getCurrentSlideIndex()
        self.locontrol.on_slide_updated(index)

    def goto_slide (self, number):
        if not self.get_document():
            return

        if not self.docu.Presentation.isRunning():
            return

        self.docu.Presentation.Controller.gotoSlideIndex(number)
        self.locontrol.on_slide_updated(number)

    def presentation_start (self):
        if not self.get_document():
            return

        # already running
        if self.docu.Presentation.isRunning():
            return

        # TODO event
        self.docu.Presentation.start()
        pages = self.docu.DrawPages
        self.locontrol.on_slideshow_started(pages.Count, 0)

    def send_slide_info (self):
        previews = self.get_previews()
        notes = self.get_notes()

        # no document / no document.DrawPages
        if len(previews) == 0 or len(notes) == 0:
            self.locontrol.error_no_document()

        for c in range(len(previews)):
            self.locontrol.on_slide_preview(c, previews[c])
            self.locontrol.on_slide_notes(c, notes[c])

    def presentation_stop (self):
        if not self.get_document():
            return

        if not self.docu.Presentation.isRunning():
            return

        self.docu.Presentation.end()
        self.locontrol.on_slideshow_ended()
        # TODO event

    def blank_screen (self):
        if not self.get_document():
            return

        if not self.docu.Presentation.isRunning():
            return

        self.docu.Presentation.Controller.blankScreen(0)
        # NOTE only sending to notify JS Remote of success
        self.locontrol.on_slide_updated(0)

    def resume (self):
        if not self.get_document():
            return

        if not self.docu.Presentation.isRunning():
            return

        self.docu.Presentation.Controller.resume()
        self.locontrol.on_slide_updated(0)

    # 
    def set_looping (self, looping):
        if not self.get_document():
            return

        self.docu.Presentation.IsEndless = looping

    # 
    def start (self, connect=False):
        soffice = "soffice"
        pipename = "libresign"

        # only connect, don't start libreoffice
        if not connect:
            # TODO make sure the binary is correct etc
            args = ["/usr/bin/soffice", '--nologo', '--norestore', '--nodefault', '--accept=pipe,name=libbo;urp']
            pid = subprocess.Popen(args).pid
            # TODO make sure it actually started! -- thought if it doesn't it will
            #      simply fail to connect which is OK
            print("started libo", pid)
    
        self.local_context = uno.getComponentContext()
        self.resolver = self.local_context.ServiceManager.createInstanceWithContext(
                 'com.sun.star.bridge.UnoUrlResolver', self.local_context)
        tries = 0

        print("Connecting to LibreOffice")

        while True:
            tries += 1

            # if tries == 100:
            #     print("can't connect to libreoffice")
            #     return 1

            try:
                sys.stdout.write(".")
                sys.stdout.flush()
                self.context = self.resolver.resolve(connection_url)
                break
            except:
                time.sleep(0.1)

        self.locontrol.focus_info_screen()

        self.smgr = self.context.ServiceManager
        self.desktop = self.smgr.createInstanceWithContext('com.sun.star.frame.Desktop', self.context)

        if not self.desktop:
            raise (Exception, "UNO: failed to create desktop")

        print("Connected to LibreOffice")

        self.connected = True
        # TODO event
        self.presentation_start()


    def stop (self):
        pass

