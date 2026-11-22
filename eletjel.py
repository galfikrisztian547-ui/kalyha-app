import streamlit as st
from firebase_admin import db
import time


def mutasd_allapot():
    esp_adat = db.reference('esp32_config').get() or {}
    parosito_kod = esp_adat.get('parosito_kod', '')
    utolso_eletjel = esp_adat.get('utolso_eletjel', 0)

    if not parosito_kod:
        st.warning("⚪ ESP32 Vezérlő: **Nincs párosítva** (Beállítások → Csatlakozás az ESP32-re)")
        return

    if not utolso_eletjel or int(utolso_eletjel) == 0:
        st.warning("🟡 ESP32 Vezérlő: **Várakozás a kártyára...**")
        return

    most = int(time.time())
    eltelt_mp = most - int(utolso_eletjel)

    if eltelt_mp <= 20:
        st.success("🟢 ESP32 Vezérlő: **ONLINE**")
    else:
        st.error(f"🔴 ESP32 Vezérlő: **OFFLINE!** (Utolsó jel: {eltelt_mp} mp-e)")