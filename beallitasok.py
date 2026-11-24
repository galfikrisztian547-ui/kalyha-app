import streamlit as st
from firebase_admin import db
import random
import time


def mutasd():
    if 'beall_aloldal' not in st.session_state:
        st.session_state.beall_aloldal = 'fomenu'

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
        with col2:
            if st.button("📶 Wi-Fi és ESP32", use_container_width=True):
                st.session_state.beall_aloldal = 'esp32'
                st.rerun()

        st.write("")
        if st.button("⏱️ Nyitás-Zárás idő & Hőfok teszt", use_container_width=True):
            st.session_state.beall_aloldal = 'idozites_teszt'
            st.rerun()

    # --- 2. FELHASZNÁLÓK ÉS KÉRELMEK ALMENÜ ---
    elif st.session_state.beall_aloldal == 'felhasznalok':
        st.title("👥 Felhasználók")
        if st.button("🔙 Vissza a Beállításokhoz"):
            st.session_state.beall_aloldal = 'fomenu'
            st.rerun()
        st.divider()

        felhasznalok = db.reference('felhasznalok').get()

        if jogosultsag == 'admin':
            st.subheader("📋 Regisztrált felhasználók és jelszavak")
            if felhasznalok:
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

    # --- 3. WI-FI ÉS ESP32 KEZELŐ ---
    elif st.session_state.beall_aloldal == 'esp32':
        st.title("📶 Wi-Fi és ESP32")
        if st.button("🔙 Vissza a Beállításokhoz"):
            st.session_state.beall_aloldal = 'fomenu'
            st.rerun()
        st.divider()

        esp_ref = db.reference('esp32_config')

        @st.fragment(run_every=4)
        def esp_statusz_panel():
            friss = db.reference('esp32_config').get() or {}
            parosito_kod = friss.get('parosito_kod', '')
            utolso_sziv = friss.get('utolso_eletjel', 0)
            aktiv_wifi = friss.get('wifi_ssid', 'Nincs megadva')
            most = int(time.time())

            if parosito_kod:
                st.info(f"🔑 **Aktív párosító kód:** `{parosito_kod}` | **Aktuális Wi-Fi:** `{aktiv_wifi}`")

            if utolso_sziv > 0 and (most - int(utolso_sziv)) <= 20:
                st.success("🟢 **Az ESP32 kártya ONLINE!**")
            elif parosito_kod:
                st.warning("🟡 **Várakozás a kártya csatlakozására...**")
            else:
                st.error("🔴 **Nincs párosított ESP32 kártya!**")

        esp_statusz_panel()
        st.divider()

        if jogosultsag == 'admin':
            adatok = esp_ref.get() or {}

            st.subheader("📡 Átcsatlakozás másik Wi-Fi-re (ha már online)")
            col_scan1, col_scan2 = st.columns([3, 1])
            with col_scan1:
                st.write("Válassz a kártya körül talált Wi-Fi-k közül:")
            with col_scan2:
                if st.button("🔍 Keresés", use_container_width=True):
                    esp_ref.update({'keres_wifi': True})
                    st.toast("ESP32 keresi a Wi-Fi hálózatokat...")
                    time.sleep(2)
                    st.rerun()

            nyers_lista = adatok.get('elerheto_wifik', '')
            wifi_opciok = [w.strip() for w in str(nyers_lista).split('|') if w.strip()]
            jelenlegi_ssid = adatok.get('wifi_ssid', '')
            if jelenlegi_ssid and jelenlegi_ssid not in wifi_opciok:
                wifi_opciok.insert(0, jelenlegi_ssid)

            if wifi_opciok:
                alap_index = wifi_opciok.index(jelenlegi_ssid) if jelenlegi_ssid in wifi_opciok else 0
                wifi_nev = st.selectbox("Elérhető Wi-Fi hálózatok", options=wifi_opciok, index=alap_index)
            else:
                st.caption("Ha az ESP32 még offline, előbb csatlakoztasd a `Kalyha_Beallitas` Wi-Fi-n, és itt azonnal megjelennek a Wi-Fi-k.")
                wifi_nev = st.selectbox("Elérhető Wi-Fi hálózatok", options=["(Még nincs betöltött Wi-Fi lista)"])

            wifi_jel = st.text_input("Új Wi-Fi jelszava", value=adatok.get('wifi_pass', ''), type="password")
            kod_mezo = st.text_input("6 jegyű párosító kód", value=adatok.get('parosito_kod', ''))

            if st.button("💾 Átállás a kiválasztott Wi-Fi-re", use_container_width=True):
                if wifi_nev and wifi_nev != "(Még nincs betöltött Wi-Fi lista)":
                    vegso_kod = kod_mezo.strip() or str(random.randint(100000, 999999))
                    esp_ref.update({
                        'wifi_ssid': wifi_nev,
                        'wifi_pass': wifi_jel,
                        'parosito_kod': vegso_kod
                    })
                    st.success(f"Mentve! Az ESP32 otthagyja a régit és átáll a(z) '{wifi_nev}' hálózatra.")
                    st.rerun()
                else:
                    st.error("Előbb csatlakoztasd az ESP32-t, hogy betöltődjenek a Wi-Fi-k!")

            st.divider()
            st.subheader("🔑 Új párosító kód generálása")
            if st.button("🔄 Új 6 jegyű kód kérése", use_container_width=True):
                uj_kod = str(random.randint(100000, 999999))
                esp_ref.update({
                    'parosito_kod': uj_kod,
                    'utolso_eletjel': 0
                })
                st.success(f"Új kód létrehozva: {uj_kod}")
                st.rerun()
        else:
            st.warning("Csak a Rendszergazda módosíthatja a Wi-Fi beállításokat.")

    # --- 4. NYITÁS-ZÁRÁS IDŐZÍTÉS ÉS HŐFOK TESZT ALMENÜ ---
    elif st.session_state.beall_aloldal == 'idozites_teszt':
        st.title("⏱️ Időzítés és Teszt")
        if st.button("🔙 Vissza a Beállításokhoz"):
            st.session_state.beall_aloldal = 'fomenu'
            st.rerun()
        st.divider()

        st.subheader("⚙️ Motor / Relé működési ideje")
        st.write("Mennyi ideig kapjon áramot a mozgató motor nyitáskor vagy záráskor (utána automatikusan lekapcsol):")

        jelenlegi_ido = db.reference('esp32_config/mozgatas_mp').get()
        if jelenlegi_ido is None:
            jelenlegi_ido = 3.0

        uj_ido = st.number_input(
            "Nyitás / Zárás időtartama (másodperc)",
            min_value=0.5,
            max_value=30.0,
            value=float(jelenlegi_ido),
            step=0.5
        )
        if st.button("Időzítés mentése 💾", use_container_width=True):
            db.reference('esp32_config/mozgatas_mp').set(float(uj_ido))
            st.success(f"Mentve! Mostantól {uj_ido} másodpercig ad áramot, aztán lekapcsol.")

        st.divider()

        st.subheader("🧪 Vízhőfok szimulátor (Szenzor nélküli teszt)")
        st.write("Húzd el a csúszkát, mintha melegedne vagy hűlne a víz, és nézd az ESP32 LED-jét:")

        akt_ho = db.reference('aktualis_ho').get()
        if akt_ho is None:
            akt_ho = 22.5

        teszt_ho = st.slider("Szimulált vízhőfok (°C)", min_value=15.0, max_value=95.0, value=float(akt_ho), step=0.5)
        if st.button("🌡️ Hőfok beküldése", use_container_width=True):
            db.reference('aktualis_ho').set(float(teszt_ho))
            st.success(f"Vízhőfok beállítva erre: {teszt_ho} °C")