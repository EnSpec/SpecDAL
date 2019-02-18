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
import qt_viewer_ui

class MyMplCanvas(FigureCanvasQTAgg):
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
        NavigationToolbar2QT.__init__(self,canvas_,parent)
        self._xlim = (0,1)
        self._ylim = (0,1)
        self._ax = ax
        self._canvas_ = canvas_

    def home(self):
        """Override home method to return to home of most recent plot"""
        self._ax.set_xlim(*self._xlim)
        self._ax.set_ylim(*self._ylim)
        self._canvas_.draw()

    def setHome(self,xlim,ylim):
        self._xlim = xlim
        self._ylim = ylim

class SpecDALViewer(QtWidgets.QMainWindow, qt_viewer_ui.Ui_MainWindow):
    def __init__(self,parent=None):
        super(SpecDALViewer,self).__init__(parent)
        self.setupUi(self)
        self._set_pens()
        self._add_plot()
        self._collection = None

        # File Dialogs
        self.actionOpen.triggered.connect(self._open_dataset)

    def _open_dataset(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self,
                filter="Supported types (*.asd *.sed *.sig *.pico)")
        directory = os.path.split(fname[0])[0]
        c = Collection(name="collection", directory=directory)
        self._set_collection(c)

    def _set_collection(self,collection):
        self._collection = collection
        self._update_plot()
        self._update_list()

    def keyPressEvent(self,event):
        pass

    def keyReleaseEvent(self,event):
        pass

    def _update_plot(self):
        self.canvas.update_artists(self._collection)

    def _update_list(self):
        for s in self._collection.spectra:
            self.spectraList.addItem(s.name)

    def _curveclicked(self,curve):
        if curve.highlighted:
            curve.highlighted = False
            curve.setPen(self._pen)
        else:
            curve.highlighted = True
            curve.setPen(self._flag_pen)

    def _set_pens(self):
        self._pen = QtGui.QPen(QtGui.QColor('black'))
        self._pen.setWidth(2)
        self._pen.setCosmetic(True)

        self._flag_pen = QtGui.QPen(QtGui.QColor('red'))
        self._flag_pen.setWidth(2)
        self._flag_pen.setDashPattern([4,5])
        self._flag_pen.setCosmetic(True)

    def _add_plot(self):
        self.canvas = MyMplCanvas(self)
        self.ax = self.canvas.ax
        self.navbar = ToolBar(self.canvas, self, self.canvas.ax) # for matplotlib features
        self.plotLayout.addWidget(self.canvas)
        self.plotLayout.addWidget(self.navbar)
        self.canvas.setupMouseNavigation()
        self.canvas.selected.connect(self.highlightFromBox)

    def update_selected(self,selected):
        print(selected)

    def highlightFromBox(self,event):
        if not self._collection:
            return
        x0,x1,y0,y1 = event
        try:
            #if our data is sorted, we can easily isolate it
            x_data = self._collection.data.loc[x0:x1]
        except:
            #Pandas builtin throws an error, use another pandas builtin
            data = self._collection.data
            in_xrange = (data.index >= x0) & (data.index <= x1)
            x_data = data.iloc[in_xrange]

        ylim = y0,y1
        is_in_box = ((x_data > y0) & (x_data < y1)).any()
        
        highlighted = is_in_box.index[is_in_box].tolist()
        key_list = list(self._collection._spectra.keys())

        self.update_selected(highlighted)
        flags = self._collection.flags
        for highlight in highlighted:
            #O(n^2) woof
            if (not (highlight in flags)) or self.show_flagged:
                pos = key_list.index(highlight)
                self.listbox.selection_set(pos)

def run():
    app = QtWidgets.QApplication(sys.argv)
    viewer = SpecDALViewer()
    viewer.show()
    app.exec_()

if __name__ == '__main__':
    run()
