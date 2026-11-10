import os
import random
import sys
import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from closest_pair.cp import closest_pair
from closest_pair.cp_view import show_cp_steps
from closest_pair.gen_cp import make_custom as make_cp
from karatsuba.gen_im import make_custom as make_im
from karatsuba.im_view import show_im_steps
from karatsuba.kara import multiply

sys.set_int_max_str_digits(0)

DATA = "data"
STEP_MAX_POINTS = 200
STEP_MAX_DIGITS = 200
SPEEDS = [0.2, 0.4, 0.6, 1.0, 1.5, 2.0]

ALGOS = {"Closest pair of points": "cp", "Karatsuba multiplication": "im"}
SOURCES = {
    "premade": ":material/folder_open: Premade file",
    "random": ":material/casino: Random input",
    "upload": ":material/upload_file: Upload a file",
}

st.set_page_config(page_title="DAA Project", page_icon=":material/account_tree:", layout="wide")


@st.cache_data
def read_file(path, mtime):
    with open(path) as f:
        text = f.read()
    lines = text.split()
    if len(text.split("\n")) <= 3 and len(lines) == 2:
        return {"kind": "im", "a": lines[0], "b": lines[1]}
    n = int(lines[0])
    pts = []
    for i in range(n):
        pts.append((float(lines[1 + 2 * i]), float(lines[2 + 2 * i])))
    return {"kind": "cp", "pts": pts}


@st.cache_data
def file_size_of(path, mtime, code):
    # input size without parsing the whole file: points for cp, longest number for im
    with open(path) as f:
        if code == "cp":
            return int(f.readline())
        return max(len(line.strip()) for line in f)


def limit_of(code):
    return STEP_MAX_POINTS if code == "cp" else STEP_MAX_DIGITS


def size_text(code, n):
    return "{:,} points".format(n) if code == "cp" else "{:,} digits".format(n)


def scroll_to(anchor, run_id):
    # runs in the page itself, waits for the heading to exist, then scrolls to it.
    # run_id makes the script unique so it runs again on every new Run.
    st.html("""<script>
    (function () {
      var tries = 0;  // run %d
      function go() {
        var el = document.getElementById("%s");
        if (el) { el.scrollIntoView({behavior: "smooth", block: "start"}); return; }
        if (++tries < 50) setTimeout(go, 100);
      }
      go();
    })();
    </script>""" % (run_id, anchor), unsafe_allow_javascript=True)


def pick_input(code):
    """Step 2. Returns the chosen file name, or None."""
    source = st.segmented_control("Input", list(SOURCES), format_func=SOURCES.get,
                                  default="premade", required=True, key="source",
                                  label_visibility="collapsed")
    if source == "premade":
        premade = [f for f in sorted(os.listdir(DATA))
                   if f.startswith(code) and f.endswith(".txt") and f[2:4].isdigit()]
        if not premade:
            st.warning("No premade files in data/. Run the generators first (see README).")
            return None

        def label(f):
            p = os.path.join(DATA, f)
            n = file_size_of(p, os.path.getmtime(p), code)
            tag = "dry run available" if n <= limit_of(code) else "result only"
            return "%s  ·  %s  ·  %s" % (f, size_text(code, n), tag)

        return st.selectbox("File", premade, format_func=label, key="premade_" + code)

    if source == "random":
        label = "Number of points" if code == "cp" else "Digits in each number"
        d1, d2, d3 = st.columns([2, 2, 1], vertical_alignment="bottom")
        size = d1.number_input(label, min_value=2, value=100, step=1,
                               help="Up to %d gives a step-by-step dry run." % limit_of(code))
        seed = d2.number_input("Seed", min_value=0, value=1, step=1)
        if d3.button("Generate", icon=":material/refresh:", width="stretch"):
            name = "custom_%s_%d_%d.txt" % (code, size, seed)
            if code == "cp":
                make_cp(int(size), int(seed), os.path.join(DATA, name))
            else:
                make_im(int(size), int(seed), os.path.join(DATA, name))
            st.session_state["custom_" + code] = name
        fname = st.session_state.get("custom_" + code)
        if fname is None:
            st.caption("Pick a size and a seed, then press Generate.")
        return fname

    up = st.file_uploader("Text file in the same format as the premade files", type=["txt"])
    if up is None:
        return None
    name = "uploaded_" + up.name
    with open(os.path.join(DATA, name), "wb") as f:
        f.write(up.getvalue())
    return name


def dry_run_panel(code, n, small):
    """Step 3 left side: says plainly whether the dry run will play. Returns True if it will."""
    limit = limit_of(code)
    unit = "points" if code == "cp" else "digits"
    if not small:
        st.toggle("Step-by-step dry run", value=False, disabled=True, key="dry_off")
        st.badge("Result and time only", icon=":material/speed:", color="orange")
        st.caption("This input has %s. The dry run is only for inputs up to %d %s, "
                   "so Run shows the answer and the running time." % (size_text(code, n), limit, unit))
        return False
    dry = st.toggle("Step-by-step dry run", value=True, key="dry_on")
    if dry:
        st.badge("Dry run will play", icon=":material/play_circle:", color="green")
        st.caption("%s is within the %d %s limit. After Run the page scrolls down to the steps "
                   "and plays them by itself. Pause any time and step by hand."
                   % (size_text(code, n).capitalize(), limit, unit))
    else:
        st.badge("Result and time only", icon=":material/speed:", color="gray")
        st.caption("Turn the switch on to watch the algorithm step by step.")
    return dry


def no_dry_run_reason(res):
    code, n = res["kind"], res["n"]
    if res["small"]:
        return ("**No step-by-step dry run:** it was switched off in step 3. "
                "Turn it on and press Run again to watch the steps.")
    unit = "points" if code == "cp" else "digits"
    what = "the closest pair" if code == "cp" else "the product"
    extra = " The plot below shows a sample of the points with the closest pair in red." \
        if code == "cp" else ""
    return ("**No step-by-step dry run for this input.** It has %s, and the dry run is only for "
            "inputs up to %d %s. Bigger inputs make too many recursive calls to follow one by one "
            "(and recording every step would slow the run down), so only %s and the running "
            "time are shown.%s"
            % (size_text(code, n), limit_of(code), unit, what, extra))


def run_page():
    with st.container(border=True):
        st.markdown("**1. Algorithm**")
        algo = st.segmented_control("Algorithm", list(ALGOS), default=list(ALGOS)[0],
                                    required=True, key="algo", label_visibility="collapsed")
        code = ALGOS[algo]

    with st.container(border=True):
        st.markdown("**2. Input**")
        fname = pick_input(code)
        if fname is None:
            return
        path = os.path.join(DATA, fname)
        inp = read_file(path, os.path.getmtime(path))
        if inp["kind"] != code:
            st.error("This file holds %s input, but %s is selected. Pick the other algorithm "
                     "in step 1, or choose another file." % (
                         "closest pair" if inp["kind"] == "cp" else "integer multiplication",
                         algo.lower()))
            return
        if code == "cp":
            n = len(inp["pts"])
        else:
            n = max(len(inp["a"]), len(inp["b"]))
        small = n <= limit_of(code)
        if code == "cp":
            detail = size_text(code, n)
        else:
            detail = "%s and %s digits" % ("{:,}".format(len(inp["a"])), "{:,}".format(len(inp["b"])))
        st.caption(":material/description: **%s**  ·  %s  ·  %.1f KB"
                   % (fname, detail, os.path.getsize(path) / 1024))

    with st.container(border=True):
        st.markdown("**3. Run**")
        left, right = st.columns([3, 2], gap="large")
        with left:
            dry = dry_run_panel(code, n, small)
        with right:
            speed = 0.6
            cutoff = 10
            if dry:
                speed = st.select_slider("Seconds per step", SPEEDS, value=0.6, key="opt_speed")
                if code == "im":
                    cutoff = st.number_input("Schoolbook below (digits)", min_value=2, value=10,
                                             step=1, key="opt_cutoff",
                                             help="Smaller numbers than this are multiplied the "
                                                  "schoolbook way. Lower it to see more splits.")
        label = "Run and play the dry run" if dry else "Run"
        clicked = st.button(label, type="primary", icon=":material/play_arrow:", width="stretch")

    if clicked:
        res = {"file": fname, "kind": code, "steps": [] if dry else None, "n": n, "small": small}
        t = time.perf_counter()
        with st.spinner("Running %s on %s..." % (algo.lower(), fname)):
            if code == "cp":
                res["d"], res["p1"], res["p2"] = closest_pair(inp["pts"], res["steps"])
            elif dry:
                res["prod"] = multiply(inp["a"], inp["b"], 10, int(cutoff), res["steps"])
            else:
                res["prod"] = multiply(inp["a"], inp["b"])
        res["time"] = time.perf_counter() - t
        st.session_state["res"] = res
        st.session_state["run_id"] = st.session_state.get("run_id", 0) + 1
        st.session_state["scroll"] = "dry-run" if dry else "result"
        if dry:
            # start the step view playing on its own. The view moves one step
            # forward before drawing, so -1 makes the first frame step 0.
            st.session_state[code + "_k"] = -1
            st.session_state[code + "_play"] = True
            st.session_state[code + "_delay"] = speed
        else:
            for key in (code + "_k", code + "_play"):
                st.session_state.pop(key, None)

    res = st.session_state.get("res")
    if not res or res["file"] != fname or res["kind"] != code:
        return

    st.subheader("Result", anchor="result")
    if res["steps"] is None:
        st.info(no_dry_run_reason(res), icon=":material/info:")
    c1, c2, c3 = st.columns(3)
    c1.metric("Running time", "%.3f s" % res["time"])
    if res["kind"] == "cp":
        c2.metric("Distance", "%.6f" % res["d"])
        c3.caption("Closest pair")
        c3.markdown("`%s`  \n`%s`" % (res["p1"], res["p2"]))
    else:
        p = res["prod"]
        c2.metric("Product digits", "{:,}".format(len(p)))
        st.markdown("First 50 digits: `%s`  \nLast 50 digits: `%s`" % (p[:50], p[-50:]))
        st.download_button("Download full product", p, file_name=fname[:-4] + "_product.txt",
                           icon=":material/download:")

    if res["steps"] is not None:
        st.subheader("Dry run", anchor="dry-run")
        if res["kind"] == "cp":
            show_cp_steps(inp["pts"], res["steps"])
        else:
            show_im_steps(inp["a"], inp["b"], res["steps"])
    elif res["kind"] == "cp":
        pts = inp["pts"]
        if len(pts) > 5000:
            pts = random.Random(0).sample(pts, 5000)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[p[0] for p in pts], y=[p[1] for p in pts], mode="markers",
                                 marker=dict(color="lightgrey", size=4), name="points (sample)"))
        fig.add_trace(go.Scatter(x=[res["p1"][0], res["p2"][0]], y=[res["p1"][1], res["p2"][1]],
                                 mode="lines+markers", line=dict(color="red"),
                                 marker=dict(size=10), name="closest pair"))
        fig.update_layout(height=500)
        st.plotly_chart(fig, width="stretch")

    target = st.session_state.pop("scroll", None)
    if target:
        scroll_to(target, st.session_state["run_id"])


def benchmark_page():
    for csvname, title, col in (("cp_results.csv", "Closest pair", "n"),
                                ("im_results.csv", "Karatsuba", "len_a")):
        p = os.path.join("results", csvname)
        if not os.path.exists(p):
            continue
        df = pd.read_csv(p, dtype=str)
        df["time_s"] = df["time_s"].astype(float)
        st.subheader(title)
        st.dataframe(df, width="stretch")
        fig = go.Figure(go.Bar(x=df["file"] + " (" + df[col].astype(str) + ")", y=df["time_s"]))
        fig.update_layout(height=350, xaxis_title="file (input size)", yaxis_title="time (s)")
        st.plotly_chart(fig, width="stretch")


os.makedirs(DATA, exist_ok=True)
st.title("Divide and conquer, step by step")
st.caption("Closest pair of points and Karatsuba multiplication. Inputs up to %d points or %d digits "
           "can be watched as a step-by-step dry run, bigger ones show the answer and running time."
           % (STEP_MAX_POINTS, STEP_MAX_DIGITS))

run_tab, bench_tab = st.tabs([":material/play_circle: Run an algorithm",
                              ":material/bar_chart: Benchmark results"])
with run_tab:
    run_page()
with bench_tab:
    benchmark_page()
