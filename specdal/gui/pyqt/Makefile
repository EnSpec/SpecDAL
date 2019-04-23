default: qt_viewer_ui.py op_config_ui.py save_dialog_ui.py
	true

qt_viewer_ui.py: qt_viewer.ui
	pyuic5 qt_viewer.ui > qt_viewer_ui.py

op_config_ui.py: op_config.ui
	pyuic5 op_config.ui > op_config_ui.py

save_dialog_ui.py: save_dialog.ui
	pyuic5 save_dialog.ui > save_dialog_ui.py

test: qt_viewer_ui.py op_config_ui.py save_dialog_ui.py
	python viewer.py
