from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import numpy as np
import pyqtgraph as pg
import qt_viewer_ui
import os
import sys
from specdal.containers.spectrum import Spectrum
from specdal.containers.collection import Collection


class SpecDALViewer(QtWidgets.QMainWindow, qt_viewer_ui.Ui_MainWindow):
    def __init__(self,parent=None):
        super(SpecDALViewer,self).__init__(parent)
        self.setupUi(self)
        self._set_pens()
        self._add_plot()

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

    def _update_plot(self):
        for s in self._collection.spectra:
            p = self._plot_widget.plot(x=s.measurement.index,y=s.measurement.values,
                    pen=self._pen,downsample=3)
            p.curve.setClickable(True)
            p.highlighted = False
            p.sigClicked.connect(self._curveclicked)

    def update_list(self):
        self.listbox.delete(0, tk.END)
        for i, spectrum in enumerate(self.collection.spectra):
            self.listbox.insert(tk.END, spectrum.name)
            if spectrum.name in self.collection.flags:
                self.listbox.itemconfigure(i, foreground='red')
        self.update_selected()
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
        self._plot_widget = pg.PlotWidget(name='Plot1')
        self.plotLayout.addWidget(self._plot_widget)
        """
        for i in range(5):
            self._plot_widget.plot(np.random.normal(size=100), 
                    title="Simplest possible plotting example",pen=self._pen)
        """
def run():
    # white background and black foreground
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    pg.setConfigOption('antialias', True)
    app = QtWidgets.QApplication(sys.argv)
    viewer = SpecDALViewer()
    viewer.show()
    app.exec_()

if __name__ == '__main__':
    run()
