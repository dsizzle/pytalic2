#!/usr/bin/python
#
# stroke class definitions
#
#

import copy
import math
import time
import random
import struct

from PyQt4 import QtCore, QtGui

#import serif
from view import shared_qt

DEBUG_BBOXES = False

class Stroke(object):
    def __init__(self, char_set, from_stroke=None, parent=None):
        self.__char_set = char_set
        self.__curve_path = []

        if from_stroke is not None:
            self.__start_serif = from_stroke.get_start_serif()
            self.__end_serif = from_stroke.get_end_serif()
            self.__stroke_ctrl_verts = from_stroke.get_ctrl_vertices()
            #self.update_ctrl_vertices()
            self.__pos = QtCore.QPointF(from_stroke.pos)
            self.__curve_path = self.calc_curve_points()
            self.__bound_rect = from_stroke.get_bound_rect()
            self.__nib_angle = from_stroke.nib_angle
            self.__nib = from_stroke.nib
            self.__nib_index = from_stroke.nib_index
            self.__override_nib_angle = from_stroke.override_nib_angle
        else:
            self.__start_serif = None
            self.__end_serif = None
            self.__stroke_ctrl_verts = []
            self.__pos = QtCore.QPointF(0, 0)
            self.__bound_rect = None
            self.__bound_path = None
            self.__nib_angle = None
            self.__nib = None
            self.__nib_index = 0
            self.__override_nib_angle = False

        self.__handle_size = 10
        self.__instances = {}
        self.__parent = parent

        self.__is_selected = False

        self.seed = time.time()

    def serialize(self):
        data = struct.pack("<I", len(self.__stroke_ctrl_verts))

        for vert in self.__stroke_ctrl_verts:
            data += struct.pack("<11s", vert)

        data += struct.pack("<dd", self.__pos.x(), self.__pos.y())
        if self.__nib_angle:
            data += struct.pack("<I", self.__nib_angle)
        else:
            data += struct.pack("<I", 360)
        data += struct.pack("<H", self.__nib_index)
        data += struct.pack("<b", self.__override_nib_angle)        
        data += struct.pack("<I", self.__handle_size)
        # instances?

        data += struct.pack("<d", self.seed)

        return data

    def unserialize(self, data):
        offset = 0
        num_verts = struct.unpack_from("<I", data)[0]
        offset += struct.calcsize("<I")

        for i in range(0, num_verts):
            vert_id = struct.unpack_from("<11s", data, offset)[0]
            offset += struct.calcsize("<11s")

            self.__stroke_ctrl_verts.append(vert_id)

        (x, y) = struct.unpack_from("<dd", data, offset)
        offset += struct.calcsize("<dd")
        
        self.__pos = QtCore.QPointF(x, y)
        self.__nib_angle = struct.unpack_from("<I", data, offset)[0]
        offset += struct.calcsize("<I")

        if self.__nib_angle == 360:
            self.__nib_angle = None

        self.__nib_index = struct.unpack_from("<H", data, offset)[0]
        offset += struct.calcsize("<H")
        self.__override_nib_angle = struct.unpack_from("<b", data, offset)[0]
        offset += struct.calcsize("<b")
        self.__handle_size = struct.unpack_from("<I", data, offset)[0]
        offset += struct.calcsize("<I")
        self.seed = struct.unpack_from("<d", data, offset)[0]

    def __getstate__(self):
        save_dict = self.__dict__.copy()

        save_dict["_Stroke__curve_path"] = None

        return save_dict

    def __setstate__(self, state_dict):
        self.__dict__ = state_dict

        self.calc_curve_points()

    def get_nib_angle(self):
        return self.__nib_angle

    def set_nib_angle(self, new_nib_angle):
        self.__nib_angle = new_nib_angle

    nib_angle = property(get_nib_angle, set_nib_angle)

    def get_override_nib_angle(self):
        return self.__override_nib_angle

    def set_override_nib_angle(self, state):
        self.__override_nib_angle = state

    override_nib_angle = property(get_override_nib_angle, set_override_nib_angle)

    def add_instance(self, inst):
        self.__instances[inst] = 1

    def remove_instance(self, inst):
        self.__instances.pop(inst, None)

    def get_instance(self):
        return self.__instances.keys()

    def set_pos(self, point):
        self.__pos = QtCore.QPointF(point)

    def get_pos(self):
        return self.__pos

    pos = property(get_pos, set_pos)

    def set_nib(self, new_nib):
        self.__nib = new_nib

    def get_nib(self):
        return self.__nib

    nib = property(get_nib, set_nib)

    def set_nib_index(self, new_nib_index):
        self.__nib_index = new_nib_index

    def get_nib_index(self):
        return self.__nib_index

    nib_index = property(get_nib_index, set_nib_index)

    def straighten(self):
        temp_ctrl_verts = []
        (ctrl_verts, behaviors) = self.get_ctrl_vertices_as_list()
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

        self.set_ctrl_vertices_from_list(temp_ctrl_verts, [], False)
        self.calc_curve_points()

    def flip_x(self):
        temp_ctrl_verts = []
        (ctrl_verts, behaviors) = self.get_ctrl_vertices_as_list()
        
        for vert in ctrl_verts:
            temp_ctrl_verts.append([self.__pos.x() - vert[0], \
                vert[1] + self.__pos.y()]) 

        self.set_ctrl_vertices_from_list(temp_ctrl_verts)
        self.calc_curve_points()

    def flip_y(self):
        temp_ctrl_verts = []
        (ctrl_verts, behaviors) = self.get_ctrl_vertices_as_list()

        for vert in ctrl_verts:
            temp_ctrl_verts.append([vert[0] + self.__pos.x(), \
                self.__pos.y() - vert[1]]) 

        self.set_ctrl_vertices_from_list(temp_ctrl_verts)
        self.calc_curve_points()

    def add_end_serif(self, distance):
        self.__end_serif = serif.Flick(serif.END)
        (verts, behaviors) = self.get_ctrl_vertices_as_list()
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
        (verts, behaviors) = self.get_ctrl_vertices_as_list()
        self.__start_serif.set_ctrl_vertices(verts)
        self.__start_serif.setLength(distance)
        # if (self.nib):
        #   self.__start_serif.setAngle(self.nib.getAngle())

    def remove_start_serif(self):
        self.__start_serif = None

    def get_start_serif(self):
        return self.__start_serif

    def calc_curve_points(self):
        (verts, behaviors) = self.get_ctrl_vertices_as_list()
        self.__curve_path = []

        offset = 0
        while len(verts) - offset > 3:
            curve_path = QtGui.QPainterPath()
            curve_path.moveTo(verts[offset][0], verts[offset][1])

            curve_path.cubicTo(verts[offset+1][0], verts[offset+1][1], \
                verts[offset+2][0], verts[offset+2][1], \
                verts[offset+3][0], verts[offset+3][1])
        
            self.__curve_path.append(curve_path)
            offset += 3

    def split_curve(self, test_angle, path_num):
        left = []
        right = []
        new_curves = []
        opp_test_angle = test_angle + 180
        tolerance = 5

        (stroke_verts, behaviors) = self.get_ctrl_vertices_as_list()
        verts = []

        vert_num = path_num * 3
        for i in range(0, 4):
            verts.append(stroke_verts[i+vert_num])

        cur_curve = self.__curve_path[path_num]

        for i in range(0, 500):
            pct = float(i) / 500.0
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
        verts = []
        if make_copy:
            for vert in self.__stroke_ctrl_verts:
                vert_item = self.__char_set.get_item_by_index(vert)

                handle = []
                for i in range(1, 4):
                    pos = vert_item.get_handle_pos(i)
                    if pos:
                        pos = QtCore.QPointF(pos)

                    handle.append(pos)

                verts.append(self.__char_set.new_control_vertex(handle[0], handle[1], handle[2], vert_item.behavior))
        else:
            verts = self.__stroke_ctrl_verts

        return verts

    def get_ctrl_vertex(self, index):
        if len(self.__stroke_ctrl_verts) > index:
            return self.__stroke_ctrl_verts[index]

        return None

    def get_ctrl_vertices_as_list(self):
        points = []
        behaviors = []

        for vert in self.__stroke_ctrl_verts:
            vert_item = self.__char_set.get_item_by_index(vert)
            points.extend(vert_item.get_handle_pos_as_list())
            behaviors.append(vert_item.behavior)

        return (points, behaviors)

    def set_ctrl_vertices_from_list(self, points, behaviors=[], reset_pos=True):
        old_verts = self.__stroke_ctrl_verts[:]
        self.__stroke_ctrl_verts = []

        tmp_points = points[:]
        if reset_pos:
            self.__pos = QtCore.QPointF(tmp_points[0][0], tmp_points[0][1])
            offset = self.__pos
        else:
            offset = QtCore.QPointF(0, 0)

        left = QtCore.QPointF()
        right = QtCore.QPointF()
        i = 0

        while tmp_points:
            point = tmp_points.pop(0)
            center = QtCore.QPointF(point[0], point[1]) - offset
            if len(tmp_points):
                point = tmp_points.pop(0)
                right = QtCore.QPointF(point[0], point[1]) - offset

            behavior = 1
            if len(behaviors) > i:
                behavior = behaviors[i]
                i += 1
            
            if len(old_verts):
                vert_to_use = old_verts.pop(0)
                vert_item = self.__char_set.get_item_by_index(vert_to_use)
                vert_item.set_behavior(behavior)
                vert_item.set_handle_pos(center, 2)
                vert_item.set_handle_pos(left, 1)
                vert_item.set_handle_pos(right, 3)
                vert_item.set_handle_pos(right, 3)
            else:
                vert_to_use = self.__char_set.new_control_vertex(left, center, right, behavior)

            self.__stroke_ctrl_verts.append(vert_to_use)

            right = None
            if len(tmp_points):
                point = tmp_points.pop(0)
                left = QtCore.QPointF(point[0], point[1]) - offset

    def generate_ctrl_vertices_from_points(self, in_points):
        new_points = []
        i = 0
        points = in_points[i:i+4]

        while (points):
            if i and i < len(in_points):
                points.insert(0, in_points[i-1])
            elif not i:
                new_points.append(points[0])
    
            num_points = len(points)
                   
            if num_points == 2:
                delta_x = (points[1][0] - points[0][0]) / 3.
                delta_y = (points[1][1] - points[0][1]) / 3.
                
                new_points.append([points[0][0] + delta_x, points[0][1] + delta_y])
                new_points.append([points[1][0] - delta_x, points[1][1] - delta_y])
                new_points.append(points[1])
            elif num_points == 3:
                delta_x1 = (points[1][0] - points[0][0]) / 3.
                delta_y1 = (points[1][1] - points[0][1]) / 3.
                
                delta_x2 = (points[2][0] - points[1][0]) / 3.
                delta_y2 = (points[2][1] - points[1][1]) / 3.
                
                new_points.append([points[1][0] - delta_x1, points[1][1] - delta_y1])
                
                new_points.append([points[1][0] + delta_x2, points[1][1] + delta_y2])
                new_points.append(points[2])
            else:
                new_points.extend(points[1:4])

            i += 4

            if i >= len(in_points) and num_points > 4:
                points = points[3:]
            elif i < len(in_points):
                points = in_points[i:i+4]
            else:
                points = []

        self.set_ctrl_vertices_from_list(new_points)

        return new_points

    def set_ctrl_vertices(self, ctrl_verts):
        self.__stroke_ctrl_verts = ctrl_verts[:]
        self.update_ctrl_vertices()

    def update_ctrl_vertices(self):
        (points, behaviors) = self.get_ctrl_vertices_as_list()

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
        self.__stroke_ctrl_verts.remove(vert)
        self.update_ctrl_vertices()
        self.calc_curve_points()

    def divide_curve_at_point(self, points, t, index):
        true_index = index * 3
        if len(points) < true_index:
            true_index /= 3

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
        (points, behaviors) = self.get_ctrl_vertices_as_list()

        (points, remainder) = self.divide_curve_at_point(points, t, index)

        new_behaviors = [behaviors.pop(0)]
        point_count = 2

        for i in range(1, len(points)):
            point_count += 1
            if point_count == 3 and len(behaviors):
                new_behaviors.append(behaviors.pop(0))
                point_count = 0

        points.extend(remainder)
        new_behaviors.append(1)
        new_behaviors.extend(behaviors)   

        self.set_ctrl_vertices_from_list(points, new_behaviors, False)
        self.calc_curve_points()

    def split_at_point(self, t, index):
        (points, behaviors) = self.get_ctrl_vertices_as_list()

        (points, remainder) = self.divide_curve_at_point(points, t, index)

        points.append(remainder[0])

        new_behaviors = [behaviors.pop(0)]
        point_count = 2

        for i in range(1, len(points)):
            point_count += 1
            if point_count == 3 and len(behaviors):
                new_behaviors.append(behaviors.pop(0))
                point_count = 0
        #new_behaviors.append(1)
        behaviors.insert(0, 1)

        self.set_ctrl_vertices_from_list(points, new_behaviors, False)
        self.calc_curve_points()

        norm_remainder = []

        for point in remainder:
            norm_remainder.append([point[0]+self.__pos.x(), point[1]+self.__pos.y()])
        
        return (norm_remainder, behaviors)

    def set_parent(self, parent):
        self.__parent = parent

    def get_parent(self):
        return self.__parent

    parent = property(get_parent, set_parent)

    def draw(self, gc, nib=None, draw_color=None):
        random.seed(self.seed)

        if nib is None:
            print "ERROR: No nib provided to draw stroke\n"
            return

        draw_nib = nib
        tmp_angle = draw_nib.angle
        tmp_color = draw_nib.color
        if self.override_nib_angle:
            if self.nib:
                draw_nib = self.nib

            draw_nib.angle = self.nib_angle

        if draw_color:
            draw_nib.color = draw_color

        gc.save()
        gc.translate(self.__pos)

        gc.setPen(draw_nib.pen)
        gc.setBrush(shared_qt.BRUSH_CLEAR) #nib.brush)

        (verts, behaviors) = self.get_ctrl_vertices_as_list()
        if len(verts) > 0:
            if not self.__curve_path:
                self.calc_curve_points()

            self.__bound_rect, self.__bound_path = draw_nib.draw(gc, self)

            for curve in self.__curve_path:
                tmp_bound_rect = curve.controlPointRect()
            
                self.__bound_rect = self.__bound_rect.united(tmp_bound_rect).adjusted(-5, -5, 5, 5)

        # if self.__start_serif:
        #     verts = self.get_ctrl_vertices_as_list()
        #     self.__start_serif.set_ctrl_vertices(verts)
        #     self.__start_serif.setAngle(nib.getAngle())
        #     self.__start_serif.draw(gc, nib)

        # if self.__end_serif:
        #     verts = self.get_ctrl_vertices_as_list()
        #     self.__end_serif.set_ctrl_vertices(verts)
        #     self.__end_serif.setAngle(nib.getAngle())
        #     self.__end_serif.draw(gc, nib)

        if self.__is_selected:
            gc.setPen(shared_qt.PEN_MD_GRAY_DOT)
            gc.setBrush(shared_qt.BRUSH_CLEAR)
            gc.drawEllipse(QtCore.QPointF(0, 0), 10, 10)

            for vert in self.__stroke_ctrl_verts:
                vert_item = self.__char_set.get_item_by_index(vert)
                vert_item.draw(gc)

            if self.__bound_rect is not None:
                gc.setBrush(shared_qt.BRUSH_CLEAR)
                gc.setPen(shared_qt.PEN_MD_GRAY_DOT)

                gc.drawRect(self.__bound_rect)

        gc.restore()
        draw_nib.angle = tmp_angle
        draw_nib.color = tmp_color

    def is_contained(self, rect):
        if rect.contains(self.__bound_rect):
            return True

        for curve in self.__curve_path:
            for i in range(0, curve.elementCount()):
                element = QtCore.QPointF(curve.elementAt(i))
                if rect.contains(element):
                    return True

        (verts, behaviors) = self.get_ctrl_vertices_as_list()
        for vert in verts:
            if rect.contains(vert[0]+self.pos.x(), vert[1]+self.pos.y()):
                return True

        return False

    def is_inside(self, point, get_closest_vert=False):
        test_point = point - self.__pos
        test_box = QtCore.QRectF(test_point.x()-20, test_point.y()-20, 40, 40)
        is_inside = False

        if self.__bound_path:
            for path in self.__bound_path:
                if path.intersects(test_box):
                    is_inside = True
                    break

        if self.__bound_rect.contains(test_point):
            if self.__is_selected:
                vertex = -1
                path_num = 0
                for curve in self.__curve_path:
                    for i in range(0, curve.elementCount()):
                        element = QtCore.QPointF(curve.elementAt(i))
                        dist = math.sqrt(
                            math.pow(element.x()-test_point.x(), 2) +
                            math.pow(element.y()-test_point.y(), 2)
                        )
                        if dist < self.__handle_size:
                           vertex = i + (path_num * 3)
                           break
                    if vertex > 0:
                        break

                    path_num += 1

                if is_inside:
                    # get exact point
                    hit_point = None
                    path_num = 0
                    for curve in self.__curve_path:
                        for i in range(0, 100):
                            pct = float(i) / 100.0
                            curve_point = curve.pointAtPercent(pct)
                            if test_box.contains(int(curve_point.x()), int(curve_point.y())):
                                hit_point = pct
                                break
                        if hit_point:
                            break

                        path_num += 1

                    if hit_point:
                        if vertex < 0 and get_closest_vert:
                            vertex = int(math.ceil(path_num + hit_point))
                            
                        return (True, vertex, hit_point)
                    else:
                        return (True, vertex, None)
                elif vertex >= 0:
                    return (True, vertex, None)
                else:
                    return (False, -1, None)

            elif is_inside:
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
            vert_item = self.__char_set.get_item_by_index(vert)
            vert_item.select_handle(None)

    def get_curve_path(self):
        return self.__curve_path

    def set_curve_path(self, new_curve_path):
        self.__curve_path = new_curve_path

    curve_path = property(get_curve_path, set_curve_path)

