import math

from PyQt4 import QtCore

SNAP_TO_GRID        = 0x0001
SNAP_TO_AXES        = 0x0002
SNAP_TO_NIB_AXES    = 0x0004
SNAP_TO_CTRL_PTS    = 0x0008
SNAP_TO_STROKES     = 0x0010
CONSTRAIN_X         = 0x0020
CONSTRAIN_Y         = 0x0040


class SnapController(object):
    def __init__(self, parent):
        self.__main_ctrl = parent
        self.__snap = SNAP_TO_AXES

    def toggle_snap_axially(self):
        self.__snap ^= SNAP_TO_AXES

    def toggle_snap_to_grid(self):
        self.__snap ^= SNAP_TO_GRID

    def toggle_snap_to_nib_axes(self):
        self.__snap ^= SNAP_TO_NIB_AXES

    def toggle_snap_to_ctrl_pts(self):
        self.__snap ^= SNAP_TO_CTRL_PTS

    def toggle_constrain_x(self):
        self.__snap ^= CONSTRAIN_X

    def toggle_constrain_y(self):
        self.__snap ^= CONSTRAIN_Y

    def is_constrained_x(self):
        return self.__snap & CONSTRAIN_X

    def is_constrained_y(self):
        return self.__snap & CONSTRAIN_Y

    def get_snap(self):
        return self.__snap

    def get_snapped_points(self, pos):
        selection = self.__main_ctrl.get_selection()
        current_view = self.__main_ctrl.get_current_view()
        cur_view_selection = selection[current_view]
        char_set = self.__main_ctrl.get_character_set()

        snapped_points = []

        if len(cur_view_selection.keys()) == 1:
            sel_stroke = cur_view_selection.keys()[0]
            sel_stroke_item = char_set.get_item_by_index(sel_stroke)

            if len(cur_view_selection[sel_stroke].keys()) == 1:
                sel_point = cur_view_selection[sel_stroke].keys()[0]

                ctrl_verts = sel_stroke_item.get_ctrl_vertices(make_copy=False)

                vert_index = ctrl_verts.index(sel_point)

                sel_point_item = char_set.get_item_by_index(sel_point)
                if sel_point_item.is_knot_selected():
                    if vert_index == 0:
                        vert_index += 1
                    else:
                        vert_index -= 1

                vert_item = char_set.get_item_by_index(ctrl_verts[vert_index])
                vpos = vert_item.get_handle_pos(2)
                stroke_pos = sel_stroke_item.pos

                if self.__snap & SNAP_TO_GRID:
                    snap_point = self.closest_grid_point(pos)

                    if snap_point != QtCore.QPoint(-1, -1):
                        snapped_points.append(snap_point)
                        return snapped_points

                if self.__snap & SNAP_TO_AXES:
                    snap_point = self.snap_to_axes(stroke_pos, pos, vpos, \
                        axis_angles=[0-char_set.guide_angle, 90])

                    if snap_point != QtCore.QPoint(-1, -1):
                        snapped_points.append(snap_point)
                        snapped_points.append(vpos + stroke_pos)
                        return snapped_points

                if self.__snap & SNAP_TO_NIB_AXES:
                    snap_point = self.snap_to_axes(stroke_pos, pos, vpos, \
                        axis_angles=[char_set.nib_angle, char_set.nib_angle-90])

                    if snap_point != QtCore.QPoint(-1, -1):
                        snapped_points.append(snap_point)
                        snapped_points.append(vpos + stroke_pos)
                        return snapped_points

                if self.__snap & SNAP_TO_CTRL_PTS:
                    snap_point = self.snap_to_ctrl_point(pos, sel_point)

                    if snap_point != QtCore.QPoint(-1, -1):
                        snapped_points.append(snap_point)
                        return snapped_points

        return snapped_points

    def snap_to_axes(self, stroke_pos, pos, vert_pos, tolerance=10, axis_angles=[]):
        snap_point = QtCore.QPoint(-1, -1)

        if len(axis_angles) == 0:
            return snap_point

        delta = pos - vert_pos - stroke_pos
        vec_length = math.sqrt(float(delta.x())*float(delta.x()) + \
            float(delta.y())*float(delta.y()))

        for angle in axis_angles:

            if delta.y() < 0:
                angle += 180

            new_point = QtCore.QPoint(vec_length * math.sin(math.radians(angle)), \
                vec_length * math.cos(math.radians(angle)))
            new_point = new_point + vert_pos + stroke_pos

            new_delta = pos - new_point

            if abs(new_delta.x()) < tolerance:
                snap_point = new_point

        return snap_point

    def snap_to_ctrl_point(self, pos, sel_point, tolerance=20):
        snap_point = QtCore.QPointF(-1, -1)
        char_set = self.__main_ctrl.get_character_set()

        test_rect = QtCore.QRectF(pos.x()-tolerance/2, pos.y()-tolerance/2, \
            tolerance, tolerance)
        cur_char = self.__main_ctrl.get_current_char()

        for char_stroke in cur_char.strokes:
            char_stroke_item = char_set.get_item_by_index(char_stroke)
            for ctrl_vert in char_stroke_item.get_ctrl_vertices(False):
                if sel_point is not ctrl_vert:
                    ctrl_vert_item = char_set.get_item_by_index(ctrl_vert)
                    test_point = ctrl_vert_item.get_handle_pos(2) + char_stroke_item.pos

                    if test_point in test_rect:
                        snap_point = test_point
                        break

        return snap_point

    def closest_grid_point(self, test_pt, nib_width=0, tolerance=10):
        grid_pt = QtCore.QPoint(-1, -1)

        guides = self.__main_ctrl.get_ui().guide_lines
        nib_width = guides.nib_width
        angle_dx = math.tan(math.radians(guides.guide_angle))

        if nib_width == 0:
            return grid_pt

        ascent_height_pixels = guides.ascent_height * nib_width
        descent_height_pixels = guides.descent_height * nib_width
        gap_height_pixels = guides.gap_height * nib_width

        base_height_pixels = guides.base_height * nib_width
        cap_height_pixels = guides.cap_height * nib_width

        left_space_pixels = guides.left_spacing * nib_width
        right_space_pixels = guides.right_spacing * nib_width

        width_x = guides.width * nib_width
        height_y = base_height_pixels + ascent_height_pixels + \
            gap_height_pixels + descent_height_pixels
        full_width_x = width_x + left_space_pixels + right_space_pixels

        x_lines = [ \
            full_width_x, \
            full_width_x + right_space_pixels, \
            full_width_x + left_space_pixels + right_space_pixels]

        y_lines = [ \
            height_y, \
            height_y + descent_height_pixels, \
            height_y + descent_height_pixels + gap_height_pixels, \
            height_y + descent_height_pixels + gap_height_pixels + \
                (ascent_height_pixels - cap_height_pixels),
            height_y + descent_height_pixels + gap_height_pixels + \
                ascent_height_pixels]

        for y_line in y_lines:
            test_y = (test_pt.y() - y_line) % height_y

            y = -1
            if abs(test_y) <= tolerance:
                y = test_pt.y() - test_y
            elif abs(y_line - test_y) <= tolerance:
                y = test_pt.y() - test_y + height_y

            if y != -1:
                y_dx = int(y * angle_dx)
                for x_line in x_lines:
                    dx = x_line - y_dx
                
                    test_x = (test_pt.x() - dx) % full_width_x

                    x = -1
                    if abs(test_x) <= tolerance:
                        x = test_pt.x() - test_x          
                    elif abs(full_width_x - test_x) <= tolerance:
                        x = test_pt.x() - test_x + full_width_x

                    if x != -1 and (abs(test_pt.x() - x) <= tolerance*2 and \
                        abs(test_pt.y() - y) <= tolerance*2):
                        return QtCore.QPoint(x, y)

        return grid_pt
