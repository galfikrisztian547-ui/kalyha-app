import streamlit as st
from firebase_admin import db
import time


def mutasd_allapot():
    adatok = db.reference('/').get() or {}
    akt_ho = adatok.get('aktualis_ho', None)
    esp_ts = adatok.get('utolso_frissites', 0)  # Ha az ESP32 küld időbélyeget

    most = int(time.time())
    allapot_ref = db.reference('rendszer_eletjel')
    mentett = allapot_ref.get() or {}

    # Ha az ESP32 nem küld időbélyeget, a hőfok változása alapján követjük az életjelet
    utolso_ho = mentett.get('utolso_ho', None)
    utolso_latva = mentett.get('utolso_latva', 0)

    if esp_ts and esp_ts > 1700000000:
        utolso_latva = int(esp_ts)
    elif akt_ho is not None and akt_ho != utolso_ho:
        utolso_latva = most
        allapot_ref.update({'utolso_ho': akt_ho, 'utolso_latva': most})

    if utolso_latva == 0:
        st.info("⚪ ESP32 Vezérlő: Várakozás az első adatra...")
        return

    eltelt_mp = most - utolso_latva

    if eltelt_mp <= 120:
        st.success(f"🟢 ESP32 Vezérlő: **ONLINE** (Vízhőfok: {akt_ho} °C)")
    elif eltelt_mp <= 600:
        st.warning(f"🟡 ESP32 Vezérlő: **Nincs új változás {eltelt_mp // 60} perce** (Vízhőfok: {akt_ho} °C)")
    else:
        st.error(f"🔴 ESP32 Vezérlő: **OFFLINE!** (Utolsó adat: {eltelt_mp // 60} perce)")