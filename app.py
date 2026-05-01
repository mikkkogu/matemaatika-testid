import streamlit as st
import pandas as pd
import random

# Lehe seaded
st.set_page_config(page_title="Matemaatika Enesekontroll", page_icon="🧮", layout="wide")

# 1. Andmete laadimine
@st.cache_data
def load_data():
    try:
        return pd.read_csv("matemaatika_testid.csv")
    except FileNotFoundError:
        st.error("❌ Faili 'matemaatika_testid_100.csv' ei leitud! Kontrolli GitHubi.")
        st.stop()

df = load_data()
all_topics = sorted(df['topic'].unique().tolist())

# --- SIDEBAR: SEADED ---
st.sidebar.title("🛠️ Seaded")

theme_choice = st.sidebar.radio("Vali teema:", ["Tume", "Hele"])

# Heleda teema CSS täiendustega (nupud ka heledaks)
if theme_choice == "Hele":
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff !important; color: #000000 !important; }
        [data-testid="stSidebar"] { background-color: #f8f9fb !important; }
        .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, 
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
            color: #000000 !important;
        }
        div.stButton > button, div.stFormSubmitButton > button {
            background-color: #ffffff !important; color: #000000 !important;
            border: 1px solid #cccccc !important;
        }
        div.stButton > button:hover { border-color: #000000 !important; background-color: #f0f2f6 !important; }
        .streamlit-expanderHeader { color: #000000 !important; background-color: #f0f2f6 !important; }
        </style>
    """, unsafe_allow_html=True)

st.sidebar.divider()
level = st.sidebar.select_slider("Vali raskusaste:", options=["Kerge", "Raske"])

st.sidebar.divider()
selected_topics = st.sidebar.multiselect("Vali teemad:", options=all_topics, default=[])
filtered_df = df[df['topic'].isin(selected_topics)] if selected_topics else df

# --- TESTI HALDUS ---
def reset_test():
    n_to_sample = min(10, len(filtered_df))
    st.session_state.current_test = filtered_df.sample(n=n_to_sample).to_dict('records')
    st.session_state.submitted = False
    st.session_state.confirmed_incomplete = False
    st.session_state.user_answers = {}

if 'current_test' not in st.session_state or st.sidebar.button("Genereeri uus test"):
    reset_test()

# --- PÕHIEKRAAN ---
st.title("🧮 Matemaatika Test")
st.info(f"Režiim: **{level}** | Teema: **{theme_choice}**")

# Kasutame session_state'i vastuste hoidmiseks, et need pärast rerun'i alles jääksid
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}

with st.form("test_form"):
    for i, q in enumerate(st.session_state.current_test):
        st.markdown(f"### {i+1}. {q['question']}")
        
        options = [q['option_a'], q['option_b'], q['option_c'], q['option_d']]
        
        # Salvestame valiku kohe session_state'i
        st.session_state.user_answers[i] = st.radio(
            "Sinu valik:", 
            options, 
            key=f"radio_{i}",
            index=options.index(st.session_state.user_answers[i]) if i in st.session_state.user_answers and st.session_state.user_answers[i] in options else None
        )
        
        # Vihje näitamine (Kerge tase + pole veel esitatud)
        if level == "Kerge" and not st.session_state.submitted:
            with st.expander("Vajad abi? (Vihje)"):
                st.write(q['hint'])
        
        # TAGASISIDE PÄRAST ESITAMIST
        if st.session_state.submitted:
            if st.session_state.user_answers[i] == q['correct_answer']:
                st.success("✅ **ÕIGE!**")
            else:
                st.error(f"❌ **VALE.** Õige vastus: **{q['correct_answer']}**")
                with st.expander("Selgitus/Vihje"):
                    st.write(q['hint'])
        st.divider()

    submit_clicked = st.form_submit_button("ESITA VASTUSED")

# --- TULEMUSTE JA HINDE LOOGIKA ---
if submit_clicked:
    # Kontrollime vastamata küsimusi
    unanswered = [i for i in range(len(st.session_state.current_test)) if st.session_state.user_answers.get(i) is None]
    
    if unanswered and not st.session_state.confirmed_incomplete:
        st.warning(f"⚠️ Sul on veel {len(unanswered)} küsimust vastamata!")
        if st.checkbox("Kinnita: Soovin esitada pooliku testi", key="confirm_check"):
            st.session_state.confirmed_incomplete = True
            st.session_state.submitted = True
            st.rerun()
    else:
        st.session_state.submitted = True
        st.rerun() # See rerun joonistab nüüd tagasiside küsimuste juurde!

# Kui test on esitatud, näitame koondtulemust vormist VÄLJASPOOL (allpool)
if st.session_state.submitted:
    correct_count = sum(1 for i, q in enumerate(st.session_state.current_test) if st.session_state.user_answers.get(i) == q['correct_answer'])
    score_percent = (correct_count / len(st.session_state.current_test)) * 100
    
    if score_percent >= 91: grade, color = "A", "green"
    elif score_percent >= 81: grade, color = "B", "blue"
    elif score_percent >= 71: grade, color = "C", "blue"
    elif score_percent >= 61: grade, color = "D", "orange"
    elif score_percent >= 51: grade, color = "E", "orange"
    else: grade, color = "F", "red"

    st.subheader("🏁 Testi koondtulemus")
    c1, c2, c3 = st.columns(3)
    c1.metric("Punktid", f"{correct_count} / {len(st.session_state.current_test)}")
    c2.metric("Protsent", f"{int(score_percent)}%")
    c3.metric("HINNE", grade)
    
    if grade != "F":
        st.balloons()
        st.success(f"Tubli! Sinu hinne on {grade}.")
    else:
        st.error("Tulemus jäi alla lävendi. Proovi uuesti!")

    # UUS NUPP: Tee test uuesti
    if st.button("🔄 TEE TEST UUESTI", use_container_width=True):
        reset_test()
        st.rerun()
