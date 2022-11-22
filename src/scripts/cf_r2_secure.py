import io
from pathlib import Path

from cryptography.fernet import Fernet

from . import cf_r2
from .const import Secret_Key

"""
參考:
https://developers.cloudflare.com/r2/examples/boto3/
"""

"""
【关于返回值】
本项目的返回值有时采用 (result, err) 的形式,
err 是 str, 有内容表示有错误, 空字符串表示没错误.

【关于 object 与 file】
为了便于区分, 在代码中将本地文件称为 file, 云端文件称为 object.
"""


def get_fernet(cfg):
    key = bytes.fromhex(cfg[Secret_Key])
    return Fernet(key)


def encrypt(data:bytes, cfg) -> bytes:
    return get_fernet(cfg).encrypt(data)


def decrypt(token:bytes, cfg) -> bytes:
    return get_fernet(cfg).decrypt(token)


def upload_file(filepath, summary, cfg_file, cfg, bucket):
    """
    :return: err: str
    """
    if err := cf_r2.check_file_size(filepath, cfg):
        return err

    obj_name = cf_r2.add_prefix(filepath)
    exists = cf_r2.obj_exists(obj_name, bucket)
    filepath_str = str(filepath)

    with open(filepath, 'rb') as data:
        token = encrypt(data.read(), cfg)
        obj = io.BytesIO(token)
        bucket.upload_fileobj(
            obj, obj_name, Callback=cf_r2.UploadProgress(filepath_str))

    if not exists:
        summary = cf_r2.update_summary(obj_name, summary)
        cf_r2.write_summary(summary, cfg_file, cfg)

    return ""


def download_file(bucket, obj_name, size, filepath:Path, cfg):
    print(f"Download {obj_name} to {filepath}")
    data = io.BytesIO()
    bucket.download_fileobj(
        obj_name, data, Callback=cf_r2.DownloadProgress(obj_name, size))
    file_data = decrypt(data.read(), cfg)
    filepath.write_bytes(file_data)
