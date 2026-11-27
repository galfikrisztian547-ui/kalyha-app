import streamlit as st
from firebase_admin import db
import time


def _normalizal_ido(ts):
    try:
        ertek = int(ts)
        # Ha a Firebase ezredmásodpercben (13 számjegy) adta vissza, átváltjuk másodpercre
        if ertek > 10_000_000_000:
            ertek = ertek // 1000
        return ertek
    except Exception:
        return 0


def _allapot_adatok():
    esp_adat = db.reference('esp32_config').get() or {}
    parosito_kod = esp_adat.get('parosito_kod', '')
    utolso_eletjel = _normalizal_ido(esp_adat.get('utolso_eletjel', 0))
    akt_ho = db.reference('aktualis_ho').get()
    return parosito_kod, utolso_eletjel, akt_ho


def mutasd_felso_sav():
    parosito_kod, utolso_eletjel, akt_ho = _allapot_adatok()
    ho_szoveg = f"🌡️ {akt_ho} °C" if akt_ho is not None else "🌡️ -- °C"

    if not parosito_kod:
        st_szin = "#FFC107"
        st_szoveg = "⚪ Nincs párosítva"
    elif utolso_eletjel == 0:
        st_szin = "#FFC107"
        st_szoveg = "🟡 Várakozás..."
    else:
        eltelt_mp = max(0, int(time.time()) - utolso_eletjel)
        if eltelt_mp <= 35:
            st_szin = "#00FF00"
            st_szoveg = "🟢 ONLINE"
        else:
            st_szin = "#FF4B4B"
            st_szoveg = f"🔴 OFFLINE ({eltelt_mp} mp)"

    st.markdown(
        f"""
        <div style="display:flex; justify-content:flex-start; align-items:center; gap:14px;
                    background:#111111; border:1px solid #333333; border-radius:10px;
                    padding:8px 14px; margin-bottom:10px; font-size:16px; font-weight:bold;">
            <span style="color:{st_szin};">{st_szoveg}</span>
            <span style="color:#555555;">|</span>
            <span style="color:#00FF00;">{ho_szoveg}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def mutasd_allapot():
    parosito_kod, utolso_eletjel, _ = _allapot_adatok()

    if not parosito_kod:
        st.warning("⚪ ESP32 Vezérlő: **Nincs párosítva** (Beállítások → Csatlakozás az ESP32-re)")
        return

    if utolso_eletjel == 0:
        st.warning("🟡 ESP32 Vezérlő: **Várakozás a kártyára...**")
        return

    eltelt_mp = max(0, int(time.time()) - utolso_eletjel)

    if eltelt_mp <= 35:
        st.success("🟢 ESP32 Vezérlő: **ONLINE**")
    else:
        st.error(f"🔴 ESP32 Vezérlő: **OFFLINE!** (Utolsó jel: {eltelt_mp} mp-e)")