# tbk.py

Temp Backup (secure): 加密并备份文件到 Cloudflare R2

- 本软件通过终端输入命令上传文件到 Cloudflare R2 进行临时(短期)备份.
- Cloudflare R2 的优点: 10GB 免费容量, 流量免费.
- 本软件专门针对小文件的临时(短期)备份, 因此 10GB 免费容量够用了.
- 上传前自动加密, 下载后自动解密.
- 本软件的安装过程比较复杂, 需要对 Cloudflare R2 及 Python 有基本的理解.

## 准备工作

### 注册 Cloudflare R2

1. 注册账户 <https://www.cloudflare.com/>
2. 启用 R2 服务 <https://developers.cloudflare.com/r2/get-started/>  
   内含 10GB 免费容量, 流量免费, 注册时需要信用卡或 PayPal  
   (注意: 上传下载等的操作次数超过上限也会产生费用,
    详情以 Cloudflare 官方说明为准).
3. 从 dashboard 进入 R2 页面，点击 Create bucket 创建一个数据桶。
   建议 bucket 的名称设为 `temp-backup-secure`

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

## 安装 tbk.py

tbk 是 py-scripts 的一部分, 安装方法详见 [py-scripts/README.md](../README.md)

安装完成后, 执行命令 `tbk -info`, 可以看到配置文件的具体位置,
接下来需要打开配置文件填写信息, 详见下一节.

### 配置

执行命令 `tbk -info`, 可以看到 `[tbk config]` 的具体位置,
请使用文本编辑器打开 `tbk_config.toml` 文件, 可以看到内容如下:

```toml
endpoint_url = 'https://<accountid>.r2.cloudflarestorage.com'
aws_access_key_id = '<access_key_id>'
aws_secret_access_key = '<access_key_secret>'
bucket = '<bucket_name>'
secret_key = '28hfhw2ghg93tigh48ut......'
```

其中 `<accountid>` 等尖括号的位置要填写正确的值, 一共有 4 个值需要填写,
这四个值都可以在上文 `准备工作` 部分找到. (填写时, 不要保留尖括号.)

填写正确的值后保存文件, 配置完成, 可以开始正常使用.

### 重要: 保存密钥！

在上面所述的 tbk_config.toml 文件中, secret_key 是自动生成的密钥,
用来自动加密解密文件, 请复制该密钥到密码管理器中妥善保存, 一旦遗失,
上传到云端的文件将无法解密.

密钥要继续保留在 tbk_config.toml 文件里, 明文保存, 任何能接触到你的电脑
的人或软件理论上都能获取到该密钥, 但由于本程序的主要用途是临时备份少量文件,
因此安全要求也不高, 这样就足够了, 主要是防止云端泄密, 不防本地泄密.

### 无加密功能的版本

本程序另外有一个不加密的版本: [tempbk](https://github.com/ahui2016/py-scripts)

tbk 与 tempbk 的功能几乎一模一样, 主要是加密与不加密的区别.

- **tbk**(加密):
  - 可以防止云端分析文件
  - 一旦丢失密钥就无法解密
  - 用 tbk 上传的文件, 通常要用 tbk 下载才方便解密
  - 加密后文件体积会增加33%
- **tempbk**(不加密):
  - 不能防止云端分析文件, 有一定法律风险或云端泄密风险 
  - 用 tempbk 上传的文件, 除了可以用 tempbk 下载, 还可以去 Cloudflare 网站下载

## 上传文件

- 使用命令 `tbk upload FILE` 上传文件到云端.
- `tbk -u FILE` 等同于 `tbk upload FILE`
- 上传文件体积上限默认 50MB, 防止不小心上传太大的文件.
- 使用命令 `tbk -info` 可以查看上传文件体积上限.
- 可以自定义上传文件体积上限, 例如 `tbk --set-size 25` 将上限设为 25MB

### 自动选择一个最新文件

- 使用命令 `tbk upload FOLDER` (其中 FOLDER 是一个文件夹)
  可以自动选择该文件夹中的一个最新文件 (以最近修改时间为准),
  按回车键上传, 输入 n 回车取消.
- 例如 `tbk upload .` 上传当前文件夹内的最新文件.
- `tbk -u FOLDER` 等同于 `tbk upload FOLDER`

### 同名文件

- 在同一天内多次上传同名文件, 新上传的文件会覆盖旧文件.
- 如果不是同一天 (比如隔天) 上传同名文件, 在云端会产生一个新的文件,
  也就是说, 昨天或更早的同名文件会保留, 不会被覆盖.

## 统计数据

- 使用命令 `tbk count` 可查看各个月份上传了多少个文件.
- `tbk -c` 等同于 `tbk count`
- 全部文件占用的总空间大小, 请到 Cloudflare 网站查看.
- 使用命令 `tbk list today` 可列出今天上传的全部文件.
- `tbk list 202211` 列出2022年11月上传的全部文件.
- `tbk list 20221111` 列出2022年11月11日上传的全部文件.
- `tbk list 202` 列出2020年至2029年上传的全部文件.
- `tbk -l` 等同于 `tbk list`

## 删除云端文件

- `tbk delete 202` 删除2020年至2029年上传的全部文件.
- `tbk delete 202211` 删除2022年11月上传的全部文件.
- `tbk delete 20221111` 删除2022年11月11日上传的全部文件.
- `tbk delete 20221111/abc.txt` 删除2022年11月11日上传的名为 abc.txt 的文件
- `tbk -del` 等同于 `tbk delete`

## 下载文件

- `tbk download 20221111/abc.txt --save-as /path/to/cde.txt`
  下载指定前缀的文件保存到指定的文件夹及文件名
- 另外可以在下载前指定保存文件的文件夹, 例如:
  `tbk download -dir /path/to/folder`  
  只需要设置一次, 后续使用命令 `tbk download 20221111/abc.txt`
  下载文件就会自动保存在指定的文件夹.
- 使用命令 `tbk -info` 可以查看当前设定的下载文件夹.
- `tbk -dl PREFIX` 等同于 `tbk download PREFIX`  
  但要注意, `tbk -dl` 不能搭配 `--save-as` 或 `-dir` 使用.

## 使用代理 (http proxy)

- 默认不使用代理.
- 使用命令 `tbk --use-proxy true` 可设置为使用代理.  
  其中 `true` 也可以是 `1`(壹) 或 `on`.
- 在上面的命令中, 如果输入参数不是 `true`, `1`, `on`, 而是其它任何文字,
  则会设置为不使用代理.
- 默认代理地址是 `http://127.0.0.1:1081`, 可通过命令 `tbk -info`
  找到 tbk config 文件的位置, 用文本编辑器打开它, 修改 http proxy.

## 与 Fav 搭配使用

Fav 是一个命令行收藏夹, 主要用于收藏文件/文件夹路径.

如果你有一些文件需要经常备份, 可以将其文件路径保存到 Fav 中, 然后用
`tbk -u $(fav 1)` 的方式上传文件, 其中 fav 后面的数字是 fav 中的
已登记文件路径的序号.

关于 Fav 的安装与使用:
[py-scripts/blob/main/docs/README-fav.md](https://github.com/ahui2016/py-scripts/blob/main/docs/README-fav.md)
