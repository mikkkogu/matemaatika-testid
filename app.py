import streamlit as st

st.set_page_config(page_title="Matemaatika Enesekontroll", page_icon="🧮")

st.title("🧮 Matemaatika Test: Mitme muutuja funktsioonid")
st.write("See test aitab sul kontrollida teadmisi kahe muutuja funktsioonide ja ekstreemumite kohta.")

# Küsimuste andmebaas
questions = [
    {
        "question": "1. Mis on funktsiooni z = f(x, y) statsionaarne punkt?",
        "options": [
            "Punkt, kus funktsiooni väärtus on 0",
            "Punkt, kus mõlemad osatuletised (dz/dx ja dz/dy) on võrdsed nulliga",
            "Punkt, kus funktsioon on pidev",
            "Punkt, mis asub graafiku keskpunktis"
        ],
        "answer": "Punkt, kus mõlemad osatuletised (dz/dx ja dz/dy) on võrdsed nulliga",
        "hint": "Ekstreemumi tarvilik tingimus."
    },
    {
        "question": "2. Kui osatuletiste abil leitud determinandi väärtus statsionaarses punktis on D < 0, siis on tegemist...",
        "options": [
            "Lokaalse maksimumiga",
            "Lokaalse miinimumiga",
            "Sadulpunktiga (ekstreemum puudub)",
            "Määramatusega, vaja on täiendavat uurimist"
        ],
        "answer": "Sadulpunktiga (ekstreemum puudub)",
        "hint": "D = fxx * fyy - (fxy)^2. Kui D < 0, siis pind 'kaardub' eri suundades."
    },
    {
        "question": "3. Mida tähistab täisdiferentsiaal dz?",
        "options": [
            "Funktsiooni täpset muutu",
            "Funktsiooni lineaarset peamuutu",
            "Funktsiooni väärtust punktis (0,0)",
            "Tuletist x-telje suunas"
        ],
        "answer": "Funktsiooni lineaarset peamuutu",
        "hint": "dz = (dz/dx)*dx + (dz/dy)*dy"
    }
]

# Kasutaja vastuste salvestamine
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

with st.form("test_form"):
    user_answers = []
    for i, q in enumerate(questions):
        st.subheader(q["question"])
        ans = st.radio(f"Vali õige vastus ({i}):", q["options"], key=f"q{i}")
        user_answers.append(ans)
        with st.expander("Vihje"):
            st.write(q["hint"])
        st.divider()
    
    submit = st.form_submit_button("Kontrolli vastuseid")

if submit:
    st.session_state.submitted = True
    correct_count = 0
    for i, q in enumerate(questions):
        if user_answers[i] == q["answer"]:
            correct_count += 1
            st.success(f"Küsimus {i+1}: Õige!")
        else:
            st.error(f"Küsimus {i+1}: Vale. Õige vastus oli: {q['answer']}")
    
    st.metric("Sinu tulemus", f"{correct_count} / {len(questions)}")
    if correct_count == len(questions):
        st.balloons()

st.sidebar.info("See äpp on loodud kordamiseks kontrolltööks nr 1.")
