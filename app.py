import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Matemaatika Enesekontroll", page_icon="🧮")

# 1. Funktsioon küsimuste laadimiseks
@st.cache_data
def load_questions():
    df = pd.read_csv("matemaatika_testid.csv")
    return df.to_dict('records')

all_questions = load_questions()

st.title("🧮 Matemaatika Test")
st.write("Sulle valitakse juhuslikult 10 küsimust kursuse materjalidest.")

# 2. Sessiooni haldus: valime 10 random küsimust ja hoiame neid seal
if 'random_questions' not in st.session_state:
    st.session_state.random_questions = random.sample(all_questions, min(10, len(all_questions)))
    st.session_state.submitted = False

# Nupp uue testi alustamiseks
if st.button("Genereeri uus test"):
    st.session_state.random_questions = random.sample(all_questions, min(10, len(all_questions)))
    st.session_state.submitted = False
    st.rerun()

# 3. Testi vorm
with st.form("math_test"):
    user_answers = []
    for i, q in enumerate(st.session_state.random_questions):
        st.subheader(f"{i+1}. {q['question']}")
        st.caption(f"Teema: {q['topic']}")
        
        # Segame vastusevariandid, et need poleks alati samas järjekorras
        options = [q['option_a'], q['option_b'], q['option_c'], q['option_d']]
        
        ans = st.radio(f"Vali vastus:", options, key=f"q{i}")
        user_answers.append(ans)
        
        with st.expander("Vihje"):
            st.write(q['hint'])
        st.divider()

    submit = st.form_submit_button("KONTROLLI TULEMUSI")

# 4. Tulemuste kuvamine
if submit:
    st.session_state.submitted = True
    score = 0
    for i, q in enumerate(st.session_state.random_questions):
        if user_answers[i] == q['correct_answer']:
            score += 1
            st.success(f"Küsimus {i+1}: Õige!")
        else:
            st.error(f"Küsimus {i+1}: Vale. Õige vastus: {q['correct_answer']}")
    
    percent = (score / len(st.session_state.random_questions)) * 100
    st.metric("Sinu skoor", f"{score} / {len(st.session_state.random_questions)}", f"{percent}%")
    
    if score == len(st.session_state.random_questions):
        st.balloons()
        st.success("Täiuslik tulemus! Oled kontrolltööks valmis.")
    elif score > 7:
        st.info("Väga hea töö!")
    else:
        st.warning("Tasub veel materjale sirvida.")

st.sidebar.markdown("### Info\nSee rakendus kasutab `matemaatika_testid.csv` andmebaasi.")
