from pathlib import Path
from typing import Any

import click

from scripts import config, cf_r2


# 初始化
config.ensure_config_file()
cf_r2.ensure_config_file()

App_Config = config.get_config()
boto3_cfg: dict
s3: Any
s3_client: Any
the_bucket: Any

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def print_err(err):
    print(f"Error: {err}")


@click.group()
@click.help_option("-h", "--help")
@click.pass_context
def cli(ctx):
    """Temp Backup: 临时备份文件"""
    global boto3_cfg, s3, s3_client, the_bucket
    boto3_cfg = cf_r2.get_boto3_cfg()
    s3 = cf_r2.get_s3(boto3_cfg)
    s3_client = cf_r2.get_s3_client(boto3_cfg)
    the_bucket = cf_r2.get_bucket(s3, boto3_cfg)


# 以上是主命令
############
# 以下是子命令


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def info(ctx):
    """Show information."""
    print()
    print(f"[tempbk]\n{__file__}\n")
    print(f"[tempbk config]\n{config.app_config_file}\n")
    print(f"[boto3 config]\n{cf_r2.boto3_config_file}\n")
    dl_dir = boto3_cfg.get(cf_r2.Download_Dir, "")
    if not dl_dir:
        dl_dir = "(未设置下载文件夹, 设置方法请查看帮助: tempbk download -h)"
    print(f"[download dir]\n{dl_dir}\n")


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def count(ctx):
    """Count files uploaded."""
    objects_summary = cf_r2.get_summary(the_bucket)
    # objects_summary 会发生网络请求, 因此不能放在程序初始化里.
    print(objects_summary)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("file", nargs=1, type=click.Path(exists=True))
@click.pass_context
def upload(ctx, file):
    """Upload a file.

    上传文件. 注意, 如果云端有同名文件, 同一天内的会直接覆盖,
    非同一天的同名文件会在云端产生不同的文件 (日期前缀不同).
    """
    objects_summary = cf_r2.get_summary(the_bucket)
    # objects_summary 会发生网络请求, 因此不能放在程序初始化里.
    cf_r2.upload_file(Path(file), objects_summary, the_bucket)


@cli.command(context_settings=CONTEXT_SETTINGS, name="list")
@click.argument("prefix", nargs=1, type=str)
@click.pass_context
def list_command(ctx, prefix):
    """List objects by prefix.

    通过前缀查找云端文件, 例如:

    tempbk list 202211 (列出2022年11月的全部文件)

    tempbk list 2022   (列出2022年的全部文件)

    tempbk list today  (列出今天的全部文件)
    """
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

    tempbk delete 20221111/abc.txt (删除2022年11月11日名为abc.txt的文件)

    tempbk delete 202211           (删除2022年11月的全部文件)
    """
    objects = cf_r2.get_objects_by_prefix(prefix, the_bucket)
    obj_del_list = cf_r2.objects_to_delete(objects)
    length = len(obj_del_list)
    if length == 0:
        print(f"Not Found: {prefix}")
        print("(注意, 必须以日期前缀开头, 并且文件名区分大小写)")
        ctx.exit()

    cf_r2.print_objects_key(objects)
    click.confirm(f"\nDelete {length} objects? (确认删除云端文件)", abort=True)
    objects_summary = cf_r2.get_summary(the_bucket)
    cf_r2.delete_objects(obj_del_list, objects_summary, the_bucket)


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

    tempbk download -dir /path/to/folder

    只需要设置一次, 后续下载就会一律保存在指定的文件夹,
    若需更换文件夹可重新设置.

    下载指定前缀的云端文件(必须包含日期前缀), 例如:

    tempbk download 20221111/abc.txt (下载2022年11月11日名为abc.txt的文件)

    第二种下载方法, 不管文件夹, 直接指定下载到哪个位置, 例如:

    tempbk download 20221111/abc.txt --save-as /path/to/cde.txt
    """
    if err := cf_r2.check_download_dir(boto3_cfg):
        if (not folder) and (not dest):
            print_err(err)
            ctx.exit()

    if (not folder) and (not dest) and (not prefix):
        print(
            "下载指定前缀的云端文件(必须包含日期前缀), 例如:\n"
            "tempbk download 20221111/abc.txt"
        )
        ctx.exit()

    if folder:
        folder = Path(folder).resolve()
        if folder.is_file():
            print_err(
                f'"{folder}" 是文件\n'
                "使用 -dir 参数时, 请指定一个文件夹"
            )
            ctx.exit()

        if not folder.exists():
            print_err(f"文件夹不存在: {folder}")
            ctx.exit()

        cf_r2.set_download_dir(str(folder), boto3_cfg)
    else:
        folder = cf_r2.get_download_dir(boto3_cfg)

    if not dest:
        dest = None
    else:
        dest = Path(dest)
        if dest.is_dir():
            print_err(
                f'"{dest}" 是文件夹\n'
                "使用 --save-as 参数时, 请指定一个文件名"
            )
            ctx.exit()

    if prefix:
        objects = cf_r2.get_objects_by_prefix(prefix, the_bucket)
        obj_list = cf_r2.objects_to_list(objects)
        length = len(obj_list)
        if length == 0:
            print(f"Not Found: {prefix}")
            print("(注意, 必须以日期前缀开头, 并且文件名区分大小写)")
            ctx.exit()
        if length > 1:
            print("每次只能下载一个文件:\n")
            cf_r2.print_objects_with_size(obj_list)
            ctx.exit()

        obj = obj_list[0]
        filepath, err = cf_r2.get_download_filepath(obj['key'], folder, dest)
        if err.find("文件夹不存在") >= 0:
            print_err(err)
            ctx.exit()

        if err.find("文件已存在") >= 0:
            print(err)
            click.confirm("要覆盖文件吗?", abort=True)
            err = ""

        if not err:
            cf_r2.download_file(the_bucket, obj['key'], obj['size'], filepath)


if __name__ == "__main__":
    cli(obj={})
