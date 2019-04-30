default:
	make -C specdal/gui/pyqt
	python setup.py install

clean:
	pip uninstall SpecDAL

test_gui: default
	bin/specdal_gui

