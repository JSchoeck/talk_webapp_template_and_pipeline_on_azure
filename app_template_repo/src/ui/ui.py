from datetime import date, timedelta

import pandas as pd
import streamlit as st
from nkd_utils_lib.nkd_database.db_data import get_sales, get_store_master_data
from nkd_utils_lib.nkd_ui.ui_elements import store_no_list
from sqlalchemy.exc import OperationalError
from streamlit import session_state as ss


def select_store_from_dataframe(data: pd.DataFrame, column_label: str = "store_no") -> int | None:
    stores = data[column_label].unique()

    # try to convert data[column_label] to integer, if it fails show a streamlit error
    try:
        stores = [int(store) for store in stores]
    except ValueError:
        st.error(f"Column '{column_label}' contains non-integer values. Please check the data.")
        return None
    else:
        return st.selectbox("Select a store", stores)


def select_store_from_dwh(input_text: bool = False, multiselect: bool = False) -> list[int] | int | None:
    if input_text:
        stores, _ = store_no_list()
        return stores
    else:
        smd = get_store_master_data()
        stores = smd["store_no"].unique()
        if multiselect:
            return st.multiselect("Select store(s)", stores)
        else:
            return st.selectbox("Select a store", stores)


def upload_excel_with_stores() -> pd.DataFrame | None:
    uploaded_file = st.file_uploader("Upload a file", type=["xlsx", "xls"])
    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file)
        return data
    else:
        return None


def database_selection() -> tuple[list[int] | int | None, pd.DataFrame | None]:
    input_text = st.toggle("Input stores as text")
    try:
        with st.form("Select stores to get their sales"):
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start date", date.today() - timedelta(days=30))
            with col2:
                end_date = st.date_input("End date")
                stores = select_store_from_dwh(input_text, True)
                agg_date = st.selectbox("Aggregate by:", ["day", "week", "month", "year"])
            if st.form_submit_button("Get sales"):
                with st.spinner("Getting sales data from the database"):
                    ss.data = get_sales(
                        start_date,  # type: ignore
                        end_date,  # type: ignore
                        store_nos=stores,  # type: ignore
                        date_agg=agg_date,  # type: ignore
                    )
                return None, None
            else:
                return None, None
    except OperationalError:
        st.error("Failed to connect to the database. Make sure you are on-site or connected via VPN.")
        return None, None
