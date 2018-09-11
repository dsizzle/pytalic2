from PyQt4 import QtCore

import model.instance
import model.stroke
import thirdparty.dp
import view.shared_qt

STROKE = 'stroke'

class Glyph(object):
    def __init__(self):
        self.__strokes = []
        self.__bitmap_preview = None

        self.__is_selected = False
        self.__pos = QtCore.QPoint(0, 0)
        self.__bound_rect = None
        self.__instances = {}

    def __getstate__(self):
        save_dict = self.__dict__.copy()

        save_dict["_Character__bitmap_preview"] = None

        return save_dict

    def add_instance(self, parent):
        self.__instances[parent] = 1

    def remove_instance(self, instance):
        self.__instances.pop(instance, None)

    @property
    def instances(self):
        return self.__instances

    def get_bound_rect(self):
        return self.__bound_rect

    def set_bound_rect(self, new_bound_rect):
        self.__bound_rect = new_bound_rect

    bound_rect = property(get_bound_rect, set_bound_rect)

    def set_pos(self, point):
        self.__pos = point

    def get_pos(self):
        return self.__pos

    pos = property(get_pos, set_pos)

    def get_strokes(self):
        return self.__strokes

    def set_strokes(self, new_strokes):
        self.__strokes = new_strokes

    strokes = property(get_strokes, set_strokes)

    children = property(get_strokes, set_strokes)

    def get_bitmap(self):
        return self.__bitmap_preview

    def set_bitmap(self, bmap):
        self.__bitmap_preview = bmap

    def del_bitmap(self):
        del self.__bitmap_preview

    bitmap_preview = property(get_bitmap, set_bitmap, del_bitmap, "bitmap_preview property")

    def get_select_state(self):
        return self.__is_selected

    def set_select_state(self, new_state):
        self.__is_selected = new_state

    selected = property(get_select_state, set_select_state)

    def new_stroke(self, points, add=True):
        my_stroke = model.stroke.Stroke()

        start_x, start_y = points[0]

        my_stroke.set_ctrl_vertices_from_list(points)
        my_stroke.pos = QtCore.QPoint(start_x, start_y)

        my_stroke.calc_curve_points()
        num_points = len(points)
        if num_points == 2:
            my_stroke.straighten()

        if add:
            self.__strokes.append(my_stroke)

        my_stroke.set_parent(self)

        return my_stroke

    def new_freehand_stroke(self, points):
        my_stroke = model.stroke.Stroke()
        raw_cv = []
        temp_cv = []

        new_points = thirdparty.dp.simplify_points(points, 10)
        start_x, start_y = new_points[0]
        num_points = len(new_points)
        while (num_points % 4) != 0:
            new_points.append(new_points[-1])
            num_points = num_points + 1

        raw_cv = my_stroke.calc_ctrl_vertices(new_points)
        for point in raw_cv:
            temp_cv.append([point[0]-start_x+1, point[1]-start_y+1])

        my_stroke.set_ctrl_vertices_from_list(temp_cv)
        my_stroke.pos = QtCore.QPoint(start_x, start_y)

        my_stroke.calc_curve_points()
        if num_points == 2:
            my_stroke.straighten()

        self.__strokes.append(my_stroke)

        my_stroke.set_parent(self)
        return my_stroke

    def add_stroke(self, args):
        copy_stroke = True

        if STROKE in args:
            stroke_to_add = args[STROKE]
        else:
            return

        if 'copy_stroke' in args:
            copy_stroke = args['copy_stroke']

        if copy_stroke:
            new_stroke = self.copy_stroke({STROKE: stroke_to_add})
            new_stroke.set_parent(self)
        else:
            new_stroke = stroke_to_add

        self.__strokes.append(new_stroke)

        return new_stroke

    def new_stroke_instance(self, args):
        if STROKE in args:
            stroke_to_add = args[STROKE]
        else:
            return

        new_stroke_inst = model.stroke.StrokeInstance()
        if not isinstance(stroke_to_add, model.stroke.Stroke):
            stroke_to_add = stroke_to_add.stroke

        new_stroke_inst.stroke = stroke_to_add
        self.__strokes.append(new_stroke_inst)
        new_stroke_inst.set_parent(self)

        return new_stroke_inst

    def add_stroke_instance(self, inst):
        if not isinstance(inst, model.stroke.Stroke):
            self.__strokes.append(inst)
            inst.set_parent(self)

    def copy_stroke(self, args):
        if STROKE in args:
            stroke_to_copy = args[STROKE]
        else:
            return

        if isinstance(stroke_to_copy, model.stroke.Stroke):
            copied_stroke = model.stroke.Stroke(fromStroke=stroke_to_copy)
        else:
            copied_stroke = model.stroke.StrokeInstance()
            real_stroke_to_copy = stroke_to_copy.getStroke()
            copied_stroke.setStroke(real_stroke_to_copy)

        return copied_stroke

    def delete_stroke(self, args):
        if STROKE in args:
            stroke_to_delete = args[STROKE]
        else:
            return

        try:
            self.__strokes.remove(stroke_to_delete)
        except ValueError:
            print "ERROR: stroke to delete doesn't exist!", stroke_to_delete
            print self.__strokes

    def is_inside(self, point):

        test_point = point - self.pos
        if not self.bound_rect:
            self.calculate_bound_rect()

        if self.bound_rect and self.bound_rect.contains(test_point):
            for sel_child in self.children:
                insideInfo = sel_child.is_inside(point)

                if insideInfo[0]:
                    return (True, -1, None)

        return (False, -1, None)

    def calculate_bound_rect(self):
        self.bound_rect = QtCore.QRectF()

        for sel_child in self.children:
            self.bound_rect = self.bound_rect.united(sel_child.bound_rect)
        
    def draw(self, gc, nib=None, nib_glyph=None):
        gc.save()
        gc.translate(self.__pos)

        if not self.__bound_rect:
            self.calculate_bound_rect()

        for sel_stroke in self.__strokes:
            sel_stroke.draw(gc, nib)

        if self.__is_selected:
            gc.setBrush(view.shared_qt.BRUSH_CLEAR)
            gc.setPen(view.shared_qt.PEN_MD_GRAY_DOT)

            gc.drawRect(self.__bound_rect)

        gc.restore()


class Character(Glyph):
    def __init__(self):
        Glyph.__init__(self)
        self.__width = 4
        self.__left_spacing = 1.0
        self.__right_spacing = 1.0
        self.__override_spacing = False

        self.__glyphs = []

    def add_glyph(self, glyph_to_add):
        if isinstance(glyph_to_add, model.instance.GlyphInstance):
            self.__glyphs.append(glyph_to_add)
            glyph_to_add.parent = self

    def remove_glyph(self, glyph_to_remove):
        self.__glyphs.remove(glyph_to_remove)
        glyph_to_remove.parent = None

    @property
    def glyphs(self):
        return self.__glyphs

    @property
    def children(self):
        child_items = self.strokes[:]
        child_items.extend(self.__glyphs[:])

        return child_items

    def get_width(self):
        return self.__width

    def set_width(self, new_width):
        self.__width = new_width

    width = property(get_width, set_width)

    def get_left_spacing(self):
        return self.__left_spacing

    def set_left_spacing(self, new_left_spacing):
        self.__left_spacing = new_left_spacing

    left_spacing = property(get_left_spacing, set_left_spacing)

    def get_right_spacing(self):
        return self.__right_spacing

    def set_right_spacing(self, new_right_spacing):
        self.__right_spacing = new_right_spacing

    right_spacing = property(get_right_spacing, set_right_spacing)

    def get_override_spacing(self):
        return self.__override_spacing

    def set_override_spacing(self, state):
        self.__override_spacing = state

    override_spacing = property(get_override_spacing, set_override_spacing)

    def draw(self, gc, nib=None, nib_glyph=None):
        if nib_glyph is None:
            nib_glyph = nib

        gc.save()
        gc.translate(self.pos)

        for glyph in self.__glyphs:
            glyph.draw(gc, nib_glyph)

        for stroke in self.strokes:
            stroke.draw(gc, nib)

        if not self.bound_rect:
            self.calculate_bound_rect()

        if self.selected:
            gc.setBrush(view.shared_qt.BRUSH_CLEAR)
            gc.setPen(view.shared_qt.PEN_MD_GRAY_DOT)

            gc.drawRect(self.bound_rect)

        gc.restore()

