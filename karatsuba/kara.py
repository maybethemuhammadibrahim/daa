import sys

sys.setrecursionlimit(10000)

BASE = 10**9
W = 9
CUTOFF = 32


def parse(s, w=W):
    a = []
    i = len(s)
    while i > 0:
        j = max(0, i - w)
        a.append(int(s[j:i]))
        i = j
    return trim(a)


def tostr(a, w=W):
    a = trim(a[:])
    out = [str(a[-1])]
    for i in range(len(a) - 2, -1, -1):
        out.append(str(a[i]).zfill(w))
    return "".join(out)


def trim(a):
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def add(a, b, base):
    if len(a) < len(b):
        a, b = b, a
    res = []
    carry = 0
    for i in range(len(a)):
        cur = a[i] + carry
        if i < len(b):
            cur += b[i]
        if cur >= base:
            res.append(cur - base)
            carry = 1
        else:
            res.append(cur)
            carry = 0
    if carry:
        res.append(carry)
    return res


# assumes a >= b
def sub(a, b, base):
    res = []
    borrow = 0
    for i in range(len(a)):
        cur = a[i] - borrow
        if i < len(b):
            cur -= b[i]
        if cur < 0:
            cur += base
            borrow = 1
        else:
            borrow = 0
        res.append(cur)
    return trim(res)


def school(a, b, base):
    la, lb = len(a), len(b)
    res = [0] * (la + lb)
    for i in range(la):
        x = a[i]
        if x == 0:
            continue
        carry = 0
        for j in range(lb):
            cur = res[i + j] + x * b[j] + carry
            carry = cur // base
            res[i + j] = cur - carry * base
        res[i + lb] += carry
    return trim(res)


def kara(a, b, base, cutoff, depth, steps):
    la, lb = len(a), len(b)
    w = len(str(base)) - 1
    if min(la, lb) < cutoff:
        res = school(a, b, base)
        if steps is not None:
            steps.append({"type": "base", "depth": depth, "x": tostr(a, w), "y": tostr(b, w),
                          "result": tostr(res, w)})
        return res
    m = min(la, lb) // 2
    alo, ahi = trim(a[:m]), a[m:]
    blo, bhi = trim(b[:m]), b[m:]
    st = None
    if steps is not None:
        st = {"type": "split", "depth": depth, "x": tostr(a, w), "y": tostr(b, w), "m": m,
              "x_hi": tostr(ahi, w), "x_lo": tostr(alo, w),
              "y_hi": tostr(bhi, w), "y_lo": tostr(blo, w)}
        steps.append(st)
    z0 = kara(alo, blo, base, cutoff, depth + 1, steps)
    z2 = kara(ahi, bhi, base, cutoff, depth + 1, steps)
    z1 = kara(add(alo, ahi, base), add(blo, bhi, base), base, cutoff, depth + 1, steps)
    if st is not None:
        st["z1_raw"] = tostr(z1, w)
    z1 = sub(sub(z1, z0, base), z2, base)
    res = add(z0, [0] * m + z1, base)
    res = add(res, [0] * (2 * m) + z2, base)
    res = trim(res)
    if st is not None:
        st["z0"] = tostr(z0, w)
        st["z1"] = tostr(z1, w)
        st["z2"] = tostr(z2, w)
        st["result"] = tostr(res, w)
    return res


def multiply(sa, sb, base=BASE, cutoff=CUTOFF, steps=None):
    w = len(str(base)) - 1
    a = parse(sa, w)
    b = parse(sb, w)
    return tostr(kara(a, b, base, cutoff, 0, steps), w)
