#!/usr/bin/python
#
# stroke class definitions
#
#

import copy
import math
import time
import random

from PyQt4 import QtCore, QtGui

import model.control_vertex
#import serif
from view import shared_qt

DEBUG_BBOXES = False

class Stroke(object):
    def __init__(self, from_stroke=None, parent=None):
        if from_stroke is not None:
            self.__start_serif = from_stroke.get_start_serif()
            self.__end_serif = from_stroke.get_end_serif()
            self.__stroke_ctrl_verts = from_stroke.get_ctrl_vertices()
            self.update_ctrl_vertices()
            self.__pos = QtCore.QPoint(from_stroke.pos)
            self.__stroke_shape = from_stroke.stroke_shape
            self.__curve_path = self.calc_curve_points()
            self.__bound_rect = from_stroke.get_bound_rect()
        else:
            self.__start_serif = None
            self.__end_serif = None
            self.__stroke_ctrl_verts = []
            self.__pos = QtCore.QPoint(0, 0)
            self.__stroke_shape = None
            self.__curve_path = None
            self.__bound_rect = None

        self.__handle_size = 10
        self.__instances = {}
        self.__parent = parent

        self.__is_selected = False

        self.seed = time.localtime()

    def __getstate__(self):
        save_dict = self.__dict__.copy()

        save_dict["_Stroke__stroke_shape"] = None
        save_dict["_Stroke__curve_path"] = None

        return save_dict

    def __setstate__(self, state_dict):
        self.__dict__ = state_dict

        self.calc_curve_points()

    def add_instance(self, inst):
        self.__instances[inst] = 1

    def remove_instance(self, inst):
        self.__instances.pop(inst, None)

    def get_instance(self):
        return self.__instances.keys()

    def set_pos(self, point):
        self.__pos = point

    def get_pos(self):
        return self.__pos

    pos = property(get_pos, set_pos)

    def straighten(self):
        temp_ctrl_verts = []
        ctrl_verts = self.get_ctrl_vertices_as_list()
        num_verts = len(ctrl_verts)

        start = ctrl_verts[0]
        end = ctrl_verts[-1]

        delta_x = (end[0]-start[0])/(num_verts-1)
        delta_y = (end[1]-start[1])/(num_verts-1)

        xpos = start[0]
        ypos = start[1]

        for i in range(0, num_verts):
            temp_ctrl_verts.append([xpos, ypos])
            xpos += delta_x
            ypos += delta_y

        self.set_ctrl_vertices_from_list(temp_ctrl_verts)
        self.calc_curve_points()

    def add_end_serif(self, distance):
        self.__end_serif = serif.Flick(serif.END)
        verts = self.get_ctrl_vertices_as_list()
        self.__end_serif.set_ctrl_vertices(verts)
        self.__end_serif.setLength(distance)
        # if (self.nib):
        #   self.__end_serif.setAngle(self.nib.getAngle())

    def remove_end_serif(self):
        self.__end_serif = None

    def get_end_serif(self):
        return self.__end_serif

    def add_start_serif(self, distance):
        self.__start_serif = serif.Flick(serif.START)
        verts = self.get_ctrl_vertices_as_list()
        self.__start_serif.set_ctrl_vertices(verts)
        self.__start_serif.setLength(distance)
        # if (self.nib):
        #   self.__start_serif.setAngle(self.nib.getAngle())

    def remove_start_serif(self):
        self.__start_serif = None

    def get_start_serif(self):
        return self.__start_serif

    def calc_curve_points(self):
        verts = self.get_ctrl_vertices_as_list()
        self.__curve_path = QtGui.QPainterPath()
        self.__curve_path.moveTo(verts[0][0], verts[0][1])

        while len(verts) > 3:
            self.__curve_path.cubicTo(verts[1][0], verts[1][1], \
                verts[2][0], verts[2][1], verts[3][0], verts[3][1])
            verts = verts[3:]

    def split_curve(self, test_angle):
        left = []
        right = []
        new_curves = []
        opp_test_angle = test_angle + 180
        tolerance = 1

        verts = self.get_ctrl_vertices_as_list()
        cur_curve = self.__curve_path

        for i in range(0, 1000):
            pct = float(i) / 1000.0
            try:
                angle = int(cur_curve.angleAtPercent(pct))
            except ValueError:
                continue

            if (angle >= test_angle - tolerance and angle <= test_angle + tolerance) or \
                (angle >= opp_test_angle - tolerance and angle <= opp_test_angle + tolerance):
                (left, right) = self.divide_curve_at_point(verts, pct, 1)
                left.append(right[0])

                cur_curve = QtGui.QPainterPath()
                cur_curve.moveTo(left[0][0], left[0][1])
                cur_curve.cubicTo(left[1][0], left[1][1], left[2][0], \
                    left[2][1], left[3][0], left[3][1])
                new_curves.append(cur_curve)
                verts = right
                cur_curve = QtGui.QPainterPath()
                cur_curve.moveTo(verts[0][0], verts[0][1])
                cur_curve.cubicTo(verts[1][0], verts[1][1], verts[2][0], \
                    verts[2][1], verts[3][0], verts[3][1])
                i = 0

        while len(verts) > 3:
            cur_curve = QtGui.QPainterPath()
            cur_curve.moveTo(verts[0][0], verts[0][1])
            cur_curve.cubicTo(verts[1][0], verts[1][1], verts[2][0], \
                verts[2][1], verts[3][0], verts[3][1])
            new_curves.append(cur_curve)
            verts = verts[3:]

        return new_curves

    def get_ctrl_vertices(self, make_copy=True):
        if make_copy:
            verts = copy.deepcopy(self.__stroke_ctrl_verts)
        else:
            verts = self.__stroke_ctrl_verts

        return verts

    def get_ctrl_vertex(self, index):
        if len(self.__stroke_ctrl_verts) > index:
            return self.__stroke_ctrl_verts[index]

        return None

    def get_ctrl_vertices_as_list(self):
        points = []
        for vert in self.__stroke_ctrl_verts:
            points.extend(vert.get_handle_pos_as_list())

        return points

    def set_ctrl_vertices_from_list(self, points):
        self.__stroke_ctrl_verts = []

        tmp_points = points[:]
        left = QtCore.QPoint()
        right = QtCore.QPoint()

        while tmp_points:
            point = tmp_points.pop(0)
            center = QtCore.QPoint(point[0], point[1])
            if len(tmp_points):
                point = tmp_points.pop(0)
                right = QtCore.QPoint(point[0], point[1])

            self.__stroke_ctrl_verts.append(model.control_vertex.ControlVertex(left, center, right))

            right = None
            if len(tmp_points):
                point = tmp_points.pop(0)
                left = QtCore.QPoint(point[0], point[1])

    def generate_ctrl_vertices_from_points(self, points):
        num_points = len(points)

        if num_points < 2:
            # not sure about this one
            pass
        elif num_points == 2:
            delta_x = (points[1][0] - points[0][0]) / 3.
            delta_y = (points[1][1] - points[0][1]) / 3.
            points = [points[0], [points[0][0] + delta_x, points[0][1] + delta_y], \
                [points[1][0] - delta_x, points[1][1] - delta_y], points[1]]
        elif num_points == 3:
            delta_x1 = (points[1][0] - points[0][0]) / 4.
            delta_y1 = (points[1][1] - points[0][1]) / 4.

            delta_x2 = (points[2][0] - points[1][0]) / 4.
            delta_y2 = (points[2][1] - points[1][1]) / 4.

            points = [points[0], [points[1][0] - delta_x1, points[1][1] - delta_y1], \
                [points[1][0] + delta_x2, points[1][1] + delta_y2], points[2]]
        else:
            first_points = [points[0], points[1]]
            last_points = [points[-2], points[-1]]
            mid_points = []

            for i in range(2, num_points-2):
                dx_t = (points[i + 1][0] - points[i - 1][0]) / 2.
                dy_t = (points[i + 1][1] - points[i - 1][1]) / 2.

                dx_a = (points[i - 1][0] - points[i][0])
                dy_a = (points[i - 1][1] - points[i][1])
                vec_len_a = math.sqrt(float(dx_a) * float(dx_a) + float(dy_a) * \
                    float(dy_a)) + 0.001
                dx_b = (points[i + 1][0] - points[i][0])
                dy_b = (points[i + 1][1] - points[i][1])
                vec_len_b = math.sqrt(float(dx_b) * float(dx_b) + float(dy_b) * \
                    float(dy_b)) + 0.001

                if vec_len_a > vec_len_b:
                    ratio = (vec_len_a / vec_len_b) / 2.
                    mid_points.append([points[i][0] - dx_t * ratio, points[i][1] - \
                        dy_t * ratio])
                    mid_points.append(points[i])
                    mid_points.append([points[i][0] + (dx_t / 2.), points[i][1] + \
                        (dy_t / 2.)])
                else:
                    ratio = (vec_len_b / vec_len_a) / 2.
                    mid_points.append([points[i][0] - (dx_t / 2.), points[i][1] - \
                        (dy_t / 2.)])
                    mid_points.append(points[i])
                    mid_points.append([points[i][0] + dx_t * ratio, points[i][1] + \
                        dy_t * ratio])

            points = first_points
            points.extend(mid_points)
            points.extend(last_points)

        self.set_ctrl_vertices_from_list(points)

    def set_ctrl_vertices(self, ctrl_verts):
        self.__stroke_ctrl_verts = ctrl_verts[:]
        self.update_ctrl_vertices()

    def update_ctrl_vertices(self):
        points = self.get_ctrl_vertices_as_list()

        if len(points) > 3:
            self.calc_curve_points()

    def delete_ctrl_vertex_by_index(self, point):
        if point == 0:
            self.__stroke_ctrl_verts[point + 1].clear_left_handle_pos()
        elif point == len(self.__stroke_ctrl_verts)-1:
            self.__stroke_ctrl_verts[point - 1].clear_right_handle_pos()

        self.__stroke_ctrl_verts.remove(self.__stroke_ctrl_verts[point])
        self.update_ctrl_vertices()
        self.calc_curve_points()

    def delete_ctrl_vertex(self, vert):
        vert.select_handle(None)
        self.__stroke_ctrl_verts.remove(vert)
        self.update_ctrl_vertices()
        self.calc_curve_points()

    def divide_curve_at_point(self, points, t, index):
        true_index = index * 3

        p3 = points[true_index]
        p2 = points[true_index - 1]
        p1 = points[true_index - 2]
        p0 = points[true_index - 3]

        new_points = []
        for i in range(0, 5):
            new_points.append([0, 0])

        for k in range(0, 2):
            p0_1 = float((1.0-t)*p0[k] + (t * p1[k]))
            p1_2 = float((1.0-t)*p1[k] + (t * p2[k]))
            p2_3 = float((1.0-t)*p2[k] + (t * p3[k]))
            p01_12 = float((1.0-t)*p0_1 + (t * p1_2))
            p12_23 = float((1.0-t)*p1_2 + (t * p2_3))
            p0112_1223 = float((1.0-t)*p01_12 + (t * p12_23))

            new_points[0][k] = p0_1
            new_points[1][k] = p01_12
            new_points[2][k] = p0112_1223
            new_points[3][k] = p12_23
            new_points[4][k] = p2_3

        points[true_index - 2:true_index] = new_points

        return (points[:true_index], points[true_index:])

    def add_ctrl_vertex(self, t, index):
        points = self.get_ctrl_vertices_as_list()

        (points, remainder) = self.divide_curve_at_point(points, t, index)

        points.extend(remainder)

        self.set_ctrl_vertices_from_list(points)
        self.calc_curve_points()

    def split_at_point(self, t, index):
        points = self.get_ctrl_vertices_as_list()

        (points, remainder) = self.divide_curve_at_point(points, t, index)

        points.append(remainder[0])

        self.set_ctrl_vertices_from_list(points)
        self.calc_curve_points()

        return remainder

    def set_parent(self, parent):
        self.__parent = parent

    def get_parent(self):
        return self.__parent

    parent = property(get_parent, set_parent)

    def draw(self, gc, show_ctrl_verts=0, nib=None):
        random.seed(self.seed)

        if nib is None:
            print "ERROR: No nib provided to draw stroke\n"
            return

        gc.save()
        gc.translate(self.__pos)

        gc.setPen(nib.pen)
        gc.setBrush(shared_qt.BRUSH_CLEAR) #nib.brush)

        verts = self.get_ctrl_vertices_as_list()
        if len(verts) > 0:
            self.__stroke_shape = QtGui.QPainterPath()
            if self.__curve_path is None:
                self.calc_curve_points()

            nib.draw(gc, self)

            path1 = QtGui.QPainterPath(self.__curve_path)
            path2 = QtGui.QPainterPath(self.__curve_path).toReversed()

            dist_x, dist_y = nib.get_actual_widths()

            path1.translate(dist_x, -dist_y)
            path2.translate(-dist_x, dist_y)

            self.__stroke_shape.addPath(path1)
            self.__stroke_shape.connectPath(path2)
            self.__stroke_shape.closeSubpath()

            #self.__stroke_shape.setFillRule(QtCore.Qt.WindingFill)

            #gc.drawPath(self.__stroke_shape)

            self.__bound_rect = self.__stroke_shape.controlPointRect()

        if self.__start_serif:
            verts = self.get_ctrl_vertices_as_list()
            self.__start_serif.set_ctrl_vertices(verts)
            self.__start_serif.setAngle(nib.getAngle())
            self.__start_serif.draw(gc, nib)

        if self.__end_serif:
            verts = self.get_ctrl_vertices_as_list()
            self.__end_serif.set_ctrl_vertices(verts)
            self.__end_serif.setAngle(nib.getAngle())
            self.__end_serif.draw(gc, nib)

        if self.__is_selected or show_ctrl_verts:
            for vert in self.__stroke_ctrl_verts:
                vert.draw(gc)

            if self.__bound_rect is not None:
                gc.setBrush(shared_qt.BRUSH_CLEAR)
                gc.setPen(shared_qt.PEN_MD_GRAY_DOT)

                gc.drawRect(self.__bound_rect)

        gc.restore()

    def inside_stroke(self, point):
        test_point = point - self.__pos
        if self.__stroke_shape is not None:
            inside = self.__stroke_shape.contains(test_point)
        else:
            inside = False

        if self.__bound_rect.contains(test_point):
            if self.__is_selected:
                for i in range(0, self.__curve_path.elementCount()):
                    element = self.__curve_path.elementAt(i)
                    dist = math.sqrt(
                        math.pow(element.x-test_point.x(), 2) +
                        math.pow(element.y-test_point.y(), 2)
                    )
                    if dist < self.__handle_size:
                        return (True, i, None)

                if inside:
                    # get exact point
                    hit_point = None
                    test_box = QtCore.QRect(test_point.x()-2, test_point.y()-2, 10, 10)
                    for i in range(0, 100):
                        pct = float(i) / 100.0
                        curve_point = self.__curve_path.pointAtPercent(pct)
                        if test_box.contains(int(curve_point.x()), int(curve_point.y())):
                            hit_point = pct
                            break

                    if hit_point is not None:
                        return (True, int(math.ceil((len(self.__stroke_ctrl_verts) - 1) * \
                            hit_point)), hit_point)
                    else:
                        return (True, -1, None)

            elif inside:
                return (True, -1, None)

        return (False, -1, None)

    def get_bound_rect(self):
        return self.__bound_rect

    def set_bound_rect(self, new_bound_rect):
        if new_bound_rect is not None:
            self.__bound_rect = new_bound_rect

    bound_rect = property(get_bound_rect, set_bound_rect)

    def get_select_state(self):
        return self.__is_selected

    def set_select_state(self, new_state):
        self.__is_selected = new_state

    selected = property(get_select_state, set_select_state)

    def deselect_ctrl_verts(self):
        for vert in self.__stroke_ctrl_verts:
            vert.select_handle(None)

    def get_stroke_shape(self):
        return self.__stroke_shape

    def set_stroke_shape(self, new_stroke_shape):
        self.__stroke_shape = new_stroke_shape

    stroke_shape = property(get_stroke_shape, set_stroke_shape)

    def get_curve_path(self):
        return self.__curve_path

    def set_curve_path(self, new_curve_path):
        self.__curve_path = new_curve_path

    curve_path = property(get_curve_path, set_curve_path)


class StrokeInstance(object):
    def __init__(self, parent=None):
        self.__stroke = None
        self.__pos = QtCore.QPoint(0, 0)
        self.__color = QtGui.QColor(128, 128, 192, 90)
        self.__bound_rect = None
        self.__parent = parent
        self.__is_selected = False

    def __del__(self):
        if self.__stroke:
            self.__stroke.remove_instance(self)

    def set_pos(self, point):
        self.__pos = point

    def get_pos(self):
        return self.__pos

    pos = property(get_pos, set_pos)

    def set_stroke(self, stroke):
        if self.__stroke:
            self.__stroke.remove_instance(self)

        self.__stroke = stroke

        self.__pos = QtCore.QPoint(stroke.get_pos())
        self.__bound_rect = stroke.get_bound_rect()

        self.__stroke.add_instance(self)

    def get_stroke(self):
        return self.__stroke

    stroke = property(get_stroke, set_stroke)

    def set_parent(self, parent):
        self.__parent = parent

    def get_parent(self):
        return self.__parent

    parent = property(get_parent, set_parent)

    def get_stroke_shape(self):
        return self.__stroke.get_stroke_shape()

    def get_start_serif(self):
        return self.__stroke.get_start_serif()

    def get_end_serif(self):
        return self.__stroke.get_end_serif()

    def draw(self, gc, show_ctrl_verts=0, nib=None):

        if self.__stroke == None:
            return

        stroke_to_draw = Stroke(from_stroke=self.__stroke)

        #
        # perform overrides
        #

        stroke_pos = self.__stroke.pos
        gc.save()

        gc.translate(-stroke_pos)
        gc.translate(self.__pos)

        stroke_to_draw.draw(gc, 0, nib)
        self.__bound_rect = stroke_to_draw.bound_rect
        gc.restore()

        if self.__is_selected or show_ctrl_verts:
            gc.save()

            gc.translate(self.__pos)
            gc.setBrush(shared_qt.BRUSH_CLEAR)
            gc.setPen(shared_qt.PEN_MD_GRAY_DOT_2)

            gc.drawRect(self.__bound_rect)

            gc.restore()

    def get_bound_rect(self):
        return self.__stroke.get_bound_rect()

    def inside_stroke(self, point):
        if self.__stroke is not None:
            stroke_pos = self.__stroke.pos
            test_point = point + stroke_pos - self.__pos
            inside = self.__stroke.inside_stroke(test_point)
        else:
            inside = (False, -1, None)

        return inside

    def get_ctrl_vertices(self, copy_stroke=False):
        return []

    def deselect_ctrl_verts(self):
        if self.__stroke:
            self.__stroke.deselect_ctrl_verts()

    def get_select_state(self):
        return self.__is_selected

    def set_select_state(self, new_state):
        self.__is_selected = new_state

    selected = property(get_select_state, set_select_state)

    def calc_curve_points(self):
        if self.__stroke:
            self.__stroke.calc_curve_points()
