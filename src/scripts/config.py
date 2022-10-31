from pathlib import Path
from appdirs import AppDirs
import tomli_w

from src.scripts import util

Config_Filename = "py-scripts-config.toml"

app_dirs = AppDirs("py-scripts", "github-ahui2016")
app_config_dir = Path(app_dirs.user_config_dir)
app_config_file = app_config_dir.joinpath(Config_Filename)


def default_config():
    return dict(http_proxy="", use_proxy=True)


def ensure_config_file() -> None:
    app_config_dir.mkdir(parents=True, exist_ok=True)
    if not app_config_file.exists():
        with open(app_config_file, "wb") as f:
            tomli_w.dump(default_config(), f)


def get_config():
    return util.tomli_load(app_config_file)


def get_proxies():
    cfg = get_config()
    proxies = None
    if cfg["use_proxy"] and cfg["http_proxy"]:
        proxies = dict(
            http=cfg["http_proxy"],
            https=cfg["http_proxy"],
        )
    return proxies
