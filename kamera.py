import streamlit as st

def mutasd():
    st.title("📷 Kályha Kamera")
    if st.button("🔙 Vissza"):
        st.session_state.oldal = 'Főmenü'
        st.rerun()
    st.divider()
    st.info("Ide kötjük be majd az ESP32-CAM képét!")