import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date, timedelta
import re

DB_PATH = "med_helper.db"

st.set_page_config(page_title="Med Helper", page_icon="🩺", layout="wide")

# =========================
# CSS — DARK CHROME SAFE
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
        color-scheme: light;
      }

      html{
        forced-color-adjust: none;
      }

      .stApp{
        background: radial-gradient(1200px 600px at 10% 0%, var(--blue-50), #fff 55%),
                    radial-gradient(900px 500px at 90% 15%, var(--blue-100), #fff 45%);
        color: var(--ink) !important;
      }

      .stApp, .stMarkdown, label, p, span, div{
        color: var(--ink) !important;
      }

      /* Header */
      .mh-header{
        padding:18px;
        background: linear-gradient(135deg, var(--blue-600), var(--blue-500));
        border-radius:18px;
        margin-bottom:16px;
      }
      .mh-header h1, .mh-header p{
        color:#fff !important;
        margin:0;
      }

      /* Cards */
      .mh-card{
        background:#fff !important;
        border-radius:18px;
        padding:16px;
        border:1px solid var(--border);
        box-shadow:0 6px 18px rgba(2,8,23,.06);
      }

      /* Inputs */
      input, textarea{
        background:#fff !important;
        color:var(--ink) !important;
        border-radius:12px !important;
        caret-color:var(--ink);
      }

      ::placeholder{
        color:#64748b !important;
      }

      /* Buttons */
      .stButton>button,
      div[data-testid="stFormSubmitButton"] button{
        background:linear-gradient(135deg, var(--blue-600), var(--blue-500)) !important;
        color:#fff !important;
        border-radius:12px !important;
        font-weight:800;
        border:none;
        padding:.55rem .9rem;
      }

      /* Sidebar */
      section[data-testid="stSidebar"]{
        background:#f8fafc !important;
      }
      section[data-testid="stSidebar"] *{
        color:var(--ink) !important;
      }

      /* Pills */
      .pill{
        background:var(--blue-50);
        border:1px solid var(--blue-200);
        color:var(--blue-700) !important;
        padding:4px 10px;
        border-radius:999px;
        font-size:12px;
        font-weight:700;
        margin-right:6px;
      }

      /* DataFrame */
      div[data-testid="stDataFrame"],
      div[data-testid="stDataFrame"] *{
        background:#fff !important;
        color:var(--ink) !important;
      }

      /* =========================
         FIX BLACK SELECTBOX
         ========================= */
      div[data-baseweb="select"] > div{
        background:#fff !important;
        border:1px solid rgba(15,23,42,.25) !important;
        border-radius:12px !important;
      }
      div[data-baseweb="select"] span,
      div[data-baseweb="select"] svg{
        color:var(--ink) !important;
        fill:var(--ink) !important;
      }
      ul[role="listbox"]{
        background:#fff !important;
        border-radius:12px !important;
        color:var(--ink) !important;
      }
      ul[role="listbox"] li{
        background:#fff !important;
        color:var(--ink) !important;
      }

      /* =========================
         FIX INLINE CODE (backticks)
         ========================= */
      code, kbd, samp{
        background:#eef2ff !important;
        color:var(--ink) !important;
        border:1px solid rgba(37,99,235,.25) !important;
        border-radius:8px !important;
        padding:0.12rem 0.35rem !important;
      }
      pre{
        background:#f8fafc !important;
        color:var(--ink) !important;
        border:1px solid rgba(37,99,235,.18) !important;
        border-radius:12px !important;
      }
      pre code{
        background:transparent !important;
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
        CREATE TABLE IF NOT EXISTS tasks (
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

def get_tasks():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM tasks ORDER BY done, due_date", conn)
    conn.close()
    if not df.empty:
        df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce").dt.date
        df["done"] = df["done"].astype(int)
        df.fillna("", inplace=True)
    return df

def add_task(title, due, tag, priority):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO tasks (title, due_date, tag, priority, created_at) VALUES (?,?,?,?,?)",
        (title, due, tag, priority, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def set_done(task_id, val):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE tasks SET done=? WHERE id=?", (1 if val else 0, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

init_db()

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("### Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Deadlines & Tasks", "Anki Helper"], label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Quick tips**
    - Keep tasks short (action verbs)
    - One idea per line for Anki
    - Tags like `Block1`, `Cardio`, `Anatomy`
    """
)

# =========================
# PAGE LOGIC (UNCHANGED)
# =========================
tasks = get_tasks()
today = date.today()

if page == "Dashboard":
    st.info("Dashboard content here (unchanged)")

elif page == "Deadlines & Tasks":
    st.info("Deadlines & Tasks content here (unchanged)")

else:
    st.info("Anki Helper content here (unchanged)")
