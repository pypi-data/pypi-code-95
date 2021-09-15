import tkinter as tk
import PIL.ImageTk
import PIL
import cv2

class Image(tk.Label):
    """ tk Label that holds onto an image reference """
    def __init__(self, *args, **kwargs):
        tk.Label.__init__(self, *args, **kwargs)
        self.img = None

    def set_image(self, img, resize_to: list = None):
        if resize_to:
            img = cv2.resize(img, resize_to)
        try:
            img = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img))
        except RuntimeError: return
        self.configure(image=img)
        self.img = img
