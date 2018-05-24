#!/bin/bash

import sys
import os
import time
import logging
from PIL import ImageGrab, ImageFile
from Tkinter import *
import tkMessageBox

logging.basicConfig(filename=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'clipper.log', level=logging.INFO)
log = logging.getLogger('clipper')


Class Clipper:
    def __init__(self, temp_folder, postfix):
        self.pic_folder = temp_folder
        self.pic_postfix = postfix
        self.pic_path = None
        if not os.path.exists(self.pic_folder):
            os.makedirs(self.pic_folder)

    def save(self):
        date = time.strftime("%Y-%m-%d-%M-%S", time.localtime(time.time()))
        self.pic_path = os.path.join(self.pic_folder, date + '.' + self.pic_postfix)
        try:
            data = ImageGrab.grabclipboard()
            if data:
                data.save(self.pic_path, self.pic_postfix)
            else:
                log.warn("There is on picture in clipboard")
        except Exception as e:
            log.error("Get picture from clipper failed, error: {}".format(e))
        return ''

    def save_mkdown_url(self):
        mkdown_url = "![]({})".format(self.pic_path)
        if sys.platform == 'win32':
            command = 'echo {} | clip'.format(mkdown_url)
            os.system(command)
            log.info("Save url %s to clipboard" % mkdown_url)

if __name__ == "__main__":
    pic_path = sys.argv[1]
    if len(sys.argv) < 2 or not os.path.exists(pic_path):
        Tk().withdraw()
        tkMessageBox.showinfo("mkdown cliper warning", "Please set the picture store path for clipper")

