import streamlit as st
from nkd_utils_lib.nkd_ui.ui_elements import streamlit_page_setup

streamlit_page_setup(multipage=True)
with st.sidebar:
    st.page_link("app.py", label="Back to main app")


st.write("This is a separate page. It shares the session state with all other pages and the main app from app.py.")

st.write("To build a mutlipage app, add navigation elements using st.page_link:")
st.write("https://docs.streamlit.io/develop/tutorials/multipage/st.page_link-nav")

st.write(
    "Alternatively, enable showSidebarNavigation in .streamlit/config.toml to get the default sidebar navigation menu."
)
