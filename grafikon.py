import streamlit as st
from firebase_admin import db
from datetime import datetime
import time


def rogzit_es_rajzol(aktualis_ho):
    st.write("---")
    st.subheader("📈 Napi vízhőfok grafikon")

    naplo_ref = db.reference('hofok_naplo')
    naplo = naplo_ref.get() or {}

    most_ts = int(time.time())
    ido_str = datetime.now().strftime("%H:%M")

    # Ellenőrizzük, mikor volt az utolsó mentés (5 percenként = 300 mp mentünk új pontot)
    utolso_ts = 0
    if naplo:
        utolso_elem = list(naplo.values())[-1]
        utolso_ts = utolso_elem.get('ts', 0)

    if aktualis_ho is not None and (most_ts - utolso_ts) >= 300:
        naplo_ref.push({
            'ts': most_ts,
            'ido': ido_str,
            'ho': float(aktualis_ho)
        })
        # Csak az utolsó 288 mérést (24 óra) tartjuk meg, hogy ne teljen meg az adatbázis
        if len(naplo) > 288:
            legregebbi_kulcs = list(naplo.keys())[0]
            naplo_ref.child(legregebbi_kulcs).delete()
        naplo = naplo_ref.get() or {}

    if not naplo:
        st.info("Még gyűlnek az adatok a grafikonhoz...")
        return

    # Adatok előkészítése a vonaldiagramhoz
    adat_lista = []
    for elem in naplo.values():
        if isinstance(elem, dict) and 'ido' in elem and 'ho' in elem:
            adat_lista.append({"Idő": elem['ido'], "Vízhőfok (°C)": elem['ho']})

    if adat_lista:
        st.line_chart(adat_lista, x="Idő", y="Vízhőfok (°C)", color="#00FF00")
        min_ho = min(d["Vízhőfok (°C)"] for d in adat_lista)
        max_ho = max(d["Vízhőfok (°C)"] for d in adat_lista)
        st.caption(f"Elmúlt 24 óra – Minimum: **{min_ho} °C** | Maximum: **{max_ho} °C**")