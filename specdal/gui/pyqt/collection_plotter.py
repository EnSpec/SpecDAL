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

def set_or_none(iterable):
    if iterable is not None and not isinstance(iterable,set):
        iterable = set(iterable)
    return iterable

class SpectrumArtist():
    show_flagged = True
    show_unselected = True

    def __init__(self,artist):
        self.artist = artist
        self._flagged = False
        self._selected = False
        self._visible = True
        self.style = '-'
        self.color = 'k'

    @property
    def flagged(self):
        return self._flagged
    
    @flagged.setter
    def flagged(self,value):
        self._flagged = value
        self.color = 'r' if self._flagged else 'k'
        self._update_look()

    @property
    def selected(self):
        return self._selected
    
    @selected.setter
    def selected(self,value):
        self._selected = value
        self.style = '--' if self._selected else '-'
        self._update_look()
    
    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self,value):
        self._visible = value
        if self._visible:
            self.artist.set_linestyle(self.style)
        else:
            self.artist.set_linestyle('None')

    def _calculate_visibility(self):
        visible = True
        if not self.selected and not self.show_unselected:
            visible = False
        if self.flagged and not self.show_flagged:
            visible = False
        self.visible = visible

    def _update_look(self):
        self._calculate_visibility()
        if self.visible:
            self.artist.set_color(self.color)
            self.artist.set_linestyle(self.style)

            

class CollectionCanvas(FigureCanvasQTAgg):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    selected = QtCore.pyqtSignal(tuple)

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        self.ax.grid(True)
        self._flag_style = 'r'
        self._unselected_style = '-'

        fig.tight_layout()
        FigureCanvasQTAgg.__init__(self, fig)
        self.setParent(parent)

        FigureCanvasQTAgg.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)


    @property 
    def show_unselected(self):
        pass

    @show_unselected.setter
    def show_unselected(self,value):
        SpectrumArtist.show_unselected = value

    @property
    def show_flagged(self):
        pass

    @show_flagged.setter
    def show_flagged(self,value):
        SpectrumArtist.show_flagged = value

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
        class FakeEvent(object):
            def __init__(self,x,y):
                self.xdata, self.ydata = x, y

        if self._rect is not None:
            self._rect.remove()
        else:
            #make a small, fake rectangle
            dy = (self.ax.get_ylim()[1]-self.ax.get_ylim()[0])/100.
            self._rect_start = FakeEvent(event.xdata-10,event.ydata+dy)
            event = FakeEvent(event.xdata+10,event.ydata-dy)

        x0 = min(self._rect_start.xdata,event.xdata)
        x1 = max(self._rect_start.xdata,event.xdata)
        y0 = min(self._rect_start.ydata,event.ydata)
        y1 = max(self._rect_start.ydata,event.ydata)
        self.selected.emit((x0,x1,y0,y1))

    def _onMouseDown(self,event):
        if self.ax.get_navigate_mode() is None:
            self._bg_cache = self.copy_from_bbox(self.ax.bbox)
            self.clicked = True
            self.rectangleStartEvent(event)

    def _onMouseUp(self,event):
        if self.ax.get_navigate_mode() is None:
            self.restore_region(self._bg_cache)
            self.blit(self.ax.bbox)
            self.clicked = False
            self.rectangleEndEvent(event)

    def _onMouseMove(self,event):
        if self.ax.get_navigate_mode() is None:
            if(self.clicked):
                self.restore_region(self._bg_cache)
                self.rectangleMoveEvent(event)
                self.blit(self.ax.bbox)

    def setupMouseNavigation(self):
        self.clicked = False
        self.select_mode = 'rectangle'
        self._bg_cache = None

        self._cids = [
            self.mpl_connect('button_press_event',self._onMouseDown),
            self.mpl_connect('button_release_event',self._onMouseUp),
            self.mpl_connect('motion_notify_event',self._onMouseMove),
        ]

    def suspendMouseNavigation(self):
        for cid in self._cids:
            self.mpl_disconnect(cid)


    def update_selected(self,selected_keys,only_add=False):
        # better lookup time
        selected_keys = set_or_none(selected_keys)
        if only_add:
            # if we're only adding, just select
            for key in selected_keys:
                self.artist_dict[key].selected = True
        else:
            # otherwise, unselect everything that isn't selected
            keys = self.artist_dict.keys()
            for key in keys:
                self.artist_dict[key].selected = key in selected_keys
        self.draw()

    def set_flagged(self,flagged_keys,selected_keys=None,flag=True):
        # better lookup time
        flagged_keys = set_or_none(flagged_keys)
        selected_keys = set_or_none(selected_keys)
        for key in flagged_keys:
            self.artist_dict[key].flagged = flag
            
        self.draw()

    def add_flagged(self,unflagged_keys,selected_keys=None):
        self.set_flagged(unflagged_keys,selected_keys,True)

    def remove_flagged(self,unflagged_keys,selected_keys=None):
        self.set_flagged(unflagged_keys,selected_keys,False)

    def update_artists(self,collection,new_lim=False):
        if collection is None:
            return
        # save limits
        if new_lim == False:
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
        # plot
        self.ax.clear()
        collection.plot(ax=self.ax, style='k', picker=1)
        #self.ax.set_title(collection.name)
        keys = [s.name for s in collection.spectra]
        artists = self.ax.lines
        self.artist_dict = {key:SpectrumArtist(artist)
                for key,artist in zip(keys,artists)}
        for key in collection.flags:
            self.artist_dict[key].flagged = True
        self.ax.legend().remove()
        self.ax.grid(True)
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
        action = [a for a in self.__actions if "Save" in a.toolTip()][0]
        print(action.toolTip())
        action.triggered.disconnect()
        action.setToolTip("Export Dataset")
        self.icons["save"] = action

    def _update_pan_zoom(self):
        def pan2():
            self.icons["select"].setChecked(False)
            self.pan()
        def zoom2():
            self.icons["select"].setChecked(False)
            self.zoom()

        self._actions["pan"].triggered.disconnect()
        self._actions["pan"].triggered.connect(pan2)
        self._actions["zoom"].triggered.disconnect()
        self._actions["zoom"].triggered.connect(zoom2)

    @property
    def __actions(self):
        return [child for child in self.children()
                   if isinstance(child, QtWidgets.QAction)]

    def _addActions(self):
        path = os.path.split(os.path.abspath(__file__))[0]
        dir_ = os.path.join(path,"Assets")
        self.icons = {}
        def _icon_of(name,fname,description, idx=None):
            icon = QtGui.QIcon(os.path.join(dir_,fname))
            if idx is None:
                action = self.addAction(icon,description)
            else:
                action = QtWidgets.QAction(icon,description)
                self.insertAction(self.__actions[idx],action)
            self.icons[name] = action 
            return action
        self._rebind_save()
        _icon_of("select","icons8-cursor-32.png","Select spectra with left mouse",5)
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
        _icon_of("reset","icons8-restart-32.png","Revert Operators")
        self.insertSeparator(self.icons['flag'])
        self.insertSeparator(self.icons['operators'])

        self.icons["select"].setCheckable(True)
        self._update_pan_zoom()

    def triggered(self,key):
        return self.icons[key].triggered

    def returnToSelectMode(self):
        if self._ax.get_navigate_mode() == 'PAN':
            #Turn panning off
            self.pan()
        elif self._ax.get_navigate_mode() == 'ZOOM':
            #Turn zooming off
            self.zoom()
