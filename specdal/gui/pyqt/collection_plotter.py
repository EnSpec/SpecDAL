from PyQt5 import QtGui, QtCore, QtWidgets
import numpy as np
import pandas as pd
import os
import sys
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from specdal.containers.spectrum import Spectrum
from specdal.containers.collection import Collection

class CollectionCanvas(FigureCanvasQTAgg):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    selected = QtCore.pyqtSignal(tuple)

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)

        fig.tight_layout()
        FigureCanvasQTAgg.__init__(self, fig)
        self.setParent(parent)

        FigureCanvasQTAgg.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)

    def rectangleStartEvent(self,event):
        self._rect = None
        self._rect_start = event

    def rectangleMoveEvent(self,event):
        try:
            dx = event.xdata - self._rect_start.xdata
            dy = event.ydata - self._rect_start.ydata
        except TypeError:
            #we're out of canvas bounds
            return

        if self._rect is not None:
            self._rect.remove()

        self._rect = Rectangle((self._rect_start.xdata,self._rect_start.ydata),
                dx,dy, color='k',ls='--',lw=1,fill=False)
        self.ax.add_patch(self._rect)
        self.ax.draw_artist(self._rect)

    def rectangleEndEvent(self,event):
        if self._rect is not None:
            self._rect.remove()
        else:
            #make a small, fake rectangle
            class FakeEvent(object):
                def __init__(self,x,y):
                    self.xdata, self.ydata = x, y

            dy = (self.ax.get_ylim()[1]-self.ax.get_ylim()[0])/100.
            self._rect_start = FakeEvent(event.xdata-10,event.ydata+dy)
            event = FakeEvent(event.xdata+10,event.ydata-dy)

        x0 = min(self._rect_start.xdata,event.xdata)
        x1 = max(self._rect_start.xdata,event.xdata)
        y0 = min(self._rect_start.ydata,event.ydata)
        y1 = max(self._rect_start.ydata,event.ydata)
        self.selected.emit((x0,x1,y0,y1))

    def setupMouseNavigation(self):
        self.clicked = False
        self.select_mode = 'rectangle'
        self._bg_cache = None
        def onMouseDown(event):
            if self.ax.get_navigate_mode() is None:
                self._bg_cache = self.copy_from_bbox(self.ax.bbox)
                self.clicked = True
                self.rectangleStartEvent(event)

        def onMouseUp(event):
            if self.ax.get_navigate_mode() is None:
                self.restore_region(self._bg_cache)
                self.blit(self.ax.bbox)
                self.clicked = False
                self.rectangleEndEvent(event)

        def onMouseMove(event):
            if self.ax.get_navigate_mode() is None:
                if(self.clicked):
                    self.restore_region(self._bg_cache)
                    self.rectangleMoveEvent(event)
                    self.blit(self.ax.bbox)

        self.mpl_connect('button_press_event',onMouseDown)
        self.mpl_connect('button_release_event',onMouseUp)
        self.mpl_connect('motion_notify_event',onMouseMove)

    def update_selected(self,selected_keys,only_add=False):
        # better lookup time
        if not isinstance(selected_keys,set):
            selected_keys = set(selected_keys)
        if only_add:
            # if we're only adding, just select
            for key in selected_keys:
                self.artist_dict[key].set_linestyle('--')
        else:
            # otherwise, unselect everything that isn't selected
            keys = self.artist_dict.keys()
            for key in keys:
                if key in selected_keys:
                    self.artist_dict[key].set_linestyle('--')
                else:
                    self.artist_dict[key].set_linestyle('-')
        self.draw()

    def add_flagged(self,flagged_keys):
        # better lookup time
        if not isinstance(flagged_keys,set):
            flagged_keys = set(flagged_keys)
        for key in flagged_keys:
            self.artist_dict[key].set_color('r')
        self.draw()

    def remove_flagged(self,unflagged_keys):
        # better lookup time
        if not isinstance(unflagged_keys,set):
            unflagged_keys = set(unflagged_keys)
        for key in unflagged_keys:
            self.artist_dict[key].set_color('k')
        self.draw()

    def update_artists(self,collection,new_lim=False):
        if collection is None:
            return
        #update values being plotted -> redo statistics
        self.mean_line = None
        self.median_line = None
        self.max_line = None
        self.min_line = None
        self.std_line = None
        # save limits
        if new_lim == False:
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
        # plot
        self.ax.clear()
        #flag_style = ' '
        flag_style = 'r'
        flags = [s.name in collection.flags for s in collection.spectra]
        collection.plot(ax=self.ax,
                             style=list(np.where(flags, flag_style, 'k')),
                             picker=1)
        #self.ax.set_title(collection.name)

        keys = [s.name for s in collection.spectra]
        artists = self.ax.lines
        self.artist_dict = {key:artist for key,artist in zip(keys,artists)}
        self.colors = {key:'black' for key in keys}
        self.ax.legend().remove()
        self.draw()

class ToolBar(NavigationToolbar2QT):
    def __init__(self,canvas_,parent,ax):
        NavigationToolbar2QT.__init__(self,canvas_,parent,coordinates=False)
        self._xlim = (0,1)
        self._ylim = (0,1)
        self._ax = ax
        self._canvas_ = canvas_
        self._addActions()


    def home(self):
        """Override home method to return to home of most recent plot"""
        self._ax.set_xlim(*self._xlim)
        self._ax.set_ylim(*self._ylim)
        self._canvas_.draw()

    def setHome(self,xlim,ylim):
        self._xlim = xlim
        self._ylim = ylim

    def _addActions(self):
        for child in self.children():
            print(child)
        path = os.path.split(os.path.abspath(__file__))[0]
        dir_ = os.path.join(path,"Assets")
        def _icon_of(fname):
            return QtGui.QIcon(os.path.join(dir_,fname))
        load = self.addAction(QtGui.QIcon(_icon_of("icons8-opened-folder-32.png")),"Load Collection")
        flag = self.addAction(QtGui.QIcon(_icon_of("icons8-flag-filled-32.png")),"Flag Selection")
        unflag = self.addAction(QtGui.QIcon(_icon_of("icons8-empty-flag-32.png")),"Unflag Selection")
        flag_vis = self.addAction(QtGui.QIcon(_icon_of("icons8-show-flag-32.png")),"Show/Hide Flags")
        self.insertSeparator(flag)
        flag.setToolTip("f")
