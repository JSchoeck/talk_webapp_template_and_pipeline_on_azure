# Templatlinkkkr streamlit web app
# Can be run locally or deployed as Azure App Service with an Azure DevOps pipeline

from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st
from nkd_utils_lib.nkd_logging import logger
from nkd_utils_lib.nkd_tools.azure import load_data_from_blob, store_data_in_blob
from nkd_utils_lib.nkd_ui.ui_elements import add_userguide, streamlit_page_setup
from streamlit import session_state as ss

import config as cfg
from ui import ui

logging = logger.get_logger(__name__)


def main() -> None:
    streamlit_page_setup(page_title="NKD Template Web App", userguide=Path("README.md"))
    add_userguide(Path("README.md"))
    cfg.init_session_state()
    st.title("NKD template streamlit web app")

    st.write("This is a template for a streamlit web app.")  # TODO: do some live changes here

    st.image("./img/nue_digital.png", caption="Nürnberg Digital Festival 2025", use_container_width=False)
    st.link_button(
        "🔗 Template-based Web App and Deployment Pipeline on Azure in an enterprise environment",
        "https://nuernberg.digital/en/events/2025/template-based-web-app-and-deployment-pipeline-at-an-enterprise-ready-level-on-azure",
    )
    st.image(
        "./img/qr_code.png",
        caption="[💻 GitHub repository](https://github.com/JSchoeck/talk_webapp_template_and_pipeline_on_azure)",
        use_container_width=False,
    )

    with st.sidebar:
        operation_mode = st.radio("Select operation mode", ["Excel", "Database", "Blob"])
        st.page_link("pages/multipage1.py", label="(How to use multiple pages)")

    match operation_mode:
        case "Excel":
            ss.data = ui.upload_excel_with_stores()
            stores = ui.select_store_from_dataframe(ss.data) if ss.data is not None else None
        case "Database":
            ui.database_selection()
        case "Blob":
            ss.blob_name = st.text_input("Blob name", "storage.feather")
            # ss.data = None
            if st.button("Load"):
                ss.data = load_data_from_blob(ss.blob_name)
                st.write(f"Loaded: {ss.blob_name!s}")
        case _:
            msg = f"Invalid operation mode: {operation_mode!s}"
            logging.error(msg)
            raise NotImplementedError(msg)

    if ss.data is not None:
        st.write(ss.data)
        ss.save_name = st.text_input("Save as", "storage.feather")

    if ss.save_name and st.button("Save to blob storage"):
        save_to_blob(operation_mode)

        ss.submit_save = False
    if ss.data is not None:
        if isinstance(ss.data, pd.DataFrame):
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                ss.data.to_excel(writer)

            # Get the Excel file in bytes
            excel_bytes = output.getvalue()
            st.download_button("Download Excel report", data=excel_bytes, file_name="report.xlsx")
        elif isinstance(ss.data, bytes):
            st.download_button("Download Excel report", data=ss.data, file_name="report.xlsx")


def save_to_blob(operation_mode: str | None) -> None:
    try:
        ss.blob_name = store_data_in_blob(ss.data, ss.save_name)
        st.success(f"Saved: {ss.blob_name!s}")
    except Exception:
        st.error("Failed to save data:")
        logging.exception("Failed to save data")


if __name__ == "__main__":
    main()
