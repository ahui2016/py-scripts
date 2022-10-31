import boto3

from . import util, config

"""
參考:
https://developers.cloudflare.com/r2/examples/boto3/
"""

Boto3_Config_File = "boto3_config_file"

"""
【关于返回值】
本项目的返回值经常采用 (result, err_code) 的形式,
err_code 是 int, 小于零表示有错误, 大于等于零表示没有错误.
当 err_code 小于零时, result 的类型是 str, 内容是关于错误的说明.
当 err_code 大于等于零时, result 就是有效的数据.
"""

Err1 = f"请打开 {config.app_config_file} 填写 Boto3_Config_File, 例:\n"
Err2 = """
Boto3_Config_File = '''/path/to/boto3-config.toml'''

然后自行创建 boto3-config.toml 文件(采用 utf-8 编码), 内容如下:

endpoint_url = 'https://<accountid>.r2.cloudflarestorage.com',
aws_access_key_id = '<access_key_id>',
aws_secret_access_key = '<access_key_secret>'

其中 <accountid> 等尖括号的位置要填写正确的值.
"""
Err_Need_Config = Err1 + Err2


def get_boto3_cfg():
    """:return: (result, err_code)"""
    app_cfg = config.get_config()
    if Boto3_Config_File not in app_cfg:
        return Err_Need_Config, -1

    boto3_cfg = util.tomli_load(app_cfg[Boto3_Config_File])
    if "endpoint_url" not in boto3_cfg \
            or "aws_access_key_id" not in boto3_cfg \
            or "aws_secret_access_key" not in boto3_cfg:
        return Err_Need_Config, -1

    return boto3_cfg, 1
