import streamlit as st
from firebase_admin import db


def mutasd():
    if 'beall_aloldal' not in st.session_state:
        st.session_state.beall_aloldal = 'fomenu'

    # Élő ellenőrzés a Firebase-ből, hogy biztosan pontos legyen a jogosultság
    aktualis_nev = st.session_state.get('nev')
    jogosultsag = st.session_state.get('jogosultsag')
    if aktualis_nev:
        user_adat = db.reference('felhasznalok').child(aktualis_nev).get()
        if isinstance(user_adat, dict):
            jogosultsag = user_adat.get('szerepkor', 'user')
            st.session_state.jogosultsag = jogosultsag

    # --- 1. BEÁLLÍTÁSOK FŐMENÜJE ---
    if st.session_state.beall_aloldal == 'fomenu':
        st.title("⚙️ Beállítások")
        if st.button("🔙 Vissza a Főmenübe"):
            st.session_state.oldal = 'Főmenü'
            st.rerun()
        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("👥 Felhasználók", use_container_width=True):
                st.session_state.beall_aloldal = 'felhasznalok'
                st.rerun()

    # --- 2. FELHASZNÁLÓK ÉS KÉRELMEK ALMENÜ ---
    elif st.session_state.beall_aloldal == 'felhasznalok':
        st.title("👥 Felhasználók")
        if st.button("🔙 Vissza a Beállításokhoz"):
            st.session_state.beall_aloldal = 'fomenu'
            st.rerun()
        st.divider()

        felhasznalok = db.reference('felhasznalok').get()

        # =========================================================
        # A) HA RENDSZERGAZDA (ADMIN) VAN BELÉPVE -> MINDENT LÁT ÉS SZERKESZT
        # =========================================================
        if jogosultsag == 'admin':
            st.subheader("📋 Regisztrált felhasználók és jelszavak")
            if felhasznalok:
                # 1. Rendszergazda (Főnök) legfelül
                for f_nev, f_adat in felhasznalok.items():
                    if isinstance(f_adat, dict) and f_adat.get('szerepkor') == 'admin':
                        jelenlegi_jel = str(f_adat.get('jelszo', ''))
                        st.info(f"👑 **{f_nev}** — Rendszergazda (Főnök)")

                        c1, c2 = st.columns([3, 1])
                        with c1:
                            uj_admin_jel = st.text_input("Jelszó módosítása", value=jelenlegi_jel, key=f"pwd_{f_nev}")
                        with c2:
                            st.write("")
                            st.write("")
                            if st.button("Mentés 💾", key=f"save_{f_nev}", use_container_width=True):
                                if uj_admin_jel.strip():
                                    db.reference('felhasznalok').child(f_nev).update({'jelszo': uj_admin_jel.strip()})
                                    st.success(f"{f_nev} új jelszava mentve!")
                                    st.rerun()
                        st.write("---")

                # 2. További felhasználók
                for f_nev, f_adat in felhasznalok.items():
                    if isinstance(f_adat, dict) and f_adat.get('szerepkor') != 'admin':
                        jelenlegi_jel = str(f_adat.get('jelszo', ''))
                        st.write(f"👤 **{f_nev}** (Felhasználó)")

                        c1, c2, c3 = st.columns([2, 1, 1])
                        with c1:
                            uj_user_jel = st.text_input("Jelszó", value=jelenlegi_jel, key=f"pwd_{f_nev}",
                                                        label_visibility="collapsed")
                        with c2:
                            if st.button("Mentés 💾", key=f"save_{f_nev}", use_container_width=True):
                                if uj_user_jel.strip():
                                    db.reference('felhasznalok').child(f_nev).update({'jelszo': uj_user_jel.strip()})
                                    st.success(f"{f_nev} jelszava módosítva!")
                                    st.rerun()
                        with c3:
                            if st.button("Törlés 🗑️", key=f"del_{f_nev}", use_container_width=True):
                                db.reference('felhasznalok').child(f_nev).delete()
                                st.warning(f"{f_nev} törölve!")
                                st.rerun()
                        st.write("---")
            else:
                st.warning("Nincsenek regisztrált felhasználók.")

            # Függőben lévő kérelmek (csak admin látja)
            st.subheader("📩 Függőben lévő kérelmek")
            kerelmek = db.reference('kerelmek').get()
            if kerelmek:
                for k_nev, k_adat in kerelmek.items():
                    k_jel = k_adat.get('jelszo', '') if isinstance(k_adat, dict) else ''
                    st.write(f"**Kérelmező:** `{k_nev}` | **Kívánt jelszó:** `{k_jel}`")
                    k_col1, k_col2 = st.columns(2)
                    with k_col1:
                        if st.button("✅ Engedélyez", key=f"eng_{k_nev}", use_container_width=True):
                            db.reference('felhasznalok').child(k_nev).set({
                                'jelszo': str(k_jel),
                                'szerepkor': 'user'
                            })
                            db.reference('kerelmek').child(k_nev).delete()
                            st.rerun()
                    with k_col2:
                        if st.button("❌ Elutasít", key=f"elu_{k_nev}", use_container_width=True):
                            db.reference('kerelmek').child(k_nev).delete()
                            st.rerun()
                    st.write("---")
            else:
                st.success("Nincsenek függőben lévő kérelmek.")

        # =========================================================
        # B) HA SIMA FELHASZNÁLÓ VAN BELÉPVE -> CSAK A NEVEKET LÁTJA
        # =========================================================
        else:
            st.subheader("📋 Rendszer tagjai")
            if felhasznalok:
                for f_nev, f_adat in felhasznalok.items():
                    if isinstance(f_adat, dict) and f_adat.get('szerepkor') == 'admin':
                        st.info(f"👑 **{f_nev}** — Rendszergazda")
                for f_nev, f_adat in felhasznalok.items():
                    if isinstance(f_adat, dict) and f_adat.get('szerepkor') != 'admin':
                        st.write(f"👤 **{f_nev}** — Felhasználó")
            else:
                st.warning("Nincsenek regisztrált felhasználók.")