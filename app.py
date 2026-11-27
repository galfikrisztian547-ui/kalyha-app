import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
import hashlib
import time

# BEIMPORTÁLJUK A KÜLSŐ FÁJLOKAT
import hofok
import kamera
import beallitasok
import uzenetek
import tuzrakas
import eletjel

st.set_page_config(page_title="Kályha App", page_icon="🔥", layout="centered")

APP_LINK = "https://kalyha-app-f6ktjmojgtaxtus3rtnigd.streamlit.app/"


def mutasd_qr_kod():
    qr_kep_url = f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data={APP_LINK}"
    st.write("---")
    st.markdown("<h4 style='text-align: center; color: #FFFFFF;'>📲 Applikáció megnyitása</h4>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='text-align: center; margin: 10px 0;'>"
        f"<img src='{qr_kep_url}' width='180' style='border-radius: 10px; border: 8px solid #FFFFFF; background: #FFFFFF;' />"
        f"</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center; color: #AAAAAA; font-size: 14px;'>Szkenneld be egy másik telefonnal!</p>",
        unsafe_allow_html=True
    )


# CSS - FEKETE HÁTTÉR, ZÖLD GOMBOK, FEHÉR MEZŐK PIROS BETŰKKEL
st.markdown("""
    <style>
    .stApp, .main { background-color: #000000 !important; }
    h1, h2, h3, label, div[data-testid="stMetricLabel"] > label { color: #FFFFFF !important; }
    p { color: #FFFFFF !important; } 
    div[data-testid="stAlert"] p { color: #000000 !important; font-weight: bold !important; }

    div.stButton > button, div.stFormSubmitButton > button {
        background-color: #111111 !important;
        color: #00FF00 !important; 
        font-weight: bold !important;
        border: 2px solid #444444 !important;
    }
    div[data-testid="column"] button { height: 100px !important; border-radius: 15px !important; font-size: 18px !important; }

    div[data-baseweb="input"], 
    div[data-baseweb="input"] > div, 
    div[data-baseweb="base-input"] { 
        background-color: #FFFFFF !important; 
    }

    input, input[type="text"], input[type="password"], input[type="number"] { 
        background-color: #FFFFFF !important; 
        color: #FF0000 !important; 
        -webkit-text-fill-color: #FF0000 !important; 
        font-weight: 900 !important; 
        font-size: 18px !important;
        border: 2px solid #555555 !important; 
    }

    div[data-testid="stMetricValue"] { color: #00FF00 !important; }
    </style>
""", unsafe_allow_html=True)

if not firebase_admin._apps:
    if "firebase" in st.secrets:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
    else:
        cred = credentials.Certificate('firebase-kulcs.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://kalyhafigyelo-default-rtdb.europe-west1.firebasedatabase.app/'})

if 'belepve' not in st.session_state:
    st.session_state.belepve = False
if 'oldal' not in st.session_state:
    st.session_state.oldal = 'Főmenü'
if 'utolso_jelzett_uzenet_id' not in st.session_state:
    st.session_state.utolso_jelzett_uzenet_id = None


# --- ESZKÖZ UJJLENYOMAT KÉSZÍTÉSE (BÖNGÉSZŐ + NYELV + PLATFORM ALAPJÁN) ---
def eszkoz_azonosito():
    fejlecek = st.context.headers
    ua = fejlecek.get("User-Agent", "ismeretlen")
    lang = fejlecek.get("Accept-Language", "")
    sec_plat = fejlecek.get("Sec-Ch-Ua-Platform", "")
    nyers = f"{ua}|{lang}|{sec_plat}"
    return hashlib.sha256(nyers.encode("utf-8")).hexdigest()[:24]


aktualis_eszkoz_id = eszkoz_azonosito()
felhasznalok = db.reference('felhasznalok').get()

# --- AUTOMATIKUS BELÉPTETÉS FIREBASE ALAPJÁN (FRISSÍTÉSKOR IS MEGMARAD) ---
if not st.session_state.belepve and felhasznalok:
    mentett_user = db.reference(f'bejelentkezett_eszkozok/{aktualis_eszkoz_id}').get()
    if mentett_user and mentett_user in felhasznalok:
        st.session_state.belepve = True
        st.session_state.jogosultsag = felhasznalok[mentett_user].get('szerepkor', 'user')
        st.session_state.nev = mentett_user

# --- LOGIN (FŐ) KÉPERNYŐ ---
if not st.session_state.belepve:
    st.title("🔒 Kályhafigyelő")

    if felhasznalok is None:
        st.warning("Még nincs Rendszergazda! Az első fiók automatikusan a Főprofil (Admin) lesz!")
        uj_nev = st.text_input("Főprofil Felhasználónév").strip()
        uj_jelszo = st.text_input("Jelszó", type="password").strip()
        if st.button("Főprofil Létrehozása 👑", use_container_width=True):
            if uj_nev and uj_jelszo:
                db.reference('felhasznalok').child(uj_nev).set({'jelszo': str(uj_jelszo), 'szerepkor': 'admin'})
                db.reference(f'bejelentkezett_eszkozok/{aktualis_eszkoz_id}').set(uj_nev)
                st.session_state.belepve = True
                st.session_state.jogosultsag = 'admin'
                st.session_state.nev = uj_nev
                st.rerun()
            else:
                st.error("Add meg a nevet és a jelszót is!")
    else:
        tab1, tab2 = st.tabs(["🚪 Belépés", "📝 Regisztráció kérése"])
        with tab1:
            nev = st.text_input("Felhasználónév").strip()
            jelszo = st.text_input("Jelszó", type="password").strip()
            maradjak_belepve = st.checkbox("Maradjak bejelentkezve", value=True)

            if st.button("Belépés", use_container_width=True):
                if nev in felhasznalok and str(felhasznalok[nev].get('jelszo', '')).strip() == jelszo:
                    st.session_state.belepve = True
                    st.session_state.jogosultsag = felhasznalok[nev].get('szerepkor', 'admin')
                    st.session_state.nev = nev
                    if maradjak_belepve:
                        db.reference(f'bejelentkezett_eszkozok/{aktualis_eszkoz_id}').set(nev)
                    else:
                        db.reference(f'bejelentkezett_eszkozok/{aktualis_eszkoz_id}').delete()
                    st.rerun()
                else:
                    st.error("Hibás adatok, vagy még nem hagyta jóvá a Rendszergazda!")
        with tab2:
            st.warning("Új fiókot csak a Rendszergazda jóváhagyásával lehet létrehozni.")
            ker_nev = st.text_input("Kívánt Felhasználónév", key="ker_nev").strip()
            ker_jelszo = st.text_input("Kívánt Jelszó", type="password", key="ker_jel").strip()
            if st.button("Kérelem Beküldése 📩", use_container_width=True):
                if ker_nev in felhasznalok:
                    st.error("Ez a név már létezik!")
                elif ker_nev and ker_jelszo:
                    db.reference('kerelmek').child(ker_nev).set({'jelszo': str(ker_jelszo)})
                    st.success("Kérelem elküldve! A Rendszergazda hagyhatja jóvá a Beállításokban.")

    # QR KÓD A BELÉPÉSI KÉPERNYŐN IS
    mutasd_qr_kod()

# --- HA BELÉPTÜNK ---
else:
    aktualis_nev = st.session_state.get('nev', '')

    # MINDEN OLDALON LÁTHATÓ FELSŐ ÁLLAPOTSÁV (ONLINE + HŐFOK)
    @st.fragment(run_every=2)
    def felso_allapotsav():
        eletjel.mutasd_felso_sav()

    felso_allapotsav()

    if st.session_state.oldal == 'Főmenü':
        st.title(f"📱 Kályha Vezérlő ({aktualis_nev})")

        # Élő Főmenü panel: 5 mp-enként ellenőrzi az új üzeneteket és a tűzrakás időzítőt
        @st.fragment(run_every=5)
        def fomenu_panel():
            osszes_uzenet = db.reference('uzenetek').get() or {}
            olvasatlan_db = 0
            legujabb_nekem = None
            legujabb_ido = 0

            for u_id, u_adat in osszes_uzenet.items():
                if isinstance(u_adat, dict):
                    if u_adat.get('cimzett') == aktualis_nev and not u_adat.get('olvasva', True):
                        olvasatlan_db += 1
                        ido = u_adat.get('timestamp', 0)
                        if ido >= legujabb_ido:
                            legujabb_ido = ido
                            legujabb_nekem = (u_id, u_adat)

            # Csippanás és értesítés, ha új üzenet érkezett
            if legujabb_nekem:
                u_id, u_adat = legujabb_nekem
                if st.session_state.utolso_jelzett_uzenet_id != u_id:
                    st.session_state.utolso_jelzett_uzenet_id = u_id
                    kuldo = u_adat.get('kuldo', 'Valaki')
                    szoveg = u_adat.get('szoveg', '')
                    components.html(
                        f"""
                        <script>
                            try {{
                                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                                function csip(start, freq) {{
                                    const osc = ctx.createOscillator();
                                    const gain = ctx.createGain();
                                    osc.type = 'sine';
                                    osc.frequency.setValueAtTime(freq, ctx.currentTime + start);
                                    gain.gain.setValueAtTime(0.3, ctx.currentTime + start);
                                    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + start + 0.15);
                                    osc.connect(gain);
                                    gain.connect(ctx.destination);
                                    osc.start(ctx.currentTime + start);
                                    osc.stop(ctx.currentTime + start + 0.15);
                                }}
                                csip(0, 880);
                                csip(0.2, 1174);
                            }} catch (e) {{}}
                            window.parent.document.title = "🔔 Új üzenet ({kuldo})! - Kályha App";
                            if ("Notification" in window && Notification.permission === "granted") {{
                                new Notification("🔥 Kályha App - {kuldo}", {{ body: "{szoveg}" }});
                            }}
                        </script>
                        """,
                        height=0,
                    )

            # Tűzrakás időzítő ellenőrzése a gomb feliratához
            tuz_adat = db.reference('tuzrakas').get() or {}
            lejarat_ts = tuz_adat.get('lejarat_ts', 0)
            if lejarat_ts > 0 and int(time.time()) >= lejarat_ts:
                tuz_gomb_felirat = "🔥 Tűzrakás (⚠️ Rá kell tenni!)"
            else:
                tuz_gomb_felirat = "🔥 Tűzrakás"

            # A piros jelzés közvetlenül az Üzenetek gombon jelenik meg
            uzenet_gomb_felirat = f"💬 Üzenetek (🔴 {olvasatlan_db})" if olvasatlan_db > 0 else "💬 Üzenetek"

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🌡️ Hőfok (Huzat)", use_container_width=True):
                    st.session_state.oldal = 'Hőfok'
                    st.rerun()
                if st.button(tuz_gomb_felirat, use_container_width=True):
                    st.session_state.oldal = 'Tűzrakás'
                    st.rerun()
            with col2:
                if st.button("📷 Kamera", use_container_width=True):
                    st.session_state.oldal = 'Kamera'
                    st.rerun()
                if st.button(uzenet_gomb_felirat, use_container_width=True):
                    st.session_state.oldal = 'Üzenetek'
                    st.rerun()

            if st.button("⚙️ Beállítások", use_container_width=True):
                st.session_state.oldal = 'Beállítások'
                st.rerun()

        fomenu_panel()

        st.divider()

        if st.button("🔔 Hang és értesítések bekapcsolása", use_container_width=True):
            components.html(
                """
                <script>
                    if ("Notification" in window) {
                        Notification.requestPermission();
                    }
                    const ctx = new (window.AudioContext || window.webkitAudioContext)();
                    const osc = ctx.createOscillator();
                    osc.connect(ctx.destination);
                    osc.start();
                    osc.stop(ctx.currentTime + 0.1);
                </script>
                """,
                height=0,
            )
            st.success("Értesítések és hang engedélyezve ezen az eszközön!")

        if st.button("Kijelentkezés 🔒", use_container_width=True):
            db.reference(f'bejelentkezett_eszkozok/{aktualis_eszkoz_id}').delete()
            st.session_state.belepve = False
            st.rerun()

        # QR KÓD A KIJELENTKEZÉS ALATT (MINDENKI LÁTJA A FŐMENÜBEN)
        mutasd_qr_kod()

    # ITT HÍVJUK MEG A KÜLSŐ FÁJLOKAT
    elif st.session_state.oldal == 'Hőfok':
        hofok.mutasd()
    elif st.session_state.oldal == 'Kamera':
        kamera.mutasd()
    elif st.session_state.oldal == 'Beállítások':
        beallitasok.mutasd()
    elif st.session_state.oldal == 'Üzenetek':
        uzenetek.mutasd()
    elif st.session_state.oldal == 'Tűzrakás':
        tuzrakas.mutasd()