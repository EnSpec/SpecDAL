default:
	pip uninstall -y specdal
	pip install .

clean:
	pip uninstall SpecDAL

test-gui:
	specdal_gui

