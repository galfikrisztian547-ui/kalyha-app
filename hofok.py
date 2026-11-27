import streamlit as st
from firebase_admin import db
import grafikon


def mutasd():
    st.title("🌡️ Huzatszabályzó")
    if st.button("🔙 Vissza"):
        st.session_state.oldal = 'Főmenü'
        st.rerun()
    st.divider()

    @st.fragment(run_every=3)
    def elo_adatok():
        adatok = db.reference('/').get() or {}
        akt_ho = adatok.get('aktualis_ho', 0)

        col1, col2 = st.columns(2)
        col1.metric("Vízhőfok", f"{akt_ho} °C")
        col2.metric("Ajtó állapota", adatok.get('allapot', 'Ismeretlen'))

        st.write("---")
        # Napi grafikon megjelenítése
        grafikon.rogzit_es_rajzol(akt_ho)

    elo_adatok()

    adatok = db.reference('/').get() or {}

    st.write("---")
    st.subheader("Automata hőfok határértékek")

    i_col1, i_col2 = st.columns(2)
    with i_col1:
        also = st.number_input("Alsó határ (Nyit) °C", value=int(adatok.get('also_hatar', 50)), step=1)
    with i_col2:
        felso = st.number_input("Felső határ (Zár) °C", value=int(adatok.get('felso_hatar', 70)), step=1)

    if st.button("Mentés 💾", use_container_width=True):
        db.reference('also_hatar').set(also)
        db.reference('felso_hatar').set(felso)
        db.reference('uzemmod').set('AUTOMATA')
        # Összekötve az ESP32 vezérléssel: Alsó = KI (26-os láb), Felső = BE (13-as láb)
        db.reference('pumpa').update({
            'ki_hatar': also,
            'be_hatar': felso,
            'uzemmod': 'AUTOMATA'
        })
        st.success("Huzatszabályzó határértékek mentve és aktiválva!")import streamlit as st
from firebase_admin import db
import grafikon


def mutasd():
    st.title("🌡️ Huzatszabályzó")
    if st.button("🔙 Vissza"):
        st.session_state.oldal = 'Főmenü'
        st.rerun()
    st.divider()

    @st.fragment(run_every=3)
    def elo_adatok():
        adatok = db.reference('/').get() or {}
        akt_ho = adatok.get('aktualis_ho', 0)

        col1, col2 = st.columns(2)
        col1.metric("Vízhőfok", f"{akt_ho} °C")
        col2.metric("Ajtó állapota", adatok.get('allapot', 'Ismeretlen'))

        st.write("---")
        # Napi grafikon megjelenítése
        grafikon.rogzit_es_rajzol(akt_ho)

    elo_adatok()

    adatok = db.reference('/').get() or {}

    st.write("---")
    st.subheader("Automata hőfok határértékek")

    i_col1, i_col2 = st.columns(2)
    with i_col1:
        also = st.number_input("Alsó határ (Nyit) °C", value=int(adatok.get('also_hatar', 50)), step=1)
    with i_col2:
        felso = st.number_input("Felső határ (Zár) °C", value=int(adatok.get('felso_hatar', 70)), step=1)

    if st.button("Mentés 💾", use_container_width=True):
        db.reference('also_hatar').set(also)
        db.reference('felso_hatar').set(felso)
        db.reference('uzemmod').set('AUTOMATA')
        # Összekötve az ESP32 vezérléssel: Alsó = KI (26-os láb), Felső = BE (13-as láb)
        db.reference('pumpa').update({
            'ki_hatar': also,
            'be_hatar': felso,
            'uzemmod': 'AUTOMATA'
        })
        st.success("Huzatszabályzó határértékek mentve és aktiválva!")