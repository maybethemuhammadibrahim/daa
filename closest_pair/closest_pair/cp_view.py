import streamlit as st
import plotly.graph_objects as go


def move(delta, last):
    k = st.session_state["cp_k"] + delta
    st.session_state["cp_k"] = max(0, min(last, k))


def draw(spts, steps):
    last = len(steps) - 1
    playing = st.session_state["cp_play"]
    if playing:
        if st.session_state["cp_k"] < last:
            st.session_state["cp_k"] += 1
        else:
            st.session_state["cp_play"] = False
            st.rerun()

    c1, c2, c3, c4 = st.columns([1, 1, 1, 5])
    if playing:
        if c1.button("Pause", key="cp_pause"):
            st.session_state["cp_play"] = False
            st.rerun()
    else:
        if c1.button("Play", key="cp_playbtn"):
            if st.session_state["cp_k"] >= last:
                st.session_state["cp_k"] = 0
            st.session_state["cp_play"] = True
            st.rerun()
    c2.button("Prev", on_click=move, args=(-1, last), key="cp_prev", disabled=playing)
    c3.button("Next", on_click=move, args=(1, last), key="cp_next", disabled=playing)
    c4.slider("Step", 0, last, key="cp_k", disabled=playing)
    st.select_slider("Seconds per step", [0.2, 0.4, 0.6, 1.0, 1.5, 2.0], key="cp_delay",
                     disabled=playing)
    k = st.session_state["cp_k"]
    s = steps[k]
    st.write("Step %d of %d" % (k + 1, last + 1) + (" (playing)" if playing else " (paused)"))

    cur = spts[s["l"]:s["r"]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[p[0] for p in spts], y=[p[1] for p in spts], mode="markers",
                             marker=dict(color="lightgrey", size=7), name="all points"))
    fig.add_trace(go.Scatter(x=[p[0] for p in cur], y=[p[1] for p in cur], mode="markers",
                             marker=dict(color="royalblue", size=8), name="current range"))
    if s["type"] == "divide":
        fig.add_vline(x=s["midx"], line_dash="dash", line_color="black")
        text = "Divide: points %d to %d split by index at x = %s (depth %d)" % (
            s["l"], s["r"] - 1, s["midx"], s["depth"])
    elif s["type"] == "base":
        if s["pair"] is None:
            text = "Base case: single point, nothing to compare (depth %d)" % s["depth"]
        else:
            text = "Base case: brute force on %d points, d = %.4f (depth %d)" % (
                s["r"] - s["l"], s["d"], s["depth"])
    else:
        d = s["d"]
        fig.add_vline(x=s["midx"], line_dash="dash", line_color="black")
        fig.add_vrect(x0=s["midx"] - d, x1=s["midx"] + d, fillcolor="orange", opacity=0.2,
                      line_width=0)
        fig.add_trace(go.Scatter(x=[p[0] for p in s["strip"]], y=[p[1] for p in s["strip"]],
                                 mode="markers", marker=dict(color="orange", size=9),
                                 name="strip"))
        text = "Strip check: d from halves = %.4f, strip has %d points, new d = %.4f (depth %d)" % (
            d, len(s["strip"]), s["new_d"], s["depth"])
    if s.get("pair"):
        p, q = s["pair"]
        fig.add_trace(go.Scatter(x=[p[0], q[0]], y=[p[1], q[1]], mode="lines+markers",
                                 line=dict(color="red", width=3), marker=dict(size=11),
                                 name="best pair"))
    fig.update_layout(height=550, margin=dict(l=10, r=10, t=10, b=10))
    st.info(text)
    st.plotly_chart(fig, width="stretch")


def show_cp_steps(pts, steps):
    spts = steps[0]["pts"]
    steps = steps[1:]
    st.session_state.setdefault("cp_play", False)
    st.session_state.setdefault("cp_delay", 0.6)
    if "cp_k" not in st.session_state or st.session_state["cp_k"] > len(steps) - 1:
        st.session_state["cp_k"] = 0
    every = st.session_state["cp_delay"] if st.session_state["cp_play"] else None
    st.fragment(run_every=every)(draw)(spts, steps)
