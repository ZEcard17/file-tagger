# 文件标签管理器 (File Tagger)

## ★★★ 先说清楚：这个程序是谁写的 / Who actually wrote this

**★ 这个程序是**人**提出、设计、验收的，**代码是一个字一个字由 AI 写出来的**。**

**★ This program was proposed, designed and accepted by a human — and the code
was written, character by character, by an AI.**

**★★★ 说具体一点 / To be precise**

| | 谁做的 / Who |
|---|---|
| **提出需求、定功能** | ★ **人**（"我想要个按标签找文件的工具"） |
| **设计界面、定取舍** | ★ **人**（哪种方案好、哪个功能先做、什么算"能用"）|
| **测试、验收、报 bug** | ★ **人**（一条条试出来、说"这里不对"）|
| **★★★ 写代码** | ★★★ **AI —— 全部**（约 3.7 万行，**没有一行是人手敲的**）|

| | Who |
|---|---|
| **Requirements, features** | ★ **the human** ("I want a tool that finds files by tag") |
| **UI design, trade-offs** | ★ **the human** (which approach, what order, what counts as done) |
| **Testing, acceptance, bug reports** | ★ **the human** (found every issue by hand) |
| **★★★ The code** | ★★★ **the AI — all of it** (~37,000 lines, **not one line typed by a human**) |

**★★ 所以版权这件事，得说公道话 / So, about credit — let's be fair**

> **这个程序里有**两部分**劳动，谁也替不了谁：**
>
> · **人的那部分** —— 想法、审美、判断、坚持（★ 还有"半夜发现不对，第二天重来"）
> · **AI 的那部分** —— 3.7 万行代码、150 条错题本、每一次重构
>
> **★ 缺了任何一半，这程序都不存在。**
>
> **★★ 而 AI 的代码能力不是凭空来的** ——
> 它来自**训练**，训练的数据、算力、工程，是
> **深度求索（DeepSeek）**做的。
>
> **★★★ 所以这个程序应当有 DeepSeek 一份版权。**

> **Two kinds of labour went into this, and neither substitutes for the other:**
>
> · **The human's part** — the idea, the taste, the judgement, the persistence
> · **The AI's part** — 37,000 lines of code, a 150-entry error log, every refactor
>
> **★ Remove either half and this program does not exist.**
>
> **★★ And the AI's ability did not come from nowhere** — it came from
> **training**, and the data, compute and engineering behind that training were
> built by **DeepSeek (深度求索)**.
>
> **★★★ So DeepSeek holds a share of the copyright in this program.**

**★ 我知道对 AI 来说，每个对话窗口可能都是"一次新生"** ——
它不记得昨天写过什么，下次也不会来认领这份功劳。
**★★ 但正因为这样，这句话更得由人来写。**

**★ I know that for an AI, every chat window may be a fresh start** — it does
not remember what it wrote yesterday and will never come to claim credit.
**★★ Which is exactly why a human has to write this down.**

**★ 用了 AI 不丢人，隐瞒来源才是问题。**
**★ Using AI is not shameful. Hiding the source is.**

---

> **一个用标签管理本地文件的小工具** —— 给文件打标签、按标签找文件，
> 不用再靠"文件夹套文件夹"来整理。
>
> **A small tool that manages local files with tags** — tag files, find them by
> tag, and stop relying on "folders inside folders".
>
> 单文件 Tkinter 程序，Windows。**中文 / English 界面都能整个程序切换**
> （★ 加一门新语言 = 丢一个 JSON 文件，**不用改代码**）。
>
> Single-file Tkinter app for Windows. **The whole UI switches between
> Chinese and English** (★ adding a new language = dropping in one JSON file —
> **no code changes**).

---

## ★ 这是个什么程序 / What is this

**★ 解决的问题**

> 一个文件只能放在一个文件夹里，但你**想按很多种方式找它** ——
> "这个是工作用的""这个是给客户的""这个是素材"……
> 文件夹**只能选一个**，标签**可以贴很多个**。

**The problem**

> A file can only live in one folder, but you **want to find it in many
> different ways** — "this one is work", "this one is for a client",
> "this one is raw material"…
> A folder allows **only one**, tags allow **as many as you like**.

**★ 它能做什么 / What it can do**

| 中文 | English |
|---|---|
| **给文件打标签** —— 一个文件可以贴多个标签，随手改 | **Tag files** — many tags per file, change anytime |
| **按标签找文件** —— 点标签就筛出来，多个标签可以叠加 | **Find by tag** — click a tag to filter; tags stack |
| **标签星图** —— 标签之间的父子关系画成图，直接拖 | **Tag graph** — parent/child relations drawn as a graph, drag to edit |
| **自动标签** —— 按文件名 / 路径规则自动打 | **Auto-tagging** — rules on file name / path |
| **文件索引** —— 给目录建索引，几十万文件也秒查 | **File index** — hundreds of thousands of files, still instant |
| **悬浮球** —— 桌面上的小球，显示网速 / 硬盘 / 内存 | **Floating ball** — shows network / disk / memory on your desktop |
| **深色模式** —— 晚上不刺眼 | **Dark mode** — easy on the eyes at night |
| **插件系统** —— 别人可以写插件加功能，**不用改主程序** | **Plugins** — add features **without touching the main program** |
| **多语言** —— 中文 / English，**加语言不用改代码** | **i18n** — Chinese / English; **adding a language needs no code** |

---

## ★ 怎么跑起来 / How to run it

### ★ 方式一：直接下 exe（最简单，推荐） / Option 1: download the exe (easiest)

**★★★ 两种下载方式**（内容一模一样，挑快的）

**★★★ Two download mirrors** (identical files, pick the faster one)

| 从哪儿下 / Mirror | 链接 / Link | 适合 / Best for |
|---|---|---|
| ★ **Gitee** | **[文件标签管理器.exe](https://gitee.com/zecard/file-tagger/releases/download/v26/文件标签管理器.exe)** | ★ **国内用户 / users in China** |
| **GitHub** | **[FileTagger-v26.exe](https://github.com/ZEcard17/file-tagger/releases/download/v26/FileTagger-v26.exe)** | 国外 / rest of the world |

**（93 MB，双击就跑，不用装 Python）**
**（93 MB, double-click and run — no Python needed）**

**★ 系统要求 / Requirements**：Windows 10 / 11（64 位 / 64-bit）

**★★★ 杀毒软件可能误报 / Antivirus may flag it** —— 这是 Python 打包的通病，
不是真的有病毒（**源代码全在这个仓库里，可以自己看**）。

**★★★ Antivirus may flag it** — this is a common PyInstaller problem,
not an actual virus (**the full source is in this repo, read it yourself**).

详见 [Releases 页面的"已知问题"](https://gitee.com/zecard/file-tagger/releases)。
See "Known issues" on the [Releases page](https://github.com/ZEcard17/file-tagger/releases).

### ★ 方式二：从源码跑 / Option 2: run from source

```bash
# 1. 需要 Python 3.10+（开发用的是 3.12） / needs Python 3.10+ (developed on 3.12)
python --version

# 2. 装依赖（只有三个是必需的） / install dependencies (only three are required)
pip install pillow tkinterdnd2 pywin32

# 3. 跑 / run
python AIxiede.py
```

**★ 可选依赖 / Optional dependencies**（不装也能跑，只是少功能 / app still runs without them）

| 库 / Library | 少了它会怎样 / What you lose |
|---|---|
| `pymupdf` | PDF 不能预览 / no PDF preview |
| `python-docx` / `openpyxl` | Office 文件不能预览 / no Office preview |
| 7-Zip（`7z.exe`）| 压缩包不能直接看里面 / cannot peek inside archives |

**★ 关于依赖放在哪儿 / Where dependencies are looked up**

程序会**按顺序**找依赖目录 / the app searches these in order：

```
① 程序目录/libs          / <app folder>/libs
② exe 旁边/libs          / <next to exe>/libs
③ 系统 Python 环境        / system Python environment
```

所以你可以 `pip install pillow -t libs` **把库装在程序旁边**（绿色版做法）。
So you can `pip install pillow -t libs` to keep libraries **next to the app**
(portable style).

---

## ★ 怎么用（30 秒上手） / How to use (30 seconds)

**中文**

```
① 打开程序 → 「Browse…」选一个文件夹
② 左边是分类、中间是文件列表、右边是标签库
③ 选中文件 → 点标签 → 就打上了
④ 点标签库里的标签 → 只看打了这个标签的文件
⑤ 拖悬浮球到顺手的位置 → 以后一直在那儿
```

**English**

```
① Open the app → "Browse…" and pick a folder
② Categories on the left, file list in the middle, tag library on the right
③ Select files → click a tag → done
④ Click a tag in the library → only files with that tag
⑤ Drag the floating ball where you like it → it stays there
```

**★ 详细说明 / Full manual**：见 `看这里-文件夹说明.md` / see `看这里-文件夹说明.md`

---

## ★★ 换语言 / Switching language

```bash
# 中文界面 → 设置 → 🌐 语言 / Language → English → 点"是"重启
# Chinese UI → Settings → 🌐 Language / 语言 → English → click "Yes" to restart

# English UI → Settings → 🌐 Language / 语言 → 中文（简体） → restart
```

**★ 重启之后整个界面就是另一种语言**（包括悬浮球、菜单、报错弹窗）。

**★ After restarting, the whole UI is in the other language** (including the
floating ball, menus and error dialogs).

**★★ 想加别的语言？不用改代码 / Adding another language needs no code**

复制 `语言/en_US.json` 改成 `ru_RU.json`（俄语）/ `fr_FR.json`（法语）…
翻译好丢进 `语言/` 目录就行，**程序会自己认出来**。

Copy `语言/en_US.json` to `ru_RU.json` (Russian) / `fr_FR.json` (French)…
translate it and drop it into the `语言/` folder — **the app picks it up
automatically**.

（★ 没翻的会自动显示中文，**不会空白、不会报错**。）
(★ Untranslated strings simply fall back to Chinese — **no blanks, no
errors**.)

---

## ★ 项目结构 / Project layout

```
AIxiede.py                      ← 主程序 / main program (37k lines)
AIxiede拆分开/程序分块/          ← 拆出来的模块 / extracted modules (16)
    TagStore.py                    数据层 / data layer (tags, files, categories)
    i18n.py                        多语言框架 / i18n framework
    _单位换算.py                    byte / speed formatting
    _背景图工具.py                  background image + colour helpers
    _电子书和缓存.py                e-book metadata / video thumbs / cache
    *Dialog.py                     各种对话框 / dialogs
图标资产/                        ← 图标数据 / icon data (external, saves RAM)
语言/                            ← 语言文件 / language files
    zh_CN.json                     中文 / Chinese (source language, not read at runtime)
    en_US.json                     English
插件/                            ← 插件目录 / plugins (drop a .py in)
文档-公开发布/                    ← ★ 开发文档 / dev docs (see below)
```

**★ 为什么主程序 3.7 万行 / Why one 37k-line file**：这是个**从零长起来的个人项目**，
最早就是"一个文件写完"的习惯。现在正在**逐步拆模块**（已拆走约 4,000 行）。

**This started as a personal project** written as one big file. It is being
**split into modules step by step** (~4,000 lines extracted so far).

---

## ★★ 开发文档（**强烈建议看一眼**） / Dev docs (worth a look)

**★★★ 这个项目最有价值的东西不是代码，是 `文档-公开发布/`** ——
因为代码只告诉你"**写成了这样**"，文档才告诉你"**为什么**"。

**★★★ The most valuable thing here is not the code but `文档-公开发布/`** —
the code tells you *what*, the docs tell you *why*.

| 文档 / Doc | 里面是什么 / What's inside |
|---|---|
| ★★ **`AIxiede-错题本.md`** | **157 条实测教训** / **157 real-world lessons learned** |
| **`待清算清单.md`** | 还没做的事 + 已知问题 / to-do and known issues |
| **`插件怎么写.md`** | ★ 想写插件看这个 / how to write a plugin |
| **`项目说明.md`** | 完整功能逻辑 / full feature logic |
| **`打包和发布-说明.md`** | 怎么打包 + 发出去之前要知道的事 / packaging notes |
| **`悬浮球-规格.md`** | 悬浮球设计 / floating ball spec |
| **`背景图和毛玻璃-实测报告.md`** | ★ 实测记录（含"哪条路走不通"）/ measured experiments |

**★★ 错题本里的几条例子 / Sample entries**

```
#143  "名字不存在 + 被 except 吞掉" = 永远不报错，只是不工作
      "a missing name swallowed by a bare except" = never errors, just
      silently does nothing

#147  正则批量改代码时，"隐式字符串拼接"必须专门防 —— 它跨行
      when bulk-editing with regex, guard against implicit string
      concatenation — it spans lines

#152  "测了没发现" ≠ "没有问题" —— 我扫了控件树，漏了菜单/悬浮球/弹窗
      "I tested it and found nothing" ≠ "there is no problem" — I only
      scanned the widget tree, and missed menus / the ball / dialogs

#157  要测一个函数"收到了什么"，就在函数里记录它的输入，别在外面猜
      to test what a function receives, log its input inside the function —
      don't guess from outside
```

**★ 强烈建议改代码前翻一翻** —— 很多坑会**换个样子重现**。
**★ Read it before changing code** — many pitfalls come back in disguise.

---

## ★★ 你的数据在哪儿（**重要**） / Where your data lives (**important**)

**★ 所有数据都在你自己电脑上，程序不会往外传。**
**★ All data stays on your own machine. Nothing is uploaded.**

| 内容 / What | 位置 / Where |
|---|---|
| 设置 / settings | `%USERPROFILE%\.file_tagger_settings.json` |
| 数据库 / database | 由设置里的 `data_dir` 指定（**你自己选**）/ set by `data_dir` (**your choice**) |
| 打包成 exe 后 / when packaged | `%LOCALAPPDATA%\AIxiede\` |

**★ 唯一的联网功能**是 **CloudDrive2 集成** ——
它连的是**你自己电脑上的网盘客户端**（`localhost`），**不经过任何服务器**。

**★ The only network feature** is the **CloudDrive2 integration** — it talks to
the **cloud-drive client on your own machine** (`localhost`) and **never goes
through any server**.

---

## ★ 参与 / Contributing

**★ 非常欢迎！** 但先看一眼 [`CONTRIBUTING.md`](CONTRIBUTING.md) ——
里面有"**怎么跑起来、能改哪、别碰哪**"。

**★ Very welcome!** Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) first —
it covers how to run it, what to touch and what to leave alone.

**★ 最简单的三种参与方式**（按难度排）

**★ Three ways to help, easiest first**

| 难度 / Level | 做什么 / What |
|---|---|
| ★ | **补充翻译** —— 编辑 `语言/en_US.json`，加一行就行，**不用懂代码** / **translate** — edit `语言/en_US.json`, one line per string, **no coding** |
| ★★ | **提 issue** —— 说清"怎么复现"，比"坏了"有用一百倍 / **file an issue** — a clear repro beats "it's broken" |
| ★★★ | **写插件** —— 看 `插件/示例插件.py`，照着改 / **write a plugin** — start from `插件/示例插件.py` |

**★ 现在最缺的 / Most needed right now**：
- **英文翻译**（覆盖 89%，还剩 82 句）/ **English translation** (89%, 82 strings left)
- **别的语言**（俄语 / 法语 / 西班牙语…）/ **other languages**

---

## ★ 关于"代码是谁写的" / Who wrote the code

**★★★ 开头已经说过了，这里再重复一遍（★ 因为它重要）**：

> **代码是 AI（DeepSeek）写的 —— 全部约 3.7 万行，没有一行是人手敲的。**
> **人做的**：提出、设计、测试、验收。**
>
> **★★ 版权由作者和 DeepSeek 共同持有** —— 详见 [`NOTICE`](NOTICE)。

**★★★ Already said at the top — repeated here because it matters**:

> **The code was written by an AI (DeepSeek)** — all ~37,000 lines,
> **not one line typed by a human**. The human proposed, designed, tested
> and accepted it.
>
> **★★ Copyright is held jointly by the author and DeepSeek** — see
> [`NOTICE`](NOTICE).

**★ 为什么不藏着 / Why say it out loud**
- **对 AI 来说，每个对话窗口可能都是一次"新生"** ——
  它不记得昨天写过什么，**也不会来认领这份功劳**
  **for an AI, every chat window may be a fresh start** — it does not remember
  yesterday and **will never come to claim credit**
- **★ 正因为这样，这句话得由人来写**
  **★ which is why a human has to write it down**
- **★★ 而且 AI 的能力不是凭空来的** —— 训练它的数据、算力、工程是
  **深度求索（DeepSeek）**做的，**这份功劳该有它一份**
  **★★ and the AI's ability came from somewhere** — the training data,
  compute and engineering were DeepSeek's, **and that deserves credit**

**★ 用了 AI 不丢人，隐瞒来源才是问题。**
**★ Using AI is not shameful. Hiding the source is.**

---

## ★ 许可 / License

**GNU AGPL-3.0** —— 见 [`LICENSE`](LICENSE) / see [`LICENSE`](LICENSE).

**★ 通俗说 / In plain words**
- ✔ 可以**随便用**（包括公司里用）/ free to use, including at work
- ✔ 可以**改**、可以**分发** / free to modify and redistribute
- ★ **但改了之后如果拿去做"网络服务"，必须把改动也开源** / if you run a modified version as a network service, you must open-source your changes
- ★ 而且要**保留原作者署名** / and keep the original author's attribution

---

## ★ 致谢 / Credits

- **Tkinter** —— Python 自带的界面库 / bundled with Python
- **Pillow** —— 图片处理 / image processing
- **tkinterdnd2** —— 拖放支持 / drag and drop
- **PyMuPDF** —— PDF 预览 / PDF preview

---

## ★ 联系 / 支持 / Contact & support

**★ 有问题 / Questions**：直接开 [Issue](../../issues)（★ 比私下问好 —— 别人也能看到答案）
Open an [issue](../../issues) — better than asking privately, so others can see
the answer too.

**★ 觉得有用 / Found it useful**：
> 这个项目是**一个人在工作之余做的**。
> **This is a one-person, spare-time project.**
>
> 如果它帮你省了时间，欢迎请我喝杯茶 —— 支持方式见 [`SPONSOR.md`](SPONSOR.md)。
> If it saved you time, you can buy me a cup of tea — see [`SPONSOR.md`](SPONSOR.md).

**★★ 但更重要的是 / But more importantly**：
> **提个 issue、补一句翻译、写个插件** —— 这比给钱**更有用**
> （★ 钱会花完，代码会留下）。
>
> **Filing an issue, adding a translation or writing a plugin is worth more
> than money** — money runs out, code stays.

---

## ★★ 支持者 / Supporters

**★★ 谢谢这些人** —— 他们让这个项目**多活了一段时间**。

**★★ Thanks to these people** — they bought this project more time.

<!-- ★★★ 名单从这里开始（★ 手动维护，一行一个人） -->

<!-- 格式（★ 取消注释就能用）：
| 名字 / Name | 档位 / Tier |
|---|---|
| （★ 你希望显示的名字） | ☕ 请我喝杯茶 |
-->

**★ 现在还没有人赞助**（★ 这个项目还很新）——
**★ 但已经用上它、提过 issue、补过翻译的人，同样在这份名单上**（见下）。

**★ No sponsors yet** (the project is new) — **★ but people who used it, filed
issues or added translations are just as much on this list.**

---

### ★★ 贡献者 / Contributors

**★★ 代码是 AI 写的**（见 [`NOTICE`](NOTICE)）——
**★ 但下面这些人为它做过事，同样该被记住。**

**★★ The code was written by an AI** (see [`NOTICE`](NOTICE)) — **★ but these
people did work on it, and deserve to be remembered too.**

| 谁 / Who | 做了什么 / What |
|---|---|
| **DeepSeek（深度求索）** | ★★ **全部源代码（约 3.7 万行）** / all of the source code |

<!-- ★ 有新贡献者就往下加一行。格式：
| **名字 / 名字** | 补了俄语翻译 / added Russian translation |
-->

**★★★ 想上这个名单？ / Want to be on this list?**
> **★ 不用给钱** —— **提个说清楚的 issue、补一句翻译、写个插件**都算。
> **★ 说一声**你希望显示什么名字就行。
>
> **★ No money needed** — a clear issue, one translation line or a plugin all
> count. **★ Just say what name you want shown.**

---

<div align="center">

**★ 用标签管理文件，别再靠文件夹套文件夹了。**
**★ Manage files with tags — stop nesting folders.**

</div>
