import streamlit as st
from firebase_admin import db


def mutasd():
    st.title("💧 Keringető Szivattyú")
    if st.button("🔙 Vissza"):
        st.session_state.oldal = 'Főmenü'
        st.rerun()
    st.divider()

    aktualis_ho = db.reference('aktualis_ho').get()
    if aktualis_ho is None:
        aktualis_ho = 0

    pumpa_adatok = db.reference('pumpa').get() or {}
    uzemmod = pumpa_adatok.get('uzemmod', 'AUTOMATA')
    allapot = pumpa_adatok.get('allapot', 'KI')

    col1, col2, col3 = st.columns(3)
    col1.metric("Vízhőfok", f"{aktualis_ho} °C")
    col2.metric("Szivattyú", allapot)
    col3.metric("Mód", uzemmod)

    st.write("---")
    if uzemmod == 'AUTOMATA':
        i_col1, i_col2 = st.columns(2)
        with i_col1:
            ki_hatar = st.number_input("Kikapcsolási hőfok (KI) °C", value=int(pumpa_adatok.get('ki_hatar', 35)),
                                       step=1)
        with i_col2:
            be_hatar = st.number_input("Bekapcsolási hőfok (BE) °C", value=int(pumpa_adatok.get('be_hatar', 45)),
                                       step=1)

        if st.button("Mentés 💾", use_container_width=True):
            db.reference('pumpa/ki_hatar').set(ki_hatar)
            db.reference('pumpa/be_hatar').set(be_hatar)
            st.success("Vízpumpa határértékek mentve!")

        if st.button("Váltás MANUÁLIS Módra 🖐", use_container_width=True):
            db.reference('pumpa/uzemmod').set('MANUALIS')
            st.rerun()
    else:
        st.warning("⚠️ Manuális mód aktív: A hőfok figyelés kikapcsolva!")
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            if st.button("BEKAPCSOLÁS 🟢", use_container_width=True):
                db.reference('pumpa/parancs').set('BE')
                db.reference('pumpa/allapot').set('BE')
                st.rerun()
        with b_col2:
            if st.button("KIKAPCSOLÁS 🔴", use_container_width=True):
                db.reference('pumpa/parancs').set('KI')
                db.reference('pumpa/allapot').set('KI')
                st.rerun()

        if st.button("Váltás AUTOMATA Módra 🤖", use_container_width=True):
            db.reference('pumpa/uzemmod').set('AUTOMATA')
            st.rerun()