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

| 顺序 | 工具 | 干什么 | 状态 |
|:---:|---|---|---|
| ① | [**CathayIndex**](https://github.com/zzhjim02/CathayIndex) | 把本地文件夹（含子目录、孙目录）扫成「本地文件库」 | v1.0.0 |
| ② | [**CathayFinder**](https://github.com/zzhjim02/CathayFinder) | 综合性图书检索引擎：11 个渠道，按书名 / 作者 / 出版者 / SSID 精准查 | v1.0.0 |
| ③ | [**CathayOCR**](https://github.com/zzhjim02/CathayOCR) | 多引擎 GPU 加速古籍 PDF 批处理 OCR | v1.2.4 |
| ④ | [**CathayShelf**](https://github.com/zzhjim02/CathayShelf) | 自动著录建夹 / 产物后缀替换 / 繁简转换（已整合 CathaySimplify） | v0.4.5 |
| ⑤ | [**CathayReader**](https://github.com/zzhjim02/CathayReader) | PDF/TXT 双栏同步古籍校勘阅读器 | v1.0.0 |

**备用软件（四个，按需取用）**

| 工具 | 干什么 | 状态 |
|---|---|---|
| **CathayRepair（你在这里）** | 先把损坏的 PDF 修好（③ OCR 前可选） | v1.0.0 |
| [**CathayRestore**](https://github.com/zzhjim02/CathayRestore) | 把 OCR 文本写回 PDF 文字层（③ OCR 之后可选） | v1.0.0 |
| [**CathayExtract**](https://github.com/zzhjim02/CathayExtract) | 已有双层 PDF → 直接提取文字层成 TXT（③ 的替代入口） | v1.2.3 |
| [**CathaySimplify**](https://github.com/zzhjim02/CathaySimplify) | TXT 繁简体转换 + 编码规范化（功能已并入 ④ CathayShelf） | v1.0.0 |

> 🧭 **主线一句话：** `CathayIndex` 建本地库 → `CathayFinder` 查书（找 SSID / 路径） → `CathayOCR` 识别 → `CathayShelf` 著录归架 → `CathayReader` 双栏校勘

> 📌 **这是本仓库（CathayRepair）** — 备用软件：坏 PDF 先修，修好的副本再进 ③ CathayOCR 跑识别。

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
