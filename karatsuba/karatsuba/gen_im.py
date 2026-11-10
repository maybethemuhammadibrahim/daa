import os
import random
import sys

SEEDS = {"im01": 201, "im02": 202, "im03": 203, "im04": 204, "im05": 205,
         "im06": 206, "im07": 207, "im08": 208, "im09": 209, "im10": 210}

DESC = {
    "im01": "two random numbers, 1000 digits each",
    "im02": "two random numbers, 10000 digits each",
    "im03": "two random numbers, 100000 digits each",
    "im04": "two random numbers, 1000000 digits each",
    "im05": "one random number of 1000000 digits, one of 10 digits",
    "im06": "100000 digits: one number all 9s, one random",
    "im07": "99999 digits (odd length), mostly zeros, first digit nonzero",
    "im08": "1000000 digits: both numbers are powers of 10",
    "im09": "one number is 0, the other has 1000000 digits",
    "im10": "two random numbers, 101 digits each, small demo file",
}

DATA = "data"


def rand_num(rnd, n):
    return str(rnd.randint(1, 9)) + "".join(rnd.choices("0123456789", k=n - 1))


def sparse_num(rnd, n):
    return str(rnd.randint(1, 9)) + "".join(rnd.choices("0000000000123456789", k=n - 1))


def make(name, rnd):
    if name == "im05":
        return rand_num(rnd, 10**6), rand_num(rnd, 10)
    if name == "im06":
        return "9" * 10**5, rand_num(rnd, 10**5)
    if name == "im07":
        return sparse_num(rnd, 99999), sparse_num(rnd, 99999)
    if name == "im08":
        return "1" + "0" * (10**6 - 1), "1" + "0" * (10**6 - 1)
    if name == "im09":
        return "0", rand_num(rnd, 10**6)
    n = {"im01": 1000, "im02": 10**4, "im03": 10**5, "im04": 10**6, "im10": 101}[name]
    return rand_num(rnd, n), rand_num(rnd, n)


def write_nums(path, a, b):
    with open(path, "w") as f:
        f.write(a + "\n" + b + "\n")


def make_custom(digits, seed, path):
    rnd = random.Random(seed)
    write_nums(path, rand_num(rnd, digits), rand_num(rnd, digits))


def update_seeds():
    path = os.path.join(DATA, "seeds.txt")
    old = []
    if os.path.exists(path):
        for line in open(path):
            if not line.startswith("im"):
                old.append(line)
    with open(path, "w") as f:
        f.writelines(old)
        for name in sorted(SEEDS):
            f.write("%s seed=%d  %s\n" % (name, SEEDS[name], DESC[name]))


def main():
    if len(sys.argv) == 4:
        make_custom(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
        return
    os.makedirs(DATA, exist_ok=True)
    for name in sorted(SEEDS):
        rnd = random.Random(SEEDS[name])
        a, b = make(name, rnd)
        write_nums(os.path.join(DATA, name + ".txt"), a, b)
        print(name, len(a), len(b))
    update_seeds()


if __name__ == "__main__":
    main()
