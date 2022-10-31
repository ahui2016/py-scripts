import click

from scripts import config, cf_r2

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def print_err(err):
    print(f"Error: {err}")

@click.group()
@click.help_option("-h", "--help")
@click.pass_context
def cli(ctx):
    """Temp Backup: 临时备份文件"""
    pass


# 以上是主命令
############
# 以下是子命令


@cli.command(context_settings=CONTEXT_SETTINGS)
# @click.argument("file", nargs=1, type=click.Path(exists=True))
@click.pass_context
def info(ctx):
    """Get information."""

    result, n = cf_r2.get_boto3_cfg()
    if n < 0:
        print_err("尚未完成配置\n" + result)
    else:
        print(f"OK.\n{result}")


# 初始化
config.ensure_config_file()

if __name__ == "__main__":
    cli(obj={})
