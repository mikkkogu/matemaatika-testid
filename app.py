import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Matemaatika Enesekontroll", page_icon="🧮", layout="wide")

# 1. Funktsioon andmete laadimiseks
@st.cache_data
def load_data():
    return pd.read_csv("matemaatika_testid.csv")

df = load_data()
all_topics = sorted(df['topic'].unique().tolist())

# --- SIDEBAR: Teemade valik ---
st.sidebar.title("Seaded")
selected_topics = st.sidebar.multiselect(
    "Vali teemad harjutamiseks:", 
    options=all_topics,
    default=[] # Tühi tähendab "kõik"
)

# Filtreerime andmed vastavalt valikule
if selected_topics:
    filtered_df = df[df['topic'].isin(selected_topics)]
else:
    filtered_df = df

st.sidebar.info(f"Valikus on {len(filtered_df)} küsimust.")

# --- TESTI GENEREERIMISE LOOGIKA ---
if 'current_test' not in st.session_state or st.sidebar.button("Genereeri uus test"):
    # Valime 10 juhuslikku (või vähem, kui andmeid on vähe)
    n_to_sample = min(10, len(filtered_df))
    st.session_state.current_test = filtered_df.sample(n=n_to_sample).to_dict('records')
    st.session_state.submitted = False

# --- PÕHIEKRAAN ---
st.title("🧮 Matemaatika enesekontrolli test")
st.write(f"Sulle on koostatud test **{len(st.session_state.current_test)}** küsimusega.")

# Kasutame vormi, et kõik vastused korraga saata
with st.form("test_form"):
    user_answers = {}
    
    for i, q in enumerate(st.session_state.current_test):
        st.markdown(f"### {i+1}. {q['question']}")
        
        # Kuvame teema märgise
        st.caption(f"📍 Teema: {q['topic']}")
        
        # Vastusevariandid
        options = [q['option_a'], q['option_b'], q['option_c'], q['option_d']]
        
        # Raadionupud vastamiseks
        user_answers[i] = st.radio(
            "Vali üks variant:", 
            options, 
            key=f"radio_{i}",
            index=None # Alustab ilma valikuta
        )
        
        # --- KOHAPEALNE TAGASISIDE ---
        # See ilmub alles siis, kui vorm on saadetud
        if st.session_state.get('submitted'):
            if user_answers[i] == q['correct_answer']:
                st.success(f"✅ Õige!")
            else:
                st.error(f"❌ Vale. Õige vastus on: **{q['correct_answer']}**")
                with st.expander("Vihje / Selgitus"):
                    st.write(q['hint'])
        
        st.divider()

    submit_button = st.form_submit_button("KONTROLLI VASTUSEID")

# --- TULEMUSTE KOKKUVÕTE ---
if submit_button:
    st.session_state.submitted = True
    
    # Arvutame skoori
    correct_count = 0
    for i, q in enumerate(st.session_state.current_test):
        if user_answers[i] == q['correct_answer']:
            correct_count += 1
            
    score_percent = int((correct_count / len(st.session_state.current_test)) * 100)
    
    st.subheader("Testi tulemus")
    col1, col2 = st.columns(2)
    col1.metric("Õigeid vastuseid", f"{correct_count} / {len(st.session_state.current_test)}")
    col2.metric("Protsent", f"{score_percent}%")
    
    if score_percent == 100:
        st.balloons()
    
    # Kuna Streamlit vajab uuesti laadimist, et "submitted" olek näitaks tagasisidet küsimuste juures:
    st.rerun()
