# tempbk.py

Temp Backup: 临时备份文件

- 本软件通过终端输入命令上传文件到 Cloudflare R2 进行临时(短期)备份.
- 上传前会自动加密, 下载后会自动解密
- Cloudflare R2 的优点: 10GB免费容量, 流量免费.
- 本软件专门针对小文件的临时(短期)备份, 因此 10GB 免费容量够用了.
- 本软件的安装过程比较复杂, 需要对 Cloudflare R2 及 Python 有基本的理解.

## 准备工作

### 注册 Cloudflare R2

1. 注册账户 <https://www.cloudflare.com/>
2. 启用 R2 服务 <https://developers.cloudflare.com/r2/get-started/>  
   内含 10GB 免费容量, 流量免费, 注册时需要信用卡或 PayPal
3. 在 dashboard 进入 R2 页面，点击 Create bucket 创建一个数据桶。
   建议 bucket 的名称设为 `temp-backup`

至此, 我们得到了一个 bucket, 请记住该 bucket 的名称.

### 生成密钥

1. 在 R2 页面可以找到 Account ID, 请复制保存, 后续有用.
2. 在 R2 页面点击 Manage R2 API Tokens
3. 点击 Create API Token, 权限选择 Edit, 再点击右下角的 Create API Token  
   按钮, 即可得到 Access Key ID 和 Secret Access Key  

**注意**: Access Key ID 和 Secret Access Key 只显示一次, 请立即复制保存
(建议保存到密码管理器中)

至此, 我们一共获得了 4 个重要信息, 请妥善保存这四个信息:

- bucket 名称 (以下称为 **bucket_name**)
- Account ID (以下称为 **accountid**)
- Access Key ID (以下称为 **access_key_id**)
- Secret Access Key (以下称为 **access_key_secret**)

## 安装

要求 Python 3.10 或以上，如果你的系统中未安装 Python 3.10,
推荐使用 [pyenv](https://github.com/pyenv/pyenv) 或
[miniconda](https://docs.conda.io/en/latest/miniconda.html)
来安装最新版本的 Python。

例如，安装 miniconda 后，可以这样创建 3.10 环境：

```sh
$ conda create --name py310 python=3.10.6
$ conda activate py310
```

安装非常简单，只要 `pip install pyboke` 即可。  

(另外推荐了解一下 [pipx](https://pypa.github.io/pipx/)
这是用来安装 Python 命令行软件的优秀工具）

### 获取源代码

可以通过以下其中一种方式下载代码:

1. 最新代码 <https://github.com/ahui2016/py-scripts/archive/refs/heads/main.zip>
2. 指定版本的代码 <https://github.com/ahui2016/py-scripts/releases/latest>

加压缩后, 进入项目根目录 (有 setup.cfg 的文件夹).

### 虚拟环境

可以不适用虚拟环境, 但建议使用 miniconda 或 venv 创建虚拟环境.  

### 本地安装

经过上述操作, 假设你已经进入到项目根目录, 此时执行

```commandline
python -m pip install -e .
```

> (提示: 执行 `python -m pip uninstall .` 可以卸载)

就完成了本地安装, 在此状态下, 你可以直接修改源代码, 一切修改都会立即生效.  
(不需要重新安装)

如果你在一个虚拟环境中进行本地安装, 则每次都需要进入该虚拟环境才能使用本软件.  
(不需要重新安装)

完成以上操作后, 执行命令 `tempbk info`, 会提示出错, 因为还需要进行配置,
配置方法详见下一节.

### 配置

### 新建配置文件

请在任意文件夹（你自己决定在哪个文件夹）新建 `boto3-config.toml` 文件
(采用 utf-8 编码), 内容如下:

```toml
endpoint_url = 'https://<accountid>.r2.cloudflarestorage.com'
aws_access_key_id = '<access_key_id>'
aws_secret_access_key = '<access_key_secret>'
bucket = '<bucket-name>'
```

其中 `<accountid>` 等尖括号的位置要填写正确的值, 一共有 4 个值需要填写,
这四个值都可以在上文 `准备工作` 部分找到.

### 填写配置文件的位置

执行命令 `tempbk info`, 可以看到出错信息, 其中提示了 `py-scripts-config.toml`
的位置, 请用文本编辑器打开该文件, 在文件末尾添加一行:
`boto3_config_file = '''/path/to/boto3-config.toml'''`

其中 `/path/to/boto3-config.toml` 改成上一步新建的 `boto3-config.toml`
文件的实际位置. 例如, 我自己填写的是

```toml
boto3_config_file = '''D:\ahui\Documents\program-settings\boto3-config.toml'''
```

保存文件, 配置完成, 此时再执行 `tempbk info`, 没有错误, 就说明可以开始正常使用了.


## 参考

### 上传文件

- upload_file
  - 通过 *指定文件路径* 来上传文件
  - <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.upload_file>
- upload_fileobj
  - 通过 *提供文件内容* 来上传文件
  - <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.upload_fileobj>


- <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/collections.html>
- <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/collections.html>
- <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html>



<https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet>