import click

from scripts import config, cf_r2


# 初始化
config.ensure_config_file()
App_Config = config.get_config()
boto3_cfg = None

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def print_err(err):
    print(f"Error: {err}")


def get_boto3_cfg(ctx):
    result, n = cf_r2.get_boto3_cfg(App_Config)
    if n < 0:
        print_err("尚未完成配置\n" + result)
        ctx.exit()
    return result


@click.group()
@click.help_option("-h", "--help")
@click.pass_context
def cli(ctx):
    """Temp Backup: 临时备份文件"""
    global boto3_cfg
    boto3_cfg = get_boto3_cfg(ctx)


# 以上是主命令
############
# 以下是子命令


@cli.command(context_settings=CONTEXT_SETTINGS)
# @click.argument("file", nargs=1, type=click.Path(exists=True))
@click.pass_context
def info(ctx):
    """Get information."""
    print(f"[tempbk config]\n{config.app_config_file}")
    print(f"[boto3 config]\n{App_Config[cf_r2.Boto3_Config_File]}")
    print(boto3_cfg)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def buckets(ctx):
    """Get buckets."""
    s3 = cf_r2.get_s3(boto3_cfg)
    print('Buckets:')
    for bucket in s3.buckets.all():
        print(' - ', bucket.name)


if __name__ == "__main__":
    cli(obj={})
