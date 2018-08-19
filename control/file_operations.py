    
import os
import os.path
import pickle

from PyQt4 import QtGui, QtCore

import model.character_set
import view.shared_qt

class FileController(object):
    def __init__(self, parent):
        self.__main_ctrl = parent
        self.__file_name = None
        self.__dir_name = os.getcwd()

        self.__blank_pixmap = QtGui.QPixmap(view.shared_qt.ICON_SIZE, view.shared_qt.ICON_SIZE)
        self.__blank_pixmap.fill(QtGui.QColor(240, 240, 240))

    def file_new(self):
        self.__file_name = None

        self.__main_ctrl.set_character_set(model.character_set.CharacterSet())
        char_set = self.__main_ctrl.get_character_set()
        ui = self.__main_ctrl.get_ui()

        ui.base_height_spin.setValue(char_set.base_height)
        ui.cap_height_spin.setValue(char_set.cap_height)
        ui.cap_height_spin.setMaximum(char_set.ascent_height)
        ui.ascent_height_spin.setValue(char_set.ascent_height)
        ui.descent_height_spin.setValue(char_set.descent_height)
        ui.angle_spin.setValue(5)

        ui.stroke_selector_list.clear()

        for idx in range(0, ui.char_selector_list.count()):
            ui.char_selector_list.item(idx).setIcon(QtGui.QIcon(self.__blank_pixmap))

        ui.char_selector_list.setCurrentRow(0)
        #self.__cur_char = self.__char_set.current_char

        ui.edit_undo.setEnabled(False)
        ui.edit_redo.setEnabled(False)
        ui.file_save.setEnabled(False)
        

    def file_save_as(self):
        ui = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        file_path = None
        
        file_name = ui.file_save_dialog.getSaveFileName(ui, \
             "Save Character Set", self.__dir_name, \
             "Character Set Files (*.cs)")

        if file_name:
            (self.__dir_name, self.__file_name) = os.path.split(str(file_name))
            (name, ext) = os.path.splitext(self.__file_name)

            if ext != ".cs":
                self.__file_name += ".cs"

            file_path = os.path.join(self.__dir_name, self.__file_name)

            self.save(file_path)
            ui.file_save.setEnabled(True)
            cmd_stack.reset_save_count()

        return file_path
            
    def file_save(self):
        cmd_stack = self.__main_ctrl.get_command_stack()
        if self.__file_name:
            file_path = os.path.join(self.__dir_name, self.__file_name)
            if os.path.isfile(file_path):
                self.save(file_path)
                cmd_stack.reset_save_count()

                return file_path
            else:
                return self.file_save_as()
        else:
            return self.file_save_as()

    def file_open(self):
        ui = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        file_path = None
        file_path = ui.file_open_dialog.getOpenFileName(ui, \
             "Open Character Set", self.__dir_name, \
             "Character Set Files (*.cs)")

        if file_path:
            ui.setUpdatesEnabled(False)
            self.load(file_path)
            char_set = self.__main_ctrl.get_character_set()
        
            ui.base_height_spin.setValue(char_set.base_height)
            ui.guide_lines.base_height = char_set.base_height
            ui.cap_height_spin.setValue(char_set.cap_height)
            ui.guide_lines.cap_height = char_set.cap_height
            ui.cap_height_spin.setMaximum(char_set.ascent_height)
            ui.ascent_height_spin.setValue(char_set.ascent_height)
            ui.guide_lines.ascent_height = char_set.ascent_height
            ui.descent_height_spin.setValue(char_set.descent_height)
            ui.guide_lines.descent_height = char_set.descent_height
            ui.angle_spin.setValue(char_set.guide_angle)
            ui.guide_lines.guide_angle = char_set.guide_angle
            ui.char_set_nib_angle_spin.setValue(char_set.nib_angle)
            ui.guide_lines.nib_angle = char_set.nib_angle
            ui.dwg_area.nib.angle = char_set.nib_angle
            ui.dwg_area.nib_instance.angle = char_set.nib_angle
            ui.stroke_dwg_area.nib.angle = char_set.nib_angle
            ui.preview_area.nib.angle = char_set.nib_angle
            ui.nominal_width_spin.setValue(char_set.width)
            ui.guide_lines.width = char_set.width

            (self.__dir_name, self.__file_name) = os.path.split(str(file_path))

            #self.__ui.setWindowTitle(self.__label + " - " + self.__file_name)

            ui.stroke_selector_list.clear()

            saved_glyph_list = char_set.get_saved_glyphs()
            if len(saved_glyph_list) > 0:
                i = 0
                ui.stroke_load.setEnabled(True)
                ui.glyph_delete.setEnabled(True)
                for sel_stroke in saved_glyph_list:
                    bitmap = ui.dwg_area.draw_icon(None, sel_stroke.strokes)
                    ui.stroke_selector_list.addItem(str(i))
                    cur_item = ui.stroke_selector_list.item(i)
                    ui.stroke_selector_list.setCurrentRow(i)
                    cur_item.setIcon(QtGui.QIcon(bitmap))
                    i += 1

            for idx in range(0, ui.char_selector_list.count()):
                ui.char_selector_list.item(idx).setIcon(QtGui.QIcon(self.__blank_pixmap))

            idx = 0
            char_list = char_set.get_char_list()

            for character in char_list.keys():
                if len(char_list[character].strokes) > 0:
                    ui.char_selector_list.setCurrentRow(idx)
                    ui.repaint()

                idx += 1

            ui.char_selector_list.setCurrentRow(1)
            ui.char_selector_list.setCurrentRow(0)

            # self.__selection[self.__current_view_pane] = {}
            # self.__ui.repaint()

            cmd_stack.clear()
            cmd_stack.reset_save_count()
            ui.file_save.setEnabled(True)
            ui.setUpdatesEnabled(True)

        return file_path

    def save(self, file_name):
        char_set = self.__main_ctrl.get_character_set()

        try:
            data_file_fd = open(file_name, 'wb')
        except IOError:
            print "ERROR: Couldn't open %s for writing." % (file_name)
            return 1

        try:
            data_pickler = pickle.Pickler(data_file_fd, pickle.HIGHEST_PROTOCOL)
            data_pickler.dump(char_set)
        except pickle.PicklingError:
            print "ERROR: Couldn't serialize data"
            return 1

        if data_file_fd:
            data_file_fd.close()

    def load(self, file_name):
        try:
            data_file_fd = open(file_name, 'rb')
        except IOError:
            print "ERROR: Couldn't open %s for reading." % (file_name)
            return 1

        try:
            data_pickler = pickle.Unpickler(data_file_fd)
            char_set = data_pickler.load()
        except pickle.UnpicklingError:
            print "ERROR: Couldn't unserialize data"
            return 1
        except Exception:
            print "ERROR: OTHER"
            return 1

        self.__main_ctrl.set_character_set(char_set)

        if data_file_fd:
            data_file_fd.close()