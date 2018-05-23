from PyQt4 import QtCore

import model.stroke
import thirdparty.dp

STROKE = 'stroke'

class Character(object):
    def __init__(self):
        self.__width = 4
        self.__left_spacing = 1.0
        self.__right_spacing = 1.0

        self.__strokes = []
        self.__bitmap_preview = None

        self.__pos = QtCore.QPoint(0, 0)

    def __getstate__(self):
        save_dict = self.__dict__.copy()

        save_dict["_Character__bitmap_preview"] = None

        return save_dict

    def set_pos(self, point):
        self.__pos = point

    def get_pos(self):
        return self.__pos

    pos = property(get_pos, set_pos)

    def new_stroke(self, points, add=True):
        my_stroke = model.stroke.Stroke()

        start_x, start_y = points[0]

        my_stroke.setCtrlVerticesFromList(points)
        my_stroke.setPos(QtCore.QPoint(start_x, start_y))

        my_stroke.calcCurvePoints()
        num_points = len(points)
        if num_points == 2:
            my_stroke.straighten()

        if add:
            self.__strokes.append(my_stroke)

        my_stroke.setParent(self)

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

        raw_cv = my_stroke.calcCtrlVertices(new_points)
        for point in raw_cv:
            temp_cv.append([point[0]-start_x+1, point[1]-start_y+1])

        my_stroke.setCtrlVerticesFromList(temp_cv)
        my_stroke.setPos(QtCore.QPoint(start_x, start_y))

        my_stroke.calcCurvePoints()
        if num_points == 2:
            my_stroke.straighten()

        self.__strokes.append(my_stroke)

        my_stroke.setParent(self)
        return my_stroke

    def add_stroke(self, args):
        copy_stroke = True

        if args.has_key(STROKE):
            stroke_to_add = args[STROKE]
        else:
            return

        if args.has_key('copy_stroke'):
            copy_stroke = args['copy_stroke']

        if copy_stroke:
            new_stroke = self.copy_stroke({STROKE: stroke_to_add})
            new_stroke.setParent(self)
        else:
            new_stroke = stroke_to_add

        self.__strokes.append(new_stroke)

        return new_stroke

    def new_stroke_instance(self, args):
        if args.has_key(STROKE):
            stroke_to_add = args[STROKE]
        else:
            return

        new_stroke_inst = model.stroke.StrokeInstance()
        if not isinstance(stroke_to_add, model.stroke.Stroke):
            stroke_to_add = stroke_to_add.getStroke()

        new_stroke_inst.setStroke(stroke_to_add)
        self.__strokes.append(new_stroke_inst)
        new_stroke_inst.setParent(self)

        return new_stroke_inst

    def add_stroke_instance(self, inst):
        if not isinstance(inst, model.stroke.Stroke):
            self.__strokes.append(inst)
            inst.setParent(self)

    def copy_stroke(self, args):
        if args.has_key(STROKE):
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
        if args.has_key(STROKE):
            stroke_to_delete = args[STROKE]
        else:
            return

        try:
            self.__strokes.remove(stroke_to_delete)
        except IndexError:
            print "ERROR: stroke to delete doesn't exist!", stroke_to_delete
            print self.__strokes

    @property
    def strokes(self):
        return self.__strokes

    def get_bitmap(self):
        return self.__bitmap_preview

    def set_bitmap(self, bmap):
        self.__bitmap_preview = bmap

    def del_bitmap(self):
        del self.__bitmap_preview

    bitmap_preview = property(get_bitmap, set_bitmap, del_bitmap, "bitmap_preview property")

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

    def draw(self, gc, show_ctrl_verts=0, draw_handles=0, nib=None):
        gc.save()
        gc.translate(self.__pos)

        for stroke in self.__strokes:
            stroke.draw(gc, show_ctrl_verts, draw_handles, nib)

        gc.restore()
