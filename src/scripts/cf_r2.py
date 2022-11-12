import json
import os
import sys
import threading
from pathlib import Path

import boto3
import tomli_w
import arrow
from humanfriendly import format_size
from botocore.config import Config

from . import util, config
from .util import MB


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

Objects_Summary = "objects_summary"
"""
dict[str, int]  # 日期(年月)与文件数量 '202201': 5
"""
default_summary = {}

Download_Dir = "download_dir"
Upload_Size_Limit = "upload_size_limit"
Use_Proxy = "use_proxy"
Http_Proxy = "http_proxy"
Boto3_Config_Filename = "boto3_config.toml"
boto3_config_file = config.app_config_dir.joinpath(Boto3_Config_Filename)


def default_config():
    return dict(
        endpoint_url          ='https://<accountid>.r2.cloudflarestorage.com',
        aws_access_key_id     = '<access_key_id>',
        aws_secret_access_key = '<access_key_secret>',
        bucket_name           = '<bucket_name>',
        download_dir          = '',
        upload_size_limit     = 50 * MB,
        http_proxy            = 'http://127.0.0.1:1081',
        use_proxy             = False,
    )


def ensure_config_file() -> None:
    if not boto3_config_file.exists():
        write_boto3_cfg(default_config())


def write_boto3_cfg(boto3_cfg):
    with open(boto3_config_file, "wb") as f:
        tomli_w.dump(boto3_cfg, f)


def get_boto3_cfg():
    return util.tomli_load(boto3_config_file)


def print_boto3_cfg(boto3_cfg):
    print(f"[boto3 config]\n{boto3_config_file}\n")
    dl_dir = boto3_cfg.get(Download_Dir, "")
    if not dl_dir:
        dl_dir = "(未设置下载文件夹, 设置方法请查看帮助: tempbk download -h)"
    print(f"[download dir]\n{dl_dir}\n")
    print(f"[upload size limit] {boto3_cfg[Upload_Size_Limit]} MB")
    print(f"[use proxy] {boto3_cfg[Use_Proxy]}")
    proxy = boto3_cfg[Http_Proxy]
    if not proxy and boto3_cfg[Use_Proxy]:
        proxy = f"\n未设置 proxy, 请用文本编辑器打开 '{boto3_config_file}' 填写 http proxy"
    print(f"[http proxy] {proxy}")


def get_bucket(s3, boto3_cfg):
    return s3.Bucket(boto3_cfg["bucket_name"])


def get_s3(boto3_cfg):
    return boto3.resource(
        's3',
        endpoint_url=boto3_cfg["endpoint_url"],
        aws_access_key_id=boto3_cfg["aws_access_key_id"],
        aws_secret_access_key=boto3_cfg["aws_secret_access_key"],
        config=Config(proxies=get_proxies(boto3_cfg)),
    )


def get_proxies(boto3_cfg):
    if boto3_cfg[Use_Proxy]:
        return dict(http=boto3_cfg[Http_Proxy], https=boto3_cfg[Http_Proxy])
    return None


def set_use_proxy(sw:str, boto3_cfg):
    use_proxy = False
    if sw.lower() in ["1", "on", "true"]:
        use_proxy = True

    boto3_cfg[Use_Proxy] = use_proxy
    write_boto3_cfg(boto3_cfg)
    proxy = boto3_cfg[Http_Proxy]
    print(f"设置成功\nuse proxy = {use_proxy}\nhttp proxy = {proxy}")

    if not proxy and use_proxy:
        print(f"未设置 proxy, 请用文本编辑器打开 {boto3_config_file} 填写 http proxy")


def set_size_limit(limit, boto3_cfg):
    boto3_cfg[Upload_Size_Limit] = limit
    write_boto3_cfg(boto3_cfg)
    print(f"设置成功, 上传文件大小上限: {limit} MB")


def get_size_limit(boto3_cfg):
    return boto3_cfg[Upload_Size_Limit] * MB


def set_download_dir(dir_path:str, boto3_cfg):
    boto3_cfg[Download_Dir] = dir_path
    write_boto3_cfg(boto3_cfg)
    print(f"设置成功, 下载文件默认保存至 {dir_path}")


def get_download_dir(boto3_cfg):
    return Path(boto3_cfg[Download_Dir])


def check_download_dir(boto3_cfg):
    """
    :return: err: str
    """
    dl_dir = boto3_cfg.get(Download_Dir, "")
    if not dl_dir:
        return "请先设置文件夹用于保存下载文件, 例如:\n" \
            "tempbk download -dir /path/to/folder"
    return ""


def get_summary(boto3_cfg):
    if Objects_Summary not in boto3_cfg:
        write_summary(default_summary, boto3_cfg)
        return default_summary

    return json.loads(boto3_cfg[Objects_Summary])


def write_summary(summary:dict, boto3_cfg):
    boto3_cfg[Objects_Summary] = json.dumps(summary)
    write_boto3_cfg(boto3_cfg)


def update_summary(obj_name, summary):
    """上传文件时, 统计数字加一."""
    month = obj_name[:6]
    n = summary.get(month, 0)
    summary[month] = n + 1
    return summary


def minus_summary(deleted, summary):
    """删除文件时, 根据删除结果更新统计数字."""
    for obj in deleted:
        month = obj['Key'][:6]
        n = summary.get(month, 0)
        summary[month] = n - 1

        if summary[month] <= 0:
            del summary[month]

    return summary


def print_summary(summary:dict):
    if len(summary) == 0:
        print("云端文件数量: 零")
        return

    for month, n in summary.items():
        month_year = arrow.get(month, 'YYYYMM').format('MMM-YYYY')
        print(f"{month_year}: {n}")


def print_deleted(deleted):
    print("\nDeleted:\n")
    for obj in deleted:
        print(obj['Key'])


def today():
    return arrow.now().format('YYYYMMDD')


def add_prefix(filepath: Path):
    return f"{today()}/{filepath.name}"


def check_file_size(file:Path, boto3_cfg):
    """
    :return: err: str
    """
    filesize = file.lstat().st_size
    sizelimit = get_size_limit(boto3_cfg)
    if filesize > sizelimit:
        return f"文件体积({format_size(filesize)}) 超过上限({boto3_cfg[Upload_Size_Limit]}MB)"
    return ""


def upload_file(filepath, summary, boto3_cfg, bucket):
    """
    :return: err: str
    """
    if err := check_file_size(filepath, boto3_cfg):
        return err

    obj_name = add_prefix(filepath)
    exists = obj_exists(obj_name, bucket)
    filepath_str = str(filepath)
    bucket.upload_file(
        filepath_str, obj_name, Callback=UploadProgress(filepath_str)
    )
    if not exists:
        summary = update_summary(obj_name, summary)
        write_summary(summary, boto3_cfg)

    return ""


def get_new_files(folder:Path):
    files = folder.glob("*")
    files = [x for x in files if x.is_file()]
    files.sort(key=lambda x: x.lstat().st_mtime, reverse=True)
    return files[0]


def obj_exists(obj_name, bucket):
    objects = get_objects_by_prefix(obj_name, bucket)
    for obj in objects:
        if obj.key == obj_name:
            return True
    return False


def get_objects_by_prefix(prefix, bucket):
    return bucket.objects.filter(Prefix=prefix)


def objects_to_list(objects):
    """objects 是迭代器, 有时需要转换为 list."""
    obj_list = []
    for obj in objects:
        obj_list.append(dict(key=obj.key, size=obj.size))
    return obj_list


def objects_to_delete(objects):
    """专门转换为待删除列表"""
    obj_list = []
    for f in objects:
        obj_list.append(dict(Key=f.key))
    return obj_list


def print_objects_with_size(objects):
    for obj in objects:
        print(f"({format_size(obj['size'])}) {obj['key']}")


def print_objects_key(objects):
    i = 0
    for obj in objects:
        print(obj.key)
        i += 1
    return i


def delete_objects(objects, summary, boto3_cfg, bucket):
    resp = bucket.delete_objects(
        Delete={'Objects': objects}
    )
    deleted = resp['Deleted']
    summary = minus_summary(deleted, summary)
    write_summary(summary, boto3_cfg)
    if len(objects) != len(deleted):
        print_deleted(deleted)
    if 'Errors' in resp:
        print(resp['Errors'])


def get_download_filepath(obj_name:str, folder:Path, filepath:Path):
    """
    :return: (result, err_code)
    """
    if filepath is None:
        filepath = folder.joinpath(obj_name[9:])
    if not filepath.parent.exists():
        return None, f"文件夹不存在: {filepath.parent}"
    if filepath.exists():
        return filepath, f"文件已存在: {filepath}"
    return filepath, ""


def download_file(bucket, obj_name, size, filepath):
    print(f"Download {obj_name} to {filepath}")
    bucket.download_file(
        obj_name, str(filepath), Callback=DownloadProgress(obj_name, size)
    )


# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
class UploadProgress(object):
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


# https://gist.github.com/egeulgen/538aadc90275d79d514a5bacc4d5694e
class DownloadProgress(object):
    def __init__(self, filename, size):
        self._filename = filename
        self._size = size
        self._seen_so_far = 0
        self._lock = threading.Lock()
        self.prog_bar_len = 80

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            ratio = round((float(self._seen_so_far) / float(self._size)) * (self.prog_bar_len - 6), 1)
            current_length = int(round(ratio))

            percentage = round(100 * ratio / (self.prog_bar_len - 6), 1)

            bars = '+' * current_length
            output = bars + ' ' * (self.prog_bar_len - current_length - len(str(percentage)) - 1) + str(
                percentage) + '%'

            if self._seen_so_far != self._size:
                sys.stdout.write(output + '\r')
            else:
                sys.stdout.write(output + '\n')
            sys.stdout.flush()
