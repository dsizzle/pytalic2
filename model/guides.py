#!/usr/bin/python
#

import math
from PyQt4 import QtCore, QtGui

class GuideLines(object):
    def __init__(self):
        # units are nibwidths from baseline
        self.__base_height_nibs = 5.0
        self.__width_nibs = 4.0
        self.__ascent_height_nibs = 3.0
        self.__descent_height_nibs = 3.0
        self.__cap_height_nibs = 2.0
        # nibwidths between rows
        self.__gap_height_nibs = 1.5

        # internal-only caching of pixel dimensions
        self.__base_height_pixels = 0
        self.__base_width_pixels = 0
        self.__half_base_width_pixels = 0
        self.__ascent_height_pixels = 0
        self.__descent_height_pixels = 0
        self.__cap_height_pixels = 0
        self.__gap_height_pixels = 0

        # degrees
        self.__angle = 5
        self.__angle_dx = math.tan(math.radians(self.__angle))

        self.__nib_width = 0
        self.__last_nib_width = 0
        self.__line_color = None
        self.__line_color_lt = None
        self.__line_color_alpha = None
        self.__line_pen_lt = None
        self.__line_pen = None
        self.__line_pen_2 = None
        self.__line_pen_dotted = None
        self.__spacer_brush = None

        self.line_color = QtGui.QColor(200, 195, 180)

    def set_angle(self, angle):
        self.__angle = angle
        self.__angle_dx = math.tan(math.radians(angle))

    def get_angle(self):
        return self.__angle

    guide_angle = property(get_angle, set_angle)

    def set_line_color(self, linecolor):
        self.__line_color = linecolor
        self.__line_color_lt = QtGui.QColor(self.__line_color.red()+30, \
            self.__line_color.green()+30, self.__line_color.blue()+30)
        self.__line_color_alpha = QtGui.QColor(self.__line_color.red()+30, \
            self.__line_color.green()+30, self.__line_color.blue()+30, 128)
        self.__line_pen_lt = QtGui.QPen(self.__line_color_lt, 1, QtCore.Qt.SolidLine)
        self.__line_pen = QtGui.QPen(self.__line_color, 1, QtCore.Qt.SolidLine)
        self.__line_pen_2 = QtGui.QPen(self.__line_color, 2, QtCore.Qt.SolidLine)
        self.__line_pen_dotted = QtGui.QPen(self.__line_color, 1, QtCore.Qt.DotLine)
        self.__spacer_brush = QtGui.QBrush(self.__line_color_alpha, QtCore.Qt.SolidPattern)

    def get_line_color(self):
        return self.__line_color

    line_color = property(get_line_color, set_line_color)

    def set_base_height(self, height):
        self.__base_height_nibs = height
        self.__base_height_pixels = height * self.__nib_width
        self.__ascent_height_pixels = (self.__ascent_height_nibs + \
            self.__base_height_nibs) * self.__nib_width
        self.__cap_height_pixels = (self.__cap_height_nibs + \
            self.__base_height_nibs) * self.__nib_width

    def get_base_height(self):
        return self.__base_height_nibs

    base_height = property(get_base_height, set_base_height)

    def set_ascent(self, height):
        self.__ascent_height_nibs = height
        self.__ascent_height_pixels = (height + self.__base_height_nibs) * self.__nib_width

    def get_ascent(self):
        return self.__ascent_height_nibs

    ascent_height = property(get_ascent, set_ascent)

    def set_cap_height(self, height):
        self.__cap_height_nibs = height
        self.__cap_height_pixels = (height + self.__base_height_nibs) * self.__nib_width

    def get_cap_height(self):
        return self.__cap_height_nibs

    cap_height = property(get_cap_height, set_cap_height)

    def set_descent(self, height):
        self.__descent_height_nibs = height
        self.__descent_height_pixels = height * self.__nib_width

    def get_descent(self):
        return self.__descent_height_nibs

    descent_height = property(get_descent, set_descent)

    def set_gap(self, height):
        self.__gap_height_nibs = height
        self.__gap_height_pixels = height * self.__nib_width

    def get_gap(self):
        return self.__gap_height_nibs

    gap_height = property(get_gap, set_gap)

    def set_nominal_width(self, new_width):
        self.__width_nibs = new_width
        self.__base_width_pixels = new_width * self.__nib_width
        self.__half_base_width_pixels = self.__base_width_pixels / 2

    def get_nominal_width(self):
        return self.__width_nibs

    nominal_width = property(get_nominal_width, set_nominal_width)

    def set_nib_width(self, new_nib_width):
        self.__nib_width = new_nib_width
        self.__base_width_pixels = new_nib_width * self.__width_nibs
        self.__half_base_width_pixels = new_nib_width * self.__width_nibs / 2
        self.__base_height_pixels = new_nib_width * self.__base_height_nibs
        self.__ascent_height_pixels = new_nib_width * \
            (self.__ascent_height_nibs + self.__base_height_nibs)
        self.__descent_height_pixels = new_nib_width * self.__descent_height_nibs
        self.__cap_height_pixels = new_nib_width * \
            (self.__cap_height_nibs + self.__base_height_nibs)
        self.__gap_height_pixels = new_nib_width * self.__gap_height_nibs

    def get_nib_width(self):
        return self.__nib_width

    nib_width = property(get_nib_width, set_nib_width)

    def draw(self, gc, size, origin, nib=None):

        nib_width = 20 #nib.getWidth() << 1

        if self.__last_nib_width != nib_width:
            self.__last_nib_width = nib_width
            self.nib_width = nib_width

        scale = gc.worldTransform().m11()

        csize = QtCore.QSize(size.width() / scale, size.height() / scale)

        coords_rect = QtCore.QRect(-origin.x() / scale, -origin.y() / scale, \
            csize.width(), csize.height())

        top_x = self.__angle_dx * origin.y() / scale
        top_y = coords_rect.topLeft().y()
        bot_x = -(self.__angle_dx * (csize.height() - origin.y() / scale))
        bot_y = coords_rect.bottomRight().y()
        gc.setPen(self.__line_pen)
        gc.drawLine(bot_x, bot_y, top_x, top_y)

        # horizontal grid
        dist = self.__base_width_pixels
        gc.drawLine(bot_x-dist, bot_y, top_x-dist, top_y)
        pos = dist
        gc.setPen(self.__line_pen_lt)

        while pos < csize.width():
            gc.drawLine(bot_x+pos, bot_y, top_x+pos, top_y)
            pos = pos + dist
            gc.drawLine(bot_x-pos, bot_y, top_x-pos, top_y)

        # baseline
        gc.setPen(self.__line_pen_2)
        gc.drawLine(coords_rect.topLeft().x(), 0, coords_rect.bottomRight().x(), 0)

        # base height line
        gc.setPen(self.__line_pen)
        gc.drawLine(coords_rect.topLeft().x(), -self.__base_height_pixels, \
            coords_rect.bottomRight().x(), -self.__base_height_pixels)

        gc.drawLine(coords_rect.topLeft().x(), -self.__ascent_height_pixels, \
            coords_rect.bottomRight().x(), -self.__ascent_height_pixels)
        gc.drawLine(coords_rect.topLeft().x(), self.__descent_height_pixels, \
            coords_rect.bottomRight().x(), self.__descent_height_pixels)

        gc.setPen(self.__line_pen_dotted)
        gc.drawLine(coords_rect.topLeft().x(), -self.__cap_height_pixels, \
            coords_rect.bottomRight().x(), -self.__cap_height_pixels)

        gc.setBrush(self.__spacer_brush)
        gc.drawRect(coords_rect.topLeft().x(), self.__descent_height_pixels, \
            csize.width(), self.__gap_height_pixels)

        vpos = -self.__ascent_height_pixels - self.__gap_height_pixels - \
            self.__descent_height_pixels

        while vpos+self.__descent_height_pixels > coords_rect.topLeft().y():
            gc.setPen(self.__line_pen_2)
            gc.drawLine(coords_rect.topLeft().x(), vpos, coords_rect.bottomRight().x(), vpos)

            gc.setPen(self.__line_pen)
            gc.drawLine(coords_rect.topLeft().x(), vpos-self.__base_height_pixels, \
                coords_rect.bottomRight().x(), vpos-self.__base_height_pixels)

            gc.drawLine(coords_rect.topLeft().x(), vpos-self.__ascent_height_pixels, \
                coords_rect.bottomRight().x(), vpos-self.__ascent_height_pixels)
            gc.drawLine(coords_rect.topLeft().x(), vpos+self.__descent_height_pixels, \
                coords_rect.bottomRight().x(), vpos+self.__descent_height_pixels)

            gc.setPen(self.__line_pen_dotted)
            gc.drawLine(coords_rect.topLeft().x(), vpos-self.__cap_height_pixels, \
                coords_rect.bottomRight().x(), vpos-self.__cap_height_pixels)

            gc.setBrush(self.__spacer_brush)
            gc.drawRect(coords_rect.topLeft().x(), vpos+self.__descent_height_pixels, \
                csize.width(), self.__gap_height_pixels)
            vpos = vpos -self.__ascent_height_pixels - self.__gap_height_pixels - \
            self.__descent_height_pixels

        vpos = self.__ascent_height_pixels + self.__gap_height_pixels + \
            self.__descent_height_pixels
        while vpos-self.__ascent_height_pixels < coords_rect.bottomRight().y():
            gc.setPen(self.__line_pen_2)
            gc.drawLine(coords_rect.topLeft().x(), vpos, coords_rect.bottomRight().x(), vpos)

            gc.setPen(self.__line_pen)
            gc.drawLine(coords_rect.topLeft().x(), vpos-self.__base_height_pixels, \
                coords_rect.bottomRight().x(), vpos-self.__base_height_pixels)

            gc.drawLine(coords_rect.topLeft().x(), vpos-self.__ascent_height_pixels, \
                coords_rect.bottomRight().x(), vpos-self.__ascent_height_pixels)
            gc.drawLine(coords_rect.topLeft().x(), vpos+self.__descent_height_pixels, \
                coords_rect.bottomRight().x(), vpos+self.__descent_height_pixels)

            gc.setPen(self.__line_pen_dotted)
            gc.drawLine(coords_rect.topLeft().x(), vpos-self.__cap_height_pixels, \
                coords_rect.bottomRight().x(), vpos-self.__cap_height_pixels)

            gc.setBrush(self.__spacer_brush)
            gc.drawRect(coords_rect.topLeft().x(), vpos+self.__descent_height_pixels, \
                csize.width(), self.__gap_height_pixels)
            vpos = vpos + self.__ascent_height_pixels + self.__gap_height_pixels + \
                self.__descent_height_pixels

        gc.setPen(self.__line_pen)
