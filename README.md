# DAA Project (CS2009, Fall 2026)

Parts 2, 3 and 4: closest pair of points (divide and conquer, O(n log n)) and Karatsuba integer multiplication, with a Streamlit UI that shows the algorithms step by step.

Everything is run from the project root.

## Install

    pip install -r requirements.txt

(`scipy` is only used by `check/verify.py`.)

## Generate data

    python -m closest_pair.gen_cp          # cp01 to cp10 into data/
    python -m karatsuba.gen_im             # im01 to im10 into data/

Custom input (size and seed chosen at run time):

    python -m closest_pair.gen_cp <n> <seed> <outfile>
    python -m karatsuba.gen_im <digits> <seed> <outfile>

Both generators also write `data/seeds.txt`. Files of 1 MB or more are git-ignored (listed in `.gitignore`), regenerate them with the commands above.

## Tests

    python -m closest_pair.test_cp         # vs brute force
    python -m karatsuba.test_im            # vs Python int

## Part 3 (run all 20 files)

    python -m closest_pair.run_cp          # results/cp_results.csv
    python -m karatsuba.run_im             # results/im_results.csv + results/imXX_product.txt

## Verification

    python -m check.verify                 # results/summary.md

## UI (Part 4)

    streamlit run app.py

1. Pick the algorithm.
2. Pick an input: a premade file (cp01 to cp10, im01 to im10), a random input (size and seed), or an uploaded file. A premade file that is not on disk yet (the large, git-ignored ones) can be generated from its seed with one click, the result is identical to running the generator.
3. Press Run.

Inputs up to 200 points / 200 digits get a step-by-step dry run: the page scrolls to it and plays it automatically (pause, previous, next, speed). Closest pair shows the divide line, the strip and the best pair on a plot; Karatsuba shows the recursion tree, the current call split into high and low parts, and the call stack. Bigger inputs show the result, the running time and why there is no dry run. The "Benchmark results" tab shows the Part 3 tables.

The app needs Python 3.11 or newer (`sys.set_int_max_str_digits`).

## Notes for the report

- Karatsuba works on all files up to 1,000,000 digits, no 100,000 digit limit was needed. im04 (1M x 1M digits) took about 200 s in pure Python (limbs of base 10^9, schoolbook below 32 limbs).
- closest pair on 1,000,000 points takes about 15 to 25 s.
- The algorithms use only their own merge sort and own limb arithmetic. Library routines (`int * int`, scipy) are used in `check/verify.py` and the tests only.

## Seeds

| file | seed | content |
|---|---|---|
| cp01 | 101 | n=1000, uniform random reals in [0, 10^6] |
| cp02 | 102 | n=10^4, uniform |
| cp03 | 103 | n=10^5, uniform |
| cp04 | 104 | n=10^6, uniform |
| cp05 | 105 | n=10^6, clustered around 10 centers |
| cp06 | 106 | n=10^6, integers in [0, 500], duplicates |
| cp07 | 107 | n=10^5, all on one vertical line |
| cp08 | 108 | n=10^5, 250 x 400 grid, spacing 10 |
| cp09 | 109 | n=10^6, closest pair straddles the middle split |
| cp10 | 110 | n=101, small demo |
| im01 | 201 | 1000 digits each |
| im02 | 202 | 10^4 digits each |
| im03 | 203 | 10^5 digits each |
| im04 | 204 | 10^6 digits each |
| im05 | 205 | 10^6 digits and 10 digits |
| im06 | 206 | 10^5 digits, one is all 9s |
| im07 | 207 | 99,999 digits, many zeros |
| im08 | 208 | 10^6 digits, both powers of 10 |
| im09 | 209 | one number is 0, other has 10^6 digits |
| im10 | 210 | 101 digits each, small demo |

## Contributions

| member | roll no | github | files | tasks |
|---|---|---|---|---|
| Hasnain | 24K-0516 | Hasnain848 | `closest_pair/` | closest pair algorithm, generator, tests, Part 3 run, step view |
| Obaid | 24K-0793 | Obaid03 | `karatsuba/` | Karatsuba algorithm, generator, tests, Part 3 run, step view |
| Ibrahim | 24K-0649 | maybethemuhammadibrahim | `app.py`, `check/`, `requirements.txt`, `.gitignore`, `README.md` | Streamlit app, verification, repo setup |
