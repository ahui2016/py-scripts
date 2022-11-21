import click

from scripts.config import app_config_dir
from scripts.util import print_err, print_err_exist, clip_copy

# 初始化
VERSION = "2022-11-22"
Config_Filename = "fav_config.txt"
Empty_Slot = ""

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


@click.command()
@click.help_option("-h", "--help")
@click.argument("n", type=int, required=False)
@click.option("-info", is_flag=True, help="Show information.")
@click.option("-add", help="Add an item to the list.")
@click.option("d", "-del", type=int, help="Delete an item form the list.")
@click.pass_context
def cli(ctx, n, info, add, d):
    """Fav: 一句话收藏夹, 主要用于收藏文件/文件夹路径

    詳細使用方法看這裡:

    https://github.com/ahui2016/py-scripts/blob/main/docs/README-fav.md
    """
    fav_list = get_config()

    if n is not None:
        item, err = get_item(n-1, fav_list)
        print_err_exist(ctx, err)
        print(item, end='')
        clip_copy(item)
        ctx.exit()
    if info:
        print()
        print(f"[Fav version] {VERSION}\n")
        print(f"[Fav main]\n{__file__}\n")
        print(f"[Fav list]\n{cfg_file_path}\n")
        ctx.exit()
    if add:
        i = add_item(add, fav_list)
        print(f"{i+1}. {fav_list[i]}")
        ctx.exit()
    if d is not None:
        err = del_fav(d-1, fav_list)
        print_err(err)
        ctx.exit()

    print()
    print_config(fav_list)
    print()


def check_fav_n(n:int, cfg):
    """参数 n 从 0 开始计数, n 等于用户输入数字减一.
    有错误时返回错误内容, 如果返回空字符串则表示没有错误.
    """
    if n < 0:
        return f"n 不可小于等于零."

    length = len(cfg)
    if n + 1 > length:
        return f"'{n+1}' 超过列表长度({length})"

    return ""


def add_item(item:str, cfg:list) -> int:
    """添加一行数据到列表中, 并返回其位置."""
    if Empty_Slot in cfg:
        i = cfg.index(Empty_Slot)
        cfg[i] = item
    else:
        cfg.append(item)
        i = len(cfg) - 1

    write_config(cfg)
    return i


def get_item(n, cfg) -> (str|None, str):
    """参数 n 从 0 开始计数, n 等于用户输入数字减一.

    Return (result, err)"""
    if err := check_fav_n(n, cfg):
        return None, err

    return cfg[n], ""


def del_fav(n:int, cfg:list):
    """参数 n 从 0 开始计数, n 等于用户输入数字减一.
    有错误时返回错误内容, 如果返回空字符串则表示没有错误.
    """
    if err := check_fav_n(n, cfg):
        return err

    item = cfg[n]
    cfg[n] = ""
    write_config(cfg)
    print(f"已删除 {n+1}. {item}")
    return ""


if __name__ == "__main__":
    cli(obj={})
