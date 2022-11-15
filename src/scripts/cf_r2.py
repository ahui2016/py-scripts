import json
import os
import sys
import threading
from pathlib import Path

import boto3
import arrow
import tomli_w
from humanfriendly import format_size
from botocore.config import Config

from . import util
from .const import MB, Use_Proxy, Http_Proxy, Upload_Size_Limit, Download_Dir, \
    Objects_Summary, Fav_Paths


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


def ensure_config_file(cfg_file, default_config) -> None:
    if not cfg_file.exists():
        write_config(cfg_file, default_config)


def write_config(cfg_file, cfg):
    with open(cfg_file, "wb") as f:
        tomli_w.dump(cfg, f)


def get_config(cfg_file):
    return util.tomli_load(cfg_file)


def print_config(cfg_file, cfg):
    dl_dir = cfg.get(Download_Dir, "")
    if not dl_dir:
        dl_dir = "(未设置下载文件夹, 设置方法请查看帮助: tempbk download -h)"
    print(f"[download dir]\n{dl_dir}\n")
    print(f"[upload size limit] {cfg[Upload_Size_Limit]} MB")
    print(f"[use proxy] {cfg[Use_Proxy]}")
    proxy = cfg[Http_Proxy]
    if not proxy and cfg[Use_Proxy]:
        proxy = f"\n未设置 proxy, 请用文本编辑器打开 '{cfg_file}' 填写 http proxy"
    print(f"[http proxy] {proxy}")


def get_bucket(s3, cfg):
    return s3.Bucket(cfg["bucket_name"])


def get_s3(cfg):
    return boto3.resource(
        's3',
        endpoint_url=cfg["endpoint_url"],
        aws_access_key_id=cfg["aws_access_key_id"],
        aws_secret_access_key=cfg["aws_secret_access_key"],
        config=Config(proxies=get_proxies(cfg)),
    )


def get_proxies(cfg):
    if cfg[Use_Proxy]:
        return dict(http=cfg[Http_Proxy], https=cfg[Http_Proxy])
    return None


def set_use_proxy(sw:str, cfg, cfg_file):
    use_proxy = False
    if sw.lower() in ["1", "on", "true"]:
        use_proxy = True

    cfg[Use_Proxy] = use_proxy
    write_config(cfg_file, cfg)
    proxy = cfg[Http_Proxy]
    print(f"设置成功\nuse proxy = {use_proxy}\nhttp proxy = {proxy}")

    if not proxy and use_proxy:
        print(f"未设置 proxy, 请用文本编辑器打开 {cfg_file} 填写 http proxy")


def set_size_limit(limit, cfg_file, cfg):
    cfg[Upload_Size_Limit] = limit
    write_config(cfg_file, cfg)
    print(f"设置成功, 上传文件大小上限: {limit} MB")


def get_size_limit(cfg):
    return cfg[Upload_Size_Limit] * MB


def add_fav(fav_path:Path, cfg_file, cfg):
    if Fav_Paths not in cfg:
        cfg[Fav_Paths] = []
    cfg[Fav_Paths].append(str(fav_path.resolve()))
    write_config(cfg_file, cfg)


def check_fav_n(n:int, cfg):
    """
    有错误时返回错误内容, 如果返回空字符串则表示没有错误.
    """
    if (Fav_Paths not in cfg) or (len(cfg[Fav_Paths]) == 0):
        return "尚未登记任何路径."
    if n <= 0:
        return f"n 不可小于等于零."
    length = len(cfg[Fav_Paths])
    if n > length:
        return f"{n} 超过已登记路径的数量({length})"
    return ""


def del_fav(n:int, cfg_file, cfg):
    """参数 n 从 1 开始计数, 用于列表时需要减一.
    有错误时返回错误内容, 如果返回空字符串则表示没有错误.
    """
    if err := check_fav_n(n, cfg):
        return err

    del cfg[Fav_Paths][n-1]
    write_config(cfg_file, cfg)
    return ""


def print_fav(cfg):
    if (Fav_Paths not in cfg) or (len(cfg[Fav_Paths]) == 0):
        print("尚未登记任何路径.")
        return

    n = 1
    for item in cfg[Fav_Paths]:
        print(f"{n} {item}")
        n += 1


def get_fav(n, cfg) -> (Path|None, str):
    """Return (result, err)"""
    if err := check_fav_n(n, cfg):
        return None, err

    fav = cfg[Fav_Paths][n]
    return Path(fav), ""


def set_download_dir(dir_path:str, cfg_file, cfg):
    cfg[Download_Dir] = dir_path
    write_config(cfg_file, cfg)
    print(f"设置成功, 下载文件默认保存至 {dir_path}")


def get_download_dir(cfg):
    return Path(cfg[Download_Dir])


def download_dir_exists(cfg):
    """
    :return: err: str
    """
    dl_dir = cfg.get(Download_Dir, "")
    if not dl_dir:
        return "请先设置文件夹用于保存下载文件, 例如:\n" \
            "tempbk download -dir /path/to/folder"
    return ""


def get_summary(cfg_file, cfg, default_summary):
    # Objects_Summary: dict[str, int]  日期(年月)与文件数量 '202201': 5
    if Objects_Summary not in cfg:
        write_summary(default_summary, cfg_file, cfg)
        return default_summary
    return json.loads(cfg[Objects_Summary])


def write_summary(summary:dict, cfg_file, cfg):
    # Objects_Summary: dict[str, int]  日期(年月)与文件数量 '202201': 5
    cfg[Objects_Summary] = json.dumps(summary)
    write_config(cfg_file, cfg)


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


def check_file_size(file:Path, cfg):
    """
    :return: err: str
    """
    filesize = file.lstat().st_size
    sizelimit = get_size_limit(cfg)
    if filesize > sizelimit:
        return f"文件体积({format_size(filesize)}) 超过上限({cfg[Upload_Size_Limit]}MB)"
    return ""


def upload_file(filepath, summary, cfg_file, cfg, bucket):
    """
    :return: err: str
    """
    if err := check_file_size(filepath, cfg):
        return err

    obj_name = add_prefix(filepath)
    exists = obj_exists(obj_name, bucket)
    filepath_str = str(filepath)
    bucket.upload_file(
        filepath_str, obj_name, Callback=UploadProgress(filepath_str)
    )
    if not exists:
        summary = update_summary(obj_name, summary)
        write_summary(summary, cfg_file, cfg)

    return ""


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
    """转换为待删除列表"""
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


def print_delete_list(del_list):
    limit = 10  # 最多只显示 10 个文件名
    length = len(del_list)
    if length < limit:
        limit = length
    for i in range(limit):
        print(del_list[i]["Key"])

    more = length - limit
    if more > 0:
        print(f"... {more} more items not showing ...")


def delete_objects(objects, summary, cfg_file, cfg, bucket):
    resp = bucket.delete_objects(
        Delete={'Objects': objects}
    )
    deleted = resp['Deleted']
    summary = minus_summary(deleted, summary)
    write_summary(summary, cfg_file, cfg)
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
