import os
import sys
import time
from karatsuba.kara import multiply

sys.set_int_max_str_digits(0)


def main():
    os.makedirs("results", exist_ok=True)
    out = open(os.path.join("results", "im_results.csv"), "w")
    out.write("file,len_a,len_b,len_product,first_50,last_50,time_s\n")
    for i in range(1, 11):
        name = "im%02d" % i
        f = open(os.path.join("data", name + ".txt"))
        a = f.readline().strip()
        b = f.readline().strip()
        f.close()
        t = time.perf_counter()
        p = multiply(a, b)
        t = time.perf_counter() - t
        row = "%s,%d,%d,%d,%s,%s,%.3f" % (name, len(a), len(b), len(p), p[:50], p[-50:], t)
        print(row)
        out.write(row + "\n")
        out.flush()
        g = open(os.path.join("results", name + "_product.txt"), "w")
        g.write(p + "\n")
        g.close()
    out.close()


if __name__ == "__main__":
    main()
