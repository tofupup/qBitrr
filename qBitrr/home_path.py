import pathlib

from jaraco.docker import is_docker

from qBitrr.env_config import ENVIRO_CONFIG

if (
    ENVIRO_CONFIG.overrides.data_path is None
    or not (p := pathlib.Path(ENVIRO_CONFIG.overrides.data_path)).exists()
):
    if is_docker():
        ON_DOCKER = True
        HOME_PATH = pathlib.Path("/config")
        HOME_PATH.mkdir(parents=True, exist_ok=True)
    else:
        ON_DOCKER = False
        HOME_PATH = pathlib.Path().home().joinpath(pathlib.Path("/qBitrr"))
else:
    HOME_PATH = p

APPDATA_FOLDER = HOME_PATH.joinpath("qBitManager")
APPDATA_FOLDER.mkdir(parents=True, exist_ok=True)
