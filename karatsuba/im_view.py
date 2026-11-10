import html

import plotly.graph_objects as go
import streamlit as st

ROLES = ["z0", "z2", "z1"]
ROLE_TEXT = {
    "z0": "z0 <small>low · low</small>",
    "z2": "z2 <small>high · high</small>",
    "z1": "z1 <small>(low+high) · (low+high)</small>",
}
COLORS = {
    "current": "#E4572E",
    "stack": "#1F5FBF",
    "done": "#2A9D8F",
    "pending": "#C9D1DC",
}
STATE_NAMES = {
    "current": "current call",
    "stack": "waiting for its sub-calls",
    "done": "returned",
    "pending": "not reached yet",
}

CSS = """
<style>
.kv {font-size: 0.95rem; line-height: 1.5;}
.kv .row {display: grid; grid-template-columns: 11rem 1fr; gap: 0.75rem; padding: 0.3rem 0;
          border-bottom: 1px solid #E3E7EE; align-items: baseline;}
.kv .row:last-child {border-bottom: none;}
.kv .lab {color: #4A5568;}
.kv .lab small {color: #6B7280; margin-left: 0.3rem;}
.kv .num {font-family: "Source Code Pro", ui-monospace, monospace; font-size: 0.9rem;
          word-break: break-all; color: #14213D;}
.kv .hi {color: #1F5FBF; font-weight: 600;}
.kv .lo {color: #B5470F; font-weight: 600;}
.kv .wait {color: #6B7280; font-style: italic; font-family: inherit;}
.kv .res {color: #1E7A6F; font-weight: 600;}
.kv .key {font-size: 0.8rem; color: #4A5568; margin-bottom: 0.4rem;}
.stack {font-size: 0.9rem; line-height: 1.7;}
.stack .item {font-family: "Source Code Pro", ui-monospace, monospace; white-space: nowrap;
              overflow: hidden; text-overflow: ellipsis;}
.stack .cur {color: #C2410C; font-weight: 600;}
.stack .role {display: inline-block; min-width: 2.2rem; color: #4A5568;
              font-family: "Source Sans Pro", sans-serif;}
</style>
"""


def short(s):
    if len(s) > 14:
        return s[:6] + ".." + s[-6:]
    return s


def build(steps):
    """Turn the pre-order step list into a tree and a list of frames.

    Each call gets an 'enter' frame. Calls that split also get a 'combine' frame
    after all three sub-calls returned, so the dry run follows the real call order.
    """
    nodes = []
    stack = []
    for s in steps:
        while stack and nodes[stack[-1]]["depth"] >= s["depth"]:
            stack.pop()
        parent = stack[-1] if stack else None
        node = {"s": s, "depth": s["depth"], "parent": parent, "kids": [],
                "role": "x · y" if parent is None else ROLES[len(nodes[parent]["kids"])]}
        nodes.append(node)
        if parent is not None:
            nodes[parent]["kids"].append(len(nodes) - 1)
        if s["type"] == "split":
            stack.append(len(nodes) - 1)

    frames = []
    leaves = [0]

    def walk(i):
        node = nodes[i]
        node["enter"] = len(frames)
        frames.append(("enter", i))
        if node["kids"]:
            for k in node["kids"]:
                walk(k)
            node["exit"] = len(frames)
            frames.append(("combine", i))
            node["x"] = sum(nodes[k]["x"] for k in node["kids"]) / len(node["kids"])
        else:
            node["exit"] = node["enter"]
            node["x"] = leaves[0]
            leaves[0] += 1

    walk(0)
    return nodes, frames


def state(node, f):
    if f < node["enter"]:
        return "pending"
    if f == node["enter"] or f == node["exit"]:
        return "current"
    if f < node["exit"]:
        return "stack"
    return "done"


def tree_figure(nodes, f, cur):
    path = set()
    i = cur
    while i is not None:
        path.add(i)
        i = nodes[i]["parent"]

    fig = go.Figure()
    for on_path in (False, True):
        ex, ey = [], []
        for i, n in enumerate(nodes):
            p = n["parent"]
            if p is None or ((i in path) != on_path):
                continue
            ex += [nodes[p]["x"], n["x"], None]
            ey += [-nodes[p]["depth"], -n["depth"], None]
        fig.add_trace(go.Scatter(x=ex, y=ey, mode="lines", hoverinfo="skip", showlegend=False,
                                 line=dict(color="#E4572E" if on_path else "#D5DBE3",
                                           width=2.5 if on_path else 1)))

    for st_name in ("pending", "done", "stack", "current"):
        xs, ys, texts, hovers = [], [], [], []
        for i, n in enumerate(nodes):
            if state(n, f) != st_name:
                continue
            s = n["s"]
            xs.append(n["x"])
            ys.append(-n["depth"])
            texts.append(n["role"] if n["depth"] <= 2 or i == cur else "")
            h = "<b>%s</b>  depth %d<br>x = %s<br>y = %s" % (n["role"], n["depth"], short(s["x"]),
                                                              short(s["y"]))
            if st_name == "done":
                h += "<br>result = %s" % short(s["result"])
            h += "<br><i>%s</i>" % ("schoolbook" if s["type"] == "base" else "split")
            hovers.append(h)
        big = st_name == "current"
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="markers+text", text=texts, textposition="top center",
            textfont=dict(size=12 if big else 11, color="#14213D"),
            hovertext=hovers, hoverinfo="text", name=STATE_NAMES[st_name],
            marker=dict(size=20 if big else 11, color=COLORS[st_name],
                        line=dict(width=3 if big else 1,
                                  color="#FFFFFF" if st_name != "pending" else "#AEB8C6"))))

    depth = max(n["depth"] for n in nodes)
    fig.update_layout(
        height=110 + 58 * depth, margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True, range=[-depth - 0.4, 0.5]),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0, font=dict(size=12)),
        hoverlabel=dict(bgcolor="#FFFFFF", font=dict(family="Source Code Pro, monospace")),
    )
    return fig


def num(s):
    return '<span class="num">%s</span>' % html.escape(s)


def split_num(s, m):
    return '<span class="num"><span class="hi">%s</span><span class="lo">%s</span></span>' % (
        html.escape(s[:-m]), html.escape(s[-m:]))


def row(label, value):
    return '<div class="row"><span class="lab">%s</span>%s</div>' % (label, value)


def detail(nodes, frames, f):
    kind, i = frames[f]
    n = nodes[i]
    s = n["s"]
    if s["type"] == "base":
        rows = [row("x", num(s["x"])), row("y", num(s["y"])),
                row("x · y", '<span class="num res">%s</span>' % html.escape(s["result"]))]
        return '<div class="kv">%s</div>' % "".join(rows)

    m = s["m"]
    rows = ['<div class="key">x and y are cut %d digits from the right: '
            '<span class="hi">high part</span> and <span class="lo">low part</span></div>' % m,
            row("x", split_num(s["x"], m)), row("y", split_num(s["y"], m))]
    for k, role in zip(n["kids"], ROLES):
        kid = nodes[k]
        st_name = state(kid, f)
        if st_name == "done":
            value = '<span class="num res">%s</span>' % html.escape(s[role if role != "z1" else "z1_raw"])
        elif st_name == "pending":
            value = '<span class="num wait">not computed yet</span>'
        else:
            value = '<span class="num wait">being computed</span>'
        rows.append(row(ROLE_TEXT[role], value))
    if kind == "combine":
        rows.append(row("middle", '<span class="num">z1 − z2 − z0 = %s</span>' % html.escape(s["z1"])))
        rows.append(row("result", '<span class="num">z2·10^%d + middle·10^%d + z0</span>' % (2 * m, m)))
        rows.append(row("", '<span class="num res">= %s</span>' % html.escape(s["result"])))
    return '<div class="kv">%s</div>' % "".join(rows)


def narration(nodes, frames, f):
    kind, i = frames[f]
    n = nodes[i]
    s = n["s"]
    who = "the whole product x · y" if n["parent"] is None else n["role"]
    if s["type"] == "base":
        return ("Base case for %s: the numbers are below the cutoff, so they are multiplied "
                "the schoolbook way." % who)
    if kind == "enter":
        return ("Split for %s: cut x and y %d digits from the right, then compute the three "
                "smaller products z0, z2 and z1 (left to right in the tree)." % (who, s["m"]))
    return ("Combine for %s: z0, z2 and z1 are back, so the result is "
            "z2·10^%d + (z1 − z2 − z0)·10^%d + z0. Only 3 multiplications instead of 4."
            % (who, 2 * s["m"], s["m"]))


def call_stack(nodes, frames, f):
    _, i = frames[f]
    chain = []
    while i is not None:
        chain.append(i)
        i = nodes[i]["parent"]
    chain.reverse()
    lines = []
    for d, j in enumerate(chain):
        n = nodes[j]
        cls = "item cur" if j == chain[-1] else "item"
        lines.append('<div class="%s" style="padding-left:%.1frem"><span class="role">%s</span>'
                     'mul(%s, %s)</div>' % (cls, 0.9 * d, html.escape(n["role"]),
                                            html.escape(short(n["s"]["x"])),
                                            html.escape(short(n["s"]["y"]))))
    return '<div class="stack">%s</div>' % "".join(lines)


def move(delta, last):
    k = st.session_state["im_k"] + delta
    st.session_state["im_k"] = max(0, min(last, k))


def draw(nodes, frames):
    last = len(frames) - 1
    playing = st.session_state["im_play"]
    if playing:
        if st.session_state["im_k"] < last:
            st.session_state["im_k"] += 1
        else:
            st.session_state["im_play"] = False
            st.rerun()

    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 5, 2], vertical_alignment="bottom")
    if playing:
        if c1.button("Pause", key="im_pause", icon=":material/pause:", width="stretch"):
            st.session_state["im_play"] = False
            st.rerun()
    else:
        if c1.button("Play", key="im_playbtn", icon=":material/play_arrow:", width="stretch"):
            if st.session_state["im_k"] >= last:
                st.session_state["im_k"] = 0
            st.session_state["im_play"] = True
            st.rerun()
    c2.button("Prev", on_click=move, args=(-1, last), key="im_prev", disabled=playing,
              icon=":material/chevron_left:", width="stretch")
    c3.button("Next", on_click=move, args=(1, last), key="im_next", disabled=playing,
              icon=":material/chevron_right:", width="stretch")
    c4.slider("Step", 0, last, key="im_k", disabled=playing)
    c5.select_slider("Seconds per step", [0.2, 0.4, 0.6, 1.0, 1.5, 2.0], key="im_delay",
                     disabled=playing)

    f = st.session_state["im_k"]
    cur = frames[f][1]
    st.caption("Step %d of %d  ·  call depth %d  ·  %s" % (
        f + 1, last + 1, nodes[cur]["depth"], "playing" if playing else "paused"))
    st.info(narration(nodes, frames, f), icon=":material/info:")

    st.markdown("**Recursion tree**  \n"
                ":small[Each dot is one call. Children left to right are z0, z2, z1. "
                "Hover a dot to see its numbers.]")
    st.plotly_chart(tree_figure(nodes, f, cur), width="stretch",
                    config={"displayModeBar": False})

    left, right = st.columns([3, 2], gap="large")
    with left:
        st.markdown("**Current call**")
        st.html(CSS + detail(nodes, frames, f))
    with right:
        st.markdown("**Call stack**")
        st.html(CSS + call_stack(nodes, frames, f))


def show_im_steps(a, b, steps):
    nodes, frames = build(steps)
    st.session_state.setdefault("im_play", False)
    st.session_state.setdefault("im_delay", 0.6)
    if "im_k" not in st.session_state or st.session_state["im_k"] > len(frames) - 1:
        st.session_state["im_k"] = 0
    every = st.session_state["im_delay"] if st.session_state["im_play"] else None
    st.fragment(run_every=every)(draw)(nodes, frames)
