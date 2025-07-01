from datetime import datetime
from pathlib import Path
from typing import Literal

import toml


def clean_version_string(version: str) -> str:
    REPLACE_CHARS = ["=", "^", "<", ">", "*", "~"]
    for char in REPLACE_CHARS:
        version = version.replace(char, "")
    return version


def set_pipeline_variable(name: str, value: str | None, scope: Literal["internal", "output", "both"] = "both") -> None:
    """Set a pipeline variable.

    Args:
        name (str): Name of the variable.
        value (str): Value of the variable.
        scope (Literal["internal", "output", "both"], optional): Scope of the variable. Defaults to "both" for use in the current and following pipeline jobs.
    """
    print(f"Setting pipeline variable {name} with value {value} with scope {scope}.")
    if scope in ["internal", "both"]:
        print(f"##vso[task.setvariable variable={name}]{value}")
    if scope in ["output", "both"]:
        print(f"##vso[task.setvariable variable={name};isOutput=true]{value}")


def get_var_from_pyproject(var_name: str, path: Path | None = None) -> None:
    if path is None:
        path = Path.cwd().joinpath("pyproject.toml")
    config = toml.load(path)
    if var_name == "pythonVersion":
        var_value = clean_version_string(config["project"]["requires-python"])
    elif var_name == "nkd_utils_lib_version":
        var_value = clean_version_string(config["tool"]["poetry"]["dependencies"]["nkd-utils-lib"]["version"])
    else:
        print(f"Error: Variable {var_name} not found in pyproject.toml file.")
        var_value = None
    set_pipeline_variable(var_name, var_value)


def id_name_split(name: str) -> tuple[str, str]:
    name = name.replace("_", "-")
    parts = name.split("-", 2)
    if len(parts) < 2:
        msg = "Invalid name format. Expected format: 'id-name'."
        raise ValueError(msg)
    # Combine the first two parts for id_part and the rest for name_part
    id_part = "-".join(parts[:2])
    name_part = "-".join(parts[2:]) if len(parts) > 2 else parts[2]
    return id_part, name_part


def get_az_var_from_pyproject(var_name: str, path: Path | None = None) -> None:
    if path is None:
        path = Path.cwd().joinpath("pyproject.toml")
    config = toml.load(path)
    if var_name == "projectId":
        id_part, _ = id_name_split(config["project"]["name"])
        var_value = id_part
    elif var_name == "projectName":
        _, name_part = id_name_split(config["project"]["name"])
        var_value = name_part
    elif var_name == "location":
        var_value = clean_version_string(config["tool"]["nkd"]["location"])
    elif var_name == "pathToApp":
        var_value = clean_version_string(config["tool"]["nkd"]["pathToApp"])
    elif var_name == "existingASPname":
        var_value = clean_version_string(config["tool"]["nkd"]["existingASPname"])
    elif var_name == "appType":
        var_value = clean_version_string(config["tool"]["nkd"]["appType"])
    elif var_name == "blobStorage":
        var_value = config["tool"]["nkd"]["blobStorage"]
        if isinstance(var_value, bool):
            var_value = str(var_value).lower()  # Convert True/False to "true"/"false"
    elif var_name == "sonarCloudQG":
        var_value = config["tool"]["nkd"]["sonarCloudQG"]
        if isinstance(var_value, bool):
            var_value = str(var_value).lower()
    elif var_name == "createKeyvault":
        var_value = config["tool"]["nkd"]["createKeyvault"]
        if isinstance(var_value, bool):
            var_value = str(var_value).lower()
    elif var_name == "runFromPackage":
        var_value = config["tool"]["nkd"]["runFromPackage"]
    else:
        print(f"Error: Variable {var_name} not found in pyproject.toml file.")
        var_value = None
    set_pipeline_variable(var_name, var_value)


def get_all_var_from_pyproject(path: Path | None = None) -> None:
    save_deployment_date()
    az_var_list = [
        "projectId",
        "projectName",
        "location",
        "pathToApp",
        "existingASPname",
        "blobStorage",
        "sonarCloudQG",
        "runFromPackage",
        "appType",
    ]
    var_list = [
        "projectId",
        "projectName",
        "location",
        "pathToApp",
        "existingASPname",
        "blobStorage",
        "sonarCloudQG",
        "runFromPackage",
        "pythonVersion",
        "nkd_utils_lib_version",
        "appType",
    ]
    if path is None:
        path = Path.cwd().joinpath("pyproject.toml")
    for var in var_list:
        if var in az_var_list:
            try:
                get_az_var_from_pyproject(var, path)
            except Exception as e:
                print(f"Warning: Failed to get variable {var} from pyproject.toml. Error: {e}")
        else:
            try:
                get_var_from_pyproject(var, path)
            except Exception as e:
                print(f"Warning: Failed to get variable {var} from pyproject.toml. Error: {e}")


def save_deployment_date() -> None:
    timestamp = datetime.now().date()
    with open("deploy_date.txt", "w") as f:
        f.write(str(timestamp))
    print("Deployment date saved:", timestamp)


def test_installation() -> None:
    import nkd_utils_lib
    from nkd_utils_lib.nkd_logging import logger

    print(f"\n== Loaded module {nkd_utils_lib.__name__!s} from file {nkd_utils_lib.__file__!s}")
    logging = logger.get_logger(__name__)

    print(f"\n== Loaded module {logger.__name__!s} from file {logger.__file__!s}")
    logging.info("Successfully loaded nkd_utils_lib.logger module.")
