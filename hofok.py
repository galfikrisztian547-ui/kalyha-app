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
        huzat_elo = db.reference('huzat').get() or {}
        ajto_allapot = huzat_elo.get('allapot', 'Ismeretlen')
        uzemmod_elo = huzat_elo.get('uzemmod', 'AUTOMATA')

        col1, col2, col3 = st.columns(3)
        col1.metric("Vízhőfok", f"{akt_ho} °C")
        col2.metric("Ajtó", ajto_allapot)
        col3.metric("Mód", uzemmod_elo)

        st.write("---")
        grafikon.rogzit_es_rajzol(akt_ho)

    elo_adatok()

    huzat_adatok = db.reference('huzat').get() or {}
    uzemmod = huzat_adatok.get('uzemmod', 'AUTOMATA')

    st.write("---")
    if uzemmod == 'AUTOMATA':
        st.subheader("Automata huzat határértékek")
        i_col1, i_col2 = st.columns(2)
        with i_col1:
            also = st.number_input("Alsó határ (Nyit) °C", value=int(huzat_adatok.get('also_hatar', 50)), step=1)
        with i_col2:
            felso = st.number_input("Felső határ (Zár) °C", value=int(huzat_adatok.get('felso_hatar', 70)), step=1)

        if st.button("Mentés 💾", use_container_width=True):
            db.reference('huzat').update({
                'also_hatar': also,
                'felso_hatar': felso,
                'uzemmod': 'AUTOMATA'
            })
            st.success("Huzatszabályzó határértékek mentve!")

        if st.button("Váltás MANUÁLIS Módra 🖐", use_container_width=True):
            db.reference('huzat/uzemmod').set('MANUALIS')
            st.rerun()
    else:
        st.warning("⚠️ Manuális mód aktív: A huzat automata hőfok-figyelése kikapcsolva!")
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            if st.button("NYITÁS 🟢", use_container_width=True):
                db.reference('huzat/parancs').set('NYIT')
                db.reference('huzat/allapot').set('NYITVA')
                st.rerun()
        with b_col2:
            if st.button("ZÁRÁS 🔴", use_container_width=True):
                db.reference('huzat/parancs').set('ZAR')
                db.reference('huzat/allapot').set('ZÁRVA')
                st.rerun()

        if st.button("Váltás AUTOMATA Módra 🤖", use_container_width=True):
            db.reference('huzat/uzemmod').set('AUTOMATA')
            st.rerun()