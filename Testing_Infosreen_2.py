from multiprocessing import Process
from PIL import ImageTk
from PIL import Image as Image_
import tkinter as tk
import qrcode
import os

proc = None
bg_color = "#55A555"

class InfoScreen(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=1)

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

        load = Image_.open(Image_.open(imagepath + '/data_png.png'))
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
    app = InfoScreen(root)
    app.configure(background=bg_color)
    app.setup(url)
    root.mainloop()

info("http://google.com")
