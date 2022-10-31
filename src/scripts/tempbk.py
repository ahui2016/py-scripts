"""Temp Backup: 临时备份文件"""

import click

from src.scripts import cf_r2


def print_err(err):
    print(f"Error: {err}")

@click.group()
@click.help_option("-h", "--help")
@click.argument("file", nargs=1, type=click.Path(exists=True))
@click.pass_context
def cli(ctx, file):
    """Temp Backup: 临时备份文件"""

    result, n = cf_r2.get_boto3_cfg()
    if n < 0:
        print_err(result)
    else:
        print(f"OK.\n{result}")
