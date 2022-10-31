"""Temp Backup: 临时备份文件"""

import click


@click.group()
@click.help_option("-h", "--help")
@click.option(
    "safe", "-s", "--safe-mode", is_flag=True, help="Safe mode: do not load recipes."
)
def cli(safe):
    """ffe: File/Folder Extensible manipulator (可扩展的文件操作工具)

    https://pypi.org/project/ffe/
    """
    if not safe:
        init_recipes(__recipes_folder__)
