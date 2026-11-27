import streamlit as st
from firebase_admin import db
import grafikon


def mutasd():
    st.title("🌡️ Huzatszabályzó")
    if st.button("🔙 Vissza"):
        st.session_state.oldal = 'Főmenü'
        st.rerun()
    st.divider()

    @st.fragment(run_every=2)
    def elo_adatok():
        akt_ho = db.reference('aktualis_ho').get()
        if akt_ho is None:
            akt_ho = 0
        ajto_allapot = db.reference('allapot').get() or 'Ismeretlen'

        col1, col2 = st.columns(2)
        col1.metric("Vízhőfok", f"{akt_ho} °C")
        col2.metric("Ajtó állapota", ajto_allapot)

        st.write("---")
        grafikon.rogzit_es_rajzol(akt_ho)

    elo_adatok()

    also_mentett = db.reference('also_hatar').get()
    felso_mentett = db.reference('felso_hatar').get()

    st.write("---")
    st.subheader("Automata hőfok határértékek")

    i_col1, i_col2 = st.columns(2)
    with i_col1:
        also = st.number_input("Alsó határ (Nyit) °C", value=int(also_mentett if also_mentett is not None else 50), step=1)
    with i_col2:
        felso = st.number_input("Felső határ (Zár) °C", value=int(felso_mentett if felso_mentett is not None else 70), step=1)

    if st.button("Mentés 💾", use_container_width=True):
        db.reference('also_hatar').set(also)
        db.reference('felso_hatar').set(felso)
        db.reference('uzemmod').set('AUTOMATA')
        db.reference('pumpa').update({
            'ki_hatar': also,
            'be_hatar': felso,
            'uzemmod': 'AUTOMATA'
        })
        st.success("Huzatszabályzó határértékek mentve és aktiválva!")