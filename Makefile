default:
	make -C specdal/gui/pyqt
	pip uninstall -y specdal
	pip install .

clean:
	pip uninstall SpecDAL

test_gui: default
	bin/specdal_gui

