import streamlit as st
from firebase_admin import db
import time
from datetime import datetime


def mutasd():
    aktualis_nev = st.session_state.get('nev', '')

    if 'chat_partner' not in st.session_state:
        st.session_state.chat_partner = None

    # --- 1. FELHASZNÁLÓ VÁLASZTÓ LISTA (3 mp-enként frissül) ---
    if st.session_state.chat_partner is None:
        st.title("💬 Üzenetek")
        if st.button("🔙 Vissza a Főmenübe"):
            st.session_state.oldal = 'Főmenü'
            st.rerun()
        st.divider()

        @st.fragment(run_every=3)
        def partner_lista():
            st.subheader("Válaszd ki, kinek szeretnél írni:")
            felhasznalok = db.reference('felhasznalok').get() or {}
            osszes_uzenet = db.reference('uzenetek').get() or {}

            # Megszámoljuk, kitől hány olvasatlan üzenetünk jött
            olvasatlan_kitol = {}
            for u_id, u_adat in osszes_uzenet.items():
                if isinstance(u_adat, dict):
                    if u_adat.get('cimzett') == aktualis_nev and not u_adat.get('olvasva', True):
                        k = u_adat.get('kuldo', '')
                        olvasatlan_kitol[k] = olvasatlan_kitol.get(k, 0) + 1

            van_mas = False
            for f_nev, f_adat in felhasznalok.items():
                if f_nev != aktualis_nev and isinstance(f_adat, dict):
                    van_mas = True
                    szerep = "👑 Rendszergazda" if f_adat.get('szerepkor') == 'admin' else "👤 Felhasználó"
                    uj_db = olvasatlan_kitol.get(f_nev, 0)

                    if uj_db > 0:
                        gomb_szoveg = f"🔴 {f_nev} ({szerep}) — {uj_db} új üzenet!"
                    else:
                        gomb_szoveg = f"💬 {f_nev} ({szerep})"

                    if st.button(gomb_szoveg, key=f"chat_{f_nev}", use_container_width=True):
                        st.session_state.chat_partner = f_nev
                        st.rerun()

            if not van_mas:
                st.info("Még nincs más regisztrált felhasználó, akinek írhatnál.")

        partner_lista()

    # --- 2. PRIVÁT BESZÉLGETÉS ABLAK (3 mp-enként élőben frissül) ---
    else:
        partner = st.session_state.chat_partner
        st.title(f"💬 Beszélgetés: {partner}")

        if st.button("🔙 Vissza a felhasználókhoz", use_container_width=True):
            st.session_state.chat_partner = None
            st.rerun()
        st.divider()

        @st.fragment(run_every=3)
        def elo_chat():
            uzenetek_ref = db.reference('uzenetek')
            osszes_uzenet = uzenetek_ref.get() or {}

            most_ido = time.time()
            harom_honap_mp = 90 * 24 * 60 * 60

            beszelgetes = []
            for u_id, u_adat in osszes_uzenet.items():
                if not isinstance(u_adat, dict):
                    continue

                kuldes_ido = u_adat.get('timestamp', 0)
                if kuldes_ido > 0 and (most_ido - kuldes_ido) > harom_honap_mp:
                    uzenetek_ref.child(u_id).delete()
                    continue

                kuldo = u_adat.get('kuldo')
                cimzett = u_adat.get('cimzett')

                if (kuldo == aktualis_nev and cimzett == partner) or (kuldo == partner and cimzett == aktualis_nev):
                    # Ha ő küldte nekünk és még olvasatlan volt, megjelöljük olvasottnak!
                    if kuldo == partner and cimzett == aktualis_nev and not u_adat.get('olvasva', True):
                        uzenetek_ref.child(u_id).update({'olvasva': True})
                    beszelgetes.append((kuldes_ido, u_adat))

            beszelgetes.sort(key=lambda x: x[0])

            if beszelgetes:
                for _, u in beszelgetes:
                    ido_szoveg = u.get('ido_szoveg', '')
                    szoveg = u.get('szoveg', '')
                    if u.get('kuldo') == aktualis_nev:
                        st.success(f"**Te** ({ido_szoveg}):\n\n{szoveg}")
                    else:
                        st.info(f"**{partner}** ({ido_szoveg}):\n\n{szoveg}")
            else:
                st.caption("Még nincs üzenetváltásotok. Írj neki elsőként!")

        elo_chat()

        st.write("---")

        # Új üzenet írása és küldése
        with st.form(key="uzenet_kuldes_form", clear_on_submit=True):
            uj_uzenet = st.text_input("Üzenet írása...")
            kuldve = st.form_submit_button("Küldés 📤", use_container_width=True)
            if kuldve and uj_uzenet.strip():
                most = datetime.now().strftime("%Y.%m.%d %H:%M")
                db.reference('uzenetek').push({
                    'kuldo': aktualis_nev,
                    'cimzett': partner,
                    'szoveg': uj_uzenet.strip(),
                    'timestamp': time.time(),
                    'ido_szoveg': most,
                    'olvasva': False
                })
                st.rerun()