import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Matemaatika Enesekontroll", page_icon="🧮", layout="wide")

# 1. Andmete laadimine
@st.cache_data
def load_data():
    return pd.read_csv("matemaatika_testid.csv")

df = load_data()
all_topics = sorted(df['topic'].unique().tolist())

# --- SIDEBAR ---
st.sidebar.title("Seaded")
selected_topics = st.sidebar.multiselect(
    "Vali teemad harjutamiseks:", 
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
st.title("🧮 Matemaatika enesekontrolli test")

with st.form("test_form"):
    user_answers = {}
    
    for i, q in enumerate(st.session_state.current_test):
        st.markdown(f"### {i+1}. {q['question']}")
        st.caption(f"📍 Teema: {q['topic']}")
        
        options = [q['option_a'], q['option_b'], q['option_c'], q['option_d']]
        
        user_answers[i] = st.radio(
            "Vali üks variant:", 
            options, 
            key=f"radio_{i}",
            index=None
        )
        
        if st.session_state.get('submitted'):
            if user_answers[i] == q['correct_answer']:
                st.success("✅ Õige!")
            else:
                st.error(f"❌ Vale. Õige: **{q['correct_answer']}**")
                with st.expander("Vihje"):
                    st.write(q['hint'])
        st.divider()

    submit_clicked = st.form_submit_button("KONTROLLI VASTUSEID")

# --- KONTROLLI JA HINDE LOOGIKA ---
if submit_clicked or st.session_state.submitted:
    # Kontrollime, kas on vastamata küsimusi
    unanswered = [i for i, ans in user_answers.items() if ans is None]
    
    if unanswered and not st.session_state.confirmed_incomplete:
        st.warning(f"⚠️ Sul on veel **{len(unanswered)}** küsimust vastamata!")
        confirm = st.checkbox("Soovin siiski esitada ja näha tulemusi sellisena nagu on.")
        if confirm:
            st.session_state.confirmed_incomplete = True
            st.rerun()
    else:
        # Arvutame tulemused
        st.session_state.submitted = True
        correct_count = sum(1 for i, q in enumerate(st.session_state.current_test) if user_answers[i] == q['correct_answer'])
        score_percent = (correct_count / len(st.session_state.current_test)) * 100
        
        # Hinde määratlemine
        if score_percent >= 91: grade = "A"
        elif score_percent >= 81: grade = "B"
        elif score_percent >= 71: grade = "C"
        elif score_percent >= 61: grade = "D"
        elif score_percent >= 51: grade = "E"
        else: grade = "F (Mittearvestatud)"

        # Kuvame hinde ja tulemuse
        st.subheader("Sinu koondtulemus")
        c1, c2, c3 = st.columns(3)
        c1.metric("Punktid", f"{correct_count} / {len(st.session_state.current_test)}")
        c2.metric("Protsent", f"{int(score_percent)}%")
        c3.metric("HINNE", grade)

        if grade != "F (Mittearvestatud)":
            st.balloons()
            st.success(f"Palju õnne! Läbisid testi hindele **{grade}**.")
        else:
            st.error("Kahjuks jäi tulemus alla lävendit (51%). Proovi uuesti!")
