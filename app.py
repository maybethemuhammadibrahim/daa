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

st.set_page_config(page_title="DAA Project", layout="wide")
st.title("Divide and conquer, step by step")
st.caption("Choose an algorithm, choose an input, then press Run. "
           "Small inputs are shown step by step, large ones show the answer and running time.")


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



os.makedirs(DATA, exist_ok=True)
ALGOS = {"Closest pair of points": "cp", "Karatsuba multiplication": "im"}

with st.container(border=True):
    c1, c2 = st.columns([1, 2])
    algo = c1.selectbox("Algorithm", list(ALGOS))
    code = ALGOS[algo]
    source = c2.radio("Input", ["Premade file", "Custom random input", "Upload a file"],
                      horizontal=True)
    # premade = the cpNN / imNN files
    premade = []
    for f in sorted(os.listdir(DATA)):
        if f.startswith(code) and f.endswith(".txt") and f[2:4].isdigit():
            premade.append(f)
    fname = None
    if source == "Premade file":
        if premade:
            fname = st.selectbox("File", premade, key="premade_" + code)
        else:
            st.warning("No premade files in data/, run the generators first")
    elif source == "Custom random input":
        label = "Number of points" if code == "cp" else "Digits in each number"
        d1, d2, d3 = st.columns([2, 2, 1])
        size = d1.number_input(label, min_value=2, value=100, step=1)
        seed = d2.number_input("Seed", min_value=0, value=1, step=1)
        d3.write("")
        d3.write("")
        if d3.button("Generate"):
            name = "custom_%s_%d_%d.txt" % (code, size, seed)
            if code == "cp":
                make_cp(int(size), int(seed), os.path.join(DATA, name))
            else:
                make_im(int(size), int(seed), os.path.join(DATA, name))
            st.session_state["custom_" + code] = name
        fname = st.session_state.get("custom_" + code)
        if fname is None:
            st.info("Pick a size and seed, then press Generate")
    else:
        up = st.file_uploader("Text file in the same format as the premade files", type=["txt"])
        if up is not None:
            name = "uploaded_" + up.name
            with open(os.path.join(DATA, name), "wb") as f:
                f.write(up.getvalue())
            fname = name

if fname is None:
    st.stop()
path = os.path.join(DATA, fname)
inp = read_file(path, os.path.getmtime(path))
if inp["kind"] != code:
    st.error("This file holds %s input, but %s is selected. Change the algorithm or the file." % (
        "closest pair" if inp["kind"] == "cp" else "integer multiplication", algo))
    st.stop()
size_kb = os.path.getsize(path) / 1024

st.subheader(fname)
c1, c2, c3 = st.columns(3)
if inp["kind"] == "cp":
    c1.metric("Points", len(inp["pts"]))
    small = len(inp["pts"]) <= STEP_MAX_POINTS
else:
    c1.metric("Digits", "%d and %d" % (len(inp["a"]), len(inp["b"])))
    small = max(len(inp["a"]), len(inp["b"])) <= STEP_MAX_DIGITS
c2.metric("File size", "%.1f KB" % size_kb)
c3.metric("Mode", "Step by step" if small else "Result and time")
if small:
    st.info("This input is small, so Run will show the algorithm as an animation. "
            "You can pause it and step through by hand.")
else:
    st.info("This input is large, so Run will show only the result and the running time.")


tab1, tab2 = st.tabs(["Run", "Benchmark results"])

with tab1:
    cutoff = 10
    if inp["kind"] == "im" and small:
        cutoff = st.number_input("Step mode cutoff (digits, schoolbook below this)",
                                 min_value=2, value=10, step=1)
    if st.button("Run"):
        res = {"file": fname, "kind": inp["kind"], "small": small, "steps": None}
        if small:
            res["steps"] = []
        t = time.perf_counter()
        with st.spinner("Running..."):
            if inp["kind"] == "cp":
                res["d"], res["p1"], res["p2"] = closest_pair(inp["pts"], res["steps"])
            elif small:
                res["prod"] = multiply(inp["a"], inp["b"], 10, int(cutoff), res["steps"])
            else:
                res["prod"] = multiply(inp["a"], inp["b"])
        res["time"] = time.perf_counter() - t
        st.session_state["res"] = res
        for key in ("cp_k", "im_k", "cp_play", "im_play"):
            st.session_state.pop(key, None)

    res = st.session_state.get("res")
    if res and res["file"] == fname:
        c1, c2 = st.columns(2)
        c1.metric("Running time", "%.3f s" % res["time"])
        if res["kind"] == "cp":
            c2.metric("Distance", "%.6f" % res["d"])
            st.write("Closest pair: %s and %s" % (res["p1"], res["p2"]))
        else:
            p = res["prod"]
            c2.metric("Product digits", len(p))
            st.write("First 50 digits: " + p[:50])
            st.write("Last 50 digits: " + p[-50:])
            st.download_button("Download full product", p, file_name=fname[:-4] + "_product.txt")
        if res["steps"] is not None:
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

with tab2:
    for csvname, title, col in (("cp_results.csv", "Closest pair", "n"),
                                ("im_results.csv", "Karatsuba", "len_a")):
        p = os.path.join("results", csvname)
        if os.path.exists(p):
            df = pd.read_csv(p, dtype=str)
            df["time_s"] = df["time_s"].astype(float)
            st.subheader(title)
            st.dataframe(df, width="stretch")
            fig = go.Figure(go.Bar(x=df["file"] + " (" + df[col].astype(str) + ")", y=df["time_s"]))
            fig.update_layout(height=350, xaxis_title="file (input size)", yaxis_title="time (s)")
            st.plotly_chart(fig, width="stretch")
