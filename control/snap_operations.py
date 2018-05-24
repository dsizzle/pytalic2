import math

from PyQt4 import QtCore

SNAP_TO_GRID        = 0x0001
SNAP_TO_AXES        = 0x0002
SNAP_TO_NIB_AXES    = 0x0004
SNAP_TO_CTRL_PTS    = 0x0008
SNAP_TO_STROKES     = 0x0010

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

            if len(cur_view_selection[sel_stroke].keys()) == 1:
                sel_point = cur_view_selection[sel_stroke].keys()[0]

                ctrl_verts = sel_stroke.getCtrlVertices(make_copy=False)

                vert_index = ctrl_verts.index(sel_point)

                if sel_point.isKnotSelected():
                    if vert_index == 0:
                        vert_index += 1
                    else:
                        vert_index -= 1

                vpos = ctrl_verts[vert_index].getHandlePos(2)
                stroke_pos = sel_stroke.getPos()

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

        delta = pos - vert_pos
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

    def snap_to_ctrl_point(self, pos, sel_point, tolerance=10):
        snap_point = QtCore.QPoint(-1, -1)

        test_rect = QtCore.QRect(pos.x()-tolerance/2, pos.y()-tolerance/2, \
            tolerance, tolerance)
        cur_char = self.__main_ctrl.get_current_char()

        for char_stroke in cur_char.strokes:
            for ctrl_vert in char_stroke.getCtrlVertices(False):
                if sel_point is not ctrl_vert:
                    test_point = ctrl_vert.getHandlePos(2)

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

        ascent_height_nibs = guides.ascent_height
        cap_height_nibs = guides.cap_height

        ascent_height_pixels = ascent_height_nibs * nib_width
        descent_height_pixels = guides.descent_height * nib_width
        gap_height_pixels = guides.gap_height * nib_width

        ascent_only = ascent_height_nibs * nib_width
        cap_only = ascent_only - (cap_height_nibs * nib_width)

        y_lines = [0, \
            gap_height_pixels + descent_height_pixels + cap_only, \
            gap_height_pixels + descent_height_pixels + ascent_only, \
            gap_height_pixels + descent_height_pixels, \
            descent_height_pixels]

        width_x = guides.nominal_width * nib_width
        height_y = ascent_height_pixels + gap_height_pixels + descent_height_pixels

        for y_line in y_lines:
            test_y = (test_pt.y() - y_line) % height_y

            y = -1
            if abs(test_y) <= tolerance:
                y = test_pt.y() - test_y
            elif abs(y_line - test_y) <= tolerance:
                y = test_pt.y() - test_y + height_y

            if y != -1:
                dx = 0-int(y * angle_dx)
                test_x = (test_pt.x() - dx) % width_x

                x = -1
                if abs(test_x) <= tolerance:
                    x = test_pt.x() - test_x          
                elif abs(width_x - test_x) <= tolerance:
                    x = test_pt.x() - test_x + width_x

                if x != -1 and (abs(test_pt.x() - x) <= tolerance*2 and \
                    abs(test_pt.y() - y) <= tolerance*2):
                    return QtCore.QPoint(x, y)

        return grid_pt
