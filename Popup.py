import tkinter as tk
import tkinter.ttk as ttk

import time
import threading

from Share import *

class Popup:
    __root = None
    __style = None
    __type = None
    popups = []
    numberofPopup = 0
    def __init__(self, defaultCloser=True):
        if Popup.__root != None:
            popup = {}
            popup['border'] = tk.Frame(Popup.__root, padx=1, pady=1, bg='#555')
            self.border = popup['border']
            popup['popup'] = tk.Frame(popup['border'], bg='#000')
            self.popup = popup['popup']
            popup['popup'].pack()
            popup['closer'] = ttk.Button(popup['popup'], style='closer.TButton')
            popup['closer'].bind('<ButtonPress-1>', self.__closerPressed)
            self.__closer = popup['closer']
            Popup.numberofPopup += 1
            popup['id'] = Popup.numberofPopup - 1
            Popup.popups.append(popup)
    def initialize(self, root):
        Popup.__root = root
        Popup.__style = ttk.Style()
        Popup.__style.configure('closer.TButton', anchor='w', font=16, foreground='#fff',
            background='#1a983d', borderwidth=0, highlightthickness=False)
        Popup.__style.map('closer.TButton', background=[('active', '#1eb749')])
    def __closerPressed(self, event):
        self.closePopup()
    def closePopup(self):
        self.border.pack_forget()
    def __autoCloser(self, t, border):
        time.sleep(t)
        border.pack_forget()
    def show(self, okText='了解', side=tk.LEFT, deathTimer=None):
        self.border.pack_forget()
        self.__closer['text'] = okText
        if okText != False:
            if side == tk.LEFT or side == tk.RIGHT:
                self.__closer.pack(side=side, fill=tk.Y)
            else:
                self.__closer.pack(side=side, fill=tk.X, anchor=tk.CENTER)
        self.border.tkraise()
        self.border.pack(pady=(10,0))
        if deathTimer != None:
            thread = threading.Thread(target=self.__autoCloser, args=(deathTimer, self.border))
            thread.daemon = True
            thread.start()
        return
    @property
    def frame(self):
        return self.popup
    @property
    def closer(self):
        return self.__closer
