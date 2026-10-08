# 贡献指南 / Contributing

> **★ 先谢谢你想帮忙！**
> **★ Thanks for wanting to help!**
>
> **★ 不管你是"完全不懂代码"还是"老手"，这个文件里都有你能做的事。**
> **★ Whether you have never written code or you are a veteran, there is
> something for you here.**

---

## ★★★ 第一次参与？从这里开始 / First time? Start here

**★★★ 你**不需要**读完整个主程序（1.6 万行，拆成 53 个模块）。**

**★★★ You do **not** need to read the whole main file** (16k lines, 53 modules).**

**★ 我知道那个主程序看起来吓人** —— 一个人写的、原来 37,000 行单文件（★ 现在已拆成 53 个模块，主程序 1.6 万行）。
**★ 但这不代表"改东西很贵"** —— 我们做了**路标**：

**★ I know the main file looks intimidating** — one person, one file,
37,000 lines originally (**now 53 modules, 16k-line main file**). **★ But that does not mean changes are expensive** — there are
signposts:

| 文件 / File | 里面是什么 / What's inside |
|---|---|
| ★★ **[`架构图.md`](文档-公开发布/架构图.md)** | **每个类/每个入口在第几行** —— 想改什么，翻到那一行 |
| ★★ **[`改这里就行.md`](文档-公开发布/改这里就行.md)** | **最常见的 10 种改动**：改哪、怎么改、注意什么 |

**★★★ 而且有三件事**一行主程序都不用碰****：

**★★★ And three kinds of work touch none of it:**

| 想做什么 / To do | 改哪儿 / Where | 门槛 / Level |
|---|---|---|
| ★★ **补翻译 / 加一门语言** | `语言/en_US.json`（**加一行就行**）| ★ **完全不用懂代码** |
| ★★ **加个功能** | `插件/我的插件.py`（照抄示例）| ★★ 会一点 Python |
| ★ **提个说清楚的 issue** | 用 issue 模板 | ★ **什么都不用会** |

**★★ 一句话**：
> **★ 这项目最缺的不是 PR，是"有人在用、有人说话"。**
> **★ 你提一个说清楚的 issue，比提一个 PR 更有用。**

**★★ In one line:**
> **★ What this project lacks is not PRs — it is people using it and
> speaking up.**
> **★ A clear issue is worth more than a PR.**

---

## ★ 目录 / Contents

- [零、先读这段（很重要）](#零先读这段很重要--read-this-first)
- [一、最简单的参与：补翻译](#一最简单的参与补翻译--easiest-translate)
- [二、报 bug / 提需求](#二报-bug--提需求--bugs--feature-requests)
- [三、改代码（提 PR）](#三改代码提-pr--code-changes-pull-requests)
- [四、写插件](#四写插件--plugins)
- [五、这个项目的"脾气"](#五这个项目的脾气--the-houses-rules)
- [六、绝对不能碰的东西](#六绝对不能碰的东西--never-touch)

---

## 零、先读这段（很重要） / Read this first

### ★ 这个项目有什么特别的 / What makes this project unusual

**★★ 它是个"从零长起来的个人项目"** —— 主程序**曾经 3.7 万行在一个文件里**（★ 现在拆成 53 个模块，主程序 1.6 万行）。
这不是好习惯，但**已经这样了**，现在正在**慢慢拆**。

**★★ It is a personal project that grew from scratch** — the main program is
**37k lines in a single file**. Not a great habit, but that is how it started,
and it is being **split up gradually**.

**★ 所以你会看到 / So you will notice**：
- 大量**中文注释**（★ 而且注释写得比代码还细 —— 这是刻意的）
  **a lot of Chinese comments** (deliberately more detailed than the code)
- 注释里会写 **"为什么这么改"**、**"踩过什么坑"**
  comments explain **why** and **what went wrong before**
- ★ **代码风格不统一**（不同时期写的）
  ★ **inconsistent style** (written over a long period)

**★★★ 一条最重要的话 / The single most important thing**：
> **这个项目的**注释**和**错题本**，比代码本身更值钱。**
> 因为它们记录了"**为什么**"，而不只是"**是什么**"。

> **The comments and the error log are worth more than the code itself**,
> because they record **why**, not just **what**.

### ★ 作者是个什么样的人 / Who the author is

**★★★ 先把最重要的事说清楚 / The most important thing first**：
> **这个程序的**代码**是 AI（DeepSeek）写的** ——
> **全部约 3.7 万行，没有一行是人手敲的。**
> **人做的是**提出、设计、测试、验收**。**
>
> 详见 [`NOTICE`](NOTICE)（版权与来源声明）。

> **The code was written by an AI (DeepSeek)** — all ~37,000 lines,
> **not one typed by a human**. The human proposed, designed, tested and
> accepted it. See [`NOTICE`](NOTICE).

**★ 具体分工 / The split**

| 做了什么 / What | 谁 / Who |
|---|---|
| 提出需求、定功能 / requirements | ★ **人 / the human** |
| 设计界面、定取舍 / design, trade-offs | ★ **人 / the human** |
| 测试、验收、报问题 / testing, bug reports | ★ **人 / the human** |
| ★★★ **写代码（3.7 万行）** / ★★★ **all the code** | ★★★ **AI（DeepSeek）** |

**★★ 所以 / Therefore**：
- **别看不起这个项目** —— 它是**一个人业余时间**一点点磨出来的
  **don't look down on it** — it was ground out in someone's spare time
- ★ **也别小看"提需求"这件事** —— 3.7 万行代码里每一个取舍都是人定的
  ★ **and don't underestimate the "just asking for it" part** — every one of
  the trade-offs behind those 37k lines was a human decision
- **也别客气** —— 有问题直说，**说清楚比说好听有用**
  **and don't be shy** — being clear beats being polite

**★★ 版权归属 / Copyright**：作者 + **DeepSeek**。
**★ 你贡献的代码，同样会被记在这里。**
**★★ Attribution**: the author **and DeepSeek**. **★ Your contributions will be
recorded here too.**

---

## 一、最简单的参与：补翻译 / Easiest: translate

**★★★ 这是"投入产出比最高"的贡献方式。**
**★★★ This gives the most value for the least effort.**

**★ 现在的情况 / Current state**：界面有约 **760 句**中文，**英文覆盖 89%**。
The UI has about **760 Chinese strings**; **English coverage is 89%**.

### 怎么做（3 步） / How to do it (3 steps)

**① 打开 `语言/en_US.json`**，你会看到这样的内容 / open it and you will see：
```json
{
  "_label": "English",
  "取消": "Cancel",
  "确定": "OK",
  "刷新": "Refresh"
}
```

**② 加一行**（左边是中文原文，右边是你的翻译）
**② add one line** (Chinese on the left, your translation on the right)：
```json
  "标签盒": "Tag box",
```

**★ 注意 / Watch out**：
- 前面那个中文**必须跟程序里的完全一样**（一个字都不能差）
  the Chinese key **must match the program exactly**
- 最后要有**逗号**（除非是最后一行）
  keep the **trailing comma** (except on the last line)
- ★ **不要动** `_` 开头的键（那是给程序看的）
  ★ **do not touch** keys starting with `_` (those are for the program)

**③ 存盘、重开程序、切到 English 看效果**
**③ save, restart the app, switch to English and check**

### ★ 怎么知道"还差哪些" / How to see what is missing

```bash
python AIxiede.py --i18n-check
```

**★ 会告诉你**：现在翻了百分之多少、**每个分类还差多少**。
**★ It tells you** the coverage percentage and what is missing per category.

### ★★ 三条规矩 / Three rules

| 规矩 / Rule | 为什么 / Why |
|---|---|
| **保留 `%d` / `%s` 占位符** / keep `%d` / `%s` placeholders | 那是"要塞数字进去"的地方，删了会出错 / deleting them breaks formatting |
| **保留 emoji**（`🎨` `🗃`）/ keep emoji | 它是界面的一部分 / they are part of the UI |
| ★ **翻译"意思"，不是"字面"** / translate the **meaning** | 界面上的字要**短、准、像本国人说的话** / UI text should be short and natural |

**★ 例 / Example**：
```
✔ 好的翻译 / good:  "重命名…"  →  "Rename…"
★ 差的翻译 / bad:   "重命名…"  →  "Again give a name…"   (word-for-word)
```

### ★ 想加一门新语言？ / Want to add a new language?

**★★ 不用改任何代码！** / **★★ No code changes needed!**

1. **复制** `语言/en_US.json` / **copy** it
2. **改名**成你的语言代码，比如 `ru_RU.json`（俄语）、`fr_FR.json`（法语）
   **rename** it to your language code, e.g. `ru_RU.json`, `fr_FR.json`
   （★ 格式：`语言代码_国家代码`，[看这里](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)）
3. **改第一行** / **change the first line**：
   ```json
   {
     "_label": "Русский",
   ```
4. **翻译**（慢慢来 —— **★ 没翻的会自动显示中文**，不会坏）
   **translate** (take your time — **★ untranslated strings fall back to
   Chinese**, nothing breaks)
5. **重启程序** → 「设置 → 🌐 语言」里**就有你的语言了**
   **restart** → your language appears under **Settings → 🌐 Language**

**★ 真的不用改代码。** 程序是**扫描这个目录**的。
**★ Really, no code changes.** The app **scans that folder**.

---

## 二、报 bug / 提需求 / Bugs & feature requests

### ★★ 一条铁律：**说清楚"怎么复现"**
### ★★ One iron rule: **describe how to reproduce it**

**★ 对比一下 / Compare**：

```
★ 差的 issue / bad:
   标题 / title: 程序坏了 / it's broken
   内容 / body:  打不开，快修 / won't open, fix it

★★ 好的 issue / good:
   标题 / title: 从网盘目录打开时，文件列表一直转圈不出现
                 / file list spins forever when opening a cloud folder
   环境 / env:   Windows 10 / Python 3.12 / 网盘是 CloudDrive2
   步骤 / steps:
     1. 用 CloudDrive2 挂载一个网盘 / mount a cloud drive with CloudDrive2
     2. 在程序里浏览到 \\CloudDrive\百度网盘\某目录 / browse to a folder there
     3. 等 30 秒 —— 列表一直是空的 / wait 30s — the list stays empty
   期望 / expected: 应该显示文件 / files should appear
   实际 / actual:   一直转圈 / it keeps spinning
   补充 / notes:    直接看本地目录没问题；日志里有"UNC 路径超时"
                    / local folders are fine; the log shows a UNC timeout
```

**★ 为什么"复现步骤"这么重要 / Why repro steps matter**：
> 作者**不在你的电脑前**。没有步骤，他**只能猜** ——
> 而猜测**十次有九次是错的**（然后你会觉得"他不理我"）。
>
> The author **is not sitting at your machine**. Without steps they can only
> guess — and guesses are wrong nine times out of ten.

### ★ issue 模板会提示你要填什么 / Templates will guide you

提 issue 时**照着模板填**就行（模板会自动出现）。
The templates appear automatically when you open an issue.

### ★★ 提需求的时候 / When requesting a feature

**★ 说"你要解决什么问题"，别只说"加个功能"**
**★ Describe the problem, not just "add a feature"**

```
★ 差 / bad:  "加个批量重命名功能" / "add batch rename"
★★ 好 / good: "我有 300 个照片想按拍摄日期改名，现在得一个个改。
              希望能选中一批、按规则批量改名。"
              / "I have 300 photos I want renamed by capture date. Right now
              it is one by one. I would like to select a batch and rename them
              by a rule."
```

**★ 为什么 / Why**：作者可能**有更好的办法**解决你那个"问题" ——
但如果他只看到"加个功能"，就**只能照做**（哪怕不是最优解）。

The author may know a **better way** to solve your actual problem — but if they
only see "add a feature", they can only do exactly that.

---

## 三、改代码（提 PR） / Code changes (pull requests)

### ★★ 先看这段（不然你的 PR 可能白写）
### ★★ Read this first (or your PR may be wasted)

**★★★ 这个项目有"几个特别的规矩"，不照做的话代码会坏。**
**★★★ This project has a few hard rules. Ignoring them breaks things.**

### 规矩 1：**改之前先备份** / Rule 1: back up before editing

项目习惯：改之前把 `AIxiede.py` 复制一份到 `备份/`，
**文件名里带"好用的"**（比如 `AIxiede.py.bak-加夜间模式-好用的-20261006`）。

The convention: copy `AIxiede.py` into `备份/` first, and put **"好用的"**
("known-good") in the file name.

**★ 为什么 / Why**：这是**个人项目**，没有 CI、没有回滚机制。
**"随时能退回上一个能用的版本"是唯一的安全网。**

There is **no CI and no rollback**. Being able to return to the last working
version **is the only safety net**.

### 规矩 2：**改完必须跑检查** / Rule 2: run the checks after editing

```bash
# ① 语法 + 中文引号检查（★ 开发时踩过 7 次这个坑）
python 测试残留/查中文引号.py AIxiede.py

# ② 程序结构检查（防止"不小心把大类拆散了"）
python 核对结构.py

# ③ 全面回归（自动点一遍所有菜单，看会不会崩）
python reg2.py
```

**★ 这三个脚本在 `测试残留/` 里**（那个目录不进版本库，
但**它们是这个项目的"测试套件"**）。

Those three scripts live in `测试残留/` (not in the repo, but they are this
project's test suite).

### 规矩 3：**`tk.Text` / `tk.Listbox` 一定要给 `width`**
### Rule 3: always give `tk.Text` / `tk.Listbox` a `width`

```python
# ★ 错的 / bad（默认 80 字符宽 ≈ 884 像素 → 窗口"莫名其妙很宽"）
tk.Text(parent)

# ✔ 对的 / good
tk.Text(parent, width=48)
```

**★ 这是这个项目**踩过最多的坑**。**
**★ This is the most frequently hit pitfall in this project.**

### 规矩 4：**"看起来成比例"的东西，不能用像素写死**
### Rule 4: never hard-code pixel sizes for proportion-based layout

```python
# ★ 错的 / bad（换个缩放比例就错位）
pad = 6

# ✔ 对的 / good（跟着字体行高走）
pad = max(2, linespace // 6)
```

### 规矩 5：**★ 加新东西的时候，顺手"留个接口"**
### Rule 5: ★ leave extension points when adding features

**★★ 这是作者特别强调的一条 / The author stresses this one**：

> 「你写程序要不多设点**冗余**吧，留点**接口**什么的，
> 以后方便改方便用，虽然这事可能跟我是善变的有关」
>
> "Leave a bit of **redundancy** and some **extension points** —
> it makes future changes easier, even if that is partly because I change my
> mind a lot."

**★ 什么意思 / What it means**：
- 加"皮肤" → **顺便留"自定义皮肤注册"的入口**（别写死两种）
  adding themes → also add a **theme registration hook** (don't hard-code two)
- 加"菜单" → **顺便留"插件加菜单项"的入口**
  adding menus → also add a **plugin menu hook**
- 加"语言" → **顺便留"加一门语言就是加个文件"的机制**
  adding languages → make it **"one file per language"**

**★ 判据 / The test**：**"以后想改这个，要不要动源码？"**
要动 → **就说明接口没留好。**
**"Will a future change require editing the source?"** If yes, the extension
point is missing.

### 规矩 6：**注释要写"为什么"** / Rule 6: comments explain **why**

```python
# ★ 差的注释 / bad
# 设置超时 30 秒 / set timeout to 30s
conn = sqlite3.connect(path, timeout=30.0)

# ✔ 好的注释 / good（这项目里的真实例子 / a real example from this project）
# ★ v26 全功能巡检：原来没设等锁时间。而程序后台有很多线程
#   也在写同一个库。只要恰好撞上，主界面一个操作就会直接报：
#     sqlite3.OperationalError: database table is locked
#   （实测能复现：起窗口后连点几下就撞上了。）
#   修法：① timeout=30 —— 锁了就等 30 秒而不是立刻报错；
#         ② 开 WAL —— 读和写可以同时进行，根本不再互相堵。
conn = sqlite3.connect(path, timeout=30.0)
```

### ★ PR 流程 / PR workflow

```
① Fork 这个仓库 / fork the repo
② 建个分支（名字随意）/ create a branch (any name)
③ 改代码（★ 照着上面 6 条规矩）/ make your changes (follow the 6 rules)
④ 跑那三个检查 / run the three checks
⑤ 提 PR —— ★ 描述里说清"改了什么、为什么、怎么验证的"
   open the PR — say what changed, why, and how you verified it
```

**★★ 别怕 PR 被拒** —— 作者会**告诉你为什么**，而不是直接关掉。
**★★ Don't fear rejection** — the author will **tell you why**, not just close
it.

---

## 四、写插件 / Plugins

**★★ 这是"扩展这个程序"的**正确姿势** —— 不用碰主程序一行代码。**
**★★ This is the right way to extend the app — without touching the main
program.**

### 最短的插件（5 行） / The shortest possible plugin

新建 `插件/我的插件.py` / create `插件/我的插件.py`：
```python
def register(api):
    api.add_menu("我的插件", [
        ("打个招呼", lambda: print("你好")),
    ])
```

**存盘、重开程序** → 菜单里就多了一栏。
**Save, restart** → a new menu appears.

### ★★ 多语言 / i18n for plugins

**★ 插件里的界面文字也走 `api.T()`**，这样切英文时插件文字也跟着变。
**★ Plugin UI strings should go through `api.T()`** so they follow the language
switch.

```python
def register(api):
    api.add_menu(api.T("我的插件"), [
        (api.T("打个招呼"), _hello),
    ])
```

**★ 老版本主程序没有 `api.T` 也不会崩**（插件里有兜底）。
**★ Older hosts without `api.T` will not crash** (there is a fallback).

### `api` 能干什么 / What `api` offers

| 想干的事 / Goal | 怎么写 / How |
|---|---|
| 加自己的菜单 / own menu | `api.add_menu("名字", [("项", 函数), None, ("项2", 函数2)])` |
| 往已有菜单插一项 / insert into an existing menu | `api.add_menu_item("设置", "我的设置", 函数)` |
| 给程序加配色 / register a theme | `api.register_theme("名字", {"win_bg": "#...", "fg": "#..."})` |
| 看当前文件夹 / current folder | `api.current_dir()` |
| 看选中了什么 / selected paths | `api.selected_paths()` |
| 往「输出」写日志 / write to the Output panel | `api.log("…")` |
| 翻译 / translate | `api.T("中文")` |

**★★ 完整说明见 `文档-公开发布/插件怎么写.md`**
**★★ Full guide: `文档-公开发布/插件怎么写.md`**

**★★★ 最重要的一条 / The single most important rule**：
> **插件坏了，程序不会坏** —— 每个插件单独 `try`，
> 坏一个只记账、**绝不影响程序启动**。
>
> **A broken plugin never breaks the app** — each plugin runs in its own
> `try`; a failure is logged and **never stops startup**.

---

## 五、这个项目的"脾气" / The house's rules

**★ 作者自己总结的几条**（★ 都是**实测踩出来的**，不是空话）
**★ Summarised by the author** (all learned the hard way)

| # | 规矩 / Rule | 出处 / Source |
|---|---|---|
| **1** | ★★ **量，别猜** —— "我觉得"不算数，**跑一遍看数据** / **measure, don't guess** | 多次验证 / verified repeatedly |
| **2** | ★★ **"有兜底"会掩盖"功能没生效"** —— 要专门验证"兜底**没**被用上" / a fallback hides "it never ran" | 错题本 #143 |
| **3** | ★★ **"改一套逻辑"要全文搜旧来源** / grep for the old source when changing logic | 错题本 #139 |
| **4** | ★★ **一个容器装两种"正交"的东西，早晚会串** / one container for two orthogonal values will scramble | 错题本 #140 |
| **5** | ★★ **"名字不存在 + 被 except 吞掉" = 永远不报错，只是不工作** / missing name + bare except = silent no-op | 错题本 #143 |
| **6** | ★★★ **"修一个坏东西"之前，先确认它到底坏没坏** / prove it is broken before fixing it | 错题本 #138 |
| **7** | ★★ **隐私/安全规则，写完要拿真实文件试一遍** / test privacy rules against real files | 错题本 #142 |
| **8** | ★★★ **"测了没发现" ≠ "没有问题"** / "I tested it" ≠ "it is fine" | 错题本 #152 |
| **9** | ★★ **要测一个函数收到了什么，就在函数里记录输入** / log inputs inside the function | 错题本 #157 |

**★★ 完整版见 `文档-公开发布/AIxiede-错题本.md`（157 条）** ——
★ **建议改代码前翻一翻**，**很多坑会以"换个样子"重现**。

**★★ Full list: `文档-公开发布/AIxiede-错题本.md` (157 entries)** —
★ **read it before editing**; many pitfalls come back in disguise.

---

## 六、绝对不能碰的东西 / Never touch

### 🚫 1. **数据库文件** / the database files

```
.file_tagger.db  /  .db-shm  /  .db-wal  /  .db.bak-*
```

**★ 那是用户的全部数据**（文件路径、标签、索引）。
**★ 改代码时如果要测试，请用临时目录，别碰真的。**
（★ `.gitignore` 已经挡住了它们，**不会进版本库** ✔）

**★ That is the user's entire dataset** (paths, tags, index).
**★ Use a temp folder for testing — never the real one.**
(★ `.gitignore` already excludes them ✔)

### 🚫 2. **`tk.Tk` 的全局补丁** / global `tk.Tk` patches

**★ 别写 `tk.Tk = 某个自定义类` 这种** ——
这个项目里**有过**，导致**很多奇怪的问题**（错题本里有）。

**★ Never write `tk.Tk = SomeCustomClass`** — it was tried here and caused
**a pile of weird bugs**.

### 🚫 3. **后台线程里碰 Tcl/Tk** / touching Tcl/Tk from background threads

**★★ Tk 不是线程安全的。** 后台线程**只能**：
- 改普通变量 / touch plain variables
- 往 `queue` 里塞东西 / push into a `queue`
- **不能**直接 `widget.configure(...)` / **never** call `widget.configure(...)`

**★ 正确做法**：后台线程塞 `queue`，主线程用 `after()` 轮询取出来再改界面。
**★ Correct pattern**: background thread → `queue` → main thread polls with
`after()` and updates the UI.

### 🚫 4. **密钥 / 个人信息** / secrets and personal data

**★ 别把**任何**密钥、密码、个人路径**写进代码**（这项目踩过）。
**★ Never put secrets, passwords or personal paths in the code.**

**★ 密钥存在**设置文件**里**（`load_ui_setting("xxx")`），
**不进代码、不进版本库**。

**★ Secrets live in the **settings file** (`load_ui_setting("xxx")`) — **never
in code, never in the repo**.

---

## ★ 最后 / Finally

**★★ 谢谢你看完这份文档。**
**★★ Thanks for reading this far.**

**★ 不管你是补了一句翻译、提了一个 issue、还是改了一行代码** ——
**都让这个项目往前挪了一点。**

**★ Whether you added one translation, filed one issue or changed one line —
you moved this project forward.**

**★ 有问题就直接问**（开 issue 或者在 PR 里问），**别客气。**
**★ Just ask** (open an issue or ask in the PR) — **don't be shy**.

---

<div align="center">

**★ 一个人做的项目，靠的是别人顺手帮一把。**
**★ A one-person project survives on other people's small favours.**

</div>
