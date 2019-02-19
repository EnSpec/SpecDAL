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
from collection_plotter import CollectionCanvas, ToolBar


class SpecDALViewer(QtWidgets.QMainWindow, qt_viewer_ui.Ui_MainWindow):
    def __init__(self,parent=None):
        super(SpecDALViewer,self).__init__(parent)
        self.setupUi(self)
        self._set_pens()
        self._add_plot()
        self._collection = None
        self.show_flagged = False

        # File Dialogs
        self.actionOpen.triggered.connect(self._open_dataset)
        self.spectraList.itemSelectionChanged.connect(self.updateFromList)

        # Flag Dialogs
        self.actionFlag_Selection.triggered.connect(self.flagFromList)
        self.actionUnflag_Selection.triggered.connect(self.unflagFromList)

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
        self.canvas = CollectionCanvas(self)
        self.ax = self.canvas.ax
        self.navbar = ToolBar(self.canvas, self, self.canvas.ax) # for matplotlib features
        self.plotLayout.addWidget(self.canvas)
        self.toolbarLayout.addWidget(self.navbar)
        self.canvas.setupMouseNavigation()
        self.canvas.selected.connect(self.highlightFromBox)

    def highlightFromBox(self,event):
        if not self._collection:
            return
        x0,x1,y0,y1 = event
        try:
            #if our data is sorted, we can easily isolate it
            x_data = self._collection.data.loc[x0:x1]
        except:
            #if pandas builtin throws an error, use another pandas builtin
            data = self._collection.data
            in_xrange = (data.index >= x0) & (data.index <= x1)
            x_data = data.iloc[in_xrange]

        ylim = y0,y1
        is_in_box = ((x_data > y0) & (x_data < y1)).any()
        
        highlighted = is_in_box.index[is_in_box].tolist()
        key_list = list(self._collection._spectra.keys())

        self.canvas.update_selected(highlighted)
        flags = set(self._collection.flags)
        # Disable signals while automatically updating the list
        self.spectraList.blockSignals(True)
        self.spectraList.clearSelection()
        for highlight in highlighted:
            if (not (highlight in flags)) or self.show_flagged:
                pos = key_list.index(highlight)
                self.spectraList.item(pos).setSelected(True)
        self.spectraList.blockSignals(False)

    @property
    def selection_items(self):
        return self.spectraList.selectedItems()

    @property
    def selection_text(self):
        return (item.text() for item in self.spectraList.selectedItems())


    def updateFromList(self):
        self.canvas.update_selected(self.selection_text)

    def flagFromList(self):
        for item in self.selection_items:
            item.setForeground(QtCore.Qt.red)
        self.canvas.add_flagged(self.selection_text)

    def unflagFromList(self):
        for item in self.selection_items:
            item.setForeground(QtCore.Qt.black)
        self.canvas.remove_flagged(self.selection_text)

def run():
    app = QtWidgets.QApplication(sys.argv)
    viewer = SpecDALViewer()
    viewer.show()
    app.exec_()

if __name__ == '__main__':
    run()
