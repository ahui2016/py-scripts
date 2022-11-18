from pathlib import Path
from appdirs import AppDirs
import tomli_w

from . import util

Config_Filename = "py-scripts-config.toml"

app_dirs = AppDirs("py-scripts", "github-ahui2016")
app_config_dir = Path(app_dirs.user_config_dir)
app_config_file = app_config_dir.joinpath(Config_Filename)


def ensure_config_file(cfg_file, default_cfg) -> None:
    app_config_dir.mkdir(parents=True, exist_ok=True)
    if not cfg_file.exists():
        write_config(cfg_file, default_cfg)


def write_config(cfg_file, cfg):
    with open(cfg_file, "wb") as f:
        tomli_w.dump(cfg, f)


def get_config(cfg_file):
    return util.tomli_load(cfg_file)


def default_config():
    return dict(http_proxy="", use_proxy=True)


def get_proxies(cfg):
    proxies = None
    if cfg["use_proxy"] and cfg["http_proxy"]:
        proxies = dict(
            http=cfg["http_proxy"],
            https=cfg["http_proxy"],
        )
    return proxies
