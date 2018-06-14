import math

from PyQt4 import QtCore, QtGui

from model import nibs
import view.shared_qt

class DrawingArea(QtGui.QFrame):
    def __init__(self, parent):
        QtGui.QFrame.__init__(self, parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setMouseTracking(True)

        self.__origin = None
        self.__origin_delta = QtCore.QPoint(0, 0)
        self.__scale = 1.0
        self.__bg_color = QtGui.QColor(240, 240, 230)
        self.__bg_brush = QtGui.QBrush(self.__bg_color, QtCore.Qt.SolidPattern)

        self.__old_view_pos = None
        self.__move_view = False

        self.__guide_lines = None
        self.__draw_guide_lines = True
        self.__draw_nib_guides = True
        self.__symbol = None
        self.__strokes_to_draw = []
        self.__snap_points = []
        initial_nib_width = self.width() / 5
        self.__nib = nibs.Nib(width=initial_nib_width, color=QtGui.QColor(125, 25, 25))
        self.__nib_instance = nibs.Nib(width=initial_nib_width, color=QtGui.QColor(25, 125, 25))
        self.__nib_special = nibs.Nib(width=initial_nib_width, color=QtGui.QColor(25, 25, 125))
        self.__bitmap = None
        self.__bitmap_size = 40

    def resizeEvent(self, event):
        x_pos = (self.__guide_lines.width + self.__guide_lines.left_spacing + \
            self.__guide_lines.right_spacing) * self.__nib.width / 2
        y_pos = (self.__guide_lines.base_height + self.__guide_lines.ascent_height + \
            self.__guide_lines.descent_height) * self.__nib.width / 2
        self.__origin = QtCore.QPoint(self.size().width() / 2 + x_pos, self.size().height() / 2 + y_pos)
        self.repaint()

    def get_bitmap(self):
        return self.__bitmap

    def get_bitmap_size(self):
        return self.__bitmap_size

    def set_bitmap_size(self, new_bitmap_size):
        self.__bitmap_size = new_bitmap_size

    bitmap_size = property(get_bitmap_size, set_bitmap_size)

    def get_scale(self):
        return self.__scale

    def set_scale(self, new_scale):
        self.__scale = new_scale
        if self.__scale < 0.01:
            self.__scale = 0.01
        elif self.__scale > 10.0:
            self.__scale = 10.0

    scale = property(get_scale, set_scale)

    def get_origin_delta(self):
        return self.__origin_delta

    def set_origin_delta(self, new_origin_delta):
        self.__origin_delta = new_origin_delta

    origin_delta = property(get_origin_delta, set_origin_delta)

    def get_origin(self):
        return self.__origin

    def get_draw_guidelines(self):
        return self.__draw_guide_lines

    def set_draw_guidelines(self, value):
        self.__draw_guide_lines = value

    draw_guidelines = property(get_draw_guidelines, set_draw_guidelines)

    def get_draw_nib_guides(self):
        return self.__draw_nib_guides

    def set_draw_nib_guides(self, value):
        self.__draw_nib_guides = value

    draw_nib_guides = property(get_draw_nib_guides, set_draw_nib_guides)

    def set_draw_strokes(self, strokes):
        self.__strokes_to_draw = strokes

    def get_draw_strokes(self):
        return self.__strokes_to_draw

    strokes = property(get_draw_strokes, set_draw_strokes)

    def set_draw_symbol(self, new_symbol):
        self.__symbol = new_symbol

    def get_draw_symbol(self):
        return self.__symbol

    symbol = property(get_draw_symbol, set_draw_symbol)

    def set_snap_points(self, points):
        self.__snap_points = points

    def get_snap_points(self):
        return self.__snap_points

    snap_points = property(get_snap_points, set_snap_points)

    def get_guidelines(self):
        return self.__guide_lines

    def set_guidelines(self, new_guides):
        self.__guide_lines = new_guides

    def get_nib(self):
        return self.__nib

    def set_nib(self, new_nib):
        self.__nib = new_nib

    nib = property(get_nib, set_nib)

    def get_nib_instance(self):
        return self.__nib_instance

    def set_nib_instance(self, new_nib):
        self.__nib_instance = new_nib

    nib_instance = property(get_nib_instance, set_nib_instance)

    def get_normalized_position(self, raw_position):
        norm_position = raw_position
        norm_position = norm_position - self.__origin - self.__origin_delta
        norm_position = norm_position / self.__scale

        norm_position = norm_position - self.symbol.pos

        return norm_position

    def draw_icon(self, dc, strokes_to_draw):
        pixmap = QtGui.QPixmap(self.width(), self.height())

        if dc is None:
            dc = QtGui.QPainter()

        dc.begin(pixmap)
        dc.setRenderHint(QtGui.QPainter.Antialiasing)

        dc.setBackground(self.__bg_brush)
        dc.eraseRect(self.frameRect())
        # for icon only translate to origin, not actual view position

        dc.translate(self.__origin)
        if len(strokes_to_draw) > 0:
            tmp_strokes = strokes_to_draw[:]

            while len(tmp_strokes):
                stroke = tmp_strokes.pop()
                stroke.draw(dc, nib=self.__nib_special) 

        dc.end()

        return pixmap.scaled(self.__bitmap_size, self.__bitmap_size, \
            QtCore.Qt.KeepAspectRatioByExpanding, 1)

    def paintEvent(self, event):
        nib_pixmap = QtGui.QPixmap(20, 2)

        dc = QtGui.QPainter()

        nib_brush = view.shared_qt.BRUSH_GREEN_SOLID 
        dc.begin(nib_pixmap)
        dc.setRenderHint(QtGui.QPainter.Antialiasing)
        dc.setBrush(nib_brush)
        dc.eraseRect(self.frameRect())
        dc.fillRect(self.frameRect(), QtGui.QColor(128, 0, 0, 180))
        dc.end()

        if self.__symbol:
            self.__bitmap = self.draw_icon(dc, self.__symbol.children)

        dc.begin(self)
        dc.setRenderHint(QtGui.QPainter.Antialiasing)

        dc.setBackground(self.__bg_brush)
        dc.eraseRect(self.frameRect())
        dc.save()
        dc.translate(self.__origin + self.__origin_delta)
        dc.scale(self.__scale, self.__scale)

        if self.__draw_guide_lines:
            self.__guide_lines.draw(dc, self.size(), self.__origin + self.__origin_delta)

        if self.__draw_nib_guides:
            nib_guide_width = self.__guide_lines.width
            nib_guide_base_pos_x = 0-(nib_guide_width * 2 * self.__nib.width) - \
                self.__nib.width * 2
            nib_guide_base_pos_y = 0
            nib_guide_base_height = self.__guide_lines.base_height
            nib_guide_ascent_pos_y = nib_guide_base_pos_y - nib_guide_base_height * \
                self.__nib.width * 2
            nib_guide_ascent = self.__guide_lines.ascent_height
            nib_guide_descent = self.__guide_lines.descent_height
            nib_guide_descent_pos_y = nib_guide_base_pos_y + nib_guide_descent * \
                self.__nib.width * 2

            self.__nib.vert_nib_width_scale(dc, nib_guide_base_pos_x, \
                nib_guide_base_pos_y, nib_guide_base_height)
            self.__nib.vert_nib_width_scale(dc, nib_guide_base_pos_x-self.__nib.width*2, \
                nib_guide_ascent_pos_y, nib_guide_ascent)
            self.__nib.vert_nib_width_scale(dc, nib_guide_base_pos_x-self.__nib.width*2, \
                nib_guide_descent_pos_y, nib_guide_descent)
            self.__nib.horz_nib_width_scale(dc, nib_guide_base_pos_x, \
                nib_guide_base_pos_y+self.__nib.width*2, nib_guide_width)

        dc.setPen(view.shared_qt.PEN_LT_GRAY)
        dc.setBrush(view.shared_qt.BRUSH_CLEAR)
        dc.drawEllipse(QtCore.QPoint(0, 0), 10, 10)     

        if self.__symbol:
            self.__symbol.draw(dc, self.__nib, self.__nib_instance)
            
        if len(self.__strokes_to_draw) > 0:
            dc.save()
            dc.translate(self.__symbol.pos)

            tmp_strokes = self.__strokes_to_draw[:]

            while len(tmp_strokes):
                strk = tmp_strokes.pop()
                strk.draw(dc, nib=self.__nib_special)

            dc.restore()
            
        if len(self.__snap_points) > 0:
            dc.setPen(view.shared_qt.PEN_DK_GRAY_DASH_2)
            dc.setBrush(view.shared_qt.BRUSH_CLEAR)

            if len(self.__snap_points) > 1:
                delta = self.__snap_points[0] - self.__snap_points[1]

                vec_length = math.sqrt(delta.x() * delta.x() + delta.y() * delta.y())

                if vec_length != 0:
                    delta = delta * 50 / vec_length
                else:
                    delta = QtCore.QPoint(0, 0)

                dc.drawLine(self.__snap_points[0], self.__snap_points[0] + delta)
                dc.drawLine(self.__snap_points[1], self.__snap_points[1] - delta)
            else:
                dc.drawEllipse(self.__snap_points[0], 20, 20)

        dc.restore()
        dc.end()
        QtGui.QFrame.paintEvent(self, event)


class LayoutArea(QtGui.QFrame):
    def __init__(self, parent):
        QtGui.QFrame.__init__(self, parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setMouseTracking(True)

        self.__origin = None
        self.__origin_delta = QtCore.QPoint(0, 0)
        self.__scale = 1.0
        self.__bg_color = QtGui.QColor(240, 240, 230)
        self.__bg_brush = QtGui.QBrush(self.__bg_color, QtCore.Qt.SolidPattern)

        self.__layout = None
        self.__strokes_to_draw = []

        self.__old_view_pos = None
        self.__move_view = False

        # will we ever need a bitmap?
        self.__bitmap = None

        self.__nib = nibs.Nib(color=QtGui.QColor(125, 25, 25))

    def resizeEvent(self, event):
        self.__origin = QtCore.QPoint(self.size().width()/2, self.size().height()/2)
        self.repaint()

    def get_bitmap(self):
        return self.__bitmap

    def get_scale(self):
        return self.__scale

    def set_scale(self, new_scale):
        self.__scale = new_scale
        if self.__scale < 0.01:
            self.__scale = 0.01
        elif self.__scale > 10.0:
            self.__scale = 10.0

    scale = property(get_scale, set_scale)

    def get_origin_delta(self):
        return self.__origin_delta

    def set_origin_delta(self, new_origin_delta):
        self.__origin_delta = new_origin_delta

    origin_delta = property(get_origin_delta, set_origin_delta)

    def get_origin(self):
        return self.__origin

    def get_nib(self):
        return self.__nib

    def set_nib(self, new_nib):
        self.__nib = new_nib

    nib = property(get_nib, set_nib)

    def get_normalized_position(self, raw_position):
        norm_position = raw_position
        norm_position = norm_position - self.__origin - self.__origin_delta
        norm_position = norm_position / self.__scale

        norm_position = norm_position - self.layout.pos

        return norm_position

    def set_draw_strokes(self, strokes):
        self.__strokes_to_draw = strokes

    def get_draw_strokes(self):
        return self.__strokes_to_draw

    strokes = property(get_draw_strokes, set_draw_strokes)

    def set_layout(self, layout):
        self.__layout = layout

    def get_layout(self):
        return self.__layout

    layout = property(get_layout, set_layout)

    def paintEvent(self, event):
        dc = QtGui.QPainter()

        dc.begin(self)
        dc.setRenderHint(QtGui.QPainter.Antialiasing)

        dc.setBackground(self.__bg_brush)
        dc.eraseRect(self.frameRect())
        dc.save()
        dc.translate(self.__origin + self.__origin_delta)
        dc.scale(self.__scale, self.__scale)

        if self.__layout:
            dc.save()
            dc.translate(self.__layout.pos)

            for symbol in self.__layout.object_list:
                symbol.draw(dc, self.__nib)

            dc.restore()

        dc.restore()
        dc.end()
        QtGui.QFrame.paintEvent(self, event)
