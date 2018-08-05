import edit_control
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
        char_index = char_set.get_current_char_index()

        do_args = {
            'strokes' : cur_view_selection.copy(),
            'char_index' : char_index,
        }

        undo_args = {
            'strokes' : cur_view_selection.copy(),
            'char_index' : char_index,
            'copy' : False,
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

        ui.char_selector_list.setCurrentRow(char_index - edit_control.START_CHAR_CODE)
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
        print char_index

        do_args = {
            'strokes' : cur_view_selection.copy(),
            'char_index' : char_index,
        }

        undo_args = {
            'strokes' : cur_view_selection.copy(),
            'char_index' : char_index,
        }

        copy_strokes_cmd.set_do_args(do_args)
        copy_strokes_cmd.set_undo_args(undo_args)
        copy_strokes_cmd.set_do_function(self.copy_clipboard)
        copy_strokes_cmd.set_undo_function(self.paste_clipboard)

        cmd_stack.do_command(copy_strokes_cmd)
        ui.edit_undo.setEnabled(True)

        ui.repaint()

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

        ui.char_selector_list.setCurrentRow(char_index - edit_control.START_CHAR_CODE)
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
        char_index = char_set.get_current_char_index()

        do_args = {
            'strokes' : self.__clipboard[:],
            'char_index' : char_index,
        }

        undo_args = {
            'strokes' : self.__clipboard[:],
            'char_index' : char_index,
            'copy' : True,
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

        ui.char_selector_list.setCurrentRow(char_index - edit_control.START_CHAR_CODE)

        for sel_stroke in cur_view_selection.keys():
            sel_stroke.selected = False

        cur_view_selection = {}

        for sel_stroke in strokes_to_paste:
            if copy_strokes and type(sel_stroke).__name__ == 'Stroke':
                paste_stroke = stroke.Stroke(from_stroke=sel_stroke)
            else:
                paste_stroke = sel_stroke

            cur_view_selection[paste_stroke] = {}
            paste_stroke.selected = True
            if type(paste_stroke).__name__ == 'Stroke':
                current_view.symbol.add_stroke({'stroke' : paste_stroke, 'copy_stroke' : False})
            else:
                new_glyph = instance.GlyphInstance()
                new_glyph.glyph = paste_stroke.glyph
                current_view.symbol.add_glyph(new_glyph)

        self.__main_ctrl.set_ui_state_selection(True)
        ui.repaint()