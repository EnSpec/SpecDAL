from PyQt5 import QtGui, QtCore, QtWidgets
import os
import sys
import re
from specdal.containers.spectrum import Spectrum
from specdal.containers.collection import Collection
import qt_viewer_ui
import op_config_ui
import save_dialog_ui 
from collection_plotter import CollectionCanvas, ToolBar
from collections import OrderedDict
from contextlib import contextmanager

@contextmanager
def block_signal(widget):
    widget.blockSignals(True)
    yield
    widget.blockSignals(False)

class SaveDialog(QtWidgets.QDialog,save_dialog_ui.Ui_Dialog):
    def __init__(self,parent=None):
        super(SaveDialog,self).__init__(parent)
        self.setupUi(self)

class OperatorConfigDialog(QtWidgets.QDialog,op_config_ui.Ui_Dialog):
    def __init__(self,op_state,parent=None, show=None):
        super(OperatorConfigDialog,self).__init__(parent)
        self.setupUi(self)
        self.dialogs = OrderedDict(
            stats = self.statsBox,
            jump = self.jumpCorrectBox,
            stitch = self.stitchBox,
            interpolate = self.interpolateBox,
            proximal = self.proximalBox
        )
        if op_state:
            self.set_opstate(op_state)
        if show:
            self.only_show(show)

        self.proxDir.clicked.connect(self._ask_proximal_dir)
        self.buttonBox.accepted.connect(self.ok)

    def only_show(self,shown):
        for value in self.dialogs.values():
            value.hide()
        self.dialogs[shown].show()
        self.dialogs[shown].setChecked(True)
        self.adjustSize()

    def set_opstate(self,state):
        # plot config
        self.meanCheck.setChecked(state.plot.mean)
        self.medianCheck.setChecked(state.plot.median)
        self.minCheck.setChecked(state.plot.min)
        self.maxCheck.setChecked(state.plot.max)
        # jump correct
        self.jumpSplices.setText(', '.join(map(str,state.jump.splices)))
        self.jumpReference.setValue(state.jump.reference)
        # stitch
        self.stitchMethod.setCurrentIndex(self.stitchMethod.findText(
            state.stitch.mode))

        # interpolate
        self.interpSpacing.setValue(state.interp.spacing)

        # proximal join
        if state.proximal.directory:
            self.proxDir.setText(state.proximal.directory)


    def make_opstate(self):
        state = OperatorState()
        # plot config
        state.plot.mean = self.meanCheck.isChecked()
        state.plot.median = self.medianCheck.isChecked()
        state.plot.max = self.maxCheck.isChecked()
        state.plot.min = self.minCheck.isChecked()
        # jump correct
        state.jump.splices = [int(s) for s in self.jumpSplices.text().split(',')]
        state.jump.reference = self.jumpReference.value()
        # stitch
        state.stitch.mode = self.stitchMethod.currentText()

        # interpolate
        state.interp.spacing = self.interpSpacing.value()
        state.proximal.directory = self.proxDir.text()
        # actions to take
        state.actions = [key for key,value in self.dialogs.items() if value.isChecked()]
        return state

    def _ask_proximal_dir(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self,
                filter="Supported types (*.asd *.sed *.sig *.pico)")
        directory = os.path.split(fname[0])[0]
        self.proxDir.setText(directory)


    def ok(self):
        self.state = self.make_opstate()


class OperatorState():
    class _ProximalState():
        directory = None

    class _InterpState():
        spacing = 1

    class _StitchState():
        mode = "Maximum"

    class _JumpState():
        splices = [1000,1800]
        reference = 1

    class _PlotState():
        mean = False
        median = False
        min = False
        max = False

    def __init__(self):
        self.actions = []
        self.stitch = self._StitchState()
        self.jump = self._JumpState()
        self.plot = self._PlotState()
        self.interp = self._InterpState()
        self.proximal = self._ProximalState()

        
class SpecDALViewer(QtWidgets.QMainWindow, qt_viewer_ui.Ui_MainWindow):
    def __init__(self,parent=None):
        super(SpecDALViewer,self).__init__(parent)
        self.setupUi(self)
        self._set_pens()
        self._add_plot()
        self._collection = None
        self.show_flagged = True
        self.op_state = OperatorState()

        # File Dialogs
        self.actionOpen.triggered.connect(self._open_dataset)
        self.navbar.triggered('save').connect(self._export_dataset)
        self.navbar.triggered('load').connect(self._open_dataset)

        # Flag Dialogs
        self.actionFlag_Selection.triggered.connect(self.flagFromList)
        self.actionUnflag_Selection.triggered.connect(self.unflagFromList)
        # Toolbar Actions
        # Flags
        self.navbar.triggered('flag').connect(self.flagFromList)
        self.navbar.triggered('unflag').connect(self.unflagFromList)
        self.navbar.triggered('vis').connect(self.toggleFlagVisibility)
        # Operators
        self.navbar.triggered('operators').connect(self.openOperatorConfig)
        self.navbar.triggered('stats').connect(
                lambda:self.openOperatorConfig('stats'))
        self.navbar.triggered('jump').connect(
                lambda:self.openOperatorConfig('jump'))
        self.navbar.triggered('stitch').connect(
                lambda:self.openOperatorConfig('stitch'))
        self.navbar.triggered('interpolate').connect(
                lambda:self.openOperatorConfig('interpolate'))
        self.navbar.triggered('proximal').connect(
                lambda:self.openOperatorConfig('proximal'))

        # Text-based selection dialog
        self.spectraList.itemSelectionChanged.connect(self.updateFromList)
        self.selectByName.clicked.connect(self.updateFromRegex)
        self.nameSelection.returnPressed.connect(self.updateFromRegex)
        self.createGroup.clicked.connect(self.updateGroupNames)
        self.groupName.returnPressed.connect(self.updateGroupNames)



    def _jump_correct(self):
        if not self._collection: 
            return
        self._collection.jump_correct(self.op_state.jump.splices, 
                self.op_state.jump.reference)
        self.canvas.update_artists(self._collection)

    def _stitch(self):
        if not self._collection: 
            return
        mode = {
            "Maximum":"max",
            "Minimum":"min",
            "Median":"median",
            "Mean":"mean",
            "Nearest":"first"
        }[self.op_state.stitch.mode]
        self._collection.stitch(mode)
        self.canvas.update_artists(self._collection)

    def _interp(self):
        if not self._collection: 
            return
        spacing = self.op_state.interp.spacing
        self._collection.interpolate(spacing)
        self.canvas.update_artists(self._collection)

    def _proximal_join(self):
        raise NotImplemented

    def _export_dataset(self):
        dialog = SaveDialog()
        if dialog.exec_() == dialog.Accepted:
            pass
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
        self.canvas.selected.connect(self.updateFromBox)

    @property
    def selection_items(self):
        return self.spectraList.selectedItems()

    @property
    def selection_text(self):
        return (item.text().split('(')[0].strip() 
                for item in self.selection_items)

    def updateFromBox(self,event):
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

        #self.canvas.update_selected(highlighted)
        flags = set(self._collection.flags)
        with block_signal(self.spectraList):
            # don't clear selection if Ctrl is pressed
            if (QtWidgets.QApplication.keyboardModifiers() 
                  != QtCore.Qt.ControlModifier):
                self.spectraList.clearSelection()
            for highlight in highlighted:
                if self.show_flagged or (not (highlight in flags)):
                    pos = key_list.index(highlight)
                    self.spectraList.item(pos).setSelected(True)
        self.updateFromList()

    def updateFromRegex(self):
        regex = self.nameSelection.text()
        with block_signal(self.spectraList):
            for i in range(self.spectraList.count()):
                if re.search(regex,self.spectraList.item(i).text()):
                    self.spectraList.item(i).setSelected(True)
                else:
                    self.spectraList.item(i).setSelected(False)
        self.updateFromList()

        
    def updateGroupNames(self):
        if self.groupName.text():
            formatter = '{{}} ({})'.format(self.groupName.text())
        else:
            formatter = '{}'
        for item,text in zip(self.selection_items,self.selection_text):
            item.setText(formatter.format(text))

    def updateFromList(self):
        self.canvas.update_selected(self.selection_text)

    def flagFromList(self):
        for item in self.selection_items:
            item.setForeground(QtCore.Qt.red)
        for spectrum in self.selection_text:
            self._collection.flag(spectrum)
        self.canvas.add_flagged(self.selection_text)

    def unflagFromList(self):
        for item in self.selection_items:
            item.setForeground(QtCore.Qt.black)
        for spectrum in self.selection_text:
            if spectrum in self._collection.flags:
                self._collection.unflag(spectrum)
        self.canvas.remove_flagged(self.selection_text)

    def toggleFlagVisibility(self):
        self.show_flagged = not self.show_flagged
        self.canvas.flag_style = 'r' if self.show_flagged else 'None'
        if self._collection:
            self.canvas.add_flagged(self._collection.flags,self.selection_text)

    def openOperatorConfig(self,show=None):
        dialog = OperatorConfigDialog(self.op_state,show=show)
        if dialog.exec_() == dialog.Accepted:
            self.op_state = dialog.state
            for action in self.op_state.actions:
                {
                    "stitch":self._stitch,
                    "jump":self._jump_correct,
                    "stats":lambda:None,
                    "interpolate":self._interp,
                    "proximal":self._proximal_join,
                }[action]()

def run():
    app = QtWidgets.QApplication(sys.argv)
    viewer = SpecDALViewer()
    viewer.show()
    app.exec_()

if __name__ == '__main__':
    run()
