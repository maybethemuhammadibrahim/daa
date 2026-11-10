import os
import time
from closest_pair.cp import closest_pair


def read_pts(path):
    f = open(path)
    n = int(f.readline())
    pts = []
    for _ in range(n):
        x, y = f.readline().split()
        if x.lstrip("-").isdigit() and y.lstrip("-").isdigit():
            pts.append((int(x), int(y)))
        else:
            pts.append((float(x), float(y)))
    f.close()
    return pts


def main():
    os.makedirs("results", exist_ok=True)
    out = open(os.path.join("results", "cp_results.csv"), "w")
    out.write("file,n,p1,p2,distance,time_s,read_time_s\n")
    for i in range(1, 11):
        name = "cp%02d" % i
        t0 = time.perf_counter()
        pts = read_pts(os.path.join("data", name + ".txt"))
        t1 = time.perf_counter()
        d, p1, p2 = closest_pair(pts)
        t2 = time.perf_counter()
        row = "%s,%d,%s,%s,%.6f,%.3f,%.3f" % (name, len(pts), "(%s %s)" % p1, "(%s %s)" % p2,
                                               d, t2 - t1, t1 - t0)
        print(row)
        out.write(row + "\n")
        out.flush()
    out.close()


if __name__ == "__main__":
    main()
