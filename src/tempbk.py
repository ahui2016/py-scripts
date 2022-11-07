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
files_summary: dict

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def print_err(err):
    print(f"Error: {err}")


@click.group()
@click.help_option("-h", "--help")
@click.pass_context
def cli(ctx):
    """Temp Backup: 临时备份文件"""
    global boto3_cfg, s3, s3_client, the_bucket, files_summary
    boto3_cfg = cf_r2.get_boto3_cfg()
    s3 = cf_r2.get_s3(boto3_cfg)
    s3_client = cf_r2.get_s3_client(boto3_cfg)
    the_bucket = cf_r2.get_bucket(s3, boto3_cfg)
    files_summary = cf_r2.get_files_summary(the_bucket)
    print()


# 以上是主命令
############
# 以下是子命令


@cli.command(context_settings=CONTEXT_SETTINGS)
# @click.argument("file", nargs=1, type=click.Path(exists=True))
@click.pass_context
def info(ctx):
    """Show information."""
    print(f"[tempbk]\n{__file__}\n")
    print(f"[tempbk config]\n{config.app_config_file}\n")
    print(f"[boto3 config]\n{cf_r2.boto3_config_file}\n")


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def count(ctx):
    """Count files uploaded."""
    print(files_summary)
    print()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("file", nargs=1, type=click.Path(exists=True))
@click.pass_context
def upload(ctx, file):
    """Upload a file."""
    cf_r2.upload_file(Path(file), files_summary, the_bucket)
    print()


@cli.command(context_settings=CONTEXT_SETTINGS, name="list")
@click.argument("prefix", nargs=1, type=str)
@click.pass_context
def list_command(ctx, prefix):
    """List files by prefix.

    通过前缀查找文件, 例如:

    tempbk list 202211 (列出2022年11月的全部文件)

    tempbk list 2022   (列出2022年的全部文件)

    tempbk list today  (列出今天的全部文件)
    """
    files = cf_r2.get_file_list(prefix, the_bucket)
    i = cf_r2.print_file_list(files)
    if i == 0:
        print(f"Not Found: {prefix}")
    print()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("prefix", nargs=1, type=str)
@click.pass_context
def delete(ctx, prefix):
    """Delete files by prefix.

    删除指定前缀的云端文件(必须包含日期前缀), 例如:

    tempbk delete 20221111/abc.txt (删除2022年11月11日名为abc.txt的文件)

    tempbk delete 202211           (删除2022年11月的全部文件)
    """
    files = cf_r2.get_file_list(prefix, the_bucket)
    objects = cf_r2.get_object_list(files)
    length = len(objects)
    if length == 0:
        print(f"Not Found: {prefix}")
        print("(注意, 必须以日期前缀开头, 并且文件名区分大小写)")
        ctx.exit()

    cf_r2.print_file_list(files)
    click.confirm(f"\nDelete {length} files? (确认删除云端文件)", abort=True)
    cf_r2.delete_objects(objects, files_summary, the_bucket)
    print()


if __name__ == "__main__":
    cli(obj={})
