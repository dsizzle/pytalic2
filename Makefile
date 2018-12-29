all: ui resources

ui: pytalic2_ui.py pytalic2_prefs.py

resources: pytalic2_rc.py
	
pytalic2_ui.py: pytalic2.ui
	pyuic4 pytalic2.ui -o pytalic2_ui.py

pytalic2_prefs.py: pytalic2_preferences.ui
	pyuic4 pytalic2_preferences.ui -o pytalic2_prefs.py

pytalic2_rc.py:
	pyrcc4 pytalic2.qrc -o pytalic2_rc.py

clean:
	rm pytalic2_ui.py pytalic2_rc.py pytalic2_prefs.py