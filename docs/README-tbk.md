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

