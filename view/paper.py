import math

from PyQt4 import QtCore, QtGui

from model import nibs
import view.shared_qt

"""
Canvas base class
"""
class Canvas(QtGui.QFrame):
    def __init__(self, parent):
        QtGui.QFrame.__init__(self, parent)
        
        self.__origin = None
        self.__origin_delta = QtCore.QPoint(0, 0)
        self.__scale = 1.0
        self.__bg_color = QtGui.QColor(240, 240, 230)
        self.__bg_brush = QtGui.QBrush(self.__bg_color, QtCore.Qt.SolidPattern)

        self.__guide_lines = None
        self.__draw_guide_lines = True
        self.__draw_nib_guides = True
        
        self.__subject = None

        self.__bitmap = None
        self.__bitmap_size = 40

        self.initial_nib_width = self.width() / 5
        self.__nib = nibs.Nib(width=self.initial_nib_width, color=QtGui.QColor(125, 25, 25))
        
    def resizeEvent(self, event):
        if self.__guide_lines:
            x_pos = (self.__guide_lines.width + self.__guide_lines.left_spacing + \
                self.__guide_lines.right_spacing) * self.__nib.width / 2
            y_pos = (self.__guide_lines.base_height + self.__guide_lines.ascent_height + \
                self.__guide_lines.descent_height) * self.__nib.width / 2
        else:
            x_pos = 0
            y_pos = 0

        self.__origin = QtCore.QPoint(self.size().width() / 2 + x_pos, self.size().height() / 2 + y_pos)
        self.repaint()

    def get_bg_color(self):
        return self.__bg_color

    def set_bg_color(self, new_bg_color):
        self.__bg_color = new_bg_color

    bg_color = property(get_bg_color, set_bg_color)

    @property
    def bg_brush(self):
        return self.__bg_brush

    def get_bitmap_size(self):
        return self.__bitmap_size

    def set_bitmap_size(self, new_bitmap_size):
        self.__bitmap_size = new_bitmap_size

    bitmap_size = property(get_bitmap_size, set_bitmap_size)
    
    def get_bitmap(self):
        return self.__bitmap

    def set_bitmap(self, new_bitmap):
        self.__bitmap = new_bitmap

    bitmap = property(get_bitmap, set_bitmap)

    def get_guidelines(self):
        return self.__guide_lines

    def set_guidelines(self, new_guides):
        self.__guide_lines = new_guides

    guide_lines = property(get_guidelines, set_guidelines)

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

    @property
    def origin(self):
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

        if self.subject:
            norm_position = norm_position - self.subject.pos

        return norm_position

    def set_subject(self, subject):
        self.__subject = subject

    def get_subject(self):
        return self.__subject

    subject = property(get_subject, set_subject)

    def paintEvent(self, event):
        dc = QtGui.QPainter()

        dc.begin(self)
        dc.setRenderHint(QtGui.QPainter.Antialiasing)

        dc.setBackground(self.__bg_brush)
        dc.eraseRect(self.frameRect())
        dc.save()
        dc.translate(self.__origin + self.__origin_delta)
        dc.scale(self.__scale, self.__scale)

        if self.subject:
            dc.save()
            dc.translate(self.subject.pos)

            self.subject.draw(gc)

            dc.restore()

        dc.restore()
        dc.end()
        QtGui.QFrame.paintEvent(self, event)


class DrawingArea(Canvas):
    def __init__(self, parent):
        Canvas.__init__(self, parent)

        self.__strokes_to_draw = []
        self.__snap_points = []

        self.__nib_instance = nibs.Nib(width=self.initial_nib_width, color=QtGui.QColor(25, 125, 25))
        self.__nib_special = nibs.Nib(width=self.initial_nib_width, color=QtGui.QColor(25, 25, 125))

    def set_draw_strokes(self, strokes):
        self.__strokes_to_draw = strokes

    def get_draw_strokes(self):
        return self.__strokes_to_draw

    strokes = property(get_draw_strokes, set_draw_strokes)

    symbol = property(Canvas.get_subject, Canvas.set_subject)

    def set_snap_points(self, points):
        self.__snap_points = points

    def get_snap_points(self):
        return self.__snap_points

    snap_points = property(get_snap_points, set_snap_points)

    def get_nib_instance(self):
        return self.__nib_instance

    def set_nib_instance(self, new_nib):
        self.__nib_instance = new_nib

    nib_instance = property(get_nib_instance, set_nib_instance)

    def get_nib_special(self):
        return self.__nib_special

    def set_nib_special(self, new_nib_special):
        self.__nib_special = new_nib_special

    nib_special = property(get_nib_special, set_nib_special)
    
    def draw_icon(self, dc, strokes_to_draw):
        pixmap = QtGui.QPixmap(self.width(), self.height())

        if dc is None:
            dc = QtGui.QPainter()

        dc.begin(pixmap)
        dc.setRenderHint(QtGui.QPainter.Antialiasing)

        dc.setBackground(self.bg_brush)
        dc.eraseRect(self.frameRect())
        # for icon only translate to origin, not actual view position

        dc.translate(self.origin)
        if len(strokes_to_draw) > 0:
            tmp_strokes = strokes_to_draw[:]

            while len(tmp_strokes):
                stroke = tmp_strokes.pop()
                stroke.draw(dc, nib=self.__nib_special) 

        dc.end()

        return pixmap.scaled(self.bitmap_size, self.bitmap_size, \
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

        if self.symbol:
            self.bitmap = self.draw_icon(dc, self.symbol.children)

        dc.begin(self)
        dc.setRenderHint(QtGui.QPainter.Antialiasing)

        dc.setBackground(self.bg_brush)
        dc.eraseRect(self.frameRect())
        dc.save()
        dc.translate(self.origin + self.origin_delta)
        dc.scale(self.scale, self.scale)

        if self.draw_guidelines:
            self.guide_lines.draw(dc, self.size(), self.origin + self.origin_delta)

        if self.draw_nib_guides:
            nib_guide_width = self.guide_lines.width
            nib_guide_base_pos_x = 0-(nib_guide_width * 2 * self.nib.width) - \
                self.nib.width * 2
            nib_guide_base_pos_y = 0
            nib_guide_base_height = self.guide_lines.base_height
            nib_guide_ascent_pos_y = nib_guide_base_pos_y - nib_guide_base_height * \
                self.nib.width * 2
            nib_guide_ascent = self.guide_lines.ascent_height
            nib_guide_descent = self.guide_lines.descent_height
            nib_guide_descent_pos_y = nib_guide_base_pos_y + nib_guide_descent * \
                self.nib.width * 2

            self.nib.vert_nib_width_scale(dc, nib_guide_base_pos_x, \
                nib_guide_base_pos_y, nib_guide_base_height)
            self.nib.vert_nib_width_scale(dc, nib_guide_base_pos_x-self.nib.width*2, \
                nib_guide_ascent_pos_y, nib_guide_ascent)
            self.nib.vert_nib_width_scale(dc, nib_guide_base_pos_x-self.nib.width*2, \
                nib_guide_descent_pos_y, nib_guide_descent)
            self.nib.horz_nib_width_scale(dc, nib_guide_base_pos_x, \
                nib_guide_base_pos_y+self.nib.width*2, nib_guide_width)

        dc.setPen(view.shared_qt.PEN_LT_GRAY)
        dc.setBrush(view.shared_qt.BRUSH_CLEAR)
        dc.drawEllipse(QtCore.QPoint(0, 0), 10, 10)     

        if self.symbol:
            self.symbol.draw(dc, self.nib, self.__nib_instance)
            
        if len(self.__strokes_to_draw) > 0:
            dc.save()
            dc.translate(self.symbol.pos)

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


class LayoutArea(Canvas):
    def __init__(self, parent):
        Canvas.__init__(self, parent)
        self.__layout = None
        self.__strokes_to_draw = []

    layout = property(Canvas.get_subject, Canvas.set_subject)

    def frame_layout(self):
         max_dim = max(self.frameRect().width(), self.frameRect().height())
         layout_bound = self.layout.bound_rect
         max_layout_dim = max(layout_bound.width(), layout_bound.height())
         if max_layout_dim:
            self.scale = max_dim / max_layout_dim  

            self.origin_delta = QtCore.QPoint(self.origin.x() - self.layout.pos.x() - layout_bound.width() / 2, 0)
            
    def paintEvent(self, event):
        dc = QtGui.QPainter()

        dc.begin(self)
        dc.setRenderHint(QtGui.QPainter.Antialiasing)

        dc.setBackground(self.bg_brush)
        dc.eraseRect(self.frameRect())
        dc.save()
        dc.translate(self.origin + self.origin_delta)
        dc.scale(self.scale, self.scale)

        dc.setPen(view.shared_qt.PEN_LT_GRAY)
        dc.setBrush(view.shared_qt.BRUSH_CLEAR)
        dc.drawEllipse(QtCore.QPoint(0, 0), 10, 10) 

        if self.draw_guidelines and self.guide_lines:
            self.guide_lines.draw(dc, self.size(), self.origin + self.origin_delta)

        if self.layout:
            dc.save()
            dc.translate(self.layout.pos)

            for symbol in self.layout.object_list:
                symbol.draw(dc, self.nib)

            dc.restore()

        dc.restore()
        dc.end()
        QtGui.QFrame.paintEvent(self, event)
