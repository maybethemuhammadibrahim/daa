import csv
import os
import sys
from math import sqrt
from scipy.spatial import cKDTree

sys.set_int_max_str_digits(0)


def read_pts(path):
    f = open(path)
    n = int(f.readline())
    pts = []
    for _ in range(n):
        x, y = f.readline().split()
        pts.append((float(x), float(y)))
    f.close()
    return pts


def brute(pts):
    best = float("inf")
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dx = pts[i][0] - pts[j][0]
            dy = pts[i][1] - pts[j][1]
            best = min(best, dx * dx + dy * dy)
    return sqrt(best)


def main():
    lines = ["# Results summary", "", "## Closest pair", "",
             "| file | n | closest distance | time (s) | verified |", "|---|---|---|---|---|"]
    allok = True
    for row in csv.DictReader(open(os.path.join("results", "cp_results.csv"))):
        pts = read_pts(os.path.join("data", row["file"] + ".txt"))
        if len(pts) <= 10000:
            exp = brute(pts)
        else:
            dist, _ = cKDTree(pts).query(pts, k=2)
            exp = min(dist[:, 1])
        d = float(row["distance"])
        ok = abs(d - exp) < 1e-5
        allok = allok and ok
        print(row["file"], d, exp, ok)
        lines.append("| %s | %s | %s | %s | %s |" % (row["file"], row["n"], row["distance"],
                                                     row["time_s"], "✓" if ok else "✗"))
    lines += ["", "## Integer multiplication", "",
              "| file | digits a | digits b | product digits | time (s) | verified |",
              "|---|---|---|---|---|---|"]
    for row in csv.DictReader(open(os.path.join("results", "im_results.csv"))):
        f = open(os.path.join("data", row["file"] + ".txt"))
        a = int(f.readline())
        b = int(f.readline())
        f.close()
        prod = open(os.path.join("results", row["file"] + "_product.txt")).read().strip()
        ok = prod == str(a * b)
        allok = allok and ok
        print(row["file"], ok)
        lines.append("| %s | %s | %s | %s | %s | %s |" % (row["file"], row["len_a"], row["len_b"],
                                                          row["len_product"], row["time_s"],
                                                          "✓" if ok else "✗"))
    with open(os.path.join("results", "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("all ok" if allok else "SOME FAILED")


if __name__ == "__main__":
    main()
