import os
import random
import sys

SEEDS = {"cp01": 101, "cp02": 102, "cp03": 103, "cp04": 104, "cp05": 105,
         "cp06": 106, "cp07": 107, "cp08": 108, "cp09": 109, "cp10": 110}

DESC = {
    "cp01": "n=1000, uniform random real coords in [0, 10^6]",
    "cp02": "n=10000, uniform random real coords in [0, 10^6]",
    "cp03": "n=100000, uniform random real coords in [0, 10^6]",
    "cp04": "n=1000000, uniform random real coords in [0, 10^6]",
    "cp05": "n=1000000, clustered, gaussian (sigma 5000) around 10 random centers",
    "cp06": "n=1000000, integer coords in [0, 500], many duplicates, closest distance 0",
    "cp07": "n=100000, all on the vertical line x=500000, distinct random integer y",
    "cp08": "n=100000, 250 x 400 grid with spacing 10 (many tied closest pairs), shuffled",
    "cp09": "n=1000000, jittered grid plus two very close points straddling the median x",
    "cp10": "n=101, integer coords in [0, 100], small demo file",
}

DATA = "data"


def write_pts(path, pts):
    with open(path, "w") as f:
        f.write(str(len(pts)) + "\n")
        for x, y in pts:
            if isinstance(x, int):
                f.write("%d %d\n" % (x, y))
            else:
                f.write("%.4f %.4f\n" % (x, y))


def uniform(rnd, n):
    return [(round(rnd.random() * 10**6, 4), round(rnd.random() * 10**6, 4)) for _ in range(n)]


def clustered(rnd, n):
    cs = [(rnd.random() * 10**6, rnd.random() * 10**6) for _ in range(10)]
    pts = []
    for i in range(n):
        cx, cy = cs[rnd.randint(0, 9)]
        pts.append((round(rnd.gauss(cx, 5000), 4), round(rnd.gauss(cy, 5000), 4)))
    return pts


def dups(rnd, n):
    return [(rnd.randint(0, 500), rnd.randint(0, 500)) for _ in range(n)]


def vertical(rnd, n):
    ys = rnd.sample(range(10**6), n)
    return [(500000, y) for y in ys]


def grid(rnd, n):
    pts = [(i * 10, j * 10) for i in range(250) for j in range(400)]
    rnd.shuffle(pts)
    return pts


def straddle(rnd, n):
    k = 1000
    pts = []
    for i in range(k):
        for j in range(k):
            if len(pts) < n - 2:
                pts.append((round(i * 1000 + rnd.uniform(-200, 200), 4),
                            round(j * 1000 + rnd.uniform(-200, 200), 4)))
    pts.sort()
    mid = n // 2
    mx = (pts[mid - 2][0] + pts[mid - 1][0]) / 2
    y = round(rnd.uniform(0, 10**6), 4)
    a = (round(mx - 0.005, 4), y)
    b = (round(mx + 0.005, 4), y)
    # base points that could be near the pair
    near = [p for p in pts if abs(p[0] - mx) < 2000]
    for p in near:
        for q in (a, b):
            assert (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 > 1
    pts.append(a)
    pts.append(b)
    pts.sort()
    # really the middle pair after sorting by x
    assert pts[mid - 1] == a and pts[mid] == b
    rnd.shuffle(pts)
    return pts


GEN = {"cp01": (uniform, 1000), "cp02": (uniform, 10**4), "cp03": (uniform, 10**5),
       "cp04": (uniform, 10**6), "cp05": (clustered, 10**6), "cp06": (dups, 10**6),
       "cp07": (vertical, 10**5), "cp08": (grid, 10**5), "cp09": (straddle, 10**6),
       "cp10": (None, 101)}


def make_custom(n, seed, path):
    rnd = random.Random(seed)
    write_pts(path, uniform(rnd, n))


def update_seeds():
    path = os.path.join(DATA, "seeds.txt")
    old = []
    if os.path.exists(path):
        for line in open(path):
            if not line.startswith("cp"):
                old.append(line)
    with open(path, "w") as f:
        for name in sorted(SEEDS):
            f.write("%s seed=%d  %s\n" % (name, SEEDS[name], DESC[name]))
        f.writelines(old)


def main():
    if len(sys.argv) == 4:
        make_custom(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
        return
    os.makedirs(DATA, exist_ok=True)
    for name in sorted(GEN):
        func, n = GEN[name]
        rnd = random.Random(SEEDS[name])
        if name == "cp10":
            pts = [(rnd.randint(0, 100), rnd.randint(0, 100)) for _ in range(n)]
        else:
            pts = func(rnd, n)
        write_pts(os.path.join(DATA, name + ".txt"), pts)
        print(name, len(pts))
    update_seeds()


if __name__ == "__main__":
    main()
