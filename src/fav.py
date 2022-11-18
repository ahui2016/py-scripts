import click

from scripts.config import app_config_dir


# 初始化
VERSION = "2022-11-18"
Config_Filename = "fav_config.txt"

cfg_file_path = app_config_dir.joinpath(Config_Filename)
default_config = [str(cfg_file_path)]


def ensure_config_file(default_cfg:list):
    app_config_dir.mkdir(parents=True, exist_ok=True)
    if not cfg_file_path.exists():
        write_config(default_cfg)


def write_config(cfg:list):
    data = "\n".join(cfg)
    cfg_file_path.write_text(data, encoding="utf-8")


def get_config() -> list:
    data = cfg_file_path.read_text(encoding="utf-8")
    return data.split("\n")


def print_config(cfg:list):
    i = 1
    for line in cfg:
        print(f"{i}. {line}")
        i += 1


ensure_config_file(default_config)
fav_list: list

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command()
@click.help_option("-h", "--help")
@click.pass_context
def cli(ctx):
    """Fav: 一句话收藏夹, 主要用于收藏文件/文件夹路径

    詳細使用方法看這裡:

    https://github.com/ahui2016/py-scripts/blob/main/docs/README-fav.md
    """
    global fav_list
    fav_list = get_config()

    print()
    print_config(fav_list)
    print()
    print("输入命令 'fav -h' 可查看使用说明.")


if __name__ == "__main__":
    cli(obj={})
