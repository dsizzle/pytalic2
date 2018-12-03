#!/usr/bin/python
"""
nibs class definitions
"""

import math
import time

from PyQt4 import QtCore, QtGui

class Nib(object):
    def __init__(self, width=10, angle=40, color=QtGui.QColor(125, 125, 125)):
        if angle < 0:
            angle = 180 + angle

        angle = angle % 180
        self.__width = width
        self.__angle = angle
        self.__angle_rads = math.radians(self.__angle)

        self.__color = color
        self.__nibwidth_x = self.__width * math.cos(self.__angle_rads)
        self.__nibwidth_y = self.__width * math.sin(self.__angle_rads)

        self.seed = time.localtime()
        self.pen = QtGui.QPen(QtGui.QColor(self.__color.red(), self.__color.green(), \
            self.__color.blue(), 90), 2, QtCore.Qt.SolidLine)
        self.guide_brush = QtGui.QBrush(QtGui.QColor(125, 125, 125, 50), QtCore.Qt.SolidPattern)
        self.brush = QtGui.QBrush(QtGui.QColor(self.__color.red(), self.__color.green(), \
            self.__color.blue(), 220), QtCore.Qt.SolidPattern)

    def from_nib(self, nib):
        self.__width = nib.width
        self.__angle = nib.angle
        self.__angle_rads = math.radians(self.__angle)
        self.__color = nib.color

        self.__nibwidth_x = self.width * math.cos(self.__angle_rads)
        self.__nibwidth_y = self.width * math.sin(self.__angle_rads)

        self.seed = time.localtime()
        self.pen.setColor(QtGui.QColor(self.__color.red(), self.__color.green(), \
            self.__color.blue(), 90))
        self.brush.setColor(QtGui.QColor(self.__color.red(), self.__color.green(), \
            self.__color.blue(), 220))

    def get_color(self):
        return self.__color

    def set_color(self, color):
        self.__color = color
        self.pen.setColor(QtGui.QColor(self.__color.red(), self.__color.green(), \
            self.__color.blue(), 90))
        self.brush.setColor(QtGui.QColor(self.__color.red(), self.__color.green(), \
            self.__color.blue(), 220))

    color = property(get_color, set_color)

    def set_alpha(self, alpha):
        self.pen.setColor(QtGui.QColor(self.__color.red(), self.__color.green(), \
            self.__color.blue(), ((90.0 / 255.0) * alpha)))
        self.brush.setColor(QtGui.QColor(self.__color.red(), self.__color.green(), \
            self.__color.blue(), ((220.0 / 255.0) * alpha)))

    def reset_alpha(self):
        self.pen.setColor(QtGui.QColor(self.__color.red(), self.__color.green(), \
            self.__color.blue(), 90))
        self.brush.setColor(QtGui.QColor(self.__color.red(), self.__color.green(), \
            self.__color.blue(), 220))

    def set_angle(self, angle):
        if angle < 0:
            angle = 180 + angle

        angle = angle % 180

        self.__angle = angle
        self.__angle_rads = math.radians(self.__angle)

        self.__nibwidth_x = self.__width * math.cos(self.__angle_rads)
        self.__nibwidth_y = self.__width * math.sin(self.__angle_rads)

    def get_angle(self):
        return self.__angle

    angle = property(get_angle, set_angle)

    def set_width(self, width):
        self.__width = width
        self.__nibwidth_x = self.__width * math.cos(self.__angle_rads)
        self.__nibwidth_y = self.__width * math.sin(self.__angle_rads)

    def get_width(self):
        return self.__width

    width = property(get_width, set_width)

    def get_actual_widths(self):
        return self.__nibwidth_x, self.__nibwidth_y

    def draw(self, gc, stroke):
        gc.setPen(self.pen)
        gc.setBrush(self.brush)

        bound_path = []
        bound_rect = QtCore.QRectF()

        for i in range(0, len(stroke.curve_path)):
            new_curves = stroke.split_curve(self.__angle, i)
            
            for curve in new_curves:
                path1 = QtGui.QPainterPath(curve)
                path2 = QtGui.QPainterPath(curve).toReversed()

                path1.translate(self.__nibwidth_x, -self.__nibwidth_y)
                path2.translate(-self.__nibwidth_x, self.__nibwidth_y)

                curve_segment = QtGui.QPainterPath()
                curve_segment.addPath(path1)
                curve_segment.connectPath(path2)
                curve_segment.closeSubpath()
                gc.drawPath(curve_segment)

                bound_path.append(curve_segment)

                bound_rect = bound_rect.united(curve_segment.boundingRect())

        return bound_rect, bound_path

    def vert_nib_width_scale(self, gc, x, y, num=2):
        ypos = y
        for i in range(0, int(math.ceil(num))):
            ypos -= self.__width * 2
            xpos = x
            if i % 2 == 0:
                xpos = x - self.__width * 2

            gc.fillRect(QtCore.QRect(xpos, ypos, self.__width * 2, \
                self.__width * 2), self.guide_brush)

    def horz_nib_width_scale(self, gc, x, y, num=2):
        xpos = x
        for i in range(0, int(math.ceil(num))):
            xpos += self.__width * 2
            ypos = y
            if i % 2 == 0:
                ypos = y-self.__width * 2

            gc.fillRect(QtCore.QRect(xpos, ypos, self.__width * 2, \
                self.__width * 2), self.guide_brush)


class PenNib(Nib):
    def __init__(self, width=10, angle=40, color=QtGui.QColor(125, 125, 125)):
        super(PenNib, self).__init__(width, angle, color)

        self.pen.setColor(QtGui.QColor(color.red(), color.green(), \
            color.blue(), 220))
        self.pen.setWidth(width)

    def from_nib(self, nib):
        super(PenNib, self).from_nib(nib)

        self.pen.setColor(QtGui.QColor(self.color.red(), self.color.green(), \
            self.color.blue(), 220))
    
    def draw(self, gc, stroke):
        bound_path = QtGui.QPainterPath(stroke.curve_path)
        bound_rect = bound_path.boundingRect()

        gc.strokePath(bound_path, self.pen)

        return bound_rect, bound_path

class ScrollNib(Nib):
    def __init__(self, width=10, angle=40, split=5, color=QtGui.QColor(125, 25, 25)):
        self.__width = width - split
        self.__split = split
        self.__split_x = None
        self.__split_y = None
        self.__rem_x = None
        self.__rem_y = None

        if split > width:
            split = 0
        super(ScrollNib, self).__init__(width, angle, color)

        self.set_split_size(split)

    def from_nib(self, nib):
        super(ScrollNib, self).from_nib(nib)
        self.set_split_size(nib.get_split_size())

    def set_width(self, width):
        super(ScrollNib, self).set_width(width)
        self.set_split_size(self.__split)

    def set_split_size(self, split_size):
        if split_size > self.__width:
            split_size = 0

        self.__split = split_size

        split_x = (split_size) * math.cos(self.__angle_rads)
        split_y = (split_size) * math.sin(self.__angle_rads)

        self.__rem_x = (self.__nibwidth_x - split_x) / 2
        self.__rem_y = (self.__nibwidth_y - split_y) / 2

        self.__split_x = (split_x + self.__rem_x)
        self.__split_y = (split_y + self.__rem_y)

    def get_split_size(self):
        return self.__split

    split_size = property(get_split_size, set_split_size)

    def draw(self, gc, stroke):
        pass

    def set_angle(self, angle):
        super(ScrollNib, self).set_angle(angle)
        self.set_split_size(self.__split)

