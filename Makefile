EDITOR=./editor
PROJECT=./project
SHARED=./shared

all: ui resources

ui: pytalic2_editor_ui.py pytalic2_prefs.py pytalic2_ui.py

resources: pytalic2_rc.py
	
pytalic2_editor_ui.py: $(EDITOR)/pytalic2_editor.ui
	pyuic5 $(EDITOR)/pytalic2_editor.ui -o $(EDITOR)/pytalic2_editor_ui.py.BAD
	sed 's/import pytalic2_rc/import shared.pytalic2_rc/' $(EDITOR)/pytalic2_editor_ui.py.BAD > $(EDITOR)/pytalic2_editor_ui.py

pytalic2_prefs.py: $(EDITOR)/pytalic2_preferences.ui
	pyuic5 $(EDITOR)/pytalic2_preferences.ui -o $(EDITOR)/pytalic2_prefs.py

pytalic2_ui.py: $(PROJECT)/pytalic2.ui
	pyuic5 $(PROJECT)/pytalic2.ui -o $(PROJECT)/pytalic2_ui.py

pytalic2_rc.py:
	pyrcc5 $(SHARED)/pytalic2.qrc -o $(SHARED)/pytalic2_rc.py

clean:
	rm $(PROJECT)/pytalic2_ui.py $(SHARED)/pytalic2_rc.py $(EDITOR)/pytalic2_prefs.py $(EDITOR)/pytalic2_editor_ui.py $(EDITOR)/pytalic2_editor_ui.py.BAD
