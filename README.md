<div align="center">

# 🩹 CathayRepair

**PDF 损伤修复工具 · 逐页抢救打不开、会崩的 PDF**

*开箱即用 · 双击即开 · 纯本地 · 不联网 · 绝不改动原件*

[![license](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
[![platform](https://img.shields.io/badge/platform-Windows%2010%2B-brightgreen)]()
[![python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![GitHub release](https://img.shields.io/github/v/release/zzhjim02/CathayRepair)]()

**一个 PDF 卡在某页打不开、读到一半就崩？→ 逐页复制，坏页跳过，另存一个新文件。**

原件一个字节都不动，修好的副本旁边放着，直接拿去 OCR。

</div>

---


## 🔗 Cathay 人文社科工具链

这是一整套给人文社科研究者用的**本地**工具：从「找到一本书」，到「把它变成能搜、能读、能引用的 PDF」，再到「在上万本书里一秒检索」——每一步一个小程序，**各自独立，只挑你用得上的那一步就行**。

| 步骤 | 工具 | 一句话 | 版本 |
|:---:|---|---|---|
| **⓪** | **CathayRepair（你在这里）** | PDF 打不开、一翻就崩 → 先把它抢救回来 | **v1.0.0** |
| ① | [CathayPDG](https://github.com/zzhjim02/CathayPDG) | 读秀 / 超星的 PDG 压缩包 → PDF | v0.1.9 |
| ② | [CathayOCR](https://github.com/zzhjim02/CathayOCR) | 扫描件做 OCR → 能搜索、能复制的 PDF | v1.2.4 |
| ③ | [CathayRestore](https://github.com/zzhjim02/CathayRestore) | 把 OCR 出来的 TXT 写回 PDF，做成双层 | v1.0.0 |
| ④ | [CathayExtract](https://github.com/zzhjim02/CathayExtract) | 已经是双层 PDF → 直接把文字抽成 TXT | v1.2.3 |
| ⑤ | [CathayShelf](https://github.com/zzhjim02/CathayShelf) | 批量建档归位、规范命名、繁简转换 | v0.4.7 |
| ⑥ | [CathayFinder](https://github.com/zzhjim02/CathayFinder) | 11 个渠道查这本书在哪（找书号 / 找路径） | v1.1.0 |
| ⑦ | [CathayHub](https://github.com/zzhjim02/CathayHub) | **索引 + 全库检索 + 浏览阅读，四合一的日常入口** | v0.3.16 |

> 🧭 **最常用的一条线**：⑥ 查到书 → ① 转成 PDF → ② 让它能搜 → ⑤ 著录归架 → ⑦ 检索、翻开。
> 每一步都能单独用，不强制串起来；整套**纯本地、不联网、不动你的原件**。

**已成历史（功能已并入后面的工具，代码还能跑）**

| 工具 | 现状 |
|---|---|
| [CathayIndex](https://github.com/zzhjim02/CathayIndex) | 已并入 ⑥ CathayFinder 的「本地文件库索引」页签，以及 ⑦ CathayHub Indexer |
| [CathayViewer](https://github.com/zzhjim02/CathayViewer) | 已并入 ⑦ CathayHub Viewer |
| [CathayReader](https://github.com/zzhjim02/CathayReader) | 已由 ⑦ CathayHub Viewer 取代 |
| [CathaySimplify](https://github.com/zzhjim02/CathaySimplify) | 已并入 ⑤ CathayShelf 的「繁简转换 / 编码规范化」 |

---

## ❓ 这个仓库是什么？

扫描/下载来的 PDF 经常有毛病：某页对象损坏、页码对不上、用阅读器打开就崩。
本工具的做法很朴素但很有效：**把原 PDF 一页一页地复制到一个新文件里**，遇到读不出来的页就跳过并记进日志，
最后输出一个「能正常打开、内容尽量完整」的新 PDF。

## ✨ 功能特性

- **逐页抢救**：坏页跳过不中断，日志里明确写出是哪几页没救回来
- **绝不改动原件**：只读源文件，输出 `原名_repaired.pdf`（后缀可在界面改）
- **递归扫描**：拖一个文件夹进来，子目录里的 PDF 全部处理
- **批量 + 多线程**：可设并行数（默认 4），一次修一整批
- **产物识别**：已经是修复产物的文件自动标「无需处理」，重复跑不会套娃
- **坏到没法解析的**：标红「需人工」，绝不瞎猜
- **修复日志**：每个文件成功几页、失败哪几页，一目了然
- **图形界面**：拖放即可，勾选行只修想修的那几个（不选=全部）

## 🚀 一分钟快速上手

1. 双击 **`修复.bat`**（便携版自带运行时；也会自动回退到系统 Python）
2. 把 PDF 或整个文件夹**拖进窗口**（也可点「选择文件夹」）
3. 点 **扫描** —— 列表会显示每个 PDF 的页数与状态
4. （可选）改输出后缀、勾选「覆盖已存在的产物」、调并行数
5. 点 **开始修复**（只修选中行；不选=全部），完成后看日志

## 📂 输出规则（重要）

| 项目 | 规则 |
|:----|:----|
| 输出位置 | 与源文件**同目录** |
| 输出文件名 | `原名` + 后缀（默认 `_repaired`）+ `.pdf`，例如 `宋史_志.pdf → 宋史_志_repaired.pdf` |
| 原件 | **不修改、不删除、不移动** |
| 已存在同名产物 | 默认**跳过**（可在界面勾选「覆盖」） |
| 修复日志 | 界面日志区；命令行方式会写 `修复日志.txt` |
| 保存参数 | `garbage=4, deflate=True, clean=True`（清垃圾对象 + 压缩 + 清理） |

## 📦 下载

> 单文件 EXE 与便携版都**自带运行环境**，解压即用，无需安装任何东西。

| 下载方式 | 链接 |
|:-------|:-----|
| 📥 **百度网盘**（密码 2026） | <待填：百度网盘分享链接> |
| 🐙 **GitHub Releases** | [CathayRepair v1.0.0](https://github.com/zzhjim02/CathayRepair/releases/tag/v1.0.0)（Assets 里直接下 `CathayRepair.exe`） |
| 🧰 **便携版（本仓库源码 + runtime）** | 解压后双击 `修复.bat`（自带 `runtime\`） |

## 🖥️ 系统要求

| 项目 | 最低 | 推荐 |
|:----|:----|:----|
| 系统 | Windows 10 64 位 | Windows 10/11 64 位 |
| 内存 | 4 GB | 8 GB 以上 |
| 磁盘 | 200 MB（便携版） | 500 MB 以上 |
| 其他 | 无需 Python、无需联网 | — |

## 🧑💻 从源码运行 / 命令行用法

```bash
pip install pymupdf
python gui.py                                    # 图形界面
python repair.py 某目录 --out _repaired          # 命令行批量修复
python repair.py 某文件.pdf --out _fixed         # 单个文件，自定义后缀
python gui.py --selftest                         # 环境自检（写 _selftest.txt）

# 打包单文件 EXE
pyinstaller --onefile --windowed --icon app.ico --name CathayRepair gui.py
```

## 📁 文件结构

```
CathayRepair-DEV\
├── repair.py         # 引擎：扫描 / 逐页修复 / 报告
├── gui.py            # 图形界面（tkinter，支持拖放）
├── 修复.bat          # 双击启动（优先自带运行时）
├── runtime\          # 便携 Python 运行时（免安装，自带 PyMuPDF）
├── app.ico           # 图标
└── README.md
```

## ❓ 常见问题

<details>
<summary>修好的文件页数比原来少？</summary>

说明少掉的那些页**物理数据已经损坏**，任何工具都救不回来。日志里会列出失败页号，可以从别处的备份补齐。
</details>

<details>
<summary>为什么不做「深度修复」？</summary>

PDF 一旦对象层级损坏，重建结构有把可读页也一起毁掉的风险。逐页复制是**最安全**的策略：能救的救，救不了的明确标出来。
</details>

<details>
<summary>会动我的原文件吗？</summary>

不会。全程只读原件，输出是新文件。
</details>

## 📝 更新日志

- **v1.0.0**：首版独立软件。基于逐页复制策略（源头是「PDF 损伤修复工具」脚本），新增图形界面、递归扫描、批量多线程、产物识别、修复日志与自检；并入 Cathay 工具链并采用 **GPL-3.0**

## ⚖️ 许可

[GPL-3.0](LICENSE) © 2026
