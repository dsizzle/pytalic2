import os.path
import json

from PyQt5 import QtGui, QtWidgets

import editor.view.widgets_qt
import editor.model.common

class UserPreferences(object):
	def __init__(self, file_path=None, dialog=None):
		self.__filepath = file_path
		self.__dialog = dialog
		self.__preferences = {}

	def get_file_path(self):
		return self.__filepath

	def set_file_path(self, new_file_path):
		self.__filepath = new_file_path

	file_path = property(get_file_path, set_file_path)
	
	def get_preferences(self):
		return self.__preferences

	preferences = property(get_preferences)

	def show_dialog(self):
		if self.__dialog and self.__dialog.exec_():
			widget_list = self.__dialog.findChildren(editor.view.widgets_qt.SelectColorButton)
			widget_list.extend(self.__dialog.findChildren(QtWidgets.QDoubleSpinBox))
			widget_list.extend(self.__dialog.findChildren(QtWidgets.QSpinBox))

			for widget in widget_list:
				self.preferences[str(widget.objectName())] = widget.value()

			self.save()
			return self.preferences
		else:
			return None

	def load(self):
		if self.__filepath and os.path.exists(self.__filepath):
			settings_fd = open(self.__filepath, "r")
			try:
				self.preferences = json.load(settings_fd)
			except ValueError:
				pass
				
			settings_fd.close()
		
		if not len(self.preferences.keys()):
			for preference in editor.model.common.DEFAULT_SETTINGS:
				self.preferences[preference] = editor.model.common.DEFAULT_SETTINGS[preference]

		for ctrl_name in self.preferences.keys():
			try:
				ui_control = getattr(self.__dialog, ctrl_name)
				ui_control.setValue(self.preferences[ctrl_name])
			except AttributeError:
				pass

	def save(self):
		if self.__filepath:
			settings_fd = open(self.__filepath, "w")
			if settings_fd:
				json.dump(self.preferences, settings_fd)
				settings_fd.close()