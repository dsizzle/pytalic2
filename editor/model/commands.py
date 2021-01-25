class CommandStack(object):
    def __init__(self, parent):
        self.__undo_stack = []
        self.__redo_stack = []
        self.__after_save_count = 0
        self.__parent = parent

    def reset_save_count(self):
        self.__after_save_count = 0
        if self.__parent:
            self.__parent.set_clean()

    def get_save_count(self):
        return self.__after_save_count

    def set_save_count(self, new_save_count):
        self.__after_save_count = new_save_count

    save_count = property(get_save_count, set_save_count)

    def clear(self):
        self.clear_undo()
        self.clear_redo()
        self.reset_save_count()

    def clear_undo(self):
        self.__undo_stack[:] = []

    def clear_redo(self):
        self.__redo_stack[:] = []

    def undo(self):
        if len(self.__undo_stack) > 0:
            self.__after_save_count -= 1
            if self.__parent and self.__after_save_count == 0:
                self.__parent.set_clean()
            
            last_cmd = self.__undo_stack.pop()

            self.__redo_stack.append(last_cmd)

            last_cmd.undo_it()

    def redo(self):
        if len(self.__redo_stack) > 0:
            self.__after_save_count += 1
            if self.__parent:
                self.__parent.set_dirty()

            last_cmd = self.__redo_stack.pop()

            self.__undo_stack.append(last_cmd)

            last_cmd.do_it()

    def do_command(self, new_cmd):
        self.add_to_undo(new_cmd)
        self.__after_save_count += 1
        if self.__parent:
            self.__parent.set_dirty()

        new_cmd.do_it()

    def add_to_undo(self, new_cmd):
        self.__undo_stack.append(new_cmd)
        self.__after_save_count += 1
        if self.__parent:
            self.__parent.set_dirty()
        
        self.clear_redo()

    def undo_is_empty(self):
        return len(self.__undo_stack) == 0

    def redo_is_empty(self):
        return len(self.__redo_stack) == 0

    def dump_undo(self):
        for cmd in self.__undo_stack:
            print(cmd)

    def dump_redo(self):
        for cmd in self.__redo_stack:
            print(cmd)

    def dump_stacks(self):
        print("UNDO\n")
        self.dump_undo()

        print("\nREDO\n")
        self.dump_redo()


class Command(object):
    def __init__(self, description=""):
        self.__do_args = {}
        self.__do_function = None

        self.__undo_args = {}
        self.__undo_function = None

        self.__description = description

    def do_it(self):
        self.__do_function(self.__do_args)

    def undo_it(self):
        self.__undo_function(self.__undo_args)

    def set_undo_args(self, new_undo_args):
        self.__undo_args = new_undo_args

    def set_do_args(self, new_do_args):
        self.__do_args = new_do_args

    def set_undo_function(self, undo_function):
        self.__undo_function = undo_function

    def set_do_function(self, do_function):
        self.__do_function = do_function

    def set_description(self, new_description):
        self.__description = new_description

    def get_description(self):
        return self.__description

    description = property(get_description, set_description)

    def __str__(self):
        cmdstr = "{\n"
        cmdstr += self.__description + "\n"
        cmdstr += str(self.__do_args) + "\n"
        cmdstr += str(self.__do_function) + "\n"
        cmdstr += str(self.__undo_args) + "\n"
        cmdstr += str(self.__undo_function) + "\n"
        cmdstr += "}\n"

        return cmdstr
