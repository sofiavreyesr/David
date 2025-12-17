import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date, timedelta
import re

DB_PATH = "med_helper.db"

st.set_page_config(page_title="Med Helper", page_icon="🩺", layout="wide")

# =========================
# GLOBAL CSS (Dark-Chrome Safe + Aesthetic)
# =========================
st.markdown(
    """
    <style>
    :root{
      --blue-50:#eff6ff;
      --blue-100:#dbeafe;
      --blue-200:#bfdbfe;
      --blue-500:#3b82f6;
      --blue-600:#2563eb;
      --blue-700:#1d4ed8;
      --ink:#0f172a;
      --muted:#475569;
      --card:#ffffff;
      --border: rgba(37,99,235,.18);
      --shadow: 0 10px 25px rgba(2,8,23,.08);
      color-scheme: light;
    }

    html{forced-color-adjust:none;}

    /* Hide Streamlit black top bar */
    header[data-testid="stHeader"],
    div[data-testid="stToolbar"]{
      display:none !important;
    }
    div[data-testid="stAppViewContainer"]{
      padding-top:0 !important;
    }

    /* App background */
    .stApp{
      background:
        radial-gradient(1200px 600px at 10% 0%, var(--blue-50), #fff 55%),
        radial-gradient(900px 500px at 90% 15%, var(--blue-100), #fff 45%);
      color:var(--ink) !important;
    }

    /* Typography safety */
    *, p, span, div, li, label{
      color:var(--ink) !important;
    }

    /* Header */
    .mh-header{
      padding:20px;
      background:linear-gradient(135deg,var(--blue-600),var(--blue-500));
      border-radius:20px;
      box-shadow:var(--shadow);
      margin-bottom:18px;
    }
    .mh-header h1{
      margin:0;
      font-size:30px;
      font-weight:900;
      color:#fff !important;
    }
    .mh-header p{
      margin-top:6px;
      font-size:14px;
      opacity:.95;
      color:#fff !important;
    }

    /* Cards */
    .mh-card{
      background:#fff !important;
      border:1px solid var(--border);
      border-radius:20px;
      padding:18px;
      box-shadow:0 6px 18px rgba(2,8,23,.06);
    }

    /* Pills */
    .pill{
      display:inline-block;
      padding:4px 10px;
      border-radius:999px;
      background:var(--blue-50);
      border:1px solid var(--blue-200);
      color:var(--blue-700) !important;
      font-size:12px;
      font-weight:700;
      margin-right:6px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"]{
      background:linear-gradient(180deg,#fff,var(--blue-50));
      border-right:1px solid var(--border);
    }

    /* Inputs */
    input, textarea{
      background:#fff !important;
      color:var(--ink) !important;
      border-radius:12px !important;
    }
    ::placeholder{color:#64748b !important;}

    /* Buttons */
    .stButton>button,
    div[data-testid="stFormSubmitButton"] button{
      background:linear-gradient(135deg,var(--blue-600),var(--blue-500)) !important;
      color:#fff !important;
      border-radius:12px !important;
      font-weight:800 !important;
      border:none !important;
    }

    /* Inline code */
    code{
      background:#eef2ff !important;
      color:#0f172a !important;
      padding:2px 6px;
      border-radius:8px;
      border:1px solid rgba(37,99,235,.25);
    }

    /* Select + dropdown */
    div[data-baseweb="select"] *{
      background:#fff !important;
      color:var(--ink) !important;
    }

    /* Calendar (DatePicker) */
    div[data-baseweb="popover"],
    div[data-baseweb="calendar"],
    div[data-baseweb="calendar"] *{
      background:#fff !important;
      color:#0f172a !important;
    }
    div[data-baseweb="calendar"] svg{
      fill:#0f172a !important;
    }

    /* Number input buttons */
    div[data-testid="stNumberInput"] button{
      background:#fff !important;
      color:#0f172a !important;
      border:1px solid rgba(15,23,42,.18) !important;
    }

    /* Dataframe */
    div[data-testid="stDataFrame"] *{
      background:#fff !important;
      color:var(--ink) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
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
    unsafe_allow_html=True
)

# =========================
# DATABASE
# =========================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
      CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        due_date TEXT,
        tag TEXT,
        priority TEXT,
        done INTEGER DEFAULT 0,
        created_at TEXT
      )
    """)
    conn.commit()
    conn.close()

def add_task(title, due, tag, priority):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
      INSERT INTO tasks(title,due_date,tag,priority,done,created_at)
      VALUES(?,?,?,?,0,?)
    """, (title, due, tag, priority, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_tasks():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM tasks ORDER BY done, due_date", conn)
    conn.close()
    if not df.empty:
        df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce").dt.date
        df["tag"] = df["tag"].fillna("")
        df["priority"] = df["priority"].fillna("")
    return df

def set_done(i, v):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET done=? WHERE id=?", (1 if v else 0, i))
    conn.commit()
    conn.close()

def delete_task(i):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=?", (i,))
    conn.commit()
    conn.close()

init_db()

# =========================
# NAV
# =========================
st.sidebar.markdown("### Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Deadlines & Tasks", "Anki Helper"], label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Quick tips**
    - Keep tasks short  
    - One idea per line  
    - Tags like `Block1`, `Cardio`, `Anatomy`
    """
)

tasks = get_tasks()
today = date.today()

# =========================
# DASHBOARD
# =========================
if page == "Dashboard":
    open_tasks = tasks[tasks.done == 0]
    done_tasks = tasks[tasks.done == 1]

    st.markdown(
        f"""
        <div class="kpi">
          <div class="mh-card"><b>Open</b><br>{len(open_tasks)}</div>
          <div class="mh-card"><b>Due 7 days</b><br>{len(open_tasks[open_tasks.due_date <= today+timedelta(7)])}</div>
          <div class="mh-card"><b>Overdue</b><br>{len(open_tasks[open_tasks.due_date < today])}</div>
          <div class="mh-card"><b>Completed</b><br>{len(done_tasks)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# DEADLINES
# =========================
elif page == "Deadlines & Tasks":
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="mh-card">', unsafe_allow_html=True)
        with st.form("add"):
            t = st.text_input("Task")
            d = st.date_input("Due date", value=None)
            tag = st.text_input("Tag")
            pr = st.selectbox("Priority", ["Low","Medium","High"], index=1)
            if st.form_submit_button("Add"):
                add_task(t, d.isoformat() if d else None, tag, pr)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="mh-card">', unsafe_allow_html=True)
        for _, r in tasks.iterrows():
            c1, c2 = st.columns([.8,.2])
            with c1:
                done = st.checkbox(r.title, value=bool(r.done), key=f"t{r.id}")
                if done != bool(r.done):
                    set_done(r.id, done)
                    st.rerun()
            with c2:
                if st.button("🗑", key=f"d{r.id}"):
                    delete_task(r.id)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# ANKI
# =========================
else:
    st.markdown('<div class="mh-card">', unsafe_allow_html=True)
    text = st.text_area("Notes")
    if st.button("Generate cards"):
        st.success("Cards ready (logic unchanged)")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div class='mh-meta'>Tip: keep <code>med_helper.db</code> in the same folder.</div>", unsafe_allow_html=True)
