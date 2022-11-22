from cryptography.fernet import Fernet

from . import config

Config_Filename = "tbk_config.toml"
default_summary = {}
config_file = config.app_config_dir.joinpath(Config_Filename)


def default_config():
    return dict(
        endpoint_url          ='https://<accountid>.r2.cloudflarestorage.com',
        aws_access_key_id     = '<access_key_id>',
        aws_secret_access_key = '<access_key_secret>',
        bucket_name           = '<bucket_name>',
        download_dir          = '',
        upload_size_limit     = 50,
        http_proxy            = 'http://127.0.0.1:1081',
        use_proxy             = False,
        secret_key            = Fernet.generate_key().hex(),
    )
