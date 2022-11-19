import sys

import tomli

"""
【关于返回值】
本项目的返回值有时采用 (result, err) 的形式,
err 是 str, 有内容表示有错误, 空字符串表示没错误.
"""


def tomli_load(file) -> dict:
    """正确处理 utf-16"""
    with open(file, "rb") as f:
        text = f.read()
        try:
            text = text.decode()  # Default encoding is 'utf-8'.
        except UnicodeDecodeError:
            text = text.decode("utf-16").encode().decode()
        return tomli.loads(text)


def print_err(err):
    """如果有错误就打印, 没错误就忽略."""
    if err:
        print(f"Error: {err}", file=sys.stderr)


def print_err_exist(ctx, err):
    """若有错误则打印并结束程序, 无错误则忽略."""
    if err:
        print(f"Error: {err}", file=sys.stderr)
        ctx.exit()


def get_new_file(folder):
    """获取指定文件夹中的一个最新文件 (按修改时间排序)

    :return: 如果是文件夹, 则返回 None
    """
    files = folder.glob("*")
    files = [x for x in files if x.is_file()]
    if len(files) == 0:
        return None
    files.sort(key=lambda x: x.lstat().st_mtime, reverse=True)
    return files[0]
