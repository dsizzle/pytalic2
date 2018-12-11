import os
import os.path

from PyQt4 import QtGui, QtCore

import model.character_set
import view.shared_qt

START_CHAR_CODE = 32
END_CHAR_CODE = 128

class FileController(object):
    def __init__(self, parent):
        self.__main_ctrl = parent
        self.__file_name = None
        self.__dir_name = os.getcwd()

        self.__blank_pixmap = QtGui.QPixmap(view.shared_qt.ICON_SIZE, view.shared_qt.ICON_SIZE)
        self.__blank_pixmap.fill(QtGui.QColor(240, 240, 240))

    @property
    def file_path(self):
        if self.__file_name:
            file_path = os.path.join(self.__dir_name, self.__file_name)
        else:
            file_path = None

        return file_path

    def file_new(self):
        self.__file_name = None

        ui_ref = self.__main_ctrl.get_ui()

        ui_ref.setUpdatesEnabled(False)
        self.__main_ctrl.clear_selection()
        ui_ref.dwg_area.strokes = []
        ui_ref.dwg_area.subject = None
        ui_ref.stroke_dwg_area.strokes = []
        ui_ref.stroke_dwg_area.subject = None
        ui_ref.preview_area.subject = None

        self.__main_ctrl.set_character_set(model.character_set.CharacterSet())
        char_set = self.__main_ctrl.get_character_set()

        ui_ref.base_height_spin.setValue(char_set.base_height)
        ui_ref.cap_height_spin.setValue(char_set.cap_height)
        ui_ref.cap_height_spin.setMaximum(char_set.ascent_height)
        ui_ref.ascent_height_spin.setValue(char_set.ascent_height)
        ui_ref.descent_height_spin.setValue(char_set.descent_height)
        ui_ref.angle_spin.setValue(5)

        ui_ref.stroke_selector_list.clear()

        for i in range(START_CHAR_CODE, END_CHAR_CODE):
            char_item = QtGui.QListWidgetItem()
            char_item.setText(str(unichr(i)))

            char_id = char_set.new_character(i)
            char_item.setData(QtCore.Qt.UserRole, char_id)

            char_item.setData(QtCore.Qt.UserRole+1, i)
            char_item.setIcon(QtGui.QIcon(self.__blank_pixmap))
            ui_ref.char_selector_list.addItem(char_item)

        ui_ref.setUpdatesEnabled(True)
        ui_ref.char_selector_list.setCurrentRow(1)
        ui_ref.repaint()
        ui_ref.char_selector_list.setCurrentRow(0)

        ui_ref.edit_undo.setEnabled(False)
        ui_ref.edit_redo.setEnabled(False)
        ui_ref.file_save.setEnabled(False)

        ui_ref.repaint()

    def file_save_as(self):
        ui_ref = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        file_path = None

        file_name = ui_ref.file_save_dialog.getSaveFileName(ui_ref, \
             "Save Character Set", self.__dir_name, \
             "Character Set Files (*.cs)")

        if file_name:
            (self.__dir_name, self.__file_name) = os.path.split(str(file_name))
            (__, ext) = os.path.splitext(self.__file_name)

            if ext != ".cs":
                self.__file_name += ".cs"

            file_path = os.path.join(self.__dir_name, self.__file_name)

            self.save(file_path)
            ui_ref.file_save.setEnabled(True)
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
        ui_ref = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        file_path = None
        file_path = ui_ref.file_open_dialog.getOpenFileName(ui_ref, \
             "Open Character Set", self.__dir_name, \
             "Character Set Files (*.cs)")

        if file_path:
            ui_ref.setUpdatesEnabled(False)
            char_set = self.__main_ctrl.get_character_set()
            char_set.reset()

            status = self.load(file_path)
            if status:
                return None

            char_set = self.__main_ctrl.get_character_set()
            update_controls(ui_ref, char_set)

            (self.__dir_name, self.__file_name) = os.path.split(str(file_path))

            ui_ref.stroke_selector_list.clear()

            saved_glyph_list = char_set.glyphs
            if len(saved_glyph_list) > 0:
                i = 0
                ui_ref.stroke_load.setEnabled(True)
                ui_ref.glyph_delete.setEnabled(True)

                for glyph_id in saved_glyph_list.keys():
                    sel_stroke = saved_glyph_list[glyph_id]
                    bitmap = ui_ref.dwg_area.draw_icon(None, sel_stroke.strokes)

                    glyph_item = QtGui.QListWidgetItem()
                    glyph_item.setText(str(i))
                    glyph_item.setData(QtCore.Qt.UserRole, glyph_id)
                    glyph_item.setIcon(QtGui.QIcon(bitmap))
                    ui_ref.stroke_selector_list.addItem(glyph_item)
                    ui_ref.stroke_selector_list.setCurrentRow(i)

                    i += 1

            for idx in range(0, ui_ref.char_selector_list.count()):
                char_item = int(str(ui_ref.char_selector_list.item(idx).data(QtCore.Qt.UserRole+1).toString()))
                sel_char = char_set.get_char_by_index(char_item)
                if sel_char and sel_char.children > 0:
                    bitmap = ui_ref.dwg_area.draw_icon(None, sel_char.children)
                    ui_ref.char_selector_list.item(idx).setIcon(QtGui.QIcon(bitmap))
                else:
                    ui_ref.char_selector_list.item(idx).setIcon(QtGui.QIcon(self.__blank_pixmap))

            ui_ref.char_selector_list.setCurrentRow(1)
            ui_ref.char_selector_list.setCurrentRow(0)

            cmd_stack.clear()
            cmd_stack.reset_save_count()
            ui_ref.setUpdatesEnabled(True)

        return file_path

    def save(self, file_name):
        char_set = self.__main_ctrl.get_character_set()

        try:
            data_file_fd = open(file_name, 'wb')
        except IOError:
            print "ERROR: Couldn't open %s for writing." % (file_name)
            return 1

        try:
            char_set.save(data_file_fd)
        except IOError:
            print "ERROR: Couldn't save file"
            if data_file_fd:
                data_file_fd.close()

            return 1

        if data_file_fd:
            data_file_fd.close()

        return 0

    def load(self, file_name):
        char_set = self.__main_ctrl.get_character_set()
        char_set.reset()

        try:
            data_file_fd = open(file_name, 'rb')
        except IOError:
            print "ERROR: Couldn't open %s for reading." % (file_name)
            return 1

        try:
            char_set.load(data_file_fd)
        except IOError:
            print "ERROR: Couldn't load file"

            if data_file_fd:
                data_file_fd.close()

            return 1
        except EOFError as eof_error:
            print "ERROR: ", eof_error
            return 1
        except Exception as other_error:
            print "ERROR: Problem reading file", other_error
            return 1

        if data_file_fd:
            data_file_fd.close()

        return 0


def update_controls(ui_ref, char_set):
    ui_ref.dwg_area.char_set = char_set
    ui_ref.stroke_dwg_area.char_set = char_set
    ui_ref.preview_area.char_set = char_set

    ui_ref.base_height_spin.setValue(char_set.base_height)
    ui_ref.guide_lines.base_height = char_set.base_height
    ui_ref.cap_height_spin.setValue(char_set.cap_height)
    ui_ref.guide_lines.cap_height = char_set.cap_height
    ui_ref.cap_height_spin.setMaximum(char_set.ascent_height)
    ui_ref.ascent_height_spin.setValue(char_set.ascent_height)
    ui_ref.guide_lines.ascent_height = char_set.ascent_height
    ui_ref.descent_height_spin.setValue(char_set.descent_height)
    ui_ref.guide_lines.descent_height = char_set.descent_height
    ui_ref.angle_spin.setValue(char_set.guide_angle)
    ui_ref.guide_lines.guide_angle = char_set.guide_angle
    ui_ref.char_set_nib_angle_spin.setValue(char_set.nib_angle)
    ui_ref.guide_lines.nib_angle = char_set.nib_angle
    ui_ref.nominal_width_spin.setValue(char_set.width)
    ui_ref.guide_lines.width = char_set.width
