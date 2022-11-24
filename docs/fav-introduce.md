# Fav: 命令行收藏夹, 主要用于收藏文件/文件夹路径

Fav 是一个只有字符界面的命令行收藏夹, 主要用于收藏文件/文件夹路径,
另外用来收藏常用的 命令/网址 也很合适.

特点:

1. 基本原理极致简单
2. 代码非常简单
3. 意外地好用

## 基本用法示例

假设已经登记了 3 行内容:

```text
/path/to/folder
https://example.com
C:\User\XiaoMei\
```

使用本程序登记的全部数据, 记录在一个纯文本文件中, 如上所示.  
(不是 JSON, 不是 YAML, 完全不需要考虑格式与字符转义, 就是纯文本, 一行一句.)

执行命令 `fav` 会显示收藏列表:

```text
1. /path/to/folder
2. https://example.com
3. C:\User\XiaoMei\abc.txt
```

执行命令 `fav 2` 会在屏幕上打印 `https://example.com`, 同时复制到剪贴板.

执行命令 `vim $(fav 3)` 相当于执行 `vim C:\User\XiaoMei\abc.txt`

执行命令 `fav -del 2` 可以删除第 2 行, 结果变成:

```text
1. /path/to/folder
2.
3. C:\User\XiaoMei\abc.txt
```

**重点: 序号与内容的对应关系不会变**, 这是本程序的最重要的特性.

后续使用命令 `fav -add` 新增内容会自动填补空缺.

如果要改变顺序, 或修改其中一行的内容, 可以直接打开原始数据文件, 直接修改即可.

例如, 假设第 1 行就是原始数据文件的路径, 那么执行命令
`vim $(fav 1)` 就能直接打开文件进行编辑, 非常方便.

执行命令 `fav -info` 可以找到原始数据文件的位置, 使用命令
`fav -add /path/to/file.txt` (其中 '/path/to/file.txt' 改为具体的文件路径)
添加路径到收藏列表中, 以后就可以通过上述方法方便地打开文件了.

## 搜索

可以采用符合命令行习惯方法进行搜索, 例如:

`fav |grep abcd`

如果使用 [ripgrep](https://github.com/BurntSushi/ripgrep), 则是
`fav |rg -i abcd` 其中 `-i` 表示不分大小写.

## 源代码

本程序的源代码基本上就是一个文件 <https://github.com/ahui2016/py-scripts/blob/main/src/fav.py>

全部代码只有 100 行左右, 极致简单, 下面介绍了通过源码进行本地安装的方法,
另外你也可以采用其它方法, 比如自己打包发布到 PyPI.

由于这个小工具的原理与代码是如此之简单, 你也可以用自己熟悉的语言改写,
只要花很少时间即可, 从此拥有一个命令行收藏夹, 还蛮好用的.

我自己是在 Windows 里使用, 将 Windows Terminal 固定在任务栏第一位,
按 Win+1 就能调出终端使用命令行工具.

## 安装与使用

- 源码仓库及安装方法 [py-scripts](https://github.com/ahui2016/py-scripts)
- 使用方法 [fav-usage.md](https://github.com/ahui2016/py-scripts/blob/main/docs/fav-usage.md)
