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
#!/usr/bin/python3
# fill the screen with a background + URL for playlist website +
# instructions on how to use this software
# this runs as a separate process

from multiprocessing import Process
from PIL import ImageTk
from PIL import Image as Image_
import tkinter as tk
import qrcode, os

proc = None
bg_color = "#55A555"


class TKInfoScreen(tk.Frame):
    def __init__ (self, master=None):
        super().__init__(master)
        self.master = master
        self.state = False
        self.master.bind("<Escape>", self.end_fullscreen)
        self.pack()

    # TODO add listener here for event in unoremote
    def toggle_fullscreen(self, event=None, state=None, mode=0):
        print("this event is run l.244 unoremote level 5")
        if state is None:
            self.state = not self.state
        else:
            self.state = state
        if mode == 0 or 1:
            self.master.attributes('-topmost', self.state)
        if mode == 1:
            self.master.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.master.attributes("-fullscreen", self.state)
        self.master.attributes('-topmost', self.state)
        return "break"

    def setup (self, url):
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
        self.url_text["text"] = url
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
        qr.add_data(url)
        qr.make()
        img = qr.make_image(fill_color="black", back_color=bg_color)
        img.save(imagepath + '/data_png.png')

        img = Image_.open(imagepath + '/data_png.png')
        img = img.convert('RGB').convert('P', palette=Image_.ADAPTIVE)
        img.save(imagepath + '/data_gif.gif', format='GIF')

        load = Image_.open(Image_.open(imagepath + '/data_gif.gif'))
        render = ImageTk.PhotoImage(load)
        self.qrcode = tk.Label(self.master)
        self.qrcode["image"] = render
        self.qrcode.place(relx='0.5', rely='0.7', anchor='center')

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

def info (url):
    root = tk.Tk()
    root.configure(background=bg_color)
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h))
    root.attributes('-fullscreen', True)
    # root.attributes('-topmost', True)   # TODO chabge this back

    app = TKInfoScreen(master=root)
    app.setup(url)
    app.mainloop()

def start_info (url):
    global proc
    proc = Process(target=info, args=(url,))
    proc.start()
    # proc.join()

def stop_info ():
    global proc

    if proc:
        proc.terminate()


