# tempbk.py

Temp Backup: 临时备份文件到 Cloudflare R2

- 本软件通过终端输入命令上传文件到 Cloudflare R2 进行临时(短期)备份.
- Cloudflare R2 的优点: 10GB 免费容量, 流量免费.
- 本软件专门针对小文件的临时(短期)备份, 因此 10GB 免费容量够用了.
- 我这里直连 Cloudflare 速度比较慢, 但设置代理后就很快了.
- 本软件的安装过程比较复杂, 需要对 Cloudflare R2 及 Python 有基本的理解.

## 准备工作

### 开通 Cloudflare R2

1. 注册账户 <https://www.cloudflare.com/>
2. 启用 R2 服务 <https://developers.cloudflare.com/r2/get-started/>  
   内含 10GB 免费容量, 流量免费, 注册时需要信用卡或 PayPal  
   (注意: 上传下载等的操作次数超过上限也会产生费用,
    详情以 Cloudflare 官方说明为准).
3. 从 dashboard 进入 R2 页面，点击 Create bucket 创建一个数据桶。
   建议 bucket 的名称设为 `temp-backup`

至此, 我们得到了一个 bucket, 请记住该 bucket 的名称.

### 生成密钥

(如果已经有密钥, 就不需要再生成了.)

1. 在 R2 页面可以找到 Account ID, 请复制保存, 后续有用.
2. 在 R2 页面点击 Manage R2 API Tokens
3. 点击 Create API Token, 权限选择 Edit, 再点击右下角的 Create API
   Token 按钮, 即可得到 Access Key ID 和 Secret Access Key

**注意**:  
Access Key ID 和 Secret Access Key 只显示一次, 请立即复制保存
(建议保存到密码管理器中)

至此, 我们一共获得了 4 个重要信息, 请妥善保存这四个信息:

- bucket 名称 (以下称为 **bucket_name**)
- Account ID (以下称为 **accountid**)
- Access Key ID (以下称为 **access_key_id**)
- Secret Access Key (以下称为 **access_key_secret**)

## 安装 tempbk.py

tempbk 是 py-scripts 的一部分, 安装方法详见 [py-scripts/README.md](../README.md)

安装完成后, 执行命令 `tempbk -info`, 可以看到配置文件的具体位置,
接下来需要打开配置文件填写信息, 详见下一节.

### 配置

执行命令 `tempbk -info`, 可以看到 `[tempbk config]` 的具体位置,
请使用文本编辑器打开 `tempbk_config.toml` 文件, 可以看到内容如下:

```toml
endpoint_url = 'https://<accountid>.r2.cloudflarestorage.com'
aws_access_key_id = '<access_key_id>'
aws_secret_access_key = '<access_key_secret>'
bucket = '<bucket_name>'
```

其中 `<accountid>` 等尖括号的位置要填写正确的值, 一共有 4 个值需要填写,
这四个值都可以在上文 `准备工作` 部分找到. (填写时, 不要保留尖括号.)

填写正确的值后保存文件, 配置完成, 可以开始正常使用.


## 上传文件

- 使用命令 `tempbk upload FILE` 上传文件到云端.
- `tempbk -u FILE` 等同于 `tempbk upload FILE`
- 上传文件体积上限默认 50MB, 防止不小心上传太大的文件.
- 使用命令 `tempbk -info` 可以查看上传文件体积上限.
- 可以自定义上传文件体积上限, 例如 `tempbk --set-size 25` 将上限设为 25MB

### 自动选择一个最新文件

- 使用命令 `tempbk upload FOLDER` (其中 FOLDER 是一个文件夹)
  可以自动选择该文件夹中的一个最新文件 (以最近修改时间为准),
  按回车键上传, 输入 n 回车取消.
- 例如 `tempbk upload .` 上传当前文件夹内的最新文件.
- `tempbk -u FOLDER` 等同于 `tempbk upload FOLDER`

### 同名文件

- 在同一天内多次上传同名文件, 新上传的文件会覆盖旧文件.
- 如果不是同一天 (比如隔天) 上传同名文件, 在云端会产生一个新的文件,
  也就是说, 昨天或更早的同名文件会保留, 不会被覆盖.

## 统计数据

- 使用命令 `tempbk count` 可查看各个月份上传了多少个文件.
- `tempbk -c` 等同于 `tempbk count`
- 全部文件占用的总空间大小, 请到 Cloudflare 网站查看.
- 使用命令 `tempbk list today` 可列出今天上传的全部文件.
- `tempbk list 202211` 列出2022年11月上传的全部文件.
- `tempbk list 20221111` 列出2022年11月11日上传的全部文件.
- `tempbk list 202` 列出2020年至2029年上传的全部文件.
- `tempbk -l` 等同于 `tempbk list`

## 删除云端文件

- `tempbk delete 202` 删除2020年至2029年上传的全部文件.
- `tempbk delete 202211` 删除2022年11月上传的全部文件.
- `tempbk delete 20221111` 删除2022年11月11日上传的全部文件.
- `tempbk delete 20221111/abc.txt` 删除2022年11月11日上传的名为 abc.txt 的文件
- `tempbk -del` 等同于 `tempbk delete`

## 下载文件

- `tempbk download 20221111/abc.txt --save-as /path/to/cde.txt`
  下载指定前缀的文件保存到指定的文件夹及文件名
- 另外可以在下载前指定保存文件的文件夹, 例如:
  `tempbk download -dir /path/to/folder`  
  只需要设置一次, 后续使用命令 `tempbk download 20221111/abc.txt`
  下载文件就会自动保存在指定的文件夹.
- 使用命令 `tempbk -info` 可以查看当前设定的下载文件夹.
- 另外, 在 Cloudflare 网站也可以下载文件.
- `tempbk -dl PREFIX` 等同于 `tempbk download PREFIX`  
  但要注意, `tempbk -dl` 不能搭配 `--save-as` 或 `-dir` 使用.

## 使用代理 (http proxy)

- 默认不使用代理.
- 使用命令 `tempbk --use-proxy true` 可设置为使用代理.  
  其中 `true` 也可以是 `1`(壹) 或 `on`.
- 在上面的命令中, 如果输入参数不是 `true`, `1`, `on`, 而是其它任何文字,
  则会设置为不使用代理.
- 默认代理地址是 `http://127.0.0.1:1081`, 可通过命令 `tempbk -info`
  找到 tempbk config 文件的位置, 用文本编辑器打开它, 修改 http proxy.

## 与 Fav 搭配使用

Fav 是一个命令行收藏夹, 主要用于收藏文件/文件夹路径.

如果你有一些文件需要经常备份, 可以将其文件路径保存到 Fav 中, 然后用
`tempbk -u $(fav 1)` 的方式上传文件, 其中 fav 后面的数字是 fav 中的
已登记文件路径的序号.

关于 Fav 的安装与使用:
[py-scripts/blob/main/docs/README-fav.md](https://github.com/ahui2016/py-scripts/blob/main/docs/README-fav.md)

## 加密功能

另外有一个有加密功能的版本: [tbk](https://github.com/ahui2016/py-scripts)

tbk 与 tempbk 的功能几乎一模一样, 主要是加密与不加密的区别.

## TODO

- 下载后自动删除云端文件

## 参考

### 上传文件

- upload_file
  - 通过 *指定文件路径* 来上传文件
  - <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.upload_file>
- upload_fileobj
  - 通过 *提供文件内容* 来上传文件
  - <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.upload_fileobj>

### proxy

<https://stackoverflow.com/questions/33480108/how-do-you-use-an-http-https-proxy-with-boto3>

### 加密

<https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet>
