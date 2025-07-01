from streamlit import session_state as ss

if "initiated" not in ss:
    ss.submit_get_data = False
