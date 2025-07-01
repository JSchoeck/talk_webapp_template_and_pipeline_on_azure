"""Configuration settings for a streamlit-based Azure App Service web application.

The module loads environment variables, and settings from the pyproject.toml and settings.yaml files.
It also initialises the session state and the NKD application monitor.
"""

from nkd_utils_lib.nkd_logging import logger
from nkd_utils_lib.nkd_tools.azure import running_on_azure
from nkd_utils_lib.nkd_tools.config_loaders import ENVS, PYPROJECT, SETTINGS  # noqa: F401
from streamlit import session_state as ss

logging = logger.get_logger(__name__)


def init_session_state() -> None:
    """Initialise the session state, including performing cloud specific actions."""
    if "initiated" not in ss:
        if running_on_azure():
            msg = "Running on Azure, initialising session state."
            logging.info(msg)

        ss.save_name = ""
        ss.initiated = True
