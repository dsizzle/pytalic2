import math

def first_derivative(points):
    a = points[0]
    b = points[1]
    c = points[2]
    d = points[3]

    return [_pscal(3, _psub(b,a)), _pscal(3, _psub(c,b)), _pscal(3, _psub(d,c))]

def second_derivative(points):
    a = points[0]
    b = points[1]
    c = points[2]

    return [_pscal(2, _psub(b,a)), _pscal(2, _psub(c,b))]

def _padd(point1, point2):
    return [point1[0]+point2[0], point1[1]+point2[1]]

def _psub(point1, point2):
    return [point1[0]-point2[0], point1[1]-point2[1]]

def _pscal(v, point):
    return [v*point[0], v*point[1]]

def roots(v1, v2, v3=None):
    if v3 is None:
        v3x = None
        v3y = None
    else:
        v3x = v3[0]
        v3y = v3[1]

    x = _get_roots(v1[0], v2[0], v3x)
    y = _get_roots(v1[1], v2[1], v3y)

    root_list = []

    for xv in x:
        if xv > 0.1 and xv < 0.9:
            root_list.append(xv)

    for yv in y:
        if yv > 0.1 and yv < 0.9:
            root_list.append(yv)

    return root_list

def _get_roots(v1, v2, v3):
    # is this actually a line?
    if v3 is None:
        return [-v1 / (v2 - v1)]

    # quadratic root finding is not super complex.
    a = v1 - 2*v2 + v3;

    # no root:
    if a == 0:
        return []

    b = 2 * (v2 - v1)
    c = v1
    d = b*b - 4*a*c

    # no root:
    if d < 0:
        return []

    # one root:
    f = -b / (2*a)
    if d == 0:
        return [f]

    # two roots:
    l = math.sqrt(d) / (2*a)
    return [f-l, f+l]

def rotate_verts(verts, angle):
    rot_verts = []

    for vert in verts:
        rot_vert_x = vert[0]*math.cos(angle)-vert[1]*math.sin(angle)
        rot_vert_y = vert[1]*math.cos(angle)+vert[0]*math.sin(angle)

        rot_verts.append([rot_vert_x, rot_vert_y])

    return rot_verts

def _u_cubic(t):
    one_minus_t3 = math.pow(1-t, 3)
    t3 = t*t*t

    return one_minus_t3 / (t3+one_minus_t3)

def _ratio_cubic(t):
    one_minus_t3 = math.pow(1-t, 3)
    t3 = t*t*t

    return math.abs((t3+one_minus_t3-1)/(t3+one_minus_t3))

def _pointC(start, end, t):
    u_t = _u_cubic(t)

    Pstart = _pscal(start, u_t)
    Pend = _pscal(end, 1-u_t)

    return _padd(Pstart, Pend)

def _pointA(B, C, t):
    ratio_inv = 1/_ratio_cubic(t)
    B_C = _psub(B, C)

    return _padd(B, _pscal(B_C, ratio_inv))

def _e12(v1, v2, A, t):
    At = _pscal(A, t)
    A1_t = _pscal(A, 1-t)

    v1_1_t = _pscal(v1, 1-t)
    v2_t = _pscal(v2, t)

    return [_padd(v1_1_t, At), _padd(A1_t, v2_t)]
