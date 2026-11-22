import streamlit as st
import streamlit.components.v1 as components
from firebase_admin import db
from datetime import datetime, timedelta
import time
import urllib.request

# Ide írj egy egyedi, titkos csatornanevet, amire az ntfy appban feliratkoztok telefonon
NTFY_CSATORNA = "kalyha_galfi_riasztas_2026"

def kuld_telefon_ertesitest(cim, uzenet):
    try:
        req = urllib.request.Request(
            f"https://ntfy.sh/{NTFY_CSATORNA}",
            data=uzenet.encode("utf-8"),
            headers={
                "Title": cim.encode("utf-8"),
                "Priority": "high",
                "Tags": "fire,bell"
            }
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass

def mutasd():
    if st.button("⬅️ Vissza a Főmenübe"):
        st.session_state.oldal = 'Főmenü'
        st.rerun()

    st.title("🔥 Tűzrakás & Időzítő")

    aktualis_nev = st.session_state.get('nev', 'Ismeretlen')
    tuz_ref = db.reference('tuzrakas')

    # --- ÚJ TŰZRAKÁS RÖGZÍTÉSE ---
    st.subheader("🪵 Új rárakás rögzítése")

    col_ora, col_perc = st.columns(2)
    with col_ora:
        ora_be = st.number_input("Óra (0 - 12)", min_value=0, max_value=12, value=2, step=1)
    with col_perc:
        perc_be = st.number_input("Perc (0 - 60)", min_value=0, max_value=60, value=0, step=1)

    osszes_perc = int(ora_be) * 60 + int(perc_be)

    if st.button("🔥 MEGRAKTAM A TÜZET MOST", use_container_width=True):
        if osszes_perc <= 0:
            st.error("Adj meg legalább 1 percet!")
        else:
            most_ts = int(time.time())
            lejarat_ts = most_ts + (osszes_perc * 60)
            most_str = datetime.now().strftime("%Y.%m.%d %H:%M")
            lejarat_str = (datetime.now() + timedelta(minutes=osszes_perc)).strftime("%H:%M")

            tuz_ref.update({
                'utolso_ki': aktualis_nev,
                'utolso_mikor_str': most_str,
                'utolso_ts': most_ts,
                'lejarat_ts': lejarat_ts,
                'lejarat_str': lejarat_str,
                'idotartam_perc': osszes_perc,
                'riasztas_elkuldve': False
            })

            # Napló mentése
            db.reference('tuzrakas_naplo').push({
                'ki': aktualis_nev,
                'mikor': most_str,
                'percek': osszes_perc
            })

            # Azonnali értesítés a telefonra
            kuld_telefon_ertesitest(
                "Kályha megrakva!",
                f"{aktualis_nev} megrakta a tüzet ({most_str}). Következő rárakás: {lejarat_str} ({ora_be} óra {perc_be} perc múlva)"
            )
            st.success(f"Rögzítve ({ora_be} óra {perc_be} perc)! Következő rárakás: {lejarat_str}")
            st.rerun()

    st.divider()

    # --- ÉLŐ ÁLLAPOT ÉS VISSZASZÁMLÁLÓ ---
    @st.fragment(run_every=5)
    def elo_allapot():
        friss = db.reference('tuzrakas').get() or {}
        if 'lejarat_ts' not in friss:
            st.info("Még nem volt rögzítve tűzrakás.")
            return

        most_ts = int(time.time())
        hatralevo_mp = friss['lejarat_ts'] - most_ts

        st.write(f"👤 **Utoljára megrakta:** {friss.get('utolso_ki', '-')}")
        st.write(f"🕒 **Rárakás ideje:** {friss.get('utolso_mikor_str', '-')}")
        st.write(f"⏰ **Következő rárakás:** {friss.get('lejarat_str', '-')}")

        if hatralevo_mp > 0:
            ora = hatralevo_mp // 3600
            perc = (hatralevo_mp % 3600) // 60
            mp = hatralevo_mp % 60
            st.success(f"⏳ Hátralévő idő: **{ora} óra {perc} perc {mp} mp**")
        else:
            keses_perc = abs(hatralevo_mp) // 60
            st.error(f"⚠️ **LEJÁRT AZ IDŐ! ({keses_perc} perce rá kellett volna tenni!)**")

            # Ha még nem küldtünk push értesítést a lejáratról, most elküldjük
            if not friss.get('riasztas_elkuldve', False):
                db.reference('tuzrakas').update({'riasztas_elkuldve': True})
                kuld_telefon_ertesitest(
                    "RÁ KELL TENNI A TŰZRE!",
                    f"Lejárt a {friss.get('idotartam_perc', '')} perces időzítő! Ideje megrakni a kályhát."
                )

            # Hangjelzés, ha nyitva van az app
            components.html(
                """
                <script>
                    try {
                        const ctx = new (window.AudioContext || window.webkitAudioContext)();
                        const osc = ctx.createOscillator();
                        osc.type = 'square';
                        osc.frequency.setValueAtTime(950, ctx.currentTime);
                        osc.connect(ctx.destination);
                        osc.start();
                        osc.stop(ctx.currentTime + 0.3);
                    } catch (e) {}
                </script>
                """,
                height=0,
            )

    elo_allapot()

    st.divider()

    # --- UTOLSÓ 5 TŰZRAKÁS NAPLÓJA ---
    with st.expander("📜 Utolsó tűzrakások előzményei"):
        naplo = db.reference('tuzrakas_naplo').get() or {}
        if naplo:
            lista = list(naplo.values())[-5:]
            lista.reverse()
            for elem in lista:
                p = elem.get('percek', 0)
                st.write(f"• **{elem.get('mikor')}** – {elem.get('ki')} ({p // 60} óra {p % 60} perc)")
        else:
            st.write("Nincs még előzmény.")