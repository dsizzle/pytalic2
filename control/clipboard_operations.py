import file_operations

from model import commands
from model import instance
from model import stroke


class ClipboardController(object):
    def __init__(self, parent):
        self.__main_ctrl = parent
        self.__clipboard = []

    def cut_strokes(self):
        selection = self.__main_ctrl.get_selection()
        current_view = self.__main_ctrl.get_current_view()
        cur_view_selection = selection[current_view]
        char_set = self.__main_ctrl.get_character_set()
        ui = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        cut_strokes_cmd = commands.Command('cut_strokes_cmd')
        char_index = ui.char_selector_list.currentRow()

        do_args = {
            'strokes' : cur_view_selection.copy(),
            'char_index' : char_index,
        }

        undo_args = {
            'strokes' : cur_view_selection.copy(),
            'char_index' : char_index,
        }

        cut_strokes_cmd.set_do_args(do_args)
        cut_strokes_cmd.set_undo_args(undo_args)
        cut_strokes_cmd.set_do_function(self.cut_clipboard)
        cut_strokes_cmd.set_undo_function(self.paste_clipboard)

        cmd_stack.do_command(cut_strokes_cmd)
        ui.edit_undo.setEnabled(True)

        ui.repaint()

    def cut_clipboard(self, args):
        ui = self.__main_ctrl.get_ui()
        selection = self.__main_ctrl.get_selection()
        current_view = self.__main_ctrl.get_current_view()
        cur_view_selection = selection[current_view]
        
        if 'char_index' in args:
            char_index = args['char_index']
        else:
            return

        if 'strokes' in args:
            strokes_to_cut = args['strokes']
        else:
            return

        ui.char_selector_list.setCurrentRow(char_index - file_operations.START_CHAR_CODE)

        self.__clipboard = []
        for sel_stroke in strokes_to_cut:
            if type(sel_stroke).__name__ == 'Stroke':
                current_view.symbol.delete_stroke({'stroke' : sel_stroke})
            else:
                current_view.symbol.remove_glyph(sel_stroke)

            self.__clipboard.append(sel_stroke)
            if sel_stroke in cur_view_selection:
                del cur_view_selection[sel_stroke]
            sel_stroke.selected = False

        ui.edit_paste.setEnabled(True)
        ui.repaint()

    def copy_strokes(self):
        selection = self.__main_ctrl.get_selection()
        current_view = self.__main_ctrl.get_current_view()
        cur_view_selection = selection[current_view]
        char_set = self.__main_ctrl.get_character_set()
        ui = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        copy_strokes_cmd = commands.Command('copy_strokes_cmd')
        char_index = char_set.get_current_char_index()

        do_args = {
            'strokes' : cur_view_selection.copy(),
            'char_index' : char_index,
        }

        undo_args = {
            
        }

        copy_strokes_cmd.set_do_args(do_args)
        copy_strokes_cmd.set_undo_args(undo_args)
        copy_strokes_cmd.set_do_function(self.copy_clipboard)
        copy_strokes_cmd.set_undo_function(self.clear_clipboard)

        cmd_stack.do_command(copy_strokes_cmd)
        ui.edit_undo.setEnabled(True)

        ui.repaint()

    def clear_clipboard(self, args):
        self.__clipboard = []

    def copy_clipboard(self, args):
        ui = self.__main_ctrl.get_ui()

        if 'char_index' in args:
            char_index = args['char_index']
        else:
            return

        if 'strokes' in args:
            strokes_to_copy = args['strokes']
        else:
            return

        ui.char_selector_list.setCurrentRow(char_index)

        self.__clipboard = []
        for sel_stroke in strokes_to_copy.keys():
            self.__clipboard.append(sel_stroke)

        ui.edit_paste.setEnabled(True)
        ui.repaint()

    def paste_strokes(self):
        char_set = self.__main_ctrl.get_character_set()
        ui = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        paste_strokes_cmd = commands.Command('paste_strokes_cmd')
        char_index = ui.char_selector_list.currentRow()

        paste_strokes = []
        for sel_stroke in self.__clipboard:
            if type(sel_stroke).__name__ == 'Stroke':
                paste_strokes.append(stroke.Stroke(from_stroke=sel_stroke))
            else:
                paste_strokes.append(sel_stroke)

        do_args = {
            'strokes' : paste_strokes,
            'char_index' : char_index,
        }

        undo_args = {
            'strokes' : paste_strokes,
            'char_index' : char_index,
        }

        paste_strokes_cmd.set_do_args(do_args)
        paste_strokes_cmd.set_undo_args(undo_args)
        paste_strokes_cmd.set_do_function(self.paste_clipboard)
        paste_strokes_cmd.set_undo_function(self.cut_clipboard)

        cmd_stack.do_command(paste_strokes_cmd)
        ui.edit_undo.setEnabled(True)

        ui.repaint()

    def paste_clipboard(self, args):
        selection = self.__main_ctrl.get_selection()
        current_view = self.__main_ctrl.get_current_view()
        cur_view_selection = selection[current_view]
        char_set = self.__main_ctrl.get_character_set()
        ui = self.__main_ctrl.get_ui()
        cmd_stack = self.__main_ctrl.get_command_stack()

        if 'char_index' in args:
            char_index = args['char_index']
        else:
            return

        if 'strokes' in args:
            strokes_to_paste = args['strokes']
        else:
            return

        if 'copy' in args:
            copy_strokes = args['copy']
        else:
            copy_strokes = True

        ui.char_selector_list.setCurrentRow(char_index - file_operations.START_CHAR_CODE)


        for sel_stroke in cur_view_selection.keys():
            sel_stroke.selected = False

        self.__main_ctrl.clear_selection()
        cur_view_selection = selection[current_view]
        
        for sel_stroke in strokes_to_paste:
            
            added_item = None

            if type(sel_stroke).__name__ == 'Stroke':
                added_item = current_view.symbol.add_stroke({'stroke' : sel_stroke, 'copy_stroke' : False})
            else:
                new_glyph = instance.GlyphInstance()
                new_glyph.glyph = sel_stroke.glyph
                new_glyph.pos = sel_stroke.pos
                current_view.symbol.add_glyph(new_glyph)
                added_item = new_glyph

            cur_view_selection[added_item] = {}
            added_item.selected = True

        self.__main_ctrl.set_ui_state_selection(True)
        ui.repaint()