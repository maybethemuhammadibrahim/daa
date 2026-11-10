import random
from math import sqrt
from closest_pair.cp import closest_pair


def brute(pts):
    best = float("inf")
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dx = pts[i][0] - pts[j][0]
            dy = pts[i][1] - pts[j][1]
            best = min(best, dx * dx + dy * dy)
    return sqrt(best)


def main():
    rnd = random.Random(12345)
    bad = 0
    total = 400
    for t in range(total):
        n = rnd.randint(2, 500)
        kind = t % 4
        if kind == 0:
            pts = [(rnd.random() * 1000, rnd.random() * 1000) for _ in range(n)]
        elif kind == 1:
            pts = [(rnd.randint(0, 20), rnd.randint(0, 20)) for _ in range(n)]
        elif kind == 2:
            pts = [(5, rnd.random() * 1000) for _ in range(n)]
        else:
            pts = [(rnd.randint(0, 10**6), rnd.randint(0, 10**6)) for _ in range(n)]
        d, p1, p2 = closest_pair(pts)
        exp = brute(pts)
        real = sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
        if abs(d - exp) > 1e-9 or abs(real - exp) > 1e-9 or p1 not in pts or p2 not in pts:
            bad += 1
            print("FAIL", n, kind, d, exp)
    print("passed", total - bad, "of", total)


if __name__ == "__main__":
    main()
