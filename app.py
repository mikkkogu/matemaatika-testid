import streamlit as st
import pandas as pd
import random

# Seadistame lehe ja algse teema
st.set_page_config(page_title="Matemaatika Enesekontroll", page_icon="🧮", layout="wide")

# 1. Andmete laadimine
@st.cache_data
def load_data():
    # Kasutame sinu uut 110 küsimusega faili
    return pd.read_csv("matemaatika_testid.csv")

df = load_data()
all_topics = sorted(df['topic'].unique().tolist())

# --- SIDEBAR: SEADED ---
st.sidebar.title("🛠️ Seaded")

# Teema valik (CSS manipuleerimine)
theme_choice = st.sidebar.radio("Vali teema:", ["Tume", "Hele"])
if theme_choice == "Hele":
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; color: #000000; }
        .stMarkdown, .stText, p { color: #000000 !important; }
        </style>
    """, unsafe_allow_html=True)

st.sidebar.divider()

# Raskusaste
level = st.sidebar.select_slider(
    "Vali raskusaste:",
    options=["Kerge", "Raske"],
    help="Kerge tase näitab vihjeid, Raske tase peidab need täielikult."
)

st.sidebar.divider()

# Teemade valik
selected_topics = st.sidebar.multiselect(
    "Vali teemad:", 
    options=all_topics,
    default=[]
)

filtered_df = df[df['topic'].isin(selected_topics)] if selected_topics else df

# Testi genereerimine
if 'current_test' not in st.session_state or st.sidebar.button("Genereeri uus test"):
    n_to_sample = min(10, len(filtered_df))
    st.session_state.current_test = filtered_df.sample(n=n_to_sample).to_dict('records')
    st.session_state.submitted = False
    st.session_state.confirmed_incomplete = False

# --- PÕHIEKRAAN ---
st.title("🧮 Matemaatika Test")
st.info(f"Režiim: **{level}** | Teema: **{theme_choice}**")

with st.form("test_form"):
    user_answers = {}
    
    for i, q in enumerate(st.session_state.current_test):
        st.markdown(f"### {i+1}. {q['question']}")
        
        options = [q['option_a'], q['option_b'], q['option_c'], q['option_d']]
        
        user_answers[i] = st.radio(
            "Sinu valik:", 
            options, 
            key=f"radio_{i}",
            index=None
        )
        
        # Vihjete kuvamine (ainult kerge tasemega ja enne esitamist)
        if level == "Kerge" and not st.session_state.submitted:
            with st.expander("Vajad abi? (Vihje)"):
                st.write(q['hint'])
        
        # TAGASISIDE PÄRAST ESITAMIST
        if st.session_state.get('submitted'):
            if user_answers[i] == q['correct_answer']:
                st.success(f"✅ **ÕIGE!**")
            else:
                st.error(f"❌ **VALE.**")
                st.info(f"💡 Õige vastus oli: **{q['correct_answer']}**")
                # Raske tasemega näitame selgitust alles siis, kui on vastatud
                with st.expander("Selgitus/Vihje"):
                    st.write(q['hint'])
        st.divider()

    submit_clicked = st.form_submit_button("ESITA VASTUSED")

# --- HINDE ARVUTAMINE ---
if submit_clicked or st.session_state.submitted:
    unanswered = [i for i, ans in user_answers.items() if ans is None]
    
    if unanswered and not st.session_state.confirmed_incomplete:
        st.warning(f"⚠️ Sul on veel {len(unanswered)} küsimust vastamata!")
        if st.checkbox("Kinnita: Soovin esitada pooliku testi"):
            st.session_state.confirmed_incomplete = True
            st.rerun()
    else:
        st.session_state.submitted = True
        correct_count = sum(1 for i, q in enumerate(st.session_state.current_test) if user_answers[i] == q['correct_answer'])
        score_percent = (correct_count / len(st.session_state.current_test)) * 100
        
        if score_percent >= 91: grade, color = "A", "green"
        elif score_percent >= 81: grade, color = "blue"
        elif score_percent >= 71: grade, color = "blue"
        elif score_percent >= 61: grade, color = "orange"
        elif score_percent >= 51: grade, color = "orange"
        else: grade, color = "F", "red"

        st.subheader("Lõpptulemus")
        c1, c2, c3 = st.columns(3)
        c1.metric("Punktid", f"{correct_count} / {len(st.session_state.current_test)}")
        c2.metric("Protsent", f"{int(score_percent)}%")
        c3.metric("HINNE", grade)
        
        if grade != "F":
            st.balloons()
