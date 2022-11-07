import io
import os
import sys
import threading
from pathlib import Path

import boto3
import msgpack
import tomli_w
import arrow
from botocore.exceptions import ClientError


from . import util, config

"""
參考:
https://developers.cloudflare.com/r2/examples/boto3/
"""

"""
【关于返回值】
本项目的返回值经常采用 (result, err_code) 的形式,
err_code 是 int, 小于零表示有错误, 大于等于零表示没有错误.
当 err_code 小于零时, result 的类型是 str, 内容是关于错误的说明.
当 err_code 大于等于零时, result 就是有效的数据.
"""

Files_Summary_Name = "files-summary.msgp"
"""
dict[str, int]  # 日期(年月)与文件数量 '202201': 5
"""
default_summary = {}

Boto3_Config_Filename = "boto3_config.toml"
boto3_config_file = config.app_config_dir.joinpath(Boto3_Config_Filename)

def default_config():
    return dict(
        endpoint_url          ='https://<accountid>.r2.cloudflarestorage.com',
        aws_access_key_id     = '<access_key_id>',
        aws_secret_access_key = '<access_key_secret>',
        bucket_name           = '<bucket_name>'
    )


def ensure_config_file() -> None:
    if not boto3_config_file.exists():
        with open(boto3_config_file, "wb") as f:
            tomli_w.dump(default_config(), f)


def get_boto3_cfg():
    return util.tomli_load(boto3_config_file)


def get_bucket(s3, boto3_cfg):
    return s3.Bucket(boto3_cfg["bucket_name"])


def get_s3(boto3_cfg):
    return boto3.resource(
        's3',
        endpoint_url = boto3_cfg["endpoint_url"],
        aws_access_key_id = boto3_cfg["aws_access_key_id"],
        aws_secret_access_key = boto3_cfg["aws_secret_access_key"]
    )


def get_s3_client(boto3_cfg):
    return boto3.client(
        's3',
        endpoint_url = boto3_cfg["endpoint_url"],
        aws_access_key_id = boto3_cfg["aws_access_key_id"],
        aws_secret_access_key = boto3_cfg["aws_secret_access_key"]
    )


def get_files_summary(bucket):
    try:
        data = get_file_obj(Files_Summary_Name, bucket)
        summary = msgpack.unpackb(data.getvalue())
    except ClientError as err:
        if err.__str__().lower().find("not found") < 0:
            raise
        # 云端找不到 summary 文件, 因此新建.
        upload_files_summary(default_summary, bucket)
        summary = default_summary
    return summary


def upload_files_summary(files_summary, bucket):
    data = msgpack.packb(files_summary)
    bucket.upload_fileobj(io.BytesIO(data), Files_Summary_Name)


def get_file_obj(obj_name, bucket):
    data = io.BytesIO()
    bucket.download_fileobj(obj_name, data)
    return data


def update_files_summary(obj_name, files_summary):
    month = obj_name[:6]
    n = files_summary.get(month, 0)
    files_summary[month] = n + 1
    return files_summary


def add_prefix(filepath: Path):
    return f"{arrow.now().format('YYYYMMDD')}/{filepath.name}"


def upload_file(filepath, files_summary, bucket):
    obj_name = add_prefix(filepath)
    filepath_str = str(filepath)
    bucket.upload_file(
        filepath_str, obj_name, Callback=ProgressPercentage(filepath_str)
    )
    summary = update_files_summary(obj_name, files_summary)
    upload_files_summary(summary, bucket)


def get_file_list(prefix, bucket):
    return bucket.objects.filter(Prefix=prefix)


def print_file_list(files):
    for f in files:
        print(f.key)


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
