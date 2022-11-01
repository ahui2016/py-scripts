import os
import sys
import threading

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

Err1 = f"请打开 {config.app_config_file} 填写 boto3_config_file, 例:\n"
Err2 = """
boto3_config_file = '''/path/to/boto3-config.toml'''

然后自行新建 boto3-config.toml 文件(采用 utf-8 编码), 内容如下:

endpoint_url = 'https://<accountid>.r2.cloudflarestorage.com'
aws_access_key_id = '<access_key_id>'
aws_secret_access_key = '<access_key_secret>'
bucket = '<bucket_name>'

其中 <accountid> 等尖括号的位置要填写正确的值.
"""
Err_Need_Config = Err1 + Err2


def get_boto3_cfg(app_cfg):
    """:return: (result, err_code)"""
    if Boto3_Config_File not in app_cfg:
        return Err_Need_Config, -1

    boto3_cfg = util.tomli_load(app_cfg[Boto3_Config_File])
    if "endpoint_url" not in boto3_cfg \
            or "aws_access_key_id" not in boto3_cfg \
            or "aws_secret_access_key" not in boto3_cfg \
            or "bucket" not in boto3_cfg:
        return Err_Need_Config, -1

    return boto3_cfg, 1


def get_s3(boto3_cfg):
    return boto3.resource(
        's3',
        endpoint_url = boto3_cfg["endpoint_url"],
        aws_access_key_id = boto3_cfg["aws_access_key_id"],
        aws_secret_access_key = boto3_cfg["aws_secret_access_key"]
    )


# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()
