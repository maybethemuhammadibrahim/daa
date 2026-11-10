import random
import sys
from karatsuba.kara import multiply

sys.set_int_max_str_digits(0)


def num(rnd, n, kind):
    if kind == 0:
        return str(rnd.randint(1, 9)) + "".join(rnd.choice("0123456789") for _ in range(n - 1))
    if kind == 1:
        return "9" * n
    if kind == 2:
        return "1" + "0" * (n - 1)
    if kind == 3:
        return "0"
    return str(rnd.randint(1, 9)) + "".join(rnd.choice("00000001") for _ in range(n - 1))


def main():
    rnd = random.Random(777)
    total = 300
    bad = 0
    for t in range(total):
        la = rnd.randint(1, 3000)
        lb = rnd.randint(1, 3000) if t % 3 else rnd.randint(1, 20)
        a = num(rnd, la, rnd.randint(0, 4))
        b = num(rnd, lb, rnd.randint(0, 4))
        exp = str(int(a) * int(b))
        got = multiply(a, b)
        ok = got == exp
        if la < 300 and lb < 300:
            ok = ok and multiply(a, b, 10, 2) == exp
        ok = ok and multiply(a, b, 1000, 4) == exp
        if not ok:
            bad += 1
            print("FAIL", la, lb)
    print("passed", total - bad, "of", total)


if __name__ == "__main__":
    main()
