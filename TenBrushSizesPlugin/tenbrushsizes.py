# SPDX-License-Identifier: CC0-1.0

import sys
import krita
from PyQt5.QtCore import (qDebug)
from PyQt5.QtGui import QIcon
from . import tenbrushsizesui

if sys.version_info[0] > 2:
    import importlib
else:
    import imp


class TenBrushSizesExtension(krita.Extension):

    def __init__(self, parent):
        super(TenBrushSizesExtension, self).__init__(parent)
        self.actions = []
        self.config = {"sizes":None, "maxSize":None}

    def setup(self):
        self.readSettings()

    def createActions(self, window):
        action = window.createAction("tbs_ten_brush_sizes", i18n("Ten Brush Sizes"))
        action.setToolTip(i18n("Assign ten brush sizes to ten shortcuts."))
        action.triggered.connect(self.initialize)
        self._loadActions(window)

    def initialize(self):
        self.tenbrushsizesui = tenbrushsizesui.TenBrushSizesUI()
        self.tenbrushsizesui.initialize(self)

    def readSettings(self):
        self.config["maxSize"] = float(Application.readSetting("", "maximumBrushSize", "1000"))
        sizes = Application.readSetting("TenBrushSizes", "sizes", "5.0,10.0,15.0,20.0,40.0,60.0,100.0,200.0,300.0,400.0").split(",")
        self.config["sizes"] = list(map(float, sizes))

    def writeSettings(self):
        saved_sizes = self.tenbrushsizesui.saved_sizes()

        for index, size in enumerate(saved_sizes):
            self.config["sizes"][index] = size

        Application.writeSetting("TenBrushSizes", "sizes", ','.join(map(str, saved_sizes)))

    def _loadActions(self, window):
        for i in range(1, 11):
            action = window.createAction("tbs_set_brush_size_"+ str(i), "Set Brush Size " + str(i), "")
            action.triggered.connect(self._setSize)
            action.i = i
            self.actions.append(action)

        action_inc = window.createAction("tbs_dec_brush_size", "Decrease Brush Size (Custom)", "")
        action_inc.triggered.connect(self._nextSize)
        action_inc.dir = "decrease"
        self.actions.append(action_inc)

        action_dec = window.createAction("tbs_inc_brush_size", "Increase Brush Size (Custom)", "")
        action_dec.triggered.connect(self._nextSize)
        action_dec.dir = "increase"
        self.actions.append(action_dec)

    def _setSize(self):
        i = self.sender().i
        win = Krita.instance().activeWindow()
        view = win.activeView()
        view.setBrushSize(self.config["sizes"][i - 1])

    def _nextSize(self):
        dir = self.sender().dir
        win = Krita.instance().activeWindow()
        view = win.activeView()
        current = view.brushSize()
        newSize = current
        if dir == "increase":
            for i, size in enumerate(self.config["sizes"]):
                if current >= size:
                    if i + 1 <= len(self.config["sizes"]) - 1:
                        newSize = self.config["sizes"][i + 1]
                    else:
                        return
        else:
            for i, size in reversed(list(enumerate(self.config["sizes"]))):
                if current <= size:
                    if i - 1 >= 0:
                        newSize = self.config["sizes"][i - 1]
                    else:
                        return

        view.setBrushSize(newSize)
