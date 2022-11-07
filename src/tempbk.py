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
    print(boto3_cfg)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def count(ctx):
    """Count files uploaded."""
    print('Buckets:')
    for bucket in s3.buckets.all():
        print(' - ', bucket.name)

    print(files_summary)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("file", nargs=1, type=click.Path(exists=True))
@click.pass_context
def upload(ctx, file):
    """Upload a file."""
    cf_r2.upload_file(Path(file), files_summary, the_bucket)


@cli.command(context_settings=CONTEXT_SETTINGS, name="list")
@click.argument("prefix", nargs=1, type=str)
@click.pass_context
def list_command(ctx, prefix):
    """List files by prefix."""
    files = cf_r2.get_file_list(prefix, the_bucket)
    cf_r2.print_file_list(files)


if __name__ == "__main__":
    cli(obj={})
