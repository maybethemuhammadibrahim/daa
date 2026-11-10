import sys
from math import sqrt

sys.setrecursionlimit(10000)


def sort_x(X, Y, tx, ty, l, r):
    if r - l <= 8:
        for i in range(l + 1, r):
            a, b = X[i], Y[i]
            j = i - 1
            while j >= l and X[j] > a:
                X[j + 1] = X[j]
                Y[j + 1] = Y[j]
                j -= 1
            X[j + 1] = a
            Y[j + 1] = b
        return
    mid = (l + r) // 2
    sort_x(X, Y, tx, ty, l, mid)
    sort_x(X, Y, tx, ty, mid, r)
    i, j, k = l, mid, l
    while i < mid and j < r:
        if X[i] <= X[j]:
            tx[k] = X[i]
            ty[k] = Y[i]
            i += 1
        else:
            tx[k] = X[j]
            ty[k] = Y[j]
            j += 1
        k += 1
    while i < mid:
        tx[k] = X[i]
        ty[k] = Y[i]
        i += 1
        k += 1
    while j < r:
        tx[k] = X[j]
        ty[k] = Y[j]
        j += 1
        k += 1
    X[l:r] = tx[l:r]
    Y[l:r] = ty[l:r]


# returns (d2, x1, y1, x2, y2), range is left sorted by y afterwards
def rec(X, Y, tx, ty, l, r, depth, steps):
    n = r - l
    if n <= 3:
        best = (float("inf"), 0, 0, 0, 0)
        for i in range(l, r):
            for j in range(i + 1, r):
                dx = X[i] - X[j]
                dy = Y[i] - Y[j]
                dd = dx * dx + dy * dy
                if dd < best[0]:
                    best = (dd, X[i], Y[i], X[j], Y[j])
        for i in range(l + 1, r):
            a, b = X[i], Y[i]
            j = i - 1
            while j >= l and Y[j] > b:
                X[j + 1] = X[j]
                Y[j + 1] = Y[j]
                j -= 1
            X[j + 1] = a
            Y[j + 1] = b
        if steps is not None:
            pair = None
            if n >= 2:
                pair = ((best[1], best[2]), (best[3], best[4]))
            steps.append({"type": "base", "l": l, "r": r, "d": sqrt(best[0]) if n >= 2 else None,
                          "pair": pair, "depth": depth})
        return best

    mid = (l + r) // 2
    midx = X[mid]
    if steps is not None:
        steps.append({"type": "divide", "l": l, "r": r, "mid": mid, "midx": midx, "depth": depth})
    left = rec(X, Y, tx, ty, l, mid, depth + 1, steps)
    right = rec(X, Y, tx, ty, mid, r, depth + 1, steps)
    best = left if left[0] <= right[0] else right
    d2 = best[0]

    # merge by y
    i, j, k = l, mid, l
    while i < mid and j < r:
        if Y[i] <= Y[j]:
            tx[k] = X[i]
            ty[k] = Y[i]
            i += 1
        else:
            tx[k] = X[j]
            ty[k] = Y[j]
            j += 1
        k += 1
    while i < mid:
        tx[k] = X[i]
        ty[k] = Y[i]
        i += 1
        k += 1
    while j < r:
        tx[k] = X[j]
        ty[k] = Y[j]
        j += 1
        k += 1
    X[l:r] = tx[l:r]
    Y[l:r] = ty[l:r]

    sx = []
    sy = []
    for i in range(l, r):
        dx = X[i] - midx
        if dx * dx < d2:
            sx.append(X[i])
            sy.append(Y[i])
    m = len(sx)
    d_old = sqrt(d2)
    for i in range(m):
        j = i + 1
        while j < m and (sy[j] - sy[i]) ** 2 < d2:
            dx = sx[i] - sx[j]
            dy = sy[i] - sy[j]
            dd = dx * dx + dy * dy
            if dd < d2:
                d2 = dd
                best = (dd, sx[i], sy[i], sx[j], sy[j])
            j += 1
    if steps is not None:
        steps.append({"type": "strip", "l": l, "r": r, "midx": midx, "d": d_old,
                      "strip": [(sx[i], sy[i]) for i in range(m)],
                      "pair": ((best[1], best[2]), (best[3], best[4])),
                      "new_d": sqrt(d2), "depth": depth})
    return best


def closest_pair(pts, steps=None):
    n = len(pts)
    X = [p[0] for p in pts]
    Y = [p[1] for p in pts]
    tx = [0] * n
    ty = [0] * n
    sort_x(X, Y, tx, ty, 0, n)
    if steps is not None:
        steps.append({"type": "sorted", "pts": [(X[i], Y[i]) for i in range(n)]})
    best = rec(X, Y, tx, ty, 0, n, 0, steps)
    return sqrt(best[0]), (best[1], best[2]), (best[3], best[4])
