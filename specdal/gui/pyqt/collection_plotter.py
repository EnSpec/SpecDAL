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

class CollectionCanvas(FigureCanvasQTAgg):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    selected = QtCore.pyqtSignal(tuple)

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        self._flag_style = 'r'

        fig.tight_layout()
        FigureCanvasQTAgg.__init__(self, fig)
        self.setParent(parent)

        FigureCanvasQTAgg.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)

    @property
    def flag_style(self):
        return self._flag_style

    @flag_style.setter
    def flag_style(self,value):
        self._flag_style = value

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
                if self.artist_dict[key].get_linestyle() == 'None':
                    continue
                if key in selected_keys:
                    self.artist_dict[key].set_linestyle('--')
                else:
                    self.artist_dict[key].set_linestyle('-')
        self.draw()

    def add_flagged(self,flagged_keys,selected_keys=None):
        # better lookup time
        if not isinstance(flagged_keys,set):
            flagged_keys = set(flagged_keys)
        if selected_keys is not None and not isinstance(selected_keys,set):
            selected_keys = set(selected_keys)
        for key in flagged_keys:
            if self.flag_style in 'rk':
                self.artist_dict[key].set_color(self.flag_style)
                if selected_keys is not None:
                    style = '--' if key in selected_keys else '-'
                    self.artist_dict[key].set_linestyle(style)
            else:
                self.artist_dict[key].set_linestyle(self.flag_style)
        self.draw()

    def remove_flagged(self,unflagged_keys,selected_keys=None):
        old_style = self.flag_style
        self.flag_style = 'k'
        self.add_flagged(unflagged_keys,selected_keys)
        self.flag_style = old_style

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
        flag_style = self.flag_style
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

    def _rebind_save(self):
        # find the save button from the matplotlib toolbar and rebind its action
        # This will probably break at some point
        actions = [child for child in self.children()
                   if isinstance(child, QtWidgets.QAction)]
        action = [action for action in actions if "Save" in action.toolTip()][0]
        print(action.toolTip())
        action.triggered.disconnect()
        action.setToolTip("Export Dataset")
        self.icons["save"] = action

    def _addActions(self):
        path = os.path.split(os.path.abspath(__file__))[0]
        dir_ = os.path.join(path,"Assets")
        self.icons = {}
        def _icon_of(name,fname,description):
            icon = QtGui.QIcon(os.path.join(dir_,fname))
            action = self.addAction(icon,description)
            self.icons[name] = action 
            return action
        self._rebind_save()
        _icon_of("load","icons8-opened-folder-32.png","Load Collection")
        _icon_of("flag","icons8-flag-filled-32.png","Flag Selection")
        _icon_of("unflag","icons8-empty-flag-32.png","Unflag Selection")
        _icon_of("vis","icons8-show-flag-32.png","Show/Hide Flags")
        _icon_of("export","icons8-flag-save-32.png","Export Flags")
        _icon_of("operators","icons8-math-32.png","Operator Configuration")
        _icon_of("stats","icons8-normal-distribution-histogram-32.png","Plot Statistics")
        _icon_of("stitch","icons8-stitch-32.png","Stitch")
        _icon_of("jump","icons8-jump-correct-32.png","Jump Correct")
        _icon_of("interpolate","icons8-interpolate-32.png","Interpolate")
        _icon_of("proximal","icons8-proximal-join.png","Proximal Join")
        self.insertSeparator(self.icons['flag'])
        self.insertSeparator(self.icons['operators'])

    def triggered(self,key):
        return self.icons[key].triggered
