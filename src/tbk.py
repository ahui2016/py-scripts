from pathlib import Path
from typing import Any

import click

from scripts import cf_r2, cf_r2_secure, util
from scripts.config import ensure_config_file, get_config
from scripts.tbk_config import config_file, default_config, default_summary
from scripts.util import print_err, print_err_exist


# 初始化
App_Name = "tbk"
VERSION = "2022-11-23"
ensure_config_file(config_file, default_config())

cfg: dict
objects_summary: dict
s3: Any
the_bucket: Any

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.option(
    "info", "-info", "-v", "-V", is_flag=True, help="Show information.")
@click.option(
    "use_proxy", "--use-proxy", help="Set '1' or 'on' or 'true' to use proxy.")
@click.option(
    "size", "--set-size", type=int, help="Set upload size limit (unit: MB).")
@click.option("c", "-c", is_flag=True, help="Count files uploaded.")
@click.option("l", "-l", help="List objects by prefix.")
@click.option("u", "-u", help="Upload a file.")
@click.option("dl", "-dl", help="Download a file.")
@click.option("d", "-del", help="Delete objects by prefix.")
@click.pass_context
def cli(ctx, info, use_proxy, size, c, l, u, dl, d):
    """Temp Backup (secure): 加密并备份文件到 Cloudflare R2

    Example:

    tbk --set-size 25 (设置上传文件体积上限为 25 MB)

    tbk --use-proxy off (不使用代理)

    tbk --use-proxy true (使用代理)

    詳細使用方法看這裡:

    https://github.com/ahui2016/py-scripts/blob/main/docs/README-tbk.md
    """
    global cfg, s3, the_bucket, objects_summary
    cfg = get_config(config_file)

    if info:
        print()
        print(f"[tbk version] {VERSION}\n")
        print(f"[tbk main]\n{__file__}\n")
        print(f"[tbk config]\n{config_file}")
        print("(注意: 请妥善保存 tbk config 文件中的 secret_key, 一旦丢失则无法解密.)\n")
        cf_r2.print_config(App_Name, config_file, cfg)
        print()
        ctx.exit()

    if use_proxy:
        cf_r2.set_use_proxy(use_proxy, cfg, config_file)
    if size:
        cf_r2.set_size_limit(size, config_file, cfg)
    if use_proxy or size:
        ctx.exit()

    s3 = cf_r2.get_s3(cfg)
    the_bucket = cf_r2.get_bucket(s3, cfg)
    objects_summary = cf_r2.get_summary(config_file, cfg, default_summary)

    if c:
        ctx.invoke(count)
        ctx.exit()
    if l:
        ctx.invoke(list_command, prefix=l)
        ctx.exit()
    if u:
        ctx.invoke(upload, file=u)
        ctx.exit()
    if dl:
        ctx.invoke(download, prefix=dl)
        ctx.exit()
    if d:
        ctx.invoke(delete, prefix=d)
        ctx.exit()

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()


"""
以上是主命令
------------
以下是子命令
"""


@cli.command(context_settings=CONTEXT_SETTINGS)
def count():
    """Count files uploaded."""
    cf_r2.print_summary(objects_summary)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("file", type=click.Path(exists=True))
@click.pass_context
def upload(ctx, file):
    """Upload a file.

    加密并上传文件. 注意, 如果云端有同名文件, 同一天内的会直接覆盖,
    非同一天的同名文件会在云端产生不同的文件 (日期前缀不同).

    `tbk upload FILE` 加密并上传文件到云端.

    `tbk upload FOLDER` 加密并上传文件夹内的最新文件
    """
    filepath = Path(file)
    if filepath.is_dir():
        filepath = util.get_new_file(filepath)
        if filepath is None:
            print(f"空文件夹 => {file}\n请指定一个文件, 或一个非空文件夹")
            ctx.exit()
        print(f"找到文件 {filepath}")
        if not click.confirm("要上传该文件吗?", default=True):
            ctx.exit()

    err = cf_r2_secure.upload_file(
        filepath, objects_summary, config_file, cfg, the_bucket)
    print_err(err)


@cli.command(context_settings=CONTEXT_SETTINGS, name="list")
@click.argument("prefix", nargs=1, type=str)
def list_command(prefix):
    """List objects by prefix.

    通过前缀查找云端文件, 例如:

    tbk list 202211 (列出2022年11月的全部文件)

    tbk list 2022   (列出2022年的全部文件)

    tbk list today  (列出今天的全部文件)
    """
    if prefix == "today":
        prefix = cf_r2.today()

    objects = cf_r2.get_objects_by_prefix(prefix, the_bucket)
    i = cf_r2.print_objects_key(objects)
    if i == 0:
        print(f"Not Found: {prefix}")


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("prefix", nargs=1, type=str)
@click.pass_context
def delete(ctx, prefix):
    """Delete objects by prefix.

    删除指定前缀的云端文件(必须包含日期前缀), 例如:

    tbk delete 20221111/abc.txt (删除2022年11月11日名为abc.txt的文件)

    tbk delete 202211           (删除2022年11月的全部文件)
    """
    objects = cf_r2.get_objects_by_prefix(prefix, the_bucket)
    del_list = cf_r2.objects_to_delete(objects)
    length = len(del_list)
    if length == 0:
        print(f"Not Found: {prefix}")
        print("(注意, 必须以日期前缀开头, 并且文件名区分大小写)")
        ctx.exit()

    cf_r2.print_delete_list(del_list)
    click.confirm(f"\nDelete {length} objects? (确认删除云端文件)", abort=True)
    cf_r2.delete_objects(
        del_list, objects_summary, config_file, cfg, the_bucket)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "folder",
    "-dir",
    help="Specify a folder to save the downloaded file.",
)
@click.option(
    "dest",
    "--save-as",
    help="Specify a path to save the downloaded file.",
)
@click.argument("prefix", required=False)
@click.pass_context
def download(ctx, folder, dest, prefix):
    """Download a file.

    下载前可先指定保存文件的文件夹, 例如:

    tbk download -dir /path/to/folder

    只需要设置一次, 后续下载就会一律保存在指定的文件夹,
    若需更换文件夹可重新设置.

    下载指定前缀的云端文件(必须包含日期前缀), 例如:

    tbk download 20221111/abc.txt (下载2022年11月11日名为abc.txt的文件)

    第二种下载方法, 不管文件夹, 直接指定下载到哪个位置, 例如:

    tbk download 20221111/abc.txt --save-as /path/to/cde.txt
    """
    cf_r2.check_download_params(ctx, folder, dest, prefix)
    download_dir_exists(ctx, folder, dest)
    cf_r2.set_download_dir(ctx, folder, config_file, cfg)

    if not prefix:
        print(
            "下载指定前缀的云端文件(必须包含日期前缀), 例如:\n"
            f"tbk download 20221111/abc.txt --save-as {dest}"
        )
        ctx.exit()

    # 正式下载.
    obj, filepath, err = cf_r2.get_obj_filepath(ctx, dest, prefix, the_bucket, cfg)
    if err.find("文件夹不存在") >= 0:
        print_err_exist(ctx, err)

    if err.find("文件已存在") >= 0:
        print(err)
        err = ""
        click.confirm("要覆盖文件吗?", abort=True)

    print_err_exist(ctx, err)
    cf_r2_secure.download_file(
        the_bucket, obj['key'], obj['size'], filepath, cfg)


def download_dir_exists(ctx, folder, dest):
    if err := cf_r2.download_dir_exists(App_Name, cfg):
        if (not folder) and (not dest):
            print_err_exist(ctx, err)


if __name__ == "__main__":
    cli(obj={})
