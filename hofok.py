import streamlit as st
from firebase_admin import db
import time

MANUALIS_IDO_MP = 120  # 2 perc


def ellenoriz_manualis_lejaratot(huzat_adat):
    uzemmod = huzat_adat.get('uzemmod', 'AUTOMATA')
    if uzemmod != 'MANUALIS':
        return uzemmod, 0, False

    most = int(time.time())
    lejarat = int(huzat_adat.get('manualis_lejarat') or 0)

    if lejarat == 0:
        lejarat = most + MANUALIS_IDO_MP
        db.reference('huzat/manualis_lejarat').set(lejarat)
        return 'MANUALIS', MANUALIS_IDO_MP, False

    hatralevo = lejarat - most
    if hatralevo <= 0:
        db.reference('huzat').update({
            'uzemmod': 'AUTOMATA',
            'manualis_lejarat': 0
        })
        return 'AUTOMATA', 0, True

    return 'MANUALIS', hatralevo, False


def mutasd():
    st.title("🌡️ Huzatszabályzó")
    if st.button("🔙 Vissza"):
        st.session_state.oldal = 'Főmenü'
        st.rerun()
    st.divider()

    huzat_adatok = db.reference('huzat').get() or {}
    uzemmod, _, _ = ellenoriz_manualis_lejaratot(huzat_adatok)
    st.session_state.hofok_utolso_mod = uzemmod

    @st.fragment(run_every=2)
    def elo_adatok():
        akt_ho = db.reference('aktualis_ho').get()
        if akt_ho is None:
            akt_ho = 0
        huzat_elo = db.reference('huzat').get() or {}
        uzemmod_elo, hatralevo_mp, visszavaltott = ellenoriz_manualis_lejaratot(huzat_elo)
        ajto_allapot = huzat_elo.get('allapot', 'Ismeretlen')

        if visszavaltott or uzemmod_elo != st.session_state.get('hofok_utolso_mod'):
            st.session_state.hofok_utolso_mod = uzemmod_elo
            st.rerun(scope="app")

        col1, col2, col3 = st.columns(3)
        col1.metric("Vízhőfok", f"{akt_ho} °C")
        col2.metric("Ajtó", ajto_allapot)
        col3.metric("Mód", uzemmod_elo)

        if uzemmod_elo == 'MANUALIS':
            perc, mp = divmod(hatralevo_mp, 60)
            st.warning(f"⚠️ Manuális mód aktív! Automatikus visszaváltás: {perc}:{mp:02d} múlva")

    elo_adatok()

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
                'uzemmod': 'AUTOMATA',
                'manualis_lejarat': 0
            })
            st.success("Huzatszabályzó határértékek mentve!")

        if st.button("Váltás MANUÁLIS Módra 🖐", use_container_width=True):
            db.reference('huzat').update({
                'uzemmod': 'MANUALIS',
                'manualis_lejarat': int(time.time()) + MANUALIS_IDO_MP
            })
            st.rerun()
    else:
        aktualis_ajto = (db.reference('huzat/allapot').get() or '').strip().upper()
        if 'manualis_jelzes' not in st.session_state:
            st.session_state.manualis_jelzes = ""

        b_col1, b_col2 = st.columns(2)
        with b_col1:
            if st.button("NYITÁS 🟢", use_container_width=True):
                db.reference('huzat/manualis_lejarat').set(int(time.time()) + MANUALIS_IDO_MP)
                if aktualis_ajto == 'NYITVA':
                    st.session_state.manualis_jelzes = "ℹ️ A huzat már NYITVA van!"
                else:
                    db.reference('huzat').update({
                        'parancs': 'NYIT',
                        'allapot': 'NYITVA'
                    })
                    st.session_state.manualis_jelzes = "✅ Nyitás parancs elküldve (NYITVA)."
                st.rerun()
        with b_col2:
            if st.button("ZÁRÁS 🔴", use_container_width=True):
                db.reference('huzat/manualis_lejarat').set(int(time.time()) + MANUALIS_IDO_MP)
                if aktualis_ajto == 'ZÁRVA':
                    st.session_state.manualis_jelzes = "ℹ️ A huzat már ZÁRVA van!"
                else:
                    db.reference('huzat').update({
                        'parancs': 'ZAR',
                        'allapot': 'ZÁRVA'
                    })
                    st.session_state.manualis_jelzes = "✅ Zárás parancs elküldve (ZÁRVA)."
                st.rerun()

        if st.session_state.manualis_jelzes:
            st.info(st.session_state.manualis_jelzes)

        if st.button("Váltás AUTOMATA Módra 🤖", use_container_width=True):
            st.session_state.manualis_jelzes = ""
            db.reference('huzat').update({
                'uzemmod': 'AUTOMATA',
                'manualis_lejarat': 0
            })
            st.rerun()