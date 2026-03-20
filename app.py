import streamlit as st
import time

from aether_flow_nifty_options import login, run_once, CONFIG

st.set_page_config(page_title="Nifty Options Bot", layout="wide")

st.title("📊 Aether Flow - Nifty Options Dashboard")

# Sidebar credentials
st.sidebar.header("🔐 Login")

CONFIG["api_key"] = st.sidebar.text_input("API Key")
CONFIG["client_code"] = st.sidebar.text_input("Client Code")
CONFIG["password"] = st.sidebar.text_input("Password", type="password")
CONFIG["totp_secret"] = st.sidebar.text_input("TOTP Secret", type="password")

run_button = st.sidebar.button("▶ Run Bot")

# Auto refresh toggle
auto_refresh = st.sidebar.checkbox("Auto Refresh (1 min)")

if run_button or auto_refresh:

    try:
        obj, _, _ = login()

        result = run_once(obj)

        if result:

            st.subheader("📈 Market Overview")

            col1, col2, col3 = st.columns(3)

            col1.metric("Nifty Spot", f"{result['spot']:.2f}")
            col2.metric("ATM Strike", result["atm"])
            col3.metric("Signal", result["signal"] or "WAIT")

            st.subheader("📊 Option Data")

            col1, col2 = st.columns(2)

            with col1:
                st.write("### CE")
                st.json(result["ce"])

            with col2:
                st.write("### PE")
                st.json(result["pe"])

        else:
            st.warning("No data received")

    except Exception as e:
        st.error(f"Error: {e}")

# Auto refresh logic
if auto_refresh:
    time.sleep(60)
    st.rerun()
