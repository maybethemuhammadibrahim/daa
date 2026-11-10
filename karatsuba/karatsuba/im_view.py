import streamlit as st


def move(delta, last):
    k = st.session_state["im_k"] + delta
    st.session_state["im_k"] = max(0, min(last, k))


def short(s):
    if len(s) > 14:
        return s[:6] + ".." + s[-6:]
    return s


def draw(steps):
    last = len(steps) - 1
    playing = st.session_state["im_play"]
    if playing:
        if st.session_state["im_k"] < last:
            st.session_state["im_k"] += 1
        else:
            st.session_state["im_play"] = False
            st.rerun()

    c1, c2, c3, c4 = st.columns([1, 1, 1, 5])
    if playing:
        if c1.button("Pause", key="im_pause"):
            st.session_state["im_play"] = False
            st.rerun()
    else:
        if c1.button("Play", key="im_playbtn"):
            if st.session_state["im_k"] >= last:
                st.session_state["im_k"] = 0
            st.session_state["im_play"] = True
            st.rerun()
    c2.button("Prev", on_click=move, args=(-1, last), key="im_prev", disabled=playing)
    c3.button("Next", on_click=move, args=(1, last), key="im_next", disabled=playing)
    c4.slider("Step", 0, last, key="im_k", disabled=playing)
    st.select_slider("Seconds per step", [0.2, 0.4, 0.6, 1.0, 1.5, 2.0], key="im_delay",
                     disabled=playing)
    k = st.session_state["im_k"]
    s = steps[k]
    st.write("Step %d of %d (call depth %d)" % (k + 1, last + 1, s["depth"])
             + (", playing" if playing else ", paused"))

    left, right = st.columns([3, 2])
    with left:
        st.markdown("**x** = `%s`" % s["x"])
        st.markdown("**y** = `%s`" % s["y"])
        if s["type"] == "base":
            st.info("Small enough, schoolbook multiplication")
            st.markdown("x · y = `%s`" % s["result"])
        else:
            m = s["m"]
            st.info("Split at m = %d digits" % m)
            st.markdown("x = high·10^%d + low → high = `%s`, low = `%s`" % (m, s["x_hi"], s["x_lo"]))
            st.markdown("y = high·10^%d + low → high = `%s`, low = `%s`" % (m, s["y_hi"], s["y_lo"]))
            st.markdown("z0 = x_low · y_low = `%s`" % s["z0"])
            st.markdown("z2 = x_high · y_high = `%s`" % s["z2"])
            st.markdown("z1 = (x_low + x_high)(y_low + y_high) = `%s`" % s["z1_raw"])
            st.markdown("middle = z1 − z2 − z0 = `%s`" % s["z1"])
            st.markdown("result = z2·10^%d + (z1 − z2 − z0)·10^%d + z0" % (2 * m, m))
            st.markdown("= `%s`" % s["result"])
    with right:
        st.write("Call tree")
        lines = []
        for i in range(len(steps)):
            t = steps[i]
            text = "mul(%s, %s)" % (short(t["x"]), short(t["y"]))
            if t["type"] == "base":
                text += " school"
            line = "&nbsp;" * 4 * t["depth"] + text
            if i == k:
                line = "**:red[" + line.replace("*", "") + " ◀]**"
            lines.append(line)
        with st.container(height=420):
            st.markdown("  \n".join(lines))


def show_im_steps(a, b, steps):
    st.session_state.setdefault("im_play", False)
    st.session_state.setdefault("im_delay", 0.6)
    if "im_k" not in st.session_state or st.session_state["im_k"] > len(steps) - 1:
        st.session_state["im_k"] = 0
    every = st.session_state["im_delay"] if st.session_state["im_play"] else None
    st.fragment(run_every=every)(draw)(steps)
