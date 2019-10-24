from multiprocessing import Process
from PIL import ImageTk
from PIL import Image as Image_
import tkinter as tk
import qrcode, os

proc = None
bg_color = "#55A555"

class InfoScreen(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=1)

        load = Image_.open("/home/space/Documents/libresign/libresign/data_png.png")
        render = ImageTk.PhotoImage(load)
        img = tk.Label(self, image=render)
        img.image = render
        img.place(x=0, y=0)

        


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
    root.mainloop()

info("http://google.com")
