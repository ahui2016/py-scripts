# py-scripts

一些零散的 Python 腳本

## fav

Fav: 一句话收藏夹, 主要用于收藏文件/文件夹路径

Fav 是一个只有字符界面的命令行收藏夹, 主要用于收藏文件/文件夹路径,
另外用来收藏常用的 命令/网址 也很合适.

特点:

1. 基本原理极致简单
2. 代码非常简单
3. 意外地好用

文档:

- [README-fav.md](./docs/README-fav.md)
- [fav-setup.md](./docs/fav-setup.md)

## tempbk

Temp Backup: 临时备份文件到 Cloudflare R2

- 本软件通过终端输入命令上传文件到 Cloudflare R2 进行临时(短期)备份.
- Cloudflare R2 的优点: 10GB 免费容量, 流量免费.
- 本软件专门针对小文件的临时(短期)备份, 因此 10GB 免费容量够用了.

文档: [README-tempbk.md](./docs/README-tempbk.md)

## 安装方法

这个项目我选择了本地安装的方式, 因为:

1. 预估会包含较多脚本和命令, 采用本地安装方式方便修改命令名.
2. 预估主要用户是程序员, 采用本地安装方式, 修改代码非常方便.

另外, 如果你想通过 pip 命令安装, 你也可以自行打包发布到 PyPI 

安装本项目会一次性安装全部命令, 如果你只想要其中一两个命令,
可自行研究源代码将想要的功能独立出来 (代码都很简单, 有疑问可以问我).

## 环境要求

要求 Python 3.10 或以上，如果你的系统中未安装 Python 3.10,
推荐使用 [pyenv](https://github.com/pyenv/pyenv) 或
[miniconda](https://docs.conda.io/en/latest/miniconda.html)
来安装最新版本的 Python。

例如，安装 miniconda 后，可以这样创建 3.10 环境：

```sh
$ conda create --name py310 python=3.10.6
$ conda activate py310
```

在 Windows 里使用 miniconda 的方法请看 <https://geeknote.net/SuperMild/posts/1797>

### 获取源代码

可以通过以下其中一种方式下载代码:

1. 最新代码 <https://github.com/ahui2016/py-scripts/archive/refs/heads/main.zip>
2. 指定版本的代码 <https://github.com/ahui2016/py-scripts/releases/latest>

解压缩后, 进入项目根目录 (有 setup.cfg 的文件夹).

或者, 如果你会使用 git, 也可通过 git clone 下载源码.

### 虚拟环境

可以不使用虚拟环境, 但建议使用 miniconda 或 venv 创建虚拟环境.  

### 本地安装

经过上述操作, 假设你已经进入到项目根目录 (py-scripts), 此时执行

```commandline
python -m pip install -e .
```

就完成了本地安装, 在此状态下, 你可以直接修改源代码, 一切修改都会立即生效.
(不需要重新安装)

如果你在一个虚拟环境中进行本地安装, 则每次都需要进入该虚拟环境才能使用本软件.

> (提示: 执行 `python -m pip uninstall .` 可以卸载)

### 更改命令名

安装后, 可以得到一些命令, 例如 tempbk, fav 等, 如果你不喜欢这些名称,
可以打开 pyproject.toml, 在 `[project.scripts]` 区域修改命令名,
保存后, 重新执行一次 `python -m pip install -e .`

(修改源代码不需要重新安装, 修改命令名需要重新安装.)
