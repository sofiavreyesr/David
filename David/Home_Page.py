import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date, timedelta
import re

DB_PATH = "med_helper.db"

st.set_page_config(page_title="Med Helper", page_icon="🩺", layout="wide")

# =========================
# CSS: Dark-Chrome-proof + Top bar visible + Fix black submit button
# =========================
st.markdown(
    """
    <style>
      :root{
        --blue-50:#eff6ff;
        --blue-100:#dbeafe;
        --blue-200:#bfdbfe;
        --blue-300:#93c5fd;
        --blue-500:#3b82f6;
        --blue-600:#2563eb;
        --blue-700:#1d4ed8;

        --ink:#0f172a;
        --muted:#475569;

        --card:#ffffff;
        --border: rgba(37, 99, 235, 0.18);
        --shadow: 0 10px 25px rgba(2, 8, 23, 0.08);

        /* Prevent Chrome forced-dark weirdness */
        color-scheme: light;
      }

      html{
        -webkit-text-size-adjust: 100%;
        forced-color-adjust: none;
      }

      /* ==========================
         STREAMLIT TOP BAR (VISIBLE + LIGHT)
         ========================== */
      header[data-testid="stHeader"]{
        background: rgba(255,255,255,0.92) !important;
        backdrop-filter: blur(10px) !important;
        border-bottom: 1px solid rgba(37,99,235,0.18) !important;
      }
      div[data-testid="stToolbar"]{
        background: transparent !important;
      }
      header[data-testid="stHeader"] svg,
      div[data-testid="stToolbar"] svg{
        fill: var(--ink) !important;
        color: var(--ink) !important;
      }
      header[data-testid="stHeader"] button,
      div[data-testid="stToolbar"] button{
        background: transparent !important;
      }
      div[data-testid="stDecoration"]{
        background: transparent !important;
      }

      /* App background */
      .stApp{
        background:
          radial-gradient(1200px 600px at 10% 0%, var(--blue-50) 0%, #ffffff 55%),
          radial-gradient(900px 500px at 90% 15%, var(--blue-100) 0%, #ffffff 45%);
        color: var(--ink) !important;
      }

      /* Keep text readable everywhere */
      .stApp, .stMarkdown, label, p, span, div, li{
        color: var(--ink) !important;
      }

      /* Header card */
      .mh-header{
        padding: 18px 18px 14px 18px;
        border: 1px solid var(--border);
        background: linear-gradient(135deg, var(--blue-600), var(--blue-500));
        color: #fff;
        border-radius: 18px;
        box-shadow: var(--shadow);
        margin-bottom: 14px;
      }
      .mh-header h1{
        font-size: 28px;
        line-height: 1.15;
        margin: 0;
        font-weight: 800;
        letter-spacing: 0.2px;
        color: #fff !important;
      }
      .mh-header p{
        margin: 6px 0 0 0;
        opacity: 0.92;
        font-size: 14px;
        color: #fff !important;
      }

      /* Cards */
      .mh-card{
        border: 1px solid var(--border);
        background: var(--card) !important;
        border-radius: 18px;
        padding: 16px 16px 14px 16px;
        box-shadow: 0 6px 18px rgba(2, 8, 23, 0.06);
      }
      .mh-card h3{
        margin: 0 0 10px 0;
        color: var(--ink) !important;
        font-size: 16px;
        font-weight: 800;
      }
      .mh-meta{
        color: var(--muted) !important;
        font-size: 13px;
        margin-top: 6px;
      }

      /* Pills */
      .pill{
        display:inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        background: var(--blue-50) !important;
        border: 1px solid var(--blue-200);
        color: var(--blue-700) !important;
        font-weight: 700;
        font-size: 12px;
        margin-right: 6px;
      }

      /* Sidebar */
      section[data-testid="stSidebar"]{
        background: linear-gradient(180deg, #ffffff 0%, var(--blue-50) 100%) !important;
        border-right: 1px solid var(--border);
      }
      section[data-testid="stSidebar"] *{
        color: var(--ink) !important;
      }

      /* Buttons */
      .stButton>button{
        border-radius: 12px !important;
        border: 1px solid rgba(37,99,235,0.25) !important;
        background: linear-gradient(135deg, var(--blue-600), var(--blue-500)) !important;
        color: white !important;
        font-weight: 800 !important;
        padding: 0.55rem 0.9rem !important;
      }
      .stButton>button:hover{
        filter: brightness(0.98);
        border-color: rgba(37,99,235,0.38);
      }

      /* ✅ FIX: Form submit button (was black block) */
      div[data-testid="stFormSubmitButton"] > button{
        border-radius: 12px !important;
        border: 1px solid rgba(37,99,235,0.25) !important;
        background: linear-gradient(135deg, var(--blue-600), var(--blue-500)) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        padding: 0.55rem 0.9rem !important;
      }
      div[data-testid="stFormSubmitButton"] > button *{
        color: #ffffff !important;
        fill: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
      }
      div[data-testid="stFormSubmitButton"] > button:hover{
        filter: brightness(0.98) !important;
        border-color: rgba(37,99,235,0.38) !important;
      }

      /* Download button */
      .stDownloadButton>button{
        border-radius: 12px !important;
        border: 1px solid rgba(37,99,235,0.25) !important;
        background: linear-gradient(135deg, #0ea5e9, var(--blue-500)) !important;
        color: white !important;
        font-weight: 800 !important;
        padding: 0.55rem 0.9rem !important;
      }

      /* Inputs (force light bg + dark text) */
      input, textarea{
        background-color: #ffffff !important;
        color: var(--ink) !important;
        caret-color: var(--ink);
        border-radius: 12px !important;
      }
      .stDateInput input{
        background-color: #ffffff !important;
        color: var(--ink) !important;
        border-radius: 12px !important;
      }

      /* Placeholders */
      ::placeholder{
        color: #64748b !important;
        opacity: 1;
      }

      /* KPI */
      .kpi{
        display:flex;
        gap: 12px;
      }
      .kpi .box{
        flex: 1;
        border: 1px solid var(--border);
        background: #fff !important;
        border-radius: 18px;
        padding: 14px 14px;
        box-shadow: 0 6px 18px rgba(2, 8, 23, 0.06);
      }
      .kpi .label{
        color: var(--muted) !important;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .04em;
      }
      .kpi .value{
        margin-top: 6px;
        color: var(--ink) !important;
        font-size: 22px;
        font-weight: 900;
      }

      /* Dataframe */
      div[data-testid="stDataFrame"]{
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid var(--border);
      }
      div[data-testid="stDataFrame"] *{
        color: var(--ink) !important;
        background-color: #ffffff !important;
      }

      /* Selectbox + listbox */
      div[data-baseweb="select"] > div{
        background: #ffffff !important;
        border: 1px solid rgba(15, 23, 42, 0.25) !important;
        border-radius: 12px !important;
      }
      div[data-baseweb="select"] span{ color: var(--ink) !important; }
      div[data-baseweb="select"] svg{ color: var(--ink) !important; fill: var(--ink) !important; }

      ul[role="listbox"]{
        background: #ffffff !important;
        color: var(--ink) !important;
        border: 1px solid rgba(15, 23, 42, 0.18) !important;
        border-radius: 12px !important;
      }
      ul[role="listbox"] li{
        background: #ffffff !important;
        color: var(--ink) !important;
      }

      /* Inline code pills */
      section[data-testid="stSidebar"] .stMarkdown code,
      section[data-testid="stSidebar"] code,
      .stMarkdown code,
      li code, p code, span code{
        background-color: #eef2ff !important;
        color: #0f172a !important;
        border: 1px solid rgba(37, 99, 235, 0.25) !important;
        border-radius: 8px !important;
        padding: 0.12rem 0.35rem !important;
        -webkit-text-fill-color: #0f172a !important;
      }

      /* Number input stepper */
      div[data-testid="stNumberInput"] button{
        background: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid rgba(15,23,42,0.18) !important;
      }
      div[data-testid="stNumberInput"] button svg{
        fill: #0f172a !important;
      }

      /* DatePicker calendar force light */
      div[data-baseweb="popover"],
      div[data-baseweb="popover"] *{
        background: #ffffff !important;
        color: #0f172a !important;
      }
      div[data-baseweb="calendar"],
      div[data-baseweb="calendar"] *{
        background: #ffffff !important;
        color: #0f172a !important;
      }
      div[data-baseweb="calendar"] svg,
      div[data-baseweb="popover"] svg{
        fill: #0f172a !important;
        color: #0f172a !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# HEADER
# =========================
st.markdown(
    """
    <div class="mh-header">
      <h1>🩺 Med Helper</h1>
      <p>Deadlines + checklist + Anki card drafts (fast, practical, no fluff)</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
# DB FUNCTIONS
# =========================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT,
            tag TEXT,
            priority TEXT,
            done INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

def add_task(title, due_date, tag, priority):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO tasks (title, due_date, tag, priority, done, created_at)
        VALUES (?, ?, ?, ?, 0, ?)
        """,
        (title, due_date, tag, priority, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()

def get_tasks():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM tasks ORDER BY done ASC, due_date ASC", conn)
    conn.close()
    if not df.empty:
        df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce").dt.date
        df["done"] = df["done"].astype(int)
        df["tag"] = df["tag"].fillna("")
        df["priority"] = df["priority"].fillna("")
    return df

def set_done(task_id, done: bool):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET done = ? WHERE id = ?", (1 if done else 0, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

# =========================
# ANKI HELPERS
# =========================
def split_lines(text: str):
    lines = [ln.strip() for ln in text.splitlines()]
    return [ln for ln in lines if ln]

def make_basic_cards(lines):
    cards = []
    for ln in lines:
        if ":" in ln:
            q, a = ln.split(":", 1)
            q, a = q.strip(), a.strip()
            if q and a:
                cards.append({"Front": q, "Back": a, "Tags": ""})
                continue
        if " - " in ln:
            q, a = ln.split(" - ", 1)
            q, a = q.strip(), a.strip()
            if q and a:
                cards.append({"Front": q, "Back": a, "Tags": ""})
                continue
        cards.append({"Front": f"Define / explain: {ln}", "Back": "", "Tags": ""})
    return pd.DataFrame(cards)

def make_cloze_cards(lines):
    cards = []
    for ln in lines:
        words = re.findall(r"[A-Za-z][A-Za-z\\-]{3,}", ln)
        candidates = []
        for w in words:
            if w[0].isupper():
                candidates.append(w)
            elif len(w) >= 8:
                candidates.append(w)
        candidates = list(dict.fromkeys(candidates))
        clozed = ln
        for i, term in enumerate(candidates[:2], start=1):
            clozed = re.sub(rf"\\b{re.escape(term)}\\b", f"{{{{c{i}::{term}}}}}", clozed, count=1)
        cards.append({"Text": clozed, "Extra": "", "Tags": ""})
    return pd.DataFrame(cards)

def df_to_tsv_bytes(df: pd.DataFrame):
    return df.to_csv(sep="\\t", index=False).encode("utf-8")

# =========================
# APP
# =========================
init_db()

st.sidebar.markdown("### Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Deadlines & Tasks", "Anki Helper"], label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown("#### Quick tips")
st.sidebar.markdown(
    """
    - Keep tasks short (action verbs).
    - One idea per line for Anki.
    - Tags like `Block1`, `Cardio`, `Anatomy`.
    """,
)

tasks = get_tasks()
today = date.today()

if page == "Dashboard":
    open_tasks = tasks[tasks["done"] == 0].copy() if not tasks.empty else tasks
    done_tasks = tasks[tasks["done"] == 1].copy() if not tasks.empty else tasks

    due_7 = open_tasks[
        (open_tasks["due_date"].notna())
        & (open_tasks["due_date"] >= today)
        & (open_tasks["due_date"] <= today + timedelta(days=7))
    ] if not open_tasks.empty else open_tasks

    overdue = open_tasks[
        (open_tasks["due_date"].notna()) & (open_tasks["due_date"] < today)
    ] if not open_tasks.empty else open_tasks

    st.markdown(
        f"""
        <div class="kpi">
          <div class="box">
            <div class="label">Open tasks</div>
            <div class="value">{len(open_tasks) if open_tasks is not None else 0}</div>
          </div>
          <div class="box">
            <div class="label">Due in 7 days</div>
            <div class="value">{len(due_7) if due_7 is not None else 0}</div>
          </div>
          <div class="box">
            <div class="label">Overdue</div>
            <div class="value">{len(overdue) if overdue is not None else 0}</div>
          </div>
          <div class="box">
            <div class="label">Completed</div>
            <div class="value">{len(done_tasks) if done_tasks is not None else 0}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    c1, c2 = st.columns([1.1, 0.9], gap="large")

    with c1:
        st.markdown('<div class="mh-card">', unsafe_allow_html=True)
        st.markdown("<h3>📅 Due soon (next 7 days)</h3>", unsafe_allow_html=True)

        if tasks.empty:
            st.info("No tasks yet. Add some in **Deadlines & Tasks**.")
        else:
            if due_7.empty:
                st.success("Nothing due in the next 7 days.")
            else:
                st.dataframe(
                    due_7[["title", "due_date", "tag", "priority"]].sort_values("due_date"),
                    use_container_width=True,
                    hide_index=True
                )
        st.markdown("</div>", unsafe_allow_html=True)

        st.write("")
        st.markdown('<div class="mh-card">', unsafe_allow_html=True)
        st.markdown("<h3>⏰ Overdue</h3>", unsafe_allow_html=True)
        if tasks.empty or overdue.empty:
            st.caption("All clear.")
        else:
            st.dataframe(
                overdue[["title", "due_date", "tag", "priority"]].sort_values("due_date"),
                use_container_width=True,
                hide_index=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="mh-card">', unsafe_allow_html=True)
        st.markdown("<h3>✅ Today’s checklist</h3>", unsafe_allow_html=True)
        st.markdown('<div class="mh-meta">Shows tasks due today + tasks with no due date.</div>', unsafe_allow_html=True)
        st.write("")

        if tasks.empty:
            st.info("Add tasks to build today’s checklist.")
        else:
            todays = open_tasks[(open_tasks["due_date"].isna()) | (open_tasks["due_date"] == today)]
            if todays.empty:
                st.info("No tasks for today.")
            else:
                for _, row in todays.iterrows():
                    tag = row["tag"].strip() or "No tag"
                    pr = row["priority"].strip() or "—"
                    label = f"{row['title']}  \n<span class='pill'>{tag}</span><span class='pill'>{pr}</span>"
                    checked = st.checkbox(label, value=False, key=f"dash_{row['id']}")
                    st.markdown(
                        """
                        <script>
                        const blocks = window.parent.document.querySelectorAll('label');
                        blocks.forEach(b => b.style.lineHeight = '1.1');
                        </script>
                        """,
                        unsafe_allow_html=True,
                    )
                    if checked:
                        set_done(int(row["id"]), True)
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

elif page == "Deadlines & Tasks":
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<div class="mh-card">', unsafe_allow_html=True)
        st.markdown("<h3>➕ Add a task</h3>", unsafe_allow_html=True)

        with st.form("add_task_form", clear_on_submit=True):
            title = st.text_input("Task", placeholder="e.g., Watch Renal lecture 3 · Do UWorld set · Draft lab report")
            due = st.date_input("Due date (optional)", value=None)
            tag = st.text_input("Tag (optional)", placeholder="e.g., Block1, Cardio, Anatomy")
            priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)

            submitted = st.form_submit_button("Add task")
            if submitted:
                if not title.strip():
                    st.error("Please enter a task name.")
                else:
                    due_str = due.isoformat() if isinstance(due, date) else None
                    add_task(title.strip(), due_str, tag.strip(), priority)
                    st.success("Task added.")
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.write("")
        st.markdown('<div class="mh-card">', unsafe_allow_html=True)
        st.markdown("<h3>🧮 Quick pacing (optional)</h3>", unsafe_allow_html=True)
        exam_date = st.date_input("Next exam date", value=today + timedelta(days=14), key="exam_date")
        cards_left = st.number_input("Cards / topics left", min_value=0, value=800, step=10)
        days_left = max((exam_date - today).days, 0)
        if days_left == 0:
            st.warning("Exam date is today (or in the past).")
        else:
            per_day = (cards_left / days_left) if days_left else 0
            st.markdown(
                f"<div class='mh-meta'><span class='pill'>{days_left} days</span>"
                f"<span class='pill'>{per_day:.0f} / day</span></div>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="mh-card">', unsafe_allow_html=True)
        st.markdown("<h3>📋 Your tasks</h3>", unsafe_allow_html=True)

        tasks = get_tasks()
        if tasks.empty:
            st.info("No tasks yet.")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            f1, f2, f3 = st.columns([1, 1, 1])
            show_done = f1.checkbox("Show completed", value=False)
            tag_filter = f2.text_input("Filter by tag", placeholder="e.g., Cardio")
            due_only = f3.checkbox("Due soon (7 days)", value=False)

            view = tasks.copy()
            if not show_done:
                view = view[view["done"] == 0]
            if tag_filter.strip():
                view = view[view["tag"].fillna("").str.contains(tag_filter.strip(), case=False)]
            if due_only:
                soon = today + timedelta(days=7)
                view = view[(view["due_date"].notna()) & (view["due_date"] >= today) & (view["due_date"] <= soon)]

            if view.empty:
                st.info("No tasks match your filters.")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                for _, row in view.iterrows():
                    line1 = f"**{row['title']}**"
                    meta = []
                    if pd.notna(row["due_date"]):
                        meta.append(f"Due: {row['due_date']}")
                    if row["tag"].strip():
                        meta.append(f"Tag: {row['tag'].strip()}")
                    if row["priority"].strip():
                        meta.append(f"Priority: {row['priority'].strip()}")

                    cA, cB = st.columns([0.82, 0.18])
                    with cA:
                        is_done = st.checkbox(line1, value=bool(row["done"]), key=f"task_{row['id']}")
                        if meta:
                            st.caption(" · ".join(meta))
                        if is_done != bool(row["done"]):
                            set_done(int(row["id"]), is_done)
                            st.rerun()

                    with cB:
                        if st.button("🗑️ Delete", key=f"del_{row['id']}"):
                            delete_task(int(row["id"]))
                            st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown('<div class="mh-card">', unsafe_allow_html=True)
    st.markdown("<h3>🧠 Anki Helper</h3>", unsafe_allow_html=True)
    st.markdown(
        "<div class='mh-meta'>Paste notes/objectives. One idea per line works best. "
        "Cards are drafts—he can edit before importing.</div>",
        unsafe_allow_html=True,
    )
    st.write("")

    raw = st.text_area(
        "Notes / objectives",
        height=190,
        placeholder=(
            "Examples:\n"
            "Renal autoregulation: afferent arteriole maintains GFR\n"
            "ACE inhibitors decrease efferent arteriole constriction\n"
            "Anion gap metabolic acidosis causes: MUDPILES\n"
        ),
    )

    c1, c2, c3 = st.columns([1, 1, 1])
    mode = c1.radio("Card type", ["Cloze (fast)", "Basic Q/A"], horizontal=True)
    tags = c2.text_input("Default tags (optional)", placeholder="e.g., Block1 Cardio Renal")
    export_name = c3.text_input("Export filename", value="anki_cards")

    st.write("")
    if st.button("✨ Generate cards"):
        lines = split_lines(raw)
        if not lines:
            st.warning("Paste some text first.")
        else:
            if mode.startswith("Cloze"):
                df = make_cloze_cards(lines)
                if tags.strip():
                    df["Tags"] = tags.strip()

                st.success(f"Generated {len(df)} cloze cards (editable below).")
                st.dataframe(df, use_container_width=True, hide_index=True)

                st.download_button(
                    "⬇️ Download TSV (Anki import)",
                    data=df_to_tsv_bytes(df),
                    file_name=f"{export_name}_cloze.tsv",
                    mime="text/tab-separated-values",
                )
                st.caption("Anki → File → Import → choose TSV → map fields to **Text / Extra / Tags**.")
            else:
                df = make_basic_cards(lines)
                if tags.strip():
                    df["Tags"] = tags.strip()

                st.success(f"Generated {len(df)} basic cards (editable below).")
                st.dataframe(df, use_container_width=True, hide_index=True)

                st.download_button(
                    "⬇️ Download TSV (Anki import)",
                    data=df_to_tsv_bytes(df),
                    file_name=f"{export_name}_basic.tsv",
                    mime="text/tab-separated-values",
                )
                st.caption("Anki → File → Import → map fields to **Front / Back / Tags**.")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='mh-meta'>Tip: Keep the file <code>med_helper.db</code> in the same folder so tasks stay saved.</div>", unsafe_allow_html=True)
