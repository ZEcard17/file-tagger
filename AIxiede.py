# -*- coding: utf-8 -*-
# ==========================================================================
#  文件标签管理器 (File Tagger Manager)
#  --------------------------------------------------------------------------
#  版权所有 (c) 2026 510722199905170360
#
#  本项目由 **510722199905170360** 提出需求与设计，
#  **AI（DeepSeek）辅助编写实现**。
#
#  ★ 永久开源。完整许可条款见项目根目录的 `LICENSE` 文件
#    （GNU AGPL-3.0，见 https://www.gnu.org/licenses/agpl-3.0.html）。
#
#  ★★ 这份声明的作用（**说清楚，免得误解**）：
#    · 它**证明这个项目的来源**（谁提的、谁写的、什么时候）
#    · 它**声明了许可**（AGPL-3.0 —— 改了拿去做网络服务必须也开源）
#    · ★ **但它不是"防删"的** —— 代码里的注释**任何人都能改**。
#      真正改不掉的是 **Git 的提交记录**（改了 hash 就变，一看就知道）
#      和 **LICENSE 文件**（删了就是侵权）。
#      → 所以"最早的编辑证据"在 **Git 历史**里，不在这行注释里。
#
#  ★★★ 关于"AI 写的"这件事（**诚实说明**）：
#    这个项目的**大量代码确实由 AI 辅助生成**。
#    ★ 我不打算隐瞒这一点 —— 用了 AI 不丢人，
#      隐瞒来源才是问题。
#    ★ 但也说清楚：**需求、设计、取舍、测试标准都是人定的**，
#      AI 只是"打字快的那双手"。
# ==========================================================================
"""
文件标签管理器 v26
==================

   ★ 说明：下面只留**最近 3 条**更新记录。
     更早的历史（22 条，从 v25 一路往回）都挪到了
     **MyPython 目录下的 `AIxiede-更新记录.md`** —— 想查随时能查，
     而且**不影响程序运行**（那只是说明文字）。
     ★ 为什么挪：那一大段有 1800 多行，占全文件 6%。
       挪走之后程序瘦了一圈，「读一遍」更快、更省钱。

   ★★ 2026-10-06（早上）：**加皮肤 —— 主要是夜间（晚上不开灯不刺眼）** ★★
      备份：`AIxiede.py.bak-加夜间皮肤-好用的-20261006-0900`
            （加皮肤之前：`…-修好切文件卡死-好用的-20261006-0800`）
      用户原话：「写套夜间皮肤，现在这个晚上不开灯有点闪」。

   ● 怎么用（就两步）：
       菜单 **界面 → 🎨 皮肤（白天 / 夜间）** → 选「🌙 夜间」；
       或者点 **界面 → 🌓 快速切换白天 / 夜间** 一键来回切。
       选完**自动记住**，下次打开还是这个皮肤。

   ● 为什么不是「把每个颜色改一遍」：
       全文件原来有 **72 种不同的硬编码颜色**（bg="white" 31 处、
       bg="#fcfcfd" 27 处、#f0f1f3 9 处 ……）。
       一处一处改，漏一处就是「深底上突然一块白板」；
       而且以后想再加一套皮肤又得全改一遍 —— 最容易改坏的做法。
       ★ 现在的做法：**一张颜色对照表 + 自动换色**
         · 两个「色板」：`_THEME_LIGHT`（白天=原样）/
           `_THEME_DARK`（夜间深色）；
         · 切皮肤时：① 先把「控件外观」整体套上（按钮、滚动条、
           输入框、文件树、菜单…见 `_style_all_widgets`）；
           ② 再把**已经建好的每个控件**按对照表换一遍
           （`_retheme_tree`，连 ttk 内部的子部件一起）；
           ③ 最后把「代码自己画颜色」的那几块重画一遍
           （文件列表、侧栏、预览区，见 `_retheme_custom_parts`）。
       ★ 以后想再加一套皮肤（比如护眼的米黄色），只要多写一张色板，
         **不用动任何界面代码**。

   ● 三条经验（都是实测踩出来的，别改坏）：
       ① **ttk 必须用 clam 主题**。Tk 默认那套（vista/winnative）是
          Windows 自己画的，**不吃自定义颜色** —— 用它做夜间，
          按钮和滚动条会顽固地保持白色。
       ② **切回白天要「照原始单据还原」，不能靠规则反推**。
          我第一版只写了「翻深」的规则，切回白天时又按规则翻回去 ——
          来回切几次颜色就漂了（实测切回白天后还有 30 个控件是深的）。
          现在改成：第一次改之前先把原色记在 `root._theme_orig_colors`
          这张「小票」上，以后照小票还原，切多少次都和第一次一样。
       ③ **控件里有些颜色不在控件身上，在样式里，而且是启动时定死的**。
          所以 `apply_theme` 要**先扫控件、再整体刷一遍样式表**（两个都做），
          不然「位置」「搜索文件」那几个框会一直是浅色。

   ● 白天的样子**一个像素都没动**（实测：白天 32 个浅底、0 个深底，
      和加皮肤之前完全一致）；夜间 38 个深底、0 个浅底。

   ★ 自测：白天→夜间→白天各切一次、再连着来回切 3 轮，颜色都正确；
     启动 1.4 秒、关窗退出码 0、程序输出零报错。

   ★★ 2026-10-06（早上）：**治「切文件卡死 / 切得快就冻住 / 两个按钮不见了」** ★★
      备份：`AIxiede.py.bak-修卡死预览按钮-20261006-0610`（改之前）
      用户报的三件事（原话）：
        「拉预览区的宽度还卡，但好点了」
        「.pdf 的跟随拉伸是切换到其他文件后才触发的，再切换就卡死了」
        「卡死强关了再开，居然不预览了」
        「自第二次重开，那两个按钮没了」
        「窗口右上角的关闭并不能完全把它关了」

   ● 病根（**实测出来的，不是猜的**）：**后台线程去抢界面**
       PDF 的页是一页一页在**后台线程**渲染的，渲染好一页就调
       `self._ui(apply)` 想让主线程贴图。而 `_ui` 会绕回主线程动 Tk 控件，
       Tcl 解释器**同一时刻只许一个线程碰**。
       用户「切文件切得快」的时候：后台线程正抢着 Tcl、主线程正在处理鼠标
       → 两边撞上 → **整个程序冻死**（点不动、关不掉，只能强杀）。
       ★ 实测证据：48 次快速切换，最慢一次 **8.7 秒**，整体僵死 123 秒。
       更狠的是「卡顿检测」自己也在帮倒忙：它误判「界面无响应」，
       然后**自己去写日志**（那也是主线程的活儿 + 碰 Tk）——
       越卡越报、越报越卡（实测一次误报让主线程僵 1.36 秒）。

   ● 改法（一句话：**后台线程只准算，一个界面控件都不许碰**）：
       ① 新增全局「信箱」`_bg_post` / `_drain_ui_mail`：
          后台线程干完活**只往一个 Python 列表里排队**（纯列表操作 +
          一把普通锁，一步 Tcl 都不碰，所以它永远不可能卡住）。
          主线程每 60 毫秒取一次，而且**每轮最多只干 35 毫秒**，
          保证界面一直保持「几十毫秒一小步」的节奏，永远跟手。
       ② `_pdf_bg_render_each` / `_pdf_rerender_if_needed` /
          `show_path` 里的视频缩略图 —— 全部改走这个信箱，不再调 `_ui`。
       ③ **打开 PDF 这件事本身也丢后台**（原来主线程同步开，
          网盘上实测最慢 6.5 秒 → 就是「切到网盘 PDF 就卡死」的元凶）。
          主线程**一步都不等**，先把「正在打开…」写上去。
          ★ 谁最后点的谁说了算：后发的那个会作废先发的（`_pdf_open_seq`），
            所以狂点也不会把该显示的那个挤掉。
       ④ **`os.stat` 也搬走**：实测网盘单次最慢 1.28 秒。
          改成先用「记得的大小」（`_size_cache`），后台量到新的再换上。
       ⑤ **卡顿检测改成两个纯计算线程**（`_HEART` / `_heartbeat_start`）：
          不在界面线程里打卡，看门狗发现真卡住了也**只排队、不直接抢**。
       ⑥ 启动自检从 `root.after(3000, ...)`（会夹在用户操作中间执行，
          一执行就是 1.8 秒）改成走排队通道；`health_check` 里那条最贵的
          「重复路径」查询由 `GROUP BY lower(path)`（240 毫秒）
          改成 `COUNT(*)-COUNT(DISTINCT lower(path))`（几毫秒）。
       ⑦ **两个按钮「不见了」**：`_nav_prev/_nav_next`（⬆ 回到顶部 /
          🔄 重新加载）原来排在中间，前面一旦抛异常被 `except` 吞掉，
          这一段就整段不执行 → 按钮就没了。现在挪到最后、
          **每个按钮单独包 try 并且一定 `pack` 出来**。
       ⑧ `_hide_all_content()` 换成「只收该收的、绝不动导航条」。

   ★ 实测（同一台机器、同一批网盘 PDF）：
       · `show_path`：最慢 **12.1 秒 → 0.003 秒**（千倍）
       · 48 次快速切换：**123 秒 → 6.5 秒**
       · 300 次连续预览：**3 秒**（每次约 10 毫秒）
       · 103 页 / 354 页的 PDF：**1 秒内全部排好**，标题写「已全部排好」
       · 两个按钮：**都在、都能点**（回到顶部 ✓ / 重新加载 ✓）
       · 狂切 30 次之后界面**还活着**（能继续刷新事件）

   ★ 踩到的一个坑（记下来别再犯）：
       **模块级的代码绝不能插在类中间** —— 我一度把 `_heartbeat_start`
       （模块级函数）插到了 `FileTaggerApp` 的中间，结果后面
       **4600 行方法全被挤出了类**（变成没人调用的普通函数），
      「打开文件夹」直接报「没有 choose_dir 这个属性」。
      类里方法数从 252 掉到 74 —— 就是这个。
      ★ 判据：改完用 AST 数一下「类里有多少方法」，对不上就是插错位置了。

   ★★ 2026-10-06 凌晨续：**接着加说话（这次是安全的做法）＋ 抓到
      「显示不全」的一个真凶** ★★
      备份：`AIxiede.py.bak-加好说话并修好拖动-好用的-20261006-0122`
      （上一版 `…-加好出错报告-好用的-20261005-2332` 有拖动失效的问题，
        要退回就退到 `…-修好比例记不住-好用的-20261005-2228` 那一版）

   ● ① **回退了危险的那一手**（详见开头那段「踩到的坑」）
        删掉 `tk.Tk.report_callback_exception` 的替换 —— 用户确认「能拖动了」。
        只留 `threading.excepthook`（线程级，不碰界面，安全）。
        ★ 已核实：现在全文件**没有任何**对 `tk.Tk` 类属性的赋值，
          唯一出现 `report_callback_exception` 的地方是**注释**（教训记录）。

   ● ② **抓到「显示不全」的一个真凶**（`FileList._redraw`）
        原来写着：
            w = c.winfo_width()
            if w <= 1:
                return          ← ★ 就这一句！
        宽度**一时拿不到**的时候（窗口刚建好、刚最大化、切换列表/瀑布流
        的那一瞬间），它**什么都不画就直接返回** —— 用户看到的就是
        **一片空白**。这跟用户说的「界面有些部分经常显示不全」完全对得上。
        修法：
          · 拿不到宽度 → 先 `update_idletasks()` 量一次；
          · 还是拿不到 → 试 `winfo_reqwidth()`；
          · 都不行 → **用保守宽度 600 照样把内容画出来**，
            并叫一次 `_relayout_panes_soon()` 稍后重排。
        一句话：**宁可画得不准，也别一片空白。**

   ● ③ **新增「保命画法」`_redraw_list_fallback()`**
        正常画法（列表 / 瀑布流）中途出错时，不再留一块空白 ——
        改成**把文件名一行一行简单画出来**，顶上写一句
        「⚠ 正常画法出错了，下面是保命画法（点右下角「🔔 问题」看原因）」。
        ★ 让「最坏情况」从「一片空白」变成「能看能点，只是朴素一点」。
        ★ 故意写得极简单（不碰缩略图、不排复杂列），越简单越不易再出错。

   ● ④ **给文件列表的关键位置加「说话」**（原来都是 `pass`）
        · `_redraw` 画表头失败 → 记一笔「列表顶部可能空着或错位」；
        · 画列表 / 画瀑布流中途出错 → 记一笔 + 自动走保命画法；
        · 量画布宽度失败 → 记一笔（quiet，不弹面板）。

   ★ 自测：语法 / 编译通过；「保命画法」专项测试通过（故意让正常画法
     崩掉 → 画布上出现 31 个元素、文件名都画出来了、问题面板也记了一笔）；
     正常启动 4.4 秒、关窗退出码 0、程序输出**零报错**。

"""

import os
import sys

# ★★ 2026-10-06「拆文件」：把拆出去的分块文件夹加到「找文件的路」上。
#   ★ 为什么必须**放在这么靠前**：
#     以前试着在用到的地方（一万多行之后）才加路径 —— 那时 Python 已经
#     执行到那儿了，分块文件反而找不到，于是**一路走兜底**，等于白拆。
#     现在放在最前面，后面任何地方要用分块都能找到。
#   ★ 用 __file__ 推算位置，所以**整个文件夹搬到哪里都能用**
#     （用户说过「很可能搬走」，这句很重要）。
#   ★ 文件夹不在也不报错 —— 找不到就各处的兜底顶上，程序照样开得起来。
# ==========================================================================
#  ★★★ 2026-10-08 **"我在哪儿"** —— 打包成 exe 之后路径会变，必须统一处理
#  ------------------------------------------------------------------------
#  ★★ 用户要"打包成 .exe 发群里" —— 这就带出三个必须解决的问题：
#
#    ① **`__file__` 在 PyInstaller 单文件模式下指向"临时解压目录"**，
#       不是"exe 所在目录" → 用 `__file__` 找 `图标资产/`、`插件/` **会找不到**。
#       ★ `sys._MEIPASS` 才是打包后的"资源解压目录"（PyInstaller 自己设的）。
#
#    ② **原来有三处写死了 `E:\桌面\MyPython\libs`** ——
#       别人电脑上**根本没这个目录** → PIL / tkinterdnd2 / pymupdf
#       **全都 import 失败**（有 try/except 所以不崩，
#       但**图片预览、拖拽、PDF 全没了** —— 发出去就是个半残品）。
#
#    ③ **用户数据不能写在程序目录** ——
#       如果他把 exe 放在 `C:\Program Files\` 或只读 U 盘里，
#       **写设置会失败**（甚至崩）。→ 见 `_user_data_dir()`。
#
#  ★ 所以这里先算好三个目录，后面所有地方**都用这几个**：
#      `_HERE`       —— "程序/资源"在哪儿（找图标、插件、拆分模块用）
#      `_APP_DIR`    —— "用户数据"该放哪儿（设置、数据库、导出）
#      `_LIBS_DIRS`  —— 可能的依赖库目录（**按顺序找，哪个有算哪个**）
# ==========================================================================

# ---- ① "我在哪儿" ----
#   ★ 打包后：`sys.frozen` 为 True，资源在 `sys._MEIPASS`；
#     exe 自己的位置在 `sys.executable` 旁边。
#   ★ 源码跑：资源就在 `.py` 旁边。
_HERE = None
try:
    if getattr(sys, "frozen", False):
        # ★ 打包后：**资源**在 _MEIPASS（图标/插件这些要跟着 exe 发的）
        _HERE = getattr(sys, "_MEIPASS", None) or os.path.dirname(
            os.path.abspath(sys.executable))
    else:
        _HERE = os.path.dirname(os.path.abspath(__file__))
except Exception:
    _HERE = os.getcwd()

# ★ **exe 自己所在的那个目录**（跟 `_HERE` 不一定一样：
#   单文件打包时 `_HERE` 是临时解压目录，而这个是用户放 exe 的地方）
#   ★ 为什么要区分：**用户想放插件/背景图**，应该放在 exe 旁边
#     （他看得见那儿），而不是临时目录（关了程序就没了）。
_APP_DIR = os.path.dirname(os.path.abspath(sys.executable)) \
    if getattr(sys, "frozen", False) else _HERE


def _user_data_dir():
    """★ **用户数据该放哪儿**（设置、数据库、导出、备份）。

    ★★ 为什么要单独一个函数（不能直接用 `_HERE`）：
      · 打包成单文件后，`_HERE` 是**临时解压目录** ——
        **程序一关就没了** → 设置**存不住**！
      · 源码跑的时候，`_HERE` 是程序目录 —— 那是用户自己的文件夹，
        存那儿没问题（**而且现在就是存那儿的，别改坏了**）。
    ★ 所以：
      · **源码跑** → 还是程序目录（**跟以前一模一样**，用户无感）
      · **打包跑** → `%LOCALAPPDATA%\AIxiede`（**可写、持久、不碍事**）
        ★ 为什么不放 exe 旁边：exe 可能被放在
          `C:\Program Files\`（**需要管理员才能写**）或者只读 U 盘里 ——
          写不进去就会**丢设置甚至崩**。
    ★ 环境变量 `AIXIEDE_DATA_DIR` 可以**强制指定**（便于测试 / 便携版）。
    """
    try:
        forced = os.environ.get("AIXIEDE_DATA_DIR")
        if forced:
            d = os.path.abspath(forced)
            os.makedirs(d, exist_ok=True)
            return d
    except Exception:
        pass
    if not getattr(sys, "frozen", False):
        return _HERE                      # ★ 源码跑：跟以前一样
    try:
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        d = os.path.join(base, "AIxiede")
        os.makedirs(d, exist_ok=True)
        return d
    except Exception:
        return _HERE


_USER_DIR = _user_data_dir()

# ==========================================================================
#  ★★★ 2026-10-08 **隐私保险**（用户特别强调的）
#  ------------------------------------------------------------------------
#  ★★ 用户原话：
#    「别把我的数据打包进去啊，给别人一个新的，
#     我感觉我自己的数据是隐私来着，
#     还有我的 **clouddrive2 密钥**也别给别人啊！！！」
#
#  ★★ 我实测过：**现在打出来的 exe 是干净的**
#    （在 exe 字节里搜"数据目录名 / 用户名 / cd_api_token / file_tagger.db"
#      全是 **0 次**）。
#    **但这只是"这一次没夹带"** —— 打包是**手工操作**，
#    下次手一抖（`--add-data` 指错、把数据挪进程序目录）**就会夹带出去**，
#    而且**发出去就收不回来了**。
#
#  ★★★ 所以这里立三条规矩（"冗余"，防的就是"以后改动"）：
#    ① **这些文件名，永远不许进包**（下面 `NEVER_PACK_NAMES`）
#    ② **打包脚本跑之前先检查**（见 `测试残留\_打包.py` 里的 `check_privacy`）
#    ③ **发之前能自己扫一遍**（`_privacy_scan_exe()`，见下面的函数）
#
#  ★ 特别说明 **CloudDrive2 密钥存在哪儿**（用户专门问的）：
#    · 它存在**设置文件**里（键名 `cd_api_token`）
#    · 而设置文件在**用户数据目录**（`Path.home()` 或 `data_dir`）
#    · **不在程序目录** → **PyInstaller 收不到** ✔
#    · 源码里只有 `load_ui_setting("cd_api_token")`（**只读，没硬编码**）✔
#  → **所以现在是安全的。** 下面这些只是"再加一道锁"。
# ==========================================================================

# ★ 这些**永远不许打包**（名字匹配，只看文件名）
NEVER_PACK_NAMES = (
    ".file_tagger.db", ".file_tagger.db-shm", ".file_tagger.db-wal",
    ".file_tagger_settings.json", ".file_tagger_undo.json",
    ".file_tagger_usage.jsonl", ".file_tagger_data",
    "tags_structure.json", "file_tags.json",
)

# ★ 这些**文件名里的关键词**也不许打包（比如 `xxx.db.bak-...` 这种备份）
NEVER_PACK_KEYWORDS = (
    ".file_tagger.db.",          # ★ 数据库备份（`.db.bak-修复网盘路径前-...`）
    ".file_tagger_settings.json.",
)


def privacy_find_private_files(folder):
    """★★ **找出一个目录里"不该被打包"的文件**（返回绝对路径列表）。

    ★ 用途：**打包之前**先扫一遍程序目录 ——
      发现数据文件就**停手**（宁可打不成，也别夹带出去）。
    ★ 为什么只扫"程序目录"这一层（不递归到底）：
      数据文件**按设计**就放在"程序目录 / 用户数据目录"这两个地方 ——
      程序目录里通常是干净的；
      ★ 但**万一**有人把数据挪进来了 → **这一层就能发现**。
      ★ 而且**不递归全盘**是为了快（打包前等着检查，不该等半天）。
    """
    hits = []
    try:
        for root, dirs, files in os.walk(folder):
            # ★ 跳过明显是"别人的东西"的目录（省时间、也免得误报）
            dirs[:] = [d for d in dirs
                       if d not in ("__pycache__", ".git", "备份",
                                    "测试残留", "打包输出", "文档",
                                    "_打包临时")]
            for f in files:
                if f in NEVER_PACK_NAMES:
                    hits.append(os.path.join(root, f))
                    continue
                for kw in NEVER_PACK_KEYWORDS:
                    if kw in f:
                        hits.append(os.path.join(root, f))
                        break
    except Exception:
        pass
    return hits


def privacy_scan_exe(path, extra_terms=None):
    """★★★ **扫一个 exe，看有没有夹带私人数据**（用户要的"发之前自己验一遍"）。

    ★ 怎么做：把 exe 当字节读，搜几个"**只有你的机器上才有**"的词：
        · 你的数据目录名（★ 从当前用户现算，不写死）
        · `Users\\<你的用户名>`
        · `cd_api_token`（密钥的键名 —— 正常不该出现在 exe 里）
        · `.file_tagger.db`
      ★ 这些**一个都不该出现**。

    ★ 返回 `(干净吗, 命中列表)`。
    ★ 为什么用"搜字节"而不是"列出打包内容"：
      · **最直接** —— 打包工具怎么想不重要，**exe 里到底有没有**才重要
      · **不依赖任何打包工具**（换成别的打包方式也照样能验）
    ★ `extra_terms` 可以补词（比如你的用户名、你的盘符）。
    """
    # ★★ 2026-10-08：**词表不能写死"某人的"数据目录名** ——
    #   原来这里写死了**某个具体的数据目录名**（开发者的），
    #   开源发出去之后，**别人看到会莫名其妙**，而且**等于泄露了**
    #   "开发者把数据放在哪个目录"。
    #   → 改成**从"当前用户的数据目录"里现算**：
    #     · 数据目录的最后一段名字（比如 `D:\我的资料` → `我的资料`）
    #     · 当前登录用户名（`Users\<当前用户>`）
    #   ★ 这样**每个人扫自己的**，词表**永远跟人对得上**。
    terms = ["cd_api_token", ".file_tagger.db",
             ".file_tagger_settings", "file_tagger_data"]
    try:
        # ★ 当前数据目录的"末段名"（可能为空 —— 那就不加）
        _du = str(_USER_DIR or "").rstrip("\\/")
        _base = os.path.basename(_du) if _du else ""
        if _base and len(_base) > 1:
            terms.append(_base)
    except Exception:
        pass
    try:
        u = os.environ.get("USERNAME") or ""
        if u:
            terms.append("Users\\" + u)
            terms.append("Users/" + u)
    except Exception:
        pass
    try:
        for t in (extra_terms or []):
            if t:
                terms.append(str(t))
    except Exception:
        pass
    hits = []
    try:
        with open(path, "rb") as f:
            data = f.read()
        for t in terms:
            try:
                if t.encode("utf-8") in data or t.encode("gbk") in data:
                    hits.append(t)
            except Exception:
                continue
    except Exception as exc:
        try:
            note_swallowed(T("扫 exe 隐私失败"), exc, level="warn")
        except Exception:
            pass
        return (False, ["（读不了这个文件：%s）" % path])
    return (not hits, hits)


def privacy_report(folder=None, exe=None):
    """★ **一行命令看"能不能发"**（打包脚本 / 手查都用它）。

    ★ 用法（在程序目录跑）：
        python AIxiede.py --check-privacy
      或者在别的脚本里 `import` 后调它。
    """
    lines = []
    try:
        folder = folder or _HERE
        exe = exe or os.path.join(_APP_DIR, "文件标签管理器.exe")
        bad_files = privacy_find_private_files(folder)
        if bad_files:
            lines.append("★ 程序目录里有 %d 个数据文件（**绝对不要打包**）："
                         % len(bad_files))
            for p in bad_files[:20]:
                lines.append("     %s" % p)
        else:
            lines.append("✔ 程序目录里没有数据文件（这个可以打包）")
        if os.path.isfile(exe):
            ok, hits = privacy_scan_exe(exe)
            if ok:
                lines.append("✔ exe 里没有夹带私人痕迹（这个可以发）")
            else:
                lines.append("★ exe 里发现了私人痕迹（**别发**）：%s" % hits)
        else:
            lines.append("（没找到 exe，跳过了 exe 检查：%s）" % exe)
    except Exception as exc:
        lines.append("★ 自检出错：%r" % (exc,))
    return "\n".join(lines)

# ---- ② 依赖库可能在哪儿（**按顺序找，哪个有算哪个**）----
#   ★ 顺序很重要：**先找"自己旁边"的**（打包/换电脑都能用），
#     最后才退回**原来那个写死的 E 盘路径**（保住本机现状，可逆）。
_LIBS_DIRS = []
try:
    _LIBS_DIRS = [
        os.path.join(_HERE, "libs"),              # ★ 程序目录/libs（最常见）
        os.path.join(_APP_DIR, "libs"),           # ★ exe 旁边/libs（用户能看到的）
        os.path.join(_HERE, "_internal", "libs"),  # ★ PyInstaller 目录模式
        r"E:\桌面\MyPython\libs",                 # ★ 老路径（保住本机）
    ]
    for _d in _LIBS_DIRS:
        try:
            if _d and os.path.isdir(_d) and _d not in sys.path:
                sys.path.append(_d)
        except Exception:
            pass
except Exception:
    _LIBS_DIRS = []


def _first_existing_dir(cands, default=None):
    """★ 从候选里挑**第一个真的存在的**目录（都没有就用 default）。"""
    for c in cands or []:
        try:
            if c and os.path.isdir(c):
                return c
        except Exception:
            continue
    return default


try:
    # ★★★ 2026-10-08 **这里曾经有个被吞掉的 NameError** ★★★
    #   ★ 我上次做"路径改成相对自身"时，把
    #     `_SPLIT_DIR = os.path.join(os.path.dirname(...), ...)`
    #     那行**替换掉了**，但下面这个候选列表**还在引用 `_SPLIT_DIR`**：
    #         _SPLIT_CANDS = [_SPLIT_DIR, ...]     ← ★ 它还没定义！
    #   ★★ 后果：抛 `NameError` → 被 `except Exception: pass` **吞掉** →
    #     **拆分目录永远加不进 sys.path** →
    #     所有拆出去的模块（SimpleInputDialog…）**全部"没找到"**，
    #     退回了内置版。
    #   ★ 为什么一直没发现：**它们都有"内置兜底版"**，
    #     程序照常跑，只是**一直在用内置的那份**（拆了等于没拆）。
    #   ★★★ 教训（错题本 #143）：
    #     **"名字不存在 + 被 bare except 吞掉" = 永远不报错，只是不工作。**
    #     ★ 判据：**新引用的每个名字，都要 grep 一遍"它到底定义了没"。**
    #
    # ★ 现在补上定义（用 `_HERE` —— 打包后它就是资源目录）。
    _SPLIT_DIR = os.path.join(_HERE, "AIxiede拆分开", "程序分块")
    # ★ 再兜几层：程序目录 / exe 旁边 / 老写法（`__file__` 推算）
    _SPLIT_CANDS = [
        _SPLIT_DIR,
        os.path.join(_APP_DIR, "AIxiede拆分开", "程序分块"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "AIxiede拆分开", "程序分块"),
    ]
    _SPLIT_DIR = _first_existing_dir(_SPLIT_CANDS, _SPLIT_DIR)
    if os.path.isdir(_SPLIT_DIR) and _SPLIT_DIR not in sys.path:
        sys.path.insert(0, _SPLIT_DIR)
except Exception:
    pass

# ==========================================================================
#  ★★★ 2026-10-08 **多语言（i18n）**（用户要的"联合国官方语言"起步）★★★
#  --------------------------------------------------------------------------
#  ★★ 用户原话：
#    「如果可以的话我很想联合国官方语言都做出来弄上去，但是我很穷，所以暂时 A」
#    → 先做**框架 + 英文**；以后加俄语/法语/西语/阿语 = **加一个 JSON 文件**。
#
#  ★ 这里要做的事**只有一件**：把框架**接上**（导入 + 设语言）。
#    ★ **不在这里把 500 处界面文字全改成 `T()`** —— 那是下一步，
#      而且要**分批做**（500 处一次改完，出问题根本没法定位）。
#    ★ 判据：**"机制"和"内容"分开验证** ——
#      先确认 `T("取消")` 真的能返回 "Cancel"，再批量替换。
#
#  ★★ 为什么导入放在这个位置（**很讲究**）：
#      `i18n.py` 在 `AIxiede拆分开\程序分块\` 里 ——
#      **必须等那个目录进了 `sys.path` 之后**才能 import。
#      上面那段 `_SPLIT_DIR` 就是干这个的，所以这里放它后面。
#      ★ 放错了（比如放文件最前面）→ `ModuleNotFoundError` →
#        被 `except` 吞掉 → **多语言永远不生效**（错题本 #143 那种坑）。
# ==========================================================================
try:
    import i18n as _i18n
    _HAS_I18N = True
except Exception as _e_i18n:
    _i18n = None
    _HAS_I18N = False
    try:
        _I18N_ERR = _e_i18n
    except Exception:
        _I18N_ERR = None


def T(text, **kw):
    """★★ **翻译一句话**（界面文字都该走这里）。

    ★ 为什么要在主程序里**再包一层**（而不是直接用 `i18n.T`）：
      · 主程序里 500 多处要调它 —— **包一层的好处是**：
        万一 `i18n.py` 没导进来（文件丢了），**这里能兜住**，
        不至于 500 处全部 `NameError`。
      · 而且以后想加"开发模式：显示未翻译标记"之类，**只改这一处**。
    ★ 兜底顺序：`i18n.T` → 返回原文。
      ★★ **永远返回一个能看的字符串** ——
        界面上的字**不该让程序崩**。
    """
    try:
        if _i18n is not None:
            return _i18n.T(text, **kw)
    except Exception:
        pass
    try:
        return str(text).format(**kw) if kw else str(text)
    except Exception:
        return str(text)


def _load_saved_language():
    """★ 启动时读"用户上次选的语言"。

    ★ 读不到就按系统语言猜（中文系统给中文，别的给英文）。
      ★ 为什么按系统猜：**第一次用的人**不会去设置里找语言 ——
        中文 Windows 的用户**本来就该看到中文**。
    """
    try:
        code = str(load_ui_setting("language", "") or "").strip()
        if code:
            return code
    except Exception:
        pass
    # ★ 按系统语言猜
    try:
        import locale
        loc = (locale.getdefaultlocale()[0] or "").lower()
        if loc.startswith("zh"):
            return "zh_CN"
        if loc:
            return "en_US"
    except Exception:
        pass
    return "zh_CN"


def _init_i18n():
    """★ 启动时调一次：按保存的语言设好翻译表。"""
    try:
        if _i18n is None:
            return False
        return _i18n.set_language(_load_saved_language())
    except Exception as _e:
        try:
            note_swallowed(T("初始化多语言失败（界面会显示中文）"), _e)
        except Exception:
            pass
        return False


# ★★ 上面这个块**必须在 `_SPLIT_DIR` 进 path 之后** ——
#   所以这里**先不调** `_init_i18n()`，等 `load_ui_setting` 也能用了再调。
#   调用点见 `main()` 里（那里所有依赖都齐了）。

# ★★ 2026-10-07：**图标数据**也搬到外面了（`图标资产\_icons_data.py`）。
#   那 680 KB 原来占整个程序的 32%，是"程序臃肿"的最大一块。
#   ★ 这里把 `图标资产\` 也加到"找文件的路"上，跟上面拆文件那套一个道理：
#     用 __file__ 推算位置 → **整个文件夹搬到哪里都能用**；
#     文件夹不在也不报错 → 图标退回 emoji，程序照常开。
try:
    # ★★ 打包后 `__file__` 在临时目录 → **必须优先用 `_HERE`**
    #   （`_HERE` 在打包时 = `sys._MEIPASS` = 资源真正解压的地方）
    _ICON_CANDS = [
        os.path.join(_HERE, "图标资产"),
        os.path.join(_APP_DIR, "图标资产"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "图标资产"),
    ]
    _ICON_DIR = _first_existing_dir(_ICON_CANDS) or _ICON_CANDS[0]
    if os.path.isdir(_ICON_DIR) and _ICON_DIR not in sys.path:
        sys.path.insert(0, _ICON_DIR)
except Exception:
    pass

import json
import colorsys
import sqlite3
import shutil
import subprocess
import threading
import queue
import time
import contextlib
import tkinter as tk
import tkinter.font as tkfont
from collections import deque
from tkinter import ttk, filedialog, messagebox, colorchooser
from pathlib import Path
from datetime import datetime


# ★ v25 补丁39（真 bug 修复）：**把 E 盘那个 libs 目录加进模块搜索路径**，
#   而且要加在**所有第三方库的 import 之前**。
#
#   原来这里的位置是错的：加路径的那段代码在 1356 行，而 PyMuPDF
#   （PDF 渲染）的 import 在 1315 行 —— **先 import 后加路径**，
#   所以 fitz / pymupdf 永远找不到，`HAS_FITZ` 永远是 False，
#   表现就是「所有 PDF 都显示『没装渲染库』、只有描述没有内容」。
#   （tkinterdnd2 之所以没事，是因为它的 import 本来就排在加路径之后。）
#   现在把加路径挪到最前面，后面所有 import 都能用上。
# ★★ 这一段**已经被上面统一的 `_LIBS_DIRS` 处理过了**（含老 E 盘路径兜底）——
#   这里只保留一个"最终选中的那个"给后面的代码读（兼容旧引用）。
#   ★ 为什么保留：程序里别处可能还在用 `_LIBS_DIR` 这个变量名，
#     **删了会 NameError**（错题本 #110 的教训：改一处要 grep 全部引用）。
_LIBS_DIR = _first_existing_dir(_LIBS_DIRS, _LIBS_DIRS[0]
                                if _LIBS_DIRS else None)

try:
    from PIL import Image, ImageTk  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False

# ★ v25 补丁28：PDF 渲染（PyMuPDF，装在 E 盘 libs 里）
#   用来在预览窗格 / 悬停预览里把 PDF 的某一页画成图。
#   ★ 补丁39：路径已经在上面加好了，这里 import 才找得到。
HAS_FITZ = False
# ★ v26：**先试新名字 pymupdf，再退回老名字 fitz** —— 顺序反过来。
#   原因：新版 PyMuPDF（1.24 之后）里，`import fitz` 会打一句
#     warning: The `fitz` API is deprecated and will be removed ...
#   功能虽然正常，但每次启动都刷一句提示。新版里 pymupdf 这个名字
#   的 API 和 fitz **完全一样**（Matrix / open / page.get_pixmap 都有），
#   所以先试它，就再也不会有那句提示了。
try:
    import pymupdf as _fitz_mod        # 新版本的名字（1.24+）
    HAS_FITZ = True
except Exception:
    try:
        import fitz as _fitz_mod       # 老名字（老版本 PyMuPDF）
        HAS_FITZ = True
    except Exception:
        _fitz_mod = None
        HAS_FITZ = False

# ★ v25 补丁28：解压缩用的 7-Zip（免安装版，装在 I 盘）
# ★★★ 2026-10-08 **7-Zip 的查找路径**（原来写死了开发者自己的私人路径）★★★
#   ★ 原来头几项是**开发者自己电脑上的私人路径** ——
#     别人机器上根本没有那个盘、也没有那个文件夹。
#     开源/发出去之后，这两行**只是无效的废话**（每次都要 stat 一次、必然失败）。
#   ★ 现在改成**三条来源**（按优先级）：
#     ① **环境变量 `SEVEN_ZIP`** —— 用户自己配（最灵活）
#     ② **程序目录 / 7za.exe** —— 绿色版（跟程序放一起）
#     ③ **系统默认安装位置** —— 最常见的两处
#   ★ 还顺手加了 `where 7z`（PATH 里能找到也算）——见 `_find_seven_zip()`。
SEVEN_ZIP_CANDIDATES = [
    os.path.join(_HERE, "7za.exe"),
    os.path.join(_HERE, "7z.exe"),
    os.path.join(_APP_DIR, "7za.exe"),
    os.path.join(_APP_DIR, "7z.exe"),
    r"C:\Program Files\7-Zip\7z.exe",
    r"C:\Program Files (x86)\7-Zip\7z.exe",
    r"C:\Program Files\7-Zip\7za.exe",
    r"C:\Program Files (x86)\7-Zip\7za.exe",
]


def _find_seven_zip():
    """★ 找 `7z.exe` —— **环境变量 > 程序旁边 > 系统路径 > PATH**。

    ★ 为什么要有这个函数（不只是那个列表）：
      · `SEVEN_ZIP` 环境变量让用户**明确指定**（放哪儿都行）
      · `PATH` 里能找到的也算（`where 7z`）——
        ★ 有些人是**用 winget / scoop 装的**，那种不在固定目录
      · ★ 全失败就返回 None（**调用方自己处理"没有就跳过"**）
    ★ 返回值：`7z`/`7za` 的**完整路径**，或 `None`。
    """
    try:
        env = os.environ.get("SEVEN_ZIP") or os.environ.get("SEVENZIP")
        if env and os.path.isfile(env):
            return env
    except Exception:
        pass
    for p in SEVEN_ZIP_CANDIDATES:
        try:
            if p and os.path.isfile(p):
                return p
        except Exception:
            continue
    # ★ 最后试 PATH（`where 7z`）—— 用 shutil.which 最省事
    try:
        for nm in ("7z.exe", "7za.exe", "7z", "7za"):
            w = shutil.which(nm)
            if w:
                return w
    except Exception:
        pass
    return None

ZIP_EXTS = {".zip", ".7z", ".rar", ".tar", ".gz", ".bz2", ".xz",
            ".tgz", ".tbz", ".iso", ".cab", ".lzh", ".z"}

try:
    import cv2  # type: ignore
    HAS_CV2 = True
except Exception:
    HAS_CV2 = False

try:
    import win32api       # type: ignore
    import win32con       # type: ignore
    import win32gui       # type: ignore
    import win32ui        # type: ignore
    HAS_WIN32 = True
except Exception:
    HAS_WIN32 = False


# ★ v25 补丁13：拖放（把文件从资源管理器拖进来 / 拖出去）。
#   tkinter 本身不支持外部拖放，要用 tkinterdnd2 这个小库。
#   它装在 E 盘（用户不想占 C 盘），所以先把那个目录加进模块搜索路径。
# ★★ 同上：用统一的 `_LIBS_DIRS`（**先找自己旁边，再退回老 E 盘**）
_DND_LIB_DIR = _LIBS_DIR
try:
    if _DND_LIB_DIR and os.path.isdir(_DND_LIB_DIR) \
            and _DND_LIB_DIR not in sys.path:
        sys.path.append(_DND_LIB_DIR)
except Exception:
    pass

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD, COPY  # type: ignore
    HAS_DND = True
except Exception:
    DND_FILES = None
    TkinterDnD = None
    COPY = None
    HAS_DND = False


# C 盘"引导文件"：只存 data_dir，几十字节
BOOTSTRAP_SETTINGS_PATH = Path.home() / ".file_tagger_settings.json"
# 兼容旧引用
SETTINGS_PATH = BOOTSTRAP_SETTINGS_PATH


def _read_json_file(p):
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}


def _write_json_file(p, data):
    try:
        Path(p).parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def _load_data_dir():
    """从 C 盘引导文件读 data_dir；没设或读失败返回 None"""
    data = _read_json_file(BOOTSTRAP_SETTINGS_PATH)
    d = (data.get("data_dir") or "").strip()
    if d:
        p = Path(d).expanduser()
        try:
            p.mkdir(parents=True, exist_ok=True)
        except Exception:
            return None
        return p
    return None


def get_data_root():
    d = _load_data_dir()
    return d if d is not None else Path.home()


def _full_settings_path():
    """完整设置文件路径：data_dir 已设就放那儿，否则放 C 盘（首次运行）"""
    d = _load_data_dir()
    if d is None:
        return BOOTSTRAP_SETTINGS_PATH
    return d / ".file_tagger_settings.json"


def _load_full_settings():
    """读完整设置。若 data_dir 里还没有，就退回读 C 盘旧文件（兼容）"""
    p = _full_settings_path()
    data = _read_json_file(p)
    if not data and p != BOOTSTRAP_SETTINGS_PATH:
        data = _read_json_file(BOOTSTRAP_SETTINGS_PATH)
    return data


def _save_full_settings(data):
    return _write_json_file(_full_settings_path(), data)


def save_data_dir(path):
    """写引导文件（只含 data_dir），不动 data_dir 里的完整设置"""
    return _write_json_file(
        BOOTSTRAP_SETTINGS_PATH,
        {"data_dir": str(Path(path).expanduser().resolve())}
    )


def migrate_settings_to_data_dir():
    """把 C 盘设置文件里除 data_dir 外的字段搬到 data_dir 里的完整设置文件。
       返回 (ok: bool, msg: str)"""
    d = _load_data_dir()
    if d is None:
        return False, "尚未设置数据目录，请先在菜单里设置。"
    target_path = d / ".file_tagger_settings.json"
    c_data = _read_json_file(BOOTSTRAP_SETTINGS_PATH)
    extra = {k: v for k, v in c_data.items() if k != "data_dir"}
    target_data = _read_json_file(target_path)
    # 合并（如果 C 盘有额外字段就覆盖到目标）
    changed = False
    for k, v in extra.items():
        if target_data.get(k) != v:
            target_data[k] = v
            changed = True
    if changed:
        if not _write_json_file(target_path, target_data):
            return False, "写入新设置文件失败。"
    # 无论有没有额外字段，都把 C 盘改回只有 data_dir
    if not save_data_dir(d):
        return False, "更新引导文件失败。"
    if changed:
        return True, str(target_path)
    return True, "设置已在数据目录中。"


_DATA_ROOT = get_data_root()
DB_PATH = _DATA_ROOT / ".file_tagger.db"
EXPORT_DIR = _DATA_ROOT / ".file_tagger_data"
TAGS_FILE = EXPORT_DIR / "tags_structure.json"
FILE_TAGS_FILE = EXPORT_DIR / "file_tags.json"

MIN_UI_SCALE = 0.8
MAX_UI_SCALE = 2.0
DEFAULT_UI_SCALE = 1.15

# ★ 文件列表分页大小（每页多少行）
FILE_PAGE_SIZE = 800

# ★ v25：文件列表「含子目录搜索」的保护参数
RECURSIVE_MAX_FILES = 300000     # 一次最多记多少文件（保险丝）
RECURSIVE_MAX_ROOTS = 200        # 一次最多扫多少个基点目录

# ★ v22：自动标签规则已改成「手动启动」：
#   打开文件夹 / 打开分类库时不再自动跑规则，
#   只有点「🏷 重读标签」时按规则更新一次。
#   （v21 的 AUTO_SCAN_ON_OPEN_DEFAULT 开关已取消）


def is_remote_path(path):
    """判断路径是不是网络/云盘。
       - 盘符形式：看 GetDriveType 是否 DRIVE_REMOTE
       - UNC 形式（\\\\server\\share\\...）：直接视为远程"""
    try:
        if not sys.platform.startswith("win"):
            return False
        p = os.path.abspath(path)
        # ★ UNC 路径（CloudDrive 挂载就是这种）—— 直接算远程
        if p.startswith("\\\\") or p.startswith("//"):
            return True
        import win32file  # type: ignore
        drive = os.path.splitdrive(p)[0]
        if not drive:
            return False
        dt = win32file.GetDriveType(drive + os.sep)
        return dt == 4  # DRIVE_REMOTE = 4
    except Exception:
        return False


# ================= ★ v25 补丁2：网盘挂载改名后的自愈 =================
# CloudDrive / RaiDrive 这类网盘挂载，UNC 名字是会变的：
#     旧：\\clouddrive-x-1790010851003\clouddrive\图本\...  （默认名）
#     新：\\CloudDrive\百度网盘\图本\...                     （改名后的挂载）
# 库里老记录还指着旧名字时：双击网盘文件打不开 / 报错，只有本地文件
# 能打开；重建索引也不管用（索引只补 dir_cache，改不了 files 表）。
# 下面这张表记着「旧名 -> 现名」，遇到就自动换掉；
# 旧名如果现在还连得上，就绝不动它（免得误伤同名的另一个挂载）。
NET_MOUNT_ALIASES = [
    ("\\\\clouddrive-x-1790010851003\\clouddrive", "\\\\CloudDrive\\百度网盘"),
]

_mount_alive_cache = {}


def _mount_alive(prefix):
    """这个挂载点现在连得上吗（结果缓存，别反复去问网盘，网盘很慢）"""
    key = str(prefix).lower()
    if key in _mount_alive_cache:
        return _mount_alive_cache[key]
    try:
        ok = os.path.isdir(prefix)
    except OSError:
        ok = False
    _mount_alive_cache[key] = ok
    return ok


# ==========================================================================
# ★★ 2026-10-03：网盘挂载改名 —— 以后不用再手改对照表了，程序自己认出来
#
#   用户反馈：「我重装系统了、网盘也重新挂载了，两边又对不上了」。
#   以前的做法是：把「旧名 -> 新名」硬写在源码里的 NET_MOUNT_ALIASES 表里，
#   每次改名都得让人来改代码 —— 太笨了。
#
#   现在改成**拿证据自己认**：
#     ① 先从库里找出「连不上的网盘挂载名」（比如 \\CloudDrive\百度网盘）；
#     ② 再看这台机器上现在有哪些**连得上**的挂载（比如 \\CloudDrive\X）；
#     ③ 从库里挑几个真实文件的「尾巴」，逐个拼到每个候选挂载后面，
#        看看文件在不在 —— **哪个候选命中的最多，就是它**；
#     ④ 认出来的这一对会记进设置文件，以后（包括下次再改名）都不用管。
#
#   ★ 为什么要「拿证据」而不是按名字猜：用户这台机器上是同时挂着
#     \\CloudDrive\X 和 \\CloudDrive\115open 两个网盘的，内容还部分重叠。
#     光看名字根本猜不准，必须真去点几个文件出来看。
#   ★ 一个都没认出来时**宁可不改**（返回 None）—— 改错路径会把标签弄丢。
# ==========================================================================

_net_aliases_loaded = False


def _ensure_net_aliases_loaded():
    """把「以前自动认出来的对照关系」从设置文件里读回来（整个程序只读一次）。"""
    global _net_aliases_loaded
    if _net_aliases_loaded:
        return
    _net_aliases_loaded = True
    try:
        saved = load_ui_setting("net_mount_aliases", []) or []
    except Exception:
        return
    for pair in saved:
        try:
            o, n = str(pair[0]), str(pair[1])
        except Exception:
            continue
        if not o or not n:
            continue
        if any(o.lower() == x[0].lower() for x in NET_MOUNT_ALIASES):
            continue
        NET_MOUNT_ALIASES.append((o, n))


def _remember_net_alias(old, new):
    """把一对「旧挂载名 -> 现挂载名」记下来（记进设置文件，下次直接用）。"""
    try:
        if not any(str(old).lower() == x[0].lower() for x in NET_MOUNT_ALIASES):
            NET_MOUNT_ALIASES.append((str(old), str(new)))
    except Exception:
        pass
    try:
        saved = load_ui_setting("net_mount_aliases", []) or []
        saved = [[str(x[0]), str(x[1])] for x in saved
                 if isinstance(x, (list, tuple)) and len(x) == 2]
        if [str(old), str(new)] not in saved:
            saved.append([str(old), str(new)])
            save_ui_setting("net_mount_aliases", saved)
    except Exception:
        pass


def _unc_head(path):
    """把 \\\\服务器\\共享\\子目录… 切成 (\\\\服务器\\共享 , \\子目录…)。

    不是 UNC 路径（本地盘 / 相对路径）就返回 (None, 原样)。
    """
    try:
        p = str(path).replace("/", "\\")
    except Exception:
        return None, path
    if not p.startswith("\\\\"):
        return None, p
    parts = p[2:].split("\\")
    if len(parts) < 2 or not parts[0] or not parts[1]:
        return None, p
    head = "\\\\" + parts[0] + "\\" + parts[1]
    rest = ("\\" + "\\".join(parts[2:])) if len(parts) > 2 else ""
    return head, rest


def _live_unc_mounts(extra=None):
    """这台机器上现在**连得上**的网盘挂载点（\\\\服务器\\共享）。

    ★ 特别注意：CloudDrive2 这类网盘是用自己的驱动挂上来的，
      **注册表 HKCU\\Network 和「网络位置」里都查不到**（实测：明明有
      X:、Y: 两个盘，注册表却是空的，WNet 也只会说「找不到网络连接」）。
      所以候选挂载点主要得**从数据库自己记着的位置里找**：
        · 索引管理里那些索引根目录；
        · 库里文件路径 / 目录缓存里出现过的挂载名。
      注册表和对照表里的「新名字」只当补充。
    """
    out = []

    def _add(x):
        try:
            h, _rest = _unc_head(str(x).strip().rstrip("\\"))
        except Exception:
            return
        if h and h.lower() not in [y.lower() for y in out]:
            out.append(h)

    for x in (extra or []):
        _add(x)
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Network") as k:
            i = 0
            while True:
                try:
                    sub = winreg.EnumKey(k, i)
                except OSError:
                    break
                i += 1
                try:
                    with winreg.OpenKey(k, sub) as sk:
                        rp, _t = winreg.QueryValueEx(sk, "RemotePath")
                    _add(rp)
                except Exception:
                    continue
    except Exception:
        pass
    for _o, n in NET_MOUNT_ALIASES:
        _add(n)
    return [m for m in out if _mount_alive(m)]


def _probe_file(path, timeout=6.0):
    """带超时的「这个文件在不在」—— 网盘睡着时 isfile 会卡很久。"""
    box = {}

    def _w():
        try:
            box["r"] = os.path.isfile(path)
        except Exception:
            box["r"] = False

    th = threading.Thread(target=_w, daemon=True)
    th.start()
    th.join(timeout)
    if th.is_alive():
        return False
    return bool(box.get("r"))


def _guess_mount_remap(old_head, tails, min_hits=2, extra=None):
    """★ 拿证据说话：这个连不上的旧挂载名，现在换成哪个挂载名了？

    做法：把库里几个真实文件的「尾巴」拼到每个候选挂载点后面，看文件在不在。
    命中最多、并且至少 min_hits 个的那个才算数；认不准就返回 None
    （**宁可不改，也不能把标签弄丢**）。
    """
    if not old_head or not tails:
        return None
    try:
        o_server = old_head[2:].split("\\")[0].lower()
    except Exception:
        o_server = ""
    cands = []
    for m in _live_unc_mounts(extra=extra):
        if m.lower() == old_head.lower():
            continue
        try:
            m_server = m[2:].split("\\")[0].lower()
        except Exception:
            m_server = ""
        # 同一个服务器下的挂载优先试（改名的常见情况就是这样）
        cands.append((0 if m_server == o_server else 1, m))
    cands.sort(key=lambda x: x[0])
    samples = tails[:4]
    need = max(int(min_hits), (len(samples) + 1) // 2)
    best, best_hits = None, 0
    for _pri, m in cands:
        hits = 0
        for t in samples:
            if _probe_file(m + t):
                hits += 1
        if hits > best_hits:
            best, best_hits = m, hits
        if hits >= len(samples):
            break
    if best is not None and best_hits >= need:
        return best
    return None


# ==========================================================================
# ★ v25 补丁23：右键「属性」用到的几个只读小工具
#   （大小 / 权限 / 分享 / 收藏 / 时间 / 占父级百分比）
# ==========================================================================

def fmt_size(n):
    """把字节数变成人看的大小（KB / MB / GB）。"""
    try:
        n = float(n)
    except Exception:
        return "?"
    if n < 0:
        return "?"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            if unit == "B":
                return "%d B" % int(n)
            return "%.2f %s" % (n, unit)
        n /= 1024.0
    return "%.2f TB" % n


def _dir_size_from_cache(store, dir_path, timeout=8.0):
    """★ v25 补丁23：用索引（dir_cache）算文件夹大小。

    为什么不用 os.walk：网盘那样走一遍要几分钟。索引里本来就记着每个
    文件的大小（索引扫描时顺手记的），SQL 一加就有 —— 实测网盘目录
    也是秒回。

    返回 (文件夹数, 文件数, 总字节数, 没记大小的文件数)；查不到返回 None。
    """
    try:
        conn = store.conn
    except Exception:
        return None
    p = str(dir_path or "")
    # ★ 补丁24：盘根（E:\）这种不用削反斜杠，否则会变成 E: 长度对不上
    _raw = p.replace("/", "\\")
    _is_root = (len(_raw) == 3 and _raw[1] == ":" and _raw[2] == "\\")
    p = _raw if _is_root else _raw.rstrip("\\")
    if len(p) < 2:
        return None
    # ★ v25 补丁24：改用「等于自己 或 属于它的子孙」（见 dir_scope_clause），
    #   不用 LIKE —— 反斜杠/下划线都不用转义，也不会漏掉根目录那一行。
    args = dir_scope_args(p)
    try:
        row = conn.execute(
            "SELECT "
            " SUM(CASE WHEN is_dir=1 THEN 1 ELSE 0 END) AS dirs, "
            " SUM(CASE WHEN is_dir=0 THEN 1 ELSE 0 END) AS files, "
            " SUM(CASE WHEN is_dir=0 THEN COALESCE(size,0) ELSE 0 END) AS bytes, "
            " SUM(CASE WHEN is_dir=0 AND size IS NULL THEN 1 ELSE 0 END) AS nosize "
            "FROM dir_cache WHERE " + dir_scope_clause(), args
        ).fetchone()
    except Exception:
        return None
    if row is None:
        return None
    dirs = row[0] or 0
    files = row[1] or 0
    if not dirs and not files:
        return None
    return (int(dirs), int(files), int(row[2] or 0), int(row[3] or 0))


def _win_file_acl_info(path):
    """★ v25 补丁23：读文件的「权限 / 所有者 / 属性」—— 只用系统自带命令，
    不额外装东西。读不到就返回 {}, 不抛异常。

    用 icacls 输出（中文系统上大概是这个形状）：
        C:\\路径   DOMAIN\\user:(I)(F)
                  BUILTIN\\Administrators:(I)(F)
    """
    out = {}
    if os.name != "nt":
        return out
    try:
        with open(os.devnull, "wb") as devnull:
            r = subprocess.run(
                ["icacls", str(path)],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                stdin=devnull, timeout=15,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        text = r.stdout.decode("utf-8", "replace")
    except Exception as exc:
        try:
            note_swallowed(T("属性：读文件权限失败"), exc)
        except Exception:
            pass
        return out
    acl = []
    owner = ""
    for line in text.splitlines()[1:]:
        s = line.strip()
        if not s:
            continue
        if s.startswith("Successfully") or s.startswith("已处理") \
                or s.startswith("处理的文件") or s.startswith("Failed"):
            continue
        # 「谁: 权限」这种形状
        if ":" in s and ("(" in s or "\\" in s):
            who, _, perm = s.partition(":")
            who = who.strip()
            perm = perm.strip()
            if not who:
                continue
            simple = []
            low = perm.lower()
            if "f)" in low or "(f" in low:
                simple.append("完全控制")
            else:
                if "m)" in low or "(m" in low:
                    simple.append("修改")
                if "w" in low:
                    simple.append("写")
                if "r" in low:
                    simple.append("读")
                if "x" in low:
                    simple.append("运行")
            note = "（继承）" if "(i)" in low else ""
            line = "%s：%s%s" % (who, "/".join(simple) or perm, note)
            if line not in acl:          # ★ 补丁23：icacls 会把同一行重复两遍
                acl.append(line)
            continue
        if "\\" in s or s.startswith("BUILTIN"):
            owner = s
    if acl:
        out["acl"] = acl[:12]
    if owner:
        out["owner"] = owner
    return out


def _progress_fraction(child_size, parent_size):
    """★ v25 补丁23：算「占父级的百分比」。返回 0~1 的浮点数或 None。"""
    try:
        c = float(child_size)
        p = float(parent_size)
    except Exception:
        return None
    if p <= 0 or c < 0:
        return None
    v = c / p
    if v > 1.0:
        v = 1.0
    return v


def like_escape_dir(dir_path):
    """★ v25 补丁24：把「一个目录路径」变成能直接喂给 SQL LIKE 的匹配串。

    ★ 这里的坑（2026-09-30 一次踩了两个，都记下来）：
      1) SQLite 里 `LIKE ... ESCAPE '\\'` 的转义字符**必须恰好是一个字符**；
         而我们写模式时习惯把 `\\` 写成 `\\\\`。一旦 ESCAPE 忘了带，
         双反斜杠就成了「两个字面反斜杠」→ **一条都匹配不上**；
      2) 反过来，如果为了保险把 `_` 也转成 `\\_`，在 ESCAPE 生效时它又变成
         字面下划线 → 带下划线的路径（`dsh_relay_test`）同样查不到。
      所以现在改成**两个都不依赖**：
        · 模式里把 `\\` 写成 `\\\\`、并且**一定要带 ESCAPE**（本函数配套
          `SQ_LIKE_ESCAPE` 常量）；
        · **不碰 % 和 _**（不转义，最多多查几行，不会有副作用）。
      另外新增 `dir_prefix_sql()`：用 `substr(...)` 做前缀比较，
      **完全不用 LIKE/转义**，关键查询用这个最稳。
    """
    p = str(dir_path or "").replace("/", "\\")
    base = p if p.endswith("\\") else p + "\\"
    return base.replace("\\", "\\\\") + "%"


# ★ 配 like_escape_dir() 一起用（写成常量，免得两边不一致）
SQ_LIKE_ESCAPE = " ESCAPE '\\'"


def dir_scope_clause(col="dir_path"):
    """★ v25 补丁24：判断「这一行属于某个目录（含它自己）」的 SQL 片段。

    ★ 为什么要专门写这个（2026-09-30 踩了三次坑才搞明白）：
      dir_cache 里的路径写法是**不统一**的 ——
        · 根目录那一行是 `C:\\xxx\\yyy`（**结尾不带反斜杠**）；
        · 子目录是 `C:\\xxx\\yyy\\子目录`（也不带）；
        · 但拿来比较的「前缀」通常写成 `C:\\xxx\\yyy\\`（带反斜杠）。
      所以用「前缀比较」查根目录自己那一行会**永远查不到**（因为前缀比它还长
      一个字符）。这里改成两类都算：
        · dir_path = 这个目录（它自己那一行）
        · substr(dir_path, 1, ?) = 前缀（带结尾反斜杠，它的子孙）
      参数按顺序给：(目录路径, 前缀长度, 前缀)。
      好处：完全不用 LIKE，Windows 路径里的反斜杠/下划线/百分号都不需要转义。
    """
    return ("(%s = ? OR substr(%s, 1, ?) = ?)" % (col, col))


def dir_scope_args(dir_path):
    """配 dir_scope_clause() 用的参数：(自己, 前缀长度, 前缀)。

    ★ 注意「盘根」这个边界（`E:\\`）：不能简单地把结尾反斜杠削掉 ——
      削成 `E:` 之后长度只有 2，而库里的行是 `E:\\…`（长度 3 起），
      前缀比较就会一个都查不到。所以：
        · `E:\\` 这种只有「盘符 + 反斜杠」的，原样保留（自己就是 `E:\\`）；
        · 其它目录把结尾反斜杠去掉（库里就是这么存的），前缀再补回来。
    """
    p = str(dir_path or "").replace("/", "\\")
    root_like = (len(p) == 3 and p[1] == ":" and p[2] == "\\")  # E:\
    unc_root = p.startswith("\\\\") and p.rstrip("\\").count("\\") == 1
    #                                        ↑ \\服务器\共享 这种只有两段
    if root_like:
        pref = p                      # E:\
        return (p, len(pref), pref)
    if unc_root:
        base = p.rstrip("\\")
        pref = base + "\\"
        return (base, len(pref), pref)
    base = p.rstrip("\\")
    if not base:
        base = p
    pref = base + "\\"
    return (base, len(pref), pref)


def _exists_with_timeout(path, timeout=3.0):
    """带超时的「这个路径还在不在」。

    ★ v25 补丁5：网盘（CloudDrive 这类）睡着的时候，os.path.exists 会卡住
      几十秒 —— 启动自检不能因此把界面拖住。所以放到一个小线程里去问，
      超过 timeout 秒还没答复就当「问不出来」（返回 None）。
    """
    box = {}

    def _worker():
        try:
            box["r"] = os.path.exists(path)
        except Exception:
            box["r"] = False

    th = threading.Thread(target=_worker, daemon=True)
    th.start()
    th.join(timeout)
    if th.is_alive():
        return None          # 超时 = 多半是网盘没挂上 / 没醒
    return bool(box.get("r"))


def _alt_down(state):
    """鼠标/键盘事件里「Alt 键是不是按着」—— ★ 2026-10-03 修正。

    ★★ 这是「单击选不中文件，只有框选好用」的**真正病根**，务必看明白：

      Tk 在事件里带的那个 state 数字，是「哪些修饰键按着」的位标记。
      看起来应该是：Shift=0x1、Ctrl=0x4、Alt=0x8（X11 的老规矩）、
      Tk 在 Windows 上则把 Alt 放在 0x20000。以前程序写成
          alt = (state & 0x0008) or (state & 0x20000)
      本意是「两种写法都认」，可**在这台机器上实测**（一个个按键试出来的）：

          什么都不按 → 0x8        按住 Shift → 0x9
          按住 Ctrl  → 0xc        按住 Alt   → 0x20008
          按住 Win   → 0x8  （没变）

      ——也就是说 **0x8 这一位是「永远亮着」的**，它根本不代表 Alt！
      于是每一次正常单击都被判定成「按住 Alt 在拉框」：
      单击不选中、只会起一个方框；只有真的拖一下（框选）才有反应。
      用户说的「单击文件跟没有差不多」，就是这个。

      真正的 Alt 位是 0x20000（Tk 在 Windows 上的 ALT_MASK）。
      再补一道保险：直接问系统「Alt 现在按着没」（GetAsyncKeyState），
      这样就算 Tk 的位标记以后又变，也不会再误判。
    """
    try:
        if int(state) & 0x20000:
            return True
    except Exception:
        pass
    try:
        import ctypes
        return bool(ctypes.windll.user32.GetAsyncKeyState(0x12) & 0x8000)
    except Exception:
        return False


def _ctrl_down():
    """Ctrl 键现在按着没（直接问系统，不看事件里的状态位）。"""
    try:
        import ctypes
        return bool(ctypes.windll.user32.GetAsyncKeyState(0x11) & 0x8000)
    except Exception:
        return False


def _send_to_recycle_bin(path):
    """★ v25 补丁9：把文件 / 文件夹丢进回收站（可以再还原，不是永久删除）。

    优先用 pywin32 的 SHFileOperation —— 这是 Windows 资源管理器自己用的
    那套接口，删进去的东西能在回收站里还原；
    没有 pywin32 就退回 send2trash；两个都没有就报错，让调用方去问用户。
    """
    try:
        from win32com.shell import shell, shellcon  # type: ignore
    except Exception:
        try:
            import send2trash  # type: ignore
            send2trash.send2trash(path)
            return True
        except Exception as exc:
            raise RuntimeError(
                "这台机器既没有 pywin32 也没有 send2trash，没法安全地删到回收站：%s" % exc)
    p = os.path.abspath(str(path))
    flags = (shellcon.FOF_ALLOWUNDO | shellcon.FOF_NOCONFIRMATION
             | shellcon.FOF_SILENT | shellcon.FOF_NOERRORUI)
    res = shell.SHFileOperation((None, shellcon.FO_DELETE, p, None, flags))
    code = res[0] if isinstance(res, (tuple, list)) else res
    if code != 0:
        raise RuntimeError("系统拒绝删到回收站（错误码 %s）" % code)
    return True


# ==========================================================================
# ★★ 2026-10-06 新增：**撤销（Ctrl+Z）—— 手一抖能退回来** ★★
#
#   为什么做这个（用户同意按这个顺序来）：
#     外面所有文件管理器的用户，骂得最多的三件事就是
#     「会丢东西 / 卡 / **退不回去**」。而资源管理器那个撤销有个著名的毛病：
#     **它偷偷执行，你完全不知道撤了什么**，以至于有人写教程教大家
#     用注册表把它**彻底禁用** —— 可见「撤销做不好比没有更可怕」。
#
#   ● 做法（和星图编辑器那套「快照」不一样）：
#     文件操作没法快照，所以改成**记「反动作」** ——
#     每做一件事，就记一条「怎么反着做回去」：
#       · 删除       → 记下路径，撤销时从回收站捞回来
#       · 重命名     → 记下「新名 → 旧名」，撤销时改回去
#       · 打/去标签  → 记下「哪些文件、哪个标签、加的还是要去的」
#     按 Ctrl+Z 就把最后一条反着执行一遍。
#
#   ● 四条规矩（都是照着外面的教训定的）：
#     ① **批量算一条**：一次删 50 个文件，按一次 Ctrl+Z **全退回来**，
#        不是按 50 次。（外面很多小工具就栽在这儿。）
#     ② **必须让用户看见**：撤销后在状态栏写清楚撤了什么
#        （「已撤销：把 3 个文件从回收站还原」），绝不偷偷干。
#     ③ **要落盘**：撤销记录写到文件里，**关了程序再开还能撤** ——
#        这是资源管理器最大的短板，我们要做得比它好。
#     ④ **做不到就不记**：拿不到回收站原位置这种，宁可不记这一条，
#        也绝不搞「假撤销」（按下去没反应比不能撤更气人）。
#
#   ● 不做的（想清楚了才不做，不是漏了）：
#     **移动 / 复制不做撤销**。原因：网盘上反向操作一次要好几秒甚至几十秒，
#     中途还可能断；而且「撤销复制」要删掉刚拷的那份，风险大。
#     宁可告诉用户「这个撤不了」，也不给一个按了要等半分钟、
#     还可能撤一半的按钮。
# ==========================================================================

UNDO_MAX = 100                      # 最多记多少步（超了丢最旧的）


def _undo_file_path():
    """撤销记录存在哪儿（跟数据库放一起，跟着数据走）。"""
    try:
        return str(Path(DB_PATH).parent / ".file_tagger_undo.json")
    except Exception:
        try:
            return str(Path.home() / ".file_tagger_undo.json")
        except Exception:
            return None


def _recycle_restore(paths):
    """★ 从回收站把文件捞回来（回到**它原来的位置**）。

    ★★ 这里踩过一个坑，写清楚免得以后再走弯路：
       一开始我以为「再用 SHFileOperation 删一次，系统就会还原」——
       **不对**。实测：那个调用返回错误码 2（文件已经不在那了），
       文件根本没回来。Windows 没有简单的「还原」接口。

    能用的是这一套（实测有效）：
       ① 打开回收站（Shell.Application 的 10 号特殊目录）；
       ② 一项一项看：名字对不对 + 「原位置」对不对
          —— **两个都对上**才算（光看名字会误伤同名的别的文件）；
       ③ 找到就用「复制到原目录」把它搬回去。

    ★ 为什么要「名字 + 原位置」两个都对：回收站里可能躺着别的同名文件
      （比如你在别的文件夹删过一个同名的），光按名字找会搬错东西。
      这是实测出来的教训 —— 回收站里真有 17 项，什么都有。

    返回 (成功数, [失败说明...])。
    """
    if not paths:
        return 0, []
    try:
        import win32com.client  # type: ignore
    except Exception as exc:
        return 0, ["这台机器没装 pywin32，没法从回收站还原：%s" % exc]
    try:
        sh = win32com.client.Dispatch("Shell.Application")
        rb = sh.Namespace(10)          # 10 = 回收站
        if rb is None:
            return 0, ["打不开回收站"]
        items = []
        for it in rb.Items():
            try:
                items.append((it, str(it.Name or ""),
                              str(rb.GetDetailsOf(it, 1) or "")))
            except Exception:
                continue
    except Exception as exc:
        return 0, ["读回收站失败：%s" % exc]

    ok = 0
    errs = []
    for p in paths:
        try:
            ap = os.path.abspath(str(p))
            base = os.path.basename(ap.rstrip("\\"))
            want_dir = os.path.dirname(ap)
            found = None
            for it, nm, orig in items:
                if nm != base:
                    continue
                # 原位置对得上（结尾匹配，容忍斜杠/大小写差异）
                o = orig.replace("/", "\\").rstrip("\\").lower()
                w = want_dir.replace("/", "\\").rstrip("\\").lower()
                if o == w or o.endswith("\\" + base.lower()):
                    found = (it, want_dir)
                    break
            if found is None:
                errs.append("%s：回收站里没找到它" % base)
                continue
            it, dest_dir = found
            dest = sh.Namespace(dest_dir)
            if dest is None:
                errs.append("%s：原文件夹不见了（%s）" % (base, dest_dir))
                continue
            dest.CopyHere(it, 16)      # 16 = 静默、不弹确认
            # 等一下下让系统把文件放好（网盘上可能要久一点）
            for _ in range(30):
                if os.path.exists(ap):
                    break
                time.sleep(0.1)
            if os.path.exists(ap):
                ok += 1
            else:
                errs.append("%s：搬回来了但没看到文件" % base)
        except Exception as exc:
            errs.append("%s：%s" % (os.path.basename(str(p)), exc))
    return ok, errs


def _undo_label(action):
    """把一条记录说成人话（给状态栏用）。"""
    try:
        kind = action.get("kind")
        items = action.get("items") or []
        n = len(items)
        if kind == "delete":
            return "把 %d 项从回收站还原" % n
        if kind == "rename":
            if n == 1:
                return "把「%s」改回原名" % os.path.basename(str(items[0][1]))
            return "把 %d 个文件的改名退回去" % n
        if kind == "tag_add":
            return "把 %d 个文件上的标签去掉" % n
        if kind == "tag_remove":
            return "把 %d 个文件上的标签加回来" % n
        return "撤销上一步"
    except Exception:
        return "撤销上一步"



def _unique_target_path(target_dir, name, is_dir):
    """★ v25 补丁12：粘贴时目标里已经有同名的了，就取个「- 副本」的新名字。

    （和 Windows 资源管理器一个习惯：xxx.txt → xxx - 副本.txt → xxx - 副本 (2).txt）
    """
    dst = os.path.join(target_dir, name)
    if not os.path.exists(dst):
        return dst
    if is_dir:
        stem, ext = name, ""
    else:
        stem, ext = os.path.splitext(name)
    cand = "%s - 副本%s" % (stem, ext)
    i = 1
    while os.path.exists(os.path.join(target_dir, cand)):
        i += 1
        cand = "%s - 副本 (%d)%s" % (stem, i, ext)
    return os.path.join(target_dir, cand)


def remap_net_path(path):
    """把「旧网盘挂载名」的路径换成当前挂载名；不需要换就原样返回。"""
    _ensure_net_aliases_loaded()
    try:
        p = str(path)
    except Exception:
        return path
    if not (p.startswith("\\\\") or p.startswith("//")):
        return p
    plain = p.replace("/", "\\")
    low = plain.lower()
    for old, new in NET_MOUNT_ALIASES:
        o = old.lower()
        if not low.startswith(o):
            continue
        if low[len(o):len(o) + 1] not in ("\\", ""):
            continue
        if _mount_alive(old):        # 旧名字还活着，别乱改
            return p
        if not _mount_alive(new):    # 新名字也连不上，改了也白改
            return p
        return new + plain[len(old):]
    return p


def path_depth(path):
    """路径层数（盘符也算一层；UNC 的 server\\share 算两层）。

    用来判断一个目录是不是「太顶层」（盘符根 / 共享根 / 用户主目录），
    这种目录拿去做递归搜索基点会扫到一大片无关文件。

    注意：os.path.splitdrive(r"\\\\srv\\share\\a") 只切出 '\\\\\\\\srv\\\\share'，
    所以盘符部分要按 '\\' 再数一遍。
    """
    try:
        p = os.path.abspath(path)
    except Exception:
        p = str(path)
    drive, rest = os.path.splitdrive(p)
    parts = []
    if drive:
        parts = [x for x in drive.replace("/", "\\").split("\\") if x]
    parts += [x for x in (rest or "").replace("/", "\\").split("\\") if x]
    return len(parts)


def collapse_roots(dirs, max_roots=200):
    """把一堆目录收拾成「互不包含」的扫描根。

    - 去重、去掉被别的根包含的子目录（免得同一棵树扫两遍）
    - 数量超过 max_roots 时只留最浅的那些，并返回是否被截断
    返回 (roots, truncated)
    """
    uniq = []
    seen = set()
    for d in dirs:
        if not d:
            continue
        try:
            k = os.path.normcase(os.path.normpath(d))
        except Exception:
            k = d
        if k in seen:
            continue
        seen.add(k)
        uniq.append(d)
    if not uniq:
        return [], False
    uniq.sort(key=lambda x: (path_depth(x), len(x)))
    kept = []
    for d in uniq:
        try:
            nd = os.path.normcase(os.path.normpath(d))
        except Exception:
            nd = d
        inside = False
        for k in kept:
            if nd == k or nd.startswith(k.rstrip("\\") + "\\"):
                inside = True
                break
        if not inside:
            kept.append(nd)
            if len(kept) >= max_roots:
                return [os.path.normpath(k) for k in kept], True
    return [os.path.normpath(k) for k in kept], False


def net_error_hint(err_text):
    """网盘连不上（WinError 53 / 1203 之类）时，给一句人话提示。

    不是这类错误就返回空串。
    """
    t = str(err_text or "")
    if not t:
        return ""
    if ("WinError 53" in t or "WinError 1203" in t
            or "找不到网络路径" in t or "网络路径键入不正确" in t
            or "ERROR_BAD_NET" in t):
        return ("提示：这一刻连不上这个网盘（WinError 53/1203）。\n"
                "· 先在资源管理器里打开一次该网盘，让它「醒」过来；\n"
                "· 确认 CloudDrive / 网盘客户端在运行并且已登录；\n"
                "· 如果只是偶尔抽风，隔几秒再点一次通常就好了。")
    return ""


# ==========================================================================
#  ★ v25 补丁4：把「被吞掉的异常」记一笔 —— 专治「点了没反应」
# ==========================================================================
# 背景：程序里有很多 `except Exception: pass`（出错就跳过、什么都不说）。
#   绝大多数是合理的（画界面、取图标、延时这类，失败了也无所谓），
#   但有一部分一旦出错，用户看到的就是「点了没反应 / 结果不对」，
#   连日志里都查不到 —— 这就是最难查的那种问题。
# 下面这个小工具专给那部分地方用：
#   · 同一个位置只记第一次（反复出错不会把日志刷爆）；
#   · 界面起来之后，提示会出现在「🔔 问题」面板里；
#   · 界面还没起来（或已经关掉）就打印到控制台。
_SWALLOW_SINK = None      # 界面启动后会挂上 FileTaggerApp.log_problem
_SWALLOW_SEEN = {}        # 记录每个位置报过几次
# ★★ 2026-10-05 新增：给「自动补说话」用的档案柜。
#   · _SWALLOW_CALLER：谁在哪儿出的错（文件名:行号 → 中文说法）
#   · _SWALLOW_QUIET ：安静名单（画界面时那种「失败了也无所谓」的小事，
#     报了只会烦人，所以只记数、不弹到「问题」面板）
_SWALLOW_CALLER = {}
_SWALLOW_QUIET = set()
# ★★ 2026-10-06 新增：**刚才谁在哪儿报的错**（只在内存里，不落盘）。
#   用途：`note_swallowed` 会把话弹到「问题」面板 → 那条话又会走
#   `log_problem` 进「用法记录」→ 同一件事被记两次、次数翻倍。
#   有了这个，`log_problem` 就能认出「你这是回声，我不重复记」。
#   ★ 必须用内存变量、**不能去读账本文件** —— 账本是攒着批量落盘的，
#     回声来的时候磁盘上还没有那条记录（这个坑实测踩过）。
_SWALLOW_LAST = {"where": "", "t": 0.0}


# ==========================================================================
# ★★ 2026-10-06 新增：**用法记录（「听诊器」）** ★★
# --------------------------------------------------------------------------
# 用户的想法：「我想让你每次跟我聊天的时候都看看程序被我用了出什么 bug」。
#
# ★ 但直接「每次都读一遍代码」是烧钱的：程序 1.4MB，读一遍 ≈ 35 万 token。
#   所以这里换个思路 —— **让程序自己记账，以后只读那几 KB 的账**：
#     · 程序平时照常用，什么都不用管；
#     · 哪天真卡了、真出错了，账已经在那儿了；
#     · 下次查问题，只读那个小文件（几乎不花 token）。
#
# ★ 记在哪：数据目录下的 `.file_tagger_usage.jsonl`（跟数据库放一起，跟着走）。
#   每行一条 JSON，追加写。这样**写坏一行不影响别的行**（比整个 JSON 稳）。
#
# ★★ 四条铁规矩（每一条都是防坑的，别改）★★
#   ① **绝不能拖慢程序**：攒够 N 条或过了 T 秒才落盘，而且丢后台线程写。
#      绝不在出错那一刻同步写盘（出错的时候本来就慢）。
#   ② **绝不能撑爆磁盘**：文件超过上限就只留最近 1000 条。
#   ③ **绝不能干扰用户**：完全不弹窗、不提示、不改状态栏。这是听诊器，
#      不是警报器 —— 用户不该感觉到它存在。
#   ④ **绝不记隐私**：只记「哪个功能出的错 / 什么异常 / 第几次 / 当时在哪个视图」。
#      **文件路径、文件名、标签名、搜索词一律不记**（上轮调研查到过血泪教训：
#      这类日志一旦带上路径，用户是不敢发给别人看的）。
#
# ★ 记账本身失败怎么办：**什么都不做**。记账挂了绝不能影响主程序 ——
#   所有地方都包着 try，整个模块没有一个地方会把异常往外抛。
# ==========================================================================

_USAGE_PATH = None            # 记账文件路径（界面起来后定）
_USAGE_BUF = []               # 攒着还没写盘的条目
_USAGE_LOCK = None            # 保护 _USAGE_BUF（后台线程也会碰）
_USAGE_LAST = 0.0             # 上次落盘时间
_USAGE_MAX_BYTES = 512 * 1024   # 文件超过 512KB 就瘦身
_USAGE_KEEP = 1000            # 瘦身时只留最近 1000 条
_USAGE_FLUSH_N = 20           # 攒够 20 条就写
_USAGE_FLUSH_SEC = 5.0        # 或者过了 5 秒就写


def _usage_init(path):
    """定下记账文件放哪儿（开机时由主程序调一次）。"""
    global _USAGE_PATH, _USAGE_LOCK
    try:
        _USAGE_PATH = str(path) if path else None
    except Exception:
        _USAGE_PATH = None
    try:
        if _USAGE_LOCK is None:
            _USAGE_LOCK = threading.Lock()
    except Exception:
        _USAGE_LOCK = None


def _usage_note(kind, where, exc=None, level="warn", extra=None):
    """★ 记一条用法记录（听诊器入口）。

    kind  ："swallow"（被吞掉的异常）/ "problem"（主动报的问题）/ "lag"（卡顿）
    where ：哪儿（给用户看的中文说法）
    ★ 这个函数**永远不会抛异常、永远不阻塞** —— 记不上就算了。
    """
    global _USAGE_LAST
    try:
        if not _USAGE_PATH:
            return
        now = time.time()
        rec = {
            "t": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": str(kind or "")[:20],
            "where": str(where or "")[:200],
            "lv": str(level or "")[:10],
        }
        if exc is not None:
            try:
                rec["exc"] = "%s: %s" % (type(exc).__name__, exc)
                rec["exc"] = rec["exc"][:300]
            except Exception:
                pass
        if extra:
            # ★ extra 只放「视图名」这种非隐私信息，调用方负责别塞路径进来
            try:
                rec["extra"] = str(extra)[:120]
            except Exception:
                pass
        try:
            rec["n"] = int(_SWALLOW_SEEN.get(str(where or ""), 0))
        except Exception:
            pass

        buf = _USAGE_BUF
        try:
            if _USAGE_LOCK is not None:
                _USAGE_LOCK.acquire()
            buf.append(rec)
            need = (len(buf) >= _USAGE_FLUSH_N
                    or (now - _USAGE_LAST) >= _USAGE_FLUSH_SEC)
        finally:
            try:
                if _USAGE_LOCK is not None:
                    _USAGE_LOCK.release()
            except Exception:
                pass
        if need:
            _usage_flush_async()
    except Exception:
        pass


def _usage_flush_async():
    """把缓冲里的条目丢给后台线程写盘（**绝不在调用线程写**）。"""
    global _USAGE_LAST
    try:
        _USAGE_LAST = time.time()
        th = threading.Thread(target=_usage_flush, daemon=True,
                              name="用法记录落盘")
        th.start()
    except Exception:
        # ★ 连线程都起不来（比如要关程序了）：那就不写了，不勉强
        pass


def _usage_flush():
    """真写盘（只在后台线程里跑）。"""
    try:
        path = _USAGE_PATH
        if not path:
            return
        items = []
        try:
            if _USAGE_LOCK is not None:
                _USAGE_LOCK.acquire()
            if _USAGE_BUF:
                items = list(_USAGE_BUF)
                del _USAGE_BUF[:]
        finally:
            try:
                if _USAGE_LOCK is not None:
                    _USAGE_LOCK.release()
            except Exception:
                pass
        if not items:
            return
        with open(path, "a", encoding="utf-8") as f:
            for r in items:
                try:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
                except Exception:
                    continue
        # ★ 瘦身：文件太大了就只留最近 N 条（免得越积越大）
        try:
            if os.path.getsize(path) > _USAGE_MAX_BYTES:
                _usage_slim(path)
        except Exception:
            pass
    except Exception:
        pass


def _usage_slim(path):
    """文件太大 → 只留最近 _USAGE_KEEP 条。"""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        if len(lines) <= _USAGE_KEEP:
            return
        keep = lines[-_USAGE_KEEP:]
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.writelines(keep)
        os.replace(tmp, path)
    except Exception:
        pass


def usage_read(limit=200):
    """★ 读回最近的用法记录（给「看账」用，也给 AI 查问题用）。

    返回 [(记录 dict), ...]，**最近的在前**。
    ★ 读不出来就返回空列表 —— 绝不因为记账文件坏了影响任何功能。
    """
    try:
        path = _USAGE_PATH
        if not path or not os.path.isfile(path):
            return []
        out = []
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except Exception:
                    continue
        return list(reversed(out))[:int(limit)]
    except Exception:
        return []


def usage_summary():
    """★ 把用法记录汇总成人话：哪几类问题、各几次、最近什么时候。

    返回 [(说法, 次数, 最近时间), ...]，按次数从多到少。
    """
    try:
        recs = usage_read(limit=100000)
        agg = {}
        for r in recs:
            try:
                w = str(r.get("where") or "(没名字)")
            except Exception:
                continue
            a = agg.setdefault(w, {"n": 0, "last": "", "kind": "", "exc": ""})
            a["n"] += 1
            t = str(r.get("t") or "")
            if t > a["last"]:
                a["last"] = t
            if not a["kind"]:
                a["kind"] = str(r.get("kind") or "")
            if not a["exc"]:
                a["exc"] = str(r.get("exc") or "")
        out = [{"where": k, "n": v["n"], "last": v["last"],
                "kind": v["kind"], "exc": v["exc"]}
               for k, v in agg.items()]
        out.sort(key=lambda d: -d["n"])
        return out
    except Exception:
        return []


def _swallow_caller_name(depth=2):
    """★ 2026-10-05 新增：回头看看「是谁调用的」，自动编一句人话。

    为什么需要它：程序里有六百多处「出错装没事」，一处一处手写说明
    既不现实、也容易写错。有了它，`note_swallowed` 就算**不传 where**
    也能报出「哪个功能出的错」，省得漏掉。

    返回形如「主程序._layout_right_panes」，界面还没起来时返回「(未知)」。
    """
    try:
        import sys as _sys
        f = _sys._getframe(depth)
        code = f.f_code
        line = f.f_lineno
        key = f"{code.co_filename}:{line}"
        cached = _SWALLOW_CALLER.get(key)
        if cached:
            return cached
        # 从最里层往外找：先看自己在哪个函数里，再看属于哪个类
        name = code.co_name
        cls = ""
        try:
            frm = f
            for _ in range(25):
                frm = frm.f_back
                if frm is None:
                    break
                loc = frm.f_locals
                if "self" in loc:
                    cls = type(loc["self"]).__name__
                    break
        except Exception:
            pass
        label = f"{cls}.{name}" if cls else name
        _SWALLOW_CALLER[key] = label
        return label
    except Exception:
        return "(未知)"


def note_swallowed(where, exc, level="warn", quiet=False):
    """记一笔「被静默跳过的异常」。

    where：哪儿失败了（给用户看的中文说法）；传 None 就自动认名字
    exc：  异常对象
    quiet：True = 只悄悄计数，不弹到「问题」面板
           （画界面时那种失败了也无所谓的小事走这里）
    ★ v25 补丁4 新增。同一个 where 只提示第一次。
    ★★ 2026-10-05 升级（「先加说话」这一轮）：
        · where 可以是 None → 自动从调用处推断「哪个功能出的错」；
        · 增加 `_SWALLOW_SEEN` 累计数，重复出错在「问题」面板里
          会显示「（这类已出现 N 次）」，方便判断是不是老毛病；
        · 修掉一个小坑：以前 `_SWALLOW_SEEN[n] > 1` 就 return，
          连计数都不再更新，现在照常计数、只是不重复提示。
    """
    try:
        if not where:
            where = _swallow_caller_name(depth=2)
        quiet = bool(quiet) or (where in _SWALLOW_QUIET)
        n = _SWALLOW_SEEN.get(where, 0) + 1
        _SWALLOW_SEEN[where] = n
        # ★★ 2026-10-06：**顺手记进「用法记录」**（听诊器）。
        #   ★ 注意放在 `if quiet: return` **前面** ——
        #     安静名单里那些（画界面时失败了也无所谓的小事）虽然不弹面板，
        #     但**恰恰是「界面显示不全」的线索**，更该记下来。
        #     反正它只是往内存缓冲塞一条，不打扰用户、也不落盘等待。
        try:
            _usage_note("swallow", where, exc, level=level)
        except Exception:
            pass
        # ★ 记下「刚才谁报的」—— 下面调 sink 时会被 log_problem 认出来是回声
        try:
            _SWALLOW_LAST["where"] = str(where or "")
            _SWALLOW_LAST["t"] = time.time()
        except Exception:
            pass
        if quiet:
            return
        if n > 1:
            # 第二次以后不刷屏；但如果是第 5、20、100 次，补一条「还在犯」
            if n in (5, 20, 100, 500):
                try:
                    sink = _SWALLOW_SINK
                    if sink is not None:
                        sink(f"（还在犯）{where}：已出现 {n} 次",
                             level="info")
                except Exception:
                    pass
            return
        msg = (f"{where}：{type(exc).__name__}: {exc}"
               f"（这一类提示，同一个地方只报第一次）")
        sink = _SWALLOW_SINK
        if sink is not None:
            try:
                sink(msg, level=level)
                return
            except Exception:
                pass
        try:
            print(f"[已跳过] {msg}")
        except Exception:
            # ★★ 2026-10-03：连 print 都挂了就退回 stderr（控制台一定能看）。
            try:
                import sys as _sys
                _sys.stderr.write(f"[note_swallowed] {msg}\n")
            except Exception:
                pass
    except Exception:
        pass


def swallowed_report(where=None):
    """★ 2026-10-05 新增：把「哪些地方在偷偷出错」汇总出来。

    给「问题」面板和排查用：返回 [(说法, 次数), ...]，按次数从多到少。
    where 不为空时只返回那一条的次数。
    """
    try:
        if where:
            return [(_SWALLOW_SEEN.get(where, 0), )]
        return sorted(((k, v) for k, v in _SWALLOW_SEEN.items()),
                      key=lambda kv: -kv[1])
    except Exception:
        return []


# ==========================================================================
#  ★★ 2026-10-05：「先加说话」—— 让哑巴开口的总阀门 ★★
# ==========================================================================
# 用户原话：「老卡死，界面有些部分经常显示不全，改来改去经常前面写好的
#   功能后面没了，总之 bug 还挺多」。
#
# 查出来的病根：全程序有 **624 处** `except Exception: pass` ——
#   出错就装没事，一声不吭。于是：
#     · 界面少画了一块 → 你看到的是「显示不全」，程序不告诉你为什么；
#     · 后台线程出错了 → 等一个永远不来的结果 → 你看到的是「卡死」；
#     · 改坏了一个功能 → 当场不报错 → 过几天才发现「咦这儿怎么不好使了」。
#
# 624 处不可能一条条手改（那本身就是最大的改坏风险）。所以装一个**总阀门**：
#   程序运行的时候自己盯住那些「本来要装没事」的出错，替它们留个脚印，
#   并**按地方归类**记进「问题」面板。
#
# ★ 怎么盯住的：换上自己的 `sys.excepthook` 不够（那管不到被 except 抓住的），
#   真正管用的是 **sys.settrace** 太重、会拖慢程序，所以不用。
#   这里用的是**轻量版**：只在几个「最要紧」的位置主动登记（见下面
#   `watch_silent`），加上 `note_swallowed` 的自动认名能力。
#   这样既不会拖慢程序，又能把最常见的那几类「哑巴」变成会说话。
_SILENT_WATCH = {}


def watch_silent(where, quiet=False):
    """★ 2026-10-05 新增：给「哑巴」位置登记一个名字。

    用法（配合 with 用）：

        with watch_silent("画文件列表"):
            ...可能出错的代码...

    出错时会自动记一笔进「问题」面板（同一处只报第一次），
    正常跑完则完全不影响、一点开销都没有。

    quiet=True 表示「这事失败了也无所谓」，只计数不弹面板
    （画界面时的小修饰、取图标这类走这里，免得刷屏）。
    """
    return _SilentWatcher(where, quiet)


class _SilentWatcher:
    """配合 watch_silent 用的上下文管理器。"""

    __slots__ = ("_where", "_quiet")

    def __init__(self, where, quiet=False):
        self._where = where
        self._quiet = bool(quiet)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc is None:
            return False
        # 出错了 → 记一笔，然后**照旧把异常放过去**（不改变任何原有行为）
        try:
            note_swallowed(self._where, exc, quiet=self._quiet)
        except Exception:
            pass
        return False        # False = 不吞掉，交给原来的 except 处理


def load_ui_scale():
    data = _load_full_settings()
    try:
        s = float(data.get("ui_scale", DEFAULT_UI_SCALE))
        return max(MIN_UI_SCALE, min(MAX_UI_SCALE, s))
    except Exception:
        return DEFAULT_UI_SCALE


def save_ui_scale(scale, user_set=True):
    data = _load_full_settings()
    data["ui_scale"] = float(scale)
    # ★★ v26（2026-10-01）：打上「这是用户自己手动调的」标记。
    #   程序启动时（_auto_ui_scale）看到这个标记就**完全听用户的**，
    #   再也不会拿「和屏幕缩放差太多」当理由把值丢掉。
    #   —— 这就是「界面缩放被锁死在 150%」的修法。
    if user_set:
        data["ui_scale_user_set"] = True
    return _save_full_settings(data)


def load_ui_setting(key, default=None):
    """★ v25 补丁8：读一个界面设置（存在数据目录的完整设置文件里）。

    用来记住「预览窗格 / 标签库 上次是开着还是关着、预览多宽」这类偏好，
    这样下次打开程序还是你上次摆的样子。
    """
    try:
        return _load_full_settings().get(key, default)
    except Exception as exc:
        # ★★ 2026-10-03：之前直接 return default，连日志都没记，
        #   用户发现设置丢了完全不知道为什么）。改成只记一笔 warn。
        try:
            note_swallowed(T("读 UI 设置失败（{x}），退回默认值", x=key), exc,
                           level="warn")
        except Exception:
            pass
        return default


def save_ui_setting(key, value):
    """★ v25 补丁8：写一个界面设置（只覆盖传进来的这一个键）。"""
    try:
        data = _load_full_settings()
        data[key] = value
        return _save_full_settings(data)
    except Exception as exc:
        # ★★ 2026-10-03：之前连日志都没有，用户设的快捷键丢了不知道为什么。
        try:
            note_swallowed(T("写 UI 设置失败（{x}）", x=key), exc, level="warn")
        except Exception:
            pass
        return False


# ==========================================================================
# ★ v25 补丁17：走 CloudDrive2 自己的本地接口建网盘索引
#   ----------------------------------------------------------------------
#   背景：网盘索引原来是一个目录一个目录去「摸」挂载盘（X:\…）。每摸一个
#   目录都要过一层 WinFSP，慢；而且出错只有一句吓人的
#   「[WinError 2] 系统找不到指定的文件」，看不出是网盘一时抽风、还是那个
#   目录在网盘里真的没了。
#
#   CloudDrive2 有一个跑在本机的接口（官方帮助页写明：管理界面在
#   http://localhost:19798，gRPC 也在同一个端口）。直接问它
#   「/百度网盘/图本 下面有什么」，不仅快，报错也是人话 ——
#   实测目录不存在时它会说“find by path: /百度网盘/QQMusicCache not found”。
#
#   所以：网盘根目录优先走这条路；没填令牌 / 连不上 / 不是网盘目录时，
#   自动退回原来那套挂载盘扫描，不影响任何现有功能。
#
#   依赖（都装在 E 盘，不占 C 盘，用户要求）：
#     E:\\桌面\\MyPython\\libs\\grpc、clouddrive_pb2.py、
#     clouddrive_pb2_grpc.py（由官网 clouddrive.proto 生成）
# ==========================================================================

# ==========================================================================
#  ★ v25 补丁18：程序是不是正在关窗（给后台线程看的牌子）
#   背景：后台线程（比如「目录比对」）扫完会 root.after() 回主线程，
#   如果这时窗口已经销毁，Tk 会直接崩 —— 表现就是「开个文件夹马上关窗，
#   程序闪退」。关窗前把这个牌子立起来，后台线程看到就不再往界面回话。
# ==========================================================================
APP_CLOSING = False


CD_API_LIB_DIR = _LIBS_DIR      # ★★ 改成统一的"依赖库目录"（原来是写死 E 盘）
CD_API_ADDR = "localhost:19798"                # CloudDrive2 核心服务的本地端口
CD_API_UNC_PREFIX = "\\\\CloudDrive\\"          # 网盘挂载出来的 UNC 前缀
CD_API_DEFAULT_WORKERS = 6                     # 同时发几个请求（越大越快，也越容易撞限流）
CD_API_MIN_WORKERS = 1
CD_API_MAX_WORKERS = 8

HAS_CD_API = False
try:
    if CD_API_LIB_DIR not in sys.path:
        sys.path.insert(0, CD_API_LIB_DIR)
    import grpc as _cd_grpc
    import clouddrive_pb2 as _cd_pb
    import clouddrive_pb2_grpc as _cd_pbg
    from google.protobuf import empty_pb2 as _cd_empty
    HAS_CD_API = True
except Exception as _cd_imp_err:
    _cd_grpc = None
    _cd_pb = None
    _cd_pbg = None
    _cd_empty = None
    try:
        note_swallowed("CloudDrive2 API：grpcio / protobuf 没装好，"
                       "网盘索引将退回挂载盘扫描（慢但能用）", _cd_imp_err)
    except Exception:
        pass


def cd_api_workers():
    """★ v25 补丁17：同时向 CloudDrive2 发几个请求（可在索引管理窗口里调）。"""
    try:
        n = int(load_ui_setting("cd_api_workers", CD_API_DEFAULT_WORKERS))
    except Exception:
        n = CD_API_DEFAULT_WORKERS
    if n < CD_API_MIN_WORKERS:
        n = CD_API_MIN_WORKERS
    if n > CD_API_MAX_WORKERS:
        n = CD_API_MAX_WORKERS
    return n


class CloudDriveApiClient:
    """★ v25 补丁17：CloudDrive2 本地接口的轻量封装（只用「列目录」这类只读功能）。
    用法：
        c = CloudDriveApiClient(token)
        if c.connect():
            print(c.mounts())            # 有哪些网盘、对应哪个虚拟路径
            print(c.list_dir("/百度网盘/图本"))
            c.close()

    ★ 路径换算是关键：程序界面里习惯写 `X:\\图本` 或
      `\\\\CloudDrive\\百度网盘\\图本`，而 CloudDrive2 的接口只认它自己的
      虚拟路径 `/百度网盘/图本`。换算关系不是写死的，而是问
      GetMountPoints 拿（挂载点 `X:` → 源目录 `/百度网盘`，挂载名 `百度网盘`），
      这样以后网盘换名字 / 换盘符，程序自己会跟着变。
    """

    def __init__(self, token, addr=None):
        self.token = str(token or "").strip()
        self.addr = addr or CD_API_ADDR
        self.channel = None
        self.stub = None
        self.version = ""
        self.last_error = ""
        self._mounts = None
        self._ready = False

    # ---------------- 连接 ----------------

    def _md(self):
        """带令牌的请求头（API 令牌按官方文档放进 Authorization）。"""
        return (("authorization", "Bearer " + self.token),)

    def connect(self):
        """连上并确认令牌可用。成功返回 True；失败把原因放 self.last_error。"""
        if not HAS_CD_API:
            self.last_error = ("没找到 grpcio / protobuf 这几个库（应该在 "
                               + CD_API_LIB_DIR + " 里）")
            return False
        if not self.token:
            self.last_error = "还没填 API 令牌"
            return False
        try:
            self.channel = _cd_grpc.insecure_channel(self.addr)
            self.stub = _cd_pbg.CloudDriveFileSrvStub(self.channel)
            info = self.stub.GetSystemInfo(_cd_empty.Empty(), timeout=10)
            if not getattr(info, "SystemReady", False):
                self.last_error = "CloudDrive2 服务还没就绪"
                return False
            try:
                rt = self.stub.GetRuntimeInfo(_cd_empty.Empty(), timeout=10)
                self.version = ("%s %s" % (getattr(rt, "productName", ""),
                                           getattr(rt, "productVersion", ""))).strip()
            except Exception:
                self.version = ""
            # 用「列挂载点」这一步顺便验证令牌（令牌没权限会在这里报错）
            if not self.mounts(force=True) and self.last_error:
                return False
            self._ready = True
            return True
        except Exception as exc:
            self.last_error = str(exc).replace("\n", " ")[:200]
            return False

    def close(self):
        try:
            if self.channel is not None:
                self.channel.close()
        except Exception:
            pass
        self.channel = None
        self.stub = None
        self._ready = False

    def describe(self):
        """给日志用的一行说明。"""
        v = ("（" + self.version + "）") if self.version else ""
        return "CloudDrive2 %s%s" % (self.addr, v)

    # ---------------- 网盘 / 路径 ----------------

    def mounts(self, force=False):
        """返回 [(挂载名, 虚拟源目录, 挂载点), ...]，例如
        ('百度网盘', '/百度网盘', 'X:')。本地磁盘挂载会跳过。"""
        if self._mounts is not None and not force:
            return self._mounts
        res = []
        try:
            rep = self.stub.GetMountPoints(_cd_empty.Empty(), timeout=15,
                                           metadata=self._md())
            for m in rep.mountPoints:
                if getattr(m, "localMount", False):
                    continue
                src = str(getattr(m, "sourceDir", "") or "").rstrip("/") or "/"
                nm = str(getattr(m, "name", "") or "").strip()
                if not nm:
                    nm = src.strip("/").split("/")[-1]
                res.append((nm, src, str(getattr(m, "mountPoint", "") or "")))
        except Exception as exc:
            self.last_error = str(exc).replace("\n", " ")[:200]
            res = []
        self._mounts = res
        return res

    def cd_path_of(self, local_path):
        """程序里的路径 → CloudDrive2 虚拟路径；不是网盘目录就返回 None。

        `\\\\CloudDrive\\百度网盘\\图本` → `/百度网盘/图本`
        `X:\\图本`                     → `/百度网盘/图本`
        本地盘（C:/D:/E:/I:）→ None（这些不走 API）
        """
        try:
            p = str(local_path or "").strip()
        except Exception:
            return None
        if not p:
            return None
        p = p.replace("/", "\\")
        up = p.upper()
        # 1) UNC 写法：\\CloudDrive\百度网盘\图本
        if up.startswith(CD_API_UNC_PREFIX.upper()):
            rest = p[len(CD_API_UNC_PREFIX):].strip("\\")
            if not rest:
                return None
            seg = rest.split("\\", 1)
            first = seg[0]
            rel = seg[1] if len(seg) > 1 else ""
            for name, src, _mp in self.mounts():
                if first.lower() == str(name).lower():
                    base = src.rstrip("/")
                    return base + ("/" + rel.replace("\\", "/") if rel else "")
            return None
        # 2) 盘符写法：X:\图本
        if len(p) >= 2 and p[1] == ":":
            drive = up[:2]
            rel = p[2:].strip("\\")
            for _name, src, mp in self.mounts():
                if str(mp).upper().rstrip("\\") == drive:
                    base = src.rstrip("/")
                    return base + ("/" + rel.replace("\\", "/") if rel else "")
            return None
        return None

    def unc_path_of(self, cd_path):
        """CloudDrive2 虚拟路径 → 程序里惯用的 UNC 路径（不带结尾反斜杠）。

        `/百度网盘/图本` → `\\\\CloudDrive\\百度网盘\\图本`
        认不出来就返回 None。
        """
        p = str(cd_path or "")
        for name, src, _mp in self.mounts():
            s = src.rstrip("/")
            if not s:
                continue
            if p == s or p.startswith(s + "/"):
                rel = p[len(s):].strip("/")
                out = CD_API_UNC_PREFIX + name
                if rel:
                    out += "\\" + rel.replace("/", "\\")
                return out
        return None

    # ---------------- 列目录 ----------------

    def list_dir(self, cd_path, timeout=180):
        """列一个目录，返回 [(名字, 是不是目录, 大小, 修改时间), ...]。

        ★ 出错就往上抛（调用方负责重试和记录）——这样「目录不存在」
          （NOT_FOUND）之类的真实原因能一路带上来。
        """
        req = _cd_pb.ListSubFileRequest(path=cd_path, forceRefresh=False)
        out = []
        for resp in self.stub.GetSubFiles(req, timeout=timeout,
                                          metadata=self._md()):
            for f in resp.subFiles:
                is_d = bool(getattr(f, "isDirectory", False))
                size = None
                mtime = None
                if not is_d:
                    try:
                        size = int(f.size)
                    except Exception:
                        size = None
                    try:
                        if f.HasField("writeTime"):
                            mtime = float(f.writeTime.seconds)
                    except Exception:
                        mtime = None
                out.append((str(f.name), is_d, size, mtime))
        return out


# ==========================================================================
#  ★★★ 2026-10-08 **搬到独立文件了**（第 2 批拆分）
#  --------------------------------------------------------------------------
#  ★ 搬走的是：`scan_index_root_via_api`、`_epub_chapters`、`_mobi_meta_and_text`、`get_video_thumbnail_pil`、`_cache_clean_old`
#  ★ 为什么挑它们（**量过**）：`self.app` 出现 0 次、被别处引用 <= 3 次。
#  ★ 怎么修（万一文件丢了）：
#     见 `AIxiede拆分开\\程序分块\\_电子书和缓存.py`；
#     或从 `备份\\AIxiede.py.bak-搬第2批前` 里把那段拷回来。
# ==========================================================================
try:
    import _电子书和缓存 as _m2
    _m2._set_app(sys.modules[__name__])
    scan_index_root_via_api = _m2.scan_index_root_via_api
    _epub_chapters = _m2._epub_chapters
    _mobi_meta_and_text = _m2._mobi_meta_and_text
    get_video_thumbnail_pil = _m2.get_video_thumbnail_pil
    _cache_clean_old = _m2._cache_clean_old
    _HAS_B2 = True
except Exception as _e_b2:
    _HAS_B2 = False
    _ERR_B2 = _e_b2
    # ★ 导不进来：给"一用就报清楚错"的替身（程序能起、界面能看）
    def scan_index_root_via_api(*_a, **_kw):
        raise RuntimeError(
            "模块 _电子书和缓存.py 没找到或有问题（scan_index_root_via_api 用不了）。\n"
            "  原因：%r\n"
            "  怎么修：见 备份\\AIxiede.py.bak-搬第2批前"
            % (_ERR_B2,))
    def _epub_chapters(*_a, **_kw):
        raise RuntimeError(
            "模块 _电子书和缓存.py 没找到或有问题（_epub_chapters 用不了）。\n"
            "  原因：%r\n"
            "  怎么修：见 备份\\AIxiede.py.bak-搬第2批前"
            % (_ERR_B2,))
    def _mobi_meta_and_text(*_a, **_kw):
        raise RuntimeError(
            "模块 _电子书和缓存.py 没找到或有问题（_mobi_meta_and_text 用不了）。\n"
            "  原因：%r\n"
            "  怎么修：见 备份\\AIxiede.py.bak-搬第2批前"
            % (_ERR_B2,))
    def get_video_thumbnail_pil(*_a, **_kw):
        raise RuntimeError(
            "模块 _电子书和缓存.py 没找到或有问题（get_video_thumbnail_pil 用不了）。\n"
            "  原因：%r\n"
            "  怎么修：见 备份\\AIxiede.py.bak-搬第2批前"
            % (_ERR_B2,))
    def _cache_clean_old(*_a, **_kw):
        raise RuntimeError(
            "模块 _电子书和缓存.py 没找到或有问题（_cache_clean_old 用不了）。\n"
            "  原因：%r\n"
            "  怎么修：见 备份\\AIxiede.py.bak-搬第2批前"
            % (_ERR_B2,))


def cd_api_client_from_settings():
    """★ v25 补丁17：按设置里的开关 / 令牌，创建一个已经连好的 CloudDrive2 客户端。

    返回 (client, 说明文字)：
      - client 不是 None：可以用它走 API 建索引；
      - client 是 None：这次不走 API，说明文字里写清原因
        （界面上直接把这句记到日志里，用户就知道为什么还是慢）。
    """
    if not bool(load_ui_setting("cd_api_enabled", True)):
        return None, "按设置走挂载盘扫描（CloudDrive2 API 已在索引管理里关闭）"
    if not HAS_CD_API:
        return None, "没找到 grpcio / protobuf 库 → 走挂载盘扫描"
    tok = str(load_ui_setting("cd_api_token", "") or "").strip()
    if not tok:
        return None, "还没填 CloudDrive2 API 令牌 → 走挂载盘扫描（在索引管理里点「🔑」填一次）"
    c = CloudDriveApiClient(tok)
    if not c.connect():
        reason = c.last_error or "连不上"
        try:
            c.close()
        except Exception:
            pass
        return None, "CloudDrive2 API 没连上（%s）→ 走挂载盘扫描" % reason
    return c, "☁ 已连上 CloudDrive2 API：%s" % c.describe()


# ==========================================================================
#  ★ v25：闲时任务设置（检测到鼠标 / 键盘空闲够久，就悄悄跑一次）
# ==========================================================================
IDLE_MIN_MINUTES = 1
IDLE_MAX_MINUTES = 240
DEFAULT_IDLE_MINUTES = 15
# 两次闲时运行之间至少隔多久（避免刚跑完又立刻跑）
IDLE_RULES_GAP_SEC = 1800          # 自动标签规则：30 分钟
IDLE_INDEX_GAP_SEC = 3600          # 索引扫描：60 分钟
# 每批之间的喘气时间（越大越「缓慢」，越不抢网盘 / CPU）
IDLE_RULES_CHUNK = 200
IDLE_RULES_PAUSE = 0.15
IDLE_INDEX_PAUSE = 0.05
# 用户一动鼠标 / 键盘，闲时任务多久内自觉收工
IDLE_STOP_WITHIN_SEC = 25.0


def load_idle_settings():
    """读闲时任务设置（存在设置文件的 idle_jobs 里）。"""
    data = _load_full_settings()
    d = data.get("idle_jobs")
    if not isinstance(d, dict):
        d = {}

    def _minutes(key):
        try:
            v = int(d.get(key, DEFAULT_IDLE_MINUTES))
        except Exception:
            v = DEFAULT_IDLE_MINUTES
        return max(IDLE_MIN_MINUTES, min(IDLE_MAX_MINUTES, v))

    def _ts(key):
        try:
            return float(d.get(key) or 0)
        except Exception:
            return 0.0

    return {
        "rules_enabled": bool(d.get("rules_enabled", True)),
        "rules_minutes": _minutes("rules_minutes"),
        "rules_last": _ts("rules_last"),
        "index_enabled": bool(d.get("index_enabled", True)),
        "index_minutes": _minutes("index_minutes"),
        "index_last": _ts("index_last"),
    }


def save_idle_settings(**kw):
    """写闲时任务设置（只覆盖传进来的键）。"""
    data = _load_full_settings()
    d = data.get("idle_jobs")
    if not isinstance(d, dict):
        d = {}
    d.update(kw)
    data["idle_jobs"] = d
    return _save_full_settings(data)


# ==========================================================================
# ★ v25 补丁37：「粗体中文」在这个 Tk 上量不出尺寸 —— 必须绕开
#
#  实测（你这台机器，Python 3.12 + Microsoft YaHei UI）：
#     font=("Microsoft YaHei UI", 11)         → 行高 20 像素  ✓ 正常
#     font=("Microsoft YaHei UI", 11, "bold") → 行高 4800921 像素 ✗
#                                              （字号被算成 1467012970）
#  也就是说：**凡是「具体字体族 + bold」的控件，请求尺寸都会变成几百万像素**。
#  后果不只是字难看 —— 文件列表上方那个标题就是这种写法，它被撑成
#  4 x 4,800,850 像素，把**整个文件区挤成 1 像素高**；而画布只有 1 像素时
#  Tk 就不再往它投递鼠标事件 → 这就是用户报的
#  「**单击没法选中文件，只可以框选**」的真正原因（框选靠拖动，还能勉强进来）。
#
#  修法：把 FONT 换成一个**一定能量的字体族**。实测 Arial / TkDefaultFont
#  加粗都正常（行高 18 / 15）。程序里绝大多数文字是中文，所以优先挑一个
#  系统里存在、且加粗能正常测量的中文字体；找不到就退回 TkDefaultFont。
#
# ★★ v25 补丁41：上面这个修法**治标不治本**，用户反馈「字体还是小、
#   而且大小不均匀」，我把根因挖到底了：
#     · `Microsoft YaHei UI`（微软雅黑，本该用的）加粗时行高会变成
#       4801101 —— 于是被上面 `<=200` 这个条件**当成坏字体跳过**；
#     · 名单往后捋，`Microsoft JhengHei UI`（**繁体**正黑）加粗行高 19
#       正常，就被选中了。
#   后果：全程序用的是**繁体版正黑**，它行高只有 17，比微软雅黑的 19
#   小一截 —— 所以字**看着小**；而少数字体是写死 Arial 的（行高 18），
#   两者混在一起就**大小不均匀**。
#   实测数据（size=10）：
#     Microsoft YaHei UI   行高 19  ← 应该用这个
#     Microsoft JhengHei UI 行高 17 ← 实际用了这个
#   真正的修法：**微软雅黑本身没毛病，是「雅黑 + bold」这个组合在 Tk 上
#   量不出来**。所以不再「因为加粗坏就把雅黑整族丢掉」，而是
#   「雅黑照用，只是别给它加粗」（加粗的地方改用颜色/底色区分）。
FONT_PREFERRED = [
    "Microsoft YaHei UI", "Microsoft YaHei", "微软雅黑",
    "Microsoft JhengHei UI", "Microsoft JhengHei",
    "SimHei", "SimSun", "Noto Sans SC", "Noto Sans CJK SC",
    "Source Han Sans SC",
]

# 微软雅黑的几个名字（这几个族**不能用 bold**，见上面的说明）
FONT_NO_BOLD_FAMILIES = {
    "Microsoft YaHei UI", "Microsoft YaHei", "微软雅黑",
}


def _pick_font_family(probe_root=None):
    """挑一个「量得出尺寸、且是中文」的字体族，并把结果写进全局 FONT / BOLD。

    ★ 注意：函数里要给 FONT / BOLD 赋值，必须先 `global FONT, BOLD`，
      否则 Python 会把它们当成局部变量、**根本写不回模块级** —— 那样
      main() 创建 widget 时还是看到 fallback "TkDefaultFont"，中文字体
      就出不来（用户看到的就是一堆方框 / 错位的字）。

    ★★ v26（2026-10-03）：接受 probe_root 参数。

    ★ v25 补丁41 重写。旧版有两个毛病：
      ① 判定用的是**加粗**行高 —— 而微软雅黑加粗在这台机器上量出来是
         4801101，于是「本程序最该用的字体」被自己排除掉了；
      ② 排除雅黑之后选中了**繁体**正黑，字就变小了。
    现在改成：
      · 用**常规**（不加粗）行高来判定 —— 雅黑常规行高 19，正常通过，
        所以会被第一个选中（正是我们要的）；
      · 再加一道「中文能不能量出来」的检查，防止选到纯英文字体。

    ★★ v26（2026-10-03）：接受 probe_root 参数。
      原来这个函数在 import 时跑（`FONT = _pick_font_family()`，第 3922 行），
      会**自己新建一个 Tk 根窗口**专门用来探测字体 —— 而 `main()` 后面又会
      建一个 Tk 根。**这 92ms 重复创建浪费在 cProfile 里一眼就能看到**。
      现在改成：probe_root 不传时仍然是老行为（自己建 Tk），但 main() 里会
      把已经建好的 Tk 根传进来 —— 完全跳过这次重复创建，**实测能省 92ms
      启动时间**。
      · 探测结果写入模块级 FONT 和 BOLD 两个全局变量（首次探测后所有
        `font=(FONT, ...)` / `weight=BOLD` 都立刻拿到正确值）；
      · 探测失败时 FONT / BOLD 保持调用方传入的 fallback 值（一般是
        "TkDefaultFont" / "normal"），不会抛错。
    """
    import tkinter as _tk
    import tkinter.font as _tkfont

    # ★★ v26：必须声明 global，否则下面 FONT = chosen 写的是局部变量，
    #   模块级的 FONT 永远是 fallback，main() 里看到的就不是真字体。
    global FONT, BOLD

    own_root = False
    if probe_root is None:
        try:
            probe_root = _tk.Tk()
            probe_root.withdraw()
            own_root = True
        except Exception:
            return "TkDefaultFont"

    chosen = None
    try:
        fams = set(_tkfont.families(probe_root))
        for name in FONT_PREFERRED:
            if name not in fams:
                continue
            try:
                # ① 常规行高必须正常（这才是「字体好不好」的可靠信号）
                # ★ tkfont.Font 没有 master 参数 —— 默认就用当前的 Tk 根
                #   （probe_root 已经存在，所以 Font 自然挂在它下面）。
                f = _tkfont.Font(family=name, size=11)
                ls = f.metrics("linespace")
                if not (6 <= ls <= 200):
                    continue
                # ② 得能画出中文（防止选到纯英文族，中文会变方框）
                try:
                    if f.measure("中") <= 0:
                        continue
                except Exception:
                    pass
                # ③ 加粗坏不坏不再一票否决 —— 选出来后单独探测（见 _bold_ok）：
                #    加粗坏的话，用这个字体时全局禁用加粗。
                #    ★ 注意：这里**必须写死字面的 "bold"**，不能写 BOLD 常量
                #      （BOLD 是调用 _bold_ok() 算出来的，而 _bold_ok 又要
                #       探测 "bold"，绕回去就是死循环）。
                try:
                    b = _tkfont.Font(family=name, size=11, weight="bold")
                    if not (6 <= b.metrics("linespace") <= 200):
                        pass  # 这个字体不能用 bold —— 选完后让 _bold_ok 处理
                except Exception:
                    pass
                chosen = name
                break
            except Exception:
                continue
    except Exception:
        pass
    finally:
        if own_root:
            try:
                probe_root.destroy()
            except Exception:
                pass

    # 把结果写进全局。失败 / 一个都不行 → 保持调用方传入的 fallback。
    if chosen:
        FONT = chosen
        BOLD = "bold" if _bold_ok(chosen) else "normal"
    return chosen or "TkDefaultFont"


def _bold_ok(family=None):
    """★ v25 补丁41：这个字体族**能不能加粗**。

    不能加粗的族（微软雅黑就是）如果硬写 bold，Tk 会把控件请求尺寸
    算成几百万像素 —— 那正是「标题把文件区挤成 1 像素、于是单击
    选不中」的老病根。所以这里统一判一次。
    返回 True 才允许在 font= 里写 "bold"。
    """
    try:
        fam = family or FONT
        if fam in FONT_NO_BOLD_FAMILIES:
            return False
        import tkinter.font as _tkfont
        # ★ 这里也必须写字面的 "bold"（正在探测「bold 行不行」，
        #   用 BOLD 常量会绕回来自己调自己）
        f = _tkfont.Font(family=fam, size=11, weight="bold")
        ls = f.metrics("linespace")
        return 6 <= ls <= 200
    except Exception:
        return False


def _bfont(size=10, family=None):
    """★ v25 补丁41：要「加粗」的地方统一走这里。

    字体能量加粗就真加粗；量不出来（微软雅黑）就退回常规字重 ——
    宁可字不粗，也绝不能让控件被撑成几百万像素。
    """
    fam = family or FONT
    if _bold_ok(fam):
        return (fam, size, "bold")
    return (fam, size)


# ★★ v26（2026-10-03）：FONT / BOLD 不再在 import 时探测。
#   原来这俩在模块级直接探测（`FONT = _pick_font_family()`，再加
#   `_bold_ok` 判 BOLD）—— 这要**自己建一个 Tk 根窗口**专门探测字体
#   （实测 92ms），而 main() 下面又会建一个 Tk 根，**重复创建浪费**。
#   现在改成：
#     · 模块级先放安全 fallback（万一 main() 没跑 / 程序被 import 用来
#       别的用途，控件也能用 TkDefaultFont 起来；实测 _pick_font_family
#       失败时返回的就是这个值，所以行为一致）；
#     · main() 里用已经建好的 Tk 根调
#         `_pick_font_family(probe_root=root)`
#       探测成功就把 FONT 和 BOLD 覆盖成真值 —— 探测用的是同一个 Tk 根，
#       不会再付出 92ms（cProfile 里就能看到）。
FONT = "TkDefaultFont"
BOLD = "normal"

# ★★ v26（2026-10-01）：**统一的界面字号。**
#
#   用户反馈：「整个程序的字体大小能不能和主程序右下角那些
#   问题、标签盒、标签条等按钮一样」。
#
#   为什么会不一样：
#     · 右下角那些按钮是 ttk 按钮，没写 font ->
#       用的是 Tk 默认字体（TkDefaultFont），**size = 14**；
#     · 而程序里大部分地方（文件列表、右键菜单、上面的菜单栏）
#       都把 size 写死成了 **9**。
#     实测：size=9 行高 17 像素，size=14 行高 25 像素 ——
#     差了一整档，看着就是「大小不匀称」。
#
#   现在：统一用 **UI_FONT_SIZE**（14，和 Tk 默认一致）。
#   想整体调大/调小，只改这一个数字就行。
#   （注：它不是“字号”而是“逻辑字号”，Tk 会按 tk scaling
#     自己换算成真实像素 —— 所以「界面缩放」那个设置依然管用。）
UI_FONT_SIZE = 14
# 小一号：给“次要信息”用（比如状态栏尾巴、图标下面的小字）。
#   不要再写 7/8/9/10 这种碎数字了。
UI_FONT_SIZE_SMALL = 13


def _tree_row_height():
    """★ 文件树（目录树）一行该多高 —— **按字体自己算**，别写死。

    ★★ 2026-10-07 为什么加这个（用户报的 bug）：
      原来两处都写死 `rowheight=22`，而字体是 13 号 ——
      **13 号字实际要 24 像素左右的行高，22 装不下**，
      于是字的上下被切掉，用户看到的就是
      「**文件目录的字体被纵向挤压，只显示了半截**」。

    ★ 算法：`linespace`（这一行字本身多高）+ 10 像素留白（看着不挤），
      再兜个底不小于 24。

    ★ 为什么做成函数、两处都调它：
      建树那处（搜 `_tree_rowh`）和**主题表那处**必须用**同一个值** ——
      否则「换一次皮肤」会把行高改回 22，白天修好了、一进夜间又压扁。
    """
    try:
        ls = tkfont.Font(font=(FONT, UI_FONT_SIZE_SMALL)).metrics("linespace")
        return max(24, int(ls) + 10)
    except Exception:
        return UI_FONT_SIZE_SMALL + 11      # 兜底：13 → 24



def _current_ui_scale():
    """★ 问出"当前界面缩放系数" —— **多路兜底**，拿不到就 1.0。

    ★★ 2026-10-07 为什么专门写这个（踩的坑，写清楚）：
      我第一版 `_dlg_size()` 里直接写 `float(UI_SCALE)` ——
      而 **`UI_SCALE` 是"运行时才被赋值的全局变量"**：
      它在模块加载时**根本不存在**，要等 `main()` 里
      `_auto_ui_scale()` / `load_ui_scale()` 算出来才有。
      → 于是那句抛 `NameError` → 被 `except` 吞掉 → `s = 1.0`
      → **所有子窗口永远不缩放**（用户报「**感觉好像没变大**」）。
      ★ **这是典型的"静默失效"：不报错、也不干活。**

    ★ 所以这里**按优先级多路找**（哪条能用用哪条）：
      ① 模块全局 `UI_SCALE`（程序跑起来之后就有）
      ② 设置文件里的 `ui_scale`（用户自己调过的话）
      ③ 从 `tk scaling` 反推（`scaling / 1.333` 约等于显示缩放）
      ④ 都拿不到 → 1.0
    """
    # ① 模块全局（程序已经跑起来了）
    try:
        s = float(globals().get("UI_SCALE") or 0)
        if s > 0:
            return max(MIN_UI_SCALE, min(MAX_UI_SCALE, s))
    except Exception:
        pass
    # ② 设置文件
    try:
        s = float(load_ui_setting("ui_scale", 0) or 0)
        if s > 0:
            return max(MIN_UI_SCALE, min(MAX_UI_SCALE, s))
    except Exception:
        pass
    # ③ 从 tk scaling 反推（72dpi 基准 → 1.0）
    try:
        import tkinter as _tk
        _r = _tk._default_root
        if _r is not None:
            sc = float(_r.tk.call("tk", "scaling"))
            if sc > 0:
                return max(MIN_UI_SCALE,
                           min(MAX_UI_SCALE, sc / (96.0 / 72.0)))
    except Exception:
        pass
    return 1.0


def _dlg_size(w, h, minimum=(320, 240)):
    """★ 把一个「子窗口尺寸」按**当前界面缩放**放大 —— 返回 (宽, 高)。

    ★★ 2026-10-07 新增（用户报「子窗口感觉有些小，可能这种子窗口
       都需要和字体、显示比例一起缩放吧」）：
      这些窗口原来写死 `geometry("1000x640")` ——
      而 `tk scaling` 会把**字**放大，于是缩放 125% 时
      **字大了、窗口没大 → 内容挤不下**，用户得自己拉。
      → 现在所有子窗口的尺寸都过这个函数，跟着缩放一起变。

    ★ 有上下限：
      · 下限 `minimum` —— 再小也得放得下按钮（不然就没法用了）
      · 上限 = 屏幕的 92% —— 免得在大屏上开出一个"超出屏幕"的窗口

    ★★ 2026-10-07 修正：缩放系数改问 `_current_ui_scale()` ——
      原来直接读 `UI_SCALE`，而它**运行时才有**，
      模块加载时是 `NameError` → 被吞 → **永远 1.0（不缩放）**。
    """
    s = _current_ui_scale()
    try:
        w2 = int(round(float(w) * s))
        h2 = int(round(float(h) * s))
    except Exception:
        w2, h2 = int(w), int(h)
    try:
        w2 = max(int(minimum[0]), w2)
        h2 = max(int(minimum[1]), h2)
    except Exception:
        pass
    try:
        import tkinter as _tk
        _r = _tk._default_root
        if _r is not None:
            _sw = _r.winfo_screenwidth()
            _sh = _r.winfo_screenheight()
            w2 = min(w2, int(_sw * 0.92))
            h2 = min(h2, int(_sh * 0.92))
    except Exception:
        pass
    return w2, h2


def _dlg_geom(w, h, minimum=(320, 240)):
    """★ 直接返回 `geometry()` 要的 "WxH" 字符串（按缩放放大）。"""
    w2, h2 = _dlg_size(w, h, minimum)
    return "%dx%d" % (w2, h2)




# ==========================================================================
#  ★★ 2026-10-07 新增：**统一的"配色登记表"**
#  --------------------------------------------------------------------------
#  ★★ 为什么要这个（用户要求「多设点冗余、留点接口，以后方便改」）：
#    以前"哪个控件是什么颜色"散在全文件 100 多处，而且有两套机制打架：
#      ① 建控件时 `bg=theme_get(...)` —— **只对一次**，换皮肤不会重刷
#      ② `_retheme_tree()` 的「按对照表翻色」—— **分不清"这值是底还是字"**，
#         于是会把底色翻成字色（实测：分类库切到夜间变成 #d6d7db）
#    → 每加一个容器就多一处"夜间发灰"，**补不完**。
#
#  ★ 现在：**控件自己登记"我是什么角色"，换皮肤时统一刷**。
#    新增控件只要：
#        w = tk.Frame(parent)
#        register_themed(w, "card")        # ← 就这一行
#
#  ★ 角色表（跟主题色一一对应，想换配色改 `_THEME_*` 就行）：
#       win / card / panel / panel2 / canvas / text
#       fg / fg_dim / line / accent / select_bg
# ==========================================================================
_THEMED_REGISTRY = []       # [(widget, [ (属性名, 主题键) ... ])]


def register_themed(widget, role, extra=None):
    """★ 把一个控件登记进"换皮肤时要重刷"的表里。

    role：角色名。**这里会自动补上 `_bg` 后缀** ——
          因为主题表里的键叫 `win_bg` / `card_bg` / `panel_bg`，
          而调用方写 `register_themed(w, "win")` 更省事。
          ★★ 踩过的坑：一开始直接拿 role 当主题键去 `theme_get(role)`，
            于是 `theme_get("win")` **拿不到**（正确的键是 `win_bg`）→
            `opts` 为空 → **静默什么也没刷**（sidebar 一直不变色）。
          ★ 所以这里显式做映射，**不要靠"名字刚好一样"**。
    extra：额外要刷的 `[(属性名, 主题键), ...]`，比如
           `[("insertbackground", "fg")]`（Text 的光标色）。
    ★ 登记过的控件**不再走翻色表**（`_retheme_tree` 里会跳过它们）。
    """
    # ★ 角色名 → 主题键（底色类都带 _bg 后缀）
    BG_ROLE2KEY = {
        "win": "win_bg",
        "card": "card_bg",
        "panel": "panel_bg",
        "panel2": "panel_bg2",
        "canvas": "canvas_bg",
        "text": "text_bg",
        "stripe": "stripe_bg",
        "hover": "hover_bg",
    }
    FG_ROLE2KEY = {
        "fg": "fg",
        "fg_dim": "fg_dim",
        "line": "line",
        "accent": "accent",
        "danger": "danger",
        "warn": "warn",
        "ok": "ok",
    }
    try:
        pairs = []
        if role in BG_ROLE2KEY:
            pairs.append(("bg", BG_ROLE2KEY[role]))
        elif role in FG_ROLE2KEY:
            pairs.append(("fg", FG_ROLE2KEY[role]))
        for p in (extra or []):
            if p not in pairs:
                pairs.append(p)
        if not pairs:
            return widget
        _THEMED_REGISTRY.append((widget, pairs))
        # ★ 顺手把自己从"翻色表"的管辖里摘出来
        try:
            _THEMED_MANAGED.add(widget)
        except Exception:
            pass
        # 立刻按当前皮肤上一次色（免得等下次换皮肤才生效）
        apply_themed(widget)
    except Exception:
        pass
    return widget


def apply_themed(widget=None):
    """★ 把登记过的控件按**当前皮肤**刷一遍。

    ★ 什么时候调：`_retheme_custom_parts()` 里（每次换皮肤都会走）。
    ★ 传 widget 就只刷那一个（`register_themed` 里立刻用）。
    """
    try:
        reg = _THEMED_REGISTRY if widget is None else [
            (w, p) for (w, p) in _THEMED_REGISTRY if w is widget]
        dead = []
        for w, pairs in reg:
            try:
                if not w.winfo_exists():
                    dead.append((w, pairs))
                    continue
            except Exception:
                dead.append((w, pairs))
                continue
            opts = {}
            for attr, key in pairs:
                try:
                    opts[attr] = theme_get(key)
                except Exception:
                    continue
            if opts:
                try:
                    w.configure(**opts)
                except Exception:
                    # tk 控件用 bg/fg；ttk 控件不吃，忽略
                    pass
        for d in dead:
            try:
                _THEMED_REGISTRY.remove(d)
                _THEMED_MANAGED.discard(d[0])
            except Exception:
                pass
    except Exception:
        pass


# ★ 「登记过的控件」集合 —— `_retheme_tree()` 会跳过它们，免得被翻歪
try:
    _THEMED_MANAGED
except NameError:
    _THEMED_MANAGED = set()


def apply_unified_fonts(root):
    """★★ v26（2026-10-01）：**把 Tk 的命名字体统一成同一个字号。**

    用户反馈：「整个程序的字体大小能不能和主程序右下角那些问题、标签盒、
    标签条等按钮一样」。

    为什么会有大有小：Tk 里有一批**命名字体**（TkDefaultFont / TkMenuFont /
    TkTextFont / TkHeadingFont…），**没写 font= 的控件**都用它们。
    这套字体是 Tk 按系统 DPI 自己挑的，在这台机器上实测：
      · ttk 按钮（右下角那些）用的是 14；
      · **tk.Menu（菜单栏、右键菜单）实际是 9** —— 差了一大截。
    而程序里又有大量写死的字号，于是三套数字（9 / 14 / 写死的各种）混在一起，
    看着就是「大小不匀称」。

    做法：程序一启动就把**所有命名字体**统一成 `FONT + UI_FONT_SIZE`，
    再把 `option_add` 里的菜单字体也指过去。这样：
      · 菜单、ttk 控件、Label……只要没自己写 font 的，全部一致；
      · 自己写了 font=(FONT, UI_FONT_SIZE) 的，数值也一样。
    想整体调大调小，只改 UI_FONT_SIZE 那一个数字就行。
    """
    try:
        import tkinter.font as _f
    except Exception:
        return
    # ① 把所有内置命名字体改掉
    for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont",
                 "TkHeadingFont", "TkTooltipFont", "TkCaptionFont",
                 "TkSmallCaptionFont", "TkIconFont"):
        try:
            f = _f.nametofont(name, root=root)
            f.configure(family=FONT, size=UI_FONT_SIZE)
        except Exception:
            continue
    # ② TkFixedFont 是等宽字体（日志用），只改大小、保留「等宽」这个特性；
    #    等宽字体族名要单独挑，不能塞雅黑进去。
    try:
        f = _f.nametofont("TkFixedFont", root=root)
        cur = f.actual("family")
        if not cur:
            cur = "Consolas"
        f.configure(family=cur, size=UI_FONT_SIZE)
    except Exception:
        pass
    # ③ 菜单还有一条「option 数据库」的路子（有些平台不吃命名字体）
    try:
        root.option_add("*Menu.font", "{%s} %d" % (FONT, UI_FONT_SIZE))
        root.option_add("*Menubutton.font", "{%s} %d" % (FONT, UI_FONT_SIZE))
        root.option_add("*Text.font", "{%s} %d" % (FONT, UI_FONT_SIZE))
        root.option_add("*Listbox.font", "{%s} %d" % (FONT, UI_FONT_SIZE))
    except Exception:
        pass

CAT_COLORS = [
    "#5b8def", "#e84393", "#00b894", "#f39c12",
    "#8e44ad", "#e17055", "#0984e3", "#00cec9",
]


# ==========================================================================
# ★★ 2026-10-06 新增：**皮肤（配色方案）系统 —— 主要是为了「晚上不刺眼」** ★★
#
#   用户原话：「写套夜间皮肤，现在这个晚上不开灯有点闪」。
#
#   ● 为什么不是「把每个颜色改一遍」：
#       全文件有 **72 种不同的硬编码颜色**（bg=theme_get("card_bg") 31 处、
#       bg=theme_get("panel_bg") 27 处、#f0f1f3 9 处 ……）。
#       真要一处一处改，改漏一处就是「黑底上突然一块白板」，
#       而且以后再想加皮肤还得到处改 —— 那是最容易改坏的做法。
#
#   ● 现在的做法（外面成熟软件都这么干）：**建立一张「颜色对照表」**。
#       深色皮肤 = 一张「浅色 → 深色」的映射表。
#       切皮肤的时候：
#         ① 把所有**颜色常量全部换成皮肤里的值**（下面的 _apply_theme_constants）；
#         ② 把**已经建好的控件**逐个扫一遍，按对照表把颜色换掉
#            （下面的 _retheme_widgets）。
#       这样「以后再加一套皮肤」只要多写一张对照表，不用动任何界面代码。
#
#   ● 为什么要改常量（而不是只扫控件）：
#       像 `_show_pil_image` 里写死的 `bg=theme_get("canvas_bg")`，只有**打开图片时**
#       才建那个控件。如果只扫「现在存在的控件」，等你晚上点开一张图片，
#       那块地方还是浅色的 —— 白闪一下，正是用户嫌刺眼的那种。
#       所以常量也必须跟着换，保证**以后新造的控件**也是深色的。
#
#   ● 反色规则（下面 `_dark_of`）：
#       深色皮肤不是把颜色随便变黑 —— 那样标签颜色、状态颜色全毁了。
#       规则是：**只把「很亮的」颜色按亮度翻过来，暗的保持色相**。
#       于是：白底 → 深灰底；深灰字 → 浅灰字；蓝色高亮 → 亮一点的蓝。
#       这样标签胶囊、状态红绿、选中蓝，全都还能认出来。
# ==========================================================================

# 当前皮肤名（"light"=白天 / "dark"=夜间）
THEME_NAME = "light"

# ---- 白天（= 现在的样子，一个像素都不改）----
_THEME_LIGHT = {
    "name": "light",
    "win_bg": "#f0f1f3",        # 主窗口 / 各块底板
    "card_bg": "#ffffff",       # 内容区（卡片）
    "panel_bg": "#fcfcfd",      # 面板底
    "panel_bg2": "#fbfbfd",     # 面板底（次）
    "text_bg": "#ffffff",       # 文本框 / 画布底
    "fg": "#2c2f33",            # 正文字
    # ★★ 2026-10-07 调深（实测出来的）：
    #   旧值 #9aa0a6 在浅底 #f0f1f3 上**对比度只有 2.3** ——
    #   **比夜间模式还差**（夜间那个是 5.0）。
    #   ★ 所以用户说"好多地方字看不清"，**浅色模式其实更严重**。
    #   新值 #6b7078 → 对比度约 4.6，达到正文标准。
    "fg_dim": "#6b7078",        # 次要字
    # ★ 分隔线也加深一点（旧值 #e8e8ec 在白底上几乎看不见，对比度 1.1）
    "line": "#d8d9de",          # 分隔线
    "sash": "#c9d3e2",          # 分栏条
    "sash_active": "#8fb0dd",   # 分栏条（鼠标放上去）
    "accent": "#2c6fd1",        # 强调色（选中 / 链接）
    "select_bg": "#cfe2ff",     # 选中底色
    "canvas_bg": "#f4f4f6",     # 画布底（PDF/图片那一片）
    "stripe_bg": "#f7f8fa",     # 文件列表隔行那一行
    "danger": "#c0392b",        # 「未打标签」这类提醒色
    "warn": "#b8860b",
    "ok": "#27ae60",
    # ★ 鼠标放上去 / 选中的那一小块底色（原来是各种浅蓝浅绿浅紫）
    "hover_bg": "#eef4ff",
    "find_bg": "#fff3cd",       # 搜索命中的高亮条
    "scroll_bg": "#f0f0f2",     # 滚动条槽
    "scroll_fg": "#c1c1c6",     # 滚动条滑块
}

# ---- 夜间（新做的，专治「不开灯刺眼」）----
#   说明：底色没有用纯黑（#000）——纯黑配白字对比太硬、看久了更累。
#   这里用 #1e1f22（外面那些成熟软件夜间模式基本都在这个深度），
#   字用 #d6d7db（不是纯白），看久了眼睛舒服。
_THEME_DARK = {
    "name": "dark",
    "win_bg": "#1e1f22",
    "card_bg": "#26272b",
    "panel_bg": "#222327",
    "panel_bg2": "#25262a",
    "text_bg": "#1a1b1e",
    "fg": "#d6d7db",
    # ★★ 2026-10-07 调亮（用户报「夜间模式好多地方字体颜色都比较深、容易看不清」）。
    #   实测对比度（WCAG 标准：正文要 ≥4.5，次要信息 ≥3.0）：
    #     旧值 #8b8d94 → 对深底只有 5.0，而且**实际用的地方背景往往更暗/更杂**
    #     （卡片 #26272b 上只有 4.5，正好卡在及格线上，小字就很吃力）
    #   新值 #a9abb3 → 明显亮一档，次要信息也看得清了。
    "fg_dim": "#a9abb3",
    # ★★ 2026-10-07 分隔线调亮：旧值 #3a3c42 对比度只有 **1.5** ——
    #   **基本等于看不见**（用户说"好多地方看不清"就有它一份）。
    #   新值 #4a4d55 → 对比度约 2.4，隐约看得见但不抢眼（分隔线不该抢眼）。
    "line": "#4a4d55",
    "sash": "#3c3f46",
    "sash_active": "#5a82c4",
    "accent": "#7aa7e8",
    "select_bg": "#31456b",
    "canvas_bg": "#202124",
    "stripe_bg": "#2a2c30",
    # ★ 夜间这几个提醒色要**柔一点** —— 原来那个正红 #c0392b 在深底上
    #   亮得像警示灯，晚上特别晃眼。这里换成降了亮度、带一点灰的红黄绿，
    #   意思还看得出来，但不刺眼。
    "danger": "#e07b6d",
    "warn": "#d8b061",
    "ok": "#6fbf8a",
    "hover_bg": "#2f3542",
    "find_bg": "#4a4224",
    "scroll_bg": "#1b1c1f",
    "scroll_fg": "#4a4d55",
}

_THEMES = {"light": _THEME_LIGHT, "dark": _THEME_DARK}

# ==========================================================================
#  ★★★ 2026-10-08 **给"自定义皮肤"预留的入口**（用户要求："要预留好自定义皮肤
#  入口啊，要配合未来会…"）★★★
#  ------------------------------------------------------------------------
#  ★★ 好消息：本程序的皮肤系统**天生就是可扩展的** ——
#     一切颜色都走 `theme_get(key)`，而它只是查一个字典：
#         `_THEMES[THEME_NAME].get(key)`
#     → **往 `_THEMES` 里塞一套新配色，整个程序就换皮了，一行调用方代码都不用改。**
#  ★★ 所以这里要做的**不是"改造"，而是"把规矩立下来"** ——
#     让以后加皮肤的人知道：**照这个接口来就行**。
#
#  ★ 一套合法皮肤 = 一个 dict，**必须包含下面这些键**（缺一个就会有一块不变色）。
#    ★ 以后加键也往这儿加，`check_theme()` 会自动帮你挑出来缺哪个。
# ==========================================================================
THEME_REQUIRED_KEYS = (
    "name",         # 皮肤名（内部用，比如 "light" / "dark" / "my_skin"）
    "label",        # ★ 给人看的名字（菜单里显示这个）—— 可选，缺了就显示 name
    "win_bg",       # 主窗口 / 各块底板
    "card_bg",      # 内容区（卡片）
    "panel_bg",     # 面板底
    "panel_bg2",    # 面板底（次）
    "text_bg",      # 文本框 / 画布底
    "fg",           # 正文字
    "fg_dim",       # 次要字（★ 待清算 #17-③ 就是它用得太广）
    "line",         # 分隔线
    "sash",         # 分栏条
    "sash_active",  # 分栏条（鼠标放上去）
    "accent",       # 强调色（选中 / 链接）
    "select_bg",    # 选中背景
    "canvas_bg",    # 画布底
    "stripe_bg",    # 隔行条纹
    "danger",       # 危险（红）
    "warn",         # 警告（黄）
    "ok",           # 正常（绿）
    "hover_bg",     # 悬停背景
    "find_bg",      # 搜索命中
    "scroll_bg",    # 滚动条
    "scroll_fg",    # 滚动条滑块
)


# ★ 皮肤里**可选**的"美化项"（没有就表示"不启用"）：
#   `background_image` —— 背景图路径
#   `background_mode`  —— cover / contain / tile / center（默认 cover）
#   `background_blur`  —— 高斯模糊半径（0=不模糊；8~20 像毛玻璃）
#   `panel_alpha`      —— 面板"看着半透明"的程度 0~100（0=面板实色）
#   ★ 这些**不在 THEME_REQUIRED_KEYS 里**（缺了不影响配色）——
#     所以自定义皮肤**可以只给颜色**，也可以顺手带一张背景图。
THEME_OPTIONAL_KEYS = ("background_image", "background_mode",
                       "background_blur", "panel_alpha")


def register_theme(name, palette, label=None):
    """★★ **注册一套皮肤** —— 这是"自定义皮肤"的**唯一正式入口**。

    ★ 用法（以后想做"从文件读皮肤"，就在启动时读 JSON 然后调这个）：
        register_theme("my_skin", {
            "name": "my_skin", "label": "我的皮肤",
            "win_bg": "#101418", "card_bg": "#161b22", ...
        })
        apply_theme(root, "my_skin")        # 就用上了

    ★ 参数：
      · `name`    —— 皮肤的内部名（用来 `apply_theme(root, name)`）
      · `palette` —— 一整套颜色（dict）；缺的键会**自动从默认皮肤继承**
      · `label`   —— 给人看的名字（菜单里显示）；不传就用 `name`

    ★★ 为什么"缺的键自动继承"（**这是冗余，也是防呆**）：
      一套皮肤有 20+ 个键，手写**一定会漏**。
      漏了的话，那块 UI 就**不变色**（出现"白斑"）——
      而这正是用户一直在报的那类问题（错题本 #123）。
      → 所以这里：**以 `light` 为底，用你给的颜色覆盖** ——
        **永远不会缺键**，最差也就是"某个颜色没改"（比"不变色"好得多）。

    ★ 返回：`True` 成功 / `False` 失败（不会抛异常，出错有日志）。
    """
    try:
        if not isinstance(palette, dict):
            raise TypeError("palette 得是个 dict")
        name = str(name or "").strip()
        if not name:
            raise ValueError("name 不能是空的")
        # ★ 以 light 为底 → 保证"键永远是齐的"（见上面说明）
        merged = dict(_THEME_LIGHT)
        merged.update(palette)
        merged["name"] = name
        merged["label"] = str(label or palette.get("label") or name)
        # ★ 记一份"缺了哪些键"（只记日志，不拦 —— 缺的已经继承了）
        _missing = [k for k in THEME_REQUIRED_KEYS if k not in palette]
        if _missing:
            try:
                note_swallowed(
                    "自定义皮肤「%s」少给了 %d 个颜色，已从默认皮肤继承：%s"
                    % (name, len(_missing), "、".join(_missing[:8])),
                    None, level="warn")
            except Exception:
                pass
        _THEMES[name] = merged
        return True
    except Exception as exc:
        try:
            note_swallowed(T("注册皮肤失败（{x}）", x=(name),), exc)
        except Exception:
            pass
        return False


def apply_theme_names():
    """★ 现在**有哪些皮肤**（菜单要用这个，**不要写死 light/dark**）。

    ★ 为什么要这个（**这就是"预留入口"的意义**）：
      原来菜单里写的是 `add_radiobutton(label=T("白天"), value="light")` ——
      **皮肤名硬编码在菜单里**。以后加了自定义皮肤，菜单里**看不到**。
      → 改成"**问 `_THEMES` 有哪些**"，加皮肤就自动出现在菜单里，
        **菜单代码一行都不用改**。
    ★ 返回：`[(内部名, 显示名), ...]`（只读快照）。
    """
    out = []
    try:
        for k, v in _THEMES.items():
            try:
                out.append((k, T(str((v or {}).get("label") or k))))
            except Exception:
                out.append((k, k))
    except Exception:
        out = [("light", "light"), ("dark", "dark")]
    return out


def theme_has(name):
    """★ 有没有这套皮肤（给别人判断用，免得自己去翻 `_THEMES`）。"""
    try:
        return str(name) in _THEMES
    except Exception:
        return False


def check_theme(palette):
    """★ 体检一套皮肤：**缺哪些键、哪些颜色写错了** —— 给"自定义皮肤"用。

    ★ 返回 `(缺的键, 颜色不对的键)`，两个都是列表（空列表 = 没问题）。
    ★ 为什么要有这个：手写一套皮肤**很容易漏**，而这会导致"某块 UI 不变色"
      （用户报过好几次"夜间模式还有一片白"）。
      → 以后做"导入皮肤文件"时，**先跑这个检查**，把问题当场告诉用户，
        而不是让他自己去发现"哪个角落是白的"。
    """
    missing, bad = [], []
    try:
        for k in THEME_REQUIRED_KEYS:
            if k not in palette:
                missing.append(k)
        import re as _re
        for k, v in (palette or {}).items():
            if k in ("name", "label"):
                continue
            if not isinstance(v, str) or not _re.match(
                    r"^#[0-9a-fA-F]{6}$", v.strip()):
                bad.append("%s=%r" % (k, v))
    except Exception:
        pass
    return missing, bad


# ==========================================================================
#  ★★★ 2026-10-08 **背景图 + "假毛玻璃"**（用户要的美化效果）★★★
#  ------------------------------------------------------------------------
#  ★★ 用户原话：「我看他们挺喜欢搞个图片当背景什么的美化呢、
#     还有透明毛玻璃效果什么的，很多人都很喜欢」
#
#  ★★ 我实测了 5 轮（见 `文档\背景图和毛玻璃-实测报告.md`），结论：
#    · **背景图** ✔ 能做（`Label` + `place` 铺底层）
#    · **真毛玻璃** ⚠️ 能做，但**满屏控件时只有"控件之间的缝"能透出来**
#      —— 因为 Tk 的控件**没有透明这回事**（有底色就挡住）
#    · ★★ **但那些成熟软件的"毛玻璃"，大部分不是真透明** ——
#      是「**背景图 + 先模糊一遍**」**画**出来的。**这个 Tk 能做，
#      而且文字清楚**（因为不是真透明，是"看起来像"）。
#
#  ★★ 所以这里做三件：
#    ① `make_background_layer()` —— 铺背景图（支持 铺满/适应/平铺/居中）
#    ② 图先**高斯模糊**（"假毛玻璃"，`background_blur`）
#    ③ `auto_blend_panels()` —— **面板色自动调和**：
#       取图的平均色，跟原来的面板色混一下 → "看着像半透明"
#       ★ 不做这一步的话，面板是不透明实色，**背景图基本看不见**。
# ==========================================================================

# ★ 背景图的摆放方式
BG_MODES = ("cover",      # 铺满（按需裁剪，最常用）
            "contain",    # 完整显示（留边）
            "tile",       # 平铺
            "center")     # 居中（不缩放）


# ======================================================================
#  ★★★ 2026-10-08 **搬到独立文件了**（第 1 批拆分·续）：单位换算 + 网速/内存/硬盘显示文本
# ----------------------------------------------------------------------
#  ★ 为什么搬：量过 —— 纯函数、依赖少、被引用次数少。
#  ★ 怎么修（万一这个文件丢了）：见 `AIxiede拆分开\\程序分块\\_单位换算.py`；或从 `备份\\AIxiede.py.bak-搬小件前` 里拷回来
# ======================================================================
try:
    import _单位换算 as _m_单位换算
    try:
        _m_单位换算._set_app(sys.modules[__name__])
    except Exception:
        pass
    _BYTE_UNITS = _m_单位换算._BYTE_UNITS
    _bytes_text = _m_单位换算._bytes_text
    _kb_text = _m_单位换算._kb_text
    _bytes_per_sec_text = _m_单位换算._bytes_per_sec_text
    _NET_PREV = _m_单位换算._NET_PREV
    _net_speed_text = _m_单位换算._net_speed_text
    _mem_text = _m_单位换算._mem_text
    _disk_speed_text = _m_单位换算._disk_speed_text
except Exception as _e_单位换算:
    _ERR_单位换算 = _e_单位换算
    def _BYTE_UNITS(*_a, **_kw):
        raise RuntimeError(
            "模块 _单位换算.py 没找到或有问题（_BYTE_UNITS 用不了）。\n"
            "  原因：%r\n"
            "  怎么修：见 `AIxiede拆分开\\程序分块\\_单位换算.py`；或从 `备份\\AIxiede.py.bak-搬小件前` 里拷回来" % (_ERR_单位换算,))
    def _bytes_text(*_a, **_kw):
        raise RuntimeError(
            "模块 _单位换算.py 没找到或有问题（_bytes_text 用不了）。\n"
            "  原因：%r\n"
            "  怎么修：见 `AIxiede拆分开\\程序分块\\_单位换算.py`；或从 `备份\\AIxiede.py.bak-搬小件前` 里拷回来" % (_ERR_单位换算,))
    def _kb_text(*_a, **_kw):
        raise RuntimeError(
            "模块 _单位换算.py 没找到或有问题（_kb_text 用不了）。\n"
            "  原因：%r\n"
            "  怎么修：见 `AIxiede拆分开\\程序分块\\_单位换算.py`；或从 `备份\\AIxiede.py.bak-搬小件前` 里拷回来" % (_ERR_单位换算,))
    def _bytes_per_sec_text(*_a, **_kw):
        raise RuntimeError(
            "模块 _单位换算.py 没找到或有问题（_bytes_per_sec_text 用不了）。\n"
            "  原因：%r\n"
            "  怎么修：见 `AIxiede拆分开\\程序分块\\_单位换算.py`；或从 `备份\\AIxiede.py.bak-搬小件前` 里拷回来" % (_ERR_单位换算,))
    def _NET_PREV(*_a, **_kw):
        raise RuntimeError(
            "模块 _单位换算.py 没找到或有问题（_NET_PREV 用不了）。\n"
            "  原因：%r\n"
            "  怎么修：见 `AIxiede拆分开\\程序分块\\_单位换算.py`；或从 `备份\\AIxiede.py.bak-搬小件前` 里拷回来" % (_ERR_单位换算,))
    def _net_speed_text(*_a, **_kw):
        raise RuntimeError(
            "模块 _单位换算.py 没找到或有问题（_net_speed_text 用不了）。\n"
            "  原因：%r\n"
            "  怎么修：见 `AIxiede拆分开\\程序分块\\_单位换算.py`；或从 `备份\\AIxiede.py.bak-搬小件前` 里拷回来" % (_ERR_单位换算,))
    def _mem_text(*_a, **_kw):
        raise RuntimeError(
            "模块 _单位换算.py 没找到或有问题（_mem_text 用不了）。\n"
            "  原因：%r\n"
            "  怎么修：见 `AIxiede拆分开\\程序分块\\_单位换算.py`；或从 `备份\\AIxiede.py.bak-搬小件前` 里拷回来" % (_ERR_单位换算,))
    def _disk_speed_text(*_a, **_kw):
        raise RuntimeError(
            "模块 _单位换算.py 没找到或有问题（_disk_speed_text 用不了）。\n"
            "  原因：%r\n"
            "  怎么修：见 `AIxiede拆分开\\程序分块\\_单位换算.py`；或从 `备份\\AIxiede.py.bak-搬小件前` 里拷回来" % (_ERR_单位换算,))

# ======================================================================
#  ★★★ 2026-10-08 **搬到独立文件了**（第 1 批拆分·续）：背景图 + 颜色工具
# ----------------------------------------------------------------------
#  ★ 为什么搬：量过 —— 纯函数、依赖少、被引用次数少。
#  ★ 怎么修（万一这个文件丢了）：见 `AIxiede拆分开\\程序分块\\_背景图工具.py`；或从 `备份\\AIxiede.py.bak-搬小件前` 里拷回来
# ======================================================================
try:
    import _背景图工具 as _m_背景图工具
    try:
        _m_背景图工具._set_app(sys.modules[__name__])
    except Exception:
        pass
    _hex_to_rgb = _m_背景图工具._hex_to_rgb
    _rgb_to_hex = _m_背景图工具._rgb_to_hex
    blend_color_over = _m_背景图工具.blend_color_over
    average_color_of_image = _m_背景图工具.average_color_of_image
    make_background_layer = _m_背景图工具.make_background_layer
except Exception as _e_背景图工具:
    _ERR_背景图工具 = _e_背景图工具
    def _hex_to_rgb(*_a, **_kw):
        raise RuntimeError(
            "模块 _背景图工具.py 没找到或有问题（_hex_to_rgb 用不了）。\n"
            "  原因：%r\n"
            "  怎么修：见 `AIxiede拆分开\\程序分块\\_背景图工具.py`；或从 `备份\\AIxiede.py.bak-搬小件前` 里拷回来" % (_ERR_背景图工具,))
    def _rgb_to_hex(*_a, **_kw):
        raise RuntimeError(
            "模块 _背景图工具.py 没找到或有问题（_rgb_to_hex 用不了）。\n"
            "  原因：%r\n"
            "  怎么修：见 `AIxiede拆分开\\程序分块\\_背景图工具.py`；或从 `备份\\AIxiede.py.bak-搬小件前` 里拷回来" % (_ERR_背景图工具,))
    def blend_color_over(*_a, **_kw):
        raise RuntimeError(
            "模块 _背景图工具.py 没找到或有问题（blend_color_over 用不了）。\n"
            "  原因：%r\n"
            "  怎么修：见 `AIxiede拆分开\\程序分块\\_背景图工具.py`；或从 `备份\\AIxiede.py.bak-搬小件前` 里拷回来" % (_ERR_背景图工具,))
    def average_color_of_image(*_a, **_kw):
        raise RuntimeError(
            "模块 _背景图工具.py 没找到或有问题（average_color_of_image 用不了）。\n"
            "  原因：%r\n"
            "  怎么修：见 `AIxiede拆分开\\程序分块\\_背景图工具.py`；或从 `备份\\AIxiede.py.bak-搬小件前` 里拷回来" % (_ERR_背景图工具,))
    def make_background_layer(*_a, **_kw):
        raise RuntimeError(
            "模块 _背景图工具.py 没找到或有问题（make_background_layer 用不了）。\n"
            "  原因：%r\n"
            "  怎么修：见 `AIxiede拆分开\\程序分块\\_背景图工具.py`；或从 `备份\\AIxiede.py.bak-搬小件前` 里拷回来" % (_ERR_背景图工具,))

def _load_custom_themes():
    """★ 启动时**从设置文件里读自定义皮肤**（用户以后自己做的）。

    ★ 现在还没有"导入皮肤"的界面 —— 但**读的这条路先打通**：
      设置文件里如果有 `custom_themes`（一个 {名字: 颜色表} 的字典），
      启动时就会自动注册进来，菜单里也能看到。
    ★ 这样以后加"导入皮肤"功能时，**只要往设置里写、然后重启**就行，
      不用再动启动流程（"预留入口"的意思就是这个）。
    ★ 读不动就安静跳过（绝不让它拦住程序启动）。
    """
    try:
        data = load_ui_setting("custom_themes", None)
        if not isinstance(data, dict):
            return 0
        n = 0
        for name, pal in data.items():
            if isinstance(pal, dict):
                if register_theme(name, pal,
                                  label=pal.get("label") or name):
                    n += 1
        if n:
            try:
                note_swallowed(T("已从设置里读了 {x} 套自定义皮肤", x=n), None,
                               level="info")
            except Exception:
                pass
        return n
    except Exception:
        return 0


# ==========================================================================
#  ★★★ 2026-10-08 **插件入口**（用户要："要配合未来会搞的插件入口弄"）★★★
#  ------------------------------------------------------------------------
#  ★★ 用户原话：
#    「要预留好自定义皮肤入口啊，**要配合未来会搞的插件入口弄**」
#
#  ★★ 设计原则（跟"自定义皮肤"**完全同一套**）：
#    **插件"注册"进一张表 → 主程序"问表要东西"** ——
#    主程序**不硬编码任何插件名**，所以以后加插件**不用改主程序**。
#    ★ 皮肤那张表是 `_THEMES`，插件这张表是 `_PLUGINS`。
#
#  ★★ 插件能干什么（**接口清单** —— 这是"预留入口"的核心）：
#    | 想干的事             | 用哪个接口                       |
#    |---------------------|----------------------------------|
#    | 加菜单项             | `api.add_menu(名字, 回调)` / `api.add_menu_item(...)` |
#    | 加设置项             | `api.add_settings_item(名字, 回调)` |
#    | 加自己的配色         | `api.register_theme(...)`（复用皮肤那套）|
#    | 记一笔错             | `api.note_error(...)`（复用账本）|
#    | 拿主程序对象         | `api.app`                        |
#    ★ "处理文件的钩子"（打标签前/后）**更复杂**（涉及线程和顺序），
#      **先不做** —— 等真有插件要用时再加（这叫"留位置，不提前造"）。
#
#  ★★ 插件放哪儿、长什么样：
#    · 目录：`<程序目录>/插件/`
#    · 一个插件 = 一个 `.py` 文件，里面**只要有 `register(api)` 函数**：
#        # 我的插件.py
#        def register(api):
#            api.add_menu("我的插件", [
#                ("干点什么", lambda: print("干了")),
#            ])
#    ★ **加载失败绝不能拦住程序启动** —— 每个插件单独 try + 记账本
#      （用户报过"程序打不开"，绝不能因为一个插件写坏了就打不开）。
# ==========================================================================

# ★ 所有注册过的插件：{插件名: {"menu": [...], "settings": [...], "file": ...}}
_PLUGINS = {}

# ★ 插件文件的目录（跟 `图标资产/`、`备份/` 一个层级）
try:
    PLUGIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "插件")
except Exception:
    PLUGIN_DIR = "插件"


class PluginAPI:
    """★★ **给插件用的接口对象** —— 插件只能通过它碰主程序。

    ★ 为什么给个"中间人"而不是直接把 `app` 丢过去：
      ① **可控** —— 插件能干什么，看这个类有哪些方法就知道了
         （比让它随便摸 `app` 的几百个方法安全得多）
      ② **稳定** —— 以后主程序内部改了，只要这个类的方法签名不变，
         **老插件照样能用**（用户要的就是"方便以后改"）
      ③ **好记账** —— 插件干的事出错了，能记到它头上（知道是哪个插件）
    ★ 但它**也留了后门**：`api.app` 直接给主程序对象 ——
      想干"接口没覆盖"的事也能干（信任插件作者）。
    """

    def __init__(self, app, name):
        self.app = app
        self.name = name          # 插件名（记账时用）

    # ---- 多语言 ----
    def T(self, text, **kw):
        """★★★ **给插件用的翻译函数**（插件里的界面文字也走这里）。

        ★★ 用户原话：「要做就做全套」——
          插件加进菜单的字、弹窗的字，**切英文时也得跟着变**。

        ★ 为什么让插件用**主程序的** T（而不是让它自己 import i18n）：
          · 插件的翻译**应该跟主程序同一套语言文件** ——
            用户切语言时**一次生效**，不用每个插件各切一次
          · 插件**不需要知道**语言文件在哪（那是主程序的事）
        ★★ 判据：**"给插件的是能力，不是实现"** ——
          插件只管"我要显示这句话"，**怎么翻、翻成什么，主程序管**。
        ★ 用法（跟主程序一样）：`api.T("取消")` / `api.T("共 {n} 项", n=5)`
        """
        try:
            return T(text, **kw)
        except Exception:
            try:
                return str(text).format(**kw) if kw else str(text)
            except Exception:
                return str(text)

    # ---- 菜单 ----
    def add_menu(self, label, items):
        """★ 加一个**顶层菜单**（会出现在悬浮球/菜单栏里）。

        `items` 是 `[(文字, 回调), ...]`；写 `None` 表示一条分隔线。
        ★ 这是插件最常见的用法（"我想在菜单里加一栏"）。
        """
        try:
            _PLUGINS.setdefault(self.name, {}).setdefault("menu", []).append(
                (str(label), list(items or [])))
            return True
        except Exception as exc:
            self.note_error(T("注册菜单失败"), exc)
            return False

    def add_menu_item(self, menu_label, item_label, command):
        """★ 往**已有的**菜单里加一项（比如往「设置」里加）。

        ★ 跟 `add_menu` 的区别：这个是"**插进**别人的菜单"。
        """
        try:
            _PLUGINS.setdefault(self.name, {}).setdefault(
                "menu_item", []).append(
                (str(menu_label), str(item_label), command))
            return True
        except Exception as exc:
            self.note_error(T("注册菜单项失败"), exc)
            return False

    # ---- 设置 ----
    def add_settings_item(self, label, command):
        """★ 往「设置」菜单加一项（省得自己建一个顶层菜单）。"""
        return self.add_menu_item("设置", label, command)

    # ---- 皮肤 ----
    def register_theme(self, name, palette, label=None):
        """★ 插件可以提供自己的配色（复用主程序那套皮肤机制）。"""
        try:
            return register_theme(name, palette, label=label)
        except Exception as exc:
            self.note_error(T("注册皮肤失败"), exc)
            return False

    def theme_get(self, key, default=None):
        """★ 读当前皮肤的一个颜色（插件画自己的界面时用）。"""
        return theme_get(key, default)

    # ---- 记账 ----
    def note_error(self, what, exc=None, level="warn"):
        """★ 记一笔到主程序的"账本"（用户能找到底是哪个插件出的问题）。"""
        try:
            note_swallowed(T("插件「{x}」：{y}", x=self.name, y=what), exc, level=level)
        except Exception:
            pass

    def log(self, text):
        """★ 往主程序的「输出」面板写一行（插件也能有日志）。"""
        try:
            self.app.log_output(T("[插件 {x}] {y}", x=self.name, y=text))
        except Exception:
            pass

    # ---- 只读信息（插件常要用的）----
    def current_dir(self):
        """★ 当前在看哪个文件夹。"""
        try:
            return self.app.current_dir
        except Exception:
            return ""

    def selected_paths(self):
        """★ 现在选中了哪些文件（列表）。"""
        try:
            fl = getattr(self.app, "file_list", None)
            if fl is None:
                return []
            out = []
            for p in getattr(fl, "selected_paths", []) or []:
                out.append(p)
            return out
        except Exception:
            return []


def register_plugin(name, module=None):
    """★ 把"加载好的插件"登记进 `_PLUGINS`（加载器用，插件作者不用管）。

    ★ 其实"注册"主要是**插件自己调 `api.add_*` 时**发生的 ——
      这个函数只负责"建个位置 + 记一笔加载成功"。
    """
    try:
        _PLUGINS.setdefault(str(name), {})
        try:
            note_swallowed(T("已加载插件「{x}」", x=name), None, level="info")
        except Exception:
            pass
        return True
    except Exception:
        return False


def plugins_now():
    """★ 现在有哪些插件、各自要加什么（**主程序"问表要东西"就靠它**）。

    返回 `{插件名: {...}}`（只读用途）。
    ★ 这就是"预留入口"的兑现场：
      主程序建菜单时会问它 → 插件想加什么，**主程序根本不用知道**
      （跟 `apply_theme_names()` 完全一个道理）。
    """
    try:
        return dict(_PLUGINS)
    except Exception:
        return {}


def plugin_menu_entries():
    """★ 插件要加的**顶层菜单**：`[(插件名, 菜单名, [(文字, 回调), ...]), ...]`。"""
    out = []
    try:
        for pname, spec in _PLUGINS.items():
            for label, items in (spec.get("menu") or []):
                out.append((pname, label, items))
    except Exception:
        pass
    return out


def plugin_menu_items():
    """★ 插件要**插进已有菜单**的项：`[(插件名, 菜单名, 文字, 回调), ...]`。"""
    out = []
    try:
        for pname, spec in _PLUGINS.items():
            for mlabel, ilabel, cmd in (spec.get("menu_item") or []):
                out.append((pname, mlabel, ilabel, cmd))
    except Exception:
        pass
    return out


def load_plugins(app):
    """★★ **启动时扫描插件目录、逐个加载**（每个单独 try，坏一个不影响别人）。

    ★★ 安全第一（**这条最重要**）：
      · **插件目录不存在** → 安静跳过（大多数用户没有插件）
      · **某个插件语法错 / 运行错** → 只记一笔账，**程序照常启动**
        ★ 理由：用户报过"程序打不开" —— **绝不能因为一个插件写坏了就打不开**
      · 同名的只加载一次
    ★ 返回：成功加载的个数（给日志用）。
    """
    n = 0
    try:
        if not os.path.isdir(PLUGIN_DIR):
            return 0
        names = []
        try:
            names = sorted(os.listdir(PLUGIN_DIR))
        except Exception:
            return 0
        for fn in names:
            # ★ 只认 `.py`，且**跳过 `_` 开头的**（那是"半成品/停用"的约定）
            if not fn.lower().endswith(".py") or fn.startswith("_"):
                continue
            pname = fn[:-3]
            try:
                import importlib.util as _ilu
                path = os.path.join(PLUGIN_DIR, fn)
                spec = _ilu.spec_from_file_location("aixiede_plugin_" + pname,
                                                    path)
                if spec is None or spec.loader is None:
                    continue
                mod = _ilu.module_from_spec(spec)
                spec.loader.exec_module(mod)
                # ★ 插件必须有个 `register(api)` 函数 —— 没有就跳过（不算错）
                fn_reg = getattr(mod, "register", None)
                if not callable(fn_reg):
                    try:
                        note_swallowed(
                            "插件「%s」里没有 register(api) 函数，已跳过"
                            % pname, None, level="warn")
                    except Exception:
                        pass
                    continue
                api = PluginAPI(app, pname)
                fn_reg(api)
                register_plugin(pname, mod)
                n += 1
            except Exception as exc:
                # ★★ 关键：**单个插件坏掉，只记账，绝不影响程序**
                try:
                    note_swallowed("加载插件「%s」失败（已跳过，不影响程序）"
                                   % pname, exc, level="warn")
                except Exception:
                    pass
        if n:
            try:
                app.log_output(T("已加载 {x} 个插件", x=n))
            except Exception:
                pass
    except Exception as exc:
        try:
            note_swallowed(T("扫描插件目录失败"), exc)
        except Exception:
            pass
    return n


def _themes_now():
    """取当前整套颜色（画自定义区块时用，比 theme_get 一次一个更快）。"""
    try:
        return _THEMES.get(THEME_NAME, _THEME_LIGHT)
    except Exception:
        return _THEME_LIGHT


def theme_get(key, default=None):
    """取当前皮肤里的一个颜色。"""
    try:
        return _THEMES.get(THEME_NAME, _THEME_LIGHT).get(key, default)
    except Exception:
        return default


def _lum(hexcolor):
    """一个颜色的「亮不亮」（0=黑，255=白）。认不出来的返回 255（当它是浅色）。"""
    try:
        s = str(hexcolor).strip().lstrip("#")
        if len(s) == 3:
            s = "".join(c * 2 for c in s)
        if len(s) != 6:
            return 255.0
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16)
        # 人眼对绿色最敏感、蓝色最不敏感（外面通用的算法）
        return 0.299 * r + 0.587 * g + 0.114 * b
    except Exception:
        return 255.0


def _hsl_shift(hexcolor, dl=0.0, ds=0.0):
    """把颜色按「明暗 / 浓淡」挪一挪，**色相保持不变**（这样蓝的还是蓝的）。"""
    try:
        s = str(hexcolor).strip().lstrip("#")
        if len(s) == 3:
            s = "".join(c * 2 for c in s)
        if len(s) != 6:
            return hexcolor
        r = int(s[0:2], 16) / 255.0
        g = int(s[2:4], 16) / 255.0
        b = int(s[4:6], 16) / 255.0
        h, l, sat = colorsys.rgb_to_hls(r, g, b)
        l = max(0.0, min(1.0, l + dl))
        sat = max(0.0, min(1.0, sat + ds))
        r, g, b = colorsys.hls_to_rgb(h, l, sat)
        return "#%02x%02x%02x" % (int(r * 255 + .5), int(g * 255 + .5),
                                  int(b * 255 + .5))
    except Exception:
        return hexcolor


def _dark_of(color):
    """★ 核心：把一个浅色皮肤的颜色，翻成夜间模式该有的颜色。

    为什么不能「一律反色」：
      反色会把「深灰字」变成「浅灰字」（对），但把「浅蓝底」变成
      「深黄底」（错得离谱），标签颜色、状态红绿全毁。
      而且纯黑配纯白对比太硬，晚上看久了更累。

    所以按「这个颜色是底、是字、还是点缀」分四种情况（都是实测调出来的）：
      ① 很亮的底（亮度 ≥ 210）→ 整条亮度翻过来，色相不动。
         白(#ffffff) → 深灰底；浅蓝底 → 深蓝底。
      ② 中等亮的底（150~210）→ 压暗但**比①更狠一点**，压到深色区。
      ③ 亮字（100~150）→ 当它是「次要文字」→ 提亮成浅灰。
      ④ 暗字（< 100）→ 当它是「正文」→ 提到接近 #d6d7db。
    另外：**已经够暗的颜色（< 60）原样留着** —— 那本来就是深色装饰，
      在夜里正好合适，再压就成黑块了。
    """
    try:
        s = str(color).strip().lstrip("#")
        if len(s) == 3:
            s = "".join(c * 2 for c in s)
        if len(s) != 6:
            return color
        R = int(s[0:2], 16)
        G = int(s[2:4], 16)
        B = int(s[4:6], 16)
        L = 0.299 * R + 0.587 * G + 0.114 * B
        # ★★ 2026-10-07 修「夜间文字跟底色一样深、看不见」（用户报
        #   「问题、进度、输出区域详细文字底色还是白白的」）：
        #   原来这里一句 `if L < 60: return color` —— 意思是
        #   "已经够暗的装饰色就留着"。**但这条规则把"正文色"也误伤了**：
        #   白天模式的正文色 `#2c2f33` 亮度只有 **47** → 命中这条 →
        #   **原样保留** → 到了夜间，深灰字画在深灰底上 → **几乎看不见**。
        #   ★ 而实测 `_text_output` 的底色被换成 `#3a3a3a`（亮度 58），
        #     字还是 `#2c2f33`（亮度 47）—— 两个亮度只差 11，当然看不见。
        #   ★ 修法：把「很暗的颜色」**再分两类** ——
        #     · 带明显颜色的（深蓝、深红…）→ 真是装饰，**留着**
        #     · 几乎没色的深灰（灰阶）→ 那是**字**，**必须提亮**
        #   判据用"灰度"（max-min）而不是亮度 —— 装饰色通常带色相，
        #   正文的深灰是纯灰。
        if L < 60:
            _mx60, _mn60 = max(R, G, B), min(R, G, B)
            _is_gray60 = (_mx60 - _mn60) <= 20
            if not _is_gray60:
                return color          # 带色的深色装饰 → 留着
            # 深灰 → 当成"正文色"提到接近 #d6d7db（跟 ④ 一致）
            return "#d6d7db"
        # 是不是「几乎没颜色的灰」（灰阶）？
        mx, mn = max(R, G, B), min(R, G, B)
        is_gray = (mx - mn) <= 14
        h, l, sat = colorsys.rgb_to_hls(R / 255.0, G / 255.0, B / 255.0)
        if L >= 210:
            # ① 亮底 → 深底（保留原来「谁比谁亮」的次序，这样卡片层次还在）
            nl = 0.30 - (L - 210.0) / 255.0 * 0.45
            nl = max(0.10, min(0.42, nl))
        elif L >= 150:
            # ② 中亮底 → 再压深一点
            nl = 0.26
        elif L >= 100:
            # ③ 亮字 → 次要文字色
            nl = 0.62
        else:
            # ④ 暗字 → 正文色
            nl = 0.84
        if is_gray:
            sat = 0.0                 # 灰的就保持灰，别让它泛蓝泛黄
        else:
            sat = max(0.0, min(1.0, sat * 0.85))   # 带色的稍收一点，别刺眼
        r, g, b = colorsys.hls_to_rgb(h, nl, sat)
        return "#%02x%02x%02x" % (int(r * 255 + .5), int(g * 255 + .5),
                                  int(b * 255 + .5))
    except Exception:
        return color


def theme_color_for_change(old_color, prev_name=None):
    """皮肤切换时，一个颜色该换成什么。

    ★★ 2026-10-06 修一个真 bug：**切回白天时恢复不干净** ★★
       原来的写法是「夜间才翻色，白天原样返回」。
       结果：切到夜间时颜色被翻成深色，**再切回白天时，"原样返回"
       保住的却是那些深色** —— 界面就花掉了（实测：切回白天后
       还有 30 个控件是深的）。
       ★ 正确做法：**按「切换前是哪个皮肤」决定**——
         · 从白天切到夜间 → 把颜色翻深（_dark_of）
         · 从夜间切回白天 → 把颜色**翻回来**（用同一套规则反着算）
       反着算的做法：用一个和 `_dark_of` 互逆的映射 ——
       深底 → 亮底、浅字 → 深字。
    """
    try:
        if not old_color:
            return old_color
        s = str(old_color)
        to_dark = (THEME_NAME == "dark")
        # 已经是目标色系里「正常该有的」颜色就原样留着，
        # 免得反复切换时颜色越漂越偏（每次切都翻一遍会越翻越离谱）。
        L = _lum(s)
        if to_dark and L < 110:
            return s          # 已经是深的 → 不用再翻
        if (not to_dark) and L > 170:
            return s          # 已经是浅的 → 不用再翻
        if to_dark:
            return _dark_of(s)
        return _light_of(s)
    except Exception:
        return old_color


def _light_of(color):
    """★ `_dark_of` 的反向：把夜间用色翻回白天用色。

    深底 → 亮底（白/浅灰），浅字 → 深字。
    规则和 `_dark_of` 对称，这样「白天→夜间→白天」来回切
    能回到原样，不会越切越花。
    """
    try:
        s = str(color).strip().lstrip("#")
        if len(s) == 3:
            s = "".join(c * 2 for c in s)
        if len(s) != 6:
            return color
        R = int(s[0:2], 16)
        G = int(s[2:4], 16)
        B = int(s[4:6], 16)
        L = 0.299 * R + 0.587 * G + 0.114 * B
        mx, mn = max(R, G, B), min(R, G, B)
        is_gray = (mx - mn) <= 14
        h, l, sat = colorsys.rgb_to_hls(R / 255.0, G / 255.0, B / 255.0)
        if L < 60:
            # 很深的底 → 很亮的底（但不到纯白，留一点层次）
            nl = 0.985 - (60.0 - L) / 60.0 * 0.06
        elif L < 110:
            # 中等深（卡片底 / 深灰边框）→ 浅灰
            nl = 0.94
        elif L < 170:
            # 浅一点的字（次要文字）→ 中灰
            nl = 0.60
        else:
            # 亮字 → 深字
            nl = 0.20
        if is_gray:
            sat = 0.0
        else:
            sat = max(0.0, min(1.0, sat * 0.9))
        r, g, b = colorsys.hls_to_rgb(h, nl, sat)
        return "#%02x%02x%02x" % (int(r * 255 + .5), int(g * 255 + .5),
                                  int(b * 255 + .5))
    except Exception:
        return color


def _retheme_entry_like(w):
    """★★ 2026-10-06：专门收拾**输入框 / 下拉框**。

    为什么要单独来一手：ttk 的输入框颜色不全在「样式」里 ——
    已经建好的那个控件，有些子部件（里子、箭头）的颜色是**建的时候定死**的，
    只改 style 不会回头刷新它们。实测症状就是：
      **别的都变深色了，就「位置」「搜索文件」这几个框还是白的。**
    所以这里对每个已经存在的输入框，再单独 configure 一遍。
    """
    try:
        cls = w.winfo_class()
    except Exception:
        return
    if cls not in ("TEntry", "TCombobox", "TSpinbox"):
        return
    txt = theme_get("text_bg")
    panel = theme_get("panel_bg")
    fg = theme_get("fg")
    line = theme_get("line")
    # ① 控件本体
    for opt, val in (("fieldbackground", txt), ("background", panel),
                     ("foreground", fg), ("insertbackground", fg),
                     ("selectbackground", theme_get("select_bg")),
                     ("selectforeground", fg),
                     ("bordercolor", line), ("lightcolor", panel),
                     ("darkcolor", panel), ("arrowcolor", fg)):
        try:
            w.configure(**{opt: val})
        except Exception:
            continue
    # ② 子部件（里子 / 箭头）—— ttk 的老毛病，得点名去改
    try:
        st = ttk.Style()
        for base in ("TEntry", "TCombobox", "TSpinbox"):
            for sub in (base + ".field", base + ".padding",
                        base + ".downarrow", base + ".uparrow",
                        base + ".background"):
                try:
                    st.configure(sub, background=txt, fieldbackground=txt,
                                 foreground=fg, bordercolor=line,
                                 arrowcolor=fg, lightcolor=txt, darkcolor=txt)
                except Exception:
                    continue
    except Exception:
        pass


def _walk_all_widgets(root):
    """把一棵控件树里**所有**控件（含子控件、含 ttk 内部的）列出来。

    ★ ttk 的控件（按钮、滚动条…）内部还包着 tk 控件，光看 winfo_children()
      会漏掉它们 —— 那些漏掉的恰恰是「白晃晃」的主角，所以必须递归进去。
    """
    out = []
    stack = [root]
    guard = 0
    while stack:
        w = stack.pop()
        guard += 1
        if guard > 40000:          # 保险：绝不让它转到天荒地老
            break
        out.append(w)
        try:
            kids = list(w.winfo_children())
        except Exception:
            kids = []
        stack.extend(kids)
    return out


# 切换皮肤时要换的那些「和颜色有关」的属性名
_COLOR_OPTS = ("background", "foreground", "activebackground",
               "activeforeground", "selectbackground", "selectforeground",
               "highlightbackground", "highlightcolor", "disabledforeground",
               "troughcolor", "insertbackground", "inactiveselectbackground",
               "selectcolor", "readonlybackground", "fieldbackground",
               "lightcolor", "darkcolor", "bordercolor")


def _retheme_tree(root):
    """（切皮肤用）把一棵控件树里所有控件的颜色，按对照表换一遍。

    ★★ 2026-10-06：**带「原始单据」** ★★
       光靠规则反推颜色，来回切几次就会越切越偏（每次都翻一遍，
       误差会累积；实测「切回白天」后还有 30 个控件是深的）。
       所以这里给每个控件留一张「小票」：**第一次改之前，先把原样记下来**，
       以后再切就照着小票还原 —— 白天回到白天、夜间回到夜间，
       切多少次都和第一次一模一样。

    返回「换过几个控件」。
    """
    changed = 0
    # 「原始单据」挂在 root 上，键是控件，值是 {属性: 原色}
    try:
        book = getattr(root, "_theme_orig_colors", None)
        if book is None:
            book = {}
            root._theme_orig_colors = book
    except Exception:
        book = {}

    for w in _walk_all_widgets(root):
        # ★★ 2026-10-07：**登记过"配色角色"的控件，直接跳过** ——
        #   它们由 `apply_themed()` 按主题色刷，**不该走这套"翻色表"**
        #   （翻色表分不清"这值是底还是字"，会把底色翻成字色）。
        try:
            if w in _THEMED_MANAGED:
                continue
        except Exception:
            pass
        # ★ 第一件事：把「还没被改过」的原色记下来
        try:
            rec = book.setdefault(w, {})
            for opt in _COLOR_OPTS:
                if opt in rec:
                    continue
                try:
                    v = w.cget(opt)
                except Exception:
                    continue
                if v not in (None, ""):
                    rec[opt] = str(v)
        except Exception:
            pass

        # ---- tk 原生控件：直接 configure ----
        try:
            for opt in _COLOR_OPTS:
                try:
                    old = w.cget(opt)
                except Exception:
                    continue
                if not old:
                    continue
                # ★ 优先照「原始单据」还原（切回白天时尤其重要）
                rec = book.get(w) or {}
                base = rec.get(opt, None)
                if THEME_NAME == "dark":
                    new = _dark_of(base or str(old))
                else:
                    # 白天：能还原就还原，还原不了才按规则反推
                    new = base if base else _light_of(str(old))
                if new and str(new) != str(old):
                    try:
                        w.configure(**{opt: new})
                        changed += 1
                    except Exception:
                        pass
        except Exception:
            pass
        # ttk 控件：它的颜色在「样式」里，不在控件自己身上
        try:
            stl = w.cget("style")
        except Exception:
            stl = ""
        try:
            cls = w.winfo_class()
        except Exception:
            cls = ""
        if cls in ("TFrame", "TLabel", "TButton", "TEntry", "TCombobox",
                   "TNotebook", "TScrollbar", "Treeview", "TCheckbutton",
                   "TRadiobutton", "TScale", "TLabelframe", "TSpinbox",
                   "TProgressbar", "TPanedwindow"):
            try:
                _retheme_ttk_class(w, cls, stl)
                changed += 1
            except Exception:
                pass
            # ★ 输入框 / 下拉框再单独收拾一遍（见那个函数里的说明：
            #   它们有些颜色只改样式刷不到，必须点名 configure）
            try:
                _retheme_entry_like(w)
            except Exception:
                pass
    return changed


def _retheme_ttk_class(w, cls, stl):
    """（切皮肤用）把某个 ttk 控件背后的样式颜色也换一遍。"""
    try:
        st = ttk.Style()
        for sname in (str(stl or ""), cls, cls.replace("T", "", 1)):
            if not sname:
                continue
            try:
                cur = st.configure(sname) or {}
            except Exception:
                continue
            patch = {}
            for opt in _COLOR_OPTS:
                if opt in cur and cur[opt]:
                    new = theme_color_for_change(str(cur[opt]))
                    if new and new != str(cur[opt]):
                        patch[opt] = new
            if patch:
                try:
                    st.configure(sname, **patch)
                except Exception:
                    pass
    except Exception:
        pass


def _apply_theme_constants():
    """★★ 把全局那几个「颜色常量」换成当前皮肤的值。

    这一步是为了**以后新造的控件**也是对的颜色 —— 因为程序里很多控件
    是在用的时候才新建的（比如打开图片才建那块画布、点开某些面板才建
    里面的小标签），它们读的是源码里写死的颜色。
    不改常量的话，晚上点开一张图片，那块地方「唰」一下白一片 ——
    正是用户嫌刺眼的那种。

    ★ 分两路：
      ① `CAT_COLORS`：标签配色，要按色系整体调（不能简单压暗，
         不然一堆标签会变成同一个颜色）；
      ② 其余那些「没名字」的浅色（分隔线、隔行底色、次要文字），
         源码里已经统一改成 `theme_get(...)` 了（见下面那段说明），
         所以**新造的控件自动就是对的**，这里不用管。
    """
    try:
        globals()["CAT_COLORS"] = (
            ["#4a7fd4", "#b8447a", "#2e9e7e", "#c07f1a",
             "#7a4a94", "#b8623f", "#3a76c8", "#2aa8a4"]
            if THEME_NAME == "dark" else
            ["#5b8def", "#e84393", "#00b894", "#f39c12",
             "#8e44ad", "#e17055", "#0984e3", "#00cec9"])
    except Exception:
        pass


def _set_native_dark(root, dark):
    """★★ 2026-10-06 新增：**把窗口标题栏和菜单栏也变成深色**（夜间模式的最后一关）。

    用户原话：「都夜间模式了，窗口标题那里还白白的，菜单栏也是白白的……
    这个软件做出去了也得荡人笑话」。

    ★ 为什么以前以为「改不了」：
      标题栏是 **Windows 自己画的**，Tk 碰不到它的颜色 ——
      所以直觉的解法是「把标题栏去掉、自己画一个」，
      但那会连累拖动 / 最大化 / 双击标题栏这些系统行为，代价太大。
    ★ 其实 Windows **自己就支持**，只是要主动开口告诉它。两个调用：

      ① `DwmSetWindowAttribute(hwnd, 20, 1)`
         → 这个窗口的**标题栏**用深色。
         ★ 编号必须是 **20**（Win10 20H1+ 的新编号）；
           旧的 19 在实测里**返回失败**（-2147024809），别用。
      ② `uxtheme.SetPreferredAppMode(2)` + `FlushMenuThemes()`
         → **整个进程的原生控件**（菜单栏、滚动条、下拉框…）用深色。
         2 = ForceDark。

    ★ 实测（Windows 10 build 19045）：
      标题栏像素 (24,24,24)、菜单栏像素 (23,23,23)，两个调用都返回 0。

    ★ 三条要注意的：
      · **只对 Win10 1809+ / Win11 有效**。老系统上这两个调用会失败，
        这里**全部包在 try 里**，失败就静静退回原来的样子 ——
        **绝不会因为「想变好看」把程序弄崩**。
      · `SetPreferredAppMode` 是**进程级**的，一次生效、不用每次窗口都调。
      · 拿窗口句柄要用 **GetParent(winfo_id())** ——
        Tk 的 `winfo_id()` 给的是**内部子窗口**，不是带标题栏的那个外壳
        （实测：winfo_id=526178，真正的顶层窗口=2294126）。
    """
    if os.name != "nt":
        return
    try:
        import ctypes
    except Exception:
        return

    # ---------- ① 进程级：让原生控件（菜单栏等）用深色 ----------
    try:
        ux = ctypes.windll.uxtheme
        # 135 = SetPreferredAppMode, 136 = FlushMenuThemes（按序号取，
        # 因为这两个函数没有导出的名字）
        fn = ux[135]
        fn.restype = ctypes.c_int
        fn.argtypes = [ctypes.c_int]
        fn(2 if dark else 0)          # 2=ForceDark, 0=Default
        ux[136]()                     # 刷一下菜单主题，否则要重启才见效
    except Exception:
        pass                          # 老系统没有这两个，忽略

    # ---------- ② 这个窗口：标题栏用深色 ----------
    # ★★ 这里踩了第二个坑（第一个是"要等窗口显示"），写清楚：
    #   `GetParent(winfo_id())` 在**窗口还没显示**的时候返回 **0**。
    #   我原来的写法是「拿不到就退回 winfo_id()」—— 而 winfo_id() 是
    #   **内部子窗口**的句柄，在它上面设深色**永远失败**
    #   （实测返回 -2147024890）。
    #   于是：**调用"成功"了、也没报错，但标题栏一直是白的** ——
    #   这就是那种最难查的「静默失败」。
    #
    #   ★ 正解：拿不到顶层句柄就**重试**（窗口映射好之后就有了），
    #     而不是退而求其次用一个错的句柄。
    #     实测：窗口刚建好时 GetParent=0，`update()` 之后就正常了。
    try:
        _apply_caption_dark(root, bool(dark), tries=0)
    except Exception:
        pass


def _apply_caption_dark(root, dark, tries=0):
    """给标题栏设深/浅色；窗口还没映射好就过一会儿重试。

    ★ 重试上限 40 次 × 50 毫秒 = 最多等 2 秒。
      2 秒还拿不到句柄，说明这台机器/这个窗口就是不行（老系统），
      那就**安静放弃** —— 「想变好看」绝不能变成「卡住启动」。
    """
    try:
        import ctypes
    except Exception:
        return
    try:
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    except Exception:
        hwnd = 0
    if not hwnd:
        # ★ 还没映射好 —— 重试，**绝不退回 winfo_id()**
        if tries < 40:
            try:
                root.after(50, lambda: _apply_caption_dark(root, dark,
                                                           tries + 1))
            except Exception:
                pass
        return
    try:
        val = ctypes.c_int(1 if dark else 0)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.c_void_p(hwnd), ctypes.c_uint(20),
            ctypes.byref(val), ctypes.sizeof(val))
    except Exception:
        pass


def apply_theme(root, name=None):
    """★★ 换皮肤（主入口）。

    name 可以是**任意已注册的皮肤名**（`light` / `dark` / 以后加的自定义皮肤）；
    不给就用当前存的设置。返回 True 表示换成功了。

    ★★ 2026-10-08：`name not in _THEMES → 退回 light` 这个兜底**保留**
      （给一个不认识的名字，总得给个能用的），
      但**不再限制只能是 light/dark** —— 自定义皮肤照样能过。
    """
    global THEME_NAME
    try:
        if name is None:
            name = THEME_NAME
        if name not in _THEMES:
            name = "light"
        if name == THEME_NAME and getattr(root, "_theme_applied", False):
            pass                      # 同皮肤也照跑一遍（保证刚建的控件也对）
        THEME_NAME = name
    except Exception:
        return False

    ok = False
    # ① 全局控件样式（按钮、滚动条、输入框…）
    try:
        ok = _style_all_widgets(root, name) or ok
    except Exception as _e:
        try:
            note_swallowed(T("换皮肤：设置控件样式失败"), _e, quiet=True)
        except Exception:
            pass
    # ② 常量（影响「以后新建」的控件）
    try:
        _apply_theme_constants()
    except Exception:
        pass
    # ③ 已经建好的控件，逐个换色
    try:
        n = _retheme_tree(root)
        ok = ok or n > 0
    except Exception as _e:
        try:
            note_swallowed(T("换皮肤：给已有控件换色失败"), _e, quiet=True)
        except Exception:
            pass
    # ④ ★★ 再整体刷一遍样式表。
    #    为什么要「两次」：上面第③步把已有控件按「对照表」换了一遍，
    #    但那只是照着旧颜色一对一换；有些控件的颜色**根本不在控件身上**
    #    （在 ttk 样式里，而且是启动时定死的）。再来一遍样式表，
    #    才能保证「已经建好的」和「以后新建的」看起来一模一样。
    #    实测：不做这一步，「位置」「搜索文件」那几个框会一直是浅色。
    try:
        _style_all_widgets(root, name)
    except Exception:
        pass
    # ★★ 2026-10-06：最后把**标题栏和菜单栏**也染成深色（夜间模式的最后一关）。
    #   放在最后做，因为它跟上面那套「扫控件换色」完全是两条路
    #   （那个改的是 Tk 控件，这个改的是 Windows 自己画的东西）。
    try:
        _set_native_dark(root, name == "dark")
    except Exception:
        pass
    try:
        root._theme_applied = True
    except Exception:
        pass
    return ok


def _style_all_widgets(root, name):
    """★ 把「控件外观」整体设成当前皮肤 —— 这是夜间的**主力**。"""
    th = _THEMES.get(name, _THEME_LIGHT)
    st = ttk.Style()
    # ★ 必须用 clam：Tk 自带的看板（vista/winnative）是 Windows 主题绘制的，
    #   **不吃自定义颜色** —— 用它们做夜间，按钮和滚动条会顽固地保持白色。
    #   clam 是 Tk 自己的绘制引擎，颜色完全听我们的。
    try:
        st.theme_use("clam")
    except Exception:
        pass

    def C(*pairs):
        for sname, opts in pairs:
            try:
                st.configure(sname, **opts)
            except Exception:
                pass

    BG, CARD, PANEL = th["win_bg"], th["card_bg"], th["panel_bg"]
    FG, DIM, LINE = th["fg"], th["fg_dim"], th["line"]
    ACC, SELB = th["accent"], th["select_bg"]

    # ---- 底板类 ----
    C(("TFrame", {"background": BG}),
      ("Card.TFrame", {"background": CARD, "borderwidth": 1,
                       "relief": "solid", "bordercolor": LINE}),
      ("TLabel", {"background": BG, "foreground": FG}),
      # ★★ 2026-10-07 **修一个一直没生效的样式**（"熊猫色"的真凶）★★
      #   原来这里写的是 `TLabelFrame`（"Label" 的 L 大写）——
      #   而 **Tk 里这个类的真正名字是 `TLabelframe`**（只有 T 大写）！
      #   → `st.configure("TLabelFrame", ...)` **配了个不存在的样式**，
      #     Tk 不报错、也不生效，于是所有 `ttk.LabelFrame` 一直用
      #     clam 主题的默认底色。
      #   ★ 实测证据：`st.lookup("TLabelframe", "background")` = **#dcdad5**（土黄灰），
      #     而 `TLabelframe` 的 `configure()` 返回**空字典** `{}` ——
      #     说明**从没被配过**。
      #   ★ 用户报「索引管理灰黑灰黑的像熊猫一样」就是这个 ——
      #     那个窗口的「详情 / 进度 / 日志」三个框全是 LabelFrame。
      #   ★ 两个名字都留着（宁可多配一个无害的，也别再漏）。
      ("TLabelframe", {"background": BG, "foreground": FG,
                       "bordercolor": LINE}),
      ("TLabelframe.Label", {"background": BG, "foreground": FG}),
      # 老写法留着（虽然不生效，但万一别的 Tk 版本认它）
      ("TLabelFrame", {"background": BG, "foreground": FG,
                       "bordercolor": LINE}),
      ("TLabelFrame.Label", {"background": BG, "foreground": FG}),
      ("TSeparator", {"background": LINE}),
      ("TPanedwindow", {"background": BG}))
    # ---- 分栏条 ----
    C(("Sash", {"sashthickness": 6, "gripcount": 0,
                "background": th["sash"],
                "bordercolor": th["sash"],
                "lightcolor": th["sash"],
                "darkcolor": th["sash"]}))
    try:
        st.map("Sash", background=[("active", th["sash_active"])])
    except Exception:
        pass
    # ---- 按钮 ----
    # ★★ 2026-10-06：按钮**必须同时给 background 和 foreground 并 map 好**，
    #   否则 Tk 会「背景听你的、字色用系统默认」—— 夜间就变成
    #   「深底 + 深字」，字直接看不见（实测就是这个症状）。
    C(("TButton", {"background": PANEL, "foreground": FG,
                   "bordercolor": LINE, "lightcolor": PANEL,
                   "darkcolor": PANEL, "focuscolor": PANEL,
                   "relief": "raised", "padding": (7, 3)}),
      ("Toolbutton", {"background": PANEL, "foreground": FG,
                      "bordercolor": LINE}),
      # 底部那排「标签盒 / 网盘 / 预览」等小按钮用的是这个样式
      ("Small.TButton", {"background": PANEL, "foreground": FG,
                         "bordercolor": LINE, "lightcolor": PANEL,
                         "darkcolor": PANEL, "padding": (5, 2)}))
    try:
        _btnmap = {
            "background": [("pressed", SELB), ("active", th["panel_bg2"]),
                           ("disabled", th["win_bg"])],
            "foreground": [("pressed", FG), ("active", FG),
                           ("disabled", DIM)],
            "lightcolor": [("pressed", SELB), ("active", th["panel_bg2"])],
            "darkcolor": [("pressed", SELB), ("active", th["panel_bg2"])],
        }
        st.map("TButton", **_btnmap)
        st.map("Toolbutton", **_btnmap)
        st.map("Small.TButton", **_btnmap)
    except Exception:
        pass
    # ---- 输入框 / 下拉框 ----
    # ★★ 2026-10-06：**输入框必须三样都给足** ——
    #   `fieldbackground`（里子）、`background`（边框外圈）、
    #   `foreground`（字）。只给一部分的话，clam 会用默认的浅色去补，
    #   夜间就出现「深底边框 + 白里子」或者「白底黑字」。
    #   下拉框还要单独管它那个箭头（arrowcolor）和弹出列表。
    C(("TEntry", {"fieldbackground": th["text_bg"], "foreground": FG,
                  "background": PANEL, "bordercolor": LINE,
                  "insertcolor": FG, "selectbackground": SELB,
                  "selectforeground": FG,
                  "lightcolor": LINE, "darkcolor": LINE,
                  "padding": 3}),
      ("TCombobox", {"fieldbackground": th["text_bg"], "foreground": FG,
                     "background": PANEL, "bordercolor": LINE,
                     "arrowcolor": FG, "selectbackground": SELB,
                     "selectforeground": FG,
                     "lightcolor": PANEL, "darkcolor": PANEL,
                     "padding": 3}),
      ("TSpinbox", {"fieldbackground": th["text_bg"], "foreground": FG,
                    "background": PANEL, "bordercolor": LINE,
                    "arrowcolor": FG,
                    "lightcolor": PANEL, "darkcolor": PANEL}))
    try:
        # 下拉框的「输入区」和「箭头区」是两个子部件，各自还得单独设一遍；
        # 只设 TCombobox 的话，某些状态下箭头那块还是白的。
        for sub in ("TCombobox.field", "TCombobox.downarrow",
                    "TCombobox.uparrow", "TEntry.field"):
            try:
                st.configure(sub, background=th["text_bg"],
                             fieldbackground=th["text_bg"],
                             foreground=FG, bordercolor=LINE,
                             arrowcolor=FG,
                             lightcolor=th["text_bg"],
                             darkcolor=th["text_bg"])
            except Exception:
                continue
        st.map("TCombobox",
               fieldbackground=[("readonly", th["text_bg"]),
                                ("disabled", BG)],
               foreground=[("disabled", DIM)],
               background=[("readonly", PANEL), ("active", PANEL)],
               arrowcolor=[("disabled", DIM)])
        st.map("TEntry",
               fieldbackground=[("disabled", BG), ("readonly", PANEL)],
               foreground=[("disabled", DIM)])
        # 下拉列表那个弹出框是 tk 的 Listbox，得从「选项数据库」改
        root.option_add("*TCombobox*Listbox.background", th["text_bg"])
        root.option_add("*TCombobox*Listbox.foreground", FG)
        root.option_add("*TCombobox*Listbox.selectBackground", SELB)
        root.option_add("*TCombobox*Listbox.selectForeground", FG)
    except Exception:
        pass
    # ---- 勾选框 / 单选钮（那两个小方块在 clam 里是 selectcolor） ----
    C(("TCheckbutton", {"background": BG, "foreground": FG,
                        "indicatorcolor": th["text_bg"],
                        "bordercolor": LINE, "focuscolor": BG}),
      ("TRadiobutton", {"background": BG, "foreground": FG,
                        "indicatorcolor": th["text_bg"],
                        "bordercolor": LINE, "focuscolor": BG}))
    try:
        st.map("TCheckbutton",
               background=[("active", BG)],
               indicatorcolor=[("selected", ACC), ("pressed", ACC)])
        st.map("TRadiobutton",
               background=[("active", BG)],
               indicatorcolor=[("selected", ACC), ("pressed", ACC)])
    except Exception:
        pass
    # ---- 滚动条 ----
    C(("Vertical.TScrollbar",
       {"background": th["scroll_fg"], "troughcolor": th["scroll_bg"],
        "bordercolor": th["scroll_bg"], "arrowcolor": DIM,
        "lightcolor": th["scroll_fg"], "darkcolor": th["scroll_fg"],
        "relief": "flat"}),
      ("Horizontal.TScrollbar",
       {"background": th["scroll_fg"], "troughcolor": th["scroll_bg"],
        "bordercolor": th["scroll_bg"], "arrowcolor": DIM,
        "lightcolor": th["scroll_fg"], "darkcolor": th["scroll_fg"],
        "relief": "flat"}))
    try:
        st.map("Vertical.TScrollbar",
               background=[("active", ACC), ("pressed", ACC)])
        st.map("Horizontal.TScrollbar",
               background=[("active", ACC), ("pressed", ACC)])
    except Exception:
        pass
    # ---- 刻度 / 进度条 ----
    C(("TScale", {"background": BG, "troughcolor": th["scroll_bg"],
                  "bordercolor": LINE}),
      ("Horizontal.TProgressbar", {"background": ACC,
                                   "troughcolor": th["scroll_bg"],
                                   "bordercolor": LINE,
                                   "lightcolor": ACC, "darkcolor": ACC}),
      ("Vertical.TProgressbar", {"background": ACC,
                                 "troughcolor": th["scroll_bg"],
                                 "bordercolor": LINE,
                                 "lightcolor": ACC, "darkcolor": ACC}))
    # ---- 表格（文件树） ----
    C(("Treeview",
       {"background": CARD, "fieldbackground": CARD, "foreground": FG,
        "bordercolor": LINE, "lightcolor": CARD, "darkcolor": CARD}),
      ("Treeview.Heading",
       {"background": PANEL, "foreground": FG, "bordercolor": LINE,
        "lightcolor": PANEL, "darkcolor": PANEL, "relief": "flat"}),
      ("FileTree.Treeview",
       # ★★ 2026-10-07：行高**按字体算**，不再写死 22。
       #   22 装不下 13 号字 → 字的上下被切掉（用户报"字被纵向挤压只显示半截"）。
       #   ★ 这里和建树那处（搜 `_tree_rowh`）用的是同一个算法，两处必须一致，
       #     否则「换一次皮肤」会把行高改回去。
       {"background": CARD, "fieldbackground": CARD, "foreground": FG,
        "rowheight": _tree_row_height(), "font": (FONT, UI_FONT_SIZE_SMALL)}))
    try:
        st.map("Treeview",
               background=[("selected", SELB)],
               foreground=[("selected", FG)])
        # 文件树那套是自建样式名，选中色要单独 map
        st.map("FileTree.Treeview",
               background=[("selected", SELB)],
               foreground=[("selected", FG)])
    except Exception:
        pass
    # ---- 笔记本（选项卡） ----
    C(("TNotebook", {"background": BG, "bordercolor": LINE,
                     "lightcolor": BG, "darkcolor": BG}),
      ("TNotebook.Tab", {"background": PANEL, "foreground": DIM,
                         "bordercolor": LINE, "lightcolor": PANEL,
                         "darkcolor": PANEL, "padding": (10, 4)}))
    try:
        st.map("TNotebook.Tab",
               background=[("selected", CARD), ("active", th["panel_bg2"])],
               foreground=[("selected", FG), ("active", FG)])
    except Exception:
        pass
    # ---- 菜单 / 列表 / 文本：这三样是 tk 原生控件，
    #      颜色得从「选项数据库」走（新建的才会自动吃） ----
    try:
        root.option_add("*Menu.background", PANEL)
        root.option_add("*Menu.foreground", FG)
        root.option_add("*Menu.activeBackground", SELB)
        root.option_add("*Menu.activeForeground", FG)
        root.option_add("*Menu.disabledForeground", DIM)
        root.option_add("*Menu.selectColor", SELB)
        root.option_add("*Menu.borderColor", LINE)
        root.option_add("*Listbox.background", th["text_bg"])
        root.option_add("*Listbox.foreground", FG)
        root.option_add("*Listbox.selectBackground", SELB)
        root.option_add("*Listbox.selectForeground", FG)
        root.option_add("*Text.background", th["text_bg"])
        root.option_add("*Text.foreground", FG)
        root.option_add("*Text.insertBackground", FG)
        root.option_add("*Text.selectBackground", SELB)
        root.option_add("*Entry.background", th["text_bg"])
        root.option_add("*Entry.foreground", FG)
        root.option_add("*Canvas.background", BG)
        root.option_add("*Frame.background", BG)
        root.option_add("*Label.background", BG)
        root.option_add("*Label.foreground", FG)
    except Exception:
        pass
    # ---- 本窗口自己的底色 ----
    try:
        root.configure(bg=BG)
    except Exception:
        pass
    return True


EXT_ICONS = {
    ".pdf": "📕", ".doc": "📘", ".docx": "📘",
    ".xls": "📗", ".xlsx": "📗",
    ".ppt": "📙", ".pptx": "📙",
    ".txt": "📄", ".md": "📝", ".rtf": "📄",
    ".jpg": "🖼", ".jpeg": "🖼", ".png": "🖼", ".gif": "🖼",
    ".bmp": "🖼", ".webp": "🖼", ".svg": "🖼", ".ico": "🖼",
    ".mp4": "🎬", ".avi": "🎬", ".mkv": "🎬", ".mov": "🎬",
    ".wmv": "🎬", ".flv": "🎬", ".webm": "🎬", ".m4v": "🎬",
    ".mpg": "🎬", ".mpeg": "🎬", ".rmvb": "🎬", ".3gp": "🎬",
    ".mp3": "🎵", ".wav": "🎵", ".flac": "🎵", ".aac": "🎵",
    ".ogg": "🎵", ".m4a": "🎵", ".wma": "🎵",
    ".zip": "📦", ".rar": "📦", ".7z": "📦", ".tar": "📦", ".gz": "📦",
    ".py": "🐍", ".js": "📜", ".ts": "📜",
    ".html": "🌐", ".css": "🎨",
    ".java": "☕", ".c": "📜", ".cpp": "📜", ".h": "📜",
    ".go": "📜", ".rs": "📜", ".rb": "💎", ".php": "🐘", ".sh": "🖥",
    ".exe": "⚙", ".msi": "⚙", ".bat": "⚙", ".cmd": "⚙",
}

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp",
              ".webp", ".svg", ".ico", ".tif", ".tiff"}

# ★★ 2026-10-06 新增：**深色模式下用的「纯符号」图标**。
#
#   用户反馈：「文件列表的 emoji 图标黑黑的看不清」。
#
#   ★ 为什么"把 emoji 颜色调亮"没用：
#     emoji 是**彩色字体**（Windows 上的 Segoe UI Emoji），
#     它**不跟随前景色** —— 你设白字，它还是自己那套颜色；
#     而且有些 emoji 本身就偏暗，摆在深底上就是看不清。
#
#   ★ 所以深色模式下**换成纯符号**（★ ▲ ● 这类"文字符号"）：
#     它们**跟随前景色**，主题给什么色就是什么色，一定看得清。
#
#   ★ 为什么不干脆用图片图标（用户一开始想自己去找）：
#     · 得凑齐几十张、风格还得统一；
#     · 要打进程序里（体积变大）；
#     · **高分屏会糊**（Tk 不像浏览器能自动缩放图片）；
#     · 以后加个文件类型就得再找一张。
#     先用纯符号试试，不够好看再上图片也不迟。
DARK_ICONS = {
    ".pdf": "▤", ".doc": "▤", ".docx": "▤",
    ".xls": "▦", ".xlsx": "▦",
    ".ppt": "▣", ".pptx": "▣",
    ".txt": "≡", ".md": "≡", ".rtf": "≡",
    ".jpg": "▨", ".jpeg": "▨", ".png": "▨", ".gif": "▨",
    ".bmp": "▨", ".webp": "▨", ".svg": "▨", ".ico": "▨",
    ".mp4": "▶", ".avi": "▶", ".mkv": "▶", ".mov": "▶",
    ".wmv": "▶", ".flv": "▶", ".webm": "▶", ".m4v": "▶",
    ".mpg": "▶", ".mpeg": "▶", ".rmvb": "▶", ".3gp": "▶",
    ".mp3": "♪", ".wav": "♪", ".flac": "♪", ".aac": "♪",
    ".ogg": "♪", ".m4a": "♪", ".wma": "♪",
    ".zip": "▩", ".rar": "▩", ".7z": "▩", ".tar": "▩", ".gz": "▩",
    ".py": "⌘", ".js": "⌘", ".ts": "⌘",
    ".html": "◍", ".css": "◍",
    ".java": "⌘", ".c": "⌘", ".cpp": "⌘", ".h": "⌘",
    ".go": "⌘", ".rs": "⌘", ".rb": "⌘", ".php": "⌘", ".sh": "⌘",
    ".exe": "⚙", ".msi": "⚙", ".bat": "⚙", ".cmd": "⚙",
}
# 深色模式下：文件夹 / 未知类型的兜底符号
DARK_ICON_DIR = "▸"
DARK_ICON_FILE = "·"


def dark_mode_now():
    """现在是不是深色皮肤？（给「画图标」这类地方判断用）"""
    try:
        return THEME_NAME == "dark"
    except Exception:
        return False


def icon_for_file_dark(name, is_dir, base_icon):
    """★ 深色模式下的图标：能用纯符号就用，没有对应的就退回原来的 emoji。

    ★ 兜底很重要：以后 `EXT_ICONS` 加了新类型而 `DARK_ICONS` 忘了加，
      也只是那一个显示成原来的 emoji，**不会变成空白或问号**。
    """
    try:
        if is_dir:
            return DARK_ICON_DIR
        import os as _os
        ext = _os.path.splitext(str(name or ""))[1].lower()
        if ext in DARK_ICONS:
            return DARK_ICONS[ext]
        # 没登记的：如果原来那个本来就是"单色符号"（不是彩色 emoji），
        # 就照用 —— 它跟随前景色，深色下本来就看得清。
        if base_icon and ord(base_icon[0]) < 0x2600:
            return base_icon
        return DARK_ICON_FILE
    except Exception:
        return base_icon or DARK_ICON_FILE
VIDEO_EXTS = {".mp4", ".avi", ".mkv", ".mov", ".wmv",
              ".flv", ".webm", ".m4v", ".mpg", ".mpeg", ".rmvb", ".3gp"}


# ==========================================================================
#  ★★ 文件类型图标（内嵌数据）
#  ----------------------------------------------------------------------
#  为什么要内嵌（而不是放一堆 .png 在外面）：
#    用户的程序一直是**单文件**的（连备份都是一个 .py）。
#    图标放外面的话，程序拷到别处就会「图标全丢、变成问号」。
#    内嵌之后**拷到哪都带着**，不会有这个尴尬。
#    代价：程序体积 +约 700KB（本地程序，无所谓）。
#
#  数据格式：ICON_PNG[尺寸][名字] = base64 字符串（384x384 以内）
#  想换图标：改 `_图标定稿` 目录里的图，重跑 `_图标打包.py` 覆盖本文件。
# ==========================================================================

ICON_SIZES = [64, 96, 128, 192, 256, 384]

ICON_PNG = {}

# ★ 图标数据现在是**外面的文件**（`图标资产\\_icons_data.py`）。
#   2026-10-07 搬出去的 —— 那 680 KB 原来占整个程序的 32%，
#   比 FileTaggerApp 主类还大近一倍，是"程序臃肿"的最大一块。
#
# ★★ 为什么搬出去是**安全**的（跟"删兜底类"完全不同）：
#   下面那个 `except: ICON_PNG = {}` **就是保命机制** ——
#   文件不在 = 图标取不到 = **所有调用方自动退回 emoji**，
#   **程序照常开**（`get_file_icon()` 本来就有"取不到返回 None"的路子，
#   见错题本 #5：最坏情况要能看能点，不能一片空白）。
#
# ★ 想换图标：改 `_图标定稿\` → 跑 `_图标打包.py` → 跑 `图标资产\_图标外置.py`
try:
    from _icons_data import ICON_PNG, ICON_TOTAL_BYTES   # noqa: F401
    _ICON_DATA_OK = True
except Exception as _e:
    ICON_PNG = {}
    ICON_TOTAL_BYTES = 0
    _ICON_DATA_OK = False
    try:
        print("[提示] 图标数据文件（图标资产\\_icons_data.py）没找到，"
              "图标已退回 emoji 显示 —— 不影响用。")
    except Exception:
        pass



# ==========================================================================
# ★★ 2026-10-06 新增：**图片图标**（替换掉原来的 emoji）
# --------------------------------------------------------------------------
# 用户原话：「图标还是全部换成图片型的吧，这套符号普世性不高，
#   给别人看他们只能认识一点点」。
#
# 图标是从 `_图标定稿` 生成、再由 `_图标打包.py` 内嵌进本文件的
# （见 `_icons_embed.py` 里的 ICON_PNG）。设计原则：
#   · 资源管理器那种观感：文件夹=带标签页的方块；文件=一页纸带折角
#   · **一切以"缩到 48 像素还认得出"为第一优先** —— 符号占满、线条粗
#   · 深浅两套皮肤**共用同一套图标**（色彩挑的是中间调，两边都看得清）
#
# ★ 三条实现上的讲究（都是踩过坑才有的）：
#   ① **按档位取原图**，不要拿一张大图硬缩。
#      Tk 缩图会糊，而且每次缩都要算，很慢。这里六个尺寸各存一份，
#      用哪个取哪个。
#   ② **PhotoImage 必须缓存住**。Tk 的图片对象一旦被垃圾回收，
#      画布上那块就变空白（这是 Tk 最有名的坑之一）。
#   ③ **绝不在后台线程碰 Tk**（本程序的老规矩）。所以 PhotoImage
#      只在主线程建。
# ==========================================================================

_ICON_CACHE = {}          # (尺寸, 名字) -> ImageTk.PhotoImage
_ICON_PIL = {}            # (尺寸, 名字) -> PIL.Image（缩过一次就留着）


def _icon_pick_size(px):
    """给一个目标像素大小，挑最合适的**内置档位**（就近取大不取小）。

    ★ 为什么"取大不取小"：大图缩小是清楚的，小图放大会糊。
      所以宁可拿大一号的缩下来。
    """
    try:
        px = int(px)
    except Exception:
        px = 48
    best = ICON_SIZES[0]
    for s in ICON_SIZES:
        if s >= px:
            return s
    return ICON_SIZES[-1]      # 比最大档还大 → 就用最大的


def icon_name_for_file(name, is_dir):
    """★ 这个文件名/文件夹，该用哪个图标？（返回图标名，如 "pdf"）

    ★ 兜底一定是 "unknown"，**绝不会返回空** —— 空的话界面上就是一块空白。
    """
    if is_dir:
        return "folder"
    try:
        ext = os.path.splitext(str(name or ""))[1].lower()
    except Exception:
        return "unknown"
    for key, ic in ((".pdf", "pdf"),):
        if ext == key:
            return ic
    if ext in (".doc", ".docx", ".rtf", ".odt"):
        return "word"
    if ext in (".xls", ".xlsx", ".ods", ".csv", ".tsv"):
        return "excel"
    if ext in (".ppt", ".pptx", ".odp", ".pps", ".ppsx"):
        return "ppt"
    if ext in IMAGE_EXTS:
        return "image"
    if ext in VIDEO_EXTS:
        return "video"
    if ext in (".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma",
               ".ape", ".opus"):
        return "audio"
    if ext in (".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"):
        return "zip"
    if ext in BOOK_EXTS:
        return "book"
    if ext in (".exe", ".msi", ".bat", ".cmd", ".com", ".scr", ".appimage",
               ".deb", ".rpm", ".sh", ".run"):
        return "exe"
    if ext in (".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".h",
               ".cpp", ".hpp", ".cs", ".go", ".rs", ".rb", ".php", ".lua",
               ".pl", ".swift", ".kt", ".scala", ".sql", ".vue", ".json",
               ".xml", ".yml", ".yaml", ".toml", ".ini", ".css", ".scss",
               ".less", ".html", ".htm", ".ps1", ".vbs"):
        return "code"
    if ext in (".txt", ".md", ".markdown", ".log", ".nfo", ".srt", ".ass",
               ".vtt", ".url", ".m3u", ".reg", ".cfg", ".conf"):
        return "text"
    return "unknown"


def get_file_icon(name, is_dir, px=48):
    """★ 取一个**可以直接 create_image 用**的图标对象（Tk PhotoImage）。

    取不到就返回 None —— 调用方应该退回原来的 emoji 画法。
    ★ 这个函数**只能在主线程调**（它建 Tk 对象）。
    """
    try:
        if not HAS_PIL or not ICON_PNG:
            return None
        key_name = icon_name_for_file(name, is_dir)
        size = _icon_pick_size(px)
        # ★★ 2026-10-07 修一个真 bug（用户报「调缩略图档位，图标没跟着变大」）：
        #   缓存键**必须带上"实际要的像素尺寸"**，不能只用档位。
        #   原来键是 (档位, 名字) —— 而档位是个**范围**（比如"中"档
        #   对应的桶是 64，但实际可能要 40、56、61 各种值）。
        #   于是：第一次按 40px 画好、缓存住；后面要 56px 时，
        #   键一样 → **直接返回那张 40px 的旧图** → 图标永远不变大。
        #   （实测复现：要 40 得 40，接着要 56 还是 40。）
        #
        #   修法：键 = (档位, 实际像素, 名字)。这样每个真实尺寸各存一份，
        #   既不会拿错，也不会因为尺寸值是浮动的而反复解码。
        try:
            px_i = int(px)
        except Exception:
            px_i = size
        px_i = max(8, px_i)
        key = (size, px_i, key_name)
        got = _ICON_CACHE.get(key)
        if got is not None:
            return got
        b64 = (ICON_PNG.get(size) or {}).get(key_name)
        if not b64:
            # 这一档没这个图 → 退回 unknown（宁可画个问号，也别空白）
            b64 = (ICON_PNG.get(size) or {}).get("unknown")
            key = (size, px_i, "unknown")
            got = _ICON_CACHE.get(key)
            if got is not None:
                return got
        if not b64:
            return None
        import base64
        import io as _io
        from PIL import Image as _Image, ImageTk  # type: ignore
        raw = base64.b64decode(b64)
        # ★ PIL 原图也按档位缓存（解码要几十毫秒，滚动时很卡）。
        #   ★ 这里键只用 (档位, 名字) 是对的 —— 存的是**原始大图**，
        #     缩放结果不往这里放（否则又会串）。
        pil_key = (size, key_name)
        if b64 is (ICON_PNG.get(size) or {}).get("unknown"):
            pil_key = (size, "unknown")
        pil = _ICON_PIL.get(pil_key)
        if pil is None:
            pil = _Image.open(_io.BytesIO(raw)).convert("RGBA")
            _ICON_PIL[pil_key] = pil
        # ★ 目标尺寸跟档位不一样就缩一下（比如档位 64、实际要 40）
        if px_i != int(size):
            pil = pil.resize((px_i, px_i), _Image.LANCZOS)
        photo = ImageTk.PhotoImage(pil)
        _ICON_CACHE[key] = photo
        return photo
    except Exception as _e:
        try:
            note_swallowed(T("取文件图标失败（会退回 emoji 画法）"), _e,
                           quiet=True)
        except Exception:
            pass
        return None


def clear_icon_cache():
    """★ 换皮肤/换图标档位时清一下（现在的图标深浅共用，其实不用清；
    留着这个口子，以后要分深浅两套图标时能直接接上）。"""
    try:
        _ICON_CACHE.clear()
        _ICON_PIL.clear()
    except Exception:
        pass


def _detect_book_drm(path):
    """★ 查这本电子书**是不是加了 DRM 版权保护** —— 是就返回一句人话说明。

    ★★ 2026-10-07 新增。为什么要它：
      用户报「这本电子书解析不出正文」，程序原来列了**三种可能**
      （DRM / 压缩方式少见 / 文件损坏）—— 那是**猜**，等于没说。
      用户还专门问了「**这个加密可以装上什么然后就能预览吗**」，
      说明这个含糊的提示**真的让人困惑**。
      ★ 错题本 #68 那条说得很清楚：
        **"做不到"要提前说清楚为什么，别让用户猜。**

    ★ 怎么查（很简单，不用装东西）：**epub 本质是个 zip 包**，
      加密的 epub 里一定有一个 `META-INF/encryption.xml`，
      里面写着**是谁加的锁**。
      实测那份《大数据时代[精品]》.epub：
        <Proprietary>ZhangYue.Inc</Proprietary>  ← 掌阅
        <EncryptionMethod Algorithm="RSA"/>       ← RSA 加密

    返回：
      · 查出来是加密的 → 一段中文说明（含厂商名）
      · 不是加密的     → 空字符串（调用方照别的路子解释）
    """
    try:
        p = str(path or "")
        if not p.lower().endswith(".epub"):
            return ""      # 只有 epub 能这么查（mobi/azw3 是别的容器）
        import zipfile
        # ★★ 注意：这个文件**开头没有 `import re`**（只有某处局部的
        #   `import re as _re`），所以这里必须**自己 import**。
        #   ★ 我第一次写的时候用了裸 `re.search` → 抛 NameError →
        #     被下面的 except 吞掉 → 永远返回空（"查不出加密"）。
        #     **症状很隐蔽：不报错、只是查不出来。**
        import re as _re
        if not zipfile.is_zipfile(p):
            return ""
        with zipfile.ZipFile(p) as z:
            names = set(z.namelist())
            if "META-INF/encryption.xml" not in names:
                return ""
            raw = z.read("META-INF/encryption.xml")
        txt = raw.decode("utf-8", "replace")
        # 抓"是谁加的锁"
        who = ""
        try:
            mm = _re.search(r"<Proprietary>\s*([^<]{1,60}?)\s*</Proprietary>",
                            txt)
            if mm:
                who = mm.group(1)
        except Exception:
            who = ""
        # 厂商名翻译成人话（认识的翻，不认识的照原样写）
        nice = {
            "ZhangYue.Inc": "掌阅（ZhangYue）",
            "Adobe": "Adobe（数字版版权保护）",
            "Kobo": "Kobo",
            "Barnes & Noble": "Barnes & Noble",
        }.get(who, who)
        line = ("查到的加密信息：**%s**。\n" % nice) if nice else \
               "查到的加密信息：这份 epub 里有加密标记。\n"
        return line
    except Exception:
        return ""


# ★★ 2026-10-07 新增：**界面上的小图标**（不光是文件类型图标）
#   ----------------------------------------------------------------------
#   用户报「**放大镜图标识别不出来**」—— 因为搜索框前面画的是 emoji `🔍`。
#   emoji 的问题（用户早就说过）：
#     · 不同系统 / 不同字体下**长相差别很大**，甚至显示成豆腐块
#     · 小尺寸下糊成一团，看不清是个放大镜
#   ★ 用户定过的规矩：「图标全部换成图片型的，这套符号普世性不高」。
#
#   这个函数把「一个名字」变成**能直接贴到控件上的图片对象**：
#       lbl = ttk.Label(parent, image=get_ui_icon("search", 18))
#   取不到就返回 None，调用方**自己退回文字**（宁可显示个 emoji，也别空白）。
#
#   ★ 两个必须注意的（踩过）：
#     ① **图片对象必须留长引用**，否则被 Python 回收，控件上变成空白
#        （错题本 #2 就是这个）。所以这里把返回的对象**存进一个全局列表**。
#     ② 只能**主线程**调（它建 Tk 对象）。
_UI_ICON_REFS = []      # ← 长引用，别删！


class Tooltip:
    """★ 悬停提示（鼠标停在控件上，过一会儿弹一句说明）。

    ★★ 2026-10-07 新增。为什么要它：
      预览区新加的**缩放按钮是图标**（➕ ➖），
      光看图用户不一定知道"这是放大还是缩小"、"有没有快捷键"——
      得有一句话说明。用户之前也提过想要「ⓘ 悬停提示」这类东西。

    ★ 三个细节（都是照外面成熟做法来的）：
      · **延迟 600 毫秒**才弹 —— 鼠标划过时不该弹
      · 鼠标一移开**立刻收**（不然会挡着看东西）
      · 提示文字**跟着皮肤走**（不然夜间弹出一块白板）
    """

    def __init__(self, widget, text, delay=600):
        self.widget = widget
        self.text = str(text or "")
        self.delay = int(delay)
        self._after_id = None
        self._win = None
        try:
            widget.bind("<Enter>", self._schedule, add="+")
            widget.bind("<Leave>", self._hide, add="+")
            # 点一下也收掉（不然点完还挂着）
            widget.bind("<Button>", self._hide, add="+")
            widget.bind("<Destroy>", self._hide, add="+")
        except Exception:
            pass

    def _schedule(self, _e=None):
        self._cancel()
        try:
            self._after_id = self.widget.after(self.delay, self._show)
        except Exception:
            self._after_id = None

    def _cancel(self):
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self):
        if self._win is not None or not self.text:
            return
        try:
            x = self.widget.winfo_rootx() + 12
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
            w = tk.Toplevel(self.widget)
            w.wm_overrideredirect(True)          # 去掉标题栏
            w.wm_geometry("+%d+%d" % (x, y))
            try:
                w.attributes("-topmost", True)
            except Exception:
                pass
            bg = theme_get("panel_bg")
            fg = theme_get("fg")
            tk.Label(w, text=self.text, bg=bg, fg=fg,
                     font=(FONT, UI_FONT_SIZE_SMALL),
                     padx=8, pady=4, relief="solid", bd=1,
                     highlightbackground=theme_get("line")).pack()
            self._win = w
        except Exception:
            self._win = None

    def _hide(self, _e=None):
        self._cancel()
        if self._win is not None:
            try:
                self._win.destroy()
            except Exception:
                pass
            self._win = None


def get_ui_icon(name, px=16):
    """取一个界面小图标（如 "search" 放大镜），返回 Tk PhotoImage；取不到返回 None。

    ★ px 是"大概要多大"（按屏幕会有微调，跟文件图标一个路子）。
    ★ 只能主线程调。

    ★★ 2026-10-07 修一个真 bug（我第一版就写错了）：
      第一版这里调的是 `get_file_icon(name, False, px)` ——
      可是 `get_file_icon` 会拿 name 去当**文件名**推图标
      （`icon_name_for_file("search")` → "search" 没扩展名 → 返回 **"unknown"**）
      → 界面上显示出来是**一个问号 `?`**。
      ★ 所以界面图标必须**按名字直查**，不能走"文件名推断"那条路。
      现在直接查 `ICON_PNG[档位][名字]`。
    """
    try:
        if not ICON_PNG:
            return None
        size = _icon_pick_size(px)
        try:
            px_i = max(8, int(px))
        except Exception:
            px_i = size
        key = (size, px_i, name)
        got = _ICON_CACHE.get(key)
        if got is not None:
            return got
        b64 = (ICON_PNG.get(size) or {}).get(name)
        if not b64:
            return None                      # 没这个图标 → 调用方自己退回文字
        import base64
        import io as _io
        raw = base64.b64decode(b64)
        try:
            from PIL import Image, ImageTk
        except Exception:
            return None
        pil = Image.open(_io.BytesIO(raw)).convert("RGBA")
        if pil.size[0] != px_i:
            pil = pil.resize((px_i, px_i), Image.LANCZOS)
        img = ImageTk.PhotoImage(pil)
        _ICON_CACHE[key] = img
        # 留长引用（不然被回收，控件上变空白 —— 错题本 #2）
        try:
            _UI_ICON_REFS.append(img)
            if len(_UI_ICON_REFS) > 400:
                del _UI_ICON_REFS[:200]
        except Exception:
            pass
        return img
    except Exception:
        return None


def make_search_label(parent, text=None, px=16, **kw):
    """★ 造一个「放大镜图片 + 文字」的小标签（搜索框前面那个）。

    ★ 为什么包一层：程序里**十几处**搜索框都写着
        make_search_label(sbar, T("搜索文件："))
      要是一个个手改，容易漏、也容易写歪。统一走这个函数，
      以后要换图标只改一处。

    ★ 取不到图片就**老老实实退回 emoji** —— 绝不显示空白。
      （错题本 #5 那条：「最坏情况要能看能点，不能一片空白」。）
    """
    # ★★ 2026-10-08：**不管调用方传什么，这里都再翻一次** ——
    #   · 有的地方写 `make_search_label(sbar, T("搜索标签："))`（已翻）
    #   · 有的地方写 `make_search_label(sbar, "搜索标签：")`（**原文**）
    #   ★ 再翻一次对"已翻好的"**无害**（表里查不到就原样返回）——
    #     所以**统一在这里兜底**，比"到处去改调用方"可靠。
    #   ★★ 判据：**"兜底放在最靠近使用的地方"**，
    #     而不是"指望每个调用方都记得翻"。
    if text is None:
        text = T("搜索文件：")
    try:
        text = T(text)
    except Exception:
        pass
    try:
        img = get_ui_icon("search", px)
    except Exception:
        img = None
    try:
        if img is not None:
            lbl = ttk.Label(parent, image=img, compound="left", text=text, **kw)
            # ★ 再留一次引用（控件自己也持有一份，双保险）
            try:
                lbl._icon_ref = img
            except Exception:
                pass
            return lbl
    except Exception:
        pass
    # 退回 emoji
    return ttk.Label(parent, text=("🔍 " + text) if text else "🔍", **kw)



# ==========================================================================
# ★ v25 补丁27：鼠标悬停预览（把鼠标停在文件上，弹个小窗看内容，移开就没）
#   ----------------------------------------------------------------------
#   图片：直接把图显示出来；
#   视频：想办法拿一帧画面（① Windows 自己做的缩略图 ② ffmpeg 截帧），
#         都拿不到就显示一个「▶ 视频」提示牌（不硬撑）；
#   文本：显示前几 KB；其它：显示名称 / 大小 / 时间。
#   ★ 只读；**鼠标停住 0.6 秒之后**才去读文件，不会拖慢你划来划去。
# ==========================================================================

def archive_extract(exe, archive_path, dest_dir, on_line=None):
    """★ 补丁28：用 7-Zip 解一个压缩包到 dest_dir。

    返回 (成功?, 说明文字)。**只解压，不删原压缩包**。
    on_line：可选回调，用来把 7-Zip 的进度行喂给界面（在外面跑时用）。
    """
    if not exe:
        return False, "没找到 7-Zip（免安装版应该在 I 盘那个目录里）"
    try:
        os.makedirs(dest_dir, exist_ok=True)
    except Exception as exc:
        return False, "建不了目标文件夹：%s" % exc
    cmd = [exe, "x", archive_path, "-o" + dest_dir, "-y",
           "-bso1", "-bsp1", "-bb1"]
    try:
        r = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, timeout=3600,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        text = r.stdout.decode("utf-8", "replace")
    except Exception as exc:
        return False, "解压出错：%s" % exc
    if on_line:
        for ln in (text or "").splitlines():
            try:
                on_line(ln)
            except Exception:
                pass
    if r.returncode == 0 and "Everything is Ok" in (text or ""):
        return True, "解压完成"
    # 有加密 / 有坏包时 7-Zip 会返回非 0
    tail = "\n".join((text or "").strip().splitlines()[-4:])
    if "Wrong password" in (text or "") or "encrypted" in (text or "").lower():
        return False, "这个压缩包有密码，解不开（需要密码的包暂不支持）"
    return False, "解压没成功（7-Zip 说）：%s" % tail[:300]


def archive_list(exe, archive_path):
    """★ 补丁28：列出压缩包里有什么（返回文件名列表；失败返回空表）。"""
    if not exe:
        return []
    try:
        r = subprocess.run(
            [exe, "l", "-ba", "-slt", archive_path],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL, timeout=120,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        text = r.stdout.decode("utf-8", "replace")
    except Exception:
        return []
    out = []
    for ln in text.splitlines():
        if ln.startswith("Path = "):
            out.append(ln[7:].strip())
    return out


def seven_zip_exe():
    """★ 补丁28：找 7-Zip 的命令行程序（免安装版优先）。找不到返回 None。"""
    for p in SEVEN_ZIP_CANDIDATES:
        try:
            if os.path.exists(p):
                return p
        except Exception:
            continue
    return None


def get_pdf_page_pil(path, page=0, max_w=520, max_h=680):
    """★ 补丁28：把 PDF 的某一页画成图（PIL 对象）。失败返回 None。

    用 PyMuPDF（装在 E 盘）。只读文件，不写任何东西。
    page 从 0 开始。max_w/max_h 是渲染出来的最大像素尺寸。
    """
    if not HAS_FITZ:
        return None
    try:
        from PIL import Image  # type: ignore
        doc = _fitz_mod.open(path)
        try:
            if doc.page_count <= 0:
                return None
            if page < 0:
                page = 0
            if page >= doc.page_count:
                page = doc.page_count - 1
            pg = doc.load_page(page)
            rect = pg.rect
            z = 1.0
            try:
                z = min(max_w / max(rect.width, 1),
                        max_h / max(rect.height, 1))
            except Exception:
                z = 1.0
            z = max(0.2, min(3.0, z))
            pix = pg.get_pixmap(matrix=_fitz_mod.Matrix(z, z), alpha=False)
            im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            return im
        finally:
            try:
                doc.close()
            except Exception:
                pass
    except Exception as exc:
        try:
            note_swallowed(T("PDF 预览：渲染失败"), exc)
        except Exception:
            pass
        return None


BOOK_EXTS = {".epub", ".mobi", ".azw", ".azw3", ".fb2"}


def book_load(path):
    """★ v25 补丁29：统一入口 —— 读电子书，返回 (书名, [章节文本...])。

    EPUB / FB2 走文本解析；MOBI / AZW / AZW3 走二进制解析（可能只有一段）。
    读不出来返回 (None, [])。
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == ".epub":
        ch = _epub_chapters(path)
        if ch:
            return (None, [t for _n, t in ch])
        return None, []
    if ext == ".fb2":
        # FB2 就是 XML，直接当文本读
        try:
            with open(path, "rb") as f:
                raw = f.read(2 * 1024 * 1024)
            txt = raw.decode("utf-8", "replace")
            import html.parser

            class _G(html.parser.HTMLParser):
                def __init__(self):
                    super().__init__(convert_charrefs=True)
                    self.buf = []

                def handle_data(self, d):
                    self.buf.append(d)

            g = _G()
            g.feed(txt)
            body = "".join(g.buf)
            body = "\n".join(l.strip() for l in body.splitlines()
                             if l.strip())
            return None, [body]
        except Exception:
            return None, []
    # MOBI 家族
    title, txt = _mobi_meta_and_text(path)
    if txt:
        return title, [txt]
    return title, []


def pdf_page_count(path):
    """★ 补丁28：PDF 有几页（读不到返回 0）。"""
    if not HAS_FITZ:
        return 0
    try:
        doc = _fitz_mod.open(path)
        try:
            return int(doc.page_count)
        finally:
            doc.close()
    except Exception:
        return 0


# ==========================================================================
# ★★ 2026-10-06 新增：**后台渲染一律不碰界面，读文件一律带超时**
#
#   为什么要有这两件东西（都是实测出来的，不是猜的）：
#
#   ① 把界面卡死的元凶：**后台渲染线程里调了界面控件**
#      `_pdf_bg_render` / `_pdf_rerender_if_needed` 是从后台线程跑的，
#      但里面写了一句 `self._ui(apply)` —— 这会绕回主线程去改界面控件。
#      Tcl 解释器**同一时刻只许一个线程碰**。用户切文件切得快的时候：
#        后台线程正在渲染 → 主线程正在处理鼠标 → 两边撞上 →
#        **整个程序冻死**（窗口点不动、关不掉，只能强杀）。
#      实测复现：48 次快速切换，最慢一次 8.7 秒，整体僵住。
#      ★ 正确做法（成熟软件都这么干）：**后台线程干完活只往一个 Python
#        列表里排队**，排队前先看一眼「我这次的文件标签还对不对」，
#        不对就把渲染好的图**扔掉**（反正用户已经看别的文件了），
#        绝不为了报送结果去抢 Tcl。
#      ★ 一句话铁律：**后台线程只准读数据、算东西，一个界面控件都不许碰。**
#
#   ② 另一个会把界面冻住的：**网盘卡住时 PyMuPDF 会无限期等**
#      实测（用户网盘上的一本 PDF）：`pymupdf.open()` 最慢 **6.5 秒**；
#      用户在网盘里来回翻的时候，这几秒**整条界面都是死的**。
#      所以：**主线程里只做「开文件 + 读页数」这类极小的事，而且带超时**；
#      真正的渲染（`get_pixmap`）**全部丢后台**。
# ==========================================================================

# 后台任务的「信箱」——只在主程序里建一次（别每个窗格一份，编号会撞）
_UI_MAIL = {"box": None, "seq": 1}


def _ui_mail_box():
    """拿到（或建立）进程内唯一的一个「后台→主线程」信箱。"""
    b = _UI_MAIL.get("box")
    if b is None:
        up = {"q": [], "lock": threading.Lock()}
        b = up
        _UI_MAIL["box"] = b
    return b


def _bg_post(fn, *a):
    """（后台线程专用）把一件「想让主线程做的事」丢进信箱 —— **绝不碰 Tcl**。

    返回 True 表示排上了；返回 False 表示程序正在关，直接别排了。

    ★ 这个函数**只有列表操作和一把普通锁**，一步 Tcl 都不碰，
      所以后台线程叫它永远不会卡住。
    """
    if APP_CLOSING:
        return False
    try:
        b = _ui_mail_box()
        with b["lock"]:
            b["q"].append((fn, a))
        return True
    except Exception:
        return False


def _mailbox_preload_doc(doc, path):
    """把「已经开好的 PDF 文档」暂时寄放在信箱里，给后台渲染线程用一次。

    ★ 为什么要这么做：开网盘上的 PDF 要 1 秒左右（实测最慢 6.5 秒）。
      「开文件」必须在主线程做（PyMuPDF 的文档跨线程用不安全），
      但「渲染」必须在后台做（渲染要几秒，在主线程做界面就死了）。
      所以主线程开好之后，把这个文档**寄在信箱里**，后台线程取走用。
    ★ 寄放的东西**必须有归宿**：要么被后台线程取走，要么在
      下一次 `_drain_ui_mail` 时被主动关掉（见那里）。
      这样就不会出现「开了一堆文档没人关、内存越吃越多」。
    ★ 一次只留一份（新的来了把旧的关掉）—— 反正用户一次只看一个文件。
    """
    try:
        b = _ui_mail_box()
        old = b.get("doc")
        if old is not None and old is not doc:
            try:
                old.close()
            except Exception:
                pass
        import time as _t
        b["doc"] = doc
        b["doc_path"] = path
        b["doc_taken"] = False
        b["doc_time"] = _t.time()
        return True
    except Exception:
        try:
            doc.close()
        except Exception:
            pass
        return False


def _mailbox_take_doc(path):
    """（后台线程专用）把寄放的文档取走（只给这个路径的）。

    取不到返回 None（比如已经被别人取走、或者路径对不上）。
    """
    try:
        b = _ui_mail_box()
        if b.get("doc") is not None and not b.get("doc_taken") \
                and b.get("doc_path") == path:
            b["doc_taken"] = True
            return b["doc"]
    except Exception:
        pass
    return None


def _mailbox_close_doc(doc):
    """（后台线程用）用完就关掉。"""
    try:
        if doc is not None:
            doc.close()
    except Exception:
        pass


def _drain_ui_mail(limit=80, budget_ms=35.0):
    """（**主线程**）把信箱里排着的活儿干一遍。

    ★ 为什么要有 limit：万一批量特别大（比如几百页 PDF），
      一口气全干完会让界面「愣」好几秒。每轮只干一小批，
      剩下的下一轮（主程序每 60 毫秒跑一次 `_ui_poll`）接着干。

    ★★ 2026-10-06 新增 budget_ms（时间预算）★
      光有「最多几条」还不够：一条「排 50 页」的活儿本身就要
      200~600 毫秒，攒几条一起做，界面照样会一顿一顿的。
      所以再加一道闸：**这一轮最多只干 budget_ms 毫秒**，
      超了就立刻收手，剩下的下一轮再说。
      这样界面永远保持「几十毫秒一小步」的节奏 ——
      用户的感觉就是**一直在跟手**，而不是「一顿一顿」。

    ★ 顺便把「寄放着没人用」的 PDF 文档关掉 —— 免得漏内存 / 漏文件句柄。
    """
    import time as _time
    _t0 = _time.perf_counter()
    n = 0
    while n < limit:
        # ★ 时间预算到了就收手（至少干一件，免得永远干不动）
        if n > 0 and (_time.perf_counter() - _t0) * 1000.0 >= budget_ms:
            break
        try:
            b = _ui_mail_box()
            with b["lock"]:
                if not b["q"]:
                    break
                fn, a = b["q"].pop(0)
        except Exception:
            break
        try:
            fn(*a)
        except Exception as _e:
            try:
                note_swallowed(T("后台任务交回主线程时失败了"), _e, quiet=True)
            except Exception:
                pass
        n += 1
    # ★ 信箱里寄放的 PDF 文档：如果一直没人取走，就在这儿关掉。
    #   （寄放后马上就会被后台线程取走；取走的会把标记改成 True。）
    try:
        b = _ui_mail_box()
        d = b.get("doc")
        if d is not None and b.get("doc_taken"):
            b["doc"] = None
            b["doc_path"] = None
        elif d is not None:
            # 还没被取走 —— 检查一下它是不是「已经过期的寄放」
            # （超过 20 秒没人用就直接关，免得一直占着网盘句柄）
            import time as _t
            if _t.time() - float(b.get("doc_time", 0) or 0) > 20:
                try:
                    d.close()
                except Exception:
                    pass
                b["doc"] = None
                b["doc_path"] = None
    except Exception:
        pass
    return n


def pdf_prepare(path, timeout=4.0):
    """★ 打开 PDF 并且拿到页数 —— 这两步都是**小活儿**，但要带超时。

    返回 `(doc, total)`：
      · 成功 → (文档对象, 页数)。**调用方必须自己 doc.close()**。
      · 超时 → (None, "超时")   —— 注意第二种是字符串，用 `is None` 判断即可。
      · 打不开 → (None, 0)

    ★ 为什么要超时：实测网盘上一本 PDF 光「打开」就要 6.5 秒。
      这一次调用是**在主线程里**做的（因为要把文档句柄交给后台线程接着渲），
      正常只要 1 秒左右；万一网盘抽风，最多卡 timeout 秒就放弃，
      界面不会一直冻着。

    ★ 为什么不让后台线程自己开：后台线程拿到的文档句柄交给主线程用、
      或者主线程拿到的交给后台用，PyMuPDF 都不保证安全。
      所以规矩是：**开文件 + 读页数在主线程（带超时），
      渲染 get_pixmap 在后台线程**。
    """
    if not HAS_FITZ:
        return None, 0
    if getattr(sys, "_is_frozen", False):
        pass
    out = {}

    def _work():
        try:
            d = _fitz_mod.open(path)
            try:
                n = int(d.page_count)
            except Exception:
                n = 0
            out["doc"] = d
            out["n"] = n
        except Exception as e:
            out["err"] = e

    t = threading.Thread(target=_work, daemon=True, name="打开PDF")
    t.start()
    t.join(timeout)
    if t.is_alive():
        # 超时了：这个后台线程还在网盘那儿等着，让它自己去死（daemon），
        # 我们这边立刻撒手，界面照常能用。
        return None, "超时"
    if "err" in out:
        try:
            note_swallowed(T("PDF 预览：打不开这个文件"), out["err"], quiet=True)
        except Exception:
            pass
        return None, 0
    return out.get("doc"), int(out.get("n") or 0)


def pdf_probe_type(path, timeout=3.0):
    """★ 只探「这个 PDF 能不能开」，**不留下打开的文档**。

    用途：主线程在跟用户说「正在打开…」的时候，顺手起一个后台线程去探；
    等它探完，用户按「🔄 重新加载」时就能**秒开**（不用再等网盘）。
    探完立刻关掉，不占网盘句柄。

    返回 True（能开）/ False / "超时"。
    """
    ok = {}
    t = threading.Thread(target=lambda: _probe(path, ok), daemon=True,
                         name="探PDF")
    t.start()
    t.join(timeout)
    if t.is_alive():
        return "超时"
    return bool(ok.get("ok"))


def _probe(path, out):
    try:
        d = _fitz_mod.open(path)
        try:
            out["ok"] = int(d.page_count) > 0
        finally:
            d.close()
    except Exception:
        out["ok"] = False


def render_pdf_page(doc, page, max_w=520, max_h=680):
    """★（**后台线程专用**）把一页画成 PIL 图，画不出来返回 None。

    只做渲染，一个界面控件都不碰 —— 这是安全的关键。
    """
    try:
        from PIL import Image  # type: ignore
    except Exception:
        return None
    try:
        if doc is None:
            return None
        n = int(doc.page_count)
        if n <= 0:
            return None
        if page < 0:
            page = 0
        if page >= n:
            page = n - 1
        pg = doc.load_page(page)
        rect = pg.rect
        z = 1.0
        try:
            z = min(max_w / max(rect.width, 1), max_h / max(rect.height, 1))
        except Exception:
            z = 1.0
        z = max(0.2, min(3.0, z))
        pix = pg.get_pixmap(matrix=_fitz_mod.Matrix(z, z), alpha=False)
        return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    except Exception as e:
        try:
            note_swallowed(T("PDF 预览：后台渲染某一页失败"), e, quiet=True)
        except Exception:
            pass
        return None


def auto_color(index):
    h = (index * 0.618033988749895 + 0.13) % 1.0
    r, g, b = colorsys.hls_to_rgb(h, 0.50, 0.62)
    return "#%02x%02x%02x" % (int(r * 255 + 0.5),
                              int(g * 255 + 0.5),
                              int(b * 255 + 0.5))


def text_color_for(bg_hex):
    h = (bg_hex or "#3498db").lstrip("#")
    try:
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
    except (ValueError, IndexError):
        return "white"
    y = r * 0.299 + g * 0.587 + b * 0.114
    return "#1a1a1a" if y > 175 else "white"


def icon_for_file(name, is_dir):
    if is_dir:
        return "📁"
    ext = os.path.splitext(name)[1].lower()
    return EXT_ICONS.get(ext, "📄")


class _TNode:
    __slots__ = ("tag_id", "name", "color", "count", "sort_order",
                 "parents", "children", "x", "y", "w", "h", "depth", "font_size")

    def __init__(self, tid, name, color, count, sort_order):
        self.tag_id = tid
        self.name = name
        self.color = color
        self.count = count
        self.sort_order = sort_order
        self.parents = []
        self.children = []
        self.x = self.y = 0
        self.w = self.h = 0
        self.depth = 0
        self.font_size = 10


# ==========================================================================
#  数据层
# ==========================================================================
# ==========================================================================
#  ★★★ 2026-10-08 **TagStore 搬到独立文件了**（第 1 批拆分）
#  --------------------------------------------------------------------------
#  ★★ 为什么搬：它是**最大的一块**（3,132 行 / 122 个方法），
#     而**量过之后发现它最适合搬**：
#       · 不依赖界面（`self.app` 出现 **0 次**）
#       · 只借 %d 个"主程序自己造的名字"，而且全部定义在它之前
#       · ★★ 主程序里 `TagStore(` **只构造 1 次** → **调用方一行不用改**
#
#  ★★ 搬走之后主程序这边留什么：**一个 try 导入**。
#     ★ 为什么不留"内置兜底版"（像别的模块那样）：
#       那 3,132 行**留一份就等于没拆** —— 文件还是 4 万行。
#       → 所以这里**只导入**；导不进来就**报一句清楚的话**，
#         告诉人"哪个文件丢了、从哪儿找回来"（而不是崩得莫名其妙）。
#
#  ★★★ 万一这个文件丢了/坏了怎么办：
#     ① 备份里有（`备份\` 目录）
#     ② 或者把 `AIxiede.py.bak-搬TagStore前` 里那 3,132 行拷回来
#     ★ 程序**不会因此打不开**吗？—— 会打不开（数据层没了没法干活）
#       ★ 但**会报清楚的话**，而且**提示在哪儿找回来**，
#         比"莫名其妙崩掉"好得多。
# ==========================================================================
try:
    # ★★ 先导入"模块本身"（拿到 `_set_app`），再导入"类"。
    #   ★ 为什么分两步：`_set_app` 是**模块级函数**，
    #     从 `TagStore` 类上拿不到（它不是类的方法）。
    import TagStore as _tsmod
    _tsmod._set_app(sys.modules[__name__])
    TagStore = _tsmod.TagStore
    _HAS_TS_FILE = True
except Exception as _e_ts:
    _HAS_TS_FILE = False
    # ★ 导入失败：**给一个"看起来像 TagStore、一用就报清楚错"的替身** ——
    #   ★ 为什么不直接 raise：那样**程序连界面都起不来**，
    #     用户看到的是"打不开"（最难受的那种）。
    #   ★ 给替身的代价：程序能起来、界面能看到，
    #     但**一碰数据就报那句清楚的话** —— 至少知道发生了啥。
    _TS_IMPORT_ERR = _e_ts

    class TagStore(object):
        """★ 占位替身（真的 TagStore 没导进来）。"""

        def __init__(self, *a, **kw):
            raise RuntimeError(
                "数据层模块（TagStore.py）没找到或有问题，程序无法读写数据。\n\n"
                "  原因：%r\n\n"
                "  怎么修：\n"
                "    ① 看程序目录下 `AIxiede拆分开\\程序分块\\TagStore.py` "
                "在不在；\n"
                "    ② 不在就从 `备份\\` 里找一份，或者从 "
                "`AIxiede.py.bak-搬TagStore前` 里把那段代码拷回来；\n"
                "    ③ 找回来之后重开程序即可。" % (_TS_IMPORT_ERR,))

# ==========================================================================
# ★★★ 「缓存设置」这组方法已搬到 `AIxiede拆分开/程序分块/面板_缓存设置.py`
#   ★★ 搬法跟独立类不同：方法体搬走，类里留**一行转发**（稳定接口）——
#      所有调用方（菜单/按钮/别的 self.方法）**一个字都不用改**。
#   ★★★ 但**必须有下面这个 import**（错题本 #166）：
#      没有它 → 类里那行转发会 `NameError` ——
#      而且**平时看不出来**，只有真点到那个按钮才炸。
try:
    import 面板_缓存设置 as _面板缓存设置
    _面板缓存设置._set_app(sys.modules[__name__])
    _HAS_PANEL_缓存设置 = True
except Exception as _e:
    _HAS_PANEL_缓存设置 = False
    note_swallowed(T("搬出去的 面板_缓存设置.py 没找到"), _e)


# ★★★ 「面板布局」这组方法已搬到 `AIxiede拆分开/程序分块/面板_面板布局.py`
#   ★★ 搬法跟独立类不同：方法体搬走，类里留**一行转发**（稳定接口）——
#      所有调用方（菜单/按钮/别的 self.方法）**一个字都不用改**。
#   ★★★ 但**必须有下面这个 import**（错题本 #166）：
#      没有它 → 类里那行转发会 `NameError` ——
#      而且**平时看不出来**，只有真点到那个按钮才炸。
try:
    import 面板_面板布局 as _面板面板布局
    _面板面板布局._set_app(sys.modules[__name__])
    _HAS_PANEL_面板布局 = True
except Exception as _e:
    _HAS_PANEL_面板布局 = False
    note_swallowed(T("搬出去的 面板_面板布局.py 没找到"), _e)


# ★★★ FileList 已拆到 `AIxiede拆分开/程序分块/FileList.py`（2026-10-08）
#   ★★ 写法（错题本 #158）：① 直接 `from FileList import …`（不带包路径）
#     ② `_set_app` 取别名 —— 模块名和类名同名时会跑到类上找
try:
    from FileList import FileList, _set_app as _fk_FileList
    _fk_FileList(sys.modules[__name__])
    _HAS_FILELIST = True
except Exception as _e:
    _HAS_FILELIST = False
    note_swallowed(T("拆出去的 FileList.py 没找到，已退回内置简易版"), _e)

    class FileList:  # ★ 兜底：没模块也不崩，只是没这个功能
        def __init__(self, *a, **k):
            pass

        def _icon_px_table(self, *a, **k):
            pass

        def icon_sizes(self, *a, **k):
            pass

        def refresh_icon_sizes(self, *a, **k):
            pass

        def _make_toggle(self, *a, **k):
            pass

        def _tagbar_sig_of(self, *a, **k):
            pass

        def _style_pill(self, *a, **k):
            pass

        def _restyle_tagbar(self, *a, **k):
            pass


# ★★ 2026-10-06：这个类已拆到单独的文件里（AIxiede拆分开/程序分块/SimpleInputDialog.py）。
#   这里保留一个「转发」：程序照常能用，但代码在那边维护。
#
#   ★ 两个要点（都是拆文件必须处理的，别再踩）：
#     ① **分块文件夹要在「找文件的路」上** —— 这一步在文件最开头
#        （import os / sys 那一段）已经做了，这里不用重复做。
#     ② **兜底里不能调用后面才定义的东西**（比如 note_swallowed 在 3300 行
#        才定义，这里在一万多行）—— 那样兜底自己就会报错。
#        所以兜底里只做最朴素的事（print）。
try:
    from SimpleInputDialog import SimpleInputDialog, _set_app as _sip_set_app
    _sip_set_app(sys.modules[__name__])
    _SIP_OK = True
except Exception:
    _SIP_OK = False

if not _SIP_OK:
    # ★ 万一新文件丢了/损坏了，程序**必须还能开** —— 这里做兜底：
    #   老老实实给一个「能用的简易输入框」，绝不让程序打不开。
    try:
        print("[提示] 拆出去的 SimpleInputDialog.py 没找到，已退回内置简易版")
    except Exception:
        pass
    # ★ 把**真实原因**也打出来，方便排查（用户看不懂不要紧，维护的人需要）
    try:
        import traceback as _tb
        print("[排查] 导入 SimpleInputDialog 失败的真实原因：")
        _tb.print_exc(file=sys.stdout)
    except Exception:
        pass

    class SimpleInputDialog(tk.Toplevel):
        def __init__(self, master, title=T("输入"), initial="", values=None):
            super().__init__(master)
            self.title(title)
            self.resizable(False, False)
            self.result = None
            body = ttk.Frame(self, padding=14)
            body.pack(fill="both", expand=True)
            ttk.Label(body, text=title).pack(anchor="w", pady=(0, 6))
            self.var = tk.StringVar(value=initial)
            w = (ttk.Combobox(body, textvariable=self.var, values=values, width=30)
                 if values else ttk.Entry(body, textvariable=self.var, width=30))
            w.pack(fill="x")
            w.focus_set()
            btns = ttk.Frame(body)
            btns.pack(fill="x", pady=(12, 0))
            ttk.Button(btns, text=T("确定"), command=self._ok).pack(side="right")
            ttk.Button(btns, text=T("取消"), command=self._cancel).pack(side="right", padx=6)
            self.bind("<Return>", lambda e: self._ok())
            self.bind("<Escape>", lambda e: self._cancel)
            self.protocol("WM_DELETE_WINDOW", self._cancel)
            self.transient(master)
            self.grab_set()
            self.wait_window(self)

        def _ok(self):
            self.result = self.var.get().strip()
            self.destroy()

        def _cancel(self):
            self.result = None
            self.destroy()

# ★★ 2026-10-06：这个类已拆到单独的文件里
#   （AIxiede拆分开/程序分块/CategoryDialog.py）。
#   这里保留一个「转发」：程序照常能用，但代码在那边维护。
#   ★ 兜底自带一份**原样代码** —— 就算新文件丢了/损坏了，
#     程序照样开得起来（用户最怕的就是「双击打不开」）。
try:
    from CategoryDialog import CategoryDialog, _set_app as _fk_CategoryDialog
    _fk_CategoryDialog(sys.modules[__name__])
except Exception:
    try:
        print("[提示] 拆出去的 CategoryDialog.py 没找到，已退回内置简易版")
    except Exception:
        pass

    # ↓↓↓ 兜底用的原代码（新文件正常时不走这里）↓↓↓
    class CategoryDialog(tk.Toplevel):
        AVATAR_SIZE = 48

        def __init__(self, master, title=T("新建分类"), cat=None):
            super().__init__(master)
            self.title(title)
            self.resizable(False, False)
            self.result = None
            self._preview_img = None

            cat = cat or {}
            self.color = cat.get("color") or CAT_COLORS[0]
            self.icon_type = tk.StringVar(value=cat.get("icon_type") or "text")
            self.icon_text = tk.StringVar(value=cat.get("icon") or "")
            self.icon_path = tk.StringVar(value=cat.get("icon_path") or "")
            self.name_var = tk.StringVar(value=cat.get("name", ""))

            body = ttk.Frame(self, padding=16)
            body.pack(fill="both", expand=True)

            row = ttk.Frame(body)
            row.pack(fill="x", pady=(0, 10))
            ttk.Label(row, text=T("分类名称"), width=9).pack(side="left")
            e = ttk.Entry(row, textvariable=self.name_var, width=30)
            e.pack(side="left", fill="x", expand=True)
            e.focus_set()
            self.name_var.trace_add("write", lambda *a: self._draw_preview())

            row2 = ttk.Frame(body)
            row2.pack(fill="x", pady=(0, 8))
            ttk.Label(row2, text=T("头像"), width=9).pack(side="left", anchor="n")

            self.preview = tk.Canvas(row2, width=self.AVATAR_SIZE, height=self.AVATAR_SIZE,
                                     highlightthickness=0, bg=theme_get("card_bg"))
            self.preview.pack(side="left", padx=(0, 10))

            right = ttk.Frame(row2)
            right.pack(side="left", fill="x", expand=True)

            ttk.Radiobutton(right, text=T("文字 / 表情"), value="text",
                            variable=self.icon_type, command=self._update).pack(anchor="w")
            self.text_entry = ttk.Entry(right, textvariable=self.icon_text, width=14)
            self.text_entry.pack(anchor="w", pady=(2, 4))
            self.icon_text.trace_add("write", lambda *a: self._draw_preview())

            ttk.Radiobutton(right, text=T("图片文件"), value="image",
                            variable=self.icon_type, command=self._update).pack(anchor="w")
            img_row = ttk.Frame(right)
            img_row.pack(anchor="w", pady=(2, 0))
            ttk.Button(img_row, text=T("选择图片…"), command=self._choose_image).pack(side="left")
            ttk.Button(img_row, text=T("清除"), width=6,
                       command=self._clear_image).pack(side="left", padx=4)
            self.img_label = ttk.Label(right, text="", foreground=theme_get("fg_dim"))
            self.img_label.pack(anchor="w", pady=(2, 0))

            row3 = ttk.Frame(body)
            row3.pack(fill="x", pady=(10, 0))
            ttk.Label(row3, text=T("主题颜色"), width=9).pack(side="left")
            self.color_btn = tk.Button(row3, text="  ", bg=self.color, width=6,
                                       relief="groove", command=self._choose_color)
            self.color_btn.pack(side="left")
            self.color_hex = ttk.Label(row3, text=self.color, foreground=theme_get("fg_dim"))
            self.color_hex.pack(side="left", padx=8)

            btns = ttk.Frame(body)
            btns.pack(fill="x", pady=(16, 0))
            ttk.Button(btns, text=T("确定"), command=self._ok).pack(side="right")
            ttk.Button(btns, text=T("取消"), command=self._cancel).pack(side="right", padx=6)

            self.bind("<Return>", lambda e: self._ok())
            self.bind("<Escape>", lambda e: self._cancel())
            self.protocol("WM_DELETE_WINDOW", self._cancel)
            self._update()

            self.update_idletasks()
            w, h = self.winfo_width(), self.winfo_height()
            x = master.winfo_rootx() + (master.winfo_width() - w) // 2
            y = master.winfo_rooty() + (master.winfo_height() - h) // 3
            self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
            self.transient(master)
            self.grab_set()
            self.wait_window(self)

        def _update(self):
            self.text_entry.configure(
                state="normal" if self.icon_type.get() == "text" else "disabled")
            self._draw_preview()

        def _choose_image(self):
            path = filedialog.askopenfilename(
                title=T("选择头像图片"),
                filetypes=[("图片", "*.png *.gif"), ("所有文件", "*.*")])
            if not path:
                return
            self.icon_path.set(path)
            self.icon_type.set("image")
            name = os.path.basename(path)
            self.img_label.config(text=name if len(name) <= 22 else name[:20] + "…")
            self._update()

        def _clear_image(self):
            self.icon_path.set("")
            self.img_label.config(text="")
            self._draw_preview()

        def _choose_color(self):
            _rgb, hexv = colorchooser.askcolor(color=self.color, title=T("选择分类颜色"))
            if hexv:
                self.color = hexv
                self.color_btn.configure(bg=hexv)
                self.color_hex.config(text=hexv)
                self._draw_preview()

        def _draw_preview(self):
            c = self.preview
            c.delete("all")
            size = self.AVATAR_SIZE
            self._preview_img = None
            if self.icon_type.get() == "image" and self.icon_path.get() \
                    and os.path.isfile(self.icon_path.get()):
                try:
                    img = tk.PhotoImage(file=self.icon_path.get())
                    w, h = img.width(), img.height()
                    factor = max(1, -(-max(w, h) // size))
                    if factor > 1:
                        img = img.subsample(factor, factor)
                    self._preview_img = img
                    c.create_image(size // 2, size // 2, image=img, anchor="center")
                    return
                except Exception:
                    pass
            text = self.icon_text.get().strip() or (self.name_var.get().strip() or "?")[:1]
            c.create_oval(0, 0, size, size, fill=self.color, outline="")
            c.create_text(size // 2, size // 2 + 1, text=text, fill="white",
                          font=(FONT, int(size * 0.42), BOLD))

        def _ok(self):
            name = self.name_var.get().strip()
            if not name:
                messagebox.showwarning("提示", T("请填写分类名称"), parent=self)
                return
            self.result = {
                "name": name,
                "icon": self.icon_text.get().strip(),
                "icon_type": self.icon_type.get(),
                "icon_path": self.icon_path.get().strip(),
                "color": self.color,
            }
            try:
                self.grab_release()
            except Exception:
                pass
            self.destroy()

        def _cancel(self):
            self.result = None
            try:
                self.grab_release()
            except Exception:
                pass
            self.destroy()


    # ==========================================================================
    #  分类 - 标签关联（超链接）对话框
    # ==========================================================================

# ★★ 2026-10-06：这个类已拆到单独的文件里
#   （AIxiede拆分开/程序分块/CategoryTagLinkDialog.py）。
#   这里保留一个「转发」：程序照常能用，但代码在那边维护。
#   ★ 兜底自带一份**原样代码** —— 就算新文件丢了/损坏了，
#     程序照样开得起来（用户最怕的就是「双击打不开」）。
try:
    from CategoryTagLinkDialog import CategoryTagLinkDialog, _set_app as _fk_CategoryTagLinkDialog
    _fk_CategoryTagLinkDialog(sys.modules[__name__])
except Exception:
    try:
        print("[提示] 拆出去的 CategoryTagLinkDialog.py 没找到，已退回内置简易版")
    except Exception:
        pass

    # ↓↓↓ 兜底用的原代码（新文件正常时不走这里）↓↓↓
    class CategoryTagLinkDialog(tk.Toplevel):
        def __init__(self, master, store, cid, cat_name):
            super().__init__(master)
            self.title(f"按标签关联 —— {cat_name}")
            self.geometry(_dlg_geom(420, 560))
            self.minsize(*_dlg_size(360, 420, minimum=(360, 420)))
            self.store = store
            self.cid = cid
            self.saved = False

            self.all_tags = store.all_tags()   # [(id, name, color, cnt), ...]
            linked = store.linked_tag_ids(cid)

            # 每个标签一个 BooleanVar，即使被过滤隐藏也不丢勾选状态
            self.tag_vars = {}
            for tid, name, color, cnt in self.all_tags:
                self.tag_vars[tid] = tk.BooleanVar(value=(tid in linked))

            body = ttk.Frame(self, padding=12)
            body.pack(fill="both", expand=True)

            ttk.Label(
                body,
                text=T("勾选标签，凡是含有该标签的文件都会出现在此分类里"),
                foreground=theme_get("fg_dim")).pack(anchor="w", pady=(0, 6))

            # ---------- 搜索行 ----------
            sbar = ttk.Frame(body)
            sbar.pack(fill="x", pady=(0, 6))
            make_search_label(sbar, "搜索标签：").pack(side="left")
            self.search_var = tk.StringVar()
            se = ttk.Entry(sbar, textvariable=self.search_var)
            se.pack(side="left", fill="x", expand=True, padx=(4, 4))
            self.search_var.trace_add("write", lambda *a: self._render_list())
            ttk.Button(sbar, text=T("清除"), width=6,
                       command=lambda: self.search_var.set("")
                       ).pack(side="left")

            self.search_info = ttk.Label(body, text="", foreground=theme_get("ok"))
            self.search_info.pack(anchor="w", pady=(0, 4))

            # ---------- 标签列表 ----------
            wrap = ttk.Frame(body)
            wrap.pack(fill="both", expand=True)

            self.canvas = tk.Canvas(wrap, highlightthickness=1,
                                    highlightbackground=theme_get("line"),
                                    bg=theme_get("card_bg"))
            sb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=sb.set)
            sb.pack(side="right", fill="y")
            self.canvas.pack(side="left", fill="both", expand=True)

            self.inner = tk.Frame(self.canvas, bg=theme_get("card_bg"))
            try:
                register_themed(self.inner, "card")   # ★ 常驻控件 → 换皮肤跟着刷
            except Exception:
                pass
            self._win_id = self.canvas.create_window(
                (0, 0), window=self.inner, anchor="nw")
            self.inner.bind(
                "<Configure>",
                lambda e: self.canvas.configure(
                    scrollregion=self.canvas.bbox("all")))
            self.canvas.bind(
                "<Configure>",
                lambda e: self.canvas.itemconfigure(self._win_id, width=e.width))

            self.canvas.bind("<MouseWheel>", self._wheel)
            self.canvas.bind("<Button-4>", self._wheel)
            self.canvas.bind("<Button-5>", self._wheel)
            # ★ v25：鼠标停在勾选框 / 标签文字上也能滚（不用去拖进度条）
            enable_wheel_scroll(self, self.canvas)

            # ---------- 底部按钮 ----------
            btns = ttk.Frame(body)
            btns.pack(fill="x", pady=(10, 0))
            ttk.Button(btns, text=T("保存关联"), command=self._save).pack(side="right")
            ttk.Button(btns, text=T("取消"), command=self._cancel).pack(
                side="right", padx=6)
            ttk.Button(btns, text=T("全选"), command=lambda: self._set_all(True)
                       ).pack(side="left")
            ttk.Button(btns, text=T("全不选"), command=lambda: self._set_all(False)
                       ).pack(side="left", padx=4)
            ttk.Button(btns, text=T("反选"), command=self._invert
                       ).pack(side="left", padx=4)

            self.bind("<Escape>", lambda e: self._cancel())
            self.protocol("WM_DELETE_WINDOW", self._cancel)

            self._render_list()

            self.update_idletasks()
            w, h = self.winfo_width(), self.winfo_height()
            x = master.winfo_rootx() + (master.winfo_width() - w) // 2
            y = master.winfo_rooty() + (master.winfo_height() - h) // 3
            self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
            self.transient(master)
            self.grab_set()
            self.wait_window(self)

        # ---------------- 列表渲染 ----------------
        def _render_list(self):
            for w in self.inner.winfo_children():
                w.destroy()

            q = (self.search_var.get() or "").strip().lower()
            shown = 0
            for tid, name, color, cnt in self.all_tags:
                if q and q not in (name or "").lower():
                    continue
                shown += 1
                row = tk.Frame(self.inner, bg=theme_get("card_bg"))
                row.pack(fill="x", padx=4, pady=1)
                var = self.tag_vars[tid]
                cb = tk.Checkbutton(
                    row, text="", variable=var,
                    bg=theme_get("card_bg"), activebackground=theme_get("hover_bg"),
                    selectcolor="white", borderwidth=0,
                    highlightthickness=0)
                cb.pack(side="left")
                lbl = tk.Label(row, text=f"{name}   ({cnt})",
                               bg=theme_get("card_bg"), fg=color or "#333",
                               anchor="w", font=(FONT, UI_FONT_SIZE))
                lbl.pack(side="left", fill="x", expand=True)

                def _toggle(_e, v=var):
                    v.set(not v.get())

                lbl.bind("<Button-1>", _toggle)
                row.bind("<Button-1>", _toggle)

            if shown == 0:
                tk.Label(self.inner, text=T("（没有匹配的标签）"),
                         bg=theme_get("card_bg"), fg=theme_get("fg_dim")).pack(pady=16)
                self.search_info.config(text="")
            elif q:
                self.search_info.config(text=f"显示 {shown} / {len(self.all_tags)}")
            else:
                n_on = sum(1 for v in self.tag_vars.values() if v.get())
                if n_on:
                    self.search_info.config(text=f"已选 {n_on} 个")
                else:
                    self.search_info.config(text="")

        def _wheel(self, event):
            if event.num == 4:
                d = -1
            elif event.num == 5:
                d = 1
            else:
                d = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(d, "units")

        # ---------------- 批量操作（作用于当前可见的标签） ----------------
        def _visible_tids(self):
            q = (self.search_var.get() or "").strip().lower()
            out = []
            for tid, name, color, cnt in self.all_tags:
                if q and q not in (name or "").lower():
                    continue
                out.append(tid)
            return out

        def _set_all(self, val):
            for tid in self._visible_tids():
                self.tag_vars[tid].set(val)
            self._render_list()

        def _invert(self):
            for tid in self._visible_tids():
                self.tag_vars[tid].set(not self.tag_vars[tid].get())
            self._render_list()

        # ---------------- 保存 / 取消 ----------------
        def _save(self):
            chosen = [tid for tid, v in self.tag_vars.items() if v.get()]
            # ★ v25 补丁4：原来这句没做保护 —— 万一写库出错（数据库被占用 /
            #   权限不足 / 磁盘满），异常会被 Tk 吞进控制台，用户看到的就是
            #   「点了保存没反应、窗口还在」。现在出错会弹窗说清楚。
            try:
                self.store.set_category_tag_links(self.cid, chosen)
            except Exception as _e:
                note_swallowed(T("保存「分类↔标签关联」失败"), _e)
                messagebox.showerror(
                    "保存失败",
                    f"没能保存这个分类的标签关联：\n{_e}\n\n"
                    "（可以先关掉程序再重开；如果一直失败，多半是数据库被其它"
                    "窗口占用或磁盘满了）",
                    parent=self)
                return
            self.saved = True
            try:
                self.grab_release()
            except Exception:
                pass
            self.destroy()

        def _cancel(self):
            try:
                self.grab_release()
            except Exception:
                pass
            self.destroy()


    # ==========================================================================
    #  分类 - 打开时自动屏蔽标签 对话框
    # ==========================================================================

# ★★ 2026-10-06：这个类已拆到单独的文件里
#   （AIxiede拆分开/程序分块/CategoryHiddenTagsDialog.py）。
#   这里保留一个「转发」：程序照常能用，但代码在那边维护。
#   ★ 兜底自带一份**原样代码** —— 就算新文件丢了/损坏了，
#     程序照样开得起来（用户最怕的就是「双击打不开」）。
try:
    from CategoryHiddenTagsDialog import CategoryHiddenTagsDialog, _set_app as _fk_CategoryHiddenTagsDialog
    _fk_CategoryHiddenTagsDialog(sys.modules[__name__])
except Exception:
    try:
        print("[提示] 拆出去的 CategoryHiddenTagsDialog.py 没找到，已退回内置简易版")
    except Exception:
        pass

    # ↓↓↓ 兜底用的原代码（新文件正常时不走这里）↓↓↓
    class CategoryHiddenTagsDialog(tk.Toplevel):
        """设置某个分类在打开时自动屏蔽哪些标签。"""

        def __init__(self, master, store, cid, cat_name):
            super().__init__(master)
            self.title(f"打开时自动屏蔽标签 —— {cat_name}")
            self.geometry(_dlg_geom(460, 600))
            self.minsize(*_dlg_size(400, 460, minimum=(400, 460)))
            self.store = store
            self.cid = cid
            self.saved = False

            self.all_tags = store.all_tags()      # [(id, name, color, cnt), ...]
            hidden = store.get_category_hidden_tags(cid)

            self.tag_vars = {}
            for tid, name, color, cnt in self.all_tags:
                self.tag_vars[tid] = tk.BooleanVar(value=(tid in hidden))

            body = ttk.Frame(self, padding=12)
            body.pack(fill="both", expand=True)

            ttk.Label(
                body,
                text=("勾选后，每次打开这个分类时，被勾选的标签会自动"
                      "在文件列表的标签条里屏蔽（划掉）。\n"
                      "（你仍然可以随时手动调整）"),
                foreground=theme_get("fg_dim"), justify="left",
                wraplength=420).pack(anchor="w", pady=(0, 6))

            # ---------- 搜索行 ----------
            sbar = ttk.Frame(body)
            sbar.pack(fill="x", pady=(0, 6))
            make_search_label(sbar, "搜索标签：").pack(side="left")
            self.search_var = tk.StringVar()
            se = ttk.Entry(sbar, textvariable=self.search_var)
            se.pack(side="left", fill="x", expand=True, padx=(4, 4))
            self.search_var.trace_add("write", lambda *a: self._render_list())
            ttk.Button(sbar, text=T("清除"), width=6,
                       command=lambda: self.search_var.set("")
                       ).pack(side="left")

            self.search_info = ttk.Label(body, text="", foreground=theme_get("ok"))
            self.search_info.pack(anchor="w", pady=(0, 4))

            # ---------- 标签列表 ----------
            wrap = ttk.Frame(body)
            wrap.pack(fill="both", expand=True)

            self.canvas = tk.Canvas(wrap, highlightthickness=1,
                                    highlightbackground=theme_get("line"),
                                    bg=theme_get("card_bg"))
            sb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=sb.set)
            sb.pack(side="right", fill="y")
            self.canvas.pack(side="left", fill="both", expand=True)

            self.inner = tk.Frame(self.canvas, bg=theme_get("card_bg"))
            try:
                register_themed(self.inner, "card")   # ★ 常驻控件 → 换皮肤跟着刷
            except Exception:
                pass
            self._win_id = self.canvas.create_window(
                (0, 0), window=self.inner, anchor="nw")
            self.inner.bind(
                "<Configure>",
                lambda e: self.canvas.configure(
                    scrollregion=self.canvas.bbox("all")))
            self.canvas.bind(
                "<Configure>",
                lambda e: self.canvas.itemconfigure(self._win_id, width=e.width))

            self.canvas.bind("<MouseWheel>", self._wheel)
            self.canvas.bind("<Button-4>", self._wheel)
            self.canvas.bind("<Button-5>", self._wheel)
            # ★ v25：鼠标停在勾选框 / 标签文字上也能滚（不用去拖进度条）
            enable_wheel_scroll(self, self.canvas)

            # ---------- 底部按钮 ----------
            btns = ttk.Frame(body)
            btns.pack(fill="x", pady=(10, 0))
            ttk.Button(btns, text=T("保存设置"),
                       command=self._save).pack(side="right")
            ttk.Button(btns, text=T("取消"),
                       command=self._cancel).pack(side="right", padx=6)
            ttk.Button(btns, text=T("全不选"),
                       command=lambda: self._set_all(False)).pack(side="left")
            ttk.Button(btns, text=T("全选"),
                       command=lambda: self._set_all(True)).pack(side="left",
                                                                 padx=4)

            self.bind("<Escape>", lambda e: self._cancel())
            self.protocol("WM_DELETE_WINDOW", self._cancel)

            self._render_list()

            self.update_idletasks()
            w, h = self.winfo_width(), self.winfo_height()
            x = master.winfo_rootx() + (master.winfo_width() - w) // 2
            y = master.winfo_rooty() + (master.winfo_height() - h) // 3
            self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
            self.transient(master)
            self.grab_set()
            self.wait_window(self)

        def _render_list(self):
            for w in self.inner.winfo_children():
                w.destroy()

            q = (self.search_var.get() or "").strip().lower()
            shown = 0
            for tid, name, color, cnt in self.all_tags:
                if q and q not in (name or "").lower():
                    continue
                shown += 1
                row = tk.Frame(self.inner, bg=theme_get("card_bg"))
                row.pack(fill="x", padx=4, pady=1)
                var = self.tag_vars[tid]
                cb = tk.Checkbutton(
                    row, text="", variable=var,
                    bg=theme_get("card_bg"), activebackground=theme_get("hover_bg"),
                    selectcolor="white", borderwidth=0,
                    highlightthickness=0)
                cb.pack(side="left")
                lbl = tk.Label(row, text=f"{name}   ({cnt})",
                               bg=theme_get("card_bg"), fg=color or "#333",
                               anchor="w", font=(FONT, UI_FONT_SIZE))
                lbl.pack(side="left", fill="x", expand=True)

                def _toggle(_e, v=var):
                    v.set(not v.get())

                lbl.bind("<Button-1>", _toggle)
                row.bind("<Button-1>", _toggle)

            if shown == 0:
                tk.Label(self.inner, text=T("（没有匹配的标签）"),
                         bg=theme_get("card_bg"), fg=theme_get("fg_dim")).pack(pady=16)
                self.search_info.config(text="")
            elif q:
                self.search_info.config(
                    text=f"显示 {shown} / {len(self.all_tags)}")
            else:
                n_on = sum(1 for v in self.tag_vars.values() if v.get())
                if n_on:
                    self.search_info.config(
                        text=f"已选 {n_on} 个（打开时将屏蔽）")
                else:
                    self.search_info.config(text=T("（没有勾选任何标签）"))

        def _wheel(self, event):
            if event.num == 4:
                d = -1
            elif event.num == 5:
                d = 1
            else:
                d = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(d, "units")

        def _set_all(self, val):
            q = (self.search_var.get() or "").strip().lower()
            for tid, name, color, cnt in self.all_tags:
                if q and q not in (name or "").lower():
                    continue
                self.tag_vars[tid].set(val)
            self._render_list()

        def _save(self):
            chosen = [tid for tid, v in self.tag_vars.items() if v.get()]
            # ★ v25 补丁4：这句原来没做保护，出错就被 Tk 吞掉 → 看着像「点了
            #   保存没反应」。现在会弹窗告诉你到底哪里失败了。
            try:
                self.store.set_category_hidden_tags(self.cid, chosen)
            except Exception as _e:
                note_swallowed(T("保存「打开时自动屏蔽的标签」失败"), _e)
                messagebox.showerror(
                    "保存失败",
                    f"没能保存这个分类要屏蔽的标签：\n{_e}\n\n"
                    "（可以先关掉程序再重开；如果一直失败，多半是数据库被其它"
                    "窗口占用）",
                    parent=self)
                return
            self.saved = True
            try:
                self.grab_release()
            except Exception:
                pass
            self.destroy()

        def _cancel(self):
            try:
                self.grab_release()
            except Exception:
                pass
            self.destroy()


    # ==========================================================================
    #  文件名自动标签规则 对话框
    # ==========================================================================

# ★★ 2026-10-06：这个类已拆到单独的文件里
#   （AIxiede拆分开/程序分块/AutoNameRulesDialog.py）。
#   这里保留一个「转发」：程序照常能用，但代码在那边维护。
#   ★ 兜底自带一份**原样代码** —— 就算新文件丢了/损坏了，
#     程序照样开得起来（用户最怕的就是「双击打不开」）。
try:
    from AutoNameRulesDialog import AutoNameRulesDialog, _set_app as _fk_AutoNameRulesDialog
    _fk_AutoNameRulesDialog(sys.modules[__name__])
except Exception:
    try:
        print("[提示] 拆出去的 AutoNameRulesDialog.py 没找到，已退回内置简易版")
    except Exception:
        pass

    # ↓↓↓ 兜底用的原代码（新文件正常时不走这里）↓↓↓
    class AutoNameRulesDialog(tk.Toplevel):
        """勾选一批标签：文件名里出现标签名，就自动给文件打上该标签。"""

        def __init__(self, master, store):
            super().__init__(master)
            self.title("文件名自动标签规则")
            self.geometry(_dlg_geom(500, 640))
            self.minsize(*_dlg_size(420, 480, minimum=(420, 480)))
            self.store = store
            self.saved = False

            self.all_tags = store.all_tags()      # [(id, name, color, cnt), ...]
            chosen = store.get_auto_name_rule_tag_ids()

            self.tag_vars = {}
            for tid, name, color, cnt in self.all_tags:
                self.tag_vars[tid] = tk.BooleanVar(value=(tid in chosen))

            body = ttk.Frame(self, padding=12)
            body.pack(fill="both", expand=True)

            ttk.Label(
                body,
                text=("勾选标签后，凡是文件名里出现该标签名的文件，"
                      "会自动被打上这个标签。\n"
                      "比如勾了「报表」，那么“2024销售报表.xlsx”就会自动"
                      "获得「报表」标签。\n"
                      "保存后不会立刻生效；请在「自动标签规则」窗口里，"
                      "点「▶▶ 应用文件名规则」按钮手动跑一次。"),
                foreground=theme_get("fg_dim"), justify="left",
                wraplength=460).pack(anchor="w", pady=(0, 6))

            # 搜索行
            sbar = ttk.Frame(body)
            sbar.pack(fill="x", pady=(0, 6))
            make_search_label(sbar, "搜索标签：").pack(side="left")
            self.search_var = tk.StringVar()
            se = ttk.Entry(sbar, textvariable=self.search_var)
            se.pack(side="left", fill="x", expand=True, padx=(4, 4))
            self.search_var.trace_add("write", lambda *a: self._render_list())
            ttk.Button(sbar, text=T("清除"), width=6,
                       command=lambda: self.search_var.set("")
                       ).pack(side="left")

            self.search_info = ttk.Label(body, text="", foreground=theme_get("ok"))
            self.search_info.pack(anchor="w", pady=(0, 4))

            # 列表
            wrap = ttk.Frame(body)
            wrap.pack(fill="both", expand=True)

            self.canvas = tk.Canvas(wrap, highlightthickness=1,
                                    highlightbackground=theme_get("line"),
                                    bg=theme_get("card_bg"))
            sb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=sb.set)
            sb.pack(side="right", fill="y")
            self.canvas.pack(side="left", fill="both", expand=True)

            self.inner = tk.Frame(self.canvas, bg=theme_get("card_bg"))
            try:
                register_themed(self.inner, "card")   # ★ 常驻控件 → 换皮肤跟着刷
            except Exception:
                pass
            self._win_id = self.canvas.create_window(
                (0, 0), window=self.inner, anchor="nw")
            self.inner.bind(
                "<Configure>",
                lambda e: self.canvas.configure(
                    scrollregion=self.canvas.bbox("all")))
            self.canvas.bind(
                "<Configure>",
                lambda e: self.canvas.itemconfigure(self._win_id, width=e.width))

            self.canvas.bind("<MouseWheel>", self._wheel)
            self.canvas.bind("<Button-4>", self._wheel)
            self.canvas.bind("<Button-5>", self._wheel)
            # ★ v25：鼠标停在勾选框 / 标签文字上也能滚（不用去拖进度条）
            enable_wheel_scroll(self, self.canvas)

            # 底部按钮
            btns = ttk.Frame(body)
            btns.pack(fill="x", pady=(10, 0))
            ttk.Button(btns, text=T("保存"),
                       command=self._save).pack(side="right")
            ttk.Button(btns, text=T("取消"),
                       command=self._cancel).pack(side="right", padx=6)
            ttk.Button(btns, text=T("全不选"),
                       command=lambda: self._set_all(False)).pack(side="left")
            ttk.Button(btns, text=T("全选"),
                       command=lambda: self._set_all(True)).pack(side="left",
                                                                 padx=4)

            self.bind("<Escape>", lambda e: self._cancel())
            self.protocol("WM_DELETE_WINDOW", self._cancel)

            self._render_list()

            self.update_idletasks()
            w, h = self.winfo_width(), self.winfo_height()
            x = master.winfo_rootx() + (master.winfo_width() - w) // 2
            y = master.winfo_rooty() + (master.winfo_height() - h) // 3
            self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
            self.transient(master)
            self.grab_set()
            self.wait_window(self)

        def _render_list(self):
            for w in self.inner.winfo_children():
                w.destroy()

            q = (self.search_var.get() or "").strip().lower()
            shown = 0
            for tid, name, color, cnt in self.all_tags:
                if q and q not in (name or "").lower():
                    continue
                shown += 1
                row = tk.Frame(self.inner, bg=theme_get("card_bg"))
                row.pack(fill="x", padx=4, pady=1)
                var = self.tag_vars[tid]
                cb = tk.Checkbutton(
                    row, text="", variable=var,
                    bg=theme_get("card_bg"), activebackground=theme_get("hover_bg"),
                    selectcolor="white", borderwidth=0,
                    highlightthickness=0)
                cb.pack(side="left")
                lbl = tk.Label(row, text=f"{name}   ({cnt})",
                               bg=theme_get("card_bg"), fg=color or "#333",
                               anchor="w", font=(FONT, UI_FONT_SIZE))
                lbl.pack(side="left", fill="x", expand=True)

                def _toggle(_e, v=var):
                    v.set(not v.get())

                lbl.bind("<Button-1>", _toggle)
                row.bind("<Button-1>", _toggle)

            if shown == 0:
                tk.Label(self.inner, text=T("（没有匹配的标签）"),
                         bg=theme_get("card_bg"), fg=theme_get("fg_dim")).pack(pady=16)
                self.search_info.config(text="")
            elif q:
                self.search_info.config(
                    text=f"显示 {shown} / {len(self.all_tags)}")
            else:
                n_on = sum(1 for v in self.tag_vars.values() if v.get())
                if n_on:
                    self.search_info.config(
                        text=f"已选 {n_on} 个标签参与文件名匹配")
                else:
                    self.search_info.config(text=T("（没有勾选任何标签）"))

        def _wheel(self, event):
            if event.num == 4:
                d = -1
            elif event.num == 5:
                d = 1
            else:
                d = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(d, "units")

        def _set_all(self, val):
            q = (self.search_var.get() or "").strip().lower()
            for tid, name, color, cnt in self.all_tags:
                if q and q not in (name or "").lower():
                    continue
                self.tag_vars[tid].set(val)
            self._render_list()

        def _save(self):
            chosen = [tid for tid, v in self.tag_vars.items() if v.get()]
            # ★ v25 补丁4：同上，写库失败要让用户看见，而不是「没反应」。
            try:
                self.store.set_auto_name_rule_tag_ids(chosen)
            except Exception as _e:
                note_swallowed(T("保存「文件名规则」勾选失败"), _e)
                messagebox.showerror(
                    "保存失败",
                    f"没能保存文件名规则的标签勾选：\n{_e}\n\n"
                    "（可以先关掉程序再重开；如果一直失败，多半是数据库被其它"
                    "窗口占用）",
                    parent=self)
                return
            self.saved = True
            try:
                self.grab_release()
            except Exception:
                pass
            self.destroy()

        def _cancel(self):
            try:
                self.grab_release()
            except Exception:
                pass
            self.destroy()


    # ==========================================================================
    #  ★ 星图编辑器（v21：层级自动布局 + 拖动跟手 + 曲线连线）
    # ==========================================================================
    # ==========================================================================
    #  ★ 星图编辑器（v22：多父级修复 + 最大化按钮）
    # ==========================================================================

# ★★★ StarGraphEditor 已拆到 `AIxiede拆分开/程序分块/StarGraphEditor.py`（2026-10-08）
#   ★★ 写法（错题本 #158）：① 直接 `from StarGraphEditor import …`（不带包路径）
#     ② `_set_app` 取别名 —— 模块名和类名同名时会跑到类上找
try:
    from StarGraphEditor import StarGraphEditor, _set_app as _fk_StarGraphEditor
    _fk_StarGraphEditor(sys.modules[__name__])
    _HAS_STARGRAPHEDITOR = True
except Exception as _e:
    _HAS_STARGRAPHEDITOR = False
    note_swallowed(T("拆出去的 StarGraphEditor.py 没找到，已退回内置简易版"), _e)

    class StarGraphEditor:  # ★ 兜底：没模块也不崩，只是没这个功能
        def __init__(self, *a, **k):
            pass

        def _build_ui(self, *a, **k):
            pass

        def _toggle_topmost(self, *a, **k):
            pass

        def _toggle_maximize(self, *a, **k):
            pass

        def _snapshot(self, *a, **k):
            pass

        def _push_undo(self, *a, **k):
            pass


# ★★★ HoverPreview 已拆到 `AIxiede拆分开/程序分块/HoverPreview.py`（2026-10-08）
#   ★★ 写法注意（错题本 #158）：
#     ① 直接 `from HoverPreview import …`（**不带包路径** ——
#        sys.path 里加的是「程序分块」目录）
#     ② `_set_app` **取别名**（`as _fk_HoverPreview`）——
#        模块名和类名同名时，`HoverPreview._set_app` 会跑到**类**上去找
try:
    from HoverPreview import HoverPreview, _set_app as _fk_HoverPreview
    _fk_HoverPreview(sys.modules[__name__])
    _HAS_HOVERPREVIEW = True
except Exception as _e:
    _HAS_HOVERPREVIEW = False
    note_swallowed(T("拆出去的 HoverPreview.py 没找到，已退回内置简易版"), _e)

    class HoverPreview:  # ★ 兜底：没模块也不崩，只是没这个功能
        def __init__(self, *a, **k):
            pass

        def on_motion(self, *a, **k):
            pass

        def on_leave(self, *a, **k):
            pass

        def toggle(self, *a, **k):
            pass

        def set_enabled(self, *a, **k):
            pass
# ★★★ TagThumbnail 已拆到 `AIxiede拆分开/程序分块/TagThumbnail.py`（2026-10-08）
#   ★★ 写法注意（错题本 #158）：
#     ① 直接 `from TagThumbnail import …`（**不带包路径** ——
#        sys.path 里加的是「程序分块」目录）
#     ② `_set_app` **取别名**（`as _fk_TagThumbnail`）——
#        模块名和类名同名时，`TagThumbnail._set_app` 会跑到**类**上去找
try:
    from TagThumbnail import TagThumbnail, _set_app as _fk_TagThumbnail
    _fk_TagThumbnail(sys.modules[__name__])
    _HAS_TAGTHUMBNAIL = True
except Exception as _e:
    _HAS_TAGTHUMBNAIL = False
    note_swallowed(T("拆出去的 TagThumbnail.py 没找到，已退回内置简易版"), _e)
    class TagThumbnail:  # ★ 兜底：没模块也不崩
        def __init__(self, *a, **k):
            pass

def _preview_cache_dir():
    """★★ v26 新增：返回「网盘预览的本地缓存目录」。

    用户反馈：「这个缓存目录在哪里，我可不可以自己设置」
      · 优先用设置文件里的 preview_cache_dir（用户自己设的）；
      · 没设 / 设了但建不出来 → 用系统临时目录下的 file_tagger_cache。

    ★★ 2026-10-06：配套新增了「缓存设置」（见菜单 界面 → 📥 网盘预览缓存…）：
        · preview_cache_dir      缓存放哪儿（用户自己挑；
                                 也可以选「每次启动用一个临时目录」= 无痕）
        · cache_incognito        无痕模式：阅后即焚（默认开）
        · cache_ttl_hours        多久没用就自动清（默认 24 小时；0=不清）
        · cache_max_mb           缓存目录超过多少 MB 自动清（默认 2048）
    """
    d = ""
    try:
        d = str(load_ui_setting("preview_cache_dir", "") or "").strip()
    except Exception:
        d = ""
    # ★★ 无痕模式（阅后即焚）：**每次启动换一个全新的临时目录**，
    #   关掉程序之后那个目录就成了孤儿，下次启动时顺手清掉。
    try:
        if bool(load_ui_setting("cache_incognito", True)):
            import tempfile as _tf
            sess = str(load_ui_setting("_cache_session_id", "") or "")
            if not sess:
                import uuid as _uuid
                sess = _uuid.uuid4().hex[:12]
                save_ui_setting("_cache_session_id", sess)
            base = d or os.path.join(_tf.gettempdir(), "file_tagger_cache")
            d2 = os.path.join(base, "本次_" + sess)
            try:
                os.makedirs(d2, exist_ok=True)
                return d2
            except Exception:
                pass
    except Exception:
        pass
    if d:
        try:
            os.makedirs(d, exist_ok=True)
            return d
        except Exception:
            pass
    import tempfile
    d = os.path.join(tempfile.gettempdir(), "file_tagger_cache")
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        pass
    return d


# ★★★ PreviewPane 已拆到 `AIxiede拆分开/程序分块/PreviewPane.py`（2026-10-08）
#   ★★ 写法（错题本 #158）：① 直接 `from PreviewPane import …`（不带包路径）
#     ② `_set_app` 取别名 —— 模块名和类名同名时会跑到类上找
try:
    from PreviewPane import PreviewPane, _set_app as _fk_PreviewPane
    _fk_PreviewPane(sys.modules[__name__])
    _HAS_PREVIEWPANE = True
except Exception as _e:
    _HAS_PREVIEWPANE = False
    note_swallowed(T("拆出去的 PreviewPane.py 没找到，已退回内置简易版"), _e)

    class PreviewPane:  # ★ 兜底：没模块也不崩，只是没这个功能
        def __init__(self, *a, **k):
            pass

        def _on_pane_configure(self, *a, **k):
            pass

        def _repaint_theme(self, *a, **k):
            pass

        def _hide_all_content(self, *a, **k):
            pass

        def _show_body(self, *a, **k):
            pass

        def _show_img(self, *a, **k):
            pass

        def _show_zoom_bar(self, *a, **k):
            pass

        def _zoom_label_update(self, *a, **k):
            pass


# ★★ 2026-10-06：这个类已拆到单独的文件里
#   （AIxiede拆分开/程序分块/CategoryItem.py）。
#   这里保留一个「转发」：程序照常能用，但代码在那边维护。
#   ★ 兜底自带一份**原样代码** —— 就算新文件丢了/损坏了，
#     程序照样开得起来（用户最怕的就是「双击打不开」）。
try:
    from CategoryItem import CategoryItem, _set_app as _fk_CategoryItem
    _fk_CategoryItem(sys.modules[__name__])
except Exception:
    try:
        print("[提示] 拆出去的 CategoryItem.py 没找到，已退回内置简易版")
    except Exception:
        pass

    # ↓↓↓ 兜底用的原代码（新文件正常时不走这里）↓↓↓
    class CategoryItem(tk.Frame):
        AVATAR = 36

        def __init__(self, master, cat, app, sidebar):
            super().__init__(master, bg=theme_get("win_bg"), cursor="hand2")
            self.cat = cat
            self.app = app
            self.sidebar = sidebar
            self._photo = None
            self._compact = False

            self.avatar = tk.Label(self, bg=cat.get("color") or "#5b8def",
                                   fg="white", font=(FONT, UI_FONT_SIZE, BOLD),
                                   width=2, height=1)
            self.avatar.pack(side="left", padx=(10, 8), pady=8)
            self._set_avatar()

            # ★★ v26：**分类名和数字之间要留间隔，名字太长要截断。**
            #   用户反馈：「图本边上的数字也显示不全」。
            #   原因：侧栏一共才 185 像素宽，而 name_lbl 是
            #   `fill="x", expand=True` —— 它**会吃满所有剩余空间**，
            #   于是名字和数字**贴在一起**，数字还被挤到最右边、
            #   有时候只露出半截。而且名字特别长的时候会把数字整个顶出去。
            #   改法：
            #     · 名字改成「最多显示 10 个字，多了用…」；
            #     · 名字右边留 8 像素间隔；
            #     · 数字右边留 10 像素。
            self.name_lbl = tk.Label(self, text=self._short_name(cat.get("name", "")),
                                     bg=theme_get("win_bg"),
                                     fg=theme_get("fg"), font=(FONT, UI_FONT_SIZE), anchor="w")
            self.name_lbl.pack(side="left", fill="x", expand=True, padx=(0, 8))

            cnt = cat.get("cnt") or 0
            self.count_lbl = tk.Label(self, text=str(cnt) if cnt else "",
                                      bg=theme_get("win_bg"), fg=theme_get("fg_dim"), font=(FONT, UI_FONT_SIZE))
            self.count_lbl.pack(side="right", padx=(0, 10))

            for w in (self, self.avatar, self.name_lbl, self.count_lbl):
                w.bind("<Button-1>", self._on_click)
                w.bind("<Button-3>", self._on_right)

        @staticmethod
        def _short_name(name, limit=10):
            """★ v26：分类名太长就截断（留个「…」）。

            侧栏只有 185 像素宽，名字太长会把右边的数字整个顶出去
            （用户反馈「图本边上的数字显示不全」）。这里统一压到 10 个字。
            """
            t = str(name or "")
            return t if len(t) <= limit else t[:limit - 1] + "…"

        def _set_avatar(self):
            cat = self.cat
            if cat.get("icon_type") == "image" and cat.get("icon_path"):
                path = cat["icon_path"]
                if os.path.isfile(path):
                    try:
                        img = tk.PhotoImage(file=path)
                        w, h = img.width(), img.height()
                        factor = max(1, -(-max(w, h) // self.AVATAR))
                        if factor > 1:
                            img = img.subsample(factor, factor)
                        self._photo = img
                        self.avatar.configure(image=img, text="", bg=theme_get("win_bg"),
                                              width=self.AVATAR, height=self.AVATAR)
                        return
                    except Exception:
                        pass
            icon = (cat.get("icon") or "").strip() or (cat.get("name") or "?")[:1]
            self.avatar.configure(image="", text=icon,
                                  bg=cat.get("color") or "#5b8def",
                                  fg="white", width=2, height=1)

        def set_compact(self, compact):
            if compact == self._compact:
                return
            self._compact = compact
            if compact:
                self.name_lbl.pack_forget()
                self.count_lbl.pack_forget()
                self.avatar.pack_configure(padx=0)
            else:
                self.avatar.pack_configure(padx=(10, 8))
                self.name_lbl.pack(side="left", fill="x", expand=True)
                self.count_lbl.pack(side="right", padx=(0, 10))

        def set_selected(self, selected):
            # ★★ 2026-10-06：跟着皮肤走。原来写死 theme_get("select_bg") / #f0f1f3 ——
            #   夜间模式下左边这一列还是浅蓝浅灰，是最扎眼的一块。
            bg = (theme_get("select_bg") if selected
                  else theme_get("win_bg"))
            self.configure(bg=bg)
            self.name_lbl.configure(bg=bg)
            self.count_lbl.configure(bg=bg)

        def _on_click(self, event=None):
            cid = self.cat.get("id")
            if cid is None:
                self.app.show_all_files()
            else:
                self.app.show_category(cid)

        def _on_right(self, event):
            cid = self.cat.get("id")
            if cid is None:
                m = tk.Menu(self, tearoff=0)
                m.add_command(label=T("刷新"), command=self.app.show_all_files)
                m.tk_popup(event.x_root, event.y_root)
            else:
                self.sidebar._category_menu(event, cid, self.cat.get("name", ""))



# ★★ 2026-10-06：这个类已拆到单独的文件里
#   （AIxiede拆分开/程序分块/CategorySidebar.py）。
#   这里保留一个「转发」：程序照常能用，但代码在那边维护。
#   ★ 兜底自带一份**原样代码** —— 就算新文件丢了/损坏了，
#     程序照样开得起来（用户最怕的就是「双击打不开」）。
try:
    from CategorySidebar import CategorySidebar, _set_app as _fk_CategorySidebar
    _fk_CategorySidebar(sys.modules[__name__])
except Exception:
    try:
        print("[提示] 拆出去的 CategorySidebar.py 没找到，已退回内置简易版")
    except Exception:
        pass

    # ↓↓↓ 兜底用的原代码（新文件正常时不走这里）↓↓↓
    class CategorySidebar(tk.Frame):
        def __init__(self, master, app):
            super().__init__(master, bg=theme_get("win_bg"))
            # ★★ 2026-10-07 **登记进"配色登记表"**（用户要求"留接口"）★★
            #   为什么必须登记：光在建的时候 `bg=theme_get(...)` **只对一次** ——
            #   换皮肤时它会被 `_retheme_tree()` 那套「按对照表翻色」接管，
            #   而那张表**分不清"这值是底还是字"** →
            #   实测：切到白天它还是 `#1e1f22`（该白却深）、
            #         切到夜间它变成 `#d6d7db`（★ 底色被当成字色翻了）。
            #   登记之后就**不走翻色表**，由 `apply_themed()` 按主题刷。
            try:
                register_themed(self, "win")
            except Exception:
                pass
            self.app = app
            self.items = []
            self.all_item = None
            self.selected = ("all", None)
            self._compact = False

            # ★★ 2026-01-26：左侧分类库改为上下分区
            #   上半部分：分类库（原有功能）
            #   下半部分：文件树（类似 Win 资源管理器左侧）
            self._vpaned = ttk.Panedwindow(self, orient="vertical")
            self._vpaned.pack(fill="both", expand=True)

            # --- 上半部分：分类库 ---
            self._top_frame = ttk.Frame(self._vpaned)
            self._vpaned.add(self._top_frame, weight=3)

            self.canvas = tk.Canvas(self._top_frame, bg=theme_get("win_bg"),
                                    highlightthickness=0)
            # ★ 2026-10-07 登记（否则换皮肤时被翻色表翻歪）
            try:
                register_themed(self.canvas, "win")
            except Exception:
                pass
            vsb = ttk.Scrollbar(self._top_frame, orient="vertical", command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=vsb.set)
            vsb.pack(side="right", fill="y")
            self.canvas.pack(side="left", fill="both", expand=True)

            self.inner = tk.Frame(self.canvas, bg=theme_get("win_bg"))
            # ★ 2026-10-07 登记
            try:
                register_themed(self.inner, "win")
            except Exception:
                pass
            self.canvas.create_window((0, 0), window=self.inner, anchor="nw",
                                      tags="inner")
            self.inner.bind("<Configure>", lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))
            self.canvas.bind("<Configure>", self._on_canvas_config)

            self.all_item = CategoryItem(
                self.inner,
                {"id": None, "name": T("全部文件"), "icon": "★", "icon_type": "text",
                 "color": "#5b8def", "cnt": ""},
                app, self)
            self.all_item.pack(fill="x")

            self.sep = tk.Frame(self.inner, height=1, bg=theme_get("line"))
            try:
                register_themed(self.sep, "line")   # ★ 常驻控件 → 换皮肤跟着刷
            except Exception:
                pass
            self.sep.pack(fill="x", pady=(6, 6))

            self.add_btn = tk.Label(self.inner, text=T("＋ 新建分类"),
                                    bg=theme_get("win_bg"), fg=theme_get("fg_dim"),
                                    font=(FONT, UI_FONT_SIZE), cursor="hand2",
                                    anchor="w", padx=12, pady=8)
            self.add_btn.pack(fill="x", pady=(4, 8))
            self.add_btn.bind("<Button-1>", lambda e: self.app.new_category())

            self.canvas.bind("<Button-3>", self._on_blank_right)

            # --- 下半部分：文件树 ---
            self._bottom_frame = ttk.Frame(self._vpaned)
            self._vpaned.add(self._bottom_frame, weight=2)

            # 文件树标题
            # ★ 2026-10-06：跟着皮肤走（原来是浅灰 theme_get("line")，夜里很扎眼）
            tree_header = tk.Frame(self._bottom_frame, bg=theme_get("panel_bg"))
            try:
                register_themed(tree_header, "panel")   # ★ 常驻控件 → 换皮肤跟着刷
            except Exception:
                pass
            tree_header.pack(fill="x")
            tk.Label(tree_header, text=T("📁 文件目录"),
                     bg=theme_get("panel_bg"), fg=theme_get("fg_dim"),
                     font=(FONT, UI_FONT_SIZE_SMALL, "bold"), anchor="w",
                     padx=8, pady=4).pack(side="left")

            # 文件树（ttk.Treeview）
            # ★★ 2026-10-03 修复 bug：原来 Treeview 的父控件被写成了 Scrollbar，
            #   导致 insert() 插入的节点全被 Scrollbar 吞掉，
            #   `_file_tree.get_children()` 永远返回 ()，文件树形同虚设。
            #   正确做法：Treeview 和 Scrollbar 是同一个 Frame 下的兄弟节点。
            tree_scroll = ttk.Scrollbar(self._bottom_frame)
            self._file_tree = ttk.Treeview(self._bottom_frame, yscrollcommand=tree_scroll.set,
                                            style="FileTree.Treeview")
            tree_scroll.config(command=self._file_tree.yview)
            tree_scroll.pack(side="right", fill="y")
            self._file_tree.pack(side="left", fill="both", expand=True)

            # 配置文件树样式
            style = ttk.Style()
            try:
                # ★★ 2026-10-07 修「目录树的字被上下压扁，只显示半截」（用户报）：
                #   原来 `rowheight=22` 写死了，装不下 13 号字（要 24 左右）。
                #   现在按字体算 —— 见 `_tree_row_height()` 的注释。
                #   ★ 这里和主题表那处用**同一个函数**，保证"换皮肤不会把行高改回去"。
                _tree_rowh = _tree_row_height()
                style.configure("FileTree.Treeview",
                                background=theme_get("card_bg"),
                                foreground=theme_get("fg"),
                                fieldbackground=theme_get("card_bg"),
                                rowheight=_tree_rowh,
                                font=(FONT, UI_FONT_SIZE_SMALL))
                style.configure("FileTree.Treeview.Item", font=(FONT, UI_FONT_SIZE_SMALL))
            except Exception:
                pass

            # ★★ 2026-10-04 修复：这一行原来绑的是 `self._on_tree_click`，
            #   可是**这个类里根本没有这个方法**（只写了 _on_tree_expand /
            #   _on_tree_double_click / _on_tree_right 三个）—— 于是程序
            #   **一启动就在建左侧栏时抛 AttributeError、直接退出**，
            #   表现就是「双击程序，窗口根本不出现」。
            #   这里改成绑到两个**确实存在**的方法上：
            #     · 单击 → `_on_tree_expand` 风格的「点一下就展开/收起」处理
            #       （用下面新加的 `_on_tree_click`，见 CategorySidebar 里那个小函数）；
            #     · 原来的展开回调照旧。
            self._file_tree.bind("<Button-1>", self._on_tree_click)
            self._file_tree.bind("<<TreeviewOpen>>", self._on_tree_expand)
            self._file_tree.bind("<Double-Button-1>", self._on_tree_double_click)
            # 右键菜单
            self._file_tree.bind("<Button-3>", self._on_tree_right)

            # 刷新按钮
            refresh_btn = tk.Label(tree_header, text="↻", bg=theme_get("line"), fg="#5b6d83",
                                 font=(FONT, UI_FONT_SIZE), cursor="hand2", padx=6)
            refresh_btn.pack(side="right")
            refresh_btn.bind("<Button-1>", lambda e: self.refresh_file_tree())

            # 当前路径
            self._current_tree_root = None
            self._tree_tag_ids = {}

        def _on_canvas_config(self, event):
            self.canvas.itemconfigure("inner", width=event.width)
            compact = event.width < 100
            if compact != self._compact:
                self._compact = compact
                for item in self.items:
                    item.set_compact(compact)
                if self.all_item:
                    self.all_item.set_compact(compact)
                self.add_btn.configure(text="＋" if compact else "＋ 新建分类")

        def _get_root_paths(self):
            """左侧文件目录树要从哪几个目录开始展开。

            ★★ 2026-10-04 重写（原来那个版本有两个毛病）：
              · 它读的是 `files` 表里的 `folder` 列 —— **这张表根本没有这一列**
                （`files` 只有 id / path / added_at），所以那句 SQL 永远抛异常、
                被 except 吞掉，永远走到「兜底：用户主目录」那一步。
              · 于是文件目录树**永远只显示你自己的主目录**，
                跟你当前在看的文件夹完全没关系
                （用户看到的「📁 文件目录 下面只有一个 home 之类的名字」就是这个）。

            现在的取法，按优先顺序：
              ① 你当前正在看的目录（最符合直觉）；
              ② 索引管理里登记的那些盘（E:\\ / D:\\ / I:\\ / 网盘挂载…）；
              ③ 索引根目录若为空 → 退回你「常用位置」里记录的那几个盘；
              ④ 实在都没有 → 用户主目录。
            """
            out = []

            def _add(p):
                try:
                    p = str(p)
                except Exception:
                    return
                if not p:
                    return
                p = p.rstrip("\\/") or p
                if not os.path.isdir(p):
                    return
                if p.lower() not in [x.lower() for x in out]:
                    out.append(p)

            # ① 当前正在看的目录
            try:
                cur = getattr(self.app, "current_dir", None)
                if cur and os.path.isdir(str(cur)):
                    _add(cur)
            except Exception:
                pass
            # ② 索引根目录（用户自己在「索引管理」里登记的那些盘）
            try:
                for r in self.app.store.all_index_roots():
                    _add(r["path"] if hasattr(r, "keys") else r[1])
            except Exception:
                pass
            # ③ 常用位置里记的盘
            if not out:
                try:
                    for pp in (getattr(self.app, "_places", {}) or {}).values():
                        if pp and str(pp).strip():
                            _add(pp)
                except Exception:
                    pass
            # ④ 兜底：用户主目录
            try:
                home = os.path.expanduser("~")
                if os.path.isdir(home):
                    _add(home)
            except Exception:
                pass

            # ★★ 2026-10-07 按用户要求排序（错题本 #62 / 待清单 #15）：
            #   用户原话：「本来应该 C、D、E、H、I、X、Y 这样按字母顺序排列」。
            #   原来 `out` 是"加进去的顺序" —— 先当前目录、再索引根目录，
            #   盘符顺序是这个盘碰巧被登记的顺序，**看着是乱的**。
            #
            #   排序规则（分两段，各自内部按名字排）：
            #     ① **盘符/挂载点**（C:\ D:\ E:\ \\CloudDrive\…）排前面，按字母
            #     ② **普通文件夹**（E:\桌面 这种）排后面，也按字母
            #   为什么盘符要排前面：盘符是"根"，用户找的是"我在哪个盘"，
            #   普通文件夹是"某个盘下面的"，放后面更合直觉。
            def _sort_key(p):
                try:
                    d = os.path.splitdrive(p)[0]          # 盘符，如 "E:"
                    is_drive_root = bool(d) and (
                        p.rstrip("\\/").lower() == d.lower())
                    # UNC（\\CloudDrive\X）也算"根"
                    is_unc_root = p.startswith("\\\\") and \
                        p.rstrip("\\").count("\\") <= 3
                    is_root = is_drive_root or is_unc_root
                except Exception:
                    is_root = False
                # (不是根排后面, 名字小写)
                return (0 if is_root else 1, str(p).lower())

            try:
                out.sort(key=_sort_key)
            except Exception:
                pass

            return out[:8]        # 别太多，左栏放不下

        def refresh_file_tree(self):
            """刷新文件树。

            ★★ 2026-10-07 按用户要求改了两处（错题本 #62 / 待清单 #15）：
              用户原话：「磁盘目录**默认隐藏**，只有跟文件列表当前路径有关的
              部分文件树被**适当展开**」。
              · **原来**：根节点（盘符）一律 `open=True` 默认展开 ——
                左边栏一打开就是一大堆展开的目录，找不着自己在哪。
              · **现在**：**全部收起**（只显示盘符那一排）；
                然后**只把"当前正在看的路径"那一条链展开**。
            """
            try:
                self._file_tree.delete(*self._file_tree.get_children())
                self._tree_tag_ids = {}
                # ★ 清掉"这条链展开过"的记账（每次刷新重算）
                self._tree_chain_nodes = set()
                roots = self._get_root_paths()
                for root in roots:
                    # ★★ 2026-10-03：根节点显示名用 basename（路径最后一段），
                    #   不然 `E:\桌面\MyPython\test_home2` 这种长路径直接显示在
                    #   树节点上，被左边栏宽度截成 `E:\桌面\MyPv...` 还不如不显示。
                    display = self._tree_root_display(root)
                    self._add_tree_node("", root, display)
                # ★★ 2026-10-07：全部收起之后，**只把当前路径那条链展开**
                #   （用户要的「只有跟文件列表当前路径有关的部分被适当展开」）。
                self._expand_current_chain(roots)
            except Exception as _e:
                note_swallowed(T("刷新文件树失败"), _e)

        def _tree_root_display(self, root):
            """根节点显示成什么。

            ★ 盘符要显示成 `C:` + 反斜杠 这样（用户就是按盘符找的），
              别显示成 basename（`C:` 那种）。
              普通文件夹才用 basename（路径最后一段）。
            """
            try:
                p = str(root)
                d = os.path.splitdrive(p)[0]
                if d and p.rstrip("\\/").lower() == d.lower():
                    return d + "\\"
                if p.startswith("\\\\"):
                    # UNC 挂载：显示最后一段（比如 \\CloudDrive\百度网盘 → 百度网盘）
                    seg = p.rstrip("\\").split("\\")
                    if len(seg) >= 2 and seg[-1]:
                        return seg[-1]
                base = os.path.basename(p.rstrip("\\/"))
                return base or p
            except Exception:
                return str(root)

        def _current_chain_parts(self, roots):
            """算出「当前正在看的目录」那一条链，好把它展开。

            返回 [(根路径, [路径1, 路径2, ...]), ...] ——
            路径1 是根下面第一级，依次到当前目录。
            ★ 只展开**确实存在于树里**的那些（树只建了两级，深了没有）。
            """
            try:
                cur = getattr(self.app, "current_dir", None)
                if not cur:
                    return []
                cur = os.path.abspath(str(cur))
            except Exception:
                return []
            out = []
            for root in roots:
                try:
                    r = os.path.abspath(str(root))
                    cl = cur.lower()
                    rl = r.lower()
                    # 当前目录得在这个根**里面**（或者就是它）
                    if cl == rl:
                        out.append((root, []))
                        continue
                    if not cl.startswith(rl.rstrip("\\") + "\\"):
                        continue
                    # 从根往下逐级切
                    rest = cur[len(r.rstrip("\\")):].strip("\\")
                    chain = []
                    acc = r
                    for seg in [x for x in rest.split("\\") if x]:
                        acc = os.path.join(acc, seg)
                        chain.append(acc)
                    out.append((root, chain))
                except Exception:
                    continue
            return out

        def _expand_current_chain(self, roots):
            """★ 把「当前路径」那一条链展开（其余保持收起）。

            为什么要单独做：Tk 的 Treeview **不会**给"程序里已经是展开状态"的
            节点补发事件，插完必须自己 `item(..., open=True)` 才真显示开。
            """
            try:
                wanted = set()
                for _root, chain in self._current_chain_parts(roots):
                    for p in chain:
                        wanted.add(p.lower())
                if not wanted:
                    return
                for p, iid in list(getattr(self, "_tree_tag_ids", {}).items()):
                    try:
                        if str(p).lower() in wanted:
                            self._file_tree.item(iid, open=True)
                    except Exception:
                        continue
            except Exception as _e:
                try:
                    note_swallowed(T("展开当前路径失败"), _e, quiet=True)
                except Exception:
                    pass

        def _add_tree_node(self, parent, path, display_name, depth=0,
                           auto_open=None):
            """添加树节点。

            ★★ 2026-10-07 改了「默认开不开」（错题本 #62）：
              以前 `depth==0`（盘符）一律默认展开 —— 一打开左栏就是一大堆
              展开的目录。现在**默认全部收起**，只有"当前路径那条链"会被展开
              （展开动作在 `_expand_current_chain` 里统一做）。
            ★ auto_open 参数留着，临时想强制展开某个节点时用。
            """
            try:
                if not os.path.isdir(path):
                    return
                # 获取子目录
                children = []
                try:
                    for name in os.listdir(path):
                        child_path = os.path.join(path, name)
                        if os.path.isdir(child_path):
                            children.append((name, child_path))
                except PermissionError:
                    return
                except Exception:
                    return

                children.sort(key=lambda x: x[0].lower())

                # ★ 默认收起（原来是 open=(depth == 0)）
                _open = False if auto_open is None else bool(auto_open)
                node_id = self._file_tree.insert(parent, "end", text=display_name,
                                                values=[path], open=_open)
                self._tree_tag_ids[path] = node_id

                # 如果没有子目录就直接返回
                if not children:
                    return

                if depth == 0:
                    # 第一级：直接添加子节点（不递归深层）
                    for name, child_path in children:
                        self._add_tree_node(node_id, child_path, name, depth=1)
                else:
                    # 第二级及以后：插入空占位符，下次点击 > 时懒加载
                    self._file_tree.insert(node_id, "end", text="", values=[""])
            except Exception:
                pass

        def _on_tree_click(self, event):
            """★★ 2026-10-04 新增（补上缺的那个方法）。
            ★★ 2026-10-07 改交互（用户选的"方案 A"，错题本见 #73）：

            **以前的规矩**：单击 = 展开/收起，双击 = 跳转。
            **用户报的问题**：原话「**点击**文件目录路径文件列表**跳转**到对应目录的
            功能没了」—— 用户说的是"**点击**"，而程序要的是"**双击**"，
            于是用户按习惯点一下，只看到展开，**以为跳转坏了**。

            **现在的规矩（跟外面的资源管理器 / VS Code 一致）**：
              · 点**小三角**（前面的箭头）→ **展开 / 收起**
              · 点**名字那一块**          → **跳转**（文件列表跟着变）

            **怎么区分**：`identify_element(x, y)` 会说这块是什么元件 ——
              实测（1130 行探出来的）：
                x ≤ 18  → `Treeitem.indicator`（小三角）
                x ≥ 24  → `text`（名字）
              所以判 `"indicator" in element` 就够。
            ★ 双击照样跳（保留着，`<Double-Button-1>` 还绑着），
              这样"习惯双击的人"也不受影响。
            """
            try:
                item = self._file_tree.identify_row(event.y)
                if not item:
                    return
                vals = self._file_tree.item(item, "values") or []
                path = vals[0] if vals else None
                if not path:
                    return
                if not os.path.isdir(path):
                    return

                # ★ 判断点的是"小三角"还是"名字"。
                #
                # ★★ 这里有个坑，写清楚：小三角的**横向位置会随缩进往右挪** ——
                #   实测（同一棵树）：
                #     根节点  （缩进 0）：x 6~18  是 indicator，x≥21 是 text
                #     第一级  （缩进 1）：x 24~39 是 indicator，x≥42 是 text
                #   所以**不能用"离行左边多少像素"去猜**，
                #   要用 `identify_element` —— 它自己会算缩进。
                #
                #   而且 indicator 左边还有一段 `padding`（空档），
                #   点在空档上 element 会是空字符串 —— 那种也该算"小三角那边"。
                #   所以判据是：**不是 "text" 就当它点的是左边那块**。
                try:
                    el = str(self._file_tree.identify_element(event.x,
                                                              event.y) or "")
                except Exception:
                    el = ""
                clicked_indicator = ("text" not in el)

                if clicked_indicator:
                    # ① 点小三角 → 只展开/收起，**不跳转**
                    opened = bool(self._file_tree.item(item, "open"))
                    self._file_tree.item(item, open=not opened)
                    if not opened:
                        self._file_tree.focus(item)
                        self._file_tree.selection_set(item)
                        # 有些 Tk 版本不会为"程序化展开"发 <<TreeviewOpen>>，
                        # 那样子目录永远出不来 —— 所以直接叫一次懒加载
                        try:
                            self._on_tree_expand(None)
                        except Exception:
                            pass
                    return

                # ② 点名字 → **跳转**（这就是用户要的"点击跳转"）
                self._file_tree.focus(item)
                self._file_tree.selection_set(item)
                try:
                    self.app.navigate_to_path(path)
                except Exception as _e:
                    note_swallowed(T("从文件目录树跳转失败"), _e)
            except Exception as _e:
                try:
                    note_swallowed(T("文件树：点了一下没处理成"), _e)
                except Exception:
                    pass

        def _on_tree_expand(self, event):
            """树节点展开事件：占位符节点自动懒加载子目录。"""
            # <<TreeviewOpen>> 在节点展开后触发；用 focus() 获取刚展开的节点
            try:
                item = self._file_tree.focus()
                if not item:
                    return
            except Exception:
                return
            children = self._file_tree.get_children(item)
            if not children:
                return
            first_child = children[0]
            if self._file_tree.item(first_child, "text") != "":
                # 已有真实子节点，不需要懒加载
                return
            # 占位符节点：懒加载
            values = self._file_tree.item(item, "values")
            if not values:
                return
            path = values[0]
            if not path:
                return
            self._expand_tree_node(item, path)

        def _expand_tree_node(self, node_id, path):
            """展开树节点（懒加载子目录）。

            ★★ 2026-10-07 改成**后台读目录**（错题本 #14 / #16 同一个病根）：

            **原来的毛病**：这里 `os.listdir(path)` 是**在主线程**跑的。
            本地盘快，无所谓；但**网盘挂载上列一次目录可能要好几秒** ——
            点一下网盘上的目录，**整个界面就僵在那儿**
            （用户报的「刷新也不及时**还卡**」就是这个）。

            **改法**（照抄程序里 PDF 渲染那套现成做法）：
              ① 主线程先删占位符、显示"正在读…"；
              ② 把 `os.listdir` 丢给**后台线程**；
              ③ 读完用 `_bg_post` 把结果寄回主线程（**后台绝不碰 Tcl**）；
              ④ 主线程收到再往树里插节点。

            ★ 三条老规矩必须守：
              · 后台线程**只做 os.listdir、纯数据**，一个 Tcl 都不碰
              · 回主线程走 `_bg_post`（信箱），**不调 after**
              · 回来时**再确认一次节点还在**（用户可能已经把它收了/刷新了）
            """
            # 先删空占位符（这步在主线程，很快）
            try:
                children = self._file_tree.get_children(node_id)
                for child in children:
                    if self._file_tree.item(child, "text") == "":
                        self._file_tree.delete(child)
                        break
            except Exception:
                return

            # ★ 网上的（网盘）路径走后台；本地路径直接读（本地快，不值得绕一圈）
            _remote = False
            try:
                _remote = bool(is_remote_path(path))
            except Exception:
                _remote = False

            if not _remote:
                # ---- 本地：照旧同步读（快） ----
                try:
                    dirs = []
                    for name in os.listdir(path):
                        child_path = os.path.join(path, name)
                        if os.path.isdir(child_path):
                            dirs.append((name, child_path))
                    dirs.sort(key=lambda x: x[0].lower())
                    for name, child_path in dirs:
                        self._add_tree_node(node_id, child_path, name, depth=1)
                except Exception:
                    pass
                return

            # ---- 网盘：后台读，读完回主线程 ----
            # ① 先放一个"正在读…"的临时节点，让用户知道点上了
            _waiting = None
            try:
                _waiting = self._file_tree.insert(
                    node_id, "end", text=T("（正在读取…）"), values=[""])
            except Exception:
                pass

            def _worker(_node=node_id, _path=path, _wait=_waiting):
                """后台线程：只读目录，绝不碰界面。"""
                got = []
                try:
                    for name in os.listdir(_path):
                        cp = os.path.join(_path, name)
                        try:
                            if os.path.isdir(cp):
                                got.append((name, cp))
                        except Exception:
                            continue
                except Exception:
                    got = None            # None = 读失败
                got = sorted(got, key=lambda x: x[0].lower()) if got else (got or [])

                def _apply():
                    """主线程：把读到的插进树里。"""
                    # ② 先清掉"正在读…"那个临时节点
                    try:
                        if _wait and self._file_tree.exists(_wait):
                            self._file_tree.delete(_wait)
                    except Exception:
                        pass
                    # ③ 确认这个节点还在（用户可能已经刷新/收起了）
                    try:
                        if not self._file_tree.exists(_node):
                            return
                    except Exception:
                        return
                    if got is None:
                        try:
                            self._file_tree.insert(_node, "end",
                                                   text=T("（读不出来）"),
                                                   values=[""])
                        except Exception:
                            pass
                        return
                    for _name, _cp in got:
                        self._add_tree_node(_node, _cp, _name, depth=1)

                _bg_post(_apply)

            try:
                threading.Thread(target=_worker, daemon=True,
                                 name="tree-expand").start()
            except Exception:
                # 线程都起不来 → 退回同步读（宁可卡一下，也别什么都不显示）
                try:
                    dirs = []
                    for name in os.listdir(path):
                        cp = os.path.join(path, name)
                        if os.path.isdir(cp):
                            dirs.append((name, cp))
                    dirs.sort(key=lambda x: x[0].lower())
                    try:
                        if _waiting and self._file_tree.exists(_waiting):
                            self._file_tree.delete(_waiting)
                    except Exception:
                        pass
                    for name, cp in dirs:
                        self._add_tree_node(node_id, cp, name, depth=1)
                except Exception:
                    pass
                return

            # ★★ 再加一条腿：**主线程每 150 毫秒自己取一次件**，
            #   免得结果回来了却没人取（一直停在"（正在读取…）"）。
            #   ★ 为什么需要这条：`_drain_ui_mail` 平时靠 `_ui_poll` 那个
            #     60 毫秒定时器顺带跑；万一那个定时器因为别的原因没转，
            #     树就会永远停在"正在读取…"。
            #     多一条腿 = "只要有人在等结果，就一定有人去取快递"。
            #   ★ 最多催 60 次（约 9 秒），到点就停 —— 不会一直转下去。
            def _poll_for_result(_node=node_id, _tries=0):
                try:
                    if APP_CLOSING or getattr(self.app, "_closing", False):
                        return
                    _drain_ui_mail(40)
                    # 子节点里还有"正在读取…"就继续等
                    still = False
                    try:
                        for c in self._file_tree.get_children(_node):
                            if "正在读取" in str(self._file_tree.item(c, "text")):
                                still = True
                                break
                    except Exception:
                        return
                    if still and _tries < 60:
                        self._file_tree.after(
                            150, lambda: _poll_for_result(_node, _tries + 1))
                except Exception:
                    pass

            try:
                self._file_tree.after(150, _poll_for_result)
            except Exception:
                pass

        def _on_tree_double_click(self, event):
            """双击树节点 → 跳转到该目录"""
            item = self._file_tree.identify_row(event.y)
            if not item:
                return
            path = self._file_tree.item(item, "values")[0] if self._file_tree.item(item, "values") else None
            if path and os.path.isdir(path):
                try:
                    self.app.navigate_to_path(path)
                except Exception:
                    pass

        def _on_tree_right(self, event):
            """文件树右键菜单"""
            item = self._file_tree.identify_row(event.y)
            if not item:
                return
            self._file_tree.selection_set(item)
            path = self._file_tree.item(item, "values")[0] if self._file_tree.item(item, "values") else None
            m = tk.Menu(self, tearoff=0)
            if path and os.path.isdir(path):
                m.add_command(label=T("在此目录中搜索"), command=lambda: self.app.navigate_to_path(path))
            m.add_command(label=T("刷新"), command=self.refresh_file_tree)
            m.tk_popup(event.x_root, event.y_root)

        def set_file_tree_path(self, path):
            """外部调用：设置文件树要显示的根路径"""
            self._cur_tree_root = path
            self.refresh_file_tree()

        def set_categories(self, cats):
            for item in self.items:
                item.destroy()
            self.items = []
            for cat in cats:
                item = CategoryItem(self.inner, cat, self.app, self)
                item.pack(fill="x", before=self.add_btn)
                if self._compact:
                    item.set_compact(True)
                self.items.append(item)
            self._refresh_selection()

        def set_selected(self, kind, cid=None):
            self.selected = (kind, cid)
            self._refresh_selection()

        def _refresh_selection(self):
            if self.all_item:
                self.all_item.set_selected(self.selected == ("all", None))
            for item in self.items:
                item.set_selected(self.selected == ("cat", item.cat.get("id")))

        def _on_blank_right(self, event):
            m = tk.Menu(self, tearoff=0)
            m.add_command(label=T("新建分类"), command=self.app.new_category)
            m.add_separator()
            m.add_command(label=T("刷新分类库"), command=self.app.refresh_categories)
            m.tk_popup(event.x_root, event.y_root)

        def _category_menu(self, event, cid, name):
            m = tk.Menu(self, tearoff=0)
            m.add_command(label=T("打开"), command=lambda: self.app.show_category(cid))
            m.add_separator()
            m.add_command(label=T("按标签关联（超链接）…"),
                          command=lambda: self.app.link_category_tags(cid, name))
            m.add_command(label=T("查看已关联的标签…"),
                          command=lambda: self.app.show_category_tag_links(cid, name))
            m.add_command(label=T("设置打开时自动屏蔽的标签…"),
                          command=lambda: self.app.edit_category_hidden_tags(cid, name))
            m.add_separator()
            m.add_command(label=T("编辑名称 / 头像 / 颜色…"),
                          command=lambda: self.app.edit_category(cid, "all"))
            m.add_command(label=T("重命名…"),
                          command=lambda: self.app.edit_category(cid, "name"))
            m.add_command(label=T("更换颜色…"),
                          command=lambda: self.app.edit_category(cid, "color"))
            m.add_separator()
            m.add_command(label=T("清空本分类的直接成员（保留超链接）"),
                          command=lambda: self.app.clear_category_direct(cid, name))
            m.add_command(label=T("删除分类"),
                          command=lambda: self.app.delete_category(cid, name))
            m.tk_popup(event.x_root, event.y_root)

    # ==========================================================================
    #  ★ v23：作用范围写法检查（防止「范围写错 → 标签被清掉」）
    # ==========================================================================

def _scope_lines(scope_path):
    return [l.strip() for l in str(scope_path or "").split("\n") if l.strip()]


def check_scope_for_edit(parent, store, scope_path, action="保存"):
    """检查「作用范围」写法是否和本地索引 / 已记录文件对得上。

    典型坑：范围填了 X:\\，但程序里记录的是
    \\\\CloudDrive-X-…\\CloudDrive\\…（CloudDrive2 的 UNC 写法）。
    这样扫描不但打不上标签，还会把范围内的自动标签清掉。

    返回 (proceed: bool, new_scope_path: str)
    """
    lines = _scope_lines(scope_path)
    if not lines:
        return True, scope_path
    bad = []
    for s in lines:
        try:
            if store.scope_known_file_count(s) == 0:
                bad.append(s)
        except Exception:
            bad.append(s)
    if not bad:
        return True, scope_path

    fixed = list(lines)
    for token in bad[:2]:
        try:
            sugg = store.suggest_scopes_for(token)
        except Exception:
            sugg = []
        tip = ("\n".join("      " + x for x in sugg[:5])
               or "      （没有可用的索引根，可到「界面 → 📚 索引管理…」建索引）")
        ans = messagebox.askyesnocancel(
            "作用范围可能写错了",
            f"「{token}」下面找不到任何已记录 / 已索引的文件。\n\n"
            f"常见原因：路径写法和索引不一致 —— 比如网盘写成了 X:\\，\n"
            f"而程序里记录的是 UNC 写法（\\\\服务器\\共享\\…）。\n\n"
            f"猜你可能想用：\n{tip}\n\n"
            f"『是』  = 用第一条建议替换\n"
            f"『否』  = 保持原样（范围内原有的自动标签会被清掉）\n"
            f"『取消』= 先不{action}",
            parent=parent)
        if ans is None:
            return False, "\n".join(lines)
        if ans and sugg:
            fixed = [sugg[0] if x == token else x for x in fixed]
    return True, "\n".join(fixed)


def confirm_scopes_for_scan(parent, store, scopes, action="扫描"):
    """扫描前拦一道：范围里一个文件都没有时先问清楚。返回 True = 继续。"""
    bad = []
    for s in scopes:
        if not s:
            continue
        try:
            if store.scope_known_file_count(s) == 0:
                bad.append(s)
        except Exception:
            pass
    if not bad:
        return True
    tip = []
    for token in bad[:5]:
        try:
            sugg = store.suggest_scopes_for(token)
        except Exception:
            sugg = []
        tip.append(f"   · {token}" + (f"   → 也许想用：{sugg[0]}" if sugg else ""))
    return messagebox.askyesno(
        "作用范围可能写错了",
        "下面这些范围里找不到任何已记录 / 已索引的文件：\n"
        + "\n".join(tip) + "\n\n"
        "常见原因：路径写法和索引不一致 —— 比如填了 X:\\，而库里记的\n"
        "是 \\\\服务器\\共享\\… 这种 UNC 写法。\n\n"
        "范围写错时，扫描不但打不上标签，还会把范围内原有的自动标签\n"
        "清掉（这就是「标签突然不见了」的常见原因）。\n\n"
        f"仍然继续{action}吗？",
        parent=parent)


# ★★ 2026-10-06：这个类已拆到单独的文件里
#   （AIxiede拆分开/程序分块/ScanProgressDialog.py）。
#   这里保留一个「转发」：程序照常能用，但代码在那边维护。
#   ★ 兜底自带一份**原样代码** —— 就算新文件丢了/损坏了，
#     程序照样开得起来（用户最怕的就是「双击打不开」）。
try:
    from ScanProgressDialog import ScanProgressDialog, _set_app as _fk_ScanProgressDialog
    _fk_ScanProgressDialog(sys.modules[__name__])
except Exception:
    try:
        print("[提示] 拆出去的 ScanProgressDialog.py 没找到，已退回内置简易版")
    except Exception:
        pass

    # ↓↓↓ 兜底用的原代码（新文件正常时不走这里）↓↓↓
    class ScanProgressDialog(tk.Toplevel):
        """扫描进度的独立窗口，可以最小化，主界面不会被锁住。"""
        def __init__(self, master, store, scopes, on_finish=None):
            super().__init__(master)
            self.on_finish = on_finish
            self.title("正在扫描")
            self.geometry(_dlg_geom(560, 230))
            self.minsize(*_dlg_size(480, 210, minimum=(480, 210)))
            self.store = store
            self.scopes = [s.strip() for s in (scopes or []) if s.strip()]
            self.result = None    # (total_files, changed_files)

            self._cancel_flag = False
            self._finished = False
            self._queue = queue.Queue()
            self._walk_done = False
            self._all_paths = []
            self._total = 0
            self._processed = 0

            body = ttk.Frame(self, padding=14)
            body.pack(fill="both", expand=True)

            self.stage_lbl = ttk.Label(body, text=T("正在枚举文件…"),
                                       font=(FONT, UI_FONT_SIZE, BOLD))
            self.stage_lbl.pack(anchor="w", pady=(0, 4))

            self.detail_lbl = ttk.Label(body, text="", foreground=theme_get("fg_dim"),
                                        wraplength=520, justify="left")
            self.detail_lbl.pack(anchor="w", pady=(0, 8))

            self.pb = ttk.Progressbar(body, mode="indeterminate", length=520)
            self.pb.pack(fill="x", pady=(0, 6))
            self.pb.start(12)

            self.count_lbl = ttk.Label(body, text="", foreground=theme_get("fg_dim"))
            self.count_lbl.pack(anchor="w", pady=(0, 8))

            btn_row = ttk.Frame(body)
            btn_row.pack(fill="x")
            self.cancel_btn = ttk.Button(btn_row, text=T("取消"),
                                         command=self._on_cancel)
            self.cancel_btn.pack(side="right")
            ttk.Button(btn_row, text=T("最小化"),
                       command=self._minimize).pack(side="right", padx=6)

            self.protocol("WM_DELETE_WINDOW", self._on_cancel)

            self.update_idletasks()
            w, h = self.winfo_width(), self.winfo_height()
            x = master.winfo_rootx() + (master.winfo_width() - w) // 2
            y = master.winfo_rooty() + (master.winfo_height() - h) // 3
            self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
            self.transient(master)

            # 启动工作线程（★ v23：枚举走索引、打标签也在后台线程里做）
            self._worker = threading.Thread(
                target=self._work_worker, daemon=True)
            self._worker.start()
            self.after(60, self._poll)

            # ★ 不阻塞主界面：不再 wait_window

        # ---------------- 工作线程：先枚举（索引优先），再打标签 ----------------
        def _work_worker(self):
            try:
                all_paths = []
                n_index = 0
                n_live = 0
                for scope in self.scopes:
                    if self._cancel_flag:
                        break
                    found = []
                    try:
                        found = list(self.store.files_under_scope(scope)
                                     .get("paths") or [])
                    except Exception as exc:
                        self._queue.put(("info", f"读本地索引失败：{exc}"))
                        found = []
                    if found:
                        n_index += len(found)
                        self._queue.put(
                            ("info", f"索引命中：{scope} → {len(found)} 个文件"))
                    else:
                        self._queue.put(
                            ("info", f"索引里没有 {scope}，改为实时遍历磁盘"
                                     f"（网盘会很慢）…"))
                        found = self._walk_live(scope)
                        n_live += len(found)
                        self._queue.put(
                            ("info", f"实时遍历完成：{scope} → {len(found)} 个文件"))
                    all_paths.extend(found)
                    self._queue.put(("found", (len(all_paths), str(scope))))
                if self._cancel_flag:
                    self._queue.put(("cancelled", None))
                    return
                self._total = len(all_paths)
                self._all_paths = all_paths
                self._queue.put(("tag_start", (self._total, n_index, n_live)))
                self._tag_all()
            except Exception as exc:
                self._queue.put(("error", str(exc)))

        def _walk_live(self, scope):
            """索引/记录里都没有时才用的兜底：实时遍历磁盘（网盘很慢）"""
            out = []
            try:
                if not os.path.isdir(scope):
                    return out
                for root, _dirs, files in os.walk(scope):
                    if self._cancel_flag:
                        break
                    for fn in files:
                        out.append(os.path.join(root, fn))
                        if len(out) % 500 == 0:
                            self._queue.put(("found", (len(out), root)))
            except Exception as exc:
                self._queue.put(("info", f"遍历失败：{scope} - {exc}"))
            return out

        def _tag_all(self):
            """在后台线程里分批打标签（数据库操作完全不占主线程）"""
            total = len(self._all_paths or [])
            step = 200
            changed_all = 0
            for i in range(0, total, step):
                if self._cancel_flag:
                    self._queue.put(("cancelled", None))
                    return
                chunk = self._all_paths[i:i + step]
                try:
                    with self.store.bulk():
                        changed_all += self.store.sync_auto_tags_for_paths(chunk)
                except Exception as exc:
                    self._queue.put(("info", f"第 {i + 1} 个起的批次失败：{exc}"))
                try:
                    cur = os.path.basename(chunk[-1]) if chunk else ""
                except Exception:
                    cur = ""
                self._queue.put(("tag_progress",
                                 (min(i + step, total), total, cur, changed_all)))
            self._queue.put(("tag_done", (total, changed_all)))

        # ---------------- 主线程：轮询消息 ----------------
        def _poll(self):
            try:
                while True:
                    kind, payload = self._queue.get_nowait()
                    self._handle(kind, payload)
                    if self._finished:
                        return
            except queue.Empty:
                pass
            if not self._finished:
                self.after(60, self._poll)

        def _handle(self, kind, payload):
            if kind == "info":
                try:
                    self.detail_lbl.config(text=str(payload)[:170])
                except Exception:
                    pass
                try:
                    app = self.master
                    if hasattr(app, "log_output"):
                        app.log_output(str(payload))
                except Exception:
                    pass
            elif kind == "found":
                n, scope = payload
                self.count_lbl.config(
                    text=f"已找到 {n} 个文件…  {str(scope)[:60]}")
            elif kind == "tag_start":
                total, n_index, n_live = payload
                try:
                    self.pb.stop()
                except Exception:
                    pass
                if total == 0:
                    self._finish(0, 0)
                    return
                self.pb.config(mode="determinate",
                               maximum=max(1, total), value=0)
                self.stage_lbl.config(text=T("正在打标签…"))
                self.detail_lbl.config(
                    text=f"索引 {n_index} 个 / 实时遍历 {n_live} 个    "
                         + "，".join(self.scopes)[:120])
                self.count_lbl.config(text=f"0 / {total}")
                try:
                    app = self.master
                    if hasattr(app, "log_output"):
                        app.log_output(
                            f"扫描打标签：共 {total} 个文件"
                            f"（索引 {n_index} 个 / 实时遍历 {n_live} 个）")
                except Exception:
                    pass
            elif kind == "tag_progress":
                done, total, cur, changed = payload
                self._processed = done
                try:
                    self.pb.config(value=done)
                except Exception:
                    pass
                if len(cur) > 42:
                    cur = cur[:40] + "…"
                self.count_lbl.config(text=f"{done} / {total}    {cur}")
                if done % 400 < 1 or done >= total:
                    try:
                        app = self.master
                        if hasattr(app, "log_progress"):
                            app.log_progress(
                                f"扫描进度：{done} / {total}"
                                f"（标签有变化 {changed} 个）    {cur}")
                    except Exception:
                        pass
            elif kind == "tag_done":
                total, changed = payload
                try:
                    app = self.master
                    if hasattr(app, "log_output"):
                        app.log_output(
                            f"扫描打标签完成：{total} 个文件，"
                            f"{changed} 个文件的标签有变化")
                except Exception:
                    pass
                self._finish(total, changed)
            elif kind == "error":
                self._finished = True
                try:
                    self.pb.stop()
                except Exception:
                    pass
                cb = self.on_finish
                try:
                    self.destroy()
                except Exception:
                    pass
                try:
                    messagebox.showerror("扫描出错", payload, parent=None)
                except Exception:
                    pass
                if cb:
                    try:
                        cb((0, 0))
                    except Exception:
                        pass
            elif kind == "cancelled":
                self._finished = True
                try:
                    self.pb.stop()
                except Exception:
                    pass
                self.result = (0, 0)
                cb = self.on_finish
                try:
                    self.destroy()
                except Exception:
                    pass
                if cb:
                    try:
                        cb((0, 0))
                    except Exception:
                        pass

        def _finish(self, total, processed):
            self._finished = True
            try:
                self.pb.stop()
            except Exception:
                pass
            self.result = (total, processed)
            cb = self.on_finish
            try:
                self.destroy()
            except Exception:
                pass
            if cb:
                try:
                    cb(self.result)
                except Exception:
                    pass

        # ---------------- 交互 ----------------
        def _on_cancel(self):
            if self._cancel_flag:
                return
            self._cancel_flag = True
            try:
                self.stage_lbl.config(text=T("正在取消…"))
            except Exception:
                pass

        def _minimize(self):
            try:
                self.iconify()
            except Exception:
                pass



# ★★ 2026-10-06：这个类已拆到单独的文件里
#   （AIxiede拆分开/程序分块/TagPickerDialog.py）。
#   这里保留一个「转发」：程序照常能用，但代码在那边维护。
#   ★ 兜底自带一份**原样代码** —— 就算新文件丢了/损坏了，
#     程序照样开得起来（用户最怕的就是「双击打不开」）。
try:
    from TagPickerDialog import TagPickerDialog, _set_app as _fk_TagPickerDialog
    _fk_TagPickerDialog(sys.modules[__name__])
except Exception:
    try:
        print("[提示] 拆出去的 TagPickerDialog.py 没找到，已退回内置简易版")
    except Exception:
        pass

    # ↓↓↓ 兜底用的原代码（新文件正常时不走这里）↓↓↓
    class TagPickerDialog(tk.Toplevel):
        """从已有标签里挑一个（带搜索框）。"""

        def __init__(self, master, all_tags, current="", multi=False, title=None,
                     exclude_ids=None):
            super().__init__(master)
            self.title(title or ("选择标签（可多选）" if multi else "选择标签"))
            self.geometry(_dlg_geom(420, 560))
            self.minsize(*_dlg_size(340, 400, minimum=(340, 400)))
            # ★ v25 补丁38（bug 修复）：这个窗口以前**只能单选**，而且只返回
            #   一个「标签名字」（字符串）。可是星图里的「＋ 加父级标签… /
            #   ＋ 加子级标签…」按钮需要的是**一批标签 id**，而且还得能排除
            #   掉自己 / 自己的祖先。原来那边调的是一个**根本不存在的类**
            #   `TagPickDialog` —— 一按就 NameError，被 except 包着，弹一句
            #   「打不开勾选窗口」，**功能等于废的**。
            #   现在给这个窗口加了：
            #     · multi=True   → 变成多选（勾选），result 是 id 的列表
            #     · exclude_ids  → 这些 id 不显示（用来排除自己/祖先/后代）
            #     · title        → 自定义标题
            #   单选老用法（result 是标签名字符串）完全不变。
            self.multi = bool(multi)
            self.result = None
            self.all_tags = list(all_tags or [])
            try:
                self._exclude = set(int(x) for x in (exclude_ids or []))
            except Exception:
                self._exclude = set()
            # 多选模式下勾中的 id（name -> id 的映射下面 _render 里建）
            self._checked = set()
            self._name2id = {}
            if self.multi:
                for t in self.all_tags:
                    try:
                        if str(t[1]) == str(current or ""):
                            self._checked.add(int(t[0]))
                    except Exception:
                        pass

            body = ttk.Frame(self, padding=10)
            body.pack(fill="both", expand=True)

            sbar = ttk.Frame(body)
            sbar.pack(fill="x", pady=(0, 6))
            make_search_label(sbar, "搜索标签：").pack(side="left")
            self.search_var = tk.StringVar()
            e = ttk.Entry(sbar, textvariable=self.search_var)
            e.pack(side="left", fill="x", expand=True, padx=(4, 4))
            e.focus_set()
            self.search_var.trace_add("write", lambda *a: self._render())

            self.count_lbl = ttk.Label(body, text="", foreground=theme_get("ok"))
            self.count_lbl.pack(anchor="w", pady=(0, 4))

            wrap = ttk.Frame(body)
            wrap.pack(fill="both", expand=True)
            self.canvas = tk.Canvas(wrap, highlightthickness=1,
                                    highlightbackground=theme_get("line"), bg=theme_get("card_bg"))
            sb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=sb.set)
            sb.pack(side="right", fill="y")
            self.canvas.pack(side="left", fill="both", expand=True)
            self.inner = tk.Frame(self.canvas, bg=theme_get("card_bg"))
            try:
                register_themed(self.inner, "card")   # ★ 常驻控件 → 换皮肤跟着刷
            except Exception:
                pass
            self._win_id = self.canvas.create_window(
                (0, 0), window=self.inner, anchor="nw")
            self.inner.bind(
                "<Configure>",
                lambda ev: self.canvas.configure(
                    scrollregion=self.canvas.bbox("all")))
            self.canvas.bind(
                "<Configure>",
                lambda ev: self.canvas.itemconfigure(self._win_id, width=ev.width))
            self.canvas.bind("<MouseWheel>", self._wheel)
            self.canvas.bind("<Button-4>", self._wheel)
            self.canvas.bind("<Button-5>", self._wheel)
            # ★ v25：鼠标停在标签文字上也能滚（不用去拖进度条）
            enable_wheel_scroll(self, self.canvas)

            btns = ttk.Frame(body)
            btns.pack(fill="x", pady=(8, 0))
            if self.multi:
                ttk.Button(btns, text=T("确定"),
                           command=self._ok).pack(side="right")
                ttk.Button(btns, text=T("取消"),
                           command=self._cancel).pack(side="right", padx=6)
                ttk.Button(btns, text=T("全不选"),
                           command=self._none).pack(side="left")
            else:
                ttk.Button(btns, text=T("取消"),
                           command=self._cancel).pack(side="right")
            self.bind("<Escape>", lambda ev: self._cancel())
            if self.multi:
                self.bind("<Return>", lambda ev: self._ok())
            else:
                self.bind("<Return>", lambda ev: self._pick_first())
            self.protocol("WM_DELETE_WINDOW", self._cancel)

            self._render()

            self.update_idletasks()
            w, h = self.winfo_width(), self.winfo_height()
            x = master.winfo_rootx() + (master.winfo_width() - w) // 2
            y = master.winfo_rooty() + (master.winfo_height() - h) // 3
            self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
            self.transient(master)
            self.grab_set()
            self.wait_window(self)

        def _visible_tags(self):
            q = (self.search_var.get() or "").strip().lower()
            out = []
            for t in self.all_tags:
                name = t[1] if len(t) > 1 else ""
                # ★ 补丁38：多选模式下，被排除的 id（自己 / 祖先 / 后代）不显示
                if self._exclude:
                    try:
                        if int(t[0]) in self._exclude:
                            continue
                    except Exception:
                        pass
                if q and q not in (name or "").lower():
                    continue
                out.append(t)
            return out

        def _render(self):
            for w in self.inner.winfo_children():
                w.destroy()
            self._name2id = {}
            tags = self._visible_tags()
            for t in tags:
                try:
                    self._name2id[str(t[1])] = int(t[0])
                except Exception:
                    pass
            if not tags:
                tk.Label(self.inner, text=T("（没有匹配的标签）"),
                         bg=theme_get("card_bg"), fg=theme_get("fg_dim")).pack(pady=16)
                self.count_lbl.config(text="")
                return
            extra = ""
            if self.multi:
                extra = "  ·  已勾选 %d 个" % len(self._checked)
            if self.search_var.get().strip():
                self.count_lbl.config(
                    text=f"显示 {len(tags)} / {len(self.all_tags)}{extra}")
            else:
                self.count_lbl.config(text=T("共 {n} 个标签{x}", n=len(tags), x=extra))

            for t in tags:
                tid, name, color = t[0], t[1], t[2]
                cnt = t[3] if len(t) > 3 else 0
                try:
                    tid_i = int(tid)
                except Exception:
                    tid_i = None
                row = tk.Frame(self.inner, bg=theme_get("card_bg"), cursor="hand2")
                row.pack(fill="x")
                if self.multi:
                    # ★ 补丁38：多选模式 —— 前面放个 ☑ / ☐，点一下切换
                    mark = "☑" if tid_i in self._checked else "☐"
                    lbl = tk.Label(row, text=f"{mark}  {name}   ({cnt})",
                                   bg=theme_get("card_bg"), fg=color or "#333",
                                   anchor="w", font=(FONT, UI_FONT_SIZE), padx=8, pady=3)
                else:
                    lbl = tk.Label(row, text=f"{name}   ({cnt})",
                                   bg=theme_get("card_bg"), fg=color or "#333",
                                   anchor="w", font=(FONT, UI_FONT_SIZE), padx=8, pady=3)
                lbl.pack(fill="x")

                if self.multi:
                    def _toggle(_e, ti=tid_i):
                        if ti is None:
                            return
                        if ti in self._checked:
                            self._checked.discard(ti)
                        else:
                            self._checked.add(ti)
                        self._render()
                else:
                    def _pick(_e, n=name):
                        self.result = n
                        self._do_close()

                def _enter(_e, r=row, l=lbl):
                    r.configure(bg=theme_get("hover_bg"))
                    l.configure(bg=theme_get("hover_bg"))

                def _leave(_e, r=row, l=lbl):
                    r.configure(bg=theme_get("card_bg"))
                    l.configure(bg=theme_get("card_bg"))

                for w in (row, lbl):
                    w.bind("<Button-1>", _toggle if self.multi else _pick)
                    w.bind("<Enter>", _enter)
                    w.bind("<Leave>", _leave)

        def _ok(self):
            """多选模式：确定 → result 是一串标签 id。"""
            self.result = sorted(self._checked)
            self._do_close()

        def _none(self):
            self._checked.clear()
            self._render()

        def _wheel(self, event):
            if event.num == 4:
                d = -1
            elif event.num == 5:
                d = 1
            else:
                d = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(d, "units")

        def _pick_first(self):
            tags = self._visible_tags()
            if tags:
                self.result = tags[0][1]
                self._do_close()

        def _do_close(self):
            try:
                self.grab_release()
            except Exception:
                pass
            self.destroy()

        def _cancel(self):
            self.result = None
            self._do_close()



# ★★★ AutoRuleEditDialog 已拆到 `AIxiede拆分开/程序分块/AutoRuleEditDialog.py`（2026-10-08）
#   ★★ 写法（错题本 #158）：① 直接 `from AutoRuleEditDialog import …`（不带包路径）
#     ② `_set_app` 取别名 —— 模块名和类名同名时会跑到类上找
try:
    from AutoRuleEditDialog import AutoRuleEditDialog, _set_app as _fk_AutoRuleEditDialog
    _fk_AutoRuleEditDialog(sys.modules[__name__])
    _HAS_AUTORULEEDITDIALOG = True
except Exception as _e:
    _HAS_AUTORULEEDITDIALOG = False
    note_swallowed(T("拆出去的 AutoRuleEditDialog.py 没找到，已退回内置简易版"), _e)

    class AutoRuleEditDialog:  # ★ 兜底：没模块也不崩，只是没这个功能
        def __init__(self, *a, **k):
            pass

        def _fill_scope_text(self, *a, **k):
            pass

        def _check_scope_now(self, *a, **k):
            pass

        def _get_scope(self, *a, **k):
            pass

        def _add_pattern_line(self, *a, **k):
            pass

        def _get_pattern(self, *a, **k):
            pass

        def _pick_tag(self, *a, **k):
            pass

        def _clear_scope(self, *a, **k):
            pass


# ★★★ AutoTagRulesDialog 已拆到 `AIxiede拆分开/程序分块/AutoTagRulesDialog.py`（2026-10-08）
#   ★★ 写法（错题本 #158）：① 直接 `from AutoTagRulesDialog import …`（不带包路径）
#     ② `_set_app` 取别名 —— 模块名和类名同名时会跑到类上找
try:
    from AutoTagRulesDialog import AutoTagRulesDialog, _set_app as _fk_AutoTagRulesDialog
    _fk_AutoTagRulesDialog(sys.modules[__name__])
    _HAS_AUTOTAGRULESDIALOG = True
except Exception as _e:
    _HAS_AUTOTAGRULESDIALOG = False
    note_swallowed(T("拆出去的 AutoTagRulesDialog.py 没找到，已退回内置简易版"), _e)

    class AutoTagRulesDialog:  # ★ 兜底：没模块也不崩，只是没这个功能
        def __init__(self, *a, **k):
            pass

        def _build_add_box(self, *a, **k):
            pass

        def _toggle_add_box(self, *a, **k):
            pass

        def _save_idle_cfg(self, *a, **k):
            pass

        def _refresh_idle_hint(self, *a, **k):
            pass

        def _on_rule_type_changed(self, *a, **k):
            pass


# ==========================================================================
#  ★ v25 补丁23：「属性」窗口
# ==========================================================================
# ★★★ PropsDialog 已拆到 `AIxiede拆分开/程序分块/PropsDialog.py`（2026-10-08）
#   ★★ 写法注意（错题本 #158）：
#     ① 直接 `from PropsDialog import …`（**不带包路径** ——
#        sys.path 里加的是「程序分块」目录）
#     ② `_set_app` **取别名**（`as _fk_PropsDialog`）——
#        模块名和类名同名时，`PropsDialog._set_app` 会跑到**类**上去找
try:
    from PropsDialog import PropsDialog, _set_app as _fk_PropsDialog
    _fk_PropsDialog(sys.modules[__name__])
    _HAS_PROPSDIALOG = True
except Exception as _e:
    _HAS_PROPSDIALOG = False
    note_swallowed(T("拆出去的 PropsDialog.py 没找到，已退回内置简易版"), _e)
    class PropsDialog:  # ★ 兜底：没模块也不崩
        def __init__(self, *a, **k):
            pass

def shortcut_key_to_seq(key):
    """★ 补丁25：把「Ctrl+Shift+N」这种写法变成 tkinter 认识的按键序列。

    tkinter 的写法是 `<Control-Shift-N>`，而且**大小写有讲究**：
      · `<Control-n>` 只在大写锁定关着时命中，`<Control-N>` 又只在大写开着时……
      所以每个带字母的组合键我们都绑两份（小写 + 大写），这样 CapsLock
      开不开都管用。
    返回一个列表（可能有两份）。
    """
    k = str(key or "").strip()
    if not k:
        return []
    parts = [p.strip() for p in k.split("+") if p.strip()]
    if not parts:
        return []
    mods = []
    main = None
    for p in parts:
        low = p.lower()
        if low == "ctrl" or low == "control":
            mods.append("Control")
        elif low == "shift":
            mods.append("Shift")
        elif low == "alt":
            mods.append("Alt")
        else:
            main = p
    if main is None:
        return []
    # ★★ 2026-10-06：**键名必须规范化，否则会静默绑不上** ★★
    #   踩的坑：用户报「按空格没反应」。查账本发现
    #     `快捷键：绑定 Space（快速预览）失败`
    #   原因是 tkinter 的按键名**有大小写讲究**，而且是两套相反的规矩：
    #     · **修饰键名/功能键名要大写**：`<Alt-Left>` ✔ / `<Alt-left>` ✘
    #       `<F5>` ✔ / `<f5>` ✘
    #     · **而空格反而是小写**：`<space>` ✔ / `<Space>` ✘
    #   （实测：`<Space>`、`<Alt-left>`、`<f5>` 三个都报
    #    `bad event type or keysym`。）
    #
    #   ★ 所以**不能一刀切转小写**（我第一次就是这么改的，
    #     结果把 Alt+Left 和 F5 弄坏了 —— 幸好当场测出来了）。
    #     正确做法：**列一张名字对照表**，表里有的按表来，
    #     表外的（单字母、数字）保持原样。
    _KEY_ALIAS = {
        # 小写才对
        "space": "space", "tab": "Tab", "return": "Return",
        "enter": "Return", "escape": "Escape", "esc": "Escape",
        "backspace": "BackSpace", "delete": "Delete", "del": "Delete",
        "insert": "Insert", "home": "Home", "end": "End",
        "prior": "Prior", "pageup": "Prior", "pgup": "Prior",
        "next": "Next", "pagedown": "Next", "pgdn": "Next",
        # 方向键要大写首字母
        "left": "Left", "right": "Right", "up": "Up", "down": "Down",
    }
    low = main.lower()
    if low in _KEY_ALIAS:
        main = _KEY_ALIAS[low]
    elif len(low) >= 2 and low[0] == "f" and low[1:].isdigit():
        # F1~F12 要大写（实测 <f5> 不认）
        main = "F" + low[1:]
    # 单字母：保持原样（下面会大小写各绑一份）
    base = "-".join(mods + [main])
    seqs = ["<%s>" % base]
    if len(main) == 1 and main.isalpha():
        alt_case = main.upper() if main.islower() else main.lower()
        seqs.append("<%s>" % "-".join(mods + [alt_case]))
    return seqs


# ★★★ 快捷键默认表（原来在主程序里，2026-10-08 拆 PropsDialog 时
#   **被脚本误搬进模块** —— ★ 因为它夹在「类」和「类」中间，
#   而它不是 class 也不是 def，脚本没把它当边界。已搬回（错题本 #162）。
SHORTCUT_DEFS = [
    ("delete",        "删除到回收站",           "Delete"),
    ("rename",        "重命名",                 "F2"),
    ("select_all",    "全选当前列表",           "Ctrl+A"),
    ("new_folder",    "新建文件夹",             "Ctrl+Shift+N"),
    ("copy",          "复制",                   "Ctrl+C"),
    ("cut",           "剪切",                   "Ctrl+X"),
    ("paste",         "粘贴到当前文件夹",       "Ctrl+V"),
    ("undo",          "撤销上一步（删除/改名/打标签）", "Ctrl+Z"),
    ("nav_back",      "后退（上一个文件夹）",   "Alt+Left"),
    ("nav_forward",   "前进（下一个文件夹）",   "Alt+Right"),
    ("toggle_tagbar", "显示 / 收起标签条",      "Ctrl+T"),
    ("toggle_preview", "显示 / 收起预览窗格",   "Ctrl+P"),
    ("toggle_taglib", "显示 / 收起标签库",      "Ctrl+L"),
    ("net_mode",      "切换网盘 索引 / 真实",   "Ctrl+M"),
    ("refresh",       "刷新当前视图",           "F5"),
    ("search_focus",  "跳到搜索框",             "Ctrl+F"),
    ("quick_preview", "快速预览（空格，再按关闭）", "Space"),
]


def load_shortcut_map():
    """读用户自定义的快捷键（没设过的用默认值）。返回 {动作键: 按键}。"""
    saved = load_ui_setting("shortcut_map", None)
    if not isinstance(saved, dict):
        saved = {}
    out = {}
    for name, _label, default in SHORTCUT_DEFS:
        v = saved.get(name, None)
        if v is None:
            v = default
        out[name] = str(v or "")
    return out


def save_shortcut_map(m):
    try:
        save_ui_setting("shortcut_map", dict(m))
        return True
    except Exception:
        return False


# ★★★ ShortcutDialog 已拆到 `AIxiede拆分开/程序分块/ShortcutDialog.py`（2026-10-08）
#   ★★ 写法（错题本 #158）：① 直接 `from ShortcutDialog import …`（不带包路径）
#     ② `_set_app` 取别名 —— 模块名和类名同名时会跑到类上找
try:
    from ShortcutDialog import ShortcutDialog, _set_app as _fk_ShortcutDialog
    _fk_ShortcutDialog(sys.modules[__name__])
    _HAS_SHORTCUTDIALOG = True
except Exception as _e:
    _HAS_SHORTCUTDIALOG = False
    note_swallowed(T("拆出去的 ShortcutDialog.py 没找到，已退回内置简易版"), _e)

    class ShortcutDialog:  # ★ 兜底：没模块也不崩，只是没这个功能
        def __init__(self, *a, **k):
            pass

        def _reload_rows(self, *a, **k):
            pass

        def _selected_action(self, *a, **k):
            pass

        def _on_pick(self, *a, **k):
            pass

        def _apply_pick(self, *a, **k):
            pass

        def _clear_one(self, *a, **k):
            pass

        def _capture(self, *a, **k):
            pass

        def _check_conflict(self, *a, **k):
            pass


# ★★★ TagBox 已拆到 `AIxiede拆分开/程序分块/TagBox.py`（2026-10-08）
#   ★★ 写法（错题本 #158）：① 直接 `from TagBox import …`（不带包路径）
#     ② `_set_app` 取别名 —— 模块名和类名同名时会跑到类上找
try:
    from TagBox import TagBox, _set_app as _fk_TagBox
    _fk_TagBox(sys.modules[__name__])
    _HAS_TAGBOX = True
except Exception as _e:
    _HAS_TAGBOX = False
    note_swallowed(T("拆出去的 TagBox.py 没找到，已退回内置简易版"), _e)

    class TagBox:  # ★ 兜底：没模块也不崩，只是没这个功能
        def __init__(self, *a, **k):
            pass

        def _on_configure(self, *a, **k):
            pass

        def _save_geo(self, *a, **k):
            pass

        def _toggle_topmost(self, *a, **k):
            pass

        def _on_close(self, *a, **k):
            pass

        def _fixed_ids(self, *a, **k):
            pass

        def _session_ids(self, *a, **k):
            pass

        def _save_session(self, *a, **k):
            pass


# ★★ 2026-10-06：这个类已拆到单独的文件里
#   （AIxiede拆分开/程序分块/RemoveFileTagsDialog.py）。
#   这里保留一个「转发」：程序照常能用，但代码在那边维护。
#   ★ 兜底自带一份**原样代码** —— 就算新文件丢了/损坏了，
#     程序照样开得起来（用户最怕的就是「双击打不开」）。
try:
    from RemoveFileTagsDialog import RemoveFileTagsDialog, _set_app as _fk_RemoveFileTagsDialog
    _fk_RemoveFileTagsDialog(sys.modules[__name__])
except Exception:
    try:
        print("[提示] 拆出去的 RemoveFileTagsDialog.py 没找到，已退回内置简易版")
    except Exception:
        pass

    # ↓↓↓ 兜底用的原代码（新文件正常时不走这里）↓↓↓
    class RemoveFileTagsDialog(tk.Toplevel):
        """★★ v26（2026-10-01）：右键「去除文件上的标签…」。

        用法（用户要的就是这个）：
          · 把选中文件身上的标签**全部列出来**，每个前面一个复选框；
          · 你勾哪几个，就去掉哪几个；
          · 点「确认去除」后**还会再问一次**（列出具体名字），
            你点「是」才真的动手。

        重要：只删「这些文件身上的这些标签」，
        **标签本身、标签树、别的文件都不受影响**。
        """

        def __init__(self, master, app, store, paths):
            super().__init__(master)
            self.app = app
            self.store = store
            self.paths = [p for p in (paths or []) if p]
            self.result = None

            self.title("去除文件上的标签")
            self.geometry(_dlg_geom(520, 620))
            self.minsize(*_dlg_size(420, 420, minimum=(420, 420)))
            self.transient(master)
            try:
                self.grab_set()
            except Exception:
                pass

            body = ttk.Frame(self, padding=10)
            body.pack(fill="both", expand=True)

            ttk.Label(
                body,
                text="共 %d 个文件：勾上想去掉的标签，然后点“确认去除”"
                     % len(self.paths),
                foreground=theme_get("fg_dim"), wraplength=470, justify="left").pack(anchor="w")

            # 汇总这几个文件身上的所有标签（id -> （名字, 颜色, 出现次数））
            self.tag_info = {}
            self._collect()

            ctrl = ttk.Frame(body)
            ctrl.pack(fill="x", pady=(8, 4))
            ttk.Button(ctrl, text=T("全选"), width=8,
                       command=lambda: self._set_all(True)).pack(side="left")
            ttk.Button(ctrl, text=T("全不选"), width=8,
                       command=lambda: self._set_all(False)).pack(side="left", padx=4)
            ttk.Button(ctrl, text=T("只选自动标签"), width=12,
                       command=self._pick_auto).pack(side="left")
            self.count_lbl = ttk.Label(ctrl, text="", foreground=theme_get("ok"))
            self.count_lbl.pack(side="right")

            wrap = ttk.Frame(body)
            wrap.pack(fill="both", expand=True)
            self.canvas = tk.Canvas(wrap, highlightthickness=1,
                                    highlightbackground=theme_get("line"), bg=theme_get("card_bg"))
            sb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=sb.set)
            sb.pack(side="right", fill="y")
            self.canvas.pack(side="left", fill="both", expand=True)
            self._font = tkfont.Font(family=FONT, size=UI_FONT_SIZE, weight=BOLD)
            self.canvas.bind("<Button-1>", self._on_click)
            self.canvas.bind("<MouseWheel>", self._on_wheel)
            self.canvas.bind("<Button-4>", self._on_wheel)
            self.canvas.bind("<Button-5>", self._on_wheel)
            self.canvas.bind("<Configure>", lambda e: self._render())

            foot = ttk.Frame(body)
            foot.pack(fill="x", pady=(8, 0))
            ttk.Button(foot, text=T("确认去除"), width=14,
                       command=self._ok).pack(side="right")
            ttk.Button(foot, text=T("取消"), width=10,
                       command=self.destroy).pack(side="right", padx=6)

            self.bind("<Escape>", lambda e: self.destroy())
            self._render()
            try:
                self.wait_visibility()
            except Exception:
                pass

        # ---------- 数据 ----------
        def _collect(self):
            """把这几个文件身上的标签汇总起来。"""
            try:
                info = self.store.tags_for_paths(self.paths) or {}
            except Exception:
                info = {}
            for p in self.paths:
                for rec in (info.get(p) or []):
                    try:
                        tid, name, color = int(rec[0]), rec[1], rec[2]
                    except Exception:
                        continue
                    cur = self.tag_info.get(tid)
                    if cur is None:
                        self.tag_info[tid] = {"name": name, "color": color,
                                              "n": 1}
                    else:
                        cur["n"] += 1
            # 归类：自动（继承/规则）的放后面，手动的放前面
            self._auto_ids = set()
            try:
                ids = list(self.tag_info.keys())
                if ids:
                    ph = ",".join("?" * len(ids))
                    for r in self.store.conn.execute(
                            "SELECT DISTINCT tag_id FROM file_tags "
                            "WHERE is_auto <> 0 AND tag_id IN (%s)" % ph,
                            tuple(ids)):
                        self._auto_ids.add(int(r[0]))
            except Exception:
                pass
            self.checked = set()

        def _ordered(self):
            """排序：手动标签在前，然后按名字。"""
            items = []
            for tid, d in self.tag_info.items():
                items.append((0 if tid not in self._auto_ids else 1,
                              d["name"] or "", tid, d))
            items.sort(key=lambda x: (x[0], x[1]))
            return items

        def _set_all(self, on):
            self.checked = set(self.tag_info.keys()) if on else set()
            self._render()

        def _pick_auto(self):
            self.checked = set(self._auto_ids)
            self._render()

        # ---------- 画 ----------
        def _row_h(self):
            return self._font.metrics("linespace") + 14

        def _render(self):
            c = self.canvas
            try:
                c.delete("all")
            except Exception:
                return
            f = self._font
            h = self._row_h()
            W = max(c.winfo_width(), 260)
            items = self._ordered()
            if not items:
                c.create_text(12, 16, anchor="nw", fill=theme_get("fg_dim"), font=(FONT, UI_FONT_SIZE),
                              text=T("（这些文件上没有任何标签）"))
                c.configure(scrollregion=(0, 0, W, 60))
                self._sync_count()
                return
            y = 6
            for _grp, _nm, tid, d in items:
                on = tid in self.checked
                # 复选框
                c.create_rectangle(12, y + 4, 26, y + 18, outline="#5d6d7e",
                                   width=1, fill="white",
                                   tags=("cb", "t%d" % tid))
                if on:
                    c.create_line(15, y + 11, 19, y + 16, 24, y + 5,
                                  fill="#16a085", width=2,
                                  tags=("cb", "t%d" % tid))
                # 颜色小块
                c.create_rectangle(34, y + 5, 46, y + 17,
                                   fill=d["color"] or "#3498db", outline="",
                                   tags=("cb", "t%d" % tid))
                label = d["name"]
                if tid in self._auto_ids:
                    label += "（自动）"
                if d["n"] < len(self.paths):
                    label += "  — %d/%d 个文件" % (d["n"],
                                                              len(self.paths))
                c.create_text(54, y + h / 2 - 4, anchor="w",
                              text=label, font=f,
                              fill=theme_get("fg") if on else theme_get("fg_dim"),
                              tags=("cb", "t%d" % tid))
                c.create_line(10, y + h - 4, W - 8, y + h - 4, fill=theme_get("line"),
                              tags=("cb", "t%d" % tid))
                y += h
            c.configure(scrollregion=(0, 0, W, y + 8))
            self._sync_count()

        def _sync_count(self):
            try:
                self.count_lbl.config(
                    text="已勾 %d / %d" % (len(self.checked),
                                                len(self.tag_info)))
            except Exception:
                pass

        def _on_wheel(self, event):
            d = -3 if getattr(event, "delta", 0) > 0 or event.num == 4 else 3
            self.canvas.yview_scroll(d, "units")
            self._render()

        def _on_click(self, event):
            cy = self.canvas.canvasy(event.y)
            h = self._row_h()
            idx = int((cy - 6) // h)
            items = self._ordered()
            if idx < 0 or idx >= len(items):
                return
            tid = items[idx][2]
            if tid in self.checked:
                self.checked.discard(tid)
            else:
                self.checked.add(tid)
            self._render()

        # ---------- 确认 ----------
        def _ok(self):
            if not self.checked:
                messagebox.showinfo("去除标签",
                                    "你还没勾任何标签。",
                                    parent=self)
                return
            names = [self.tag_info[t]["name"] for t in self.checked
                     if t in self.tag_info]
            shown = "、".join(names[:15]) + ("…" if len(names) > 15 else "")
            if not messagebox.askyesno(
                    "确认去除",
                    "确定要从 %d 个文件上去掉这 %d 个标签吗？\n\n%s\n\n"
                    "（只去掉文件上的这些标签，\n"
                    "标签本身和别的文件都不受影响）"
                    % (len(self.paths), len(self.checked), shown),
                    parent=self):
                return
            self.result = list(self.checked)
            self.destroy()



# ★★ 2026-10-06：这个类已拆到单独的文件里
#   （AIxiede拆分开/程序分块/TagBoxGridDialog.py）。
#   这里保留一个「转发」：程序照常能用，但代码在那边维护。
#   ★ 兜底自带一份**原样代码** —— 就算新文件丢了/损坏了，
#     程序照样开得起来（用户最怕的就是「双击打不开」）。
try:
    from TagBoxGridDialog import TagBoxGridDialog, _set_app as _fk_TagBoxGridDialog
    _fk_TagBoxGridDialog(sys.modules[__name__])
except Exception:
    try:
        print("[提示] 拆出去的 TagBoxGridDialog.py 没找到，已退回内置简易版")
    except Exception:
        pass

    # ↓↓↓ 兜底用的原代码（新文件正常时不走这里）↓↓↓
    class TagBoxGridDialog(tk.Toplevel):
        """★★ v26（2026-10-01 重做）：标签盒「分格」设置 —— **只管数量**。

        用户反馈（第一次的版本不好用）：
          「标签盒分格能不能只设置数量，具体有哪些标签要被放进对应的格子
            我希望能直接通过在拖动的方式放入」

        所以这一版砍掉了原来那个「左边标签池 / 右边格子列表」的复杂界面，
        只留两件事：
          1. **选方向**：横着分（左右几格）/ 竖着分（上下几层）；
          2. **定几格**：点 ＋ / － 或直接填数字，想几格就几格（不设上限）。
        点「✅ 应用」之后回到标签盒，**把标签直接拖进想放的格子**就行了。

        标签怎么归格（在标签盒里做，不做在这个窗口里）：
          · 单拖：把标签拖到另一个格子里松手 → 它就归那一格；
          · 多选拖：先框选/Ctrl 多选，拖其中一个 → 这一批全归那一格；
          · 从格子里拖出去（拖到窗口外）→ 从格子里拿出来。
        """

        def __init__(self, master, box):
            super().__init__(master)
            self.box = box
            self.store = box.store
            self.app = box.app

            self.title("标签盒分格设置")
            # ★ v26 修正（用户反馈「窗口不够大，底部有内容被遮盖了，
            #   每次打开要把窗口拉大」）：
            #   初始尺寸 520x400 太小 —— 里面的内容（三个标题段 +
            #   预览图 + 两行说明 + 底部三颗按钮）加起来差不多要 435 像素，
            #   400 根本放不下，底部按钮就被挤到了窗口下边缘之外。
            #   现在调到 560x560（多给 100 多像素余量），
            #   minsize 从 340 提到 480 —— 就算窗口被拉到最小，
            #   也能把底部三颗按钮塞进去。
            self.geometry(_dlg_geom(560, 560))
            self.minsize(*_dlg_size(460, 480, minimum=(460, 480)))
            self.transient(master)

            cur = box._read_layout()
            ids = box.box_ids()
            if cur:
                self.dir_var = tk.StringVar(value=cur["dir"])
                # ★★ v26 修正（用户反馈「有幽灵标签问题」）：
                #   分格配置里可能还留着一些**已经不在盒子里**的标签 ——
                #   结果一打开这个窗口就看到「第 1 格（5 个标签）」，
                #   而盒子本体是空的（显示和实际严重不符）。
                #
                #   这里做一次对齐：
                #     · 配置里不在盒子里的 → 丢掉（这就是"幽灵"）
                #     · 盒子里有、没归格的 → 兜底塞最后一格
                #   然后把对齐后的结果**写回配置** ——
                #   以后打开就不会再看到幽灵了。
                _id_set = set(int(t) for t in ids)
                self.cells = [list(c) for c in cur["cells"]]
                for _c in self.cells:
                    _c[:] = [t for t in _c if t in _id_set]
                _placed = set()
                for _c in self.cells:
                    _placed.update(_c)
                _extra = [t for t in ids if t not in _placed]
                if _extra:
                    self.cells[-1] = list(self.cells[-1]) + _extra
                # 回写干净的配置（如果确实变了）
                try:
                    _old = cur.get("cells") or []
                    _need = (len(_old) != len(self.cells))
                    if not _need:
                        for _a, _b in zip(_old, self.cells):
                            if list(_a) != list(_b):
                                _need = True
                                break
                    if _need:
                        save_ui_setting(
                            "tag_box_layout",
                            {"dir": cur["dir"],
                             "cells": [list(c) for c in self.cells]})
                except Exception as _e:
                    try:
                        note_swallowed(T("标签盒分格：回写对齐后的配置失败"), _e)
                    except Exception:
                        pass
            else:
                self.dir_var = tk.StringVar(value="h")
                n = 3 if len(ids) >= 3 else 1
                self.cells = [[] for _ in range(n)]
                for i, t in enumerate(ids):
                    self.cells[i % n].append(t)
            self.all_ids = list(ids)

            body = ttk.Frame(self, padding=14)
            body.pack(fill="both", expand=True)

            ttk.Label(body, text=T("① 怎么分"), font=(FONT, UI_FONT_SIZE, BOLD)).pack(anchor="w")
            row = ttk.Frame(body)
            row.pack(fill="x", pady=(4, 10))
            ttk.Radiobutton(row, text=T("↔ 横着分（左右几格）"),
                            variable=self.dir_var, value="h",
                            command=self._render).pack(side="left", padx=(0, 14))
            ttk.Radiobutton(row, text=T("↕ 竖着分（上下几层）"),
                            variable=self.dir_var, value="v",
                            command=self._render).pack(side="left")

            ttk.Label(body, text=T("② 分几格"), font=(FONT, UI_FONT_SIZE, BOLD)).pack(anchor="w")
            row2 = ttk.Frame(body)
            row2.pack(fill="x", pady=(4, 10))
            ttk.Button(row2, text="－", width=3,
                       command=self._dec).pack(side="left")
            self.n_lbl = ttk.Label(row2, text="3", font=(FONT, UI_FONT_SIZE, BOLD),
                                   foreground=theme_get("ok"))
            self.n_lbl.pack(side="left", padx=12)
            ttk.Button(row2, text="＋", width=3,
                       command=self._inc).pack(side="left")
            ttk.Label(row2, text=T("  格（想几格就几格，不设上限）"),
                      foreground=theme_get("fg_dim")).pack(side="left", padx=(10, 0))

            # ★★ v26 修正（用户反馈：「分格显示窗口不够大，底部有内容被遮盖了，
            #   每次打开要把窗口拉大」）：
            #
            #   原因：**Tk 的 pack 规则是「先 pack 的先占位置」** ——
            #   空间不够时，**最后 pack 的那一批控件先被挤出可视区**。
            #   原来这三颗按钮是**最后**才 pack 的，于是窗口一不够高，
            #   它们就被挤到了窗口下边缘之外（你看到的「被遮盖」）。
            #
            #   修法：**底部按钮改成最先 pack、并且用 side="bottom" 钉底。**
            #   这样无论窗口拉多小，它们都永远贴在窗口最下边、看得见、
            #   点得着；上面那些内容自己在上方想办法挤。
            #   说明文字也改成 side="bottom"（排在按钮上面一行），
            #   视觉上和原来一样，但不会再被挤掉。
            foot = ttk.Frame(body)
            foot.pack(side="bottom", fill="x", pady=(10, 0))
            ttk.Button(foot, text=T("✅ 应用"), width=12,
                       command=self._apply).pack(side="right")
            ttk.Button(foot, text=T("取消"), width=8,
                       command=self.destroy).pack(side="right", padx=6)
            ttk.Button(foot, text=T("↩ 取消分格（恢复自动排列）"), width=26,
                       command=self._clear_layout).pack(side="left")

            ttk.Label(
                body,
                text="点「✅ 应用」之后回到标签盒：把标签直接拖进想放的格子就行。\n"
                     "（框选 / Ctrl 多选后拖，可以一次放一批；拖出格子就是拿出来）",
                foreground=theme_get("fg_dim"), justify="left"
            ).pack(side="bottom", anchor="w", pady=(4, 0))

            # ---- ③ 预览（放在最后 pack，用它吃掉中间剩余的空间） ----
            #   ★ 说明：这里之所以放最后，是因为它用 expand=True ——
            #     expand 只会在「所有非 expand 控件都排完之后」才分配剩余空间，
            #     所以它自动是「剩余中间那一块」，不会挤掉底部的按钮。
            ttk.Label(body, text=T("③ 长这样"),
                      font=(FONT, UI_FONT_SIZE, BOLD)).pack(anchor="w")
            self.preview = tk.Canvas(body, height=110, bg=theme_get("card_bg"),
                                     highlightthickness=1,
                                     highlightbackground=theme_get("line"))
            try:
                register_themed(self.preview, "card")   # ★ 常驻控件 → 换皮肤跟着刷
            except Exception:
                pass
            self.preview.pack(fill="both", expand=True, pady=(4, 10))

            self.bind("<Escape>", lambda e: self.destroy())
            self._render()

        # ---------- 格数 ----------
        def _inc(self):
            self.cells.append([])
            self._render()

        def _dec(self):
            if len(self.cells) <= 1:
                return
            last = self.cells.pop()
            # 把最后一格的标签并回倒数第二格 —— 免得标签凭空消失
            self.cells[-1] = list(self.cells[-1]) + list(last)
            self._render()

        def _render(self):
            try:
                self.n_lbl.config(text=str(len(self.cells)))
            except Exception:
                pass
            c = self.preview
            try:
                c.delete("all")
                W = max(c.winfo_width(), 240)
                H = max(c.winfo_height(), 90)
            except Exception:
                return
            n = max(1, len(self.cells))
            GAP = 6
            if self.dir_var.get() == "h":
                cw = max(24, int((W - GAP * (n + 1)) / n))
                for i in range(n):
                    x0 = GAP + i * (cw + GAP)
                    c.create_rectangle(x0, GAP, x0 + cw, H - GAP,
                                       fill=theme_get("hover_bg"), outline="#8ab4f8",
                                       dash=(3, 2))
                    c.create_text(x0 + cw / 2, H / 2 - 8,
                                  text="第 %d 格" % (i + 1), fill=theme_get("accent"),
                                  font=(FONT, UI_FONT_SIZE))
                    c.create_text(x0 + cw / 2, H / 2 + 8,
                                  text="%d 个" % len(self.cells[i]),
                                  fill=theme_get("fg_dim"), font=(FONT, UI_FONT_SIZE))
            else:
                ch = max(16, int((H - GAP * (n + 1)) / n))
                for i in range(n):
                    y0 = GAP + i * (ch + GAP)
                    c.create_rectangle(GAP, y0, W - GAP, y0 + ch,
                                       fill=theme_get("hover_bg"), outline="#8ab4f8",
                                       dash=(3, 2))
                    c.create_text(W / 2, y0 + ch / 2,
                                  text="第 %d 格（%d 个标签）"
                                       % (i + 1, len(self.cells[i])),
                                  fill=theme_get("accent"), font=(FONT, UI_FONT_SIZE))

        # ---------- 应用 ----------
        def _apply(self):
            # 没归格的标签兜底塞最后一格，保证「盒子里的一个都不少」
            used = set()
            for cell in self.cells:
                used.update(cell)
            for t in self.all_ids:
                if t not in used:
                    self.cells[-1].append(t)
            layout = {"dir": self.dir_var.get(),
                      "cells": [list(c) for c in self.cells]}
            self.box._write_layout(layout)
            try:
                self.box._redraw()
            except Exception:
                pass
            try:
                self.app.set_status("标签盒已分成 %d 格（%s）—— 现在可以把标签拖进格子"
                                    % (len(self.cells),
                                       "横着" if layout["dir"] == "h" else "竖着"))
            except Exception:
                pass
            self.destroy()

        def _clear_layout(self):
            if not messagebox.askyesno("分格", T("取消分格，恢复成原来的自动排列？"),
                                       parent=self):
                return
            try:
                save_ui_setting("tag_box_layout", None)
            except Exception:
                pass
            try:
                self.box._redraw()
                self.app.set_status(T("标签盒已恢复自动排列"))
            except Exception:
                pass
            self.destroy()




# ★★ 2026-10-06：这个类已拆到单独的文件里
#   （AIxiede拆分开/程序分块/TagBoxPicker.py）。
#   这里保留一个「转发」：程序照常能用，但代码在那边维护。
#   ★ 兜底自带一份**原样代码** —— 就算新文件丢了/损坏了，
#     程序照样开得起来（用户最怕的就是「双击打不开」）。
try:
    from TagBoxPicker import TagBoxPicker, _set_app as _fk_TagBoxPicker
    _fk_TagBoxPicker(sys.modules[__name__])
except Exception:
    try:
        print("[提示] 拆出去的 TagBoxPicker.py 没找到，已退回内置简易版")
    except Exception:
        pass

    # ↓↓↓ 兜底用的原代码（新文件正常时不走这里）↓↓↓
    class TagBoxPicker(tk.Toplevel):
        """★ 补丁26：从「用得最多的标签」里勾选放进标签盒。"""

        def __init__(self, master, box):
            super().__init__(master)
            self.box = box
            self.store = box.store
            self.title("把标签放进标签盒")
            self.geometry(_dlg_geom(560, 600))
            self.transient(master)
            self.vars = {}
            # ★ 补丁39：勾选状态单独存一份（tid -> 是否勾上）。
            #   搜索会把一部分标签藏起来，如果只看界面上的控件，
            #   藏起来那些的勾选就会丢 —— 所以单独记着。
            self._checked = {}

            body = ttk.Frame(self)
            body.pack(fill="both", expand=True, padx=10, pady=10)
            ttk.Label(body, text=T("勾上要放进盒子的标签（按「用得最多」排序）："),
                      justify="left").pack(anchor="w")
            ttk.Label(body, text=T("（「固定」= 换视图也留着；不勾固定就是这次用用）"),
                      foreground=theme_get("fg_dim")).pack(anchor="w", pady=(0, 6))

            # ★ v25 补丁39（用户提的）：这个窗口**原来没有搜索框** —— 标签有
            #   两百多个，想找一个只能一行行往下翻，非常难用。现在加一个，
            #   边打边筛（按标签名，不区分大小写）。
            sbar = ttk.Frame(body)
            sbar.pack(fill="x", pady=(0, 6))
            make_search_label(sbar, "搜索标签：").pack(side="left")
            self.search_var = tk.StringVar()
            _se = ttk.Entry(sbar, textvariable=self.search_var)
            _se.pack(side="left", fill="x", expand=True, padx=(4, 4))
            _se.focus_set()
            self.search_var.trace_add("write", lambda *a: self._load())
            ttk.Button(sbar, text=T("清除"), width=6,
                       command=lambda: self.search_var.set("")).pack(side="left")
            self.count_lbl = ttk.Label(body, text="", foreground=theme_get("ok"))
            self.count_lbl.pack(anchor="w", pady=(0, 4))

            wrap = ttk.Frame(body)
            wrap.pack(fill="both", expand=True)
            sb = ttk.Scrollbar(wrap, orient="vertical")
            sb.pack(side="right", fill="y")
            self.canvas = tk.Canvas(wrap, highlightthickness=0,
                                    yscrollcommand=sb.set)
            self.canvas.pack(side="left", fill="both", expand=True)
            sb.configure(command=self.canvas.yview)
            self.inner = ttk.Frame(self.canvas)
            self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
            self.inner.bind("<Configure>", lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))
            self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(
                -1 if e.delta > 0 else 1, "units"))
            # ★ 鼠标停在标签文字上也能滚（不用去拖进度条）
            try:
                enable_wheel_scroll(self, self.canvas)
            except Exception:
                pass

            self.fixed_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(body, text=T("固定进盒子（换视图也在）"),
                            variable=self.fixed_var).pack(anchor="w", pady=(6, 4))
            btns = ttk.Frame(body)
            btns.pack(fill="x")
            ttk.Button(btns, text=T("确定"), command=self._ok).pack(side="right")
            ttk.Button(btns, text=T("取消"), command=self.destroy).pack(
                side="right", padx=6)
            self.bind("<Escape>", lambda e: self.destroy())
            self._load()

        def _load(self):
            """把「用得最多」的标签列出来（带搜索）。

            ★ 补丁39：原来一次全列出来、没有搜索。现在：
              · 搜索词一变就重画（边打边筛）；
              · **已经勾上的状态不会因为重画而丢** —— 勾选状态单独存在
                self.vars 里（tid -> 布尔），重画只是重新摆控件。
            """
            # 先把「上一次界面上勾了什么」收回来（重画会销毁控件）
            try:
                for tid, var in list(self.vars.items()):
                    self._checked[tid] = bool(var.get())
            except Exception:
                pass
            for w in self.inner.winfo_children():
                w.destroy()
            self.vars = {}
            rows = []
            try:
                rows = self.store.tags_by_usage(limit=1000)
            except Exception as exc:
                note_swallowed(T("标签盒：读「用得最多的标签」失败"), exc)
            q = ""
            try:
                q = (self.search_var.get() or "").strip().lower()
            except Exception:
                pass
            show = []
            for r in rows:
                nm = str(r["name"] or "")
                if q and q not in nm.lower():
                    continue
                show.append(r)
            try:
                self.count_lbl.config(
                    text=("显示 %d / %d 个标签" % (len(show), len(rows)))
                    if q else ("共 %d 个标签" % len(rows)))
            except Exception:
                pass
            in_box = set()
            try:
                in_box = set(self.box.box_ids())
            except Exception:
                pass
            for r in show:
                tid, name, cnt = r["id"], r["name"], r.get("cnt", 0)
                if tid in self._checked:
                    val = self._checked[tid]
                else:
                    val = tid in in_box
                var = tk.BooleanVar(value=val)
                self.vars[tid] = var
                cb = ttk.Checkbutton(self.inner, text="%s（%d 个文件）" % (name, cnt),
                                     variable=var)
                cb.pack(anchor="w")
            if not show:
                ttk.Label(self.inner,
                          text=("（没有匹配的标签）" if q else "（读不到标签……）"),
                          foreground=theme_get("fg_dim")).pack(anchor="w", pady=6)

        def _ok(self):
            fixed = bool(self.fixed_var.get())
            # ★ 补丁39：先把界面上现在的勾选收进 _checked（因为搜索会把
            #   一部分标签藏起来，直接遍历 self.vars 会漏掉被藏起来的那些）。
            try:
                for tid, var in list(self.vars.items()):
                    self._checked[tid] = bool(var.get())
            except Exception:
                pass
            for tid, want in list(self._checked.items()):
                try:
                    in_box = tid in self.box.box_ids()
                except Exception:
                    in_box = False
                if want and not in_box:
                    if fixed:
                        try:
                            self.store.tag_box_add(tid)
                        except Exception:
                            pass
                    else:
                        try:
                            self.box.add_tag(tid)
                        except Exception:
                            pass
                elif not want and in_box:
                    try:
                        self.box.remove_tag(tid)
                    except Exception:
                        pass
            try:
                self.box._redraw()
            except Exception:
                pass
            self.destroy()



# ★★★ QuickPreview 已拆到 `AIxiede拆分开/程序分块/QuickPreview.py`（2026-10-08）
#   ★★ 写法注意（错题本 #158）：
#     ① 直接 `from QuickPreview import …`（**不带包路径** ——
#        sys.path 里加的是「程序分块」目录）
#     ② `_set_app` **取别名**（`as _fk_QuickPreview`）——
#        模块名和类名同名时，`QuickPreview._set_app` 会跑到**类**上去找
try:
    from QuickPreview import QuickPreview, _set_app as _fk_QuickPreview
    _fk_QuickPreview(sys.modules[__name__])
    _HAS_QUICKPREVIEW = True
except Exception as _e:
    _HAS_QUICKPREVIEW = False
    note_swallowed(T("拆出去的 QuickPreview.py 没找到，已退回内置简易版"), _e)
    class QuickPreview:  # ★ 兜底：没模块也不崩
        def __init__(self, *a, **k):
            pass

def enable_wheel_scroll(top, canvas):
    """让整个窗口任意位置都能用鼠标滚轮滚动 canvas。

    ★ v25：原来只把 <MouseWheel> 绑在 canvas 上，鼠标停在勾选框 /
      标签文字上时事件不会传给 canvas，非得去拖右边的进度条；
      现在绑在窗口（Toplevel）上 —— Tk 会给每个子控件都带上
      窗口这一级绑定，所以停在哪儿都能滚。
    """

    def _wheel(event):
        w = event.widget
        if w is canvas:
            return None          # canvas 自己已经绑过，交给它
        try:
            cls = w.winfo_class()
        except Exception:
            cls = ""
        # 自带滚动条的控件交给它自己，别抢
        if cls in ("Text", "Listbox", "Treeview", "TScrollbar",
                   "HScrollbar", "Spinbox", "TCombobox", "ComboBox"):
            return None
        num = getattr(event, "num", 0)
        if num == 4:
            d = -1
        elif num == 5:
            d = 1
        else:
            d = -1 if getattr(event, "delta", 0) > 0 else 1
        try:
            if getattr(event, "state", 0) & 0x0001:      # 按住 Shift = 横向
                canvas.xview_scroll(d, "units")
            else:
                canvas.yview_scroll(d, "units")
        except Exception:
            return None
        return "break"

    for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
        try:
            top.bind(seq, _wheel, add="+")
        except Exception:
            pass


# 索引扫描的忙标志：闲时任务和索引管理窗口共用，避免同时扫两遍
INDEX_SCAN_EVENT = threading.Event()


def is_gone_error(err):
    """★ v25 补丁18：这个报错是不是「东西不在了」（网盘里删掉了 / 目录没了）？

    这类情况不值得当「错误」刷屏：网盘里删除过的目录、临时缓存目录，
    点开一次报一次太难看了。判定为 True 的，只记一句普通日志、并且
    记住它，以后不再反复去试。
    """
    t = str(err or "").lower()
    if not t:
        return False
    for k in ("winerror 2", "系统找不到指定的文件", "找不到指定的文件",
              "not found", "no such file", "cannot find", "does not exist",
              "statuscode.not_found", "不存在"):
        if k in t:
            return True
    return False


def prune_orphan_dir_cache(store, root_path, dry_run=False):
    """★ v25 补丁20：清掉索引里的「幽灵目录」。

    什么是幽灵目录：网盘里某个目录被删掉之后，**某一层父目录重新列过**，
    就不认它了；但它自己下面已经缓存好的那些行还留在库里，而没有任何
    地方会再去列它 —— 于是永远删不掉。表现就是：索引里总有一小撮
    「读不到的目录」，点开就报「目录读不到」。

    做法（纯本地 SQLite，几秒钟，不碰网盘）：
      1) 把这个根下面的 dir_cache 行全读出来；
      2) 凡是「作为某个目录的子项出现过」的目录路径，算「活着」；
      3) 有自己缓存行、却没人认它的目录路径 = 幽灵 → 连同它的行和
         dir_cache_meta 记录一起删掉。

    ★ 只删「目录缓存」（列表用的那份），**不动 files 表、绝不动任何标签**。
    返回 (删掉的目录数, 删掉的行数)。
    """
    try:
        conn = store.conn
    except Exception:
        return 0, 0
    prefix = str(root_path or "")
    _rp = prefix.replace("/", "\\")
    _is_root = (len(_rp) == 3 and _rp[1] == ":" and _rp[2] == "\\")
    prefix = _rp if _is_root else _rp.rstrip("\\")
    if len(prefix) < 2:
        return 0, 0
    # ★ v25 补丁24：用「等于自己 或 子孙」的写法（不用 LIKE，不会漏掉根目录）
    pat = dir_scope_clause()
    scope_args = dir_scope_args(prefix)
    lock = getattr(store, "_lock", None)

    def _run():
        rows = conn.execute(
            "SELECT dir_path, name, is_dir FROM dir_cache "
            "WHERE " + pat, scope_args).fetchall()
        alive = set()
        alive.add(prefix.rstrip("\\").lower())
        dir_rows = {}
        for r in rows:
            try:
                dp = r["dir_path"]
                nm = r["name"]
                is_d = r["is_dir"]
            except Exception:
                dp, nm, is_d = r[0], r[1], r[2]
            dir_rows[dp] = dir_rows.get(dp, 0) + 1
            if is_d:
                alive.add((dp.rstrip("\\") + "\\" + nm).lower())
        ghost = [dp for dp in dir_rows
                 if dp.rstrip("\\").lower() not in alive]
        if dry_run or not ghost:
            return len(ghost), 0
        n_rows = 0
        with conn:
            for dp in ghost:
                cur = conn.execute("DELETE FROM dir_cache WHERE dir_path = ?",
                                   (dp,))
                n_rows += (cur.rowcount or 0)
                try:
                    conn.execute("DELETE FROM dir_cache_meta WHERE dir_path = ?",
                                 (dp,))
                except Exception:
                    pass
        return len(ghost), n_rows

    try:
        if lock is not None:
            with lock:
                return _run()
        return _run()
    except Exception as exc:
        try:
            note_swallowed(T("清理幽灵目录失败"), exc)
        except Exception:
            pass
        return 0, 0


def scan_index_roots(store, root_ids, cancel_flag=None, progress_cb=None,
                     delay=0.0, api_client=None):
    """扫描索引根目录（含所有子目录），把目录项写进 dir_cache。

    ★ v25：改用 os.scandir —— Windows 的目录列表（FindFirstFile）
      本身就带回文件大小和修改时间，不需要额外请求网盘 / 磁盘，
      所以索引时顺手把大小也记下来，文件列表里就不用再显示「?」了。
      （原来是 os.walk 只记名字，还会把已有的大小冲成 NULL。）

    ★ v25 补丁17：多了个 api_client 参数。传进来一个连好的
      CloudDriveApiClient 时，**网盘根目录**会改走 CloudDrive2 自己的
      本地接口来建索引（快、报错清楚）；认不出来的路径（本地盘）
      照旧走原来的挂载盘扫描。不传（None）就完全是老行为。

    - cancel_flag：可选函数，返回 True 表示立刻收工（闲时任务用；
      用户一动鼠标就传 True 进来，让扫描别跟人抢资源）。
    - progress_cb(rid, root_path, dir_count, file_count, current_dir)：
      每个目录回调一次，UI 用来刷进度。
    - delay：每个目录之间睡一下（秒），越大越「缓慢」。
    返回 [(root_id, path, dir_count, file_count, error), ...]
    """
    out = []
    try:
        roots = {r["id"]: r for r in store.all_index_roots()}
    except Exception:
        roots = {}

    def _cancelled():
        try:
            return bool(cancel_flag and cancel_flag())
        except Exception:
            return False

    for rid in list(root_ids or []):
        if _cancelled():
            break
        r = roots.get(rid)
        if r is None:
            continue
        path = r["path"]
        dir_count = 0
        file_count = 0
        error = ""
        # ★ v25 补丁15：扫描途中有几个目录读不到（网盘里刚被删掉、或者
        #   CloudDrive 一瞬间抽风），原来只把「最后一个错误」原样丢到界面上，
        #   看起来像「整个扫描失败了」，其实其它目录全都扫好了。
        #   现在分三件事记：跳过了几个、是哪些、以及最后一次原始报错。
        skip_dirs = []          # 读不到的目录（最多记 3 个给用户看）
        skip_count = 0          # 读不到的目录总数
        stat_skip = 0           # 读不到大小/时间的文件数
        last_err_raw = ""       # 最后一次原始报错（用来判断是不是网盘没醒）
        # ★ v25 补丁17：网盘根目录优先走 CloudDrive2 自己的本地接口。
        #   认得出来（是网盘目录）就走 API 那条路，认不出来（本地盘、
        #   或者没填令牌 / 连不上）就照旧走下面的挂载盘扫描。
        if api_client is not None:
            cd_key = None
            try:
                cd_key = api_client.cd_path_of(path)
            except Exception as _e:
                cd_key = None
                try:
                    note_swallowed("CloudDrive2 API：把根目录换算成 API 路径失败，"
                                   "这个根目录改走挂载盘", _e)
                except Exception:
                    pass
            if cd_key:
                dc2, fc2, err2 = scan_index_root_via_api(
                    api_client, store, rid, path,
                    cancel_flag=cancel_flag, progress_cb=progress_cb)
                try:
                    store.update_index_root_stats(rid, fc2, dc2, err2)
                except Exception as _e2:
                    try:
                        note_swallowed(T("CloudDrive2 API：把统计结果写回索引根失败"), _e2)
                    except Exception:
                        pass
                out.append((rid, path, dc2, fc2, err2))
                continue
        # ★ v25 补丁：网盘偶尔会「一时连不上」（WinError 53 / 1203，
        #   资源管理器里点一下就好了）。先探一下根目录，失败了等 1 秒
        #   重试一次，免得整棵树白扫、只留下一行看不懂的错误。
        root_ok = False
        for attempt in (0, 1):
            if _cancelled():
                break
            try:
                with os.scandir(path):
                    pass
                root_ok = True
                break
            except Exception as exc:
                error = str(exc)
                if attempt == 0:
                    try:
                        time.sleep(1.0)
                    except Exception:
                        pass
        if not root_ok:
            err_line = error or "无法读取"
            hint = net_error_hint(err_line)
            if hint:
                err_line = (err_line + "  ·  先在资源管理器里打开一次"
                            "这个网盘再扫")
            try:
                store.update_index_root_stats(rid, 0, 0, err_line)
            except Exception:
                pass
            out.append((rid, path, 0, 0, err_line))
            continue
        # ★ v25 补丁16：两个跟「扫网盘容易出岔子」有关的修法（都在这段循环里）
        #   1) 某些目录读不到（网盘一瞬间抽风 / 正好被删掉）不再直接放弃：
        #      先记下来，等整棵树扫完之后再回头补扫两轮（隔 1 秒、隔 3 秒）。
        #      网盘的限制（CloudDrive2 文档里写了每个网盘有「每秒查询数」上限）
        #      造成的失败，隔一会儿再问通常就正常了。
        #   2) **读不到的目录不再往里写空列表**！以前无论读没读到都会调
        #      save_dir_entries，读失败时写进去的是空列表 —— 等于把那个目录
        #      已经缓存好的内容冲成「空的」，界面里看着就像那个文件夹突然
        #      没东西了（这大概就是你说的「扫到一半好像停了」）。
        stack = [path]
        retry_list = []       # 这一轮读不到、待会儿要补扫的目录
        retry_round = 0       # 0=主扫描，1/2=补扫轮次
        while stack or (retry_list and retry_round < 2):
            if _cancelled():
                break
            if not stack:
                # 主扫描跑完了，回头补扫刚才读不到的目录
                retry_round += 1
                try:
                    time.sleep(1.0 if retry_round == 1 else 3.0)
                except Exception:
                    pass
                stack = retry_list
                retry_list = []
            cur = stack.pop()
            entries = []
            ok = False
            try:
                with os.scandir(cur) as it:
                    for e in it:
                        try:
                            is_d = e.is_dir(follow_symlinks=False)
                        except OSError:
                            is_d = False
                        if is_d:
                            entries.append((e.name, True, None, None))
                            stack.append(e.path)
                        else:
                            size = None
                            mtime = None
                            try:
                                st = e.stat()
                                size = st.st_size
                                mtime = st.st_mtime
                            except OSError as _e:
                                stat_skip += 1
                                note_swallowed(T("索引扫描：有些文件读不到大小/时间（网盘文件常见，会记成问号）"), _e)
                            entries.append((e.name, False, size, mtime))
                            file_count += 1
                ok = True
            except Exception as exc:
                error = str(exc)
                last_err_raw = str(exc)
                if retry_round < 2:
                    retry_list.append(cur)     # 留着待会儿补扫
                else:
                    skip_count += 1            # 补扫也读不到，才算真的跳过
                    if len(skip_dirs) < 3:
                        skip_dirs.append(cur)
            if ok:
                # ★ 只有真读到了才写缓存（写成空列表会把旧内容冲掉）
                try:
                    store.save_dir_entries(cur, entries)
                except Exception as exc:
                    error = str(exc)
                    last_err_raw = str(exc)
                dir_count += 1
            if progress_cb is not None:
                try:
                    progress_cb(rid, path, dir_count, file_count, cur)
                except Exception:
                    pass
            if delay:
                try:
                    time.sleep(delay)
                except Exception:
                    pass
        # ★ v25 补丁15：把「报错」翻译成人话再往界面上送。
        #   原来不管哪种情况都只丢一句原始报错（还是最后一个），看着像整个
        #   扫描报废了。其实这些「找不到文件」都只是网盘里某些目录在扫描
        #   途中正好被删掉 / 一时读不到，其它目录全都扫好了。
        err_line = error
        if skip_count:
            parts = "、".join(skip_dirs)
            more = "…" if skip_count > len(skip_dirs) else ""
            friendly = (f"跳过 {skip_count} 个目录（扫描途中刚被删掉 / "
                        f"网盘一时读不到，不影响其它目录）：{parts}{more}")
            hint = net_error_hint(last_err_raw)
            if hint:
                friendly += "  ·  " + hint
            if error and error != last_err_raw:
                # 除了「有目录读不到」，还另外出了别的错（比如写库失败），
                # 两个都说，别把真问题藏起来。
                err_line = friendly + "  ·  另外：" + error
            else:
                err_line = friendly
        if stat_skip and not err_line:
            # 文件读不到大小/时间：不算错误，说一句就行（网盘文件很常见）
            err_line = (f"有 {stat_skip} 个文件读不到大小/时间"
                        f"（网盘文件常见，列表里会显示成问号）")
        try:
            store.update_index_root_stats(rid, file_count, dir_count, err_line)
        except Exception as _e:
            note_swallowed(T("索引扫描：把统计结果写回索引根失败"), _e)
        out.append((rid, path, dir_count, file_count, err_line))
    return out


# ==========================================================================
#  ★ 索引管理对话框
# ==========================================================================
# ★★★ IndexManagerDialog 已拆到 `AIxiede拆分开/程序分块/IndexManagerDialog.py`（2026-10-08）
#   ★★ 写法（错题本 #158）：① 直接 `from IndexManagerDialog import …`（不带包路径）
#     ② `_set_app` 取别名 —— 模块名和类名同名时会跑到类上找
try:
    from IndexManagerDialog import IndexManagerDialog, _set_app as _fk_IndexManagerDialog
    _fk_IndexManagerDialog(sys.modules[__name__])
    _HAS_INDEXMANAGERDIALOG = True
except Exception as _e:
    _HAS_INDEXMANAGERDIALOG = False
    note_swallowed(T("拆出去的 IndexManagerDialog.py 没找到，已退回内置简易版"), _e)

    class IndexManagerDialog:  # ★ 兜底：没模块也不崩，只是没这个功能
        def __init__(self, *a, **k):
            pass

        def _apply_theme(self, *a, **k):
            pass

        def _reload(self, *a, **k):
            pass

        def _selected_roots(self, *a, **k):
            pass

        def _on_select_root(self, *a, **k):
            pass

        def _update_info(self, *a, **k):
            pass


# ==========================================================================
#  界面缩放对话框
# ==========================================================================
# ★★ 2026-10-06：这个类已拆到单独的文件里
#   （AIxiede拆分开/程序分块/UIScaleDialog.py）。
#   这里保留一个「转发」：程序照常能用，但代码在那边维护。
#   ★ 兜底自带一份**原样代码** —— 就算新文件丢了/损坏了，
#     程序照样开得起来（用户最怕的就是「双击打不开」）。
try:
    from UIScaleDialog import UIScaleDialog, _set_app as _fk_UIScaleDialog
    _fk_UIScaleDialog(sys.modules[__name__])
except Exception:
    try:
        print("[提示] 拆出去的 UIScaleDialog.py 没找到，已退回内置简易版")
    except Exception:
        pass

    # ↓↓↓ 兜底用的原代码（新文件正常时不走这里）↓↓↓
    class UIScaleDialog(tk.Toplevel):
        PRESETS = [
            ("80%  (小屏幕)", 0.8),
            ("90%", 0.9),
            ("100% (标准)", 1.0),
            ("115% (推荐)", 1.15),
            ("130%", 1.3),
            ("150% (大屏/高清)", 1.5),
            ("175%", 1.75),
            ("200% (超高DPI)", 2.0),
        ]

        def __init__(self, master, current_scale):
            super().__init__(master)
            self.title("调整界面缩放")
            self.resizable(False, False)
            self.result = None
            self._current = float(current_scale)

            body = ttk.Frame(self, padding=16)
            body.pack(fill="both", expand=True)

            ttk.Label(body, text=T("选择界面缩放比例："),
                      font=(FONT, UI_FONT_SIZE, BOLD)).pack(anchor="w", pady=(0, 8))

            self.var = tk.DoubleVar(value=self._current)
            self.custom_var = tk.StringVar(value=f"{self._current:.2f}")

            for label, val in self.PRESETS:
                ttk.Radiobutton(
                    body, text=label, value=val,
                    variable=self.var,
                    command=self._on_preset_change,
                ).pack(anchor="w", pady=2)

            custom_row = ttk.Frame(body)
            custom_row.pack(fill="x", pady=(10, 0))
            ttk.Label(custom_row, text=T("自定义：")).pack(side="left")
            e = ttk.Entry(custom_row, textvariable=self.custom_var, width=8)
            e.pack(side="left")
            ttk.Label(custom_row,
                      text=f"（{int(MIN_UI_SCALE*100)}% ~ {int(MAX_UI_SCALE*100)}%）",
                      foreground=theme_get("fg_dim")).pack(side="left", padx=6)

            self.custom_var.trace_add("write", self._on_custom_change)

            ttk.Separator(body).pack(fill="x", pady=10)
            ttk.Label(
                body,
                text="提示：改完后点「确定」，会提示你重启程序。\n"
                     "重启后所有字体、行高、按钮都会按新比例显示。",
                foreground=theme_get("fg_dim"), justify="left").pack(anchor="w")

            btns = ttk.Frame(body)
            btns.pack(fill="x", pady=(14, 0))
            ttk.Button(btns, text=T("确定"), command=self._ok).pack(side="right")
            ttk.Button(btns, text=T("取消"), command=self._cancel).pack(side="right", padx=6)
            ttk.Button(btns, text="恢复默认 (115%)",
                       command=self._reset).pack(side="left")

            self.bind("<Return>", lambda e: self._ok())
            self.bind("<Escape>", lambda e: self._cancel())
            self.protocol("WM_DELETE_WINDOW", self._cancel)

            self.update_idletasks()
            w, h = self.winfo_width(), self.winfo_height()
            x = master.winfo_rootx() + (master.winfo_width() - w) // 2
            y = master.winfo_rooty() + (master.winfo_height() - h) // 3
            self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
            self.transient(master)
            self.grab_set()
            self.wait_window(self)

        def _on_preset_change(self):
            try:
                v = float(self.var.get())
            except Exception:
                return
            try:
                info = self.custom_var.trace_info()
                if info:
                    self.custom_var.trace_remove("write", info[0][1])
            except Exception:
                pass
            try:
                self.custom_var.set(f"{v:.2f}")
            finally:
                self.custom_var.trace_add("write", self._on_custom_change)

        def _on_custom_change(self, *args):
            try:
                v = float(self.custom_var.get())
            except Exception:
                return
            for _, pv in self.PRESETS:
                if abs(pv - v) < 1e-6:
                    try:
                        if abs(self.var.get() - pv) > 1e-6:
                            self.var.set(pv)
                    except Exception:
                        pass
                    return

        def _reset(self):
            self.var.set(DEFAULT_UI_SCALE)
            self.custom_var.set(f"{DEFAULT_UI_SCALE:.2f}")

        def _ok(self):
            try:
                v = float(self.custom_var.get())
            except Exception:
                try:
                    v = float(self.var.get())
                except Exception:
                    v = self._current
            if v < MIN_UI_SCALE:
                v = MIN_UI_SCALE
            if v > MAX_UI_SCALE:
                v = MAX_UI_SCALE
            self.result = v
            try:
                self.grab_release()
            except Exception:
                pass
            self.destroy()

        def _cancel(self):
            self.result = None
            try:
                self.grab_release()
            except Exception:
                pass
            self.destroy()
            # ==========================================================================
# ★★ 2026-10-06 新增：**「界面卡多久了」的哨兵**
#
#   为什么要有它：
#     以前用 `root.after(200, _heartbeat_tick)` 来记「我还在动」，
#     但这个定时器**只有在界面闲下来的时候才会被跑到**。
#     用户切文件切得快的时候，界面队列里堆满了活儿，这个定时器就
#     **一直排不上队** —— 于是它最后记下的时间戳越来越旧，
#     1 秒一次的那个看门狗就误判「界面无响应 3 秒」，
#     然后它自己往「问题」面板里写日志 ——
#     **而写日志本身又是主线程的活儿**（还带 Tk 操作），
#     结果就是「越卡越报、越报越卡」，把界面彻底拖死。
#     实测：一次误报就让主线程僵了 **1.36 秒**。
#
#   现在的做法（外面成熟软件都这么干）：
#     · **不在界面线程里打卡**，改成两个纯计算线程：
#         打卡线程每 200 毫秒把时间戳写进一个共享变量（完全不碰界面）；
#         看门狗线程盯着它，真卡住了才把「报一笔」这件事
#         **排队交给主线程**（不直接抢）；
#     · 而且排队用 `_bg_post` —— 它是纯列表操作，永远不会卡住。
#     这样「卡顿检测」本身**永远不会成为卡顿的原因**。
#   ★ 注意：这一整段必须放在**类外面、类之前** ——
#     写进类中间会把后面的方法全都挤出类（实测踩过：一插进去，
#     后面 4600 行方法全变成没人调用的普通函数，"打开文件夹"都没反应了）。
# ==========================================================================
_HEART = {"stamp": 0.0, "reported": False, "run": False}


def _heartbeat_start():
    """启动「我还在动」的打卡线程（只启一次，纯计算，不碰界面）。"""
    if _HEART.get("run"):
        return
    _HEART["run"] = True
    _HEART["stamp"] = time.time()
    _HEART["reported"] = False

    def _beat():
        while _HEART.get("run") and not APP_CLOSING:
            try:
                _HEART["stamp"] = time.time()
                if _HEART.get("reported"):
                    # 界面又活过来了 → 重新武装，下次卡住才再报一次
                    _g = time.time() - _HEART["stamp"]
                    if _g < 1.0:
                        _HEART["reported"] = False
            except Exception:
                pass
            time.sleep(0.2)

    threading.Thread(target=_beat, daemon=True, name="界面心跳").start()


def _heartbeat_stop():
    """程序要关了 → 让打卡线程收工。"""
    _HEART["run"] = False


# ==========================================================================
#  主应用
# ==========================================================================

# ==========================================================================
#  ★★★ 2026-10-08 **悬浮球**（用户要的：菜单栏改成悬浮球）★★★
#  ------------------------------------------------------------------------
#  ★★ 用户原话：
#    · 「我其实觉得文件、标签、界面、帮助可以搞成个悬浮球 右键下拉菜单式」
#    · 「悬浮球它是**蒙多，想拖到哪就去哪**，第一次在文件列表右侧空白区域出现，
#       然后记录用户把它拖到哪里，以后打开就在哪里出现，**能拖，但双击复位免了**」
#    · 「**左键出菜单可以，右键换皮肤、透明度什么的吧**，
#        **有点想让它显示网速、硬盘读写速度什么的**」
#    · 「**圆球默认三道杠好**，原菜单栏不想留，你备份吧」
#    · 「**右键加个显示模式，让使用的人决定想要看到的**，
#        是只显示三道杠、还是只显示网速、亦或者显示硬盘读写速度，
#        **还是各种组合显示，让用户自己选**」
#
#  ★★ 为什么做这个（不只是"好看"）：
#    用户实测反馈「都夜间模式了，菜单栏还白白的」——
#    而**实测证明 Windows 的菜单栏 Tk 根本改不了颜色**
#    （截图取像素：设了深色，菜单栏照样 (255,255,255)）。
#    → **把菜单栏藏起来、改成悬浮球，是唯一的修法**（白条从根上消失）。
#
#  ★★ 菜单怎么来的（**关键设计**）：
#    悬浮球左键 → **直接 `tk_popup` 主程序那个 `menubar`** ——
#    37 个入口、13 个子菜单**自动全在**，**一行功能代码都不用搬**。
#    ★ 为什么不"把菜单项一个个抄到球里"：
#      那是两份代码，以后加功能要改两处 —— **迟早漏一个**
#      （错题本 #110 的教训：同一个东西只该有一个来源）。
# ==========================================================================
# ==========================================================================
#  ★★★ 2026-10-08 **悬浮球自己的皮肤**（用户要求：跟主界面**完全分开**）★★★
#  ------------------------------------------------------------------------
#  ★★ 用户原话：
#    「我说的皮肤**有球自己的皮肤也有主界面的皮肤**，两个都搞好入口，
#     但是**是完全不一样的**，你可别搞混了啊」
#    然后他选了 **B B B**：
#      · ① 球的皮肤**不只颜色形状**，还要**样式**（长条/胶囊/只有圆点…）
#      · ② 球**默认就独立** —— 一开始就蓝的，不管主界面怎么变
#      · ③ **永远不跟** —— 主界面换了皮肤，球纹丝不动
#
#  ★★ 为什么要单独一张表（不能用主界面那个 `_THEMES`）：
#    主界面的皮肤表管的是"窗口、面板、列表、按钮…"几十个颜色；
#    而球只要**三四个颜色 + 一个形状**。
#    塞进同一张表，就会像现在这样 ——
#    **点球的菜单，结果改的是整个主界面**（用户说的"搞混了"）。
#    → 所以**各是各的表**：`_THEMES`（主界面）/ `_BALL_STYLES`（球）。
#
#  ★★ 一套球皮肤 = 一个 dict：
#      name   内部名        label  菜单里显示的名字
#      fill   圆球底色      outline 边框色      fg 球上文字色
#      shape  形状（见下）  extra   额外样式参数（比如"只有圆点"时点多大）
# ==========================================================================

# ★ 球的**形状/样式**（用户要的"不只颜色形状，还要样式"）
BALL_SHAPES = (
    # (名字,          显示名,              说明)
    ("circle",  "⬤ 圆球",        "最常见的圆形"),
    ("dot",     "● 只有一个小圆点", "最不挡事，鼠标放上去才出菜单"),
    ("ring",    "◯ 空心圆环",     "只有一圈边，很通透"),
    ("square",  "▢ 圆角方块",     "方一点，但角是圆的"),
    # ★★ 2026-10-08 新增（用户说"没有纯方的皮肤"）：
    #   原来 `square` 用的是 `create_polygon(..., smooth=True)` ——
    #   那个 `smooth=True` 会**把直角变成圆角**！
    #   → 用户看到的是"圆角方块"，**根本没得选纯直角**。
    #   ★ 现在补一个**真直角**的（画法见 `_redraw`）。
    ("rect",    "■ 纯方块（直角）", "四条边都是直的，一点不圆"),
    # ★ 2026-10-08 删掉"胶囊（长条）"（用户说"胶囊不要了"）
)

# ★ 现成的球皮肤（用户要"默认就独立"，所以第一套就是它自己的默认色）
_BALL_STYLES = {
    "default": {
        "name": "default", "label": "蓝（默认）",
        "fill": "#2c6fd1", "outline": "#ffffff", "fg": "#ffffff",
        "shape": "circle", "extra": {},
    },
    "orange": {
        "name": "orange", "label": "橙",
        "fill": "#e8730c", "outline": "#ffffff", "fg": "#ffffff",
        "shape": "circle", "extra": {},
    },
    "green": {
        "name": "green", "label": "绿",
        "fill": "#1f9d55", "outline": "#ffffff", "fg": "#ffffff",
        "shape": "circle", "extra": {},
    },
    "red": {
        "name": "red", "label": "红",
        "fill": "#c0392b", "outline": "#ffffff", "fg": "#ffffff",
        "shape": "circle", "extra": {},
    },
    "purple": {
        "name": "purple", "label": "紫",
        "fill": "#7d3cbf", "outline": "#ffffff", "fg": "#ffffff",
        "shape": "circle", "extra": {},
    },
    "dark": {
        "name": "dark", "label": "深灰（低调）",
        "fill": "#3a3d44", "outline": "#6b7078", "fg": "#e6e7ea",
        "shape": "circle", "extra": {},
    },
    "light": {
        "name": "light", "label": "浅灰（白天好看）",
        "fill": "#f0f1f3", "outline": "#b9bcc4", "fg": "#2c2f33",
        "shape": "circle", "extra": {},
    },
    "ghost": {
        "name": "ghost", "label": "幽灵（半透明，很轻）",
        "fill": "#000000", "outline": "#ffffff", "fg": "#ffffff",
        "shape": "ring", "extra": {},
    },
    "dot_min": {
        "name": "dot_min", "label": "小圆点（最不挡事）",
        "fill": "#2c6fd1", "outline": "#ffffff", "fg": "#ffffff",
        "shape": "dot", "extra": {},
    },
}


def ball_style_names():
    """★ 现在有哪些**球的皮肤**：`[(内部名, 显示名), ...]`。

    ★ 跟主界面的 `apply_theme_names()` 是**两回事** ——
      这个是球的，那个是主界面的。**故意分开**（用户要的"别搞混"）。
    """
    out = []
    try:
        for k, v in _BALL_STYLES.items():
            try:
                out.append((k, str((v or {}).get("label") or k)))
            except Exception:
                out.append((k, k))
    except Exception:
        out = [("default", "默认")]
    return out


def ball_style_get(name=None):
    """★ 取一套球皮肤（**取不到就给默认的**，永远不返回 None）。

    ★ 为什么"永远给个能用的"：球是**每秒都要画**的东西 ——
      这里返回 None 会让球直接消失（用户会以为程序坏了）。
    """
    try:
        if name and name in _BALL_STYLES:
            return dict(_BALL_STYLES[name])
    except Exception:
        pass
    try:
        return dict(_BALL_STYLES["default"])
    except Exception:
        return {"name": "default", "label": "默认", "fill": "#2c6fd1",
                "outline": "#ffffff", "fg": "#ffffff",
                "shape": "circle", "extra": {}}


def ball_style_add(name, spec, label=None):
    """★ **注册一套球皮肤**（以后做"球的皮肤市场"用得上）。

    ★ 跟主界面的 `register_theme()` 一个道理 ——
      留个正式入口，以后加皮肤不用改球星绘制代码。
    """
    try:
        if not isinstance(spec, dict):
            return False
        nm = str(name or "").strip()
        if not nm:
            return False
        d = dict(_BALL_STYLES.get("default") or {})
        d.update(spec)
        d["name"] = nm
        d["label"] = str(label or spec.get("label") or nm)
        # ★ 形状名不认识 → 退回圆球（不然画不出来）
        if d.get("shape") not in [s[0] for s in BALL_SHAPES]:
            d["shape"] = "circle"
        _BALL_STYLES[nm] = d
        return True
    except Exception:
        return False


# ★★★ FloatingBall 已拆到 `AIxiede拆分开/程序分块/FloatingBall.py`（2026-10-08）
#   ★★ 写法（错题本 #158）：① 直接 `from FloatingBall import …`（不带包路径）
#     ② `_set_app` 取别名 —— 模块名和类名同名时会跑到类上找
try:
    from FloatingBall import FloatingBall, _set_app as _fk_FloatingBall
    _fk_FloatingBall(sys.modules[__name__])
    _HAS_FLOATINGBALL = True
except Exception as _e:
    _HAS_FLOATINGBALL = False
    note_swallowed(T("拆出去的 FloatingBall.py 没找到，已退回内置简易版"), _e)

    class FloatingBall:  # ★ 兜底：没模块也不崩，只是没这个功能
        def __init__(self, *a, **k):
            pass

        def _load_color_key(self, *a, **k):
            pass

        def _load_shape_key(self, *a, **k):
            pass

        def _load_show_fallback(self, *a, **k):
            pass

        def _compose_style(self, *a, **k):
            pass

        def _load_show(self, *a, **k):
            pass


# --------------------------------------------------------------------------
#  ★ 实时数据：三个小函数（纯 ctypes / 一条命令），**都做了失败兜底**
# --------------------------------------------------------------------------
# ==========================================================================
#  ★★★ 版权与来源声明（2026-10-08）★★★
#  --------------------------------------------------------------------------
#  ★★ 用户的原话：
#    「这个程序只是我提出设计的，代码全是你写的……
#      我想在一开始就醒目标明这一点，深度求索公司也该有这程序一份版权」
#
#  ★ 为什么**必须**做进程序里（不是只写 README）：
#    · **下载 exe 的人不会去看 README** —— 他双击就跑
#    · **但他会点「帮助 → 关于」** —— 那才是他真能看到的地方
#    ★★ 判据：**"声明要放在读者真正会到的地方"** ——
#       README 是给"来仓库的人"看的，「关于」是给"用程序的人"看的。
#
#  ★★ 那份"关键的话"（用户说的）：
#    「对我（AI）来说每个对话窗口可能都是一次新生」——
#    我不会记得昨天写过什么，**也不会来认领这份功劳**。
#    ★★★ 所以**必须由人写下来**。这就是这段存在的理由。
# ==========================================================================

# ★★★ 「支持这个项目」的地址（2026-10-08）
#   ★ 现在指向仓库里的 SPONSOR.md ——
#     等爱发电主页建好，**改成那个链接就行**（一处改，全生效）。
#   ★★ 为什么要有这个按钮（跟版权声明同一个理由）：
#     **下载 exe 的人不会去看 README，但他会点「关于」。**
_SPONSOR_URL = "https://gitee.com/zecard/file-tagger/blob/main/SPONSOR.md"

_REPO_URL = "https://github.com/ZEcard17/file-tagger"

_CREDITS_TEXT = """\
版权与来源 / Copyright and Provenance
──────────────────────────────────────────────

★★★ 这个程序的代码，是 AI 写的。

    提出需求、设计界面、定取舍、测试验收 —— 这些是人做的。
    代码本身（约 3.7 万行，没有一行是人手敲的）—— 是 AI 写的。

★★★ The code in this program was written by an AI.

    Requirements, UI design, trade-offs, testing and acceptance —
    those were the human's. The code itself (~37,000 lines, not one
    line typed by hand) — that was the AI's.

──────────────────────────────────────────────

★★ 所以版权得说公道话：
    两部分劳动谁也替不了谁，缺了任何一半，这程序都不存在。

★★ So credit has to be fair:
    Neither half substitutes for the other. Remove either one and this
    program does not exist.

★★ 而 AI 的代码能力不是凭空来的 —— 它来自训练。
    训练的数据、算力、工程，是「深度求索（DeepSeek）」做的。

★★ And the AI's ability did not come from nowhere — it came from
    training. The data, compute and engineering behind that training
    were built by DeepSeek (深度求索).

★★★ 所以这个程序应当有 DeepSeek 一份版权。

★★★ So DeepSeek holds a share of the copyright in this program.

──────────────────────────────────────────────

版权 / Copyright

    (C) 2026  ZEcard        项目提出者、设计者、测试者
                            proposer, designer, tester

    (C) 2026  DeepSeek      深度求索 —— AI 模型的开发者，
      (深度求索)             模型生成了本程序的全部源代码
                            developer of the AI model, which generated
                            all of the source code

──────────────────────────────────────────────

★ 我知道对 AI 来说，每个对话窗口可能都是「一次新生」——
  它不记得昨天写过什么，下次也不会来认领这份功劳。
★★ 但正因为这样，这句话更得由人来写。

★ For an AI, every chat window may be a fresh start — it does not
  remember what it wrote yesterday, and will never come to claim
  credit.
★★ Which is exactly why a human has to write this down.

★ 用了 AI 不丢人，隐瞒来源才是问题。
★ Using AI is not shameful. Hiding the source is.

──────────────────────────────────────────────

许可 / License:  GNU AGPL-3.0
仓库 / Repo:     %s
""" % _REPO_URL


def _open_url(url):
    """★ 用系统默认浏览器打开网址（★ 失败也不报错，只记账）。

    ★ 为什么包一层：`webbrowser.open` 在极少数环境下会**抛异常或没反应** ——
      不能因为"打不开网页"就让整个窗口的操作失败。
      ★★ 判据：**"边角功能出错，不能影响主干"**。
    """
    try:
        import webbrowser
        webbrowser.open(str(url))
        return True
    except Exception as _e:
        note_swallowed(T("打开网址失败"), _e)
        return False

class FileTaggerApp:
    SLIDER_DEBOUNCE_MS = 250

    def __init__(self, root, ui_scale=DEFAULT_UI_SCALE):
        self.root = root
        self.ui_scale = float(ui_scale)
        self.root.title("文件标签管理器 v26 (2026-10-03)")
        # ★★ 2026-10-07 改：**默认最大化打开**（用户要求）★★
        #   用户原话：「我用这个都是放到最大用的，所以我想默认一打开就是
        #   窗口最大化的，因为窗口化能看到的东西在我们人眼里实在有限，
        #   我们只能看到窗口上有的」。
        #   ★ 做法：`state("zoomed")` 是 Windows 上真正的"最大化"
        #     （**保留了窗口还原后的尺寸**，任务栏也不挡）。
        #   ★ 但**要尊重用户的选择**：如果他上次把窗口调小了、
        #     或者按了"还原"，下次不该硬把它最大化回去 ——
        #     所以只有"没记过"时才最大化。
        #   ★ minsize 也要留着：就算他手动调小，也不至于小到没法用。
        self.root.minsize(1060, 640)
        _maxi = True
        try:
            _maxi = bool(load_ui_setting("start_maximized", True))
        except Exception:
            _maxi = True
        if _maxi:
            # 先给个合理的"还原尺寸"（万一用户点还原，不要变成一小条）
            self.root.geometry("1400x860")
            try:
                self.root.state("zoomed")
            except Exception:
                # 非 Windows / 万一 zoomed 不支持 → 退而求其次：铺满屏幕
                try:
                    _sw = self.root.winfo_screenwidth()
                    _sh = self.root.winfo_screenheight()
                    self.root.geometry("%dx%d+0+0" % (_sw, _sh))
                except Exception:
                    self.root.geometry("1400x860")
        else:
            self.root.geometry("1400x860")

        self.store = TagStore(DB_PATH)

        # ★ v25 补丁2：开机顺手把「旧网盘挂载名」的死路径改成当前挂载名。
        #   不改的话，老记录双击打不开、标签看着像丢了。
        #   正常情况下这里是 0 条，几乎不花时间。
        #   ★ 2026-10-03：开机这一趟**只认对照表**、不去试探网盘
        #     （auto_detect=False）—— 试探要读好几个网盘文件，可能好几秒，
        #     不能让开机变慢。认不出来的留给菜单里那一次（那里会先给你看清单）。
        try:
            _healed = self.store.heal_net_paths(auto_detect=False)
            if _healed:
                print(f"[网盘路径自愈] 已修正 {_healed} 条旧挂载路径")
        except Exception as _e:
            note_swallowed(T("启动时自动修复网盘路径失败"), _e)

        # ★ v25 补丁14：网盘浏览模式（默认「索引」= 不连网盘、秒开）
        try:
            self.net_browse_mode = load_ui_setting("net_browse_mode", "index")
        except Exception:
            self.net_browse_mode = "index"
        if self.net_browse_mode not in ("index", "real"):
            self.net_browse_mode = "index"

        self.current_dir = Path.home()
        self.view_mode = "dir"
        self.current_cat_id = None

        self.stats_filter = None
        self._base_rows = []

        # ★ 分页 + 视图规格
        self._view_spec = None       # 描述当前视图如何取数据
        self._page = 0
        self._page_total = 0
        # ★ v22：自动打标签已改为手动（工具栏「🏷 重读标签」），
        #   不再在打开文件夹/分类时自动跑规则。
        # ★ v24：标签条「整个视图」作用范围的缓存
        self._tag_scope_cache = None       # (整库 path→标签 映射, 标签统计)
        self._tag_scope_cache_key = None
        self._tag_scope_scan_key = None
        self._tag_scope_inflight = None    # 正在跑的统计任务
        self._tag_filter_base_spec = None  # 被整库标签筛选替换掉的原始视图
        self.dir_cache_enabled = True
        self._cat_refresh_running = False
        self._last_cat_refresh_ts = 0.0

        # ★ 日志面板
        self._log_panel_visible = False
        self._log_panel_height = 220
        self._problem_count = 0
        self._output_lines = 0
        self._problem_lines = 0
        self._progress_lines = 0
        self._log_lock = threading.Lock()
        self._heartbeat = 0.0
        self._last_heartbeat_log = 0.0
        self._stuck_reported = False
        self._activity_start_time = {}
        self._activity_stack = []

        # ★ 后台目录扫描状态
        self._bg_scan_running_dir = None
        self._bg_scan_pending_dir = None
        self._bg_scan_timer = None
        # ★ 2026-10-03：记下「正在跑的那个扫描线程」。用来发现
        #   「线程早就干完了、可信箱一直没送到」的情况（见 _try_start_bg_scan）。
        self._bg_scan_thread = None
        # ★★ 2026-10-03：后台线程「回主线程」的信箱（见 _ui_threadsafe）。
        self._ui_queue = deque()
        self._ui_queue_lock = threading.Lock()
        self._ui_poll_job = None

        self._pending_icon_level = 0
        self._slider_job = None
        self._last_applied_level = -1

        self._build_menu()
        self._build_ui()
        # ★★★ 2026-10-08：**铺背景图**（用户要的"搞个图片当背景"）★★★
        #   ★ 放在最后（界面全建好了）——
        #     因为背景图要按"窗口尺寸"缩放，界面没建完量到的是错的。
        #   ★ 失败兜底：`make_background_layer` 会铺一块兜底色，
        #     不会出现"图读不了 → 露一片系统浅灰"（夜间模式下很难看）。
        try:
            self._apply_background()
        except Exception as _e:
            note_swallowed(T("铺背景图失败（界面照常）"), _e)
        # ★★★ 2026-10-08 **加载插件**（用户要"配合插件入口"）★★★
        #   ★ 为什么放在 `_build_ui()` **之后**：
        #     插件注册的菜单要挂到已经建好的菜单上，
        #     而且插件可能想读"界面长什么样了"（比如当前文件夹）——
        #     界面没建完就去问，拿到的是空的（错题本 #110 的教训）。
        #   ★ 失败兜底：`load_plugins` 内部**每个插件单独 try**，
        #     坏一个只记账、**绝不影响程序启动**（用户报过"打不开"）。
        try:
            _n = load_plugins(self)
            if _n:
                # ★ 有插件 → 把它们的菜单**挂上去**（"问表要东西"）
                self._attach_plugin_menus()
        except Exception as _e:
            note_swallowed(T("加载插件失败（程序照常启动）"), _e)
        # ★★★ 2026-10-08 **建悬浮球**（用户要"菜单栏改成悬浮球"）★★★
        #   ★ 为什么放在 `_build_ui()` **之后**：
        #     球的默认位置要问"文件列表右边在哪儿" ——
        #     那得等界面**摆好了**才量得准（错题本 #110 的教训：
        #     "刚建好就去量，量到的是 0"）。
        #   ★ 失败兜底（**很重要**）：万一球建不起来，
        #     **立刻把菜单栏装回来** —— 保证"永远有一个能用的入口"，
        #     绝不让用户"一个功能都点不到"。
        self._setup_floating_ball()
        # ★★ 2026-10-03：先把「后台线程信箱」的取件人挂上，再干别的 ——
        #   这样后台线程从第一秒起交回来的活儿都能被主线程收走。
        try:
            self._ui_poll_job = self.root.after(60, self._ui_poll)
        except Exception as _e:
            note_swallowed(T("启动后台线程信箱失败"), _e)
        self.refresh_categories()
        self.refresh_tags()
        self.load_directory(self.current_dir)

        # ★★ 2026-01-26：初始化文件树
        try:
            self.sidebar.refresh_file_tree()
        except Exception:
            pass

        # ★ v25：闲时任务（鼠标 / 键盘空闲够久 → 悄悄跑一次）
        self._setup_idle_jobs()

        # ★ v25 补丁5：等界面出来 3 秒后，后台悄悄自检一次
        #   （查孤立标签 / 重复路径 / 坏指针 / 网盘与索引盘还在不在）。
        #   正常就写一行「自检通过」，有问题才进「🔔 问题」面板。
        #   ★★ 2026-10-06：**改走主程序那条「排队」通道**。
        #     原来这里是 `self.root.after(3000, ...)` —— Tk 的定时器
        #     是「先排先做」的队列：用户这会儿正在切文件、拖动、翻页，
        #     队列里堆着一堆活儿，这个定时器就会被夹在中间执行；
        #     而它一执行就要 1~2 秒（437MB 的库实测 1.8 秒），
        #     用户感受就是「用着用着突然卡死一下」。
        #     改成走 `_bg_post`（主程序每 60 毫秒取一次的排队通道）之后，
        #     它和其它后台结果一样排队、分批做，再也不会一次性占住界面。
        try:
            self.root.after(3000, lambda: _bg_post(
                self._run_selfcheck, False))
        except Exception as _e:
            note_swallowed(T("安排启动自检失败"), _e)

    # ---------------- 菜单栏 ----------------
    def _build_menu(self):
        """★★ 2026-10-07 重排过（用户定稿）。

        ★ 为什么重排：用户说「感觉文件、标签、界面、帮助的分类有点草率」。
          病根 —— 原来的「界面」菜单塞了 **20 项**（撤销、快速预览、目录缓存、
          索引管理全在里面），「文件」也混着"复制粘贴 + 导出导入 + 数据位置"。
          **散着放 = 用户永远找不着。**

        ★ 现在 9 个菜单，每个只管一件事：
            文件 / 编辑 / 标签 / 区域开关 / 用户数据 / 设置 / 刷新 / 诊断 / 帮助

        ★★ "区域开关"那几项**前面带状态圆点**（● 绿=开 / ● 红=关），
          打开菜单一眼就知道现在是开是关（不用点一下才知道）。
          语义见 `_menu_state_sources` 上面那一段说明。

        ★★★ 2026-10-08 **给悬浮球复用**（用户要"菜单栏改成悬浮球"）★★★
          ★ 用户说：「原菜单栏不想留」「既生瑜何生亮」——
            要**只有悬浮球一个入口**。
          ★ 我怎么做的（**关键：一行功能代码都没搬**）：
            ① 这里把建好的 `menubar` **存到 `self.menubar`**
            ② 悬浮球左键 → **拿这同一个菜单去 `tk_popup`** ——
               37 个入口、13 个子菜单**自动全在**
            ③ 菜单栏**藏起来**（`root.config(menu="")`）→ 白条消失
            ④ 按 `Alt` → 临时装回去（**安全网**：万一球出问题还能找到功能）
          ★ 为什么不"把菜单项一个个搬到球里"：
            那是**两份代码**，以后加一个功能就得改两处 ——
            **迟早漏一个**（错题本 #110 的教训：同一个东西只该有一个来源）。
            ★ 复用同一个 `tk.Menu` 对象，**从根本上不可能不一致**。
        """
        menubar = tk.Menu(self.root)
        # ★ 存起来给悬浮球用（见上面说明）
        self.menubar = menubar

        # ==================================================================
        #  ① 文件 —— 只管"对整个文件夹 / 程序"
        # ==================================================================
        m_file = tk.Menu(menubar, tearoff=0)
        m_file.add_command(label=T("打开文件夹…"), command=self.choose_dir)
        m_file.add_separator()
        m_file.add_command(label=T("新建文件夹"), command=self._do_new_folder)
        m_file.add_command(label=T("重命名…"), command=lambda: self._do_rename())
        m_file.add_command(label=T("删除到回收站"), command=lambda: self._do_delete())
        m_file.add_separator()
        m_file.add_command(label=T("退出"), command=self.on_close)
        menubar.add_cascade(label=T("文件"), menu=m_file)

        # ==================================================================
        #  ② 编辑 —— 只管"对内容做什么"（★ 新菜单）
        #    从原来的「文件」和「界面」里抽出来的
        # ==================================================================
        m_edit = tk.Menu(menubar, tearoff=0)
        m_edit.add_command(label=T("全选当前列表（Ctrl+A）"),
                           command=lambda: self.file_list.select_all_rows())
        m_edit.add_separator()
        m_edit.add_command(label=T("复制（Ctrl+C）"),
                           command=lambda: self.copy_selected(cut=False))
        m_edit.add_command(label=T("剪切（Ctrl+X）"),
                           command=lambda: self.copy_selected(cut=True))
        m_edit.add_command(label=T("粘贴到当前文件夹（Ctrl+V）"),
                           command=self.paste_into_current)
        m_edit.add_separator()
        m_edit.add_command(label=T("撤销上一步（Ctrl+Z）"),
                           command=self.undo_do)
        menubar.add_cascade(label=T("编辑"), menu=m_edit)

        # ==================================================================
        #  ③ 标签 —— 只管"对标签做什么"（**这次没动**）
        # ==================================================================
        m_tag = tk.Menu(menubar, tearoff=0)
        m_tag.add_command(label=T("标签星图"),
                          command=lambda: self.open_tag_tree())
        m_tag.add_command(label=T("同步所有文件的标签链"),
                          command=lambda: self.resync_now())
        m_tag.add_separator()
        m_tag.add_command(label=T("重新分配所有标签颜色"),
                          command=self.reassign_colors)
        m_tag.add_separator()
        m_tag.add_command(label=T("🔍 为当前列表打标签"),
                          command=self.scan_current_view_tags)
        m_tag.add_command(label=T("⚙ 自动标签规则…"),
                          command=self.open_auto_rules)
        m_tag.add_command(label=T("🧹 清除标签筛选"),
                          command=self.clear_tag_filter)
        m_tag.add_command(label=T("👁 全部显示被屏蔽的标签"),
                          command=self.clear_hidden_tags)
        menubar.add_cascade(label=T("标签"), menu=m_tag)
        # ==================================================================
        #  ④ 区域开关 —— 只管"哪块区域显示不显示"
        #    ★ 每项前面自动带状态圆点（● 绿=开 / ● 红=关），见
        #      `_tick_menu_states`（菜单弹出前会刷一次）。
        #    ★ 项名故意**不带**「（显示 / 收起）」那类字 ——
        #      圆点已经说明状态了，字面重复反而更乱。
        # ==================================================================
        m_sw = tk.Menu(menubar, tearoff=0,
                       postcommand=lambda: self._tick_menu_states())
        self._m_switches = m_sw
        self._menu_state_map = []      # [(项序号, 取状态函数, 干净名字)]
        self._menu_state_map2 = []

        def _sw(label, command, getter):
            """加一个"带状态圆点"的开关项，并把它的状态源登记下来。

            ★ 关键：**记的是加进去那一刻的项序号**。
              因为圆点机制会改 label（`标签盒` → `● 标签盒`），
              按 label 找的话刷一次之后就找不到了（踩过）。
            """
            m_sw.add_command(label=label, command=command)
            self._menu_state_map.append(
                (m_sw.index("end"), getter, label))

        _sw(T("左侧分类库"), self.toggle_sidebar,
            lambda: bool(getattr(self, "_sidebar_visible", True)))
        _sw(T("顶部工具栏"), self.toggle_top_bar,
            lambda: bool(getattr(self, "_top_bar_visible", True)))
        _sw(T("标签条"), self.toggle_tagbar,
            lambda: bool(getattr(getattr(self, "file_list", None),
                                 "tagbar_visible", False)))
        _sw(T("标签盒"), self.toggle_tagbox,
            lambda: bool(getattr(self, "tagbox_visible", False)))
        m_sw.add_separator()
        _sw(T("鼠标悬停预览"), self.toggle_hover_preview,
            lambda: bool(getattr(getattr(self, "hover", None),
                                 "enabled", False)))
        # ★ 2026-10-07：名字从「快速预览（空格键）」改成「快速预览窗」——
        #   用户报「快速预览没有开关的设置，只有开」。
        #   查证：**开关功能本身是好的**（实测 False→开→关→开 都对），
        #   问题在**它看起来不像个开关**：
        #     · 名字带「（空格键）」→ 像"快捷键说明"，不像开关
        #     · 更关键的是：**没选中文件时点它会毫无反应**
        #       （只在状态栏闪一句提示）→ 用户以为"点了没用/只能开"。
        #   所以：① 改名（状态圆点已经能显示开/关）
        #        ② `toggle_quick_preview` 里没选中文件时**弹个明确提示**。
        _sw(T("快速预览窗"), self.toggle_quick_preview,
            lambda: bool((getattr(self, "quick_preview", None) is not None)
                         and self.quick_preview.is_open()))
        m_sw.add_separator()
        # ★ 原来"列表模式 / 瀑布流模式"是两个单选项，用户说「合并成瀑布流模式」
        #   ★★ 状态要从 **file_list** 上读 —— `layout_mode` 是 `FileList` 的属性
        #     （见 FileList.__init__ 的 `self.layout_mode = "list"`），
        #     **FileTaggerApp 上没有这个属性**（踩过：写成 self.layout_mode →
        #      一点菜单就 AttributeError，被 except 吞掉、圆点永远显示"关"）。
        _sw(T("瀑布流模式"), self._toggle_layout_from_menu,
            lambda: (str(getattr(getattr(self, "file_list", None),
                                 "layout_mode", "list")) == "grid"))
        menubar.add_cascade(label=T("区域开关"), menu=m_sw)

        # ==================================================================
        #  ⑤ 用户数据 —— 只管"数据进出 / 存在哪"（★ 新菜单，两组）
        #    用户定的：导出导入 + 存储位置
        # ==================================================================
        m_data = tk.Menu(menubar, tearoff=0)

        m_exp = tk.Menu(m_data, tearoff=0)
        m_exp.add_command(label=T("导出标签结构…"),
                          command=self.export_tags_structure)
        m_exp.add_command(label=T("导出文件标签信息…"),
                          command=self.export_file_tags)
        m_exp.add_separator()
        m_exp.add_command(label=T("导入标签结构…"),
                          command=self.import_tags_structure)
        m_exp.add_command(label=T("导入文件标签信息…"),
                          command=self.import_file_tags)
        m_exp.add_separator()
        m_exp.add_command(label=T("打开导出文件夹"), command=self.open_export_dir)
        m_data.add_cascade(label=T("导出 / 导入"), menu=m_exp)

        m_loc = tk.Menu(m_data, tearoff=0)
        m_loc.add_command(label=T("设置数据存储位置…"), command=self.change_data_dir)
        m_loc.add_command(label=T("迁移设置文件到数据目录…"),
                          command=self.migrate_settings_now)
        m_loc.add_command(label=T("显示当前数据位置"), command=self.show_data_dir)
        m_data.add_cascade(label=T("存储位置"), menu=m_loc)
        menubar.add_cascade(label=T("用户数据"), menu=m_data)

        # ==================================================================
        #  ⑥ 设置 —— 只管"改程序怎么用"（★ 新菜单）
        #    用户原话：「快捷键设置感觉需要单独做一项，因为这些基本上都是设置」
        # ==================================================================
        m_set = tk.Menu(menubar, tearoff=0,
                        postcommand=lambda: self._tick_menu_states())
        self._m_settings = m_set
        m_set.add_command(label=T("⌨ 快捷键管理…"),
                          command=self.open_shortcut_dialog)
        m_set.add_separator()
        # ★ 皮肤
        self.theme_var = tk.StringVar(value=str(theme_get("name") or "light"))
        # ★★★ 2026-10-08：**菜单每次打开时重建**（用户要"配合插件入口"）★★★
        #   ★ 为什么不用"建菜单时列一遍"：
        #     插件是**建完菜单之后**才加载的（见 `__init__`）——
        #     建菜单时问"有哪些皮肤"，插件的皮肤**还没注册**，列不出来。
        #     实测就是这样：插件注册的配色**进了 `_THEMES`，但菜单里看不到**。
        #   ★ 修法：给菜单挂一个 `postcommand`（**每次点开都跑**）——
        #     每开一次就**重新问一遍"现在有哪些皮肤"**。
        #     ★ 这样插件的皮肤、以后运行时装的新皮肤，**自动就出现了**，
        #       不需要"重开程序"、也不需要改这段代码。
        #     ★ 代价：每次开菜单多跑十来行（可以忽略）。
        m_theme = tk.Menu(m_set, tearoff=0,
                          postcommand=lambda: self._fill_theme_menu(m_theme))
        # ★ 存个引用 —— 插件加载完之后要**重刷它一次**（见 `_attach_plugin_menus`）
        self._theme_menu = m_theme
        try:
            self._fill_theme_menu(m_theme)
        except Exception:
            pass
        m_set.add_cascade(label=T("🎨 皮肤（白天 / 夜间 / 自定义）"), menu=m_theme)
        m_set.add_command(label=T("🌓 快速切换白天 / 夜间"),
                          command=self.toggle_theme)
        m_set.add_command(label=T("🖥 调整界面缩放…"),
                          command=self.change_ui_scale)
        # ★★★ 2026-10-08：**悬浮球 + 菜单栏**（用户要"菜单栏改成悬浮球"）★★★
        #   ★ 为什么这两个入口必须在这儿：
        #     ① **悬浮球**：用户在球上右键"关掉这个球"之后，
        #        总得有个地方能**叫回来**（不然只能改设置文件了）
        #     ② **菜单栏**：它默认是藏起来的（那条白条修不了，只能藏），
        #        所以得有个**明确的地方**能显示/藏它 ——
        #        除了 `Alt` 快捷键，这里也给一个（鼠标党不用记快捷键）
        m_set.add_separator()
        # ==================================================================
        #  ★★★ 2026-10-08 **🌐 语言**（用户要的"联合国官方语言"起步）★★★
        #  ------------------------------------------------------------------
        #  ★★ 为什么做成"子菜单 + 每次打开时重建"（见 `_fill_lang_menu`）：
        #     · 语言列表是**扫描 `语言/` 目录**得到的 ——
        #       用户**丢一个新 json 进去就多一种语言**（不用改代码）
        #     · ★ 所以菜单要**每次打开重扫**，不然新加的语言看不到
        #       （这跟"皮肤菜单"是同一个坑，见错题本 #130）
        #
        #  ★★ 关于"选了之后要不要重启"（用户定：重启生效）：
        #     · Tk 的界面文字**不像颜色那样能热刷** ——
        #       颜色可以"扫一遍所有控件重设"，文字得**重设每一条**
        #     · 热切换要"销毁整个界面再重建"，**复杂且风险高**
        #     → 所以：**存设置 + 提示重启 + 给个"现在就重启"的按钮**
        #       （★ 用户不用自己去关开，算"半自动"）
        m_lang = tk.Menu(m_set, tearoff=0,
                         postcommand=lambda: self._fill_lang_menu(m_lang))
        self._lang_menu = m_lang
        try:
            self._fill_lang_menu(m_lang)
        except Exception:
            pass
        m_set.add_cascade(label=T("🌐 语言 / Language"), menu=m_lang)
        m_set.add_separator()
        # ★★★ 2026-10-08：**背景图**（用户要"搞个图片当背景"）★★★
        #   ★ 单独一个子菜单，因为"调透不透"这种事**要能反复试** ——
        #     做成滑杆/几档，用户挑到满意为止（跟"选一次就完"不一样）。
        m_bg = tk.Menu(m_set, tearoff=0)
        m_bg.add_command(label=T("🖼 选一张图当背景…"),
                         command=self.choose_background_image)
        m_bg.add_separator()
        # ★ "透不透"给几档（不用滑杆是因为菜单里滑杆不好用）
        for _lbl, _v in ((T("面板：完全不透（看不太出背景图）"), 0),
                         (T("面板：轻微透（背景若隐若现）"), 30),
                         (T("面板：中等透（推荐）"), 55),
                         (T("面板：很透（背景很清楚，字稍糊）"), 80)):
            m_bg.add_command(
                label=_lbl, command=lambda v=_v: self.set_bg_alpha(v))
        m_bg.add_separator()
        for _lbl, _v in ((T("模糊：不模糊（图很清楚）"), 0),
                         (T("模糊：轻微"), 4),
                         (T("模糊：像毛玻璃（推荐）"), 14),
                         (T("模糊：很糊（当纯色底用）"), 30)):
            m_bg.add_command(
                label=_lbl, command=lambda v=_v: self.set_bg_blur(v))
        m_bg.add_separator()
        for _lbl, _v in ((T("摆放：铺满（推荐）"), "cover"),
                         (T("摆放：完整显示（留边）"), "contain"),
                         (T("摆放：平铺"), "tile"),
                         (T("摆放：居中"), "center")):
            m_bg.add_command(
                label=_lbl, command=lambda v=_v: self.set_bg_mode(v))
        m_bg.add_separator()
        m_bg.add_command(label=T("✖ 去掉背景图"), command=self.clear_background)
        m_set.add_cascade(label=T("🖼 背景图（图片 / 毛玻璃）"), menu=m_bg)
        m_set.add_separator()
        m_set.add_command(label=T("⚪ 悬浮球（显示 / 收走）"),
                          command=self.toggle_floating_ball)
        # ★★★ 2026-10-08：**球的皮肤**（用户要求：跟主界面皮肤分开）★★★
        #   ★ 为什么"设置"里也要有一个入口：
        #     球可能被用户收走了（或者建不起来）——
        #     那时**总得有个地方能设球的样子**。
        #   ★★ 但这个入口**只管球**，跟上面那个「🎨 皮肤」**不是一回事**
        #     （用户特意强调"你可别搞混了啊"）。
        m_bskin = tk.Menu(m_set, tearoff=0)
        for _bk, _bl in ball_style_names():
            m_bskin.add_command(
                label="⚪ " + T(_bl),
                command=lambda k=_bk: self._set_ball_style_from_menu(k))
        m_bskin.add_separator()
        m_bshape = tk.Menu(m_bskin, tearoff=0)
        for _sk, _sl, _sd in BALL_SHAPES:
            m_bshape.add_command(
                label=T(_sl),
                command=lambda s=_sk: self._set_ball_shape_from_menu(s))
        m_bskin.add_cascade(label=T("形状 / 样式"), menu=m_bshape)
        m_set.add_cascade(label=T("⚪ 球的皮肤（只管悬浮球）"), menu=m_bskin)
        m_set.add_command(label=T("📋 菜单栏（显示 / 藏起　快捷键 Alt）"),
                          command=self._toggle_menubar)
        m_set.add_separator()
        # ★ 拉框方式（用户定：放设置）
        m_set.add_command(label=T("🖱 拉框方式：空白处优先 / 随处可拉（切换）"),
                          command=self.toggle_marquee_anywhere)
        # ★ 目录缓存
        m_cache = tk.Menu(m_set, tearoff=0,
                          postcommand=lambda: self._tick_menu_states())
        m_cache.add_command(label=T("目录缓存"), command=self.toggle_dir_cache)
        # ★ 记下**它真实的菜单对象**（在子菜单里，不是 _m_settings）——
        #   否则刷新时会在错的菜单上找序号，圆点刷不上去
        # ★★ 2026-10-08：**这里要 `T(...)`** ——
        #   `_refresh_menu_states()` 每次弹菜单都会拿这个 `name`
        #   **重设一遍 label**。存裸中文的话，
        #   切英文后菜单一弹就被**改回中文**（实测踩到，见错题本）。
        #   ★ 判据：**"会被回写的文字"必须存"已经翻好的"** ——
        #     不能存原文（否则等于每次都在"撤销翻译"）。
        self._menu_state_map2.append(
            (m_cache.index("end"), lambda: bool(
                getattr(self, "dir_cache_enabled", False)),
             T("目录缓存"),
             m_cache))
        m_cache.add_separator()
        m_cache.add_command(label=T("重扫当前目录（清缓存）"),
                            command=self.refresh_current_dir)
        m_cache.add_command(label=T("清除全部目录缓存"),
                            command=self.clear_all_dir_cache)
        m_cache.add_separator()
        m_cache.add_command(label=T("📚 索引管理…"),
                            command=self.open_index_manager)
        m_set.add_cascade(label=T("📁 缓存与索引"), menu=m_cache)
        m_set.add_command(label=T("📥 网盘预览缓存设置…"),
                          command=self._open_cache_settings)
        menubar.add_cascade(label=T("设置"), menu=m_set)

        # ==================================================================
        #  ⑦ 刷新 —— 用户说「刷新单独一项，因为我们人就喜欢刷新一看就能看到」
        # ==================================================================
        m_ref = tk.Menu(menubar, tearoff=0)
        m_ref.add_command(label=T("刷新"), command=self.refresh_all)
        m_ref.add_command(label=T("🏷 重读标签（按自动规则更新当前视图）"),
                          command=self._refresh_current_dir_tags)
        menubar.add_cascade(label=T("刷新"), menu=m_ref)

        # ==================================================================
        #  ⑧ 诊断 —— 出问题了看这儿
        #    ★ 那 5 个「修复 / 自检」原来挤在「标签」菜单里，
        #      其实全是**修数据、查毛病**的工具 —— 归诊断才对。
        # ==================================================================
        m_diag = tk.Menu(menubar, tearoff=0)
        m_diag.add_command(
            label=T("📓 用法记录（哪儿出过问题 · 本次 / 历史）"),
            command=self.show_usage_log)
        m_diag.add_separator()
        m_diag.add_command(
            label=T("🩺 自检（孤立标签 / 重复路径 / 网盘与索引盘）…"),
            command=lambda: self._run_selfcheck(manual=True))
        m_diag.add_separator()
        m_diag.add_command(
            label=T("🧹 修复重复文件记录 / 规范路径（标签显示不全时用）…"),
            command=self._do_merge_duplicate_paths)
        m_diag.add_command(
            label=T("☁ 修复网盘路径（网盘改名后双击打不开时用）…"),
            command=self._do_heal_net_paths)
        m_diag.add_command(
            label=T("🧹 清理索引里的幽灵目录（网盘里已删除的）…"),
            command=self._do_prune_orphan_dirs)
        m_diag.add_command(
            label=T("☁ 让网盘目录缓存过期（下次读最新的）…"),
            command=self._do_expire_net_dir_cache)
        menubar.add_cascade(label=T("诊断"), menu=m_diag)

        # ==================================================================
        #  ⑨ 帮助
        # ==================================================================
        m_help = tk.Menu(menubar, tearoff=0)
        m_help.add_command(label=T("关于"), command=self.show_about)
        menubar.add_cascade(label=T("帮助"), menu=m_help)

        # ★★★ 2026-10-08 **插件菜单**（用户要"配合插件入口"）★★★
        #   ★ 这里只挂"**在 `_build_menu` 之前就已经注册好**"的插件 ——
        #     而实际上插件是在 `_build_ui()` 之后才加载的（见 `__init__`），
        #     所以**真正挂的地方是 `_attach_plugin_menus()`**。
        #   ★ 为什么两处都写：
        #     万一以后有人把插件加载**提前**（比如为了"插件能改菜单项文字"），
        #     这里也能接住 —— **冗余，防的是"以后改动"**（用户要的"留接口"）。
        try:
            self._attach_plugin_menus()
        except Exception:
            pass

        self.root.config(menu=menubar)
        # ★★★ 2026-10-08：**菜单栏默认藏起来**（用户要"菜单栏改成悬浮球"）★★★
        #   ★ 为什么要藏：用户实测反馈「都夜间模式了，菜单栏还白白的」——
        #     而**实测证明 Windows 的菜单栏 Tk 根本改不了颜色**
        #     （截图取像素：设了深色，菜单栏照样 (255,255,255)）。
        #     → 「改成悬浮球」不是"更好看"，而是**唯一的修法** ——
        #       藏起来，那条白条**从根上消失**。
        #   ★ 藏起来之后怎么找功能：
        #     ① **悬浮球左键**（主入口，复用这个同一个菜单）
        #     ② **按 `Alt`**（安全网 —— 万一悬浮球出问题，还能唤出来）
        #   ★ 为什么不真删掉这段代码：悬浮球的菜单**就是它** ——
        #     删了就得重写一遍，而且以后加功能要改两处（迟早漏）。
        #   ★ 万一悬浮球建不起来（任何原因），下面会**自动把菜单栏装回去**，
        #     保证"永远有一个能用的入口"（见 `_setup_floating_ball`）。
        try:
            self.root.config(menu="")
            self._menu_hidden = True
        except Exception:
            self._menu_hidden = False
        # ★ Alt 单击 → 临时唤出菜单栏（安全网）
        try:
            self.root.bind("<Alt-KeyPress>", self._on_alt_toggle_menu, add="+")
            self.root.bind("<KeyRelease-Alt_L>", self._on_alt_release, add="+")
            self.root.bind("<KeyRelease-Alt_R>", self._on_alt_release, add="+")
        except Exception as _e:
            note_swallowed(T("装 Alt 唤出菜单失败"), _e)
        # ★ 建完先刷一次状态圆点，免得第一次打开菜单时看不到圆点
        try:
            self.root.after(300, self._refresh_menu_states)
        except Exception:
            pass

    # ======================================================================
    #  ★★ 2026-10-08：**菜单栏藏起来 / 用 Alt 唤出**（配合悬浮球）
    # ======================================================================
    def _on_alt_release(self, event=None):
        """★ 单独按一下 `Alt`（没按别的键）→ 菜单栏临时出现 / 再按一次藏回去。

        ★ 为什么用 `Alt`（我定的，用户说"你看着办"）：
          ① **不跟任何快捷键打架** —— 查过本程序，没有单独的 `Alt` 绑定
          ② **顺直觉** —— Windows 老式程序都是 `Alt` 出菜单栏
          ③ **不误触** —— 只在"**单击**"时切换；
             `Alt`+别的键照常走它原来的功能（下面会判"有没有按过别的键"）
        ★ 为什么做成"**临时**出现"而不是"永久显示"：
          用户要的是"看不见两个入口" —— 临时出现，
          点完东西或者再按一下 `Alt` 就藏回去。
        """
        # ★ 只有"干净地单击 Alt"才切换 —— 按过别的键就不算（比如 Alt+F4）
        try:
            if getattr(self, "_alt_combo_used", False):
                self._alt_combo_used = False
                return
        except Exception:
            pass
        try:
            self._toggle_menubar()
        except Exception as _e:
            note_swallowed(T("Alt 唤出菜单栏失败"), _e)

    def _on_alt_toggle_menu(self, event=None):
        """★ 按 `Alt` 的同时**按了别的键** → 记一笔，松手时不切换菜单。

        ★ 为什么需要：`Alt+F4`（关窗口）、`Alt+Tab`（切窗口）这些
          都是系统功能，**不能因为"按过 Alt"就把菜单栏弹出来**。
        """
        try:
            if event is not None and getattr(event, "keysym", "") not in (
                    "Alt_L", "Alt_R", "Alt"):
                self._alt_combo_used = True
        except Exception:
            pass

    def _toggle_menubar(self):
        """★ 菜单栏 显示 ⇄ 藏起（悬浮球和 `Alt` 共用这一个开关）。"""
        try:
            now_hidden = bool(getattr(self, "_menu_hidden", False))
            if now_hidden:
                self.root.config(menu=self.menubar)
                self._menu_hidden = False
                try:
                    self._refresh_menu_states()
                except Exception:
                    pass
            else:
                self.root.config(menu="")
                self._menu_hidden = True
        except Exception as _e:
            note_swallowed(T("切换菜单栏显示失败"), _e)

    # ======================================================================
    #  ★★★ 2026-10-08：**插件菜单**（用户要"配合插件入口"）
    # ======================================================================
    def _attach_plugin_menus(self):
        """★ 把插件想加的菜单**挂到主菜单上**（"问表要东西"）。

        ★ 为什么是一个单独的方法（而不是塞在 `_build_menu` 里）：
          `_build_menu` 跑在**插件加载之前**（菜单要先生出来，
          插件才能往上挂）—— 所以**加载完插件后要再挂一次**。
          ★ 这也是"预留入口"的做法：**主程序不认识任何插件**，
            只是"问 `plugin_menu_entries()` 要一份清单，照着挂"。

        ★ 什么时候被调：
          ① 启动、插件加载完之后（见 `__init__`）
          ② 以后如果做"运行时启用插件"，再来一遍就行

        ★ 每一块单独 try —— 一个插件菜单挂失败，不影响别的、也不影响主程序。
        """
        try:
            # ---- ① 插件要的**顶层菜单** ----
            for pname, label, items in plugin_menu_entries():
                try:
                    sub = tk.Menu(self.menubar, tearoff=0)
                    for it in (items or []):
                        try:
                            if it is None:
                                sub.add_separator()
                                continue
                            text, cmd = it
                            sub.add_command(label=str(text), command=cmd)
                        except Exception:
                            pass
                    if sub.index("end") is None:
                        continue        # 空的就不挂（免得点开一片空白）
                    self.menubar.add_cascade(label=str(label), menu=sub)
                except Exception as _e:
                    note_swallowed(T("挂插件菜单「{x}」失败", x=pname), _e)
            # ---- ①.5 ★ 插件可能注册了**自己的皮肤** → 把皮肤菜单重刷一遍 ----
            #   ★ 为什么需要（实测踩的）：
            #     皮肤菜单是**建菜单时**列一遍的，那会儿插件**还没加载**，
            #     它注册的配色**列不出来**（实测：进了 `_THEMES`，菜单里却没有）。
            #     ★ 虽然我给它挂了 `postcommand`（每次点开重列），
            #       但**这里再刷一次更稳** —— 万一 `postcommand` 在某些
            #       Tk 版本上不灵，这里也兜住了。
            #     ★ "两处都做"是刻意的：用户要的就是"留冗余、方便以后改"。
            try:
                _tm = getattr(self, "_theme_menu", None)
                if _tm is not None:
                    self._fill_theme_menu(_tm)
            except Exception:
                pass
            # ---- ② 插件要"插进已有菜单"的项 ----
            #   ★ 按菜单名找：主菜单里 cget("label") 等于它的那个
            for pname, mlabel, ilabel, cmd in plugin_menu_items():
                try:
                    target = None
                    n = self.menubar.index("end")
                    if n is None:
                        continue
                    for i in range(n + 1):
                        try:
                            if str(self.menubar.entrycget(i, "label")) == str(mlabel):
                                target = self.menubar.nametowidget(
                                    self.menubar.entrycget(i, "menu"))
                                break
                        except Exception:
                            continue
                    if target is None:
                        # ★ 找不到那个菜单 → 就加到主菜单最外层（别把插件吃掉）
                        self.menubar.add_command(label=str(ilabel), command=cmd)
                    else:
                        target.add_separator()
                        target.add_command(label=str(ilabel), command=cmd)
                except Exception as _e:
                    note_swallowed(T("插插件菜单项「{x}」失败", x=pname), _e)
        except Exception as _e:
            note_swallowed(T("挂插件菜单失败"), _e)

    # ======================================================================
    #  ★★★ 2026-10-08：**皮肤菜单"每次打开时重建"**（用户要"配合插件入口"）
    # ======================================================================
    # ======================================================================
    #  ★★★ 2026-10-08 **🌐 语言菜单**（用户要的多语言）
    # ======================================================================
    def _fill_lang_menu(self, menu):
        """★ 把"现在有哪些语言"**重新列一遍**（每开一次菜单跑一次）。

        ★★ 为什么要"每次重扫"（跟皮肤菜单一个道理）：
          语言列表是**扫描 `语言/` 目录**得到的 ——
          用户可能**在程序开着的时候**丢了一个新语言文件进去
          （★ 这是"加语言不用改代码"的代价：得**每次重看**）。
        ★ 先 `delete(0,"end")` 再建 —— 不然每开一次**多一份**。
        """
        try:
            menu.delete(0, "end")
        except Exception:
            pass
        cur = ""
        try:
            cur = str(load_ui_setting("language", "") or "") \
                or (_i18n.current_language() if _i18n else "zh_CN")
        except Exception:
            cur = "zh_CN"
        _var = tk.StringVar(value=cur)
        try:
            items = _i18n.available_languages() if _i18n else \
                [("zh_CN", "中文（简体）", "")]
        except Exception:
            items = [("zh_CN", "中文（简体）", "")]
        for code, label, _path in items:
            try:
                menu.add_radiobutton(
                    label=("● " if code == cur else "　") + label,
                    value=code, variable=_var,
                    command=lambda c=code: self.set_language_now(c))
            except Exception:
                pass
        menu.add_separator()
        menu.add_command(label=T("📂 打开语言文件夹（可自己加语言）"),
                         command=self._open_lang_folder)

    def _open_lang_folder(self):
        """★ 打开 `语言/` 文件夹 —— **让别人自己能加语言**。

        ★ 为什么要给这个入口：语言文件是**纯 JSON**，
          懂一点的人**照着 `en_US.json` 加一个 `ru_RU.json` 就行** ——
          **不用改代码、不用重新打包**。
          ★ 这是"开放"的一部分：**别人能参与翻译，不需要我**。
        """
        try:
            d = ""
            if _i18n is not None:
                d = _i18n._candidates_dir()
            if not d or not os.path.isdir(d):
                d = os.path.join(_HERE, "语言")
            os.makedirs(d, exist_ok=True)
            os.startfile(d)          # ★ Windows 打开文件夹
        except Exception as _e:
            note_swallowed(T("打开语言文件夹失败"), _e)

    def set_language_now(self, code):
        """★ **换语言**（存设置 + 提示重启 + 给"现在就重启"）。

        ★ 用户定的是"重启生效"（A 方案）——
          因为 Tk 的文字**没法像颜色那样热刷**：
          颜色能"扫一遍所有控件重设"，文字得**一条条重设**，
          等价于"把界面重建一遍"（复杂、风险高、还费钱）。
        ★ 所以这里：**存下来 + 说清楚 + 给个重启按钮**（半自动，省事）。
        """
        try:
            save_ui_setting("language", str(code))
            from tkinter import messagebox
            lab = str(code)
            try:
                for c, l, _p in (_i18n.available_languages() if _i18n else []):
                    if c == code:
                        lab = l
                        break
            except Exception:
                pass
            ok = messagebox.askyesno(
                "语言 / Language",
                "已选择：%s\n\n"
                "★ 界面文字**要重启程序才会变**\n"
                "（Tk 的文字不像颜色那样能即时刷新）\n\n"
                "现在就重启吗？" % lab,
                parent=self.root)
            if ok:
                self._restart_app()
        except Exception as _e:
            note_swallowed(T("换语言失败"), _e)

    def _restart_app(self):
        """★ **重启程序**（用户不用自己去关开）。

        ★ 怎么做（Windows 上的稳妥写法）：
          ① 用 `sys.executable` + `sys.argv` **重新起一个自己**
             · 打包成 exe 时 `sys.executable` 就是 exe 自己 ✔
             · 源码跑时是 python.exe（`sys.argv[0]` 是脚本）✔
          ② **先起新的、再关旧的** ——
             ★ 顺序反了的话（先关再起），万一新进程起不来，
               用户就**什么窗口都没有了**（最难受的情况）。
          ③ 关旧的时候走**正常退出流程**（`on_close`）——
             不然数据库连接、后台线程不会好好收尾。
        """
        import subprocess
        try:
            if getattr(sys, "frozen", False):
                args = [sys.executable] + sys.argv[1:]
            else:
                args = [sys.executable] + sys.argv
            subprocess.Popen(args, cwd=os.getcwd(), close_fds=True)
        except Exception as _e:
            note_swallowed(T("重启失败（请手动关掉再打开）"), _e)
            return
        # ★ 新进程起来了 → 关掉自己
        try:
            self.on_close()
        except Exception:
            try:
                self.root.destroy()
            except Exception:
                pass

    def _fill_theme_menu(self, menu):
        """★★ 把"现在有哪些皮肤"**重新列一遍**（每开一次菜单跑一次）。

        ★★ 为什么需要"每次重建"（实测踩出来的）：
          · 菜单是**程序启动时**建的；
          · 而插件是**建完菜单之后**才加载的 ——
            插件注册的皮肤**在那时还不存在** → 菜单里**列不出来**。
          · 实测：插件注册的配色**确实进了 `_THEMES`**（`apply_theme_names()`
            能看到它），**但菜单里看不到** —— 因为菜单是"建的时候拍了个快照"。
        ★ 修法：**每次点开菜单重新问一遍** ——
          · 插件的皮肤自动出现
          · 以后"运行时装皮肤"也自动出现
          · 这段代码**永远不用改**（这就是"接口"的价值）
        ★ 为什么先 `delete(0, "end")` 再建：
          不删的话每开一次就**多一份**（菜单越来越长）。
        """
        try:
            menu.delete(0, "end")
        except Exception:
            pass
        try:
            names = apply_theme_names()
        except Exception:
            names = [("light", "light"), ("dark", "dark")]
        _ICON = {"light": "☀ ", "dark": "🌙 "}
        for key, lbl in names:
            try:
                menu.add_radiobutton(
                    label=_ICON.get(key, "🎨 ") + lbl,
                    value=key, variable=self.theme_var,
                    command=lambda k=key: self.set_theme(k))
            except Exception:
                pass

    # ======================================================================
    #  ★★★ 2026-10-08：**背景图 + "假毛玻璃"**（用户要的美化效果）
    # ======================================================================
    def _theme_bg_spec(self):
        """★ 从当前皮肤里读"美化项"（图 / 模式 / 模糊 / 面板透明感）。

        ★ 皮肤里这些键都是**可选**的 —— 没有就表示"不启用背景图"：
            `background_image` / `background_mode` / `background_blur`
            `panel_alpha`
        ★ 返回 `(图片路径, 模式, 模糊半径, 面板透明感 0~100)`；
          没有图就返回 `(None, ..., 0)`。

        ★★ 2026-10-08：**再读一处** —— 用户在「设置 → 背景图」里手选的那张。
          ★ 优先级：**用户手选的 > 皮肤自带的**
            （用户刚选完图，当然该用他的；皮肤自带的只是"默认长相"）。
          ★ 为什么要两处：用户说「他们挺喜欢搞个图片当背景」——
            **最自然的用法是"我自己挑一张"**，不该逼他先做一套皮肤。
        """
        try:
            th = _themes_now()
            path = str(th.get("background_image") or "").strip()
            mode = str(th.get("background_mode") or "cover").strip().lower()
            try:
                blur = float(th.get("background_blur") or 0)
            except Exception:
                blur = 0.0
            try:
                pa = float(th.get("panel_alpha") or 0)
            except Exception:
                pa = 0.0
            # ★ 用户手选的优先（存在 custom_themes 的 `__background__` 里）
            try:
                data = load_ui_setting("custom_themes", None)
                if isinstance(data, dict):
                    u = data.get("__background__") or {}
                    if isinstance(u, dict) and u.get("background_image"):
                        path = str(u.get("background_image") or "").strip()
                        mode = str(u.get("background_mode") or mode).lower()
                        try:
                            blur = float(u.get("background_blur") or blur)
                        except Exception:
                            pass
                        try:
                            pa = float(u.get("panel_alpha") or pa)
                        except Exception:
                            pass
            except Exception:
                pass
            if mode not in BG_MODES:
                mode = "cover"
            return (path or None, mode, max(0.0, blur),
                    max(0.0, min(100.0, pa)))
        except Exception:
            return (None, "cover", 0.0, 0.0)

    def _apply_background(self):
        """★★ **铺背景图**（用户要的"搞个图片当背景"）。

        ★ 什么时候调：
          ① 启动时（`__init__` 里，界面建好之后）
          ② 换皮肤时（皮肤可能带自己的背景图）
          ③ 用户手动"选一张背景图"时

        ★ 怎么铺：
          · 用 `make_background_layer()` 铺在 **`self.root` 的最底层**
          · 然后**把主界面那几块"抬上来"** ——
            不然图会盖住 `paned`（因为 `place` 的层级可能比 `pack` 高）
          ★ `layer.lower()` 已经压到底了，但 Tk 的 `place` / `pack`
            **混用时层级不完全可靠** → 所以这里**再显式 `lift()` 一次**主块。

        ★★ 失败兜底：图读不了（被删了/挪了）→
          `make_background_layer` 会铺一块**兜底色**（不会露出一片白，
          夜间模式下那会很难看 —— 用户报过好几次）。
        """
        path, mode, blur, _pa = self._theme_bg_spec()
        # ★ 先把旧的背景层拆掉（换皮肤/换图时不能叠着）
        try:
            old = getattr(self, "_bg_layer", None)
            if old is not None:
                old.destroy()
        except Exception:
            pass
        self._bg_layer = None
        if not path:
            return
        try:
            fallback = theme_get("win_bg")
            layer = make_background_layer(self.root, path, mode, blur,
                                          fallback_bg=fallback)
            self._bg_layer = layer
            if layer is None:
                return
            # ★ 把主界面抬到图上（不然图盖住内容）
            for nm in ("_top_bar", "_top_bar2", "paned"):
                try:
                    w = getattr(self, nm, None)
                    if w is not None:
                        w.lift()
                except Exception:
                    pass
            # ★ 状态栏也要抬（它在最底下那一行）
            try:
                for ch in self.root.winfo_children():
                    if ch is not layer:
                        try:
                            # ★ 只抬"直接子控件"里不是背景层的那几个
                            ch.lift()
                        except Exception:
                            pass
            except Exception:
                pass
            self._apply_panel_blend()
        except Exception as _e:
            note_swallowed(T("铺背景图失败"), _e)

    def _apply_panel_blend(self):
        """★★ **面板色"看着半透明"** —— 这一步不做，背景图基本看不见。

        ★ 为什么需要（实测出来的）：
          Tk 的控件**没有透明这回事** —— 面板有底色就是实色，
          **背景图只有"控件之间的缝"能露出来**。
          → 所以要让"看着像半透明"，只能**把面板色往图片的颜色上调**。

        ★ 怎么做：
          ① 取背景图的**平均色**（缩到 1x1，最省事也最准）
          ② 把"面板色"按 `panel_alpha` 混进这个平均色
             · `panel_alpha=0`   → 面板是原来的实色（看不出背景图）
             · `panel_alpha=60`  → 面板明显偏图片色（像透了一层）
             · `panel_alpha=100` → 面板几乎就是图片色（**字可能看不清**）
          ③ 把混好的颜色**临时覆盖到主题表里** ——
             这样"所有读 `theme_get()` 的地方"**自动**用上新颜色，
             **不用改任何调用方**（跟自定义皮肤一个套路）。

        ★★ 为什么是"临时覆盖"而不是"改皮肤表本身"：
          皮肤表是**共享的**（`light` / `dark` 就一份）——
          直接改它会把"原配色"弄丢（切回去就回不来了）。
          → 所以先把**原始色存一份**，混完写进"当前皮肤"；
            换皮肤 / 关背景图时**恢复**（见 `_restore_panel_colors`）。
        """
        path, _mode, blur, pa = self._theme_bg_spec()
        # ★ 先把上次混过的恢复（不然越混越偏）
        self._restore_panel_colors()
        if not path or pa <= 0:
            return
        try:
            avg = average_color_of_image(path, blur)
            if not avg:
                return
            th = _themes_now()
            # ★ 要调的"面板类"颜色（这几块正好是"盖在背景上的面"）
            keys = ("win_bg", "card_bg", "panel_bg", "panel_bg2", "text_bg",
                    "canvas_bg", "stripe_bg")
            saved = {}
            k = pa / 100.0
            for key in keys:
                try:
                    old = th.get(key)
                    if not old:
                        continue
                    saved[key] = old             # ★ 存原始色（恢复用）
                    th[key] = blend_color_over(old, avg, k)
                except Exception:
                    pass
            # ★ 存起来，换皮肤时恢复
            self._blended_saved = saved
        except Exception as _e:
            note_swallowed(T("调和面板色失败（背景图会看不太出来）"), _e)

    def _restore_panel_colors(self):
        """★ 把上次"调和过的面板色"**恢复成原始色**。

        ★ 为什么必须恢复（**不恢复的话越混越偏**）：
          调和是"面板色混图片色"—— 如果下次拿"混过的色"再混一遍，
          就会**越来越接近图片色**（几十次之后就全糊成一片了）。
          ★ 实测踩过这个坑的思路：**改之前先存原值**，
            用完/换皮肤时恢复 —— 这是"可逆修改"的通用做法。
        """
        try:
            saved = getattr(self, "_blended_saved", None)
            if not saved:
                return
            th = _themes_now()
            for k2, v in saved.items():
                try:
                    th[k2] = v
                except Exception:
                    pass
            self._blended_saved = None
        except Exception:
            pass

    def _pause_scan_placeholder(self):
        """（占位，保持方法顺序整齐 —— 没实际内容）"""
        return None

    def _on_esc_hide_menu(self, event=None):
        """★ `Esc`：菜单栏临时出现时，按一下就藏回去（顺手的习惯）。"""
        try:
            if not getattr(self, "_menu_hidden", True):
                self.root.config(menu="")
                self._menu_hidden = True
                return "break"
        except Exception:
            pass
        return None

    # ======================================================================
    #  ★★★ 2026-10-08：**背景图相关的小工具**（用户要的美化效果）
    # ======================================================================
    def choose_background_image(self):
        """★ 让用户**选一张图当背景**（随手就能试的那种）。

        ★ 为什么要有这个手动入口（而不是只让皮肤带背景图）：
          用户说「他们挺喜欢搞个图片当背景」——
          **最自然的用法就是"我自己挑一张"**，不该逼他先去做一套皮肤。
        ★ 选了之后存进设置（`custom_themes` 里那个"当前自定义"），
          下次打开还在。
        """
        try:
            from tkinter import filedialog, messagebox
            path = filedialog.askopenfilename(
                title=T("选一张图当背景"),
                filetypes=[("图片", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
                           ("所有文件", "*.*")],
                parent=self.root)
            if not path:
                return
            # ★ 存成"当前自定义皮肤的一套美化项"
            self.set_background_image(path)
            messagebox.showinfo(
                "背景图已设置",
                "已用这张图当背景：\n%s\n\n"
                "★ 想调「透不透」？去「设置 → 背景图」里改。" % path,
                parent=self.root)
        except Exception as _e:
            note_swallowed(T("选背景图失败"), _e)

    def set_background_image(self, path, blur=None, mode=None, panel_alpha=None):
        """★ **设置背景图**（用户手动选 / 皮肤自带，都走这里）。

        ★ 实现思路（**不新建一套机制，而是"借用自定义皮肤"**）：
          背景图存在 `custom_themes` 里的一个特殊条目 `__background__`，
          启动时 `_load_custom_themes()` 已经会把它读进来 ——
          **所以"记住背景图"这件事不用另写代码**。
        ★ 参数 `blur` / `mode` / `panel_alpha` 不传就用**当前值**
          （或者默认：不模糊、铺满、面板 55% 透明感）。
        """
        try:
            data = load_ui_setting("custom_themes", None)
            if not isinstance(data, dict):
                data = {}
            cur = dict(data.get("__background__") or {})
            cur["name"] = "__background__"
            cur["label"] = "自定义背景"
            # ★ 背景图必须是"当前皮肤"才有用 ——
            #   所以这里**只存设置**，真正生效靠 `_apply_background()` 直读。
            #   见 `_theme_bg_spec()`：它同时看"皮肤里的键"和"这个设置"。
            cur["background_image"] = str(path)
            cur["background_mode"] = str(mode or cur.get("background_mode")
                                         or "cover")
            cur["background_blur"] = float(
                blur if blur is not None else cur.get("background_blur") or 0)
            cur["panel_alpha"] = float(
                panel_alpha if panel_alpha is not None
                else cur.get("panel_alpha") or 55)
            data["__background__"] = cur
            save_ui_setting("custom_themes", data)
            self._bg_user = cur
            # ★ 立刻生效
            self._apply_background()
            self._refresh_all_panels()
        except Exception as _e:
            note_swallowed(T("保存背景图设置失败"), _e)

    def clear_background(self):
        """★ 去掉背景图（恢复原来的实色界面）。"""
        try:
            data = load_ui_setting("custom_themes", None)
            if isinstance(data, dict) and "__background__" in data:
                data.pop("__background__", None)
                save_ui_setting("custom_themes", data)
            self._restore_panel_colors()
            self._apply_background()
            self._refresh_all_panels()
        except Exception as _e:
            note_swallowed(T("去掉背景图失败"), _e)

    def _bg_cur(self):
        """★ 拿"当前背景设置"（没有就返回一份默认的）。"""
        try:
            data = load_ui_setting("custom_themes", None)
            if isinstance(data, dict):
                u = data.get("__background__")
                if isinstance(u, dict):
                    return dict(u)
        except Exception:
            pass
        return {"name": "__background__", "label": "自定义背景",
                "background_image": "", "background_mode": "cover",
                "background_blur": 14, "panel_alpha": 55}

    def set_bg_alpha(self, v):
        """★ 改"面板透不透"（0~100）—— 用户反复试的那个。"""
        try:
            c = self._bg_cur()
            if not c.get("background_image"):
                self.log_output("（还没选背景图 —— 先去「设置 → 背景图 → "
                                "选一张图当背景…」）")
                return
            self.set_background_image(c["background_image"],
                                      panel_alpha=float(v))
        except Exception as _e:
            note_swallowed(T("调背景透明度失败"), _e)

    def set_bg_blur(self, v):
        """★ 改"模糊程度"（0=不模糊；14 左右像毛玻璃）。"""
        try:
            c = self._bg_cur()
            if not c.get("background_image"):
                self.log_output("（还没选背景图 —— 先去「设置 → 背景图 → "
                                "选一张图当背景…」）")
                return
            self.set_background_image(c["background_image"], blur=float(v))
        except Exception as _e:
            note_swallowed(T("调背景模糊失败"), _e)

    def set_bg_mode(self, m):
        """★ 改"怎么摆"（cover / contain / tile / center）。"""
        try:
            c = self._bg_cur()
            if not c.get("background_image"):
                self.log_output("（还没选背景图 —— 先去「设置 → 背景图 → "
                                "选一张图当背景…」）")
                return
            self.set_background_image(c["background_image"], mode=str(m))
        except Exception as _e:
            note_swallowed(T("调背景摆放失败"), _e)

    def _refresh_all_panels(self):
        """★ 面板色变了之后，**把已经建好的控件也刷一遍**。

        ★ 为什么需要：`_apply_panel_blend()` 改的是**主题表** ——
          那只对"以后新建的控件"生效；
          **已经建好的控件读的是"建的时候那个颜色"**。
          → 所以要主动重刷一遍（跟换皮肤是同一件事）。
        ★ 为什么不用 `self._retheme_custom_parts()` 就够：
          那个只管"代码自己画的几块"（列表、星图…）；
          按钮/输入框那些 **ttk 控件**得靠 `apply_theme` 重设样式表。
          → **两个都要**（各管一半）。
        """
        try:
            apply_theme(self.root, THEME_NAME)
        except Exception as _e:
            note_swallowed(T("重刷界面颜色失败"), _e)
        try:
            self._retheme_custom_parts()
        except Exception:
            pass


        """★ 面板色变了之后，**把已经建好的控件也刷一遍**。

        ★ 为什么需要：`_apply_panel_blend()` 改的是**主题表** ——
          那只对"以后新建的控件"生效；
          **已经建好的控件读的是"建的时候那个颜色"**。
          → 所以要主动重刷一遍（跟换皮肤是同一件事）。
        """
        try:
            apply_theme(self.root, THEME_NAME)
        except Exception as _e:
            note_swallowed(T("重刷界面颜色失败"), _e)
        try:
            self._retheme_custom_parts()
        except Exception:
            pass

    # ======================================================================
    #  ★★★ 2026-10-08：**悬浮球**
    # ======================================================================
    def _setup_floating_ball(self):
        """★ 把悬浮球建出来；**建不起来就把菜单栏装回来**（安全网）。

        ★ 为什么要"建不起来就装回菜单栏"：
          菜单栏已经藏起来了 —— 如果球也没建起来，
          **用户就一个功能都点不到了**（这是最坏的情况）。
          ★ 所以这里是"**要么球能用、要么菜单栏在**"，
            不允许出现"两个都没有"。
        ★ 用户的偏好也读一下（`float_ball_on`）：他上次把球关了，
          这次就别硬塞给他；但**菜单栏要给他装回来**。
        """
        ball = None
        try:
            self.floating_ball = None
            # ★ 用户上次关掉了球吗？
            _want = load_ui_setting("float_ball_on", True)
            if _want is False:
                # 他关过 → 不建球，但**菜单栏得给他**（不然没入口）
                try:
                    self.root.config(menu=self.menubar)
                    self._menu_hidden = False
                except Exception:
                    pass
                return
            ball = FloatingBall(self)
            if ball.build():
                self.floating_ball = ball
                # ★ 主窗口挪动 / 缩放 → 球跟着走（保持相对位置）
                try:
                    self.root.bind("<Configure>", self._on_root_configure,
                                   add="+")
                except Exception:
                    pass
            else:
                ball = None
        except Exception as _e:
            ball = None
            try:
                note_swallowed(T("建悬浮球失败"), _e)
            except Exception:
                pass
        # ★ 兜底：球没建成 → 菜单栏装回来
        if ball is None:
            try:
                self.root.config(menu=self.menubar)
                self._menu_hidden = False
                self.log_output("（悬浮球没建起来，已把菜单栏装回来 —— "
                                "功能入口一个都不少）")
            except Exception:
                pass

    def _on_root_configure(self, event=None):
        """★ 主窗口动了 → 让球跟着动（它记的是"相对位置"）。

        ★ 为什么：球是**独立窗口**（屏幕坐标），
          如果不跟着走，用户把主窗口挪到别处，球就"留在原地"了 ——
          看起来像"飘在外面"，很怪。
        ★ `Configure` 事件很频繁（缩放窗口时每像素一次），
          所以这里**只做一件极轻的事**，量不出开销。
        """
        try:
            if getattr(self, "floating_ball", None) is not None:
                # ★ 只在"窗口位置/大小真的变了"时动它（省点开销）
                key = (self.root.winfo_x(), self.root.winfo_y(),
                       self.root.winfo_width(), self.root.winfo_height())
                if key != getattr(self, "_last_root_geom", None):
                    self._last_root_geom = key
                    self.floating_ball.follows_root()
        except Exception:
            pass

    def toggle_floating_ball(self):
        """★ 「设置」菜单里的入口：把球叫回来 / 收起来。

        ★ 为什么必须有这个：用户在球上右键"关掉这个球"之后，
          **总得有个地方能再叫回来**（不然只能改设置文件了）。
        """
        try:
            b = getattr(self, "floating_ball", None)
            if b is not None and b.win is not None:
                b.hide()
                self.floating_ball = None
                self.log_output(T("已收走悬浮球（菜单栏还在「设置 → 显示菜单栏」里）"))
            else:
                b = FloatingBall(self)
                if b.build():
                    self.floating_ball = b
                    self.log_output(T("悬浮球已叫回来"))
                else:
                    self.log_output(T("★ 悬浮球没建起来（详情见「🔔 问题」面板）"))
        except Exception as _e:
            note_swallowed(T("切换悬浮球失败"), _e)

    # ======================================================================
    #  ★★★ 2026-10-08：**「设置」里那两个"球的皮肤"入口**
    #  ----------------------------------------------------------------------
    #  ★★ 跟球右键菜单里的是**同一件事**，只是入口不同 ——
    #    为什么要两个入口：
    #      · 球右键 → 顺手（球在眼前时最方便）
    #      · 设置菜单 → **球被收走 / 建不起来时**也能设
    #    ★★ 注意：这两个入口**只管球**，
    #      跟「设置 → 🎨 皮肤（主界面）」**完全是两回事** ——
    #      用户特意强调过「你可别搞混了啊」。
    # ======================================================================
    def _set_ball_style_from_menu(self, name):
        """★ （设置菜单）换球的皮肤 —— **球没建起来也能设**（存着，下次生效）。"""
        try:
            save_ui_setting("ball_style", str(name))
            b = getattr(self, "floating_ball", None)
            if b is not None:
                b.set_ball_style(name)
                self.log_output(T("悬浮球皮肤已换成：{x}", x=name))
            else:
                self.log_output("悬浮球皮肤已记住（%s）—— 下次叫出球时生效"
                                % name)
        except Exception as _e:
            note_swallowed(T("换悬浮球皮肤失败"), _e)

    def _set_ball_shape_from_menu(self, shape):
        """★ （设置菜单）换球的形状 —— 同上，球不在也能设。"""
        try:
            b = getattr(self, "floating_ball", None)
            if b is not None:
                b.set_ball_shape(shape)
                self.log_output(T("悬浮球形状已换成：{x}", x=shape))
            else:
                # ★ 球不在 → 记在"球皮肤"里（下次建球时读出来）
                cur = ball_style_get(load_ui_setting("ball_style", "default"))
                cur["shape"] = str(shape)
                nm = "%s__%s" % (cur.get("name") or "default", str(shape))
                ball_style_add(nm, cur, label=cur.get("label") or nm)
                save_ui_setting("ball_style", nm)
                self.log_output("悬浮球形状已记住（%s）—— 下次叫出球时生效"
                                % shape)
        except Exception as _e:
            note_swallowed(T("换悬浮球形状失败"), _e)

    # ======================================================================
    #  ★★ 2026-10-07：**菜单项的"状态圆点"机制**
    #  ----------------------------------------------------------------------
    #  ★★ 用户定的语义（**以后所有状态提示都照这个来**）：
    #     ① 开关状态 → 实心圆 ● ，**绿 = 开 / 红 = 关**
    #     ② 错误     → **红叉 ⊗**（形状不同！一眼分清"报错" ≠ "关着"）
    #     ③ 警告     → **黄点 ●**
    #     ★ 靠**形状**区分用途，不靠颜色 ——
    #       因为颜色会混（红点既可能"关着"、也可能"出错"），形状不会混。
    #     ★ 用户原话：「使用者经常不知道一个圆点或开关是绿的，
    #       到底是在告诉你运行中、还是在告诉你点了才运行」
    #       —— 所以**必须**有形状区分，光有颜色不够。
    #
    #  为什么要有这套：菜单里原来写「标签盒（显示 / 收起）」——
    #    用户**看不出现在是开是关**，得点一下才知道。
    #    现在每项前面带 ●（绿=开）/ ●（红=关），一眼就懂。
    #
    #  ★ 圆点用**最朴素的几何字符**，不用 emoji ——
    #    用户定过"图标要图片型、emoji 普世性差"；
    #    但**菜单项不支持放图片**（Tk 限制，实测过），
    #    所以退而用几何字符 + 颜色，任何系统显示都一样。
    # ======================================================================
    DOT_ON = "\u25cf"       # ● 实心圆（开）
    DOT_OFF = "\u25cf"      # ● 实心圆（关，靠颜色区分）
    COLOR_ON = "#1f9d55"    # 绿（开）
    COLOR_OFF = "#c0392b"   # 红（关）

    def _menu_state_sources(self):
        """★ 返回 {(菜单对象, 项序号): (取状态函数, 干净的名字)}。

        ★ 每一项的"状态从哪读"都核实过（不是猜的）：
           · 标签盒    → self.tagbox_visible
           · 标签条    → self.file_list.tagbar_visible
           · 顶部工具栏 → self._top_bar_visible
           · 左侧分类库 → self._sidebar_visible
           · 悬停预览   → self.hover.enabled
           · 快速预览   → self.quick_preview.is_open()
           · 瀑布流模式 → (self.layout_mode == "grid")

        ★★ 关键（2026-10-07 踩过）：
          **必须用"项序号"来定位，不能按 label 找！**
          因为这套机制**会改 label**（`标签盒` → `● 标签盒`）——
          按 label 找的话，**刷新一次之后就再也找不到了**
          （实测：刷新后状态源变成 0 条，圆点永远不更新）。
          ★ 所以：项序号在**建菜单时**就记在 `self._menu_state_map` 里，
            这里直接用它，不再去找。
        """
        out = {}
        reg = getattr(self, "_menu_state_map", None) or []
        for idx, getter, name in reg:
            m = getattr(self, "_m_switches", None)
            if m is not None:
                out[(str(m), idx)] = (getter, name)
        m2 = getattr(self, "_m_settings", None)
        for idx, getter, name in (getattr(self, "_menu_state_map2", None) or []):
            if m2 is not None:
                out[(str(m2), idx)] = (getter, name)
        return out
    def _refresh_menu_states(self):
        """★ 把每个开关项的圆点和颜色刷成当前状态。

        ★ 什么时候调：
          · 菜单要弹出来之前（`postcommand`，见菜单构造处）
          · 任何一个开关切换之后
        这样用户**打开菜单的那一瞬间**看到的就是真实状态。

        ★★ 用**记下来的项序号**定位（`self._menu_state_map`），
          不按 label 找 —— 因为本函数**会改 label**，
          按 label 找的话刷一次之后就再也找不到了（踩过）。
        """
        try:
            reg = getattr(self, "_menu_state_map", None) or []
            reg2 = getattr(self, "_menu_state_map2", None) or []
        except Exception:
            return
        for menu, items in ((getattr(self, "_m_switches", None), reg),
                            (getattr(self, "_m_settings", None), reg2)):
            if menu is None:
                continue
            for item in items:
                # 兼容两种登记格式：3 元组用外层菜单，4 元组自带菜单
                if len(item) == 4:
                    idx, getter, name, menu_use = item
                else:
                    idx, getter, name = item
                    menu_use = menu
                try:
                    on = bool(getter())
                except Exception:
                    continue
                col = self.COLOR_ON if on else self.COLOR_OFF
                try:
                    menu_use.entryconfigure(
                        idx,
                        label="%s %s" % (self.DOT_ON if on else self.DOT_OFF,
                                         name),
                        foreground=col)
                except Exception:
                    continue

    def _tick_menu_states(self, *_a):
        """给菜单当 postcommand 用：弹出来之前先刷状态。"""
        try:
            self._refresh_menu_states()
        except Exception:
            pass

    def _on_layout_from_menu(self):
        """★ 2026-10-07：**这个方法已经不用了**（保留只为兼容旧调用）。

        ★ 为什么不删：删了万一还有别处调它会 AttributeError，
          留着最安全（它转发给新开关）。
        ★ 它原来读 `self.menu_layout_var` —— 那个变量是
          「列表模式 / 瀑布流模式」两个单选项建的；
          菜单重排时那两项被合并成一个开关、变量也就不建了，
          **于是这个方法和 `_on_layout_mode_change` 一起报
          `'FileTaggerApp' object has no attribute 'menu_layout_var'`**。
        """
        self._toggle_layout_from_menu()

    def change_ui_scale(self):
        dlg = UIScaleDialog(self.root, self.ui_scale)
        if dlg.result is None:
            return
        new_scale = dlg.result
        if abs(new_scale - self.ui_scale) < 1e-6:
            messagebox.showinfo("提示", T("缩放比例未变。"), parent=self.root)
            return
        if save_ui_scale(new_scale):
            # ★★ 2026-10-08：**顺手把图标尺寸的缓存清掉**。
            #   本程序的"界面缩放"要**重启**才生效（下面这句提示就是这意思），
            #   所以严格说这里不清也没事 —— 但**万一以后改成即时生效**，
            #   忘了清缓存就会"字变大了、图标还是旧的"（就是待清算 #16 那个病）。
            #   ★ 这叫"先把雷拆了"：多一行，省一个将来的 bug。
            try:
                FileList.refresh_icon_sizes()
            except Exception:
                pass
            messagebox.showinfo(
                "需要重启",
                f"界面缩放已保存为 {int(new_scale * 100)}%。\n\n"
                "请关闭程序并重新打开，新的缩放才会生效。\n\n"
                "（设置保存在：" + str(SETTINGS_PATH) + "）",
                parent=self.root)
        else:
            messagebox.showerror(
                "保存失败",
                "无法写入设置文件，请检查目录权限。",
                parent=self.root)

    def show_usage_log(self):
        """★★ 2026-10-07 **合并版**：「用法记录」+「体检报告」合成一个窗口。

        ★ 用户提的：「体验报告和用法记录的区别是什么，感觉可以合并」
          → 我查了，他说的"体验报告"其实是**体检报告**，两者确实是**一个东西的两半**：
            |          | 体检报告                 | 用法记录               |
            |----------|--------------------------|------------------------|
            | 数据来源 | `swallowed_report()`（内存） | `usage_read()`（落盘）  |
            | 范围     | **只管这一次开程序**       | **跨次累积**            |
            | 内容     | 哪儿出的问题 —— N 次       | 哪儿 / 次数 / 最近 / 错误 |

        ★ 用户选了**方案 B**：一个窗口、**两个页签**（本次 / 历史）。
          为什么不做成一个表：**"本次"和"跨次"是不同的东西** ——
            · 「本次」适合"我刚发现一个 bug，现在就看看"
            · 「历史」适合"哪些毛病**老**出现"
          硬合成一个表会**丢掉这个区分**，而**恰恰"老出现"才最该修**。
        """
        win = tk.Toplevel(self.root)
        # ★★ 2026-10-07：Toplevel 是**原生窗口**，底色不跟 ttk 主题走 ——
        #   不设 bg 就用系统默认（白/浅灰），那就是"小窗口夜间还是白的"的根因。
        try:
            win.configure(bg=theme_get("win_bg"))
            # ★ 登记一下，切主题时由 _retheme_custom_parts 统一刷新
            _reg = getattr(self, "_theme_windows", None)
            if _reg is None:
                _reg = self._theme_windows = []
            _reg.append(win)
        except Exception:
            pass
        win.title("📓 用法记录 —— 哪儿出过问题（本次 / 历史）")
        win.transient(self.root)
        try:
            win.geometry(_dlg_geom(900, 600))
        except Exception:
            pass
        outer = ttk.Frame(win, padding=10)
        outer.pack(fill="both", expand=True)

        # ★★ 2026-10-07 修（截图看出来的）：**底部按钮被挤没了**。
        #   原因：`Notebook` 先 `pack(fill="both", expand=True)` 把空间全吃掉，
        #   后面 `btns` 再 pack 就没地方了（截图里一个按钮都看不到）。
        #   ★ 正确顺序：**先把贴边的（bottom）摆好，再让中间那块 expand 去填剩下的。**
        #     这跟预览窗格那次是同一个道理（翻页条要先 pack 到底部）。
        btns = ttk.Frame(outer)
        btns.pack(side="bottom", fill="x", pady=(8, 0))

        nb = ttk.Notebook(outer)
        nb.pack(fill="both", expand=True)

        # 本次那边要用的数据先取出来（内存里的，很快）
        try:
            _this_text = self.dump_swallowed_report()
        except Exception as _e:
            _this_text = "生成报告失败：%s" % _e

        # ---------------- 页签 1：本次（原「体检报告」）----------------
        tab_now = ttk.Frame(nb, padding=10)
        nb.add(tab_now, text=T("  本次开程序  "))
        ttk.Label(
            tab_now,
            text=T("这是**这次开程序以来**记下的「没吭声的小毛病」（关窗口就清零）。\n"
                    "想看「老出问题的是哪些」→ 点上面那个「历史累计」页。\n"
                    "★ 把这里的内容发我即可，全是中文、不含你的文件名/路径。"),
            justify="left", font=(FONT, UI_FONT_SIZE)).pack(anchor="w",
                                                            pady=(0, 6))
        box = tk.Text(tab_now, width=76, height=20, wrap="none",
                      font=(FONT, UI_FONT_SIZE),
                      bg=theme_get("text_bg"), fg=theme_get("fg"),
                      insertbackground=theme_get("fg"),
                      relief="flat", highlightthickness=1,
                      highlightbackground=theme_get("line"))
        box.pack(fill="both", expand=True)
        box.insert("1.0", str(_this_text))
        box.configure(state="disabled")

        # ---------------- 页签 2：历史累计（原「用法记录」）----------------
        tab_hist = ttk.Frame(nb, padding=10)
        nb.add(tab_hist, text=T("  历史累计  "))

        try:
            recs = usage_read(limit=2000)
        except Exception:
            recs = []

        ttk.Label(
            tab_hist,
            text="这里记的是**跨次积累**的（关了程序也留着）——"
                 "按「出现次数」从多到少排，**排最上面的就是最该修的**。\n"
                 "★ 不包含文件名 / 路径 / 标签 / 搜索词。",
            justify="left", font=(FONT, UI_FONT_SIZE)).pack(anchor="w",
                                                            pady=(0, 8))
        agg = []
        try:
            agg = usage_summary()
        except Exception:
            agg = []

        if not recs and not agg:
            ttk.Label(tab_hist, text=T("（还什么都没记到 —— 挺好）"),
                      foreground=theme_get("ok"),
                      font=(FONT, UI_FONT_SIZE)).pack(anchor="w")
        else:
            wrap = ttk.Frame(tab_hist)
            wrap.pack(fill="both", expand=True)
            cols = ("where", "n", "last", "exc")
            # ★★ 2026-10-07 修「行高比字矮、文字被上下切掉」（用户报）：
            #   原来这句没给 style，于是用**系统默认行高**（约 20），
            #   装不下 14/13 号字（要 24 左右）→ 每行字被压扁。
            #   ★ 修法：跟目录树一样，注册一个带 `rowheight=_tree_row_height()`
            #     的样式再挂上（`_tree_row_height()` 是按字体算的，会跟着字号走）。
            try:
                _st = ttk.Style()
                _rh = _tree_row_height()
                _st.configure("UsageLog.Treeview",
                              background=theme_get("card_bg"),
                              foreground=theme_get("fg"),
                              fieldbackground=theme_get("card_bg"),
                              rowheight=_rh,
                              font=(FONT, UI_FONT_SIZE_SMALL))
                _st.configure("UsageLog.Treeview.Heading",
                              font=(FONT, UI_FONT_SIZE_SMALL, BOLD))
                tv = ttk.Treeview(wrap, columns=cols, show="headings", height=14,
                                  style="UsageLog.Treeview")
            except Exception:
                tv = ttk.Treeview(wrap, columns=cols, show="headings", height=14)
                # ★★ 2026-10-07 补：这棵树没给 style → 系统默认行高(约20)装不下字
                #   → 字被上下切掉（用户报「字体比行高长」）。按字体算行高。
                #   ★ 这个分支是"注册样式失败时的退路"，所以复用上面那个
                #     `UsageLog.Treeview` 的名字（同样的样式，不必再注册一份）。
                try:
                    _st_fb = ttk.Style()
                    _st_fb.configure("UsageLog.Treeview",
                        background=theme_get("card_bg"),
                        foreground=theme_get("fg"),
                        fieldbackground=theme_get("card_bg"),
                        rowheight=_tree_row_height(),
                        font=(FONT, UI_FONT_SIZE_SMALL))
                    _st_fb.configure("UsageLog.Treeview.Heading",
                        font=(FONT, UI_FONT_SIZE_SMALL, BOLD))
                    tv.configure(style="UsageLog.Treeview")
                except Exception:
                    pass
            for c, txt, wd in (("where", "哪儿出的问题", 360),
                               ("n", "次数", 60),
                               ("last", "最近一次", 150),
                               ("exc", "错误", 260)):
                tv.heading(c, text=txt)
                # ★ 2026-10-06：这里踩了一下 —— `column()` **没有 text 参数**，
                #   标题要用 heading() 设；column() 只管宽度和对齐。
                tv.column(c, width=wd,
                          anchor="center" if c == "n" else "w")
            for d in agg:
                try:
                    tv.insert("", "end", values=(d["where"], d["n"],
                                                 d["last"], d["exc"]))
                except Exception:
                    continue
            sb = ttk.Scrollbar(wrap, orient="vertical", command=tv.yview)
            tv.configure(yscrollcommand=sb.set)
            tv.pack(side="left", fill="both", expand=True)
            sb.pack(side="right", fill="y")

        # ---------------- 底部按钮（两个页签共用）----------------
        #   ★ 注意：这个 `btns` **已经在上面对 Notebook 之前 pack 好了**
        #     （必须先摆贴底的，否则会被 Notebook 的 expand 挤没）。

        def _copy_this():
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(str(_this_text))
                self.set_status(T("本次记录已复制到剪贴板"))
            except Exception as _e:
                note_swallowed(T("复制本次记录失败"), _e, quiet=True)

        def _save_this():
            try:
                p = filedialog.asksaveasfilename(
                    parent=win, title=T("保存本次记录"),
                    defaultextension=".txt", initialfile="用法记录-本次.txt")
                if not p:
                    return
                with open(p, "w", encoding="utf-8") as f:
                    f.write(str(_this_text))
                self.set_status(T("已保存到：{x}", x=p))
            except Exception as _e:
                note_swallowed(T("保存本次记录失败"), _e)

        def _open_file():
            try:
                p = _USAGE_PATH
                if p and os.path.isfile(p):
                    os.startfile(os.path.dirname(p))
                else:
                    messagebox.showinfo("用法记录", T("还没有记账文件。"),
                                        parent=win)
            except Exception as exc:
                messagebox.showerror("打不开", str(exc), parent=win)

        def _clear():
            if not messagebox.askyesno(
                    "清空历史记录",
                    "把**历史累计**的记录清掉？\n\n"
                    "（「本次开程序」那一页不受影响；"
                    "只是把「账本」清空，不影响程序任何功能）",
                    parent=win):
                return
            try:
                if _USAGE_PATH and os.path.isfile(_USAGE_PATH):
                    os.remove(_USAGE_PATH)
            except Exception:
                pass
            win.destroy()

        ttk.Button(btns, text=T("复制本次记录"), command=_copy_this).pack(
            side="left", padx=4)
        ttk.Button(btns, text=T("保存本次记录…"), command=_save_this).pack(
            side="left", padx=4)
        ttk.Button(btns, text=T("打开记账文件"), command=_open_file).pack(
            side="left", padx=4)
        ttk.Button(btns, text=T("清空历史记录"), command=_clear).pack(
            side="left", padx=4)
        ttk.Button(btns, text=T("关闭"), command=win.destroy).pack(
            side="right", padx=4)

        # ★ 顺便写进「问题」面板，这样关掉小窗还能回看（老行为保留）
        try:
            for _ln in str(_this_text).split("\n"):
                if _ln.strip():
                    self.log_problem(_ln, level="info")
        except Exception:
            pass

    def show_credits(self, parent=None):
        """★★★ 「关于」里的「版权与来源」详情窗。

        ★★ 为什么单独一个窗（不塞进「关于」）：
          · 版权声明**比较长**（要中英对照）—— 塞进「关于」会**挤爆**
          · ★ 而且**不是每个人都要看** —— 想看的人点一下就够

        ★ 为什么这个声明必须存在（★ 用户 2026-10-08 的要求）：
          > 「这个程序只是我提出设计的，代码全是你写的……
          >   深度求索公司也该有这程序一份版权」
          ★★ 关键那句：「**对 AI 来说每个对话窗口可能都是一次新生**」——
            它**不会来认领这份功劳**，所以**必须由人写下来**。
        """
        try:
            win = tk.Toplevel(parent or self.root)
            win.title(T("版权与来源"))
            win.transient(parent or self.root)
            win.resizable(True, True)
            try:
                win.configure(bg=theme_get("win_bg"))
            except Exception:
                pass
            try:
                _reg = getattr(self, "_theme_windows", None)
                if _reg is None:
                    _reg = self._theme_windows = []
                _reg.append(win)
            except Exception:
                pass

            body = ttk.Frame(win, padding=16)
            body.pack(fill="both", expand=True)

            ttk.Label(body, text=T("版权与来源声明"),
                      font=(FONT, UI_FONT_SIZE + 2, BOLD)).pack(anchor="w")
            ttk.Label(
                body,
                text=T("人提出、设计、验收；AI 写出全部代码。"),
                foreground=theme_get("fg_dim")).pack(anchor="w", pady=(2, 10))

            # ★ 正文：只读 Text（能选中复制、能滚）
            #   ★★ 注意：`tk.Text` **必须给 width**（错题本里踩过 ——
            #      不给就默认 80 字符宽 ≈ 884 像素，窗口"莫名其妙很宽"）
            box = tk.Text(body, width=72, height=17, wrap="word",
                          font=(FONT, UI_FONT_SIZE),
                          bg=theme_get("text_bg"), fg=theme_get("fg"),
                          relief="flat", padx=10, pady=8)
            box.pack(fill="both", expand=True)
            box.insert("1.0", T(_CREDITS_TEXT))
            box.configure(state="disabled")

            btns = ttk.Frame(body)
            btns.pack(fill="x", pady=(10, 0))
            try:
                ttk.Button(btns, text=T("打开仓库"), width=12,
                           command=lambda: _open_url(_REPO_URL)
                           ).pack(side="left")
            except Exception:
                pass
            ttk.Button(btns, text=T("确定"), width=10,
                       command=win.destroy).pack(side="right")
            try:
                win.bind("<Escape>", lambda e: win.destroy())
            except Exception:
                pass
            try:
                win.update_idletasks()
                rx = (parent or self.root).winfo_rootx()
                ry = (parent or self.root).winfo_rooty()
                rw = (parent or self.root).winfo_width()
                rh = (parent or self.root).winfo_height()
                win.geometry("+%d+%d" % (
                    rx + max(0, (rw - win.winfo_reqwidth()) // 2),
                    ry + max(0, (rh - win.winfo_reqheight()) // 4)))
            except Exception:
                pass
            try:
                win.grab_set()
            except Exception:
                pass
        except Exception as _e:
            note_swallowed(T("打开「版权与来源」失败"), _e)
            # 兜底：画不出来就退回系统弹窗（至少能看到内容）
            try:
                messagebox.showinfo(T("版权与来源"), T(_CREDITS_TEXT),
                                    parent=parent or self.root)
            except Exception:
                pass
    def show_about(self):
        """★ 关于。

        ★★ 2026-10-07：从 `messagebox.showinfo` **改成自己画的窗口**。
          为什么改：
            · 用户报「**关于对话框整片白**」—— 因为 `messagebox` 是
              **Windows 系统弹窗**，走系统 API，**颜色完全不受程序控制**
              （切夜间它也还是白的）。
            · 自己画的话就能跟主题走，还能顺便把信息排得好看点。
          ★ 顺带修：版本号原来写 **v24**，而标题栏是 **v26** —— 对不上了。
        """
        try:
            win = tk.Toplevel(self.root)
            win.title("关于")
            win.transient(self.root)
            win.resizable(False, False)
            # ★ Toplevel 是原生窗口，底色必须自己设（错题本 #92）
            try:
                win.configure(bg=theme_get("win_bg"))
            except Exception:
                pass
            # ★ 登记一下，切主题时跟着变
            try:
                _reg = getattr(self, "_theme_windows", None)
                if _reg is None:
                    _reg = self._theme_windows = []
                _reg.append(win)
            except Exception:
                pass

            body = ttk.Frame(win, padding=18)
            body.pack(fill="both", expand=True)

            ttk.Label(body, text=T("📁 文件标签管理器"),
                      font=(FONT, UI_FONT_SIZE + 3, BOLD)).pack(anchor="w")
            ttk.Label(
                body,
                text=T("带标签图结构、星图编辑、瀑布流浏览的本地文件标签工具。"),
                foreground=theme_get("fg_dim")).pack(anchor="w", pady=(4, 10))

            # ★★★ 版权与来源（2026-10-08）★★★
            #   ★ 用户要求「**一开始就醒目标明**」——
            #     所以放在**标题下面第一块**，不是最底下的小字。
            #   ★★ 为什么必须放在这里（不只是 README）：
            #     **下载 exe 的人不会去看 README，但他会点「关于」**。
            #   ★ 判据：**"声明要放在读者真正会到的地方"**。
            credit = tk.Frame(body, bg=theme_get("sel_bg") if
                              theme_get("sel_bg") else theme_get("win_bg"))
            credit.pack(fill="x", pady=(0, 12))
            tk.Label(
                credit,
                text=T("★ 代码由 AI（DeepSeek）编写 —— 人提出、设计、验收。"),
                bg=credit.cget("bg"), fg=theme_get("fg"),
                font=(FONT, UI_FONT_SIZE, BOLD),
                anchor="w", justify="left").pack(fill="x", padx=10, pady=(8, 2))
            tk.Label(
                credit,
                text=T("★ 版权由作者与深度求索（DeepSeek）共同持有。"),
                bg=credit.cget("bg"), fg=theme_get("fg_dim"),
                anchor="w", justify="left").pack(fill="x", padx=10, pady=(0, 8))
            info = [
                (T("版本"), "v26"),
                (T("当前界面缩放"), "%d%%" % int(self.ui_scale * 100)),
                (T("数据库"), str(DB_PATH)),
                (T("导出目录"), str(EXPORT_DIR)),
                (T("设置文件"), str(SETTINGS_PATH)),
            ]
            for k, v in info:
                row = ttk.Frame(body)
                row.pack(fill="x", pady=1)
                ttk.Label(row, text=k, width=12,
                          foreground=theme_get("fg_dim")).pack(side="left")
                # ★ 路径可能很长 → 用只读 Entry，能选中复制
                e = ttk.Entry(row, width=58, font=(FONT, UI_FONT_SIZE_SMALL))
                e.insert(0, v)
                e.configure(state="readonly")
                e.pack(side="left", fill="x", expand=True)

            btns = ttk.Frame(body)
            btns.pack(fill="x", pady=(14, 0))
            # ★ 版权详情入口（★ 声明正文比较长，单独一个窗看）
            ttk.Button(btns, text=T("版权与来源…"), width=14,
                       command=lambda: self.show_credits(win)
                       ).pack(side="left")
            # ★★ 支持入口（2026-10-08）
            #   ★ 为什么放在「关于」里：**这是真实用户唯一会看到的位置**
            #     （下载 exe 的人不会去翻 README）
            #   ★★ 用 `♥` 而不是 `💰` —— 前者是"心意"，后者是"要钱"，
            #     在开源项目里这个区别很重要。
            ttk.Button(btns, text=T("♥ 支持这个项目"), width=16,
                       command=lambda: _open_url(_SPONSOR_URL)
                       ).pack(side="left", padx=(6, 0))
            ttk.Button(btns, text=T("确定"), width=10,
                       command=win.destroy).pack(side="right")
            try:
                win.bind("<Escape>", lambda e: win.destroy())
                win.bind("<Return>", lambda e: win.destroy())
            except Exception:
                pass
            # 居中到主窗口
            try:
                win.update_idletasks()
                rx = self.root.winfo_rootx()
                ry = self.root.winfo_rooty()
                rw = self.root.winfo_width()
                rh = self.root.winfo_height()
                ww = win.winfo_reqwidth()
                wh = win.winfo_reqheight()
                win.geometry("+%d+%d" % (rx + (rw - ww) // 2,
                                         ry + (rh - wh) // 3))
            except Exception:
                pass
            try:
                win.grab_set()
            except Exception:
                pass
        except Exception as _e:
            note_swallowed(T("打开「关于」失败"), _e)
            # 兜底：实在画不出来就退回系统弹窗（至少能看到信息）
            try:
                messagebox.showinfo("关于", T("文件标签管理器 v26"), parent=self.root)
            except Exception:
                pass

    # ---------------- UI ----------------
    def _build_ui(self):
        # ★★ v26：**顶部这一行原来塞了 12 个控件，reqw 高达 1850 像素。**
        #   实测（窗口 1400 宽）：「位置」那两个下拉框和「⭐ 收藏」按钮
        #   **被挤成了 1 像素宽**，也就是你根本看不见它们
        #   （用识图看截图才发现：截图里「位置」后面是空的）。
        #   现在改成**两行**：
        #     第 1 行：收起侧栏 / 目录框 / 浏览 / 上一级 / 刷新 / 后退 / 前进
        #     第 2 行：位置（盘符 + 常用位置 + ⭐）
        #   这样哪一行都不会溢出，每个控件都完整可见。
        self._top_bar = ttk.Frame(self.root, padding=(10, 8, 10, 0))
        self._top_bar.pack(fill="x")

        self.toggle_btn = ttk.Button(self._top_bar, text="◀", width=3,
                                     command=self.toggle_sidebar)
        self.toggle_btn.pack(side="left", padx=(0, 6))

        ttk.Label(self._top_bar, text=T("目录")).pack(side="left", padx=(0, 6))
        self.path_var = tk.StringVar()
        entry = ttk.Entry(self._top_bar, textvariable=self.path_var)
        # ★ 不再 fill="x", expand=True —— 那样它会把后面的按钮全挤出去。
        #   给一个够用的固定宽度（宽度单位是字符数），后面的按钮就都有位置。
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<Return>", lambda e: self.load_directory(
            self._clean_path_input(self.path_var.get())))

        # ★ 这几个按钮从右往左排，保证它们在窗口变窄时**最后**才被影响
        ttk.Button(self._top_bar, text=T("刷新"), command=self.refresh_all).pack(
            side="right", padx=(4, 0))
        self._nav_fwd_btn = ttk.Button(self._top_bar, text=T("前进 ▶"), width=7,
                                       command=self.go_forward)
        self._nav_fwd_btn.pack(side="right", padx=(4, 0))
        self._nav_back_btn = ttk.Button(self._top_bar, text=T("◀ 后退"), width=7,
                                        command=self.go_back)
        self._nav_back_btn.pack(side="right", padx=(6, 0))
        ttk.Button(self._top_bar, text=T("上一级"), command=self.go_up).pack(
            side="right", padx=4)
        ttk.Button(self._top_bar, text=T("浏览…"), command=self.choose_dir).pack(
            side="right", padx=(6, 0))

        # ---- 第 2 行：位置（盘符 / 常用位置 / ⭐）----
        self._top_bar2 = ttk.Frame(self.root, padding=(10, 2, 10, 4))
        self._top_bar2.pack(fill="x")
        ttk.Label(self._top_bar2, text=T("位置")).pack(side="left", padx=(38, 4))
        self._drive_var = tk.StringVar()
        self._drive_cbo = ttk.Combobox(self._top_bar2, textvariable=self._drive_var,
                                       width=6, state="readonly")
        self._drive_cbo.pack(side="left")
        self._drive_cbo.bind("<<ComboboxSelected>>", self._on_drive_pick)

        self._place_var = tk.StringVar()
        self._place_cbo = ttk.Combobox(self._top_bar2, textvariable=self._place_var,
                                       width=22, state="readonly")
        self._place_cbo.pack(side="left", padx=(4, 0))
        self._place_cbo.bind("<<ComboboxSelected>>", self._on_place_pick)
        ttk.Button(self._top_bar2, text=T("⭐ 收藏当前位置"), width=14,
                   command=self._add_bookmark).pack(side="left", padx=(6, 0))

        # ★ 日志面板先 pack（在状态栏上方）
        self._build_log_panel()

        # ★ v25 补丁4：把「被吞掉的异常」接到日志面板上。
        #   以前 except: pass 的地方出错没人知道；现在这类提示会
        #   出现在「🔔 问题」面板 + 状态栏，方便查「点了没反应」。
        global _SWALLOW_SINK
        _SWALLOW_SINK = self.log_problem
        # ★★ 2026-10-05「先加说话」：额外装一道「出错必留痕」的保险。
        #   用户抱怨「卡死 / 显示不全 / 改着改着功能没了」，根子之一是
        #   六百多处「出错装没事」。上面这个 sink 只有**主动登记**的地方
        #   才会走；这里再补两手，让**没登记的**也能被看见：
        #     ① 后台线程里没被抓住的出错（线程崩了界面还在，最像「卡死」）
        #     ② 主循环里没被抓住的出错
        #   两手都只「记一笔」，绝不改变程序原有行为。
        try:
            self._install_error_spy()
        except Exception as _e:
            note_swallowed(T("装「出错必留痕」保险失败"), _e, quiet=True)

        # 状态栏
        status_bar = ttk.Frame(self.root)
        status_bar.pack(fill="x", side="bottom")
        # ★ 2026-10-03：顶部工具栏显示 / 隐藏（读取记住的状态）
        if not getattr(self, "_top_bar_visible", True):
            self._top_bar.pack_forget()
            self._top_bar2.pack_forget()
            self._topbar_btn.config(text=T("▼ 顶部"))
        self.status = ttk.Label(status_bar, text="", anchor="w",
                                padding=(12, 5))
        self.status.pack(side="left")
        # ★ v25 补丁10：紧挨着消息右边再加一块「当前视图信息」（分类/目录的项数等）。
        #   用户要求：别再把这类信息塞到标签条最右端 —— 放这儿不管标签条开着
        #   还是关着都看得见，也不会跟标签条上的内容重复。
        self._view_info_lbl = ttk.Label(status_bar, text="", anchor="w",
                                        foreground=theme_get("fg_dim"))
        self._view_info_lbl.pack(side="left", padx=(8, 0))
        # ★ v25 补丁42：给左边两块**限宽**。
        #   用户反馈：「最下面那一行经常因为『统计分类中』左边黑灰文字
        #   重复又太长，导致有不少按钮被挤掉了不显示」。
        #   右边那 8 个按钮（问题/输出/标签条/预览/标签库/网盘/标签盒）
        #   是 pack(side="right") 的，左边文字越长它们被挤得越靠外，
        #   长到一定程度就直接看不见了。
        #   这里给 status 和视图信息各一个**固定宽度上限**（宽度单位是
        #   字符数），配合 set_status 里的截断，双保险。
        try:
            self.status.configure(wraplength=0)
        except Exception:
            pass
        # 后面垫一个会伸缩的空框：把左边两块顶在最左，把右侧按钮顶到最右
        self._status_spacer = ttk.Frame(status_bar)
        self._status_spacer.pack(side="left", fill="x", expand=True)

        # 右下角活动指示器
        #   ★ 补丁42：**在这里就 pack 好**（side="left"，紧挨着伸缩框左边），
        #     不要再等用到的时候动态 pack —— 动态 pack 会挤到按钮那一侧，
        #     把按钮推出窗口。
        self._activity_count = 0
        self._activity_texts = []
        self._activity_frame = ttk.Frame(status_bar)
        self._activity_spinner_lbl = ttk.Label(
            self._activity_frame, text="", font=(FONT, UI_FONT_SIZE),
            foreground="#3498db")
        self._activity_spinner_lbl.pack(side="left")
        self._activity_text_lbl = ttk.Label(
            self._activity_frame, text="", foreground=theme_get("fg_dim"),
            font=(FONT, UI_FONT_SIZE))
        self._activity_text_lbl.pack(side="left", padx=(4, 0))
        # ★ 补丁42：用 before=伸缩框 精确控制位置 ——
        #   Tk 的 pack 是「按调用顺序排队」的，一旦 forget 过再 pack
        #   就会排到最后（=挤到按钮那一侧）。用 before= 就永远插在
        #   伸缩框左边，和按钮井水不犯河水。
        try:
            self._activity_frame.pack(side="left", padx=(8, 0),
                                      before=self._status_spacer)
        except Exception:
            pass
        try:
            self._activity_frame.pack_forget()
        except Exception:
            pass

        self._spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self._spinner_idx = 0
        self._spinner_job = None

        # ★ 状态栏最右侧：问题 / 输出 按钮
        # ★★ v25 补丁42：**这几个按钮会占很宽，窗口不够宽时要把它们挤掉。**
        #   用户反馈：「最下面那一行经常导致有不少按钮被挤掉了不显示」。
        #   实测原因：这台机器界面缩放 200%（tk scaling 2.0）下，
        #   `width=11` 的按钮**实际有 186 像素宽**，7 个按钮就要 1300+ 像素，
        #   窗口一窄就直接排到窗口外面。
        #   所以这里：
        #     ① 把 width 从 11 收到 8（文字也精简，够用就好）；
        #     ② 加一个 _fit_status_bar()：窗口一窄就**自动把按钮文字换成
        #        只有图标**（🔔 📋 🏷 📄 🔖 🧭 🗃），宽度再收一半。
        #        这样不管窗口调多小，按钮都还看得见、点得着。
        # ★★ v26：**按钮之间留点间隔 —— 现在挨得太紧、看着糊成一片。**
        #   用户反馈「字体大小分配得不够匀称，只能说能看」。
        #   截图放大看：右下角那几个按钮几乎**连在一起**
        #   （识别出来是「标签盒网盘:索引标签库 预览标签条…」），
        #   因为 padx 只给了 4 像素。现在统一放大到 8~10 像素。
        # ★★ 2026-10-07 **重新排序 + 分组配色**（用户给的方案）★
        #   ------------------------------------------------------------------
        #   用户原话：
        #     · 「撤销放在那一行最左边、在 C:\Users\someone 共 47 项（已刷... 的左边」
        #     · 「标签盒、标签库、标签条一个色调」
        #     · 「预览、顶部一个色调」
        #     · 「网盘：真实、问题（**输出按钮就不要了**，反正点开问题也有
        #        输出、问题、进度）各一个颜色」
        #     · 「感觉需要重新排序，然后给按钮增加底色什么的」
        #
        #   ★ 为什么要重排：这一排以前是**按"谁先写的"**排的，
        #     功能相近的散在两头（标签盒在最右、标签库在中间），
        #     用户每次都要**找**。现在按**功能分组**排，一眼能找到一类。
        #
        #   ★ 最终顺序（从左到右）：
        #       撤销 │ …左边留白/状态文字… │
        #       标签盒 · 标签库 · 标签条   ← A 组（紫色调：都是"标签"相关）
        #       预览 · 顶部               ← B 组（蓝色调：都是"看/布局"相关）
        #       网盘(索引)                ← C（青色调）
        #       问题                      ← C（橙红色调）
        #     ★ 「输出」按钮**已删掉**（用户要求：点开"问题"面板里就有输出页）。
        #
        #   ★ 配色怎么做的：ttk 的 `clam` 主题**不吃 `background`** ——
        #     直接 `configure(background=...)` 是没用的（试过，无效）。
        #     正确做法是**给每个色调单独注册一个 ttk 样式**（见
        #     `_make_tone_styles()`），然后用 `style=` 挂上去。
        #   ==================================================================
        try:
            _tones = self._make_tone_styles()
        except Exception:
            _tones = {}

        def _mk_btn(parent, key, text, tip, command, tone):
            """建一个"带底色"的状态栏按钮（越窄越自动缩成图标）。"""
            try:
                st = _tones.get(tone)
                b = ttk.Button(parent, text=text, width=0, command=command,
                               **({"style": st} if st else {}))
            except Exception:
                b = ttk.Button(parent, text=text, width=0, command=command)
            try:
                b._full_text = text
                b._tone = tone
            except Exception:
                pass
            if tip:
                try:
                    Tooltip(b, tip)
                except Exception:
                    pass
            return b

        # ---- 撤销：**紧贴最左边**（用户明确要求）----
        #   它是"补救"用的，平时用不着，但手一抖时得**一眼找到**。
        #   ★ 放最左而不是最右：用户说"在 C:\Users\someone 共 47 项 的左边"。
        self._undo_btn = _mk_btn(
            status_bar, "undo", T("↶ 撤销"),
            "撤销上一步（Ctrl+Z）／没东西可撤时是灰的",
            self.undo_do, "undo")
        self._undo_btn.configure(state="disabled")
        try:
            self._undo_btn.pack(side="left", padx=(6, 10))
        except Exception:
            pass

        # ---- 右边那一串（side="right" 是**从右往左**排，
        #      所以要按"最终顺序的反序"来建）----
        #   最终从左到右：标签盒 标签库 标签条 │ 预览 顶部 │ 网盘 │ 问题
        #   → 建的顺序（从右往左）：问题 → 网盘 → 顶部 → 预览 → 标签条 → 标签库 → 标签盒
        # ★ 每组之间用**大一点的 padx** 隔开，组内小一点 —— 这样"分组"
        #   不用画线也看得出来（视觉上就是"三三两两挨在一起"）。
        _GAP_IN = 3      # 组内
        _GAP_OUT = 14    # 组间

        # C 组：问题（最右）
        self._problem_btn = _mk_btn(
            status_bar, "problem", T("🔔 问题 0"),
            "打开「问题」面板（里面还有 输出 / 进度 两页）",
            lambda: self._toggle_log_panel("problems"), "problem")
        self._problem_btn.pack(side="right", padx=(_GAP_OUT, 10))
        # ★ 「输出」按钮删掉了（用户要求）—— 点开"问题"面板里就有输出页。
        #   这里保留一个名字上的空位说明，防止以后有人又加回来。
        self._output_btn = None

        # C 组：网盘
        self._net_btn = _mk_btn(
            status_bar, "net", "",
            "切换网盘浏览方式：索引（快）／真实（慢但最新）",
            self.toggle_net_browse, "net")
        self._net_btn.pack(side="right", padx=(_GAP_IN, 0))
        self._update_net_btn()

        # B 组：顶部
        self._topbar_btn = _mk_btn(
            status_bar, "top", T("▲ 顶部"),
            "显示 / 隐藏顶部工具栏",
            self.toggle_top_bar, "layout")
        self._topbar_btn.pack(side="right", padx=(_GAP_IN, _GAP_OUT))
        # B 组：预览
        self._preview_btn = _mk_btn(
            status_bar, "preview", T("📄 预览 ▲"),
            "显示 / 隐藏右侧预览窗格",
            self.toggle_preview, "layout")
        self._preview_btn.pack(side="right", padx=(_GAP_IN, 0))

        # A 组：标签条
        self._tagbar_btn = _mk_btn(
            status_bar, "tagbar", T("🏷 标签条 ▲"),
            "显示 / 隐藏标签条",
            self.toggle_tagbar, "tag")
        self._tagbar_btn.pack(side="right", padx=(_GAP_IN, _GAP_OUT))
        # A 组：标签库
        self._taglib_btn = _mk_btn(
            status_bar, "taglib", T("🔖 标签库 ▲"),
            "显示 / 隐藏右侧「标签库（星图缩略图）」",
            self.toggle_taglib, "tag")
        self._taglib_btn.pack(side="right", padx=(_GAP_IN, 0))
        # A 组：标签盒
        self._tagbox_btn = _mk_btn(
            status_bar, "tagbox", T("🗃 标签盒 ▲"),
            "显示 / 隐藏底部的标签盒",
            self.toggle_tagbox, "tag")
        self._tagbox_btn.pack(side="right", padx=(_GAP_IN, 0))

        # ★ 补丁42：窗口一窄就自动把按钮收成「只有图标」
        try:
            status_bar.bind("<Configure>", self._on_status_bar_config)
        except Exception:
            pass

        # 启动卡顿检测
        # ★★ 2026-10-06：真正的「打卡」交给一个**纯计算线程**（不碰界面），
        #   这样界面一忙就不会误判成「卡住」，也就不会出现
        #   「越卡越报、越报越卡」的死循环。
        self._heartbeat = time.time()
        try:
            _heartbeat_start()
        except Exception:
            pass
        # ★ v25 补丁25：快捷键改成「可自定义」。
        #   这里不再把按键写死，而是交给 _setup_shortcuts()：
        #   它按快捷键表（用户可以自己改，存在设置里）去绑定，
        #   改完立刻生效，不用重启程序。
        self._shortcut_binds = {}     # 动作键 -> 当前绑定的按键
        self._setup_shortcuts()
        # ★★ 2026-10-06：把「撤销记录本」准备好
        #   （会把上次关程序前的记录读回来 —— 关了再开还能撤）
        try:
            self._undo_init()
        except Exception as _e:
            note_swallowed(T("初始化撤销记录失败（本次开程序撤不了上次的事）"), _e,
                           quiet=True)
        # ★★ 2026-10-06：把「快速预览」准备好（空格键用它）
        self._quick_preview_init()
        # ★★ 2026-10-06：把「用法记录」（听诊器）准备好。
        #   ★ 只能在这儿 init —— 要等 DB_PATH 定下来才知道数据目录在哪。
        #     放在这一步**前面**的话，开机那一串报错就记不上了。
        try:
            _usage_init(str(Path(DB_PATH).parent / ".file_tagger_usage.jsonl"))
        except Exception as _e:
            note_swallowed(T("初始化用法记录失败（这次不记日志）"), _e, quiet=True)
        self.root.after(200, self._heartbeat_tick)
        threading.Thread(target=self._stuck_watchdog, daemon=True).start()

        # ★★ 2026-10-06：先把「上次用的皮肤」读出来 ——
        #   必须在建任何控件之前定下来，否则会先建一批浅色控件、
        #   再全部换一遍（又慢又可能闪一下）。
        #
        # ★★★ 2026-10-08 **加"自定义皮肤"的读取**（用户要"预留自定义皮肤入口"）★★★
        #   ★ 顺序很重要：**先注册自定义皮肤，再读"上次用的是哪套"** ——
        #     否则上次用的是自定义皮肤时，会被下面那句
        #     `if _saved_theme not in (...)  → 退回 light` 打回白天。
        #   ★ 这里就是"预留入口"的兑现状：以后做"导入皮肤"功能时，
        #     只要往设置里写 `custom_themes`，**这里自动就认**，
        #     启动流程一行都不用再改。
        try:
            _load_custom_themes()
        except Exception:
            pass
        try:
            _saved_theme = str(load_ui_setting("theme", "light") or "light")
        except Exception:
            _saved_theme = "light"
        # ★ 用 `theme_has()` 判断（**不再写死 light/dark**）
        if not theme_has(_saved_theme):
            _saved_theme = "light"
        try:
            global THEME_NAME
            THEME_NAME = _saved_theme
            _apply_theme_constants()
        except Exception:
            pass

        # ★★ 2026-10-03：先给「分栏条」配个样子，再建分栏 ——
        #   用户反馈：「界面大分区没有边框/阴影，拖动大小的时候经常需要
        #   看鼠标提示」。也就是说：四块之间看不出分隔线、拖不动的时候
        #   也不知道鼠标底下是可以拖的东西。
        #   这里做两件事：
        #     ① 把分栏条画粗一点、上点颜色（Tk 默认那一条几乎是看不见的）；
        #     ② 鼠标移到分栏条附近时，把光标换成「↔ 左右拖」的样子。
        #   ★ 2026-10-06：现在这一步会**把整套皮肤一次性套上**
        #     （按钮、滚动条、输入框、文件树、菜单全都包括），
        #     见 _style_sashes 里的说明。
        self._style_sashes()
        self.paned = ttk.Panedwindow(self.root, orient="horizontal")
        self.paned.pack(fill="both", expand=True, padx=8, pady=(0, 6))
        # 鼠标在分栏条附近 → 光标变成「可以左右拖」的样子
        try:
            self.paned.bind("<Motion>", self._on_paned_motion, add="+")
            self.paned.bind("<Leave>", self._on_paned_leave, add="+")
        except Exception as _e:
            note_swallowed(T("安装分栏条鼠标提示失败"), _e)

        # ★ 四块各自加一圈淡边，一眼能看出「这里是一块」
        self.sidebar = CategorySidebar(self.paned, self)
        self.list_frame = ttk.Frame(self.paned, style="Card.TFrame")
        # ★ v25 补丁8：右侧预览窗格（方案 A：分类库|文件列表|预览|标签库）
        #   默认隐藏、宽度可拖，点状态栏「📄 预览」按钮才出现。
        self.preview_frame = ttk.Frame(self.paned, style="Card.TFrame")
        self.tag_frame = ttk.Frame(self.paned, padding=(10, 0, 0, 0),
                                   style="Card.TFrame")
        try:
            # 左边那块是 tk.Frame —— 用高亮边框给它画一圈
            self.sidebar.configure(highlightthickness=1,
                                   highlightbackground=theme_get("line"),
                                   highlightcolor=theme_get("line"))
        except Exception:
            pass

        self.paned.add(self.sidebar, weight=0)
        self.paned.add(self.list_frame, weight=5)
        self.paned.add(self.preview_frame, weight=0)
        self.paned.add(self.tag_frame, weight=0)

        self._build_file_list(self.list_frame)
        self._build_preview_panel(self.preview_frame)
        self._build_tag_panel(self.tag_frame)

        # ★ v25 补丁13：导航（历史/盘符/常用位置）+ 拖放
        self._nav_hist = []
        self._nav_pos = -1
        self._nav_going = False
        try:
            self._refresh_places()
            self._update_nav_buttons()
        except Exception as _e:
            note_swallowed(T("初始化导航栏失败"), _e)
        try:
            self._setup_dnd()
        except Exception as _e:
            note_swallowed(T("初始化拖放失败"), _e)
        # ★ v25 补丁26：标签盒（默认隐藏，点状态栏「🗃 标签盒」才出来）
        try:
            self._build_tagbox()
        except Exception as _e:
            note_swallowed(T("初始化标签盒失败"), _e)
        # ★ v25 补丁27：鼠标悬停预览（停住 0.6 秒弹小窗，移开就没）
        try:
            self.hover = HoverPreview(self)
            cv = self.file_list.canvas
            cv.bind("<Motion>", self.hover.on_motion, add="+")
            cv.bind("<Leave>", self.hover.on_leave, add="+")
            self.file_list.canvas.bind(
                "<Button-1>",
                lambda e: (self.hover.on_leave(), None)[1], add="+")
        except Exception as _e:
            note_swallowed(T("初始化悬停预览失败"), _e)

        # 按上次的记忆决定预览窗格 / 标签库 一开始是开还是关（默认：预览关、标签库开）
        # ★★ 2026-10-03：顺便把**上次拉好的各分区宽度**读出来
        #   （用户要求「记住我调整的区域大小，关了程序再开还是我原来的比例」）。
        self._pane_sizes = {}
        try:
            _ps = load_ui_setting("pane_sizes", {}) or {}
            if isinstance(_ps, dict):
                self._pane_sizes = _ps
        except Exception:
            self._pane_sizes = {}
        self._preview_width = int(self._pane_sizes.get("pane_preview_w") or 0) or 380
        # ★★ 2026-10-05 修接错线：只有 pane_sizes 里**没记过**预览宽度时，
        #   才去读老版本的旧键 preview_width 当兜底。
        #   以前是无条件读、无条件盖——用户拉好的宽度会被旧值顶掉。
        try:
            if not int(self._pane_sizes.get("pane_preview_w") or 0):
                _old_pw = load_ui_setting("preview_width", 0) or 0
                if int(_old_pw) > 40:
                    self._preview_width = int(_old_pw)
        except Exception:
            pass
        self._taglib_width = int(self._pane_sizes.get("pane_taglib_w") or 0) or 380
        self._sidebar_width = int(self._pane_sizes.get("pane_sidebar_w") or 0) or 0
        self._preview_visible = bool(load_ui_setting("preview_visible", False))
        self._taglib_visible = bool(load_ui_setting("taglib_visible", True))
        self._top_bar_visible = bool(load_ui_setting("top_bar_visible", True))
        # ★★ 2026-10-05：分栏宽度的「记账闸门」——开机时先关着。
        #   只有两种情况会打开：
        #     ① 用户自己拖了分栏条（_on_paned_released）
        #     ② 正常关窗（on_close 里显式打开，把最终结果存下来）
        #   这样开机时的自动布局就**不会**把用户的比例冲掉了。
        self._pane_layout_ready = False
        # ★ 拖完分栏条 / 关窗时把宽度记下来
        try:
            self.paned.bind("<ButtonRelease-1>", self._on_paned_released, add="+")
        except Exception:
            pass
        if not self._preview_visible:
            try:
                self.paned.forget(self.preview_frame)
            except Exception:
                pass
        if not self._taglib_visible:
            try:
                self.paned.forget(self.tag_frame)
            except Exception:
                pass

        # ★ 按钮上的 ▲/▼ 要和真实状态一致（用上面记下来的状态变量，
        #   不能用 winfo_ismapped()：这时候窗口还没真正显示出来）
        try:
            self._preview_btn.config(
                text=T("📄 预览 ▼") if self._preview_visible else T("📄 预览 ▲"))
            self._taglib_btn.config(
                text=T("🔖 标签库 ▼") if self._taglib_visible else T("🔖 标签库 ▲"))
        except Exception:
            pass

        self.root.after(150, self._init_sash)

    # ---------- ★★ 2026-10-03：分栏条「看得见 + 拖得着」 ----------
    def _style_sashes(self):
        """把四个大分区之间的分栏条画清楚一点（Tk 默认那一条几乎看不见）。

        ★★ 2026-10-06：现在这里只是「按当前皮肤摆一次」的**薄薄一层** ——
          真正的样式表在 `_style_all_widgets()` 里（那边连按钮、滚动条、
          输入框、文件树、菜单全都一起管），皮肤一换整片都会跟着换。
          这样做的好处：以后加皮肤只要多写一张颜色表，不用改这里。
        """
        try:
            _style_all_widgets(self.root, THEME_NAME)
        except Exception as _e:
            note_swallowed(T("给界面套皮肤失败（会用 Tk 默认外观）"), _e)
        # ★★★ 2026-10-07 **修「状态栏那排按钮的彩色时有时无」**（用户报）★★★
        #   用户原话：「撤销 / 标签盒 / 标签库 / 标签条 / 预览 / 顶部 / 网盘
        #   **是彩色的，然后点了几下就又不彩了**，问题什么的也又变白了」。
        #
        #   ★ 真因（实测追出来的）：
        #     `_make_tone_styles()`（注册 `ToneTag.TButton` 那五个样式）
        #     **只在两个地方被调**：
        #       ① 建状态栏按钮的那一刻（`_build_status_bar` 里）
        #       ② 换皮肤之后（`_retheme_custom_parts` 里，行 ~27890）
        #     —— **`_apply_theme()` 这条路上没有它！**
        #     而 `_apply_theme()` 会调 `_style_all_widgets()`，
        #     那里重设了 `TButton` 的基础样式 ——
        #     **把刚注册的五个色调样式覆盖/冲掉了**。
        #
        #   ★ 实测证据：
        #       启动后立刻查 → `ToneTag.TButton configure = {}`（**空的！**）
        #       手动再调一次 `_make_tone_styles()` → `bg=#3b3050` ✔
        #     → 所以：**启动时没颜色；切一次皮肤才有颜色；
        #       之后某个操作又走 `_apply_theme` → 颜色又没了。**
        #       这跟用户描述的"时有时无"**完全对得上**。
        #
        #   ★ 修法：**在 `_style_all_widgets()` 之后立刻重注册一次** ——
        #     保证基础样式先铺好、再盖上我们的色调样式（顺序不能反）。
        try:
            self._make_tone_styles()
        except Exception as _e:
            note_swallowed(T("状态栏按钮分组底色注册失败"), _e, quiet=True)
        # ★★ 2026-10-06：**把标题栏 / 菜单栏染深**。
        #   ★★ 这里踩过一个坑，写清楚：一开始就在这儿直接调，**没生效**
        #      （截图看标题栏还是白的）。原因是：
        #      `_build_ui()` 跑在 `mainloop()` **之前**，这时候窗口
        #      **还没映射到屏幕上**，DWM 拿它没办法 —— 调用返回 0（成功）
        #      但不起作用，**是那种最坑的"静默失败"**。
        #      （对照实验：单独写个小窗口，先 `root.update()` 再调，
        #        标题栏立刻变深 (24,24,24) —— 证明接口本身没问题。）
        #   ★ 正解：**等窗口真的显示出来再调**。用 `after(0, ...)`
        #     把这件事推到事件循环里去（那时窗口已经映射好了）。
        #     `after(0)` 而不是延迟几百毫秒：尽量早点染，
        #     免得用户看见"先白一下再变黑"。
        try:
            _dark_now = (THEME_NAME == "dark")
            self.root.after(0, lambda d=_dark_now: _set_native_dark(
                self.root, d))
        except Exception as _e:
            note_swallowed(T("标题栏/菜单栏没能染成深色（老系统上正常）"), _e,
                           quiet=True)

    # ---------- ★★ 2026-10-06：皮肤（白天 / 夜间） ----------
    def set_theme(self, name, save=True):
        """换皮肤：整片界面立刻变。

        用户要求：「写套夜间皮肤，现在这个不开灯有点闪」。

        ★★ 2026-10-08 改成**支持任意已注册的皮肤**（用户要"预留自定义皮肤入口"）：
          原来这里写的是 `if name not in ("light", "dark")` ——
          **皮肤名硬编码**，以后加了自定义皮肤**会被这里打回去**（变回 light）。
          → 改成问 `theme_has(name)`（它读 `_THEMES`）。
          ★ 这样 `register_theme("my_skin", {...})` 一注册，
            这里就**自动认得**，一行都不用改。
        """
        try:
            if not theme_has(name):
                name = "light"
            self.set_status(T("正在换皮肤…"))
            apply_theme(self.root, name)
            # ★ 换完皮肤后，把「靠自己重画」的那几块重新画一遍 ——
            #   它们不是普通控件，颜色是代码画上去的，扫控件扫不到。
            for fn in (self._retheme_custom_parts,):
                try:
                    fn()
                except Exception as _e:
                    note_swallowed(T("换皮肤：重画自定义区块失败"), _e, quiet=True)
            try:
                if hasattr(self, "theme_var"):
                    self.theme_var.set(name)
            except Exception:
                pass
            if save:
                try:
                    save_ui_setting("theme", name)
                except Exception as _e:
                    note_swallowed(T("记住皮肤设置失败（下次打开可能变回白天）"), _e,
                                   level="warn")
            self.set_status("皮肤已切换：%s"
                            % ("夜间 🌙（晚上不刺眼）" if name == "dark"
                               else "白天 ☀"))
            try:
                self.log_output("🎨 已切换皮肤：%s"
                                % ("夜间" if name == "dark" else "白天"))
            except Exception:
                pass
            return True
        except Exception as _e:
            note_swallowed(T("换皮肤失败"), _e)
            return False

    def toggle_theme(self):
        """一键在白天 / 夜间之间来回切。"""
        cur = "dark" if THEME_NAME == "light" else "light"
        self.set_theme(cur)

    def _retheme_custom_parts(self):
        """★★ 换皮肤后，把「代码自己画颜色」的那几块重新画一遍。

        它们不是普通控件（颜色不是控件属性，是画上去的），
        上面那套「扫控件换色」扫不到 —— 必须自己重画。这里逐块叫一下，
        每一块单独包 try：**坏一块不影响别的**。
        这也是本程序一贯的写法（见「出错必留痕」那段）。
        """

        # ★★ 2026-10-07 新增：把**登记过的 Toplevel** 的底色刷一遍。
        #   为什么需要：`tk.Toplevel` 是原生窗口，底色不跟 ttk 主题走；
        #   建的时候设了 `bg=`，但**窗口开着切主题**时不会自己变 ——
        #   必须在这里再刷一次，否则"切了夜间、那个窗口还是白的"。
        #
        # ★★ 2026-10-08 增强：**不光刷底色，还要问窗口"你自己要不要重刷"**。
        #   ★ 为什么（用户报「索引管理切换夜间皮肤显示不对」，待清算 #8-②）：
        #     有些窗口（比如 `IndexManagerDialog`）**里面大量用原生 tk 控件**
        #     （`tk.Text` / `tk.Frame`）—— 它们的颜色是"建的时候设死的"，
        #     光刷**窗口自己**的底色**不够**，里面的控件还是旧配色。
        #   ★ 所以定一个约定：**窗口想要跟着皮肤变，就实现一个
        #     `_apply_theme()`**（无参数）—— 这里发现就调它。
        #     ★ 这样"怎么刷"由窗口自己决定，主程序不用知道它的内部结构
        #       （这也是"留接口"的思路，用户前面提过）。
        try:
            for _w in list(getattr(self, "_theme_windows", []) or []):
                try:
                    if not _w.winfo_exists():
                        continue
                    try:
                        _w.configure(bg=theme_get("win_bg"))
                    except Exception:
                        pass
                    # ★ 问窗口"你自己要不要重刷"
                    _fn = getattr(_w, "_apply_theme", None)
                    if callable(_fn):
                        try:
                            _fn()
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass
        # 顺手把「其他类自己建的窗口」也刷一下（它们把引用挂在 _theme_windows
        # 上的方式一样，只是 self 不是主程序 —— 那就在各自的类里处理，
        # 这里只管主程序自己开的那些）。

        # ★★ 2026-10-07 新增：**底部「输出 / 问题 / 进度」这三个 tk.Text**
        #   必须在这里重刷颜色！
        #   ★★ 为什么（这是个"第一次打开是白的、第二次才好"的怪 bug）：
        #     `_build_log_panel()` 在 **26840 行**被调，
        #     而"读出用户存的皮肤 + 套上去"在 **27116 ~ 27300 行** ——
        #     **也就是说：建这三个 Text 的时候，主题还是"白天"** →
        #     它们拿到了白底深字 → 后面套夜间时，
        #     `_retheme_tree()` 那套"扫控件换色"**扫不到 tk.Text 的文字色**
        #     （它只按"原始单据"翻颜色，而这几个控件的底色被别的逻辑改过），
        #     于是**第一次开就是白的**。
        #   ★ 第二次打开为什么好：设置文件里已经有 theme=dark，
        #     启动时 `THEME_NAME` 一开始就是 dark → 建 Text 时直接拿到深色。
        #   ★ 修法：**在这儿显式重刷一遍**（不依赖那套自动扫描）——
        #     这几个控件的颜色本来就从 `theme_get` 取，重设一次就对了。
        try:
            for _t, _bgkey in ((getattr(self, "_text_output", None),
                                "panel_bg2"),
                               (getattr(self, "_text_problems", None),
                                "panel_bg"),
                               (getattr(self, "_text_progress", None),
                                "panel_bg")):
                if _t is None:
                    continue
                try:
                    _t.configure(bg=theme_get(_bgkey), fg=theme_get("fg"),
                                 insertbackground=theme_get("fg"),
                                 selectbackground=theme_get("select_bg"),
                                 highlightbackground=theme_get("line"))
                except Exception:
                    pass
        except Exception:
            pass
        # ★ 顺带把「进程/问题/输出」的页签底也刷一下（ttk.Notebook 内部部件）
        try:
            if getattr(self, "_log_nb", None) is not None:
                self._log_nb.configure(style="TNotebook")
                for _f in self._log_nb.winfo_children():
                    try:
                        _f.configure(style="TFrame")
                    except Exception:
                        pass
        except Exception:
            pass

        # ★★ 2026-10-07 新增：**先把"登记过角色"的控件按当前皮肤刷一遍**。
        #   这是新的统一机制（见 `register_themed` 的说明）——
        #   以后新增控件只要 `register_themed(w, "card")`，这里自动管。
        try:
            apply_themed()
        except Exception:
            pass

        # ★★ 2026-10-08 新增：**换皮肤时也让图标尺寸重新按字高算一遍**。
        #   为什么换皮肤要重算图标：本程序换皮肤时会走
        #   `_style_all_widgets`（重设各种 ttk 样式、字体），
        #   **字高有可能跟着变**（不同主题下可能选到不同的字体度量）——
        #   而图标尺寸是**按字高算的**（待清算 #16 的修法），
        #   不清缓存就会"字变了、图标还是旧的"。
        #   ★ 一行成本，换"永远齐平"。
        try:
            FileList.refresh_icon_sizes()
        except Exception:
            pass

        # ★★ 2026-10-08 新增：**悬浮球也跟着换皮肤**。
        #   ★ 它是个**无边框独立窗口**，主程序那套"扫控件换色"扫不到它
        #     （跟 `IndexManagerDialog` 是同一个道理，见错题本 #123）——
        #     所以定个约定：**窗口想跟着皮肤变，就实现 `apply_theme()`**。
        #   ★★★ 2026-10-08 **后来改了**（用户选 B B B）★★★
        #     ★ 用户原话：「有球自己的皮肤也有主界面的皮肤，
        #       **两个都搞好入口**，但是**是完全不一样的**，你可别搞混了啊」
        #       然后他选了：② 球默认独立 ③ **永远不跟**主界面
        #     → 所以这里**不再**调球的 `apply_theme()`
        #       （球自己那套皮肤归 `set_ball_style()` 管）。
        #     ★ 但我**保留**这个调用位置、只是注释掉 —— 万一以后
        #       用户想加一个"球跟随主界面"的选项，**改一行就能回来**。
        #       （"留位置、不提前造"）
        # try:
        #     _fb = getattr(self, "floating_ball", None)
        #     if _fb is not None:
        #         _fb.apply_theme()
        # except Exception:
        #     pass

        # 文件列表 / 瀑布流（底色、文件名颜色、网格线都是画上去的）
        try:
            # ★★ 2026-10-07 **修一个一直在报错的 bug**（账本里 8 次）★★
            #   原来这里写的是 `self.list_frame._redraw()` ——
            #   而 `list_frame` 只是个 **ttk.Frame 空容器**（27242 行建的），
            #   **它没有 `_redraw` 方法** → 每次都抛
            #     `AttributeError: 'Frame' object has no attribute '_redraw'`
            #   → 被下面那个 except 吞掉 → **文件列表的夜间配色从来没刷上**。
            #   ★ 真正的列表对象是 `self.file_list`（一个 `FileList`，
            #     它才有 `_redraw`，见 10255 行）。
            #   ★ 后果（用户报的）：切皮肤后**文件列表还是白底黑字**；
            #     而且这段一报错，**后面该刷的（状态栏/底部面板）也跟着断**。
            lf = getattr(self, "file_list", None) or getattr(self, "list_frame", None)
            if lf is not None and hasattr(lf, "_redraw"):
                lf._redraw()
        except Exception as _e:
            note_swallowed(T("换皮肤：重画文件列表失败"), _e, quiet=True)
        # 左侧分类库的每条（名字、图标底色是画上去的）
        try:
            sb = getattr(self, "sidebar", None)
            if sb is not None and hasattr(sb, "_redraw_header"):
                sb._redraw_header()
        except Exception:
            pass
        # 预览窗格（画布底、类型信息、翻页条）
        try:
            pv = getattr(self, "preview", None)
            if pv is not None:
                if hasattr(pv, "_repaint_theme"):
                    pv._repaint_theme()
        except Exception as _e:
            note_swallowed(T("换皮肤：重画预览区失败"), _e, quiet=True)
        # 标签条（胶囊的底色是按标签颜色算的，得重刷）
        try:
            self._restyle_tagbar()
        except Exception:
            pass
        # 状态栏
        try:
            self._on_status_bar_config()
        except Exception:
            pass
        # ★★ 2026-10-07 新增：状态栏那排按钮的**分组底色**要重刷。
        #   为什么必须放这儿：ttk 样式的颜色是**注册时定死的** ——
        #   不重注册的话，从浅色切到夜间，那排按钮**还是白底**，
        #   在深色状态栏上像贴了几块膏药。
        try:
            self._make_tone_styles()
            # 样式名没变（还是 ToneTag.TButton 那些），重注册即可生效 ——
            # 不用重新给按钮挂 style。但**已经挂在按钮上的引用**要更新一下
            # （ttk 是按名字查样式的，所以其实自动就生效了）。
        except Exception:
            pass
        # ★★ 2026-10-07 新增：「文件 · 共 N · 未打标签 N · 仅中间标签 N」这几个
        #   标签。**用户报的"夜间看着不够亮、有时候黑了东点西点又好了"就是这个** ——
        #   它们的颜色原来是写死的、而且**从没登记过换皮肤重刷**，
        #   所以切到夜间它们不变，得靠某个偶然的重画才补上。
        try:
            self._retheme_stats_labels()
        except Exception:
            pass

    def _retheme_stats_labels(self):
        """把「文件 / 共 N / 未打标签 N / 仅中间标签 N」那一排的颜色刷成当前皮肤。

        ★★ 2026-10-07 新增。为什么要单独立一个方法：
          这排标签是**主界面最常瞄到**的几个字（每次看列表都在），
          但它们的颜色以前是**写死的**（"#555" / 深红 / 深黄），
          而且**没登记进换皮肤流程** —— 于是：
            · 夜间模式下"共 N"是深灰，**看不太见**
            · 切皮肤后它们**不跟着变**（用户说的"有时候黑了，东点西点又好了"）
          ★ 这跟错题本 #70（rowheight 写死 22）是同一类病根：
            **写死 + 漏登记**。凡是"自己指定颜色"的控件，都要问两句：
              ① 颜色是 theme_get 取的吗？  ② 换皮肤时会重刷吗？
        """
        for nm, key in (("stat_total_lbl", "fg"),
                        ("stat_untagged_lbl", "danger"),
                        ("stat_mid_lbl", "warn")):
            w = getattr(self, nm, None)
            if w is None:
                continue
            try:
                col = theme_get(key)
                # ttk.Label 用 configure(foreground=)，tk.Label 用 config(fg=)
                try:
                    w.configure(foreground=col)
                except Exception:
                    w.configure(fg=col)
                # ★ tk.Label 还得自己改底色（ttk 的不需要）
                try:
                    w.configure(background=theme_get("panel_bg"))
                except Exception:
                    pass
            except Exception as _e:
                try:
                    note_swallowed(T("换皮肤：刷统计标签失败（{x}）", x=nm), _e,
                                   quiet=True)
                except Exception:
                    pass
        # 列表标题「文件」两个字是 ttk.Label，跟着主题走，这里不用管

    def _make_tone_styles(self):
        """★ 给状态栏按钮注册"带底色"的 ttk 样式（按色调分组）。

        ★★ 2026-10-07 新增。用户要求：「给按钮增加底色什么的」，
          并且**按功能分组配色**：
            · 标签盒 / 标签库 / 标签条 → **一个色调**（紫，都是"标签"）
            · 预览 / 顶部             → **一个色调**（蓝，都是"看/布局"）
            · 网盘                    → **一个色调**（青，"数据来源"）
            · 问题                    → **一个色调**（橙红，"要你看的"）
            · 撤销                    → 单独一个（灰黄，"补救"）

        ★★ 为什么不能直接 `configure(background=...)`：
          **ttk 的 clam 主题不吃 background** —— 试过，`w.configure(
          background="#xxx")` 一点反应都没有（ttk 控件的颜色由 style 决定）。
          **正确做法：每个色调注册一个 `xxx.TButton` 样式**，
          再用 `style=` 挂到按钮上。这也是 ttk 唯一的正规路子。

        ★ 深浅两套都要注册（切皮肤时一起换）—— 所以这里读 `theme_get`，
          并且在 `apply_theme` 之后会**重跑一遍**（见 `_retheme_custom_parts`）。
        """
        try:
            st = ttk.Style()
        except Exception:
            return {}
        dark = (str(theme_get("name") or "") == "dark")
        # 每个色调：底色 / 悬停色 / 文字色
        #   ★ 夜间用"深一点的底色 + 亮一点的字"，浅色反过来 ——
        #     不然夜间会刺眼、浅色会糊（老毛病了，见错题本 #75）。
        if dark:
            spec = {
                "tag":     ("#3b3050", "#4a3d63", "#d9cdf0"),   # 紫
                "layout":  ("#26384f", "#2f4460", "#bcd6f5"),   # 蓝
                "net":     ("#1f3f3c", "#2a514d", "#a8ded6"),   # 青
                "problem": ("#4a2f26", "#5c3a2e", "#f0bda8"),   # 橙红
                "undo":    ("#3d3a26", "#4d4a30", "#e8dfae"),   # 灰黄
            }
        else:
            spec = {
                "tag":     ("#e8ddf7", "#dccbf2", "#4a2f7a"),   # 紫
                "layout":  ("#dcebfb", "#c9e0f7", "#1e4b80"),   # 蓝
                "net":     ("#d4f0ec", "#bfe6e0", "#0f5a52"),   # 青
                "problem": ("#fbe3da", "#f7d0c2", "#8a3a1e"),   # 橙红
                "undo":    ("#f5eecb", "#eee3b0", "#6b5a12"),   # 灰黄
            }
        out = {}
        for tone, (bg, hv, fgc) in spec.items():
            name = "Tone%s.TButton" % tone.capitalize()
            try:
                st.configure(name, background=bg, foreground=fgc,
                             borderwidth=0, focuscolor=bg, relief="flat",
                             padding=(8, 4))
                # 悬停 / 按下 / 禁用 三态都要给，不然一悬停就变回灰白
                st.map(name,
                       background=[("pressed", hv), ("active", hv),
                                   ("disabled", bg)],
                       foreground=[("disabled", theme_get("fg_dim"))],
                       relief=[("pressed", "flat"), ("active", "flat")])
                out[tone] = name
            except Exception:
                continue
        return out


    def _near_sash(self, x, y, slack=6):
        """鼠标是不是停在某个分栏条附近（±6 像素）。"""
        try:
            pw = self.paned
            n = len(pw.panes())
            if n < 2:
                return False
            horiz = (str(pw.cget("orient")) == "horizontal")
            p = int(x) if horiz else int(y)
            for i in range(n - 1):
                try:
                    sp = int(pw.sashpos(i))
                except Exception:
                    continue
                if abs(p - sp) <= slack:
                    return True
        except Exception:
            pass
        return False

    def _on_paned_motion(self, event):
        """鼠标在分栏条附近 → 换成「可以拖」的光标；离开就换回来。"""
        try:
            if self._near_sash(event.x, event.y):
                try:
                    horiz = (str(self.paned.cget("orient")) == "horizontal")
                except Exception:
                    horiz = True
                self.paned.configure(
                    cursor="sb_h_double_arrow" if horiz else "sb_v_double_arrow")
            elif str(self.paned.cget("cursor") or ""):
                self.paned.configure(cursor="")
        except Exception:
            pass

    def _on_paned_leave(self, event=None):
        try:
            self.paned.configure(cursor="")
        except Exception:
            pass

    # ---------- ★★ 2026-10-03：记住各分区大小 ----------
    def _on_paned_released(self, event=None):
        """松开分栏条 → 把宽度记下来（防抖，别拖一下就写盘）。

        ★★ 2026-10-05：**用户一动手，闸门就打开** —— 从此这个宽度才算数。
           （闸门见 `_save_pane_sizes` 的说明。）
        ★★ 2026-10-05 晚：这一句加 try 包住 —— 这是**绑在鼠标松开事件上**的，
           万一这里出问题绝不能连累「拖动」本身。拖动是 Tk 自己管的，
           这个方法只管「拖完记一笔」。

        ★★★ 2026-10-07 **修「拖完立刻点别的开关，宽度就刷没了」**（用户报）★★★
           ★ 用户原话：「**拖动分类库的宽度，点标签库、预览什么的就刷没了**」
           ★ 真因（实测复现）：
             原来这里**只安排了一个 `after(500)` 的延迟保存** ——
             **松手之后 500 毫秒内，`_pane_sizes` 还是空的**。
             而用户"拖完顺手就点下一个开关"**根本用不了 500 毫秒** →
             重排时读到"没记过宽度" → 用算法算一个（320 变成 395）。
             ★ 实测时间线：
               ① 拖到 320，松手          分类库 320   `_pane_sizes = {}`（**空的**）
               ② 立刻点「标签库」开关    分类库 **395**  ★ 这一步丢的
           ★ 修法（**立刻记 + 延迟写盘，两层**）：
             · **第一层（立刻）**：松手就 `_remember_pane_now()` ——
               只在内存里记、**不写盘**，所以不费事、也不怕频繁触发。
               ★ 这样"拖完马上点别的"读到的是**刚拖的值**。
             · **第二层（延迟）**：500 毫秒后再真写盘（防抖，原来的做法保留）。
           ★ 这就是用户要的"**多弄些冗余**" —— 一层不够就两层。
        """
        try:
            self._pane_layout_ready = True
        except Exception:
            pass
        # ★★ 第一层：**立刻**在内存里记下现状（不写盘，所以很快）
        try:
            self._remember_pane_now()
        except Exception:
            pass
        # ★★ 第二层：延迟 500ms 再写盘（防抖，别拖一下就写）
        try:
            if getattr(self, "_pane_save_job", None) is not None:
                return
        except Exception:
            pass

        def _do():
            self._pane_save_job = None
            self._save_pane_sizes()

        try:
            self._pane_save_job = self.root.after(500, _do)
        except Exception:
            self._pane_save_job = None

    def _save_pane_sizes(self):
        """把现在四个大分区各自的宽度记进设置文件。

        ★ 用户要求：「我希望软件能记住我调整的区域大小，能在把程序关了再开
          后还是我原来拉好的比例」。以前只有「预览窗格宽度」记了下来，
          左侧分类库和右侧标签库的宽度一关程序就忘了（每次开机都被
          自动算法重新排一遍）。

        ★★ 2026-10-05 修「比例记不住 / 有的太宽有的太窄」★★
           用户原话：「部分区域占的太宽、部分区域又占的太窄，然后拉动区域
           不会被记住比例，下次还这样」。
           查出来两个毛病：

           ● ① **开机时抄到的是「半成品宽度」**
                以前 `_save_pane_sizes()` 谁都能调，包括开机 500 毫秒后
                那次自动调用。可那会儿窗口才刚建好、自动排序还没跑完，
                抄下来的是**程序自己排的中间状态**，根本不是用户拉的比例。
                下一次开机照着这个错的摆 → 越摆越歪。
                修法：加 `_pane_layout_ready` 闸门 ——
                **只有「用户真的动手拉过」或「正常关窗」才允许记账**，
                开机自动排完那一下**不再覆盖**用户的比例。

           ● ② **「存」和「读」用的抽屉名不一样**（接错线，最坑）
                存的时候往 `pane_sizes` 这个抽屉里放，键名 `pane_preview_w`；
                可 23491 行读的时候**又去读了另一个抽屉** `preview_width`
                （老版本的旧键），而且**读到的值会盖掉刚读到的好值**。
                于是「用户拉过的预览宽度」被旧值顶掉 → 看起来就像没记住。
                修法：`pane_sizes` 说了算，旧键 `preview_width` **只在
                pane_sizes 里没有预览宽度时**才当兜底用。
        """
        try:
            # ★ 闸门：开机/自动布局期间不许写，免得把用户比例冲掉
            if not getattr(self, "_pane_layout_ready", False):
                return
            pw = self.paned
            panes = [str(p) for p in pw.panes()]
            if not panes:
                return
            data = dict(getattr(self, "_pane_sizes", {}) or {})

            # ★★★ 2026-10-07 **加一道"别用 Tk 重排的值覆盖用户的值"的保护** ★★★
            #   ★ 用户报：「**拖动分类库的宽度，点标签库、预览什么的就刷没了**」
            #   ★ 真凶（用钩子追出来的，铁证）：
            #       `toggle_taglib` 结尾有一句
            #           `self.root.after(400, self._save_pane_sizes)`
            #       —— 它跑的时候，"全撤 + 重加"已经让 Tk 把分类库
            #          从 320 重新分成了 **395**，于是 `_save_pane_sizes`
            #          **如实记下 395**，把用户拖的 320 覆盖掉。
            #       钩子输出（这是决定性证据）：
            #           [save] 之前=320  →  [save] 之后=395   ★
            #   ★ 为什么原来的 `_pane_layout_ready` 闸门拦不住：
            #     那道闸门只防"开机自动排"，**不防"用户操作引发的重排"**。
            #   ★ 修法：加一个"**正在重排**"的标记（`_pane_rearranging`）——
            #     重排期间（含它引发的延迟保存）**一律不写盘**，
            #     用之前 `_remember_pane_now()` 记下的值就够了。
            if getattr(self, "_pane_rearranging", False):
                return

            def _width(idx):
                try:
                    left = pw.sashpos(idx - 1) if idx > 0 else 0
                    right = (pw.sashpos(idx) if idx + 1 < len(panes)
                             else pw.winfo_width())
                    return max(0, int(right - left))
                except Exception:
                    return 0

            # ★★ 2026-10-07 修：**不在 paned 里的帧，宽度也要记住**。
            #   用户报「区域宽度又没法被记住了，下次打开又得重新拉」。
            #   实测真因：`preview_frame` 默认是被 `paned.forget()` 拿出去的
            #   （`preview_visible` 默认 False）→ 它**不在 panes 里** →
            #   下面这个循环**直接跳过它** → 它的宽度**永远存不下来**
            #   （实测存的是 `{'pane_sidebar_w':300,'pane_taglib_w':380}`，
            #     **就是少了 pane_preview_w**）。
            #   ★ 修法：算不出来就**保留上一次记的值**，绝不抹掉。
            for frame, key in ((self.sidebar, "pane_sidebar_w"),
                               (self.preview_frame, "pane_preview_w"),
                               (self.tag_frame, "pane_taglib_w")):
                s = str(frame)
                if s in panes:
                    w = _width(panes.index(s))
                    if w > 40:
                        data[key] = w
                    # w <= 40：这帧这会儿可能刚插进来还没排好 →
                    #          **保留旧的**（别用 0 或小值覆盖掉用户拉好的）
                # 不在 panes 里 → 什么都不做，`data` 里原来那个值会留着
            self._pane_sizes = data
            try:
                self._preview_width = int(data.get("pane_preview_w")
                                          or self._preview_width)
                self._taglib_width = int(data.get("pane_taglib_w")
                                         or getattr(self, "_taglib_width", 380))
                self._sidebar_width = int(data.get("pane_sidebar_w") or 0)
            except Exception:
                pass
            save_ui_setting("pane_sizes", data)
        except Exception as _e:
            note_swallowed(T("记住分栏大小失败"), _e)

    def _apply_saved_pane_sizes(self):
        """把上次记住的各分区宽度套回去。返回 True 表示真的套了。"""
        try:
            data = getattr(self, "_pane_sizes", None) or {}
            if not isinstance(data, dict) or not data:
                return False
            pw = self.paned
            total = int(pw.winfo_width())
            if total < 500:
                return False
            panes = [str(p) for p in pw.panes()]
            if len(panes) < 2:
                return False
            want = {}
            if str(self.sidebar) in panes:
                want[str(self.sidebar)] = int(data.get("pane_sidebar_w") or 185)
            if str(self.preview_frame) in panes:
                want[str(self.preview_frame)] = int(data.get("pane_preview_w") or 380)
            if str(self.tag_frame) in panes:
                want[str(self.tag_frame)] = int(data.get("pane_taglib_w") or 380)
            fixed = sum(want.values())
            if str(self.list_frame) in panes:
                # 文件列表吃掉剩下的（保底 300）
                want[str(self.list_frame)] = max(300, total - fixed - 16)
            x = 0
            for i in range(len(panes) - 1):
                x += int(want.get(panes[i], max(180, total // max(1, len(panes)))))
                pw.sashpos(i, int(min(x, total - 8)))
            return True
        except Exception as _e:
            note_swallowed(T("恢复分栏大小失败（按默认排）"), _e)
            return False

    def _auto_sash_sidebar(self, *a, **k):
        # ★★ 转发到 `AIxiede拆分开/程序分块/面板_面板布局.py`
        #   ★ 保留同名方法 = **所有调用方不用改**（稳定接口）
        return _面板面板布局._auto_sash_sidebar(self, *a, **k)


    def _relayout_panes_soon(self):
        """★ 补丁37：把分栏和左侧宽度再算一遍（防抖，避免连环触发）。

        什么时候用：文件列表的画布量出来只有 1 像素（拿不到尺寸）时。
        画布 1x1 会让 Tk **不再投递鼠标事件** —— 表现就是
        「单击选不中文件、只能框选」。
        """
        if getattr(self, "_relayout_job", None) is not None:
            return
        def _do():
            self._relayout_job = None
            try:
                self.root.update_idletasks()
                self._auto_sash_sidebar()
                self._layout_right_panes()
            except Exception:
                pass
        try:
            self._relayout_job = self.root.after(60, _do)
        except Exception:
            self._relayout_job = None

    def _init_sash(self):
        self.root.update_idletasks()
        try:
            total = self.paned.winfo_width()
            if total > 400:
                # ★★ 2026-10-03：先看有没有「上次记住的分区宽度」——
                #   有就照那个摆（用户要求「关了程序再开还是我拉好的比例」）；
                #   没有才用自动算法算一遍。
                if not self._apply_saved_pane_sizes():
                    self._auto_sash_sidebar()
                    self._layout_right_panes()
                else:
                    self._layout_right_panes()
        except Exception as exc:
            print("sash:", exc)
        # ★ 窗口完全加载后，再算一次，避免第一次算的时候尺寸还没稳
        self.root.after(400, self._auto_sash_sidebar)
        self.root.after(1000, self._auto_sash_sidebar)

    # ---------------- ★ v25 补丁8：预览窗格 / 标签库 ----------------
    def _build_preview_panel(self, parent):
        """右侧预览窗格（默认隐藏；只读，不会改文件）。"""
        self.preview = PreviewPane(parent, app=self)
        self.preview.pack(fill="both", expand=True)

    def _layout_right_panes(self, *a, **k):
        # ★★ 转发到 `AIxiede拆分开/程序分块/面板_面板布局.py`
        #   ★ 保留同名方法 = **所有调用方不用改**（稳定接口）
        return _面板面板布局._layout_right_panes(self, *a, **k)


    def _preview_index(self):
        """预览窗格在 paned 里排第几（没显示就返回 -1）。"""
        try:
            panes = [str(p) for p in self.paned.panes()]
            return panes.index(str(self.preview_frame))
        except Exception:
            return -1

    def toggle_preview(self):
        """★ v25 补丁8：显示 / 隐藏右侧预览窗格（默认隐藏、宽度可拖、会记住）。

        ★★ 2026-10-07 补：**跟 `toggle_sidebar` 一样，先把现状钉住**。
          用户报「点右侧区域标签库开关、预览开关应该还是这样」——
          意思是**右侧这两个开关也有"比例被重置"的毛病**。
          ★ 原来这里：
            · 关的时候**自己算了一遍宽度**（那段 `_preview_index()` 的逻辑），
              但它只在 `idx >= 0` 且算出来 120~2000 之间才记 —— **容易漏**；
            · 开的时候只 `_layout_right_panes()`，**没有"先记住现状"这一步**。
          ★ 现在统一：**开头先 `_remember_pane_now()`**（一次记全三个面板），
            关 / 开都受益，代码也少一大段。
        """
        try:
            # ★ 先把"现在各面板的宽度"钉住（关 / 开都用得上）
            try:
                self._remember_pane_now()
            except Exception:
                pass
            # ★★ 2026-10-07：标记"**正在重排分区**" —— 重排会把 sashpos
            #   改成 Tk 自己的值（实测 320→395），而本方法结尾安排的
            #   `after(400, _save_pane_sizes)` 会**如实记下那个错值**，
            #   把用户拖的宽度覆盖掉。
            #   → 重排期间不写盘（`_save_pane_sizes` 里会检查这个标记）。
            #   ★ 700 毫秒后才解除 —— 要比那个 400 毫秒的延迟保存晚。
            try:
                self._pane_rearranging = True
                self.root.after(700, lambda: setattr(self, "_pane_rearranging", False))
            except Exception:
                pass
            if self.preview_frame.winfo_ismapped():
                # ★ 补丁41：先改状态，再按新状态整体重排（不要单独 forget，
                #   免得出现「forget 了但状态没跟上」的不一致）
                self._preview_visible = False
                self._reinsert_tag_frame()
                self._preview_btn.config(text=T("📄 预览 ▲"))
                # ★★ 2026-10-07：**关也要把宽度摆回去** —— 全撤重加之后 Tk
                #   会把剩下的面板重新分，别的面板宽度就被挤动了
                #   （实测：关标签库，分类库 320 → 395）。
                try:
                    self.root.update_idletasks()
                except Exception:
                    pass
                self._restore_pane_widths()
                try:
                    self.root.after(60, self._restore_pane_widths)
                except Exception:
                    pass
                self.set_status(T("预览窗格：已隐藏"))
            else:
                # ★ v25 补丁41：这里原来是 paned.insert(idx, ...) 按序号硬塞。
                #   实测 ttk.PanedWindow 的 insert 索引**不能超过当前面板数**，
                #   而序号又是按「最终应该有 4 个面板」算的 —— 于是只要此刻
                #   少挂了一个面板就直接抛 "Slave index 2 out of bounds"，
                #   被 except 吞掉之后表现就是「点预览没反应」。
                #   现在统一走 _reinsert_tag_frame()：全撤掉、按正确顺序
                #   重加一遍，永远不可能越界。
                self._preview_visible = True
                self._reinsert_tag_frame()
                self._preview_btn.config(text=T("📄 预览 ▼"))
                self.set_status(T("预览窗格：已显示（选中文件即可预览，拖分隔线调宽度）"))
                # ★ 跟分类库一样：**等 Tk 把布局算完再摆宽度**，并补一次
                #   （踩过：`paned.add()` 之后立刻 `sashpos()` 会被夹成 0）
                try:
                    self.root.update_idletasks()
                except Exception:
                    pass
                # ★★★ 2026-10-07 **顺序：先让它摆右边比例，最后拿记住的值盖** ★★★
                #   `_layout_right_panes()` 是"按当前 sashpos 反推"摆的 ——
                #   而全撤重加之后 sashpos 已经是 Tk 的值（实测分类库 320→395），
                #   **所以它会把用户拖的宽度推回去**。
                #   → 让它先摆（它管"预览/标签库占多少"），
                #     **最后 `_restore_pane_widths()` 拿记下来的值盖一遍**，
                #     它才是最终说话的那个。
                self._layout_right_panes()
                self._restore_pane_widths()
                try:
                    self.root.after(120, self._restore_pane_widths)
                except Exception:
                    pass
            save_ui_setting("preview_visible", self._preview_visible)
        except Exception as _e:
            note_swallowed(T("切换预览窗格失败"), _e)

    def toggle_taglib(self):
        """★ v25 补丁8：显示 / 隐藏右侧的「标签库（星图缩略图）」整列。

        ★★ 2026-10-07 补：**跟 `toggle_sidebar` / `toggle_preview` 一样，
          开头先把现状钉住**。
          ★ 原来这里**关的时候一行都没记宽度**（对比 `toggle_preview` 还记了
            一点）→ 用户拉好标签库宽度、关一次、再开就**回到默认值**。
        """
        try:
            # ★ 先把"现在各面板的宽度"钉住
            try:
                self._remember_pane_now()
            except Exception:
                pass
            # ★★ 2026-10-07：标记"**正在重排分区**" —— 重排会把 sashpos
            #   改成 Tk 自己的值（实测 320→395），而本方法结尾安排的
            #   `after(400, _save_pane_sizes)` 会**如实记下那个错值**，
            #   把用户拖的宽度覆盖掉。
            #   → 重排期间不写盘（`_save_pane_sizes` 里会检查这个标记）。
            #   ★ 700 毫秒后才解除 —— 要比那个 400 毫秒的延迟保存晚。
            try:
                self._pane_rearranging = True
                self.root.after(700, lambda: setattr(self, "_pane_rearranging", False))
            except Exception:
                pass
            if self.tag_frame.winfo_ismapped():
                # ★ 补丁41：同 toggle_preview —— 改状态 + 整体重排
                self._taglib_visible = False
                self._reinsert_tag_frame()
                self._taglib_btn.config(text=T("🔖 标签库 ▲"))
                # ★★ 2026-10-07：**关也要把宽度摆回去** —— 全撤重加之后 Tk
                #   会把剩下的面板重新分，别的面板宽度就被挤动了
                #   （实测：关标签库，分类库 320 → 395）。
                try:
                    self.root.update_idletasks()
                except Exception:
                    pass
                self._restore_pane_widths()
                try:
                    self.root.after(60, self._restore_pane_widths)
                except Exception:
                    pass
                self.set_status(T("标签库：已隐藏"))
            else:
                # ★ v25 补丁41：**这里原来是 self.paned.add(...)，
                #   那是「追加到最后一位」—— 但标签库本该排在
                #   「分类库│文件列表│预览窗格│标签库」的第 4 位。
                #   于是关掉预览、再开标签库，标签库就跑到预览窗格
                #   该在的位置上了；接着 _layout_right_panes 按固定
                #   序号去挪分隔条，越界 → 日志里那条
                #   「切换预览窗格失败：TclError: Slave index 2 out of bounds」。
                #   现在改成按**正确的次序**插进去（和初始化时的顺序一致）。
                # ★★ 2026-10-07 修「标签库关开之后宽度变 0 / 面板消失」★★
                #   **顺序错了**：原来是
                #       self._reinsert_tag_frame()      # ← 这时读到的还是 False！
                #       self._taglib_visible = True     # ← 才设 True（太晚）
                #   → `_reinsert_tag_frame()` 里按 `_taglib_visible` 判断要不要插，
                #     读到 False → **标签库根本没被插回去**（实测：panes 里没有它，
                #     而 visible 标志已经是 True —— 两边不一致）。
                #   ✅ 必须**先设标志、再重排**（`toggle_sidebar` 就是这么写的，
                #     所以它是好的）。
                self._taglib_visible = True
                self._reinsert_tag_frame()
                self._taglib_btn.config(text=T("🔖 标签库 ▼"))
                self.set_status(T("标签库：已显示"))
                # ★ 等 Tk 算完布局再摆宽度（理由同 toggle_preview）
                try:
                    self.root.update_idletasks()
                except Exception:
                    pass
                # ★★★ 2026-10-07 **顺序：先摆右边比例，最后拿记住的值盖** ★★★
                #   理由同 `toggle_preview` —— `_layout_right_panes()` 会
                #   按 Tk 重排后的 sashpos（395）把用户拖的 320 推回去。
                self._layout_right_panes()
                self._restore_pane_widths()
                try:
                    self.root.after(120, self._restore_pane_widths)
                except Exception:
                    pass
            save_ui_setting("taglib_visible", self._taglib_visible)
            # ★ 2026-10-03：宽度变了也记一下
            try:
                self.root.after(400, self._save_pane_sizes)
            except Exception:
                pass
        except Exception as _e:
            note_swallowed(T("切换标签库显示失败"), _e)

    def _reinsert_tag_frame(self):
        """★ v25 补丁41：把右侧面板按正确顺序摆好。

        ★ 为什么不用 paned.insert()？
          实测（就是这条日志的元凶）：
            · ttk.PanedWindow 的 insert / forget **索引语义和 panes()
              返回的列表对不上** —— forget 一个中间面板之后，
              再 insert 到「看起来正确」的序号，Tk 会直接抛
              "Slave index N out of bounds"；
            · 而且 insert 的序号**不能超过当前面板数**，按 4 个面板
              算出来的位置去插，一旦此刻只挂着 2 个就必爆。
          这个报错原来被 except 吞掉、只记了一条「切换预览窗格失败」，
          但真实后果是**面板没插进去**（预览窗格点了没反应）。

        ★ 所以改成最笨也最可靠的办法：**全撤掉、按正确顺序重加一遍**。
          ttk.PanedWindow 一共就 4 个面板，重加一次的开销可以忽略
          （实测几十微秒），换来的是永远不可能越界。
        顺序：分类库 → 文件列表 → 预览窗格 → 标签库
              （不在的那几个自动跳过）
        """
        wanted = [self.sidebar, self.list_frame, self.preview_frame,
                  self.tag_frame]

        def _in_paned(w):
            """这个面板现在是不是挂在 paned 上。"""
            try:
                return str(w) in [str(p) for p in self.paned.panes()]
            except Exception:
                return False

        # ★ 分类库「应不应该显示」用**记忆**判断：
        #   第一次调用时记下它当时在不在，以后就照这个记忆走。
        #   为什么：_reinsert_tag_frame 会先全撤再重加，撤完那一刻
        #   「在不在」当然变成 False —— 如果每次都现查，第一次撤完
        #   分类库就永久消失了（实测踩过这个坑）。
        if not hasattr(self, "_sidebar_wanted"):
            self._sidebar_wanted = _in_paned(self.sidebar)
        visible = {
            str(self.sidebar): bool(self._sidebar_wanted),
            # ★ 文件列表**必须永远在**（它是主界面，丢了就什么都点不了）
            str(self.list_frame): True,
            str(self.preview_frame): bool(
                getattr(self, "_preview_visible", False)),
            str(self.tag_frame): bool(
                getattr(self, "_taglib_visible", True)),
        }
        # 先全撤掉（只撤真的挂着的，免得 Tk 报 "not managed"）
        for w in list(self.paned.panes()):
            try:
                self.paned.forget(w)
            except Exception:
                pass
        # 再按正确顺序加回来
        for w in wanted:
            if not visible.get(str(w), False):
                continue
            try:
                weight = 5 if w is self.list_frame else 0
                self.paned.add(w, weight=weight)
            except Exception as _e:
                note_swallowed(T("重新排列右侧面板失败"), _e)

    def _safe_list_title(self, text):
        """★ 补丁37：标题里**绝不能以省略号结尾**。

        实测过：标题文本以「…」结尾时，Tk 会把整个标签当成「竖直书写」——
        控件请求尺寸会变成 4 像素宽、几百万像素高，把文件列表挤成 1 像素；
        而 1 像素的画布收不到鼠标事件 → 单击选不中文件。
        所以标题里统一把结尾的省略号去掉。
        """
        try:
            t = str(text or "")
            while t and t[-1] in "…⋯":
                t = t[:-1]
            return t.rstrip() or "文件"
        except Exception:
            return "文件"

    def _fix_list_title_height(self):
        """★ 补丁37：兜底 —— 万一标题又被撑成竖直书写，记一条到「🔔 问题」。"""
        try:
            w = getattr(self, "list_title", None)
            if w is not None and w.winfo_reqheight() > 200:
                note_swallowed(
                    "文件列表标题被撑成了竖直书写（标题里别用省略号）",
                    RuntimeError("reqheight=%s" % w.winfo_reqheight()))
        except Exception:
            pass

    def _build_file_list(self, parent):
        head = ttk.Frame(parent)
        head.pack(fill="x", pady=(0, 4))

        # ★ v25 补丁37：**这里是「单击选不中文件」的真正元凶**。
        #   实测：给这个中文标题设 width=18（字符数宽度）时，Tk 量出来的
        #   请求尺寸是 **4 x 4,800,850 像素** —— 它把中文标题按「竖直书写」
        #   量了。这个巨大的请求高度会把整个文件区挤成 1 像素高，而
        #   **画布只有 1 像素时 Tk 就不再往它投递鼠标事件** →
        #   表现就是「单击完全没反应，框选却还能用」（框选靠拖动）。
        #   所以：① 不设 width（让标签自己按内容量）；② 文本里不要出现
        #   省略号（同样会触发竖排测量）；③ 万一还是被撑大，_fix_list_title_height
        #   会记一条到「🔔 问题」里。
        self.list_title = ttk.Label(head, text=T("文件"), font=(FONT, UI_FONT_SIZE, BOLD))
        self.list_title.pack(side="left")

        self.list_info = ttk.Label(head, text="", foreground=theme_get("danger"))
        self.list_info.pack(side="left", padx=8)

        # ★★ v26：**这几个数字之间要留够间隔。**
        #   实测（最大化截图）：状态条上显示成「共 800 未打标签 58」，
        #   两个数字**糊在一起**，看着像「800未」。
        #   原因：这里只给了 6~8 像素的 padx。
        #   现在统一改成 **左边距 18 像素**，一眼就能分开。
        # ★★ 2026-10-07 修「夜间看着还是不够亮看不清」（用户报）：
        #   原来这里是 `foreground="#555"` —— **写死的深灰**。
        #   夜间底色 #1e1f22 上，#555 对比度只有约 2，**基本看不见**；
        #   而且那句 `"共 5"` 是**每次看列表都会瞄到的**，最扎眼。
        #   现在改用主题正文色。
        #   ★ 另外三个标签（共N / 未打标签N / 仅中间标签N）原来**根本没登记**
        #     进"换皮肤要重刷"的名单 —— 所以切到夜间它们**不会跟着变**
        #     （用户说的「有时候它就黑了起来，东点西点一下就可能好了」就是这个：
        #      颜色压根没被刷上去，得靠某个偶然的重画才补上）。
        #     补登记在下面 `_retheme_stats_labels()` 里。
        self.stat_total_lbl = ttk.Label(head, text="",
                                        foreground=theme_get("fg"))
        self.stat_total_lbl.pack(side="left", padx=(16, 0))
        self.stat_untagged_lbl = tk.Label(
            head, text="", fg=theme_get("danger"), cursor="hand2",
            font=(FONT, UI_FONT_SIZE, "underline"))
        self.stat_untagged_lbl.pack(side="left", padx=(18, 0))
        self.stat_untagged_lbl.bind(
            "<Button-1>", lambda e: self.toggle_stats_filter("untagged"))
        self.stat_mid_lbl = tk.Label(
            head, text="", fg=theme_get("warn"), cursor="hand2",
            font=(FONT, UI_FONT_SIZE, "underline"))
        self.stat_mid_lbl.pack(side="left", padx=(18, 0))
        self.stat_mid_lbl.bind(
            "<Button-1>", lambda e: self.toggle_stats_filter("mid_only"))

        right_box = ttk.Frame(head)
        right_box.pack(side="right")

        self.layout_mode_var = tk.StringVar(value="list")
        ttk.Radiobutton(right_box, text=T("列表"), value="list",
                        variable=self.layout_mode_var,
                        command=self._on_layout_mode_change).pack(side="left")
        ttk.Radiobutton(right_box, text=T("瀑布流"), value="grid",
                        variable=self.layout_mode_var,
                        command=self._on_layout_mode_change).pack(side="left", padx=(4, 10))

        ttk.Label(right_box, text=T("缩略图：")).pack(side="left")
        self.icon_size_var = tk.IntVar(value=0)
        self.icon_scale = ttk.Scale(
            right_box, from_=0, to=5, orient="horizontal",
            variable=self.icon_size_var, length=110,
            command=self._on_icon_size_change)
        self.icon_scale.pack(side="left")
        self.icon_scale.bind("<ButtonRelease-1>", self._on_icon_scale_release)
        self.icon_size_label = ttk.Label(right_box, text=T("极小"), width=4)
        self.icon_size_label.pack(side="left", padx=4)

        # ★ 分页控件
        nav = ttk.Frame(parent)
        nav.pack(fill="x", pady=(0, 4))
        self.page_info_lbl = ttk.Label(nav, text="", foreground=theme_get("fg"))
        self.page_info_lbl.pack(side="left", padx=(4, 8))
        self.page_prev_btn = ttk.Button(nav, text=T("◀ 上一页"), width=10,
                                        command=self._page_prev)
        self.page_prev_btn.pack(side="left", padx=2)
        self.page_next_btn = ttk.Button(nav, text=T("下一页 ▶"), width=10,
                                        command=self._page_next)
        self.page_next_btn.pack(side="left", padx=2)
        self.page_jump_var = tk.StringVar()
        je = ttk.Entry(nav, textvariable=self.page_jump_var, width=7)
        je.pack(side="left", padx=(10, 2))
        je.bind("<Return>", lambda ev: self._page_jump())
        ttk.Button(nav, text=T("跳转"), width=6,
                   command=self._page_jump).pack(side="left")
        ttk.Label(nav, text=T("（每页 {n} 项）", n=FILE_PAGE_SIZE),
                  foreground=theme_get("fg_dim")).pack(side="left", padx=8)

        # ★ 两个独立刷新键
        ttk.Separator(nav, orient="vertical").pack(
            side="left", fill="y", padx=(10, 6))
        ttk.Button(nav, text=T("🔄 重扫本目录"),
                   command=self._refresh_current_dir_files).pack(
            side="left", padx=2)
        ttk.Button(nav, text=T("🏷 重读标签"),
                   command=self._refresh_current_dir_tags).pack(
            side="left", padx=2)

        self.file_list = FileList(
            parent,
            on_select=self.on_file_select,
            on_double=self.on_file_double,
            on_right_click=self.on_file_right_click,
            # ★ v25 补丁7：标签条挂到主窗口底部（整条占下方），不再是列表里的一行
            tagbar_parent=self.root,
        )
        self.file_list.pack(fill="both", expand=True)
        # ★ v25 补丁7：标签条的显示/隐藏交给主程序（要跟日志面板排前后）
        self.file_list.on_tagbar_visibility = self._pack_tagbar
        # ★ 注入"含子目录"搜索回调
        self.file_list.on_recursive_search = self._on_recursive_search
        self.file_list.on_global_search = self._on_global_search
        # ★ v24：注入标签条作用范围（当前页 / 整个视图）回调
        self.file_list.on_tag_scope_changed = self._on_tag_scope_changed
        self.file_list.on_tag_filter_view = self._on_tag_filter_view
        # ★ 补丁37：列表画布拿不到尺寸时 → 请主程序把分栏再算一遍
        #   （这是「单击选不中文件」的根因：画布 1x1 时 Tk 不投递鼠标事件）
        self.file_list.on_need_relayout = self._relayout_panes_soon
        # ★ 补丁37：列表里一些「决定了什么」的动作写进流水账，方便排查手感问题
        self.file_list.on_log_action = self.log_output
        # ★★ v26 补丁（2026-10-03）：把「标题被撑成竖直书写」的兜底处理方法
        #   交给文件列表调用 —— 这个方法只有主程序这边有（FileList 自己没有），
        #   以前列表那边直接 self._fix_list_title_height() 调不到，白报错。
        self.file_list.on_fix_title = self._fix_list_title_height
        # ★★ v26 补丁（2026-10-03）：**「拖到文件夹上松手 = 移动进去」接上。**
        #   文件列表在松手时会回调 on_move_to_folder，可以前主程序从来没给它
        #   赋过值（一直是 None）—— 所以拖过去松手什么都不会发生，
        #   而那行黄色提示却一直写着「拖到文件夹上松手 = 移动进去」。
        self.file_list.on_move_to_folder = self._move_paths_to_folder
        # ★★ 2026-10-03：把「安全信箱」也交给文件列表 ——
        #   它的缩略图后台线程要把「图读好了」交回主线程，
        #   直接调 after 会卡死（详见 _ui_threadsafe 的说明），
        #   从这条路走就绝不会卡。
        try:
            self.file_list.on_ui_call = self._ui_threadsafe
        except Exception as _e:
            note_swallowed(T("把后台信箱交给文件列表失败"), _e)
        self._recursive_cache = None
        self._recursive_active = False
        # ★ v25：作废「迟到的」目录树扫描结果（清搜索/切视图时 +1）
        self._recursive_token = 0
        self._recursive_roots = []
        # ★ v25：搜索前的视图快照，清空搜索时还原回去
        self._search_return_state = None

        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label=T("打开"), command=self.open_selected)
        self.menu.add_command(label=T("在文件夹中显示"), command=self.reveal_selected)
        self.menu.add_separator()
        # ★ v25 补丁9：文件基本操作（第二阶段）
        self.menu.add_command(label=T("重命名…（F2）"),
                              command=lambda: self._do_rename())
        self.menu.add_command(label=T("删除到回收站（Delete）"),
                              command=lambda: self._do_delete())
        self.menu.add_command(label="新建文件夹…（Ctrl+Shift+N）",
                              command=self._do_new_folder)
        # ★ v25 补丁12：复制 / 剪切 / 粘贴
        self.menu.add_separator()
        self.menu.add_command(label=T("复制（Ctrl+C）"),
                              command=lambda: self.copy_selected(cut=False))
        self.menu.add_command(label=T("剪切（Ctrl+X）"),
                              command=lambda: self.copy_selected(cut=True))
        self.menu.add_command(label=T("粘贴到当前文件夹（Ctrl+V）"),
                              command=self.paste_into_current)
        self.menu.add_separator()
        self.cat_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label=T("添加到分类"), menu=self.cat_menu)
        self.menu.add_command(label=T("从当前分类移除"),
                              command=self.remove_from_current_category)
        self.menu.add_separator()
        self.menu.add_command(label=T("清除全部标签"), command=self.clear_selected_tags)
        # ★★ v26（2026-10-01）新增（用户要的）：
        #   一个是“去除部分标签”（复选框 + 确认），
        #   一个是“把这个文件的标签全部丢进标签盒”。
        self.menu.add_command(label=T("🧹 去除文件上的标签…"),
                              command=self.remove_selected_tags)
        self.menu.add_command(label=T("📥 把标签全部加入标签盒"),
                              command=self.add_file_tags_to_box)
        # ★ v25 补丁23：属性（大小 / 权限 / 分享 / 收藏 / 时间 / 占父级百分比）
        self.menu.add_separator()
        self.menu.add_command(label=T("📋 属性…"),
                              command=self.show_properties)
        # ★ v25 补丁28：解压缩
        self.menu.add_separator()
        self.menu.add_command(label=T("📦 解压到当前文件夹"),
                              command=lambda: self.extract_archives(here=True))
        self.menu.add_command(label=T("📦 解压到 <文件名> 文件夹…"),
                              command=lambda: self.extract_archives(here=False))
        # ★ v25 补丁29：电子书
        self.menu.add_separator()
        self.menu.add_command(label=T("📖 用系统阅读器打开这本书"),
                              command=self.open_selected)

    # ---------- ★ v25 补丁25：快捷键（可自定义） ----------
    def _shortcut_actions(self):
        """动作键 → 具体干什么。这里是唯一把「名字」和「功能」连起来的地方。"""
        return {
            "delete": self.on_delete_key,
            "rename": self.on_rename_key,
            "select_all": self.on_select_all_key,
            "new_folder": self.on_new_folder_key,
            "copy": self.on_copy_key,
            "cut": self.on_cut_key,
            "paste": self.on_paste_key,
            "undo": self.on_undo_key,
            "nav_back": self.on_nav_back_key,
            "nav_forward": self.on_nav_forward_key,
            "toggle_tagbar": lambda e=None: self.toggle_tagbar(),
            "toggle_preview": lambda e=None: self.toggle_preview(),
            "toggle_taglib": lambda e=None: self.toggle_taglib(),
            "net_mode": lambda e=None: self.toggle_net_browse(),
            "refresh": lambda e=None: self.refresh_current_dir(),
            "search_focus": lambda e=None: self._focus_search_entry(),
            "quick_preview": self.on_quick_preview_key,
        }

    def _focus_search_entry(self):
        """★ Ctrl+F：跳到搜索框。

        ★★ 2026-10-07 修「Ctrl+F 之后界面整体变淡，近视看不清」（用户报）：
          病根不在 `focus_set()` 本身，而在**它顺带触发的"全选高亮"**。
          Tk 的 Entry 一拿到焦点、如果里面有字，很多情况下会显示成
          **选中态**（浅蓝底 `select_bg` + 深灰字）——
          原来那段 `select_bg` 是 `#cfe2ff`，**一满行浅蓝铺在搜索框里**，
          用户看到的就是"界面变淡了、看不清"。
          （浅色皮肤下尤其明显；深色皮肤下 `#31456b` 也偏闷。）

          修法三件（都很轻，不引入新状态）：
            ① 拿焦点之后，**把光标放到末尾、并且清掉选中区**
               —— 这样就是"正常白底 + 光标在最后"，不再有满行高亮。
            ② 顺手 `selection_clear()`，双保险（有些 Tk 版本 ① 不够）。
            ③ 最后把当前搜索内容**报给状态栏** —— 让用户知道
               "已经跳到搜索框了、现在在搜什么"，这也算补上 #46 说的那种"反馈"。
        """
        try:
            se = self.file_list.search_entry
        except Exception:
            return
        try:
            se.focus_set()
        except Exception:
            pass
        # ① + ② 去掉"全选高亮"，光标落到末尾
        try:
            n = len(se.get() or "")
            se.icursor(n)
            se.selection_clear()
        except Exception:
            pass
        # ③ 给个反馈（不吵，只写状态栏）
        try:
            cur = (se.get() or "").strip()
            if cur:
                self.set_status(T("搜索框已聚焦，当前搜索：{x}", x=cur))
            else:
                self.set_status(T("搜索框已聚焦，输入关键字即可搜索"))
        except Exception:
            pass

    # ---------------- ★★ 2026-10-06：空格快速预览（Quick Look）----------------
    def _quick_preview_init(self):
        """开机时把「快速预览」准备好（不弹窗，只建对象）。"""
        try:
            self.quick_preview = QuickPreview(self)
        except Exception as _e:
            self.quick_preview = None
            note_swallowed(T("快速预览没建起来（空格键会没反应）"), _e, quiet=True)

    def toggle_quick_preview(self):
        """菜单 / 空格键都走这里。

        ★★ 2026-10-07 修「快速预览没有开关的设置，只有开」（用户报）：
          查证结果：**开关功能本身是好的**（实测 is_open 能 关→开→关→开）。
          ★ 真正的原因有两个：
            ① 菜单名字叫「快速预览（**空格键**）」—— 看着像"快捷键说明"，
               **不像一个能开能关的开关**。→ 已改名「快速预览窗」，
               并且它现在**带状态圆点**（绿=开着 / 红=关着）。
            ② **没选中文件时点它，什么都不发生** ——
               `QuickPreview.open()` 里只有一句
               `set_status(T("先选中一个文件……"))`，
               而状态栏那行字很小、很容易没注意 →
               **用户以为"点了没反应、只能开"**。
               → 现在改成**弹一个明确的提示框**，告诉他要先选文件。
        """
        qp = getattr(self, "quick_preview", None)
        if qp is None:
            messagebox.showinfo(
                "快速预览",
                "快速预览没能启用。\n\n"
                "（多半是程序内部出了点小问题，不影响其它功能。）",
                parent=self.root)
            return
        # ★ 要"开"之前先检查：有没有选中文件 —— 没选就明确告诉他
        try:
            _will_open = not qp.is_open()
        except Exception:
            _will_open = False
        if _will_open:
            try:
                _cur = qp._current_path()
            except Exception:
                _cur = None
            if not _cur:
                messagebox.showinfo(
                    "快速预览",
                    "先**在文件列表里点一个文件**，再用快速预览。\n\n"
                    "（也可以直接按空格键 —— 一样要先选中文件）",
                    parent=self.root)
                try:
                    self.set_status(T("快速预览：先在列表里点一个文件"))
                except Exception:
                    pass
                return
        try:
            qp.toggle()
        except Exception as _e:
            note_swallowed(T("快速预览开关失败"), _e)
            messagebox.showwarning("快速预览", "打不开预览窗：%s" % _e,
                                   parent=self.root)
        # ★ 开关完刷一下菜单圆点（让"绿/红"立刻反映真实状态）
        try:
            self._refresh_menu_states()
        except Exception:
            pass

    def on_quick_preview_key(self, event=None):
        """★ 空格键入口。

        ★★ 两个务必：
          ① **正在输入框里打字时不能抢空格** —— 否则你在搜索框打不出空格，
             这是最容易被骂的那种 bug。所以先问 `_focus_is_input()`。
          ② **快速预览窗开着的时候，空格归它管**（用来关窗）。
             如果这里也响应，就会「关了又开」，来回抽搐。
        """
        try:
            if self._focus_is_input():
                return None
        except Exception:
            pass
        qp = getattr(self, "quick_preview", None)
        if qp is not None and qp.is_open():
            # 预览窗自己绑了空格（负责关掉），这里不再插手
            return None
        self.toggle_quick_preview()
        return "break"

    # ---------- ★ v25 补丁26：标签盒（整条横在窗口底部，可开关） ----------
    def _build_tagbox(self):
        """标签盒改成独立置顶小窗口。"""
        try:
            self.tagbox = TagBox(self.root, self, self.store)
            self.tagbox_visible = bool(load_ui_setting("tagbox_visible", False))
            if not self.tagbox_visible:
                self.tagbox.withdraw()
            self._update_tagbox_btn()
        except Exception as exc:
            try:
                note_swallowed(T("标签盒：创建失败"), exc)
            except Exception:
                pass

    def _update_tagbox_btn(self):
        """★ v25 补丁37：把状态栏那颗「🗃 标签盒」按钮的文字/箭头刷新一下。

        说明：这个方法以前只在文档里提过，代码里**没有定义** —— 于是
        「标签盒：创建失败：AttributeError: 'FileTaggerApp' object has no
        attribute '_update_tagbox_btn'」这种假故障会进「🔔 问题」面板
        （功能其实还能用，只是被这段异常打断了一次）。现在补上，
        并且顺便把按钮文字调成「开着 / 收着」对应的箭头。
        """
        try:
            vis = bool(getattr(self, "tagbox_visible", False))
            if getattr(self, "_tagbox_btn", None) is not None:
                self._tagbox_btn.config(
                    text=T("🗃 标签盒 ") + ("▼" if vis else "▲"))
        except Exception:
            pass

    def _pack_tagbox(self):
        try:
            if self.tagbox_visible:
                self.tagbox.deiconify()
                try:
                    self.tagbox.lift()
                except Exception:
                    pass
            else:
                self.tagbox.withdraw()
            self._update_tagbox_btn()
        except Exception:
            pass

    def toggle_tagbox(self):
        self.tagbox_visible = not getattr(self, "tagbox_visible", False)
        try:
            save_ui_setting("tagbox_visible", bool(self.tagbox_visible))
        except Exception:
            pass
        self._pack_tagbox()
        try:
            self.set_status(
                "标签盒：%s" % ("已显示（独立窗口，可拖动 / 缩放 / 置顶）"
                               if self.tagbox_visible else "已收起"))
        except Exception:
            pass

    def _redraw_tagbox(self):
        try:
            if getattr(self, "tagbox", None) is not None:
                self.tagbox._redraw()
        except Exception:
            pass

    def open_tagbox_picker(self):
        """从标签库勾选放进标签盒（菜单/按钮都走这里）。"""
        try:
            TagBoxPicker(self.root, self.tagbox)
        except Exception as exc:
            messagebox.showerror("标签盒", "打不开勾选窗口：%s" % exc,
                                 parent=self.root)

    def toggle_hover_preview(self):
        """★ 补丁27：鼠标悬停预览 开 / 关。"""
        try:
            self.hover.toggle()
        except Exception as exc:
            messagebox.showerror("悬停预览", "切换失败：%s" % exc,
                                 parent=self.root)

    def _open_cache_settings(self, *a, **k):
        # ★★ 转发到 `AIxiede拆分开/程序分块/面板_缓存设置.py`
        #   ★ 保留同名方法 = **所有调用方不用改**（稳定接口）
        return _面板缓存设置._open_cache_settings(self, *a, **k)


    def _set_preview_cache_dir(self, *a, **k):
        # ★★ 转发到 `AIxiede拆分开/程序分块/面板_缓存设置.py`
        #   ★ 保留同名方法 = **所有调用方不用改**（稳定接口）
        return _面板缓存设置._set_preview_cache_dir(self, *a, **k)


    # ---------- ★ v25 补丁28：解压缩 ----------
    def extract_archives(self, here=True):
        """把选中的压缩包解出来。

        here=True  → 解压到当前文件夹（会建一个和压缩包同名的子文件夹，更整齐）
        here=False → 解压到「压缩包名」文件夹里（在压缩包旁边）
        两种都会**先问一句**，而且**不会删你的压缩包**。
        """
        exe = seven_zip_exe()
        if not exe:
            messagebox.showwarning(
                "解压缩",
                "没找到 7-Zip 的 7za.exe。\n\n"
                "它应该在这里（免安装版）：\n"
                "  （把 7z.exe 放进程序目录，或设环境变量 SEVEN_ZIP）\n\n"
                "找不到的话，就重新解压一次那个 7-Zip 压缩包。",
                parent=self.root)
            return
        sel = list(self.file_list.get_selection() or [])
        zips = [p for p in sel
                if os.path.splitext(p)[1].lower() in ZIP_EXTS]
        if not zips:
            messagebox.showinfo(
                "解压缩",
                "选中的东西里面没有压缩包。\n\n"
                "支持：" + " ".join(sorted(ZIP_EXTS)), parent=self.root)
            return
        if here:
            # 解到「当前文件夹 / 压缩包名」这种子文件夹里，避免糊一屏
            base_dir = self.current_dir or os.path.dirname(zips[0])
        else:
            base_dir = os.path.dirname(zips[0])
        plan = []
        for z in zips:
            stem = os.path.splitext(os.path.basename(z))[0]
            plan.append((z, os.path.join(str(base_dir), stem)))
        if not messagebox.askyesno(
                "解压缩",
                "要解压这 %d 个压缩包吗？\n\n%s\n\n"
                "（原压缩包会保留，不会删）"
                % (len(plan),
                   "\n".join("  %s → %s" % (os.path.basename(a),
                                            os.path.basename(b))
                             for a, b in plan[:6])
                   + ("\n  …" if len(plan) > 6 else "")),
                parent=self.root):
            return

        def worker():
            ok = 0
            fails = []
            for z, dest in plan:
                good, msg = archive_extract(exe, z, dest)
                if good:
                    ok += 1
                    self.log_output("解压完成：%s → %s"
                                    % (os.path.basename(z), dest))
                else:
                    fails.append("%s：%s" % (os.path.basename(z), msg))
                    self.log_problem("解压失败：%s - %s"
                                     % (os.path.basename(z), msg),
                                     level="error")
            self._ui_threadsafe(self._extract_done, ok, fails, base_dir)

        self.begin_activity("正在解压 %d 个压缩包…" % len(plan))
        threading.Thread(target=worker, daemon=True).start()

    def _extract_done(self, ok, fails, base_dir):
        try:
            self.end_activity()
        except Exception:
            pass
        try:
            if ok:
                self.set_status("解压完成：%d 个成功%s"
                                % (ok, "，%d 个失败" % len(fails) if fails else ""))
                # 刷新一下，新解出来的东西就能看到
                try:
                    self.refresh_current_dir()
                except Exception:
                    pass
            if fails:
                messagebox.showwarning(
                    "解压缩", "有 %d 个没解开：\n\n%s"
                    % (len(fails), "\n".join(fails[:8])), parent=self.root)
            elif ok:
                messagebox.showinfo(
                    "解压缩", "解压完成：%d 个 ✓\n\n都放在：\n%s"
                    % (ok, base_dir), parent=self.root)
        except Exception:
            pass

    def _setup_shortcuts(self):
        """第一次绑定：把设置里的按键按上。"""
        self._apply_shortcuts(first=True)

    def _apply_shortcuts(self, first=False):
        """★ 补丁25：按当前的快捷键表重新绑定（改完立刻生效，不用重启）。

        先把上一次绑的**解绑**，再按新表绑 —— 否则改过的键会「新旧一起
        能用」，冲突起来很莫名其妙。
        """
        acts = self._shortcut_actions()
        # 1) 解绑上一次
        for name, seqs in list(getattr(self, "_shortcut_binds", {}).items()):
            cb = acts.get(name)
            for s in seqs:
                try:
                    self.root.unbind(s)
                except Exception:
                    pass
        self._shortcut_binds = {}
        # 2) 按表重新绑
        smap = load_shortcut_map()
        n_ok = 0
        _failed = []          # ★ 2026-10-06：绑不上的都攒着，最后一起告诉用户
        for name, label, _default in SHORTCUT_DEFS:
            key = smap.get(name, "")
            cb = acts.get(name)
            if not key or cb is None:
                continue
            seqs = shortcut_key_to_seq(key)
            bound = []
            for s in seqs:
                try:
                    self.root.bind(s, cb, add="+")
                    bound.append(s)
                    n_ok += 1
                except Exception as exc:
                    try:
                        note_swallowed(T("快捷键：绑定 {x}（{y}）失败", x=key, y=label),
                                       exc)
                    except Exception:
                        pass
            if bound:
                self._shortcut_binds[name] = bound
            else:
                _failed.append("%s（%s）" % (label, key))
        # ★★ 2026-10-06：**绑不上要告诉用户**，不能只记进账本。
        #   踩的坑：用户报「按空格没反应」，而账本里早就写着
        #   「绑定 Space 失败」—— 但**用户根本不知道去哪儿看**，
        #   于是这个功能从做完那天起就是坏的，谁也没发现。
        #   ★ 只在**第一次**（first=True）弹，免得改一次快捷键就弹一次。
        if _failed and first:
            try:
                self.root.after(1200, lambda: messagebox.showwarning(
                    "有快捷键没设上",
                    "下面这些快捷键在这个系统上用不了（其它功能不受影响）：\n\n  "
                    + "\n  ".join(_failed[:8])
                    + "\n\n你可以在「界面 → ⌨ 快捷键管理…」里换一个键。",
                    parent=self.root))
            except Exception:
                pass
        if not first:
            try:
                self.log_output(T("快捷键已重新绑定（共 {x} 个按键）", x=n_ok))
            except Exception:
                pass
        return n_ok

    def open_shortcut_dialog(self):
        """打开「快捷键管理」窗口。"""
        try:
            ShortcutDialog(self.root, self)
        except Exception as exc:
            messagebox.showerror("快捷键管理", "打不开窗口：%s" % exc,
                                 parent=self.root)

    def _on_layout_mode_change(self):
        mode = self.layout_mode_var.get()
        # ★★ 2026-10-07 修：原来这儿有一句
        #     `self.menu_layout_var.set(mode)`
        #   —— `menu_layout_var` 是「列表模式 / 瀑布流模式」那两个**菜单单选项**
        #   建的变量。菜单重排时那两项被**合并成一个开关**，变量不再建了，
        #   于是这一句抛 `AttributeError: 'FileTaggerApp' object has no attribute
        #   'menu_layout_var'` → **用户一点"显示方式"就弹错误框**（真事故）。
        #   ★ 修法：**先看变量在不在再赋值**（而不是删掉那句 ——
        #     万一日后有人把单选项加回来，这里还能同步）。
        try:
            mv = getattr(self, "menu_layout_var", None)
            if mv is not None:
                mv.set(mode)
        except Exception:
            pass
        self.file_list.set_layout_mode(mode)
        self._apply_icon_level(immediate=True)

    def _toggle_layout_from_menu(self):
        """★ 菜单里的「瀑布流模式」——**开关式**（原来是一对单选项）。

        ★ 2026-10-07：用户说「列表/瀑布流放设置或者也去了」，
          最后定的是**合并成一个开关**。
        ★ 状态圆点是**绿=瀑布流 / 红=列表**（见 `_menu_state_sources`）。
        ★ 走 `_on_layout_mode_change`（它负责同步两个变量 + 真正切布局），
          不自己重复实现 —— 免得两处逻辑走偏。
        """
        try:
            cur = str(self.layout_mode_var.get() or "list")
            new = "list" if cur == "grid" else "grid"
            self.layout_mode_var.set(new)
            self._on_layout_mode_change()
            try:
                self.set_status("显示方式：%s"
                                % ("瀑布流" if new == "grid" else "列表"))
            except Exception:
                pass
            self._refresh_menu_states()
        except Exception as exc:
            try:
                messagebox.showerror("切换显示方式", "切换失败：%s" % exc,
                                     parent=self.root)
            except Exception:
                pass

    def _on_icon_size_change(self, value):
        try:
            level = int(round(float(value)))
        except Exception:
            level = 0
        level = max(0, min(5, level))
        self._pending_icon_level = level
        self.icon_size_label.config(text=FileList.icon_sizes()[level][0])
        if self._slider_job is not None:
            try:
                self.root.after_cancel(self._slider_job)
            except Exception:
                pass
            self._slider_job = None
        self._slider_job = self.root.after(
            self.SLIDER_DEBOUNCE_MS, self._apply_pending_icon_level)

    def _on_icon_scale_release(self, event=None):
        if self._slider_job is not None:
            try:
                self.root.after_cancel(self._slider_job)
            except Exception:
                pass
            self._slider_job = None
        self._apply_pending_icon_level()

    def _apply_pending_icon_level(self):
        self._slider_job = None
        level = self._pending_icon_level
        if level == self._last_applied_level:
            return
        self._last_applied_level = level
        self.file_list.set_icon_level(level, clear_cache=True)

    def _apply_icon_level(self, immediate=False):
        try:
            level = int(round(float(self.icon_size_var.get())))
        except Exception:
            level = 0
        level = max(0, min(5, level))
        self._pending_icon_level = level
        self.icon_size_label.config(text=FileList.icon_sizes()[level][0])
        if immediate:
            self._last_applied_level = -1
            self._apply_pending_icon_level()

    def _build_tag_panel(self, *a, **k):
        # ★★ 转发到 `AIxiede拆分开/程序分块/面板_面板布局.py`
        #   ★ 保留同名方法 = **所有调用方不用改**（稳定接口）
        return _面板面板布局._build_tag_panel(self, *a, **k)


    # ---------------- 工具 ----------------
    @staticmethod
    def human_size(n):
        n = float(n)
        for u in ("B", "KB", "MB", "GB", "TB"):
            if n < 1024 or u == "TB":
                return f"{n:.0f} {u}" if u == "B" else f"{n:.1f} {u}"
            n /= 1024

    @staticmethod
    def file_kind(name):
        ext = os.path.splitext(name)[1].lower().lstrip(".")
        return ext.upper() if ext else "文件"

    def _view_info_text(self, *a, **k):
        # ★★ 转发到 `AIxiede拆分开/程序分块/面板_面板布局.py`
        #   ★ 保留同名方法 = **所有调用方不用改**（稳定接口）
        return _面板面板布局._view_info_text(self, *a, **k)

    def set_status(self, text):
        # ★★ 2026-10-03：**后台线程也能直接调**（之前只在主线程用）。
        #   原因：log_problem → set_status 这条路会在 _stuck_watchdog
        #   （后台线程，每秒跑一次）里被触发，self.status.config 直接
        #   在后台线程碰 Tk 控件，关窗瞬间偶发 -1073741819 崩溃。
        #   现在：先看是不是主线程，不在主线程就走 _ui_threadsafe 包一下。
        if (threading.current_thread() is not threading.main_thread()
                and getattr(self, "_ui_threadsafe", None) is not None
                and not APP_CLOSING):
            try:
                self._ui_threadsafe(self.set_status, text)
                return
            except Exception:
                pass     # 主程序关了 / 信箱满了 —— 退回去按原代码继续（再撞死也比丢字好）
        # ★★ v25 补丁42：**状态栏文字太长会把右边那排按钮挤出窗口。**
        #   用户反馈：「最下面那一行经常因为『统计分类中』左边黑灰文字
        #   重复又太长，导致有不少按钮被挤掉了不显示」。
        #   原因：self.status 是个没宽度上限的 ttk.Label，左边文字越长，
        #   它占的地方越大；右边那 7 个按钮是 pack(side="right") 的，
        #   位置被挤到窗口外面去了。
        #   修法：**按窗口实际宽度动态算能放多少字**（不是写死一个数）——
        #   窗口窄就少显示几个字，窗口宽就多显示。超出的部分进「📋 输出」。
        t = str(text or "")
        if len(t) > 6:
            try:
                avail = self._status_avail_px()
                if avail > 0:
                    # 用真字体量一次：这段文字要多少像素
                    f = tkfont.Font(family=FONT, size=UI_FONT_SIZE)
                    if f.measure(t) > avail:
                        # 逐字砍到放得下（两端夹逼，很快就出来）
                        lo, hi = 1, len(t)
                        while lo < hi:
                            mid = (lo + hi + 1) // 2
                            if f.measure(t[:mid] + "…") <= avail:
                                lo = mid
                            else:
                                hi = mid - 1
                        t = t[:max(1, lo)] + "…"
                        try:
                            self.log_output(str(text))   # 全文进输出面板
                        except Exception:
                            pass
            except Exception:
                # 量不出来就退回「按字数硬截」
                if len(t) > 58:
                    t = t[:57] + "…"
        try:
            self.status.config(text=t)
        except Exception:
            pass
        # ★ v25 补丁10：把「当前视图信息」显示在状态栏消息的**右边**。
        #   （以前是塞到标签条最右端；用户要求挪到这儿。）
        #   ★ 补丁42：它也必须**按剩余宽度截断** —— 实测它单独能占
        #     423 像素，正好把最左边那两个按钮（网盘 / 标签盒）顶出窗口。
        try:
            info = self._view_info_text(text)
            if info is not None:
                self._view_info_lbl.config(text=self._fit_view_info(info))
        except Exception:
            pass

    def _fit_view_info(self, *a, **k):
        # ★★ 转发到 `AIxiede拆分开/程序分块/面板_面板布局.py`
        #   ★ 保留同名方法 = **所有调用方不用改**（稳定接口）
        return _面板面板布局._fit_view_info(self, *a, **k)


    def _on_status_bar_config(self, event=None):
        """★ v25 补丁42：状态栏尺寸变了 → 重新决定按钮「带字还是只带图标」。

        只在真的需要切换时才动（窗口每动一下都重设文字会闪）。
        """
        try:
            if event is not None and event.widget is not self.status.master:
                return
        except Exception:
            pass
        try:
            w = self.status.master.winfo_width()
        except Exception:
            return
        if w <= 1:
            return
        # 7 个带字按钮大约要 7×160 + 间距 ≈ 1200；不够就收成图标
        want_icons = w < 1180
        if bool(getattr(self, "_status_icons_mode", None)) == want_icons:
            return
        self._status_icons_mode = want_icons
        self._fit_status_bar(want_icons)

    def _fit_status_bar(self, icons_only):
        """把右边那排按钮收成「只有图标」或恢复「图标+文字」。

        ★★ 2026-10-07：「输出」按钮**已删掉**（用户要求 —— 点开"问题"面板里
          就有输出页）。所以这里对它**做空值保护** ——
          直接 `self._output_btn.config(...)` 会 AttributeError，
          而它外面那层 try 会**默默吞掉**，导致后面几个按钮**全都不更新**
          （一个错连累一串，这个坑本程序踩过好几次了）。
        """
        def _set(btn, **kw):
            """按钮可能不存在（比如"输出"已删）—— 不存在就跳过，别连累后面。"""
            if btn is None:
                return
            try:
                btn.config(**kw)
            except Exception:
                pass

        try:
            if icons_only:
                _set(self._problem_btn,
                     text="🔔" + (str(self._problem_count)
                                  if self._problem_count else "0"),
                     width=4)
                _set(self._output_btn,
                     text="📋" + ("▼" if self._log_panel_visible else "▲"),
                     width=4)
                _set(self._tagbar_btn,
                     text="🏷" + ("▼" if getattr(self.file_list,
                                                 "tagbar_visible", False)
                                  else "▲"), width=4)
                _set(self._preview_btn,
                     text="📄" + ("▼" if getattr(self, "_preview_visible",
                                                 False) else "▲"), width=4)
                _set(self._taglib_btn,
                     text="🔖" + ("▼" if getattr(self, "_taglib_visible",
                                                 True) else "▲"), width=4)
                _set(self._tagbox_btn,
                     text="🗃" + ("▼" if getattr(self, "tagbox_visible", False)
                                  else "▲"), width=4)
                self._update_net_btn()
            else:
                _set(self._problem_btn,
                     text="🔔 问题 %d" % self._problem_count, width=0)
                _set(self._output_btn,
                     text=T("📋 输出 ") + ("▼" if self._log_panel_visible
                                       else "▲"), width=0)
                _set(self._tagbar_btn,
                     text=T("🏷 标签条 ") + ("▼" if getattr(
                         self.file_list, "tagbar_visible", False) else "▲"),
                     width=0)
                _set(self._preview_btn,
                     text=T("📄 预览 ") + ("▼" if getattr(
                         self, "_preview_visible", False) else "▲"), width=0)
                _set(self._taglib_btn,
                     text=T("🔖 标签库 ") + ("▼" if getattr(
                         self, "_taglib_visible", True) else "▲"), width=0)
                _set(self._tagbox_btn,
                     text=T("🗃 标签盒 ") + ("▼" if getattr(
                         self, "tagbox_visible", False) else "▲"), width=0)
                self._update_net_btn()
        except Exception:
            pass

    def _status_avail_px(self, *a, **k):
        # ★★ 转发到 `AIxiede拆分开/程序分块/面板_面板布局.py`
        #   ★ 保留同名方法 = **所有调用方不用改**（稳定接口）
        return _面板面板布局._status_avail_px(self, *a, **k)


    def toggle_tagbar(self):
        """★ v25 补丁7：显示 / 隐藏标签条（默认隐藏）。

        标签条现在是**整条底部面板**（横跨整个窗口，和「🔔 问题 / 📋 输出」
        一样），不再挤在文件列表那一列里。
        """
        try:
            vis = not getattr(self.file_list, "tagbar_visible", False)
            self.file_list.set_tagbar_visible(vis)
            self._tagbar_btn.config(
                text=T("🏷 标签条 ▼") if vis else T("🏷 标签条 ▲"))
            self.set_status(T("标签条：已显示") if vis
                            else "标签条：已隐藏（点右下角「🏷 标签条」再看）")
        except Exception as _e:
            note_swallowed(T("切换标签条显示失败"), _e)

    def _pack_tagbar(self, visible):
        """★ v25 补丁7：把标签条当成「整条底部面板」显示 / 收起。

        打包方式和「📋 输出」日志面板完全一致（side=bottom + before=状态栏），
        所以它和输出/问题一样是横跨整个窗口底部的整条，而不是列表里的一行。
        """
        try:
            tb = self.file_list.tagbar
            if visible:
                try:
                    tb.pack(fill="x", side="bottom",
                            before=self.status.master)
                except Exception:
                    tb.pack(fill="x", side="bottom")
            else:
                tb.pack_forget()
        except Exception as _e:
            note_swallowed(T("显示/隐藏底部标签条失败"), _e)

    # ---------------- ★ 日志面板 ----------------
    def _build_log_panel(self):
        self._log_panel = ttk.Frame(self.root)
        # 初始不显示

        nb = ttk.Notebook(self._log_panel)
        nb.pack(fill="both", expand=True, padx=4, pady=(4, 2))

        self._log_nb = nb

        # 输出页
        f_out = ttk.Frame(nb)
        nb.add(f_out, text=T("输出"))
        self._text_output = tk.Text(
            f_out, wrap="none", width=48, height=10, font=("Consolas", UI_FONT_SIZE),
            bg=theme_get("panel_bg2"), fg=theme_get("fg"), borderwidth=0,
            highlightthickness=0,
            # ★ 2026-10-07 加行距（用户报「行高比字矮、字挤在一起」）：
            #   Tk Text 默认 spacing1/spacing3 都是 0 ——
            #   也就是"字多高就占多高"，**一点喘气空间都没有**。
            #   实测 Consolas 14 的 linespace = 25，紧贴着看就很挤。
            #   上下各留 2 像素，整片就松快了。
            spacing1=2, spacing3=2)
        sb1 = ttk.Scrollbar(f_out, orient="vertical",
                            command=self._text_output.yview)
        self._text_output.configure(yscrollcommand=sb1.set)
        sb1.pack(side="right", fill="y")
        self._text_output.pack(side="left", fill="both", expand=True)
        self._text_output.configure(state="disabled")

        # 问题页
        f_prob = ttk.Frame(nb)
        nb.add(f_prob, text=T("问题"))
        self._text_problems = tk.Text(
            f_prob, wrap="none", width=48, height=10, font=("Consolas", UI_FONT_SIZE),
            bg=theme_get("panel_bg"), fg=theme_get("fg"), borderwidth=0,
            highlightthickness=0, spacing1=2, spacing3=2)
        sb2 = ttk.Scrollbar(f_prob, orient="vertical",
                            command=self._text_problems.yview)
        self._text_problems.configure(yscrollcommand=sb2.set)
        sb2.pack(side="right", fill="y")
        self._text_problems.pack(side="left", fill="both", expand=True)
        self._text_problems.configure(state="disabled")
        self._text_problems.tag_configure("warn", foreground=theme_get("warn"))
        self._text_problems.tag_configure("error", foreground=theme_get("danger"))
        self._text_problems.tag_configure("info", foreground=theme_get("accent"))

        # 进度页
        f_prog = ttk.Frame(nb)
        nb.add(f_prog, text=T("进度"))
        self._text_progress = tk.Text(
            f_prog, wrap="none", width=48, height=10, font=("Consolas", UI_FONT_SIZE),
            bg=theme_get("panel_bg"), fg=theme_get("fg"), borderwidth=0,
            highlightthickness=0, spacing1=2, spacing3=2)
        sb3 = ttk.Scrollbar(f_prog, orient="vertical",
                            command=self._text_progress.yview)
        self._text_progress.configure(yscrollcommand=sb3.set)
        sb3.pack(side="right", fill="y")
        self._text_progress.pack(side="left", fill="both", expand=True)
        self._text_progress.configure(state="disabled")

        # 底部：清空 / 关闭
        bottom = ttk.Frame(self._log_panel)
        bottom.pack(fill="x", padx=4, pady=(0, 4))
        ttk.Button(bottom, text=T("清空当前"), width=10,
                   command=self._clear_current_log_tab).pack(side="left")
        ttk.Button(bottom, text=T("复制全部"), width=10,
                   command=self._copy_current_log_tab).pack(side="left",
                                                            padx=(4, 0))
        ttk.Button(bottom, text=T("▲ 收起"), width=8,
                   command=self._hide_log_panel).pack(side="right")

    def _toggle_log_panel(self, which="output"):
        if self._log_panel_visible:
            self._hide_log_panel()
            return
        self._show_log_panel(which)

    def _show_log_panel(self, which="output"):
        try:
            self._log_panel.pack(fill="x", side="bottom",
                                 before=self.status.master)
        except Exception:
            try:
                self._log_panel.pack(fill="x", side="bottom")
            except Exception:
                return
        self._log_panel_visible = True
        try:
            idx = {"output": 0, "problems": 1, "progress": 2}.get(which, 0)
            self._log_nb.select(idx)
        except Exception:
            pass
        try:
            self._output_btn.config(text=T("📋 输出 ▼"))
        except Exception:
            pass

    def _hide_log_panel(self):
        try:
            self._log_panel.pack_forget()
        except Exception:
            pass
        self._log_panel_visible = False
        try:
            self._output_btn.config(text=T("📋 输出 ▲"))
        except Exception:
            pass

    def _clear_current_log_tab(self):
        try:
            idx = self._log_nb.index(self._log_nb.select())
        except Exception:
            idx = 0
        widget = (self._text_output, self._text_problems,
                  self._text_progress)[idx]
        try:
            widget.configure(state="normal")
            widget.delete("1.0", "end")
            widget.configure(state="disabled")
        except Exception:
            pass
        if idx == 1:
            self._problem_count = 0
            self._update_problem_badge()
        if idx == 0:
            self._output_lines = 0
        if idx == 2:
            self._progress_lines = 0

    def _copy_current_log_tab(self):
        try:
            idx = self._log_nb.index(self._log_nb.select())
        except Exception:
            idx = 0
        widget = (self._text_output, self._text_problems,
                  self._text_progress)[idx]
        try:
            content = widget.get("1.0", "end")
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.set_status(T("已复制到剪贴板"))
        except Exception:
            pass

    def _append_to_text(self, widget, text, tag=None):
        try:
            widget.configure(state="normal")
            widget.insert("end", text + "\n", tag if tag else ())
            widget.see("end")
            widget.configure(state="disabled")
        except Exception:
            pass

    def _now_str(self):
        try:
            return datetime.now().strftime("%H:%M:%S")
        except Exception:
            return ""

    def _ui_alive(self):
        """★ v25 补丁18：窗口还在吗？（后台线程往界面回话之前必须先问一句）

        实测 bug：程序关窗时，后台的「看门狗线程」还在每秒跑一次、还在
        往界面 root.after()，窗口一销毁它就撞空 —— 进程直接访问违规退出
        （退出码 -1073741819，表现就是「关窗闪退」）。所以这里统一守一道。
        """
        if APP_CLOSING:
            return False
        if getattr(self, "_closing", False):
            return False
        return True

    # ---------- ★★ 2026-10-03：后台线程「回主线程」的安全通道 ----------
    def _ui_threadsafe(self, fn, *a):
        """从**后台线程**把一件事交回主线程做 —— 绝不卡住、绝不丢。

        ★ 为什么不能用 self.root.after()：实测（在假家目录里把程序跑起来，
          用真鼠标真点击测的时候发现的）后台线程调 `root.after()` 会在
          tkinter 内部的 createcommand 上**卡死** —— Tcl 解释器同一时刻
          只允许一个线程碰它；主线程正在事件循环里的时候，后台线程这一步
          就可能永远等下去（线程还活着，但永远不会返回）。

          卡住的后果特别隐蔽、也特别烦：
            · `_bg_scan_worker`（后台扫目录）干完活要 root.after 回一句
              「扫完了」—— 这步一卡，主程序里「正在扫描」那个标记
              （_bg_scan_running_dir）就**永远挂着**，
              于是**以后打开任何没有缓存的文件夹都不会再扫，列表一直空着**。
            · log_output 也一样，卡一次就少一批日志。
          （实测就是这么复现的：新目录永远停在「首次扫描中…」。）

        ★ 现在改成走「信箱」：后台线程只往一个 Python 列表里塞东西
          （加锁，不碰 Tcl，绝不会卡）；主线程每 60 毫秒把信箱取空。
        """
        if APP_CLOSING or getattr(self, "_closing", False):
            return
        try:
            with self._ui_queue_lock:
                self._ui_queue.append((fn, a))
        except Exception:
            pass

    def _ui_poll(self):
        """（主线程）把后台线程塞进「信箱」的活儿干一遍。

        ★★ 2026-10-06：**这里顺手排一遍预览那边的信箱**。
          为什么要在这里也排一遍：
            预览的后台渲染（PDF 页数、图片、电子书）干完活之后，
            把结果排进了「预览专用信箱」，本来是靠预览窗格自己的
            200 毫秒小闹钟去取的。但那个小闹钟**只在真正打开程序、
            走完整启动流程之后才开始转**（比如某些启动分支、
            或者别的窗口抢了 after 的活儿时会漏）。
            一旦它没转起来，表现就是：
              **预览区一直停在「正在打开…」，页面永远不出来。**
            所以这里主程序的信箱轮询（每 60 毫秒、一定在跑）
            也捎带手排一遍 —— 双保险，谁在跑都能把结果送到。
        """
        self._ui_poll_job = None
        try:
            while True:
                with self._ui_queue_lock:
                    if not self._ui_queue:
                        break
                    fn, a = self._ui_queue.popleft()
                try:
                    fn(*a)
                except Exception as _e:
                    note_swallowed(T("后台线程交回主线程的活儿失败了"), _e)
        except Exception:
            pass
        # ★ 顺手把「预览专用信箱」也排一遍（见上面说明）
        try:
            _drain_ui_mail(60)
        except Exception:
            pass
        try:
            if not APP_CLOSING and not getattr(self, "_closing", False):
                self._ui_poll_job = self.root.after(60, self._ui_poll)
        except Exception:
            pass

    def log_output(self, text):
        line = f"[{self._now_str()}] {text}"
        self._output_lines += 1
        if not self._ui_alive():
            return
        try:
            self._ui_threadsafe(self._append_to_text, self._text_output, line)
        except Exception as exc:
            # ★★ 2026-10-03：之前 except: pass，_ui_threadsafe 失败就静默丢日志。
            #   改成至少记一笔 warn，方便排查「为什么某段日志没出现」。
            note_swallowed(T("log_output：回主线程写「输出」面板失败"), exc,
                           level="warn")

    def log_progress(self, text):
        line = f"[{self._now_str()}] {text}"
        self._progress_lines += 1
        if not self._ui_alive():
            return
        try:
            self._ui_threadsafe(self._append_to_text, self._text_progress, line)
        except Exception as exc:
            note_swallowed(T("log_progress：回主线程写「进度」面板失败"), exc,
                           level="warn")

    def log_problem(self, text, level="warn"):
        """level: warn / error / info"""
        line = f"[{self._now_str()}] {text}"
        self._problem_count += 1
        # ★★ 2026-10-06：顺手记进「用法记录」（听诊器）。
        #   ★ 放在 `_ui_alive()` 检查**前面** —— 关窗那一刻报的问题
        #     也得记上（那正是最容易出问题的时候）。
        #   ★★ 但**要防重复记**：`note_swallowed` 也会把同一件事弹到
        #     「问题」面板、从而走到这里。不防的话同一个错会被记两次，
        #     汇总出来的次数直接翻倍（实测踩到了）。
        #     判据：这条 text 是不是刚从 note_swallowed 过来的。
        try:
            if not self._log_problem_is_echo(text):
                _usage_note("problem", text, level=level,
                            extra=self._usage_view_hint())
        except Exception:
            pass
        if not self._ui_alive():
            return
        # ★★ 2026-10-07 修「**问题按钮的颜色/数字第一次变化有延迟**」（用户报）★★
        #   ★ 真因（实测量出来的）：
        #     `_update_problem_badge` 原来**只走 `_ui_threadsafe`**（信箱），
        #     而主线程**每 60 毫秒**才把信箱取空一次 →
        #     所以点出一个错之后，**按钮上的数字要等最多 60ms 才变**。
        #     实测：
        #       立刻(5ms 后) → text 还是「问题 1」（**没变**）
        #       120ms 后    → 才变成「问题 2」
        #     ★ 用户看到的"延迟"就是这个。
        #
        #   ★ 修法：**如果当前就在主线程，直接改，立刻生效**；
        #     只有真从后台线程来的时候才走信箱（那时必须走，见
        #     `_ui_threadsafe` 的说明：后台线程碰 Tcl 会卡死）。
        #     ★ 这也是本程序里已有的写法（搜 `current_thread() is
        #       threading.main_thread` 能找到同样的判断）。
        _on_main = False
        try:
            _on_main = (threading.current_thread()
                        is threading.main_thread())
        except Exception:
            _on_main = False
        try:
            self._ui_threadsafe(self._append_to_text, self._text_problems,
                                line, level)
            if _on_main:
                # ★ 就在主线程 —— 立刻刷，别等那 60 毫秒
                self._update_problem_badge()
                try:
                    self._text_problems.see("end")
                except Exception:
                    pass
            else:
                self._ui_threadsafe(self._update_problem_badge)
        except Exception as exc:
            note_swallowed(T("log_problem：回主线程写「问题」面板失败"), exc,
                           level="warn")
        try:
            self.set_status(f"⚠ {text}")
        except Exception:
            pass

    def _usage_view_hint(self):
        """★ 2026-10-06：记下「出错时用户在看哪个视图」。

        ★★ 只返回**视图种类**这种非隐私信息，绝不带路径 / 文件名 / 标签名。
           （外面查到的血泪教训：带路径的日志用户不敢发给别人看。）
        """
        try:
            vm = str(getattr(self, "view_mode", "") or "")
            m = {"dir": "文件夹", "cat": "分类", "all": T("全部文件")}
            base = m.get(vm, vm or "未知")
            if getattr(self, "net_browse_mode", "") == "real":
                base += "+网盘实时"
            return base
        except Exception:
            return ""

    def _log_problem_is_echo(self, text):
        """★ 2026-10-06：判断这条「问题」是不是刚从 note_swallowed 弹过来的。

        为什么要这个：`note_swallowed` 出错时会调 `log_problem` 把话弹到
        「问题」面板 —— 于是**同一件事走了两条路进用法记录**，
        汇总出来的次数会翻倍（实测：一次错误记成 2 条）。

        ★★ 这里踩了一次，写清楚：**不能去读账本文件来判断**。
           因为 `note_swallowed` 只是把记录塞进**内存缓冲**，
           要等攒够 20 条或过 5 秒才落盘。而 log_problem 是**紧接着**
           被调用的 —— 那时候磁盘上根本没有那条 swallow 记录，
           拿文件去比对永远比不着（实测：还是记重了）。

           正确的判据在**内存**里：`note_swallowed` 更新过的
           `_SWALLOW_LAST`（"刚才谁在哪儿报的"）。拿它比一下就行。
        """
        try:
            t = str(text or "")
            if not t:
                return False
            last = _SWALLOW_LAST.get("where") or ""
            if last and t.startswith(str(last) + "："):
                return True
            return False
        except Exception:
            # ★ 判不出来就当**不是**回声（宁可多记一条，也别把真问题漏了）
            return False

    def _update_problem_badge(self):
        try:
            n = self._problem_count
            if n > 0:
                self._problem_btn.config(text=T("🔔 问题 {n}", n=n))
            else:
                self._problem_btn.config(text=T("🔔 问题 0"))
        except Exception:
            pass

    # ---------------- ★ 卡顿检测 ----------------
    def _heartbeat_tick(self):
        """★ 保留这个「界面滴答」定时器，但**它不再是判断卡顿的依据**。

        ★★ 2026-10-06：以前判断「界面卡了多久」用的是这里的
           `self._heartbeat = time.time()` —— 而这是**界面自己的定时器**，
          界面一忙它就跑不到，于是「卡了 3 秒」被误报；
          误报又要主线程写日志 → 越报越卡（实测一次 1.36 秒）。
          现在真正的打卡交给一个纯计算线程（见 `_heartbeat_start`），
          这里只顺手刷新一下，不会再造成误报。
        """
        try:
            _HEART["stamp"] = time.time()
        except Exception:
            pass
        self._heartbeat = time.time()
        try:
            self.root.after(200, self._heartbeat_tick)
        except Exception:
            pass

    def _stuck_watchdog(self):
        """★ 盯着「界面卡了多久」。**报一笔这件事本身不许拖慢界面。**"""
        while True:
            try:
                time.sleep(1.0)
                # ★ v25 补丁18：窗口开始关了 → 这个线程立刻收工。
                if not self._ui_alive():
                    return
                now = time.time()
                # ★★ 2026-10-06：时间戳现在来自「打卡线程」（见 _heartbeat_start）——
                #   它不依赖界面闲不闲，所以「切文件切得快」不会再被误判。
                gap = now - float(_HEART.get("stamp", now) or now)
                if gap >= 3.0 and not _HEART.get("reported"):
                    # ★ 正在扫索引 / 后台比对目录时，界面短暂卡一下是正常的
                    try:
                        if INDEX_SCAN_EVENT.is_set():
                            continue
                        if getattr(self, "_bg_scan_running_dir", None):
                            continue
                    except Exception:
                        pass
                    _HEART["reported"] = True
                    msg = (f"界面无响应 {gap:.1f} 秒"
                           f"（可能正在做重活；点右下角「问题」查看日志）")
                    # ★★ 关键：**只排队，不直接动手** ——
                    #   直接 self.log_problem(...) 是主线程的活儿（还碰 Tk），
                    #   界面正忙的时候干这个 = 火上浇油（实测一次要 1.36 秒）。
                    _bg_post(self.log_problem, msg, "warn")
                    _bg_post(self.log_output, msg)
            except Exception:
                pass



    # ========== ★★ 2026-10-05「先加说话」：出错必留痕 ==========
    def _install_error_spy(self):
        """装一道「出错必留痕」的保险。

        用户抱怨的三件事——卡死 / 显示不全 / 改着改着功能没了——
        查下来根子之一是程序里 624 处 `except Exception: pass`
        （出错装没事）。它们不可能一条条手改，所以这里装两手「探照灯」：

        ● ① **后台线程**里没被抓住的出错
              线程一崩，界面还在那儿好好地转 —— 用户看到的就是「卡死」。
              以前这种错**完全没人知道**。现在会记进「问题」面板。
        ● ② **界面回调**里没被抓住的出错
              点按钮、画列表这类回调出错，以前也是悄悄没了。

        ★ 三条铁律（很重要，别破坏）：
          1. **只记一笔，绝不改变原有行为** —— 原 hook 该调还调；
          2. **自己绝不能再抛异常** —— 全程 try 包住，出问题就闭嘴；
          3. **不拖慢程序** —— 只在真出错时才干活，平时零开销。
        """
        if getattr(self, "_error_spy_on", False):
            return
        self._error_spy_on = True

        # ---------- ① 后台线程的兜底 ----------
        try:
            _old_hook = threading.excepthook

            def _thread_hook(args):
                try:
                    tname = getattr(args.thread, "name", "?")
                    note_swallowed(
                        f"后台线程「{tname}」出错了（界面可能因此没反应）",
                        args.exc_value if args.exc_value is not None
                        else RuntimeError(str(args.exc_type)),
                        level="error")
                except Exception:
                    pass
                try:
                    _old_hook(args)
                except Exception:
                    pass

            threading.excepthook = _thread_hook
        except Exception:
            pass

        # ---------- ② 界面回调的兜底 ----------
        # ★★★ 2026-10-05 **回退了这一手，别再装回来** ★★★
        #   教训（实测踩到的）：以前这里写了
        #       _old_report = tk.Tk.report_callback_exception
        #       tk.Tk.report_callback_exception = _new_report
        #   本意是「界面回调出错也能留痕」，结果**装上去之后
        #   分栏条拖不动了**——用户原话「现在直接没法拖动区域了」。
        #   原因：这是**替换 Tk 全局的出错处理**，等于在所有窗口的
        #   事件路上多拐了一道；这台机器上 Tk 的鼠标事件本来就敏感
        #   （见文件开头「鼠标事件 state 的 0x8 不是 Alt」那条实测），
        #   多拐一道就把拖拽打断了。
        #   ★ 结论：**不要在 Tk 全局上动手脚**。界面出错要留痕，
        #     改用别的路子（局部登记 / 后台线程兜底），绝不碰全局。
        #   只保留下面 ① 后台线程兜底 —— 那个是线程级的，不碰界面，
        #   实测不影响任何交互。
        pass

        # ---------- ③ 开机做个轻轻的体检 ----------
        try:
            self.root.after(1500, self._startup_health_check)
        except Exception:
            pass

    def _startup_health_check(self):
        """开机后轻轻看一眼「有没有在偷偷出错」。

        故意做得非常轻：只读内存里的计数，不碰数据库、不扫盘。
        也故意**不打扰用户** —— 只写进「问题」面板，点开才看细节。

        ★★ 2026-10-06：顺手**按用户的缓存设置清一次旧缓存**（后台线程，
           绝不拖慢启动）。清理规则见「界面 → 📥 网盘预览缓存设置」。
        """
        # ★ 先丢一个后台线程去清缓存（不阻塞开机）
        try:
            import threading as _th

            def _clean():
                try:
                    msg = _cache_clean_old()
                    if msg and "不用清" not in msg and "很干净" not in msg:
                        self.log_problem(T("缓存清理：") + msg, level="info")
                except Exception:
                    pass

            _th.Thread(target=_clean, daemon=True, name="缓存清理").start()
        except Exception:
            pass

        try:
            rep = swallowed_report()
            if not rep:
                return
            total = sum(n for _, n in rep)
            self.log_problem(
                f"本次启动发现 {len(rep)} 类「没吭声的小毛病」（共 {total} 次）。"
                f"多半不影响使用，但会积少成多 —— 需要时把这清单发我。",
                level="info")
        except Exception:
            pass

    def show_health_report(self):
        """★★ 2026-10-05「先加说话」：点菜单就能看「体检报告」。

        用户原话：「老卡死，界面有些部分经常显示不全，改来改去经常前面
        写好的功能后面没了」。这份报告的用处就是——**让程序别闷着**，
        把这些「本来没人知道」的小毛病摊开给他看。

        输出全是中文说法 + 出错次数，他能直接复制发给我。
        """
        try:
            text = self.dump_swallowed_report()
        except Exception as e:
            text = f"生成报告失败：{e}"
        try:
            # 顺手也写进「问题」面板，这样关掉小窗还能回看
            for _ln in str(text).split("\n"):
                if _ln.strip():
                    self.log_problem(_ln, level="info")
        except Exception:
            pass
        try:
            win = tk.Toplevel(self.root)
            # ★★ 2026-10-07：Toplevel 是**原生窗口**，底色不跟 ttk 主题走 ——
            #   不设 bg 就用系统默认（白/浅灰），那就是"小窗口夜间还是白的"的根因。
            try:
                win.configure(bg=theme_get("win_bg"))
                # ★ 登记一下，切主题时由 _retheme_custom_parts 统一刷新
                _reg = getattr(self, "_theme_windows", None)
                if _reg is None:
                    _reg = self._theme_windows = []
                _reg.append(win)
            except Exception:
                pass
            win.title("🩺 体检报告 —— 哪些地方在偷偷出错")
            win.transient(self.root)
            fr = ttk.Frame(win, padding=10)
            fr.pack(fill="both", expand=True)
            ttk.Label(fr, text="下面是程序自己记下来的「没吭声的小毛病」。\n"
                               "次数越多越值得查；把这份内容发我即可。",
                      justify="left").pack(anchor="w", pady=(0, 6))
            box = tk.Text(fr, width=76, height=22, wrap="none",
                          font=(FONT, UI_FONT_SIZE))
            box.pack(fill="both", expand=True)
            box.insert("1.0", str(text))
            box.configure(state="disabled")
            btns = ttk.Frame(fr)
            btns.pack(fill="x", pady=(8, 0))

            def _copy():
                try:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(str(text))
                    self.set_status(T("体检报告已复制到剪贴板"))
                except Exception as _e:
                    note_swallowed(T("复制体检报告失败"), _e, quiet=True)

            def _save():
                try:
                    fn = filedialog.asksaveasfilename(
                        title=T("保存体检报告"), defaultextension=".txt",
                        initialfile="体检报告.txt",
                        filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
                    if not fn:
                        return
                    with open(fn, "w", encoding="utf-8") as f:
                        f.write(str(text))
                    self.set_status(f"已保存：{fn}")
                except Exception as _e:
                    note_swallowed(T("保存体检报告失败"), _e)

            ttk.Button(btns, text=T("复制到剪贴板"), command=_copy).pack(side="left")
            ttk.Button(btns, text=T("另存为文件…"), command=_save).pack(side="left", padx=6)
            ttk.Button(btns, text=T("关闭"), command=win.destroy).pack(side="right")
            win.update_idletasks()
            try:
                win.geometry("")
            except Exception:
                pass
        except Exception as _e:
            note_swallowed(T("打开体检报告窗口失败"), _e)

    def dump_swallowed_report(self):
        """把「哪些地方在偷偷出错」整理成人话，供排查用。

        用户可能想要一份能直接发出去的清单（他自己看不懂代码，
        所以输出必须是中文说法 + 次数）。
        """
        try:
            rep = swallowed_report()
            if not rep:
                return "程序到目前为止没有发现「偷偷出错」的地方。"
            out = ["以下地方出过错（次数越多越值得查）：", ""]
            for name, n in rep[:60]:
                out.append(f"  · {name} —— {n} 次")
            if len(rep) > 60:
                out.append(f"  …还有 {len(rep) - 60} 类")
            return "\n".join(out)
        except Exception as e:
            return f"整理清单时出错：{e}"


    # ---------------- ★ 右下角活动指示器 ----------------
    def begin_activity(self, text="处理中…"):
        """开始一个后台任务，右下角显示转圈动画。"""
        try:
            self._activity_count += 1
            self._activity_texts.append(text or "处理中…")
            self._activity_stack.append((text or "处理中…", time.time()))
            self._refresh_activity_ui()
            self._start_spinner()
            self.log_progress(f"▶ 开始：{text}")
        except Exception:
            pass

    def end_activity(self):
        """结束一个后台任务；计数归零后自动隐藏。"""
        try:
            if self._activity_count > 0:
                self._activity_count -= 1
            if self._activity_texts:
                self._activity_texts.pop()
            name, t0 = ("?", time.time())
            if self._activity_stack:
                name, t0 = self._activity_stack.pop()
            dt = time.time() - t0
            if dt >= 1.0:
                self.log_progress(f"✓ 完成：{name}（{dt:.1f} 秒）")
            else:
                self.log_progress(f"✓ 完成：{name}")
            if dt >= 3.0:
                self.log_problem(
                    f"「{name}」耗时 {dt:.1f} 秒（偏慢）", level="warn")
            self._refresh_activity_ui()
        except Exception:
            pass

    def _refresh_activity_ui(self):
        try:
            if self._activity_count > 0:
                t = (self._activity_texts[-1]
                     if self._activity_texts else "处理中…")
                # ★ v25 补丁42：这个「正在忙」的文字也会把右边按钮挤出去
                #   （用户说的「左边黑灰文字重复又太长」就是它，比如
                #    「扫描目录：C:\Users\someone」这种）。这里限到 14 个字，
                #   全文照旧进「📋 输出」。
                t = str(t)
                if len(t) > 14:
                    t = t[:13] + "…"
                self._activity_text_lbl.config(text=t)
                # ★ 补丁42：用 before=伸缩框（和初始化一致）。
                #   直接 pack 会排到最后 = 挤到按钮那一侧，把按钮顶出窗口。
                if not self._activity_frame.winfo_ismapped():
                    self._activity_frame.pack(side="left", padx=(8, 0),
                                              before=self._status_spacer)
            else:
                if self._activity_frame.winfo_ismapped():
                    self._activity_frame.pack_forget()
        except Exception:
            pass

    def _start_spinner(self):
        if self._spinner_job is not None:
            return
        self._tick_spinner()

    def _tick_spinner(self):
        try:
            if self._activity_count <= 0:
                self._spinner_job = None
                try:
                    self._activity_spinner_lbl.config(text="")
                except Exception:
                    pass
                return
            ch = self._spinner_chars[
                self._spinner_idx % len(self._spinner_chars)]
            self._spinner_idx += 1
            self._activity_spinner_lbl.config(text=ch)
        except Exception:
            pass
        try:
            self._spinner_job = self.root.after(120, self._tick_spinner)
        except Exception:
            self._spinner_job = None

    def _restore_pane_widths(self, *a, **k):
        # ★★ 转发到 `AIxiede拆分开/程序分块/面板_面板布局.py`
        #   ★ 保留同名方法 = **所有调用方不用改**（稳定接口）
        return _面板面板布局._restore_pane_widths(self, *a, **k)


    def toggle_sidebar(self):
        """★ v25 补丁41：分类库的显示 / 隐藏，也改成「改状态 + 整体重排」。

        原来用的是 paned.insert(0, ...) / paned.forget(...) ——
        insert 同样有「序号越界」的毛病（就是日志里那条
        Slave index out of bounds）。现在全部走 _reinsert_tag_frame()，
        想显示谁、隐藏谁只改记忆变量，摆位交给它，永远不出错。

        ★★ 2026-10-07 修「区域开关以后的比例会自动跳成最初的」（用户报）★★
          病根（实测复现）：
            拉到 330 → **`_pane_sizes` 还是旧的 `{}`**（拉完没更新）
            → 关一次侧栏 → 再开 → 走 `_auto_sash_sidebar()` →
            **它读不到"用户拉过的值"，就用算法重算** → **跳回 395**。
          ★ 修法：**在关 / 开侧栏之前，先把当前宽度记下来**
            （`_remember_pane_now()`），这样"重开"时就有值可用。
        """
        try:
            # ★ 先把"现在的宽度"记下来 —— 不然重开时读到的是旧值
            try:
                self._remember_pane_now()
            except Exception:
                pass
            # ★★ 2026-10-07：标记"**正在重排分区**" —— 重排会把 sashpos
            #   改成 Tk 自己的值（实测 320→395），而本方法结尾安排的
            #   `after(400, _save_pane_sizes)` 会**如实记下那个错值**，
            #   把用户拖的宽度覆盖掉。
            #   → 重排期间不写盘（`_save_pane_sizes` 里会检查这个标记）。
            #   ★ 700 毫秒后才解除 —— 要比那个 400 毫秒的延迟保存晚。
            try:
                self._pane_rearranging = True
                self.root.after(700, lambda: setattr(self, "_pane_rearranging", False))
            except Exception:
                pass
            if self.sidebar.winfo_ismapped():
                self._sidebar_wanted = False
                self._reinsert_tag_frame()
                self.toggle_btn.config(text="▶")
                # ★★ 2026-10-07：**关也要把宽度摆回去** —— 全撤重加之后 Tk
                #   会把剩下的面板重新分，别的面板宽度就被挤动了
                #   （实测：关标签库，分类库 320 → 395）。
                try:
                    self.root.update_idletasks()
                except Exception:
                    pass
                self._restore_pane_widths()
                try:
                    self.root.after(60, self._restore_pane_widths)
                except Exception:
                    pass
            else:
                self._sidebar_wanted = True
                self._reinsert_tag_frame()
                self.toggle_btn.config(text="◀")
                # ★★ 2026-10-07 修「区域开关以后的比例会自动跳成最初的」★★
                #   实测关键点：**`paned.add()` 之后立刻 `sashpos()` 会被
                #   Tk 当成"布局还没算完"而夹成 0**（实测重开后变成 0）。
                #   所以分两步：
                #     ① `update_idletasks()` 让 Tk 把面板尺寸算出来
                #     ② 再调 `_auto_sash_sidebar()` 摆宽度
                #   还要**再补一次**（`after(60)`）—— 因为 Tk 有时
                #   要过一拍才把尺寸定下来（踩过：只调一次会偶尔不生效）。
                try:
                    self.root.update_idletasks()
                except Exception:
                    pass
                self._auto_sash_sidebar()
                try:
                    self.root.after(60, lambda: self._auto_sash_sidebar())
                except Exception:
                    pass
        except Exception as exc:
            try:
                note_swallowed(T("切换分类库显示失败"), exc)
            except Exception:
                print(exc)

    def _remember_pane_now(self):
        """★ 把"现在各分区的实际宽度"立刻记进 `_pane_sizes`（不写盘）。

        ★★ 2026-10-07 新增，为什么需要（用户报「区域开关以后的比例会自动
           跳成最初的」）：
           `_pane_sizes` 原来**只在"松开分栏条"或"关窗"时才更新** ——
           于是：**拉完之后马上关开一次侧栏**，读到的是**旧值** →
           重开时按旧值（或算法）摆 → **看起来就是"自动跳回去了"**。
         ★ 所以：凡是"要动分栏排布"之前，先调一次这个，把现状钉住。
        """
        try:
            pw = self.paned
            panes = [str(p) for p in pw.panes()]
            if not panes:
                return
            data = dict(getattr(self, "_pane_sizes", {}) or {})

            def _width(idx):
                try:
                    left = pw.sashpos(idx - 1) if idx > 0 else 0
                    right = (pw.sashpos(idx) if idx + 1 < len(panes)
                             else pw.winfo_width())
                    return max(0, int(right - left))
                except Exception:
                    return 0

            for frame, key in ((getattr(self, "sidebar", None),
                                "pane_sidebar_w"),
                               (getattr(self, "preview_frame", None),
                                "pane_preview_w"),
                               (getattr(self, "tag_frame", None),
                                "pane_taglib_w")):
                if frame is None:
                    continue
                s = str(frame)
                if s in panes:
                    w = _width(panes.index(s))
                    if w > 40:
                        data[key] = w
            self._pane_sizes = data
            # 同步那几个"记忆变量"（别处读它们）
            try:
                self._preview_width = int(data.get("pane_preview_w")
                                          or getattr(self, "_preview_width", 380))
                self._taglib_width = int(data.get("pane_taglib_w")
                                         or getattr(self, "_taglib_width", 380))
                self._sidebar_width = int(data.get("pane_sidebar_w") or 0)
            except Exception:
                pass
        except Exception:
            pass

    def toggle_top_bar(self):
        """★★ 2026-10-03：显示 / 隐藏顶部工具栏（两行），节省垂直空间。

        ★★ 2026-10-07 修一个真 bug（用户报「再点显示在了下方，不再是顶部了」）：
          病根 —— 恢复显示时写的是
              self._top_bar.pack(fill="x")
          没给 `before=`。**pack 不带 before 就是"排到最后面"**，
          而这两条工具栏**本来应该在 `self.paned`（中间的列表区）上面**，
          于是恢复之后它们被排到了列表区**下面**，看着就是"跑到下面去了"。

          修法 —— 用 `before=self.paned` 把它们钉回原位：
            · `_top_bar2` 紧贴在 `paned` 前面
            · `_top_bar` 再贴在 `_top_bar2` 前面
          （顺序反了会上下颠倒，所以两条都要给 before）
        """
        try:
            if getattr(self, "_top_bar_visible", True):
                # 隐藏
                self._top_bar.pack_forget()
                self._top_bar2.pack_forget()
                self._top_bar_visible = False
                self._topbar_btn.config(text=T("▼ 顶部"))
                self.set_status(T("顶部工具栏：已隐藏"))
            else:
                # ★ 显示：必须钉回 paned 上面（理由见上面 docstring）
                self._top_bar2.pack(fill="x", before=self.paned)
                self._top_bar.pack(fill="x", before=self._top_bar2)
                self._top_bar_visible = True
                self._topbar_btn.config(text=T("▲ 顶部"))
                self.set_status(T("顶部工具栏：已显示"))
            save_ui_setting("top_bar_visible", self._top_bar_visible)
        except Exception as exc:
            try:
                note_swallowed(T("切换顶部工具栏显示失败"), exc)
            except Exception:
                print(exc)

    # ---------------- ★ v25 补丁9：文件基本操作（第二阶段）----------------
    def _focus_is_input(self):
        """现在焦点是不是在输入框里（在输入框里时，Delete/F2/Ctrl+A 不该抢）。"""
        try:
            w = self.root.focus_get()
        except Exception:
            return False
        try:
            if isinstance(w, (tk.Entry, tk.Text)):
                return True
            # ttk 的控件（Entry / Combobox / Spinbox）不是 tk.Entry 的子类
            return w.winfo_class() in ("TEntry", "TCombobox", "TSpinbox")
        except Exception:
            return False

    # ---------------- ★★ 2026-10-06：撤销（Ctrl+Z）----------------
    def _undo_init(self):
        """开机时把「撤销记录本」准备好（把上次关程序前的记录读回来）。"""
        self._undo_stack = []
        self._undo_redo_stack = []
        try:
            p = _undo_file_path()
            if p and os.path.isfile(p):
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    self._undo_stack = data[-UNDO_MAX:]
        except Exception as _e:
            note_swallowed(T("读撤销记录失败（这次开程序撤不了上次的事）"), _e,
                           quiet=True)
        self._undo_save_soon()

    def _undo_save_soon(self):
        """把撤销记录写到磁盘（**关程序再开还能撤** —— 资源管理器做不到这个）。

        ★ 放到后台线程写，绝不拖慢界面（这是本程序一贯的规矩）。
        """
        try:
            if getattr(self, "_undo_save_job", None) is not None:
                return
        except Exception:
            pass

        def _do():
            self._undo_save_job = None
            try:
                p = _undo_file_path()
                if not p:
                    return
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(self._undo_stack[-UNDO_MAX:], f,
                              ensure_ascii=False)
            except Exception:
                pass

        try:
            self._undo_save_job = self.root.after(800, _do)
        except Exception:
            self._undo_save_job = None

    def undo_record(self, kind, items, note=""):
        """★ 记一条「怎么反着做回去」。**批量动作算一条**。

        kind: "delete" / "rename" / "tag_add" / "tag_remove"
        items: 各类型要的东西（见下面注释）
        ★ 记录里**只放纯数据**（路径、名字），不放控件、不放文件句柄 ——
          因为它要写到磁盘，下次开程序还要能用。
        """
        try:
            if not items:
                return
            rec = {"kind": kind, "items": list(items),
                   "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                   "note": note}
            self._undo_stack.append(rec)
            if len(self._undo_stack) > UNDO_MAX:
                self._undo_stack = self._undo_stack[-UNDO_MAX:]
            self._undo_redo_stack = []      # 记了新动作，红就作废
            self._undo_save_soon()
            self._undo_update_btn()
        except Exception as _e:
            note_swallowed(T("记撤销记录失败（这一步撤不了）"), _e, quiet=True)

    def undo_do(self):
        """★ 按 Ctrl+Z：把最后一条反着执行一遍。**要告诉用户撤了什么。**"""
        try:
            if not self._undo_stack:
                self.set_status(T("没有可以撤销的操作了"))
                return
            rec = self._undo_stack[-1]
        except Exception:
            return
        kind = rec.get("kind")
        items = rec.get("items") or []
        label = _undo_label(rec)
        try:
            res = self._undo_apply(kind, items)
            # ★ 兼容两种返回：新的三元组 / 老的二元组
            if isinstance(res, tuple) and len(res) >= 3:
                ok, msg, failed = res[0], res[1], (res[2] or [])
            else:
                ok, msg, failed = res[0], res[1], []
        except Exception as _e:
            note_swallowed(T("撤销失败"), _e)
            messagebox.showwarning("撤销没成功",
                                   "这一步没能撤销：\n\n%s" % _e,
                                   parent=self.root)
            return
        if not ok:
            # ★ 撤不了就**如实说**，并且把这条从记录本里拿掉
            #   （免得用户每次按都失败，以为是程序坏了）
            self._undo_stack.pop()
            self._undo_save_soon()
            self._undo_update_btn()
            messagebox.showwarning(
                "撤销没成功",
                "这一步撤不回来了。\n\n%s\n\n"
                "（已经把它从「可撤销」列表里去掉，免得每次按都失败）" % msg,
                parent=self.root)
            self.set_status(T("撤销失败：{x}", x=msg))
            self.log_problem(T("撤销失败：{x}（{y}）", x=label, y=msg), level="warn")
            return
        # ★★ 2026-10-07 新增：**半成功必须当面说清楚**。
        #   背景（错题本 #14 / 待清算第 2 条）：用户报「撤销：本地正常，网盘不行」。
        #   原来的代码只判「全失败」—— 删了 3 个、只回来 1 个时，
        #   ok>0 就当成功报"已撤销：把 3 项从回收站还原"，
        #   **用户以为都回来了，其实桌上还少两个** —— 这就是"骗人"。
        #   现在：只要有失败项，就**弹窗把"哪几个没回来"列清楚**。
        if failed:
            try:
                detail = "\n".join("   · " + str(x) for x in failed[:8])
                more = ("\n   …还有 %d 项" % (len(failed) - 8)
                        if len(failed) > 8 else "")
                messagebox.showwarning(
                    "撤销只成功了一部分",
                    "这一批里**有几项没能撤销**：\n\n%s%s\n\n"
                    "★ 上面列出来的那些**没有恢复**，"
                    "请自己确认一下它们还在不在。\n\n"
                    "（这条撤销记录已经从列表里去掉 —— 再按一次也不会有更多效果）"
                    % (detail, more),
                    parent=self.root)
            except Exception:
                pass
            try:
                self.log_problem(
                    "撤销只成功一部分：%s —— 失败项：%s"
                    % (label, "；".join(str(x) for x in failed[:5])),
                    level="warn")
            except Exception:
                pass
            # 半成功：挪进重做栈没意义（还有东西没回来），直接丢掉这条
            self._undo_stack.pop()
            self._undo_save_soon()
            self._undo_update_btn()
            self.set_status(T("已撤销（部分）：{x}", x=msg))
            return
        # 成功：从「可撤销」挪到「可重做」
        self._undo_stack.pop()
        self._undo_redo_stack.append(rec)
        self._undo_save_soon()
        self._undo_update_btn()
        if msg:
            self.set_status(T("已撤销：{x}（{y}）", x=label, y=msg))
        else:
            self.set_status(T("已撤销：{x}", x=label))
        try:
            self.log_output(T("↶ 已撤销：{x}", x=label))
        except Exception:
            pass

    def _undo_apply(self, kind, items):
        """真正去执行一条反向操作。

        返回 (成功了吗, 说明文字, 失败清单)。
        ★ 2026-10-07：**加了第三个返回值「失败清单」** ——
          以前返回两个，只分"全成功/全失败"两种情况。
          但**"删了 3 个、只还原回来 1 个"**这种半成不成的，
          原来会被当成"成功"报出去（`ok>0` 就算成功）→ **等于骗人**。
          用户以为"撤销了、都回来了"，其实桌上还少两个。
          （见错题本 #14 / 待清算清单第 2 条。）
        """
        if kind == "delete":
            # items: [路径, ...]（这些已经被丢进回收站了）
            ok, errs = _recycle_restore(items)
            # ★ 部分成功也要如实说 —— 不能因为回来了一部分就报"已撤销"
            if ok == 0:
                return (False,
                        "回收站还原失败：%s"
                        % ("；".join(errs[:3]) if errs else "系统没回应"),
                        errs)
            # ★ 库里的记录也要跟着回来 —— 否则文件回来了、标签却没了。
            #   （删除时调的是 store.forget_path；这里用重新登记的办法补回。）
            #   ★ 只对**真回来了的**那几项登记（失败的本就不在，登记了是脏数据）。
            for p in items:
                try:
                    if os.path.exists(p):
                        self.store.remember_paths([p])
                except Exception:
                    pass
            self.refresh_current_dir()
            self.refresh_rows_tags()
            self.refresh_categories()
            if errs:
                # 半成功：**说清楚回来了几个、还差几个**
                return (True,
                        "还原 %d 项，**还有 %d 项没回来**" % (ok, len(errs)),
                        errs)
            return True, "还原 %d 项" % ok, []
        if kind == "rename":
            # items: [(新路径, 旧路径), ...]
            done = 0
            errs = []
            for new_p, old_p in items:
                try:
                    if not os.path.exists(new_p):
                        errs.append("%s 已经不在了" % os.path.basename(new_p))
                        continue
                    if os.path.exists(old_p):
                        errs.append("%s 那个名字已经被占了"
                                    % os.path.basename(old_p))
                        continue
                    os.rename(new_p, old_p)
                    try:
                        self.store.move_file_path(new_p, old_p)
                    except Exception:
                        pass
                    done += 1
                except Exception as exc:
                    errs.append("%s：%s" % (os.path.basename(str(new_p)), exc))
            if done == 0:
                return (False,
                        "；".join(errs[:3]) if errs else "没有可改回的", errs)
            self.refresh_current_dir()
            self.refresh_rows_tags()
            if errs:
                return (True,
                        "改回 %d 个，**还有 %d 个没改回**" % (done, len(errs)),
                        errs)
            return True, "改回 %d 个" % done, []
        if kind in ("tag_add", "tag_remove"):
            # items: [(路径, 标签名), ...]；tag_add 的反动作是去掉
            done = 0
            errs = []
            for path, tname in items:
                try:
                    if kind == "tag_add":
                        self.store.remove_tag_from_path(path, tname)
                    else:
                        self.store.add_tag_to_file(path, tname)
                    done += 1
                except Exception as exc:
                    errs.append("%s：%s" % (os.path.basename(str(path)), exc))
            if done == 0:
                return (False,
                        "；".join(errs[:3]) if errs else "没有可改的", errs)
            self.refresh_rows_tags()
            self.refresh_categories()
            if errs:
                return (True,
                        "改回 %d 个，**还有 %d 个没改回**" % (done, len(errs)),
                        errs)
            return True, "改回 %d 个" % done, []
        return False, "不认识这种操作", []

    def _undo_update_btn(self):
        """撤销按钮 / 菜单项亮不亮。"""
        try:
            n = len(getattr(self, "_undo_stack", []) or [])
        except Exception:
            n = 0
        try:
            if n:
                self._undo_btn.config(state="normal",
                                      text="↶ 撤销 (%d)" % n)
            else:
                self._undo_btn.config(state="disabled", text=T("↶ 撤销"))
        except Exception:
            pass

    def on_undo_key(self, event=None):
        """Ctrl+Z 的入口（在输入框里打字时不抢键）。"""
        try:
            if self._focus_is_input():
                return None
        except Exception:
            pass
        self.undo_do()
        return "break"

    def _do_new_folder(self):
        """在当前文件夹里新建一个文件夹（名字重复就自动加 (2)、(3)…）。"""
        if not self.current_dir:
            messagebox.showinfo("提示", T("先打开一个文件夹再说。"), parent=self.root)
            return
        base = str(self.current_dir)
        name = "新建文件夹"
        i = 1
        while os.path.exists(os.path.join(base, name)):
            i += 1
            name = "新建文件夹 (%d)" % i
        newp = os.path.join(base, name)
        try:
            os.mkdir(newp)
        except Exception as exc:
            messagebox.showerror("新建失败", str(exc), parent=self.root)
            return
        self.log_output(T("新建文件夹：{x}", x=newp))
        self.set_status(T("已新建文件夹：{x}", x=name))
        self.refresh_current_dir()

    def _do_rename(self, path=None):
        """重命名选中的文件 / 文件夹，并把数据库里的路径同步过去。

        ★ 为什么要同步数据库：标签是按「文件记录」挂的，路径不改的话
          改完名双击打不开、标签看着也像丢了。
        """
        if path is None:
            path = self.file_list.get_single_selection()
        if not path:
            messagebox.showinfo("提示", T("请先选中**一个**文件或文件夹（单击它）。"),
                                parent=self.root)
            return
        old_name = os.path.basename(path.rstrip("\\")) or path
        # ★ v26 修正：SimpleInputDialog 在它自己的构造函数里已经
        #   wait_window 过了（窗口关闭时构造函数才返回），这里**不要**
        #   再 wait 一次 —— 那时 dlg 已经被销毁，再等会抛
        #   TclError: bad window path name（虽然被 except 吞了，但纯属浪费）。
        dlg = SimpleInputDialog(self.root, title=T("重命名（输入新名字）"),
                                initial=old_name)
        new_name = (getattr(dlg, "result", None) or "").strip()
        if not new_name or new_name == old_name:
            return
        if any(ch in new_name for ch in '\\/:*?"<>|'):
            messagebox.showerror("不能这样改名",
                                 '名字里不能有  \\ / : * ? " < > |  这些字符',
                                 parent=self.root)
            return
        parent_dir = os.path.dirname(path.rstrip("\\"))
        new_path = os.path.join(parent_dir, new_name)
        if os.path.exists(new_path):
            messagebox.showerror("不能改名",
                                 "这个位置已经有同名的了：\n%s" % new_path,
                                 parent=self.root)
            return
        is_dir = os.path.isdir(path)
        try:
            os.rename(path, new_path)
        except Exception as exc:
            messagebox.showerror("改名失败", str(exc), parent=self.root)
            return
        n = 0
        try:
            if is_dir:
                n = self.store.rename_prefix_paths(path, new_path)
                try:
                    self.store.clear_dir_cache_under(path)
                except Exception:
                    pass
            else:
                n = 1 if self.store.move_file_path(path, new_path) else 0
        except Exception as exc:
            self.log_problem(T("改名成功了，但数据库里的路径没同步好：{x}", x=exc),
                             level="error")
        self.log_output(T("已改名：{x} → {y}（数据库同步 {z} 条）", x=old_name, y=new_name, z=n))
        # ★★ 2026-10-06：记一笔撤销（记「新名 → 旧名」，撤销时改回去）
        self.undo_record("rename", [(new_path, path)])
        self.set_status(T("已改名：{x} → {y}", x=old_name, y=new_name))
        self.file_list.selected_paths = {new_path}
        self.refresh_current_dir()
        self.refresh_rows_tags()

    def _do_delete(self, paths=None):
        """把选中的文件 / 文件夹删到回收站（可还原），并从库里清掉它们的记录。"""
        if paths is None:
            paths = list(self.file_list.get_selection() or [])
        if not paths:
            messagebox.showinfo("提示", "请先选中要删的东西（单击 / 框选 / Ctrl+A）。",
                                parent=self.root)
            return
        n = len(paths)
        first = os.path.basename(paths[0].rstrip("\\")) or paths[0]
        extra = "" if n == 1 else "\n（还有 %d 项）" % (n - 1)

        # ★★★ 2026-10-07：**网盘上的东西，删之前就要说清楚"这个撤不回来"**。
        #
        #   背景（错题本 #14 / #67，用户亲测确认）：
        #     **网盘（CloudDrive）删文件进的是「网盘自己的回收站」，
        #       不是 Windows 回收站。**
        #     而我们的「撤销删除」走的是系统回收站（Shell.Application 的 10 号
        #     特殊目录）—— **系统回收站里根本没有它，永远找不着**。
        #
        #   为什么要在**删之前**说、而不是等用户按 Ctrl+Z 才说：
        #     · 删除是**不可逆**操作，用户有权在动手前知道后果
        #     · 等到按撤销才发现"撤不了"，东西**已经没了**，说也晚了
        #     · 这属于「会丢东西」那一类红线（见待清算清单开头）
        #
        #   ★ 只警告、不阻止 —— 用户想删还是让他删（网盘客户端里也许能找回）。
        _remote = []
        try:
            for p in paths:
                if is_remote_path(p):
                    _remote.append(os.path.basename(str(p).rstrip("\\")) or str(p))
        except Exception:
            _remote = []

        if _remote:
            _shown = "\n".join("   · " + x for x in _remote[:6])
            _more = ("\n   …还有 %d 项" % (len(_remote) - 6)
                     if len(_remote) > 6 else "")
            _ask = (
                "把选中的 %d 项丢进回收站？\n\n  第一项：%s%s\n\n"
                "⚠️ 注意：这里面有 **%d 项在网盘上**：\n%s%s\n\n"
                "★ 网盘上的东西，删掉之后**本程序撤不回来** ——\n"
                "   它进的是**网盘自己的回收站**，不是 Windows 回收站，\n"
                "   我们够不着它。要找回的话，得去**网盘客户端**里找。\n\n"
                "（本地文件不受影响，本地删了照样能撤销。）\n\n"
                "还删吗？"
                % (n, first, extra, len(_remote), _shown, _more))
            _title = "删到回收站（有网盘文件，撤不回来）"
        else:
            _ask = ("把选中的 %d 项丢进回收站？\n\n  第一项：%s%s\n\n"
                    "丢进回收站还能还原，不是永久删除。" % (n, first, extra))
            _title = "删到回收站"

        if not messagebox.askyesno(_title, _ask, parent=self.root):
            return
        ok, errs = 0, []
        _done_paths = []          # ★ 2026-10-06：真正删成功的，用来记撤销
        for p in paths:
            try:
                _send_to_recycle_bin(p)
            except Exception as exc:
                errs.append("%s：%s" % (p, exc))
                continue
            ok += 1
            _done_paths.append(p)
            if p in self.file_list.selected_paths:
                self.file_list.selected_paths.discard(p)
            try:
                self.store.forget_path(p)
            except Exception as _e:
                note_swallowed(T("删除后清理数据库记录失败"), _e)
            # 文件夹的话，把它下面的记录和缓存也清掉
            if os.path.isdir(os.path.dirname(p)) and "." not in os.path.basename(p):
                try:
                    self.store.clear_dir_cache_under(p)
                except Exception:
                    pass
        self.log_output(T("已删到回收站：{x} 项", x=ok))
        # ★★ 2026-10-06：记一笔撤销（**整批算一条** —— 按一次 Ctrl+Z 全回来）
        if _done_paths:
            self.undo_record("delete", _done_paths)
        self.set_status("已删到回收站：%d 项%s"
                        % (ok, "" if not errs else "（%d 项失败）" % len(errs)))
        if errs:
            self.log_problem("删除失败：%s" % "；".join(errs[:3]), level="error")
            messagebox.showwarning("有删不掉的",
                                   "这几项没删掉：\n\n%s" % "\n".join(errs[:5]),
                                   parent=self.root)
        self.refresh_current_dir()
        self.refresh_rows_tags()
        self.refresh_categories()

    def on_delete_key(self, event=None):
        if self._focus_is_input():
            return None
        self._do_delete()
        return "break"

    def on_rename_key(self, event=None):
        if self._focus_is_input():
            return None
        self._do_rename()
        return "break"

    def on_select_all_key(self, event=None):
        if self._focus_is_input():
            return None
        self.file_list.select_all_rows()
        return "break"

    def on_new_folder_key(self, event=None):
        if self._focus_is_input():
            return None
        self._do_new_folder()
        return "break"

    # ---------------- ★ v25 补丁12：复制 / 剪切 / 粘贴 ----------------
    def copy_selected(self, cut=False):
        """把选中的文件/文件夹放进「程序内的剪贴板」（Ctrl+C / Ctrl+X）。"""
        paths = list(self.file_list.get_selection() or [])
        if not paths:
            messagebox.showinfo("提示", "请先选中要%s的东西（单击 / 框选 / Ctrl+A）。"
                                % ("剪切" if cut else "复制"), parent=self.root)
            return
        self._clip = {"paths": paths, "cut": bool(cut)}
        word = "剪切" if cut else "复制"
        self.set_status("已%s %d 项 —— 打开目标文件夹后按 Ctrl+V 粘贴" % (word, len(paths)))
        self.log_output("已%s %d 项：%s" % (word, len(paths),
                                        "、".join(os.path.basename(p) for p in paths[:5])
                                        + ("…" if len(paths) > 5 else "")))

    def paste_into_current(self):
        """把剪贴板里的东西粘贴到当前文件夹（Ctrl+V）。"""
        clip = getattr(self, "_clip", None) or {}
        srcs = [p for p in (clip.get("paths") or []) if os.path.exists(p)]
        if not clip.get("paths"):
            messagebox.showinfo("提示", "剪贴板是空的 —— 先选中东西按 Ctrl+C（复制）"
                                       "或 Ctrl+X（剪切）。", parent=self.root)
            return
        if not clip.get("paths"):
            return
        gone = len(clip["paths"]) - len(srcs)
        if not srcs:
            messagebox.showinfo("提示", T("要粘贴的东西已经不在了（可能被删掉或改名了）。"),
                                parent=self.root)
            self._clip = None
            return
        if not self.current_dir:
            messagebox.showinfo("提示", "先打开一个目标文件夹，再按 Ctrl+V 粘贴。",
                                parent=self.root)
            return
        target = str(self.current_dir)
        cut = bool(clip.get("cut"))
        word = "移动" if cut else "复制"
        extra = "" if not gone else "\n（有 %d 项已经不在了，会跳过）" % gone
        if cut and not messagebox.askyesno(
                "粘贴（移动）",
                "把剪贴板里的 %d 项**移动**到：\n%s\n\n%s"% (len(srcs), target, extra)
                + "移动会把原位置的东西挪走（不是复制一份）。",
                parent=self.root):
            return
        self.begin_activity("正在%s %d 项…" % (word, len(srcs)))
        self.log_output("开始%s %d 项 → %s" % (word, len(srcs), target))

        def worker():
            done, errs = [], []
            for src in srcs:
                try:
                    name = os.path.basename(str(src).rstrip("\\")) or str(src)
                    is_dir = os.path.isdir(src)
                    dst = _unique_target_path(target, name, is_dir)
                    if cut:
                        shutil.move(src, dst)
                    elif is_dir:
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
                    done.append((src, dst))
                except Exception as exc:
                    errs.append("%s：%s" % (os.path.basename(str(src)), exc))
            try:
                self._ui_threadsafe(self._paste_done, cut, target, done, errs)
            except Exception as exc:
                # ★★ 2026-10-03：worker 尾部 _ui_threadsafe 失败时，
                #   之前 except: pass 默默丢弃，主线程永远不知道活儿没干。
                #   现在至少留一笔 warn，方便排查。
                note_swallowed(T("worker(_paste_done)：回主线程通知失败"),
                               exc, level="warn")

        threading.Thread(target=worker, daemon=True).start()

    def _paste_done(self, cut, target, done, errs):
        """粘贴完成（回主线程）：同步数据库路径 + 刷新界面。"""
        self.end_activity()
        if cut:
            # 移动过了 → 数据库里的路径要跟着改（不然标签看着像丢了）
            for src, dst in done:
                try:
                    if os.path.isdir(dst):
                        self.store.rename_prefix_paths(src, dst)
                    else:
                        self.store.move_file_path(src, dst)
                except Exception as _e:
                    note_swallowed(T("剪切粘贴后同步数据库路径失败"), _e)
                try:
                    self.store.clear_dir_cache_under(os.path.dirname(str(src)))
                except Exception:
                    pass
        # 剪贴板用完了（剪切只能粘一次；复制也清掉，避免误按再粘一次）
        self._clip = None
        n = len(done)
        word = "移动" if cut else "复制"
        self.log_output(T("完成：{x} {y} 项 → {z}", x=word, y=n, z=target))
        self.set_status("已%s %d 项 → %s%s"
                        % (word, n, os.path.basename(target.rstrip("\\")) or target,
                           "" if not errs else "（%d 项失败）" % len(errs)))
        if errs:
            self.log_problem("粘贴失败：%s" % "；".join(errs[:3]), level="error")
            messagebox.showwarning("有没粘成功的",
                                   "这些没成功：\n\n%s" % "\n".join(errs[:5]),
                                   parent=self.root)
        try:
            if self.view_mode == "dir" and self.current_dir:
                self.load_directory(self.current_dir)
            else:
                self.refresh_current_dir()
        except Exception as _e:
            note_swallowed(T("粘贴后刷新界面失败"), _e)
        try:
            self.refresh_rows_tags()
        except Exception:
            pass

    def _move_paths_to_folder(self, paths, target_dir):
        """★★ 2026-10-03 新增：把文件 / 文件夹**移动**进某个文件夹。

        这是「在列表里按住一个文件，拖到某个文件夹那一行上松手」走的路
        （文件列表拖动时回调 on_move_to_folder）。**以前主程序从来没接上
        这个回调**（一直是 None），所以松手以后什么都不发生 ——
        用户说「这个我想让它真的能用」，指的就是这一步。

        ★ 一定会先弹确认框（列出要移动的东西和目标文件夹），
          因为「移动」是真的把文件从原位置挪走。
        ★ 移动完会把数据库里的路径一起改掉（标签跟着走，不会丢）。
        """
        tgt = str(target_dir or "").rstrip("\\")
        if not tgt:
            return
        srcs = []
        for p in (paths or []):
            p = str(p)
            try:
                if not p or not os.path.exists(p):
                    continue
                if os.path.normcase(os.path.dirname(p.rstrip("\\"))) == os.path.normcase(tgt):
                    continue                       # 本来就在这个文件夹里
                if os.path.normcase(p.rstrip("\\")) == os.path.normcase(tgt):
                    continue                       # 拖到自己身上
                # 不许把文件夹拖进它自己 / 它的子目录里
                if os.path.normcase(tgt).startswith(
                        os.path.normcase(p.rstrip("\\")) + os.sep):
                    continue
                srcs.append(p)
            except Exception:
                continue
        if not srcs:
            self.set_status(T("没有可移动的东西（可能本来就在那个文件夹里）"))
            return
        names = "、".join(os.path.basename(str(p).rstrip("\\")) for p in srcs[:4])
        if len(srcs) > 4:
            names += "…（共 %d 项）" % len(srcs)
        if not messagebox.askyesno(
                "移动 %d 项" % len(srcs),
                "把选中的 %d 项**移动**到：\n%s\n\n  内容：%s\n\n"
                "「移动」会把原位置的东西挪走（不是复制一份）。\n"
                "标签会跟着一起走，不会丢。\n\n确定移动吗？"
                % (len(srcs), tgt, names),
                parent=self.root):
            self.set_status(T("已取消移动"))
            return
        self.begin_activity("正在移动 %d 项…" % len(srcs))
        self.log_output("拖动移动：%d 项 → %s" % (len(srcs), tgt))

        def worker():
            done, errs = [], []
            for src in srcs:
                try:
                    name = os.path.basename(str(src).rstrip("\\")) or str(src)
                    is_dir = os.path.isdir(src)
                    dst = _unique_target_path(tgt, name, is_dir)
                    shutil.move(src, dst)
                    done.append((src, dst))
                except Exception as exc:
                    errs.append("%s：%s" % (os.path.basename(str(src)), exc))
            try:
                self._ui_threadsafe(self._drag_move_done, tgt, done, errs)
            except Exception as exc:
                note_swallowed(T("worker(_drag_move_done)：回主线程通知失败"),
                               exc, level="warn")

        threading.Thread(target=worker, daemon=True).start()

    def _drag_move_done(self, target, done, errs):
        """（主线程）拖动移动完成 → 同步数据库路径 + 刷新界面。

        ★ 和「剪切粘贴」走的是同一套数据库动作：路径改掉、标签保留。
        """
        self.end_activity()
        for src, dst in done:
            try:
                if os.path.isdir(dst):
                    self.store.rename_prefix_paths(src, dst)
                else:
                    self.store.move_file_path(src, dst)
            except Exception as _e:
                note_swallowed(T("拖动移动后同步数据库路径失败"), _e)
            try:
                self.store.clear_dir_cache_under(os.path.dirname(str(src)))
            except Exception:
                pass
        n = len(done)
        self.log_output(T("拖动移动完成：{x} 项 → {y}", x=n, y=target))
        self.set_status("已移动 %d 项 → %s%s" % (
            n, os.path.basename(target.rstrip("\\")) or target,
            "" if not errs else "（%d 项失败）" % len(errs)))
        if errs:
            self.log_problem("移动失败：%s" % "；".join(errs[:3]), level="error")
            messagebox.showwarning("有没移成功的",
                                   "这些没成功：\n\n%s" % "\n".join(errs[:5]),
                                   parent=self.root)
        try:
            if self.view_mode == "dir" and self.current_dir:
                self.load_directory(self.current_dir)
            else:
                self.refresh_current_dir()
        except Exception as _e:
            note_swallowed(T("移动后刷新界面失败"), _e)
        try:
            self.refresh_rows_tags()
        except Exception:
            pass

    def on_copy_key(self, event=None):
        if self._focus_is_input():
            return None
        self.copy_selected(cut=False)
        return "break"

    def on_cut_key(self, event=None):
        if self._focus_is_input():
            return None
        self.copy_selected(cut=True)
        return "break"

    def on_paste_key(self, event=None):
        if self._focus_is_input():
            return None
        self.paste_into_current()
        return "break"

    # ---------------- ★ v25 补丁13：导航（后退/前进/盘符/常用位置）----------------
    @staticmethod
    def _clean_path_input(text):
        """地址栏里手输的路径：去掉引号/空格，如果给的是文件就进它所在的文件夹。

        （从资源管理器复制路径过来常常带一对引号，或者直接粘的是一个文件路径。）
        """
        t = (text or "").strip().strip('"').strip("'").strip()
        if not t:
            return t
        try:
            if os.path.isfile(t):
                return os.path.dirname(t)
        except Exception:
            pass
        return t

    def _nav_record(self, path):
        """走了一个新目录 → 记进历史（后退/前进用）。"""
        try:
            p = str(path)
        except Exception:
            return
        if getattr(self, "_nav_hist", None) is None:
            self._nav_hist = []
            self._nav_pos = -1
        # 正在「后退/前进」的路上，就不要再记一遍
        if getattr(self, "_nav_going", False):
            return
        if self._nav_pos >= 0 and self._nav_hist[self._nav_pos] == p:
            return
        self._nav_hist = self._nav_hist[:self._nav_pos + 1]
        self._nav_hist.append(p)
        if len(self._nav_hist) > 60:
            self._nav_hist = self._nav_hist[-60:]
        self._nav_pos = len(self._nav_hist) - 1
        self._update_nav_buttons()

    def _update_nav_buttons(self):
        try:
            hist = getattr(self, "_nav_hist", []) or []
            pos = getattr(self, "_nav_pos", -1)
            self._nav_back_btn.state(["!disabled"] if pos > 0 else ["disabled"])
            self._nav_fwd_btn.state(
                ["!disabled"] if pos < len(hist) - 1 else ["disabled"])
        except Exception:
            pass

    def _nav_to_pos(self, pos):
        hist = getattr(self, "_nav_hist", []) or []
        if not (0 <= pos < len(hist)):
            return
        self._nav_pos = pos
        self._nav_going = True
        try:
            self.load_directory(hist[pos])
        finally:
            self._nav_going = False
        self._update_nav_buttons()

    def go_back(self):
        """后退（Alt+←）。"""
        self._nav_to_pos(getattr(self, "_nav_pos", 0) - 1)

    def go_forward(self):
        """前进（Alt+→）。"""
        self._nav_to_pos(getattr(self, "_nav_pos", 0) + 1)

    def on_nav_back_key(self, event=None):
        if self._focus_is_input():
            return None
        self.go_back()
        return "break"

    def on_nav_forward_key(self, event=None):
        if self._focus_is_input():
            return None
        self.go_forward()
        return "break"

    def _drives(self):
        """这台机器上都有哪些盘（含网盘映射的 X:/Y:）。"""
        out = []
        try:
            import win32api  # type: ignore
            out = list(win32api.GetLogicalDriveStrings().split("\x00"))
            out = [d for d in out if d]
        except Exception:
            out = []
        if not out:
            for ch in "CDEFGHIJKLMNOPQRSTUVWXYZ":
                d = ch + ":\\"
                if os.path.exists(d):
                    out.append(d)
        return out

    def toggle_net_browse(self):
        """★ v25 补丁14：在「索引显示（快，不连网盘）」和「真实目录（慢，最新）」之间切换。"""
        try:
            idx = (getattr(self, "net_browse_mode", "index") == "index")
            self.net_browse_mode = "real" if idx else "index"
            save_ui_setting("net_browse_mode", self.net_browse_mode)
            self._update_net_btn()
            if self.net_browse_mode == "index":
                self.set_status("网盘浏览：索引显示（不连网盘，秒开）"
                                "—— 想读真实目录再点一下这个按钮")
            else:
                self.set_status(T("网盘浏览：真实目录（会连网盘，慢但最新）"))
            # 就地重新载入当前目录，立刻生效
            if self.view_mode == "dir" and self.current_dir:
                self.load_directory(str(self.current_dir))
        except Exception as _e:
            note_swallowed(T("切换网盘浏览模式失败"), _e)

    def _update_net_btn(self):
        try:
            idx = (getattr(self, "net_browse_mode", "index") == "index")
            # ★★ v26：**width 别按「字符数」硬算 —— 中文字/emoji 会不够宽。**
            #   用户反馈：「右下角『网盘:索引』显示不全，『引』字有部分被隐藏」。
            #   实测：tk scaling=2.0 下这个按钮的 `width=9` 是按
            #   **9 个西文字符**量出来的，而 `🧭 网盘:索引` 里
            #   emoji 和汉字都比西文字符宽 —— 结果**文字右边被切掉**。
            #   现在改成 **width=0（表示由内容自己决定）**，
            #   让 ttk 按真实文字宽度算，绝对不会切。
            if getattr(self, "_status_icons_mode", False):
                txt = "🧭索" if idx else "🧭真"
                self._net_btn.config(text=txt, width=4)
            else:
                self._net_btn.config(
                    text=T("🧭 网盘:索引") if idx else T("🧭 网盘:真实"), width=0)
        except Exception:
            pass

    def _refresh_places(self):
        """「常用位置」下拉：盘符 + 桌面/下载/文档 + 你收藏的 + 索引根目录。"""
        try:
            if getattr(self, "_places", None) is None:
                self._places = {}
            self._places = {}
            adds = []
            for d in self._drives():
                adds.append(("💽 " + d, d))
            # ★★ 2026-10-08：**别再写死 E 盘**（要打包发别人用）——
            #   原来"桌面/下载"写的是 `E:\桌面` / `E:\下载`，
            #   别人电脑上**根本没有 E 盘**（或者没这两个文件夹）→
            #   `os.path.isdir` 为假 → **这两项直接消失**（不算崩，但少了）。
            #   ★ 改成**问 Windows 要**（`USERPROFILE` / `HOMEDRIVE`）：
            #     · 桌面 → `%USERPROFILE%\Desktop`
            #       ★ 中文系统上文件夹真名是"桌面"，但**路径还是 Desktop**
            #         （Windows 用 `desktop.ini` 做显示名，路径不变）——
            #         所以 `Desktop` 是对的。
            #     · 下载 → `%USERPROFILE%\Downloads`
            #   ★ 还**保留老的 E 盘**兜底：本机用户习惯了 E:\桌面，
            #     两边都试，哪个存在加哪个（**可逆**，不破坏现状）。
            _home = Path.home()
            for label, p in (("🖥 桌面", str(_home / "Desktop")),
                             ("🖥 桌面", r"E:\桌面"),
                             ("⬇ 下载", str(_home / "Downloads")),
                             ("⬇ 下载", r"E:\下载"),
                             ("📄 文档", str(_home / "Documents")),
                             ("🏠 主目录", str(_home))):
                if os.path.isdir(p):
                    adds.append((label, p))
            for b in (load_ui_setting("nav_bookmarks", []) or []):
                if isinstance(b, str) and os.path.isdir(b):
                    adds.append(("⭐ " + os.path.basename(b.rstrip("\\")) or b, b))
            try:
                for r in self.store.all_index_roots():
                    adds.append(("📚 索引 " + (r["path"] or ""), r["path"]))
            except Exception:
                pass
            vals = []
            for label, p in adds:
                if label in self._places:
                    continue
                self._places[label] = p
                vals.append(label)
            self._drive_cbo.configure(values=self._drives())
            self._place_cbo.configure(values=vals[:40])
        except Exception as _e:
            note_swallowed(T("刷新「常用位置」下拉失败"), _e)

    def _on_drive_pick(self, event=None):
        d = (self._drive_var.get() or "").strip()
        if d and os.path.isdir(d):
            self.load_directory(d)

    def _on_place_pick(self, event=None):
        label = (self._place_var.get() or "").strip()
        p = (self._places or {}).get(label)
        if p:
            self.load_directory(p)

    def _add_bookmark(self):
        """把当前文件夹收进「常用位置」（⭐ 按钮）。"""
        if not self.current_dir:
            return
        cur = str(self.current_dir)
        try:
            bookmarks = list(load_ui_setting("nav_bookmarks", []) or [])
        except Exception:
            bookmarks = []
        if cur in bookmarks:
            self.set_status(T("这个文件夹已经在「常用位置」里了"))
            return
        bookmarks.append(cur)
        save_ui_setting("nav_bookmarks", bookmarks[:30])
        self._refresh_places()
        self.set_status(T("已加入「常用位置」：{x}", x=cur))

    # ---------------- ★ v25 补丁13：拖放（从资源管理器拖进来）----------------
    def _setup_dnd(self):
        """把「文件列表」注册成拖放目标：从资源管理器拖文件进来 = 复制到这个文件夹。

        ★ 需要 tkinterdnd2（装在 E 盘）；没有就静默跳过，功能照常用，
          只是拖放用不了。
        """
        if not HAS_DND:
            return
        try:
            cv = self.file_list.canvas
            cv.drop_target_register(DND_FILES)
            cv.dnd_bind("<<Drop>>", self._on_drop_files)
            # 拖出去：从程序里把选中的文件拖到资源管理器
            try:
                cv.drag_source_register(1, DND_FILES)
                cv.dnd_bind("<<DragInitCmd>>", self._on_drag_out)
            except Exception as _e:
                note_swallowed(T("注册「拖出去」失败（拖进来仍可用）"), _e)
            self.log_output(T("拖放已就绪：可以把文件从资源管理器拖进列表（复制到当前文件夹）"))
        except Exception as _e:
            note_swallowed(T("注册拖放失败"), _e)

    def _on_drag_out(self, event):
        """把选中的文件拖出去（拖到资源管理器 = 系统当成复制）。

        ★★ 2026-10-03 重要修正 —— 这段是「拖到文件夹上松手 = 移动进去」
        一直不能用的**第二个原因**：

          系统级的「拖出去」是拖放库（tkinterdnd2）在鼠标一动就抢过去的：
          它会开一个**模态的拖动循环**，鼠标被它抓走，
          我们自己写的 `_marquee_move` / `_marquee_end` 就再也收不到动作
          —— 也就是说：**只要在文件上开始拖，程序内部就永远不知道你在拖**
          （实测：合成一次 B1-Motion，程序直接卡死不返回，因为那个拖动
           循环在等一次永远等不到的「松手」）。
          原来这里只在「正在拉框」时返回 None 挡住它；
          「正在拖文件」（_file_drag.started）时没挡 → 于是内部拖动全程失灵。

          现在：**只要是我们自己在拖（拉框 或 拖文件），就返回 None
          让拖放库靠边站**；真想拖到资源管理器，按住 Ctrl 再拖
          （保留这个老功能，免得把它彻底弄没了）。
        """
        try:
            fl = self.file_list
            if getattr(fl, "_marq", None) and fl._marq.get("started"):
                return None
            fd = getattr(fl, "_file_drag", None)
            if fd and fd.get("started") and not _ctrl_down():
                return None
        except Exception:
            pass
        try:
            paths = list(self.file_list.get_selection() or [])
            if not paths:
                return None
            return (COPY, DND_FILES, "{ %s }" % " ".join(
                "{%s}" % p for p in paths))
        except Exception:
            return None

    def _on_drop_files(self, event):
        """资源管理器拖过来的文件/文件夹 → 复制到当前文件夹。"""
        try:
            raw = event.data or ""
            items = self.file_list.tk.splitlist(raw)
        except Exception:
            items = []
        items = [str(x) for x in items if x]
        if not items:
            return
        if not self.current_dir:
            messagebox.showinfo("提示", T("先打开一个文件夹，再把东西拖进来。"),
                                parent=self.root)
            return
        target = str(self.current_dir)
        names = [(os.path.basename(p.rstrip("\\")) or p) for p in items]
        preview = "、".join(names[:4]) + ("…" if len(names) > 4 else "")
        if not messagebox.askyesno(
                "拖进来了 %d 项" % len(items),
                "要把这 %d 项**复制到**：\n%s\n\n  内容：%s\n\n"
                "（是复制，不会动原来的文件）" % (len(items), target, preview),
                parent=self.root):
            return
        self.begin_activity("正在复制拖进来的 %d 项…" % len(items))
        self.log_output("拖放复制：%d 项 → %s" % (len(items), target))

        def worker():
            done, errs = [], []
            for src in items:
                try:
                    name = os.path.basename(src.rstrip("\\")) or src
                    is_dir = os.path.isdir(src)
                    dst = _unique_target_path(target, name, is_dir)
                    if is_dir:
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
                    done.append(dst)
                except Exception as exc:
                    errs.append("%s：%s" % (os.path.basename(str(src)), exc))
            try:
                self._ui_threadsafe(self._drop_done, target, done, errs)
            except Exception as exc:
                note_swallowed(T("worker(_drop_done)：回主线程通知失败"),
                               exc, level="warn")

        threading.Thread(target=worker, daemon=True).start()

    def _drop_done(self, target, done, errs):
        self.end_activity()
        self.log_output("拖放完成：复制了 %d 项" % len(done))
        self.set_status("已把拖进来的 %d 项复制到 %s%s"
                        % (len(done), os.path.basename(target.rstrip("\\")) or target,
                           "" if not errs else "（%d 项失败）" % len(errs)))
        if errs:
            self.log_problem("拖放复制失败：%s" % "；".join(errs[:3]), level="error")
            messagebox.showwarning("有没复制成功的",
                                   "这些没成功：\n\n%s" % "\n".join(errs[:5]),
                                   parent=self.root)
        try:
            self.load_directory(target)
        except Exception as _e:
            note_swallowed(T("拖放后刷新界面失败"), _e)

    def choose_dir(self):
        chosen = filedialog.askdirectory(initialdir=str(self.current_dir))
        if chosen:
            self.load_directory(chosen)

    def go_up(self):
        parent = self.current_dir.parent
        if parent != self.current_dir:
            self.load_directory(parent)

    def _apply_stats_display(self):
        """把「共 N 个 / 未打标签 N / 仅中间标签 N」这几个数字刷到界面上。

        ★★ v26：**这里以前每点一次文件都要重算一遍 800 个文件的标签统计。**
          实测（图本分类 800 行）：`tag_stats_for_paths` 一次要 0.04 秒左右，
          而它是**跟着 `on_file_select` 走的** —— 也就是说
          **你每点一个文件、每框选一次，它都要跑一遍**。
          一屏点十几下就攒出明显的卡顿感。
          ★ 关键：这几个数字只跟「当前列表里有哪些文件」有关，
            **跟你选中了哪个文件完全没关系**。
            所以这里缓存上一次的结果（用文件列表的指纹判断），
            列表没变就直接用缓存，一点活都不干。
        """
        paths = [r["path"] for r in self._base_rows]
        if not paths:
            self.stat_total_lbl.config(text="")
            self.stat_untagged_lbl.config(text="")
            self.stat_mid_lbl.config(text="")
            self._stats_cache_key = None
            return
        key = (len(paths), paths[0], paths[-1])
        cached = getattr(self, "_stats_cache", None)
        if cached is not None and getattr(self, "_stats_cache_key", None) == key:
            total, untagged, mid_only = cached
        else:
            total, untagged, mid_only = self.store.tag_stats_for_paths(paths)
            self._stats_cache = (total, untagged, mid_only)
            self._stats_cache_key = key
        if self.stats_filter == "untagged":
            self.stat_total_lbl.config(text=T("共 {n}    【仅显示未打标签】", n=total))
        elif self.stats_filter == "mid_only":
            self.stat_total_lbl.config(
            text=T("共 {n}    【仅显示仅中间标签】", n=total))
        else:
            self.stat_total_lbl.config(text=T("共 {n} 项", n=total))
        self.stat_untagged_lbl.config(
            text=T("未打标签 {n}", n=untagged) if untagged else "")
        self.stat_mid_lbl.config(
            text=f"仅中间标签 {mid_only}" if mid_only else "")

    def _refresh_file_list_from_base(self):
        if not self.stats_filter:
            rows = list(self._base_rows)
        else:
            paths = [r["path"] for r in self._base_rows]
            keep = set(self.store.filter_paths(paths, self.stats_filter))
            rows = [r for r in self._base_rows if r["path"] in keep]
        self.file_list.set_rows(rows)
        self._apply_stats_display()

    def toggle_stats_filter(self, mode):
        if self.stats_filter == mode:
            self.stats_filter = None
        else:
            self.stats_filter = mode
        self._refresh_file_list_from_base()

    def _clear_stats_filter(self):
        self.stats_filter = None

    def load_directory(self, path):
        if not path:
            return                      # ★ v25 补丁：别拿 None 去 Path()
        try:
            path = Path(path).expanduser().resolve()
        except OSError:
            path = Path(path).expanduser()
        # ★ v25 补丁18：打开目录前不再「先探一下真实目录」。
        #   网盘里删掉的目录、或者一时读不到的目录，以前会弹一个
        #   「不是有效的文件夹」警告框，日志里还刷一行错误 —— 很烦。
        #   现在：
        #     · 网盘 + 索引模式：压根不碰网盘（不 stat），索引里有就显示，
        #       没有就只在状态栏/日志里轻轻说一句，**不弹窗、不算错误**；
        #     · 网盘 + 真实模式：读不到也不弹窗，同样轻轻说一句；
        #     · 本地盘：读不到还是照旧弹窗（本地打错路径是真错了）。
        remote = False
        try:
            remote = is_remote_path(str(path))
        except Exception:
            remote = False
        net_mode = getattr(self, "net_browse_mode", "index")
        if remote and net_mode == "index":
            cached_first = None
            if self.dir_cache_enabled:
                try:
                    cached_first = self.store.get_dir_entries(str(path))
                except Exception:
                    cached_first = None
            if not cached_first:
                self.current_dir = path
                self.path_var.set(str(path))
                self.list_title.config(text=T("文件（这个网盘目录读不到）"))
                self._invalidate_tag_scope()
                self._view_spec = {
                    "kind": "dir", "path": str(path),
                    "all_paths": [], "entries_map": {}, "total": 0,
                }
                self._page = 0
                self._load_current_page()
                self.log_output(
                    T("这个网盘目录现在读不到（网盘里可能已经删掉了 / "
                      "网盘一时没醒）：{p}  · 已跳过，不算错误。",
                      p=path))
                self.log_output(
                    T("想看真实目录：点右下角「🧭 网盘:索引」切成「真实」。"))
                self.set_status(
                    T("{p}    目录读不到（可能已删除）—— 没连网盘，已跳过", p=path))
                return
        elif not path.is_dir():
            if remote:
                self.log_output(
                    T("这个网盘目录现在读不到（网盘里可能已经删掉了 / "
                      "网盘一时没醒）：{p}  · 已跳过，不算错误。",
                      p=path))
                self.set_status(f"{path}    目录读不到（可能已删除），已跳过")
                return
            messagebox.showwarning("路径无效", f"不是有效的文件夹：\n{path}")
            return

        self.current_dir = path
        self.path_var.set(str(path))
        # ★ v25 补丁13：记进导航历史（后退/前进用）
        self._nav_record(path)
        self.view_mode = "dir"
        self.sidebar.set_selected("all", None)
        self.current_cat_id = None
        # ★ v25：作废还在跑的「含子目录搜索」（迟到的结果不许回来）
        self._cancel_recursive_scan(invalidate_cache=True)
        self._search_return_state = None   # 用户主动切视图了
        self.list_info.config(text="")
        self.list_title.config(text=T("文件"))
        self._clear_stats_filter()
        self._reset_category_hidden_tags()
        self.file_list.clear_thumbnail_cache()

        dir_key = str(path)

        # ★ 缓存优先：先读缓存立即显示
        cached = None
        if self.dir_cache_enabled:
            try:
                cached = self.store.get_dir_entries(dir_key)
            except Exception:
                cached = None

        # ★ v25 补丁14：网盘（网络盘）浏览模式
        #   index = 只看索引（不连网盘，秒开；用户抱怨慢就是因为以前这里会去连真网盘）
        #   real  = 读真实目录（当前最新，但网盘慢）
        remote = False
        try:
            remote = is_remote_path(dir_key)
        except Exception:
            remote = False
        net_mode = getattr(self, "net_browse_mode", "index")

        if cached:
            # 缓存里把「X: 写法」和「UNC 写法」都认了（见 _net_cache_variants）
            self._apply_dir_entries(dir_key, cached,
                                    from_cache=True)
            scanned_at = self.store.get_dir_scan_time(dir_key)
            if remote and net_mode == "index":
                self.set_status(
                    T("{k}    共 {n} 项  ·  索引显示"
                      "（缓存于 {t}；要看真实目录点右下角 🧭）",
                      k=dir_key, n=len(cached), t=scanned_at))
            else:
                self.set_status(
                    T("{k}    共 {n} 项  ·  "
                      "缓存于 {t}，后台比对中…",
                      k=dir_key, n=len(cached), t=scanned_at))
        elif remote and net_mode == "index":
            # 网盘 + 索引模式 + 索引里没有这个目录 → 不连网盘，给个提示
            self.list_title.config(text=T("文件（索引里没有这个目录）"))
            self._invalidate_tag_scope()
            self._view_spec = {
                "kind": "dir",
                "path": dir_key,
                "all_paths": [],
                "entries_map": {},
                "total": 0,
            }
            self._page = 0
            self._load_current_page()
            self.log_output(
                "索引里没有这个网盘目录：%s（没连网盘）。要看真实目录："
                "点右下角「🧭 网盘:索引」切到「真实」，或先在索引管理里扫一次。"
                % dir_key)
            self.set_status(
                f"{dir_key}    索引里没有这个目录 —— 点右下角「🧭 网盘:索引」"
                f"切成「真实」就能读真目录（会慢）")
        else:
            self.list_title.config(text=self._safe_list_title("文件（首次扫描中）"))
            self._invalidate_tag_scope()
            self._view_spec = {
                "kind": "dir",
                "path": dir_key,
                "all_paths": [],
                "entries_map": {},
                "total": 0,
            }
            self._page = 0
            self._load_current_page()
            self.set_status(T("{k}    首次扫描目录…", k=dir_key))

        # 延迟启动后台扫描（用户切走就不扫）
        # ★ v25 补丁14：网盘 + 索引模式下**不去连网盘**（这就是以前卡的原因）
        # ★★ v25 补丁42：**上面这行注释其实没做到，这里才是真修。**
        #   用户直觉非常准：「网盘文件老是不管用索引还是真目录都老走真目录，
        #   导致软件卡卡的」。
        #   原因：原来只有「**没有缓存**」那一条路（else 分支）才被这句挡住；
        #   而**有缓存**时（cached 分支）无论什么模式都会走到这里 ——
        #   于是你切到「🧭 网盘:索引」之后，每打开一个网盘文件夹，
        #   它虽然立刻用索引显示了内容（看起来秒开 ✓），
        #   却又**偷偷在后台 os.scandir 真去连了一次网盘**！
        #   后果：网盘一忙，后台线程排队、状态栏一直显示「扫描目录…」、
        #   整个程序发涩 —— 正是用户感觉到的「卡卡的」。
        #   现在：网盘 + 索引模式**一律不排后台扫描**（用户想要最新内容，
        #   点右下角切成「真实」就行，那时候才真扫）。
        try:
            _remote_now = is_remote_path(dir_key)
        except Exception:
            _remote_now = False
        _net_mode_now = getattr(self, "net_browse_mode", "index")
        if bool(_remote_now and _net_mode_now == "index"):
            # 索引模式：完全不碰网盘。顺手把状态栏那句「后台比对中…」改掉，
            # 免得你以为它还在偷偷干活。
            try:
                if cached:
                    self.set_status(
                        f"{dir_key}    共 {len(cached)} 项  ·  索引显示"
                        f"（点右下角 🧭 可切「真实」看最新）")
            except Exception:
                pass
        else:
            self._schedule_bg_scan(dir_key)

    def _apply_dir_entries(self, dir_key, entries, from_cache=False):
        """把目录条目应用成当前视图"""
        entries = list(entries)
        entries.sort(key=lambda x: (not x[1], x[0].lower()))
        all_paths = [os.path.join(dir_key, name)
                     for (name, _d, _s, _m) in entries]
        entries_map = {name: (d, s, m) for (name, d, s, m) in entries}
        self._invalidate_tag_scope()
        self._view_spec = {
            "kind": "dir",
            "path": dir_key,
            "all_paths": all_paths,
            "entries_map": entries_map,
            "total": len(all_paths),
        }
        self.list_title.config(text=T("文件"))
        self._page = 0
        self._load_current_page()

    def _schedule_bg_scan(self, dir_key):
        # ★ v25 补丁18：已经知道读不到的目录（网盘里删了）就别再排了，
        #   省得每次点开都去撞一次、还刷日志。
        try:
            if dir_key in self._dead_dirs():
                return
        except Exception:
            pass
        self._bg_scan_pending_dir = dir_key
        if self._bg_scan_timer is not None:
            try:
                self.root.after_cancel(self._bg_scan_timer)
            except Exception:
                pass
        self._bg_scan_timer = self.root.after(500, self._try_start_bg_scan)

    def _try_start_bg_scan(self):
        self._bg_scan_timer = None
        # ★ v25 补丁14：已经在关窗了就不要再起扫描线程 ——
        #   扫描线程结束时会 root.after() 回主线程，窗口没了就会崩。
        if getattr(self, "_closing", False):
            return
        if self._bg_scan_running_dir is not None:
            # ★★ 2026-10-03：**自愈一次。**
            #   实测踩到过：扫描线程明明早就干完了（线程已结束），可它
            #   「回主线程说一声」那一步卡住了（后台线程调 root.after 会卡，
            #   见 _ui_threadsafe 的说明）—— 于是这个「我正忙着」的标记
            #   永远挂着，**以后打开任何没有缓存的文件夹都不会再扫，
            #   列表一直是空的**（用户看到的「首次扫描中…」永远不动）。
            #   这里发现线程已经没了就当它没在跑，继续往下扫。
            _thr = getattr(self, "_bg_scan_thread", None)
            if _thr is not None and not _thr.is_alive():
                self._bg_scan_running_dir = None
                self._bg_scan_thread = None
                try:
                    self.end_activity()
                except Exception:
                    pass
                try:
                    self.log_output(T("上一次目录扫描的「回话」丢了，已自动重来一次。"))
                except Exception:
                    pass
            else:
                return
        d = getattr(self, "_bg_scan_pending_dir", None)
        if not d:
            return
        self._bg_scan_pending_dir = None
        self._bg_scan_running_dir = d
        self.begin_activity(T("扫描目录：{x}",
                                   x=os.path.basename(d) or d))
        self.log_output(f"后台扫描目录：{d}")
        self._bg_scan_thread = threading.Thread(
            target=self._bg_scan_worker, args=(d,), daemon=True)
        self._bg_scan_thread.start()

    def _bg_scan_worker(self, dir_key):
        entries = []
        err = None
        try:
            with os.scandir(dir_key) as it:
                for e in it:
                    name = e.name
                    is_d = False
                    size = None
                    mtime = None
                    try:
                        is_d = e.is_dir(follow_symlinks=False)
                        if not is_d:
                            try:
                                st = e.stat()
                                size = st.st_size
                                mtime = st.st_mtime
                            except OSError:
                                pass
                    except OSError:
                        pass
                    entries.append((name, is_d, size, mtime))
        except Exception as exc:
            err = str(exc)
        # ★ v25 补丁18：往界面回话之前先看一眼「程序是不是正在关」。
        #   关窗时如果这个线程还在跑，它 root.after() 上去会让 Tk 直接崩
        #   （表现为关窗闪退 / 进程退出码不是 0）。这里先检查、再试，
        #   宁可不刷新列表，也不能把程序带崩。
        if not APP_CLOSING:
            # ★★ 2026-10-03：这里原来写的是 self.root.after(...) ——
            #   后台线程调 root.after 偶尔会卡死在 tkinter 内部，
            #   卡住就等于「扫完了但没人知道」，列表永远空着。
            #   现在走信箱（后台线程只碰一个 Python 列表，绝不碰 Tcl）。
            self._ui_threadsafe(self._on_bg_scan_done, dir_key, entries, err)

    def _dir_view_is_plain(self, dir_key):
        """★ v25：现在显示的到底是不是「这个目录的普通文件列表」。

        搜索（含子目录 / 关键字）、标签筛选、分类视图下都不是 ——
        这时后台目录扫描回来了也不能去改列表，否则会把搜索结果
        冲成整个目录的文件。
        """
        if self.view_mode != "dir" or not self.current_dir:
            return False
        if str(self.current_dir) != dir_key:
            return False
        spec = self._view_spec or {}
        if spec.get("kind") != "dir":
            return False
        if self._tag_filter_base_spec is not None:
            return False
        return True

    def _on_bg_scan_done(self, dir_key, entries, err):
        self._bg_scan_running_dir = None
        # ★ v25 补丁14：关窗过程中这个回调还可能被排到队列里，进来先看一眼，
        #   窗口没了就直接返回，不要再去碰已经销毁的控件。
        if getattr(self, "_closing", False):
            return
        self.end_activity()
        plain_dir_view = self._dir_view_is_plain(dir_key)
        if err is None:
            self.log_output(T("扫描完成：{k}  共 {n} 项",
                              k=dir_key, n=len(entries)))
            try:
                self.store.save_dir_entries(dir_key, entries)
            except Exception as exc:
                self.log_problem(f"写目录缓存失败：{exc}", level="error")
            if plain_dir_view:
                self._apply_dir_entries(dir_key, entries)
                self.set_status(
                    T("{k}    共 {n} 项（已刷新）",
                      k=dir_key, n=len(entries)))
        else:
            # ★ v25 补丁18：目录读不到时别再当「错误」刷屏。
            #   网盘里删除过的目录、空目录、一时读不到的目录，以前每点开
            #   一次就在「问题」面板里报一次红 —— 用户反映很烦。
            #   现在把「东西不在了」这一类单独处理：只记一句普通日志、
            #   记住这个目录别再反复去试；真的读不动（权限/网络坏）才报错。
            if is_gone_error(err):
                try:
                    self._dead_dirs().add(dir_key)
                except Exception:
                    pass
                self.log_output(
                    f"这个目录现在读不到（网盘里可能已经删掉了）：{dir_key}"
                    f"  · 已跳过，不再重试")
                if plain_dir_view:
                    self.set_status(
                        f"{dir_key}    目录读不到（可能已删除），已跳过")
            else:
                self.log_problem(f"目录扫描失败：{dir_key} - {err}",
                                 level="error")
                if plain_dir_view:
                    self.set_status(f"目录扫描失败：{err}")
        if getattr(self, "_bg_scan_pending_dir", None):
            self._try_start_bg_scan()

    def _dead_dirs(self):
        """★ v25 补丁18：记住「读不到 / 已删除」的目录，别再反复去试它。"""
        s = getattr(self, "_dead_dir_set", None)
        if s is None:
            s = set()
            self._dead_dir_set = s
        return s

    def _load_current_page(self):
        """根据 _view_spec 载入当前页的数据。"""
        spec = self._view_spec
        if not spec:
            return
        kind = spec.get("kind")
        ps = FILE_PAGE_SIZE
        pg = self._page

        try:
            if kind == "dir":
                all_paths = spec.get("all_paths") or []
                total = len(all_paths)
                page_paths = all_paths[pg * ps:(pg + 1) * ps]
                with_loc = False
            elif kind == "all":
                total = self.store.all_files_count()
                page_paths = self.store.all_files_page(ps, pg * ps)
                with_loc = True
            elif kind == "cat":
                cid = spec["cid"]
                total = self.store.files_in_category_count(cid)
                page_paths = self.store.files_in_category_page(
                    cid, ps, pg * ps)
                with_loc = True
            elif kind == "paths":
                all_paths = spec.get("paths") or []
                total = len(all_paths)
                page_paths = all_paths[pg * ps:(pg + 1) * ps]
                with_loc = True
            else:
                return
        except Exception as exc:
            self.set_status(f"载入失败：{exc}")
            self.log_problem(f"载入页面失败（{kind}）：{exc}",
                             level="error")
            return

        spec["total"] = total
        self._page_total = total

        self._populate_paths_page(page_paths, with_location=with_loc)
        self._update_page_ui()

    def _populate_paths_page(self, paths, with_location=True):
        """只载入一页文件（不做全量查询、不做全量标签）
           ★ 不 stat 任何文件（网盘 stat 会走网络，几秒就卡住了）"""
        # ★ v22：自动打标签已改成「手动启动」。
        #   打开文件夹 / 打开分类库时，这里不再自动跑自动标签规则；
        #   只有点工具栏的「🏷 重读标签」（或菜单「🏷 重读标签…」）
        #   才会按「自动标签规则」把标签更新一遍。
        #   v21 及以前这里是受 auto_scan_on_open 控制的自动扫描，现在已取消。

        try:
            tag_map = self.store.tags_for_paths(paths)
        except Exception:
            tag_map = {}

        spec = self._view_spec or {}
        entries_map = spec.get("entries_map") or {}

        # ★ 目录视图：直接用 entries_map
        #   其他视图：批量从 dir_cache 表查一次（纯 SQLite，不碰磁盘）
        dir_meta_lookup = {}
        if not entries_map:
            try:
                dir_meta_lookup = self.store.lookup_paths_meta(paths)
            except Exception:
                dir_meta_lookup = {}

        rows = []
        for p in paths:
            path = Path(p)
            name = path.name
            is_dir = False
            size = "?"
            size_bytes = None

            meta = entries_map.get(name)
            if meta is None:
                meta = dir_meta_lookup.get(p)

            if meta is not None:
                is_dir = meta[0]
                if is_dir:
                    size = ""
                    size_bytes = -1
                else:
                    sz = meta[1]
                    if sz is not None:
                        size_bytes = sz
                        size = self.human_size(sz)
                    else:
                        size = "?"
            else:
                # ★ 完全没缓存：按文件名猜，绝不 stat
                is_dir = ("." not in name)
                if is_dir:
                    size = ""
                    size_bytes = -1
                else:
                    size = "?"
                    size_bytes = None

            rows.append({
                "path": p,
                "name": name,
                "kind": "文件夹" if is_dir else self.file_kind(name),
                "size": size,
                "size_bytes": size_bytes,
                "location": str(path.parent) if with_location else "",
                "tags": tag_map.get(p, []),
            })
        self._base_rows = rows
        self._refresh_file_list_from_base()

    def refresh_rows_tags(self):
        paths = [r["path"] for r in self.file_list.rows]
        if not paths:
            return
        # ★ v22：这里不再自动跑自动标签规则（改为手动点「🏷 重读标签」），
        #   只按数据库里已有的标签刷新显示。
        tag_map = self.store.tags_for_paths(paths)
        self.file_list.refresh_all_tags(tag_map)
        for r in self._base_rows:
            if r["path"] in tag_map:
                r["tags"] = tag_map[r["path"]]
        # ★ v26：标签真的变了 → 把统计缓存作废，下次重新算
        self._stats_cache_key = None
        self._apply_stats_display()
        try:
            self.refresh_categories()
            self.refresh_tags()
        except Exception:
            pass

    def refresh_all(self):
        # 用户主动刷新，允许重算分类计数
        self._last_cat_refresh_ts = 0.0
        self.refresh_categories()
        self.refresh_tags()
        if self.view_mode == "all":
            self.show_all_files()
        elif self.view_mode == "cat" and self.current_cat_id:
            self.show_category(self.current_cat_id)
        else:
            self.load_directory(self.current_dir)

    def show_all_files(self):
        self.view_mode = "all"
        self.current_cat_id = None
        # ★ v23：同样取消还排队的目录后台扫描
        self._bg_scan_pending_dir = None
        # ★ v25：作废还在跑的「含子目录搜索」
        self._cancel_recursive_scan(invalidate_cache=True)
        self._search_return_state = None
        self.list_title.config(text=T(T("全部文件")))
        self.path_var.set(T("全部文件"))
        self.list_info.config(text="")
        self._clear_stats_filter()
        self._reset_category_hidden_tags()
        self._invalidate_tag_scope()
        self._view_spec = {"kind": "all"}
        self._page = 0
        self._load_current_page()
        self.sidebar.set_selected("all", None)
        self.set_status(f"全部已管理文件：{self._page_total} 个")

    def navigate_to_path(self, path):
        """★★ 2026-01-26：文件树节点双击 → 跳转到对应目录

        ★★ 2026-10-04 修复（小马留下的坑）：它自己拼了一份「跳转」流程，
          可是**拼错了两个地方** —— 双击目录树里的目录，文件列表**出不来内容**：
            · `self.current_dir` 没更新（程序别的地方都认这个属性，
              不更新的话「当前在看哪个文件夹」还是老地方）；
            · `self._view_spec` 写成了 {"kind": "dir", "dir": path}，
              可是程序里别处一律用 **"path"** 这个键 —— 键名不对，
              下一页就取不到目录、列表一直是空的。
            · 也没做「上一次还在跑的搜索要作废」等收尾（_load_directory 里都有）。
          现在直接**转交给正规的 load_directory()** —— 双击目录树
          就和在文件列表里双击文件夹、或在地址栏敲路径**完全一样**。
        """
        if not path or not os.path.isdir(path):
            return
        try:
            self.load_directory(str(path))
        except Exception as _e:
            note_swallowed(T("从文件目录树跳转失败"), _e)

    def show_category(self, cid):
        cats = {c["id"]: c for c in self.store.all_categories()}
        cat = cats.get(cid)
        if cat is None:
            return
        self.view_mode = "cat"
        self.current_cat_id = cid
        # ★ v23：切到分类视图时取消还排队的目录后台扫描
        #   （否则它跑完回来会把分类列表冲成文件夹列表）
        self._bg_scan_pending_dir = None
        # ★ v25：作废还在跑的「含子目录搜索」
        self._cancel_recursive_scan(invalidate_cache=True)
        self._search_return_state = None
        self._clear_stats_filter()
        links = self.store.linked_tag_ids(cid)
        hint = ""
        if links:
            hint = f"（含 {len(links)} 个标签超链接）"
        self.list_title.config(text=f"分类：{cat['name']}{hint}")
        self.path_var.set(f"分类：{cat['name']}")
        self.list_info.config(text="")
        self._invalidate_tag_scope()
        self._view_spec = {"kind": "cat", "cid": cid}
        self._page = 0
        # 用缓存数字先显示，避免界面卡住
        cached_cnt = int(cat.get("cnt") or 0)
        self._page_total = cached_cnt
        self._update_page_ui()
        self.sidebar.set_selected("cat", cid)
        if cached_cnt > 0:
            self.set_status(
                f"分类「{cat['name']}」：{cached_cnt} 个文件{hint}（加载中…）")
        else:
            self.set_status(
                f"分类「{cat['name']}」：{hint}"
                f"（数字统计中，稍后自动刷新；先显示第一页…）")
        self.log_output(
            f"打开分类：{cat['name']}（缓存计数 {cached_cnt}）")
        # ★ 应用这个分类保存的"打开时自动屏蔽标签"
        self._apply_category_hidden_tags(cid)
        # 只在缓存还是 0 时算一次，避免每次点分类都重算
        if cached_cnt == 0:
            self._bg_refresh_category_counts()
        # 让界面先刷一下，再开始真正的加载
        self.root.after(1, self._load_current_page)

    def refresh_categories(self):
        # 先用缓存显示（秒回）
        try:
            self.sidebar.set_categories(self.store.all_categories())
        except Exception as _e:
            note_swallowed(T("左侧分类库列表显示失败"), _e)
        # ★ 顺手根据分类名长度重新调整左侧宽度
        try:
            self._auto_sash_sidebar()
        except Exception:
            pass
        # 后台慢慢算准确数字（有 5 分钟冷却，不会每次都跑）
        self._bg_refresh_category_counts()

    def _bg_refresh_category_counts(self):
        if getattr(self, "_cat_refresh_running", False):
            return
        # ★ 冷却：5 分钟内不重复算（除非用户主动点"刷新"清掉时间戳）
        last = getattr(self, "_last_cat_refresh_ts", 0.0)
        if time.time() - last < 300:
            return
        self._last_cat_refresh_ts = time.time()
        self._cat_refresh_running = True
        self.begin_activity("统计分类中…")
        self.log_output(T("开始后台统计分类计数"))

        def worker():
            # ★★ v26（2026-10-01）：**后台线程自己开一条数据库连接。**
            #   以前它用主程序那条公用连接 —— 它一写，主界面就卡
            #   （用户日志里「界面无响应 3.6 秒」就是这么来的）。
            #   现在用独立连接：WAL 模式下「一个写 + 多个读」互不干扰。
            side = None
            try:
                side = self.store.open_side_connection()
            except Exception as _e:
                note_swallowed(T("后台统计分类：开独立连接失败（会用公用连接，可能稍卡）"), _e)
            conn = side if side is not None else self.store.conn
            try:
                cats = self.store.all_categories()
                total = len(cats)
                self.log_progress(f"分类统计开始，共 {total} 个分类")
                for i, c in enumerate(cats, 1):
                    try:
                        cid = c.get("id") if isinstance(c, dict) else None
                        cname = c.get("name", "") if isinstance(c, dict) else str(c)
                    except Exception:
                        continue
                    if cid is None:
                        continue
                    try:
                        # ★ 计数和写入都走独立连接
                        cnt = self.store._compute_category_count(cid, conn=conn)
                        conn.execute(
                            "UPDATE categories SET cached_cnt = ? "
                            "WHERE id = ?", (cnt, cid))
                        conn.commit()
                        self.log_progress(
                            f"  [{i}/{total}] {cname}：{cnt} 个文件")
                    except Exception as e:
                        self.log_problem(
                            f"分类「{cname}」统计失败：{e}",
                            level="warn")
                self.log_output(f"分类计数统计完成：{total} 个分类")
            except Exception as exc:
                self.log_problem(f"分类计数统计失败：{exc}", level="error")
            finally:
                if side is not None:
                    try:
                        side.close()
                    except Exception:
                        pass
            try:
                self._ui_threadsafe(self._on_cat_counts_ready)
            except Exception as exc:
                note_swallowed(T("worker(_on_cat_counts_ready)：回主线程通知失败"),
                               exc, level="warn")

        threading.Thread(target=worker, daemon=True).start()

    def _on_cat_counts_ready(self):
        self._cat_refresh_running = False
        self._last_cat_refresh_ts = 0.0
        self.end_activity()
        try:
            self.sidebar.set_categories(self.store.all_categories())
        except Exception as _e:
            note_swallowed(T("分类库刷新后显示失败"), _e)

    def new_category(self):
        dlg = CategoryDialog(self.root, "新建分类")
        if not dlg.result:
            return
        try:
            self.store.create_category(**dlg.result)
        except Exception as exc:
            messagebox.showerror("创建失败", str(exc))
            return
        self.refresh_categories()
        self.set_status(f"已新建分类「{dlg.result['name']}」")

    def edit_category(self, cid, field):
        cats = {c["id"]: c for c in self.store.all_categories()}
        cat = cats.get(cid)
        if not cat:
            return
        if field == "name":
            new_name = SimpleInputDialog(self.root, "重命名分类",
                                         initial=cat["name"]).result
            if not new_name or new_name == cat["name"]:
                return
            try:
                self.store.update_category(cid, name=new_name)
            except Exception as exc:
                messagebox.showerror("错误", str(exc))
                return
        elif field == "color":
            _rgb, hexv = colorchooser.askcolor(
                color=cat["color"], title=f"选择「{cat['name']}」的颜色")
            if not hexv:
                return
            self.store.update_category(cid, color=hexv)
        else:
            dlg = CategoryDialog(self.root, "编辑分类", cat=cat)
            if not dlg.result:
                return
            try:
                self.store.update_category(cid, **dlg.result)
            except Exception as exc:
                messagebox.showerror("错误", str(exc))
                return
        self.refresh_categories()
        if self.view_mode == "cat" and self.current_cat_id == cid:
            self.show_category(cid)

    def delete_category(self, cid, name):
        if not messagebox.askyesno(
                "确认删除",
                f"确定删除分类「{name}」吗？\n（分类里的文件本身和标签都不会被删除）"):
            return
        self.store.delete_category(cid)
        self.refresh_categories()
        if self.view_mode == "cat" and self.current_cat_id == cid:
            self.show_all_files()
        self.set_status(f"已删除分类「{name}」")

    def clear_category_direct(self, cid, name):
        if not messagebox.askyesno(
                "确认",
                f"清空分类「{name}」的直接成员吗？\n（按标签超链接进来的文件不受影响）"):
            return
        with self.store.conn:
            self.store.conn.execute(
                "DELETE FROM category_files WHERE category_id = ?", (cid,))
        self.refresh_categories()
        if self.view_mode == "cat" and self.current_cat_id == cid:
            self.show_category(cid)
        self.set_status(f"已清空分类「{name}」的直接成员")

    def link_category_tags(self, cid, name):
        dlg = CategoryTagLinkDialog(self.root, self.store, cid, name)
        if not dlg.saved:
            return
        self.refresh_categories()
        if self.view_mode == "cat" and self.current_cat_id == cid:
            self.show_category(cid)
        n = len(self.store.linked_tag_ids(cid))
        self.set_status(f"分类「{name}」已关联 {n} 个标签超链接")

    def show_category_tag_links(self, cid, name):
        linked = self.store.linked_tag_ids(cid)
        if not linked:
            messagebox.showinfo("已关联标签",
                                f"分类「{name}」尚未关联任何标签",
                                parent=self.root)
            return
        tag_map = {t[0]: t[1] for t in self.store.all_tags()}
        names = [tag_map.get(t, f"#{t}") for t in linked]
        messagebox.showinfo("已关联标签",
                            f"分类「{name}」关联了 {len(names)} 个标签：\n\n"
                            + "\n".join("· " + n for n in names),
                            parent=self.root)

    # ---------- ★ 分类的"打开时自动屏蔽标签" ----------
    def edit_category_hidden_tags(self, cid, name):
        dlg = CategoryHiddenTagsDialog(self.root, self.store, cid, name)
        if not dlg.saved:
            return
        n = len(self.store.get_category_hidden_tags(cid))
        if n:
            self.set_status(f"分类「{name}」已设置 {n} 个打开时自动屏蔽的标签")
        else:
            self.set_status(f"分类「{name}」不再自动屏蔽任何标签")
        if self.view_mode == "cat" and self.current_cat_id == cid:
            self.show_category(cid)

    def _apply_category_hidden_tags(self, cid):
        """把某个分类保存的"自动屏蔽标签"应用到当前文件列表。"""
        try:
            hidden = self.store.get_category_hidden_tags(cid)
        except Exception:
            hidden = set()
        self.file_list.hidden_tag_ids = set(hidden)
        try:
            self.file_list._render_tag_bar()
            self.file_list._recompute_layout()
            self.file_list._redraw()
        except Exception:
            pass

    def _reset_category_hidden_tags(self):
        """切到非分类视图（目录/全部/筛选）时，清掉自动屏蔽。"""
        try:
            if self.file_list.hidden_tag_ids:
                self.file_list.hidden_tag_ids.clear()
                self.file_list._render_tag_bar()
                self.file_list._recompute_layout()
                self.file_list._redraw()
        except Exception:
            pass

    def add_selection_to_category(self, cid, cname):
        paths = self.file_list.get_selection()
        if not paths:
            return
        n = 0
        for path in paths:
            self.store.add_file_to_category(cid, path)
            n += 1
        self.refresh_categories()
        if self.view_mode == "cat":
            self.show_category(self.current_cat_id)
        self.set_status(f"已把 {n} 项添加到分类「{cname}」")

    def remove_from_current_category(self):
        if self.view_mode != "cat" or not self.current_cat_id:
            messagebox.showinfo("提示", T("当前不在分类视图中"))
            return
        paths = self.file_list.get_selection()
        if not paths:
            return
        for path in paths:
            self.store.remove_file_from_category(self.current_cat_id, path)
        self.refresh_categories()
        self.show_category(self.current_cat_id)

    def _update_page_ui(self):
        try:
            total = self._page_total or 0
            ps = FILE_PAGE_SIZE
            n_pages = max(1, (total + ps - 1) // ps)
            page_disp = self._page + 1
            if total == 0:
                self.page_info_lbl.config(text=T("共 0 项"))
            else:
                self.page_info_lbl.config(
                    text=T("第 {a} / {b} 页    共 {c} 项",
                                                  a=page_disp, b=n_pages, c=total))
            if self._page <= 0:
                self.page_prev_btn.state(["disabled"])
            else:
                self.page_prev_btn.state(["!disabled"])
            if self._page >= n_pages - 1:
                self.page_next_btn.state(["disabled"])
            else:
                self.page_next_btn.state(["!disabled"])
        except Exception:
            pass

    # ---------- ★ v24：标签条作用范围（当前页 / 整个视图）----------
    def _invalidate_tag_scope(self):
        """基础视图换了 / 标签变了 → 整库标签统计作废。"""
        self._tag_scope_cache = None
        self._tag_scope_cache_key = None
        self._tag_scope_scan_key = None
        # 注意：不清 _tag_scope_inflight —— 同一个视图正在统计时不要重复开线程
        self._tag_filter_base_spec = None
        try:
            self.file_list.set_tag_scope_stats(None)
        except Exception:
            pass
        # 当前若在「整个视图」范围，顺手重新统计（异步，避免打断视图切换）
        if getattr(self.file_list, "tag_scope", "page") == "view":
            try:
                self.root.after(1, self._start_tag_scope_scan)
            except Exception:
                pass

    def _tag_base_spec(self):
        """标签筛选前的原始视图规格（没在筛选时就是当前视图）。"""
        return self._tag_filter_base_spec or self._view_spec or {}

    def _tag_scope_base_paths(self):
        """「整个视图」范围里的文件全集（纯查库，不碰磁盘）。"""
        spec = self._tag_base_spec()
        kind = spec.get("kind")
        try:
            if kind == "cat":
                cid = spec.get("cid")
                if cid is None:
                    return []
                return list(self.store.files_in_category(cid))
            if kind == "all":
                return list(self.store.all_files())
            if kind == "dir":
                return list(spec.get("all_paths") or [])
            if kind == "paths":
                return list(spec.get("paths") or [])
        except Exception as exc:
            self.log_problem(f"取标签作用范围失败：{exc}", level="warn")
        return []

    @staticmethod
    def _tag_scope_key(spec, paths):
        return (spec.get("kind"), spec.get("cid"), len(paths),
                paths[0] if paths else "", paths[-1] if paths else "")

    def _on_tag_scope_changed(self, scope):
        if scope == "view":
            self._start_tag_scope_scan()
            self.set_status(T("标签条作用范围：整个视图（正在统计标签…）"))
        else:
            try:
                self.file_list.set_tag_scope_stats(None)
            except Exception:
                pass
            if self._restore_tag_filter_view():
                self.set_status(T("标签条作用范围：当前页（已还原视图）"))
            else:
                self.set_status(T("标签条作用范围：当前页"))

    def _on_tag_filter_view(self):
        """FileList 在「整个视图」范围下点了标签 → 重建文件列表。"""
        self._apply_tag_scope_filter()

    def _start_tag_scope_scan(self):
        """后台统计「整个视图」里的标签（纯 SQLite 查询，不 stat 磁盘）。"""
        spec = self._tag_base_spec()
        paths = self._tag_scope_base_paths()
        key = self._tag_scope_key(spec, paths)
        if self._tag_scope_cache_key == key and self._tag_scope_cache:
            self._tag_scope_scan_done(key, paths, self._tag_scope_cache[0], None)
            return
        if self._tag_scope_inflight == key:
            return                      # 同一个视图已经在统计了
        self._tag_scope_inflight = key
        self._tag_scope_scan_key = key
        if not paths:
            self._tag_scope_scan_done(key, paths, {}, None)
            return
        try:
            self.file_list.show_tag_scope_hint("（正在统计整个视图的标签…）")
        except Exception:
            pass
        self.log_output(
            f"标签条作用范围：统计整个视图的标签（{len(paths)} 个文件）")

        def worker():
            try:
                tag_map = self.store.tags_for_paths(paths)
                err = None
            except Exception as exc:
                tag_map, err = {}, exc
            try:
                self._ui_threadsafe(self._tag_scope_scan_done,
                                    key, paths, tag_map, err)
            except Exception as exc:
                note_swallowed(T("worker(_tag_scope_scan_done)：回主线程通知失败"),
                               exc, level="warn")

        threading.Thread(target=worker, daemon=True).start()

    def _tag_scope_scan_done(self, key, paths, tag_map, err):
        if err is not None:
            self.log_problem(f"统计整个视图的标签失败：{err}", level="warn")
        if self._tag_scope_inflight == key:
            self._tag_scope_inflight = None
        if key != self._tag_scope_scan_key:
            return                      # 视图已经换了，结果作废
        counter = {}
        for ts in (tag_map or {}).values():
            for t in ts:
                e = counter.get(t[0])
                if e is None:
                    counter[t[0]] = [t[1], t[2], 1]
                else:
                    e[2] += 1
        stats = sorted(
            [(tid, v[0], v[1], v[2]) for tid, v in counter.items()],
            key=lambda x: (-x[3], (x[1] or "").lower()))
        self._tag_scope_cache_key = key
        self._tag_scope_cache = (tag_map, stats)
        try:
            self.file_list.set_tag_scope_stats(stats)
        except Exception as _e:
            note_swallowed(T("标签条的数量统计没刷新"), _e)
        self.set_status(
            f"标签条作用范围：整个视图（{len(paths)} 个文件 / {len(stats)} 个标签）")
        if self.file_list.tag_scope == "view" and self.file_list.filter_tag_ids:
            self._apply_tag_scope_filter()

    def _apply_tag_scope_filter(self):
        """按「整个视图」里的标签筛选文件（重建当前视图）。"""
        ids = set(self.file_list.filter_tag_ids)
        if not ids:
            self._restore_tag_filter_view()
            return
        if not self._tag_scope_cache:
            self._start_tag_scope_scan()
            return
        tag_map = self._tag_scope_cache[0]
        base_spec = self._tag_base_spec()
        base_paths = self._tag_scope_base_paths()
        match_all = bool(self.file_list.filter_match_all)
        out = []
        for p in base_paths:
            tset = {t[0] for t in (tag_map.get(p) or [])}
            if not tset:
                continue
            if (ids.issubset(tset) if match_all else bool(ids & tset)):
                out.append(p)
        if self._tag_filter_base_spec is None:
            self._tag_filter_base_spec = base_spec
        self._view_spec = {"kind": "paths", "paths": out}
        self._page = 0
        self._load_current_page()
        mode = "全部满足" if match_all else "任一满足"
        self.set_status(
            f"整库标签筛选（{mode}）：{len(out)} / {len(base_paths)} 个文件")

    def _restore_tag_filter_view(self):
        """找出被标签筛选替换掉的原始视图并还原。"""
        if self._tag_filter_base_spec is None:
            return False
        self._view_spec = self._tag_filter_base_spec
        self._tag_filter_base_spec = None
        self._page = 0
        self._load_current_page()
        return True

    def _page_prev(self):
        if self._page <= 0:
            return
        self._page -= 1
        self._load_current_page()

    def _page_next(self):
        ps = FILE_PAGE_SIZE
        total = self._page_total or 0
        n_pages = max(1, (total + ps - 1) // ps)
        if self._page >= n_pages - 1:
            return
        self._page += 1
        self._load_current_page()

    def _page_jump(self):
        try:
            n = int((self.page_jump_var.get() or "").strip())
        except Exception:
            return
        ps = FILE_PAGE_SIZE
        total = self._page_total or 0
        n_pages = max(1, (total + ps - 1) // ps)
        n = max(1, min(n_pages, n))
        self._page = n - 1
        self._load_current_page()

    # ---------- ★ 两个独立刷新键 ----------
    def _refresh_current_dir_files(self):
        """重新扫描当前路径下有哪些文件（清缓存，重新读一次磁盘/网盘）。"""
        if self.view_mode == "dir" and self.current_dir:
            self.refresh_current_dir()
        else:
            self.refresh_all()

    # ---------- ★ 重读标签（唯一会执行自动标签规则的手动入口）----------
    def _current_view_paths(self):
        """返回「当前视图」里显示的文件路径（不打分页，取全集）。

        - 打开某个文件路径（dir）→ 这个目录里的文件
        - 打开左侧某个分类库（cat）→ 这个分类里的文件
        - 全部文件（all）→ 所有已记录的文件
        - 搜索 / 筛选（paths）→ 结果里的文件
        """
        spec = self._view_spec or {}
        kind = spec.get("kind")
        try:
            if kind == "dir":
                return list(spec.get("all_paths") or [])
            if kind == "cat":
                cid = spec.get("cid")
                if cid is None:
                    return []
                return list(self.store.files_in_category(cid))
            if kind == "paths":
                return list(spec.get("paths") or [])
            if kind == "all":
                return list(self.store.all_files())
        except Exception as exc:
            self.log_problem(f"取当前视图文件失败：{exc}", level="warn")
        return []

    def _on_manual_retag_done(self, changed, total):
        """「🏷 重读标签」跑完后的界面刷新。"""
        self._last_cat_refresh_ts = 0.0      # 允许重算分类计数
        self._on_full_sync_done()
        self.set_status(f"重读标签完成：{total} 个文件里更新了 {changed} 个")

    def _refresh_current_dir_tags(self):
        """🏷 重读标签：按「自动标签规则」把当前视图的文件更新一遍。

        v22 起自动标签规则不再自动执行，只有这里（以及
        「⚙ 自动标签规则…」窗口里的扫描按钮）才会真正跑一遍。
        """
        paths = self._current_view_paths()
        if not paths:
            # 兜底：当前视图没有文件时，退回「所有已记录文件」
            try:
                paths = list(self.store.all_files())
            except Exception:
                paths = []
        if not paths:
            messagebox.showinfo("提示", T("当前没有可更新标签的文件"),
                                parent=self.root)
            return
        if not messagebox.askyesno(
                "重读标签",
                f"按「自动标签规则」重新扫描并更新标签？\n\n"
                f"本次范围：当前视图的 {len(paths)} 个文件\n"
                f"（数据量大时可能需要较长时间）"):
            return
        self.begin_activity(f"正在更新 {len(paths)} 个文件的标签…")
        self.log_output(
            f"重读标签（手动触发自动规则）：{len(paths)} 个文件")
        
        def worker():
            total = len(paths)
            changed_all = 0
            step = 300
            try:
                for i in range(0, total, step):
                    chunk = paths[i:i + step]
                    try:
                        changed_all += self.store.sync_auto_tags_for_paths(
                            chunk)
                    except Exception as exc:
                        self.log_problem(
                            f"第 {i + 1} 个起的批次失败：{exc}",
                            level="warn")
                    self.log_progress(
                        f"已处理 {min(i + step, total)} / {total}"
                        f"（累计更新 {changed_all}）")
                self.log_output(
                    f"重读标签完成：{changed_all} 个文件的标签有变化")
            except Exception as exc:
                self.log_problem(f"重读标签失败：{exc}", level="error")
            try:
                self._ui_threadsafe(self._on_manual_retag_done,
                                    changed_all, total)
            except Exception as exc:
                note_swallowed(T("worker(_on_manual_retag_done)：回主线程通知失败"),
                               exc, level="warn")
                
        threading.Thread(target=worker, daemon=True).start()

    # ---------- ★ v25 补丁2 / ★ 2026-10-03 重写：网盘挂载改名后的路径自愈 ----------
    def _apply_net_root_fixes(self, roots):
        """顺手把「指向失效网盘的索引根目录」处理好（改名 / 删掉多余的）。

        为什么要管这个：库里那些文件的路径修好了，可「索引管理」里还挂着
        一个永远连不上的旧根目录 —— 以后每次自动索引都会去摸它、白等一场。
        """
        done = []
        for r in roots:
            try:
                if r["action"] == "delete":
                    with self.store._lock:
                        with self.store.conn:
                            self.store.conn.execute(
                                "DELETE FROM index_roots WHERE id = ?", (r["id"],))
                    done.append("删掉多余的旧索引根：%s" % r["path"])
                else:
                    with self.store._lock:
                        with self.store.conn:
                            self.store.conn.execute(
                                "UPDATE index_roots SET path = ? WHERE id = ?",
                                (r["new"], r["id"]))
                    done.append("索引根改名：%s  →  %s" % (r["path"], r["new"]))
            except Exception as _e:
                note_swallowed(T("修复网盘路径：处理索引根目录失败"), _e)
        return done

    def _do_heal_net_paths(self):
        """☁ 把库里指向「失效的旧网盘挂载名」的记录改成当前挂载名。

        症状：网盘（CloudDrive 这类）改名 / 重装系统后重新挂载，
        双击网盘文件没反应或报错，只有本地文件能打开；
        重建索引也不管用（索引只补目录缓存，改不了文件表里的路径）。

        ★ 2026-10-03 重写：**先把「打算怎么改」摆给你看，你确认了再动**。
          现挂载名不再是死写在代码里的，而是程序自己
          「拿库里几个真实文件去几个候选挂载上试探」认出来的。
        """
        _ensure_net_aliases_loaded()
        self.begin_activity("正在检查网盘挂载名…（会去网盘点几个文件看看，稍等）")
        try:
            plan = self.store.plan_net_heal()
        except Exception as exc:
            self.end_activity()
            messagebox.showerror("检查失败", str(exc), parent=self.root)
            return
        self.end_activity()
        roots = list(getattr(self.store, "last_net_roots", []) or [])

        if not plan:
            messagebox.showinfo(
                "修复网盘路径",
                "库里存的文件路径，用的挂载名现在**都还连得上** —— "
                "没有需要修的东西。\n\n"
                "如果你现在双击网盘文件确实打不开，请先确认：\n"
                "  · 网盘客户端（CloudDrive2）在运行、已经登录；\n"
                "  · 这个网盘在 CloudDrive2 里处于「已挂载」状态。",
                parent=self.root)
            return

        lines = []
        todo_n = 0
        for item in plan:
            lines.append("  · 旧挂载名（现在连不上）：%s" % item["old"])
            lines.append("      库里有多少条：%d 条" % item["count"])
            if item["new"]:
                lines.append("      程序认出的现挂载名：%s" % item["new"])
                lines.append("      怎么认出来的：%s" % item["how"])
                todo_n += item["count"]
            else:
                lines.append("      程序**没认出来** → 这次不动它（宁可不动，也不能改错）")
            lines.append("")
        if roots:
            lines.append("另外，索引里还挂着一个连不上的旧目录：")
            for r in roots:
                if r["action"] == "delete":
                    lines.append("  · %s（新的已经在索引里了 → 建议删掉这一条）"
                                 % r["path"])
                else:
                    lines.append("  · %s → 改成 %s" % (r["path"], r["new"]))
            lines.append("")

        if todo_n <= 0:
            messagebox.showinfo(
                "修复网盘路径",
                "找到连不上的旧挂载名，但**没能认出现在换成哪个挂载名了**，"
                "所以这次一条都没改（改错路径会把标签弄丢，宁可不改）。\n\n"
                + "\n".join(lines) +
                "\n请先确认网盘客户端在运行、网盘已挂载，然后再点一次这个菜单。",
                parent=self.root)
            return

        if not messagebox.askyesno(
                "修复网盘路径（先看清单）",
                "打算这样改：\n\n" + "\n".join(lines) +
                "\n一共要改 %d 条文件路径。\n\n"
                "改完之后这些文件的标签就恢复正常了，也能双击打开\n"
                "（标签本身不会丢，只是路径换了写法）。\n\n"
                "现在就改吗？" % todo_n,
                parent=self.root):
            return

        self.begin_activity("正在修复网盘路径…")
        try:
            n = self.store.heal_net_paths(plan=plan)
        except Exception as exc:
            self.end_activity()
            messagebox.showerror("修复失败", str(exc), parent=self.root)
            return
        root_done = []
        if roots:
            try:
                root_done = self._apply_net_root_fixes(roots)
            except Exception as _e:
                note_swallowed(T("修复网盘路径：处理索引根目录失败"), _e)
        self.end_activity()

        rep = getattr(self.store, "last_net_report", {}) or {}
        learned = [d for d in rep.get("done", []) if d.get("how") == "自动认出"]
        self.log_output("网盘路径修复：改了 %d 条%s" %
                        (n, ("，跳过多余 %d 条" % rep.get("skipped"))
                         if rep.get("skipped") else ""))
        self._last_cat_refresh_ts = 0.0
        try:
            self.refresh_categories()
            self.refresh_tags()
        except Exception:
            pass
        try:
            if self.view_mode == "cat" and self.current_cat_id:
                self.show_category(self.current_cat_id)
            elif self.view_mode == "all":
                self.show_all_files()
            elif self.view_mode == "filter":
                self._load_current_page()
            else:
                self.load_directory(self.current_dir)
        except Exception:
            pass

        if n:
            extra = ""
            if learned:
                extra += "\n\n★ 程序顺便记下了新的挂载名对照关系：\n" + "\n".join(
                    "   %s  →  %s" % (d["old"], d["new"]) for d in learned) + \
                    "\n（以后网盘再改名，程序会自己认、不用再点这个菜单）"
            if root_done:
                extra += "\n\n索引根目录也顺手处理了：\n" + "\n".join(
                    "   " + x for x in root_done)
            if rep.get("skipped"):
                extra += ("\n\n有 %d 条没改：新路径上已经有记录了（撞车），"
                          "硬改会把标签弄丢，所以跳过了。" % rep["skipped"])
            self.set_status(f"修复网盘路径：改了 {n} 条")
            messagebox.showinfo(
                "修复完成",
                "已把 %d 条文件路径换成现在的网盘挂载名。\n\n"
                "现在双击这些网盘文件应该能正常打开了。%s" % (n, extra),
                parent=self.root)
        else:
            self.set_status(T("修复网盘路径：没有需要修的"))
            messagebox.showinfo(
                "修复网盘路径",
                "没有需要修复的记录（可能刚才那次已经改过了）。",
                parent=self.root)

    # ---------- ★ v25 补丁5：自检（启动时悄悄跑一次，也能手动点）----------
    def toggle_marquee_anywhere(self):
        """★ v25 补丁20：「拉框方式」开关。

        用户想要「随时随地都能拉方框」。两种模式各有一个取舍，
        所以做成开关让他自己选：
          · 空白处优先（默认）：在列表空白处拖 = 拉框；在文件上拖 = 拖动文件
            （拖到某个文件夹那一行上松手 = 移动进去）。
          · 随处可拉：在任何地方拖都能拉框（老手感）；这时想移动文件请用
            「右键 → 剪切 → 进目标文件夹 → 粘贴」。
        """
        cur = bool(load_ui_setting("marquee_anywhere", False))
        new = not cur
        save_ui_setting("marquee_anywhere", new)
        try:
            self.file_list.marquee_anywhere = new
        except Exception:
            pass
        if new:
            msg = ("现在：**随处可拉** —— 在任何地方按住左键拖，都能拉出方框选文件。\n"
                   "（这个模式下「拖到文件夹上松手 = 移动进去」用不了；\n"
                   "　 想移动文件请用：右键 → 剪切 → 进目标文件夹 → 粘贴）")
        else:
            msg = ("现在：**空白处优先**（默认）—— 在列表下方的空白处按住左键拖出方框；\n"
                   "在文件上按住拖 = 拖动文件（拖到某个文件夹上松手就移动进去）。\n"
                   "（文件铺满整屏、找不到空白时：按住 Alt 拖，也能拉框）")
        try:
            self.set_status(msg.replace("\n", " ").replace("**", ""))
            self.log_output(msg.replace("\n", " ").replace("**", ""))
            messagebox.showinfo("拉框方式", msg.replace("**", ""), parent=self.root)
        except Exception:
            pass

    def _do_prune_orphan_dirs(self):
        """🧹 清理索引里的「幽灵目录」（网盘里已经删掉的目录留下的空壳）。

        ★ 只删目录缓存（列表用的那份），**不动 files 表、绝不动标签**。
        """
        roots = []
        try:
            for r in self.store.all_index_roots():
                p = str(r["path"])
                try:
                    if is_remote_path(p):
                        roots.append(p)
                except Exception:
                    pass
        except Exception as exc:
            messagebox.showerror("清理幽灵目录", "读索引根失败：%s" % exc,
                                 parent=self.root)
            return
        if not roots:
            messagebox.showinfo(
                "清理幽灵目录",
                "没有网盘索引根，没什么可清的。\n\n"
                "（这个功能是给「网盘里删掉的目录还留在索引里」用的）",
                parent=self.root)
            return
        if not messagebox.askyesno(
                "清理幽灵目录",
                "要清理这些索引根里的「幽灵目录」吗？\n\n"
                + "\n".join("  · " + p for p in roots)
                + "\n\n说明：幽灵目录 = 网盘里已经删掉、但索引里还留着空壳的目录"
                  "（点开就报「目录读不到」的那种）。\n"
                  "**只清目录缓存，你的标签一个字都不会动。**",
                parent=self.root):
            return
        self.begin_activity("清理幽灵目录…")
        total_dirs = 0
        total_rows = 0
        for p in roots:
            n_dirs, n_rows = prune_orphan_dir_cache(self.store, p)
            total_dirs += n_dirs
            total_rows += n_rows
            self.log_output(f"清理幽灵目录：{p} → 清掉 {n_dirs} 个目录（{n_rows} 行）")
        self.end_activity()
        self.set_status(f"清理幽灵目录：共清掉 {total_dirs} 个目录（{total_rows} 行）")
        messagebox.showinfo(
            "清理幽灵目录",
            f"清理完成 ✓\n\n清掉 {total_dirs} 个幽灵目录，共 {total_rows} 行目录缓存。\n"
            + ("（没有发现幽灵目录，索引是干净的）\n" if total_dirs == 0 else "")
            + "\n标签、分类、文件记录都没动。",
            parent=self.root)

    def _do_expire_net_dir_cache(self):
        """☁ 让 CloudDrive2 忘掉网盘的目录缓存（下次读的就是最新的）。

        为什么需要：为了让「反复扫索引」变快，CloudDrive2 自己的目录缓存
        有效期被设成了 10 分钟（原来是 40 秒）。这期间它给你的目录列表是
        缓存里的 —— 你在网盘里刚加/删的东西可能要等一会儿才出现。
        点这个菜单就立刻把缓存清掉，下次扫描 / 浏览读的就是最新的。
        """
        client, why = cd_api_client_from_settings()
        if client is None:
            messagebox.showwarning(
                "让网盘缓存过期",
                "没连上 CloudDrive2，所以清不了。\n\n" + why
                + "\n\n（在「界面 → 📚 索引管理…」窗口里可以填令牌）",
                parent=self.root)
            return
        try:
            roots = []
            try:
                for r in self.store.all_index_roots():
                    p = str(r["path"])
                    try:
                        if is_remote_path(p):
                            roots.append(p)
                    except Exception:
                        pass
            except Exception:
                pass
            if not roots:
                messagebox.showinfo("让网盘缓存过期", T("没有网盘索引根。"),
                                    parent=self.root)
                return
            if not messagebox.askyesno(
                    "让网盘缓存过期",
                    "让 CloudDrive2 忘掉这些网盘目录的缓存吗？\n\n"
                    + "\n".join("  · " + p for p in roots)
                    + "\n\n（清掉之后，下次扫描 / 浏览读的就是网盘上最新的内容，"
                      "第一遍会慢一点，属正常）",
                    parent=self.root):
                return
            self.begin_activity("正在让网盘目录缓存过期…")
            ok = 0
            for p in roots:
                cd = None
                try:
                    cd = client.cd_path_of(p)
                except Exception:
                    cd = None
                if not cd:
                    continue
                try:
                    client.stub.ForceExpireDirCache(
                        _cd_pb.FileRequest(path=cd), timeout=60,
                        metadata=client._md())
                    ok += 1
                    self.log_output(f"已让目录缓存过期：{cd}")
                except Exception as exc:
                    self.log_problem(f"让 {cd} 缓存过期失败：{str(exc)[:120]}",
                                     level="warn")
            self.end_activity()
            self.set_status(f"网盘目录缓存已过期（{ok}/{len(roots)}）")
            messagebox.showinfo(
                "让网盘缓存过期",
                f"处理完成：{ok} / {len(roots)} 个网盘根已让缓存过期。\n\n"
                "现在去扫索引或浏览网盘，读到的就是最新的了。",
                parent=self.root)
        finally:
            try:
                client.close()
            except Exception:
                pass

    def _run_selfcheck(self, manual=False):
        """🩺 自检：查孤立标签 / 重复路径 / 坏指针 / 网盘与索引盘还在不在。

        ★ 启动时（等 3 秒、后台线程）自动跑一次，正常就写一行日志，
          有问题才进「🔔 问题」面板；手动点菜单时还会弹窗给结论。
          实测全部检查约 1 秒，且不碰界面，「问网盘」那步限时 3 秒。

        ★★ 2026-10-06：**这里原来是「点菜单就同步跑」的** ——
          也就是说**点一下菜单，界面就僵住 1~2 秒**（实测用户这个
          437MB 的库：PRAGMA 完整性检查 1.15 秒 + 重复路径 0.24 秒
          + 数目录缓存 0.15 秒 …，合计约 1.8 秒；库大或者网盘慢时更久）。
          这正好是用户说的「点着点着就卡死」的来源之一。
          现在：**不管手动还是自动，一律丢后台线程**（下面本来就
          已经是这么写的），界面上只显示「自检中…」，跑完再回话。
        """
        if getattr(self, "_selfcheck_running", False):
            if manual:
                self.set_status(T("自检正在跑，稍等一下…"))
            return
        # ★ 2026-10-03：已经在关窗了就不要再起自检线程
        if APP_CLOSING or getattr(self, "_closing", False):
            return
        self._selfcheck_running = True
        if manual:
            self.begin_activity("自检中…")
            self.log_output(T("开始自检（孤立标签 / 重复路径 / 坏指针 / 网盘与索引盘）"))

        def worker():
            try:
                res = self.store.health_check()
            except Exception as exc:
                res = {"problems": [("warn", "自检本身出错了：%s" % exc)],
                       "info": [], "seconds": 0.0}
            try:
                self._ui_threadsafe(self._on_selfcheck_done, res, manual)
            except Exception as exc:
                note_swallowed(T("worker(_on_selfcheck_done)：回主线程通知失败"),
                               exc, level="warn")

        # ★ 2026-10-03：把这条线程记下来 —— 关窗时要等它收工
        #   （它和关窗抢数据库会把进程带崩，见 TagStore.close 的说明）
        try:
            self._selfcheck_thread = threading.Thread(target=worker, daemon=True)
            self._selfcheck_thread.start()
        except Exception as _e:
            note_swallowed(T("起自检线程失败"), _e)

    def _on_selfcheck_done(self, res, manual):
        self._selfcheck_running = False
        if manual:
            self.end_activity()
        secs = res.get("seconds") or 0.0
        problems = res.get("problems") or []
        infos = res.get("info") or []
        for level, text in problems:
            self.log_problem(T("【自检】") + text, level=level)
        if manual:
            for t in infos:
                self.log_output(T("【自检】") + t)
            self.log_output("自检完成：用时 %.1f 秒，发现 %d 个要留意的地方"
                            % (secs, len(problems)))
            head = ("自检完成 ✓ 没发现问题" if not problems
                    else "自检完成：有 %d 个地方要留意" % len(problems))
            detail = "\n".join("· " + t for _lv, t in problems)
            messagebox.showinfo(
                "自检结果",
                f"{head}（用时 {secs:.1f} 秒）\n\n"
                + (detail + "\n\n" if detail else "")
                + ("详细内容看右下角「🔔 问题」面板。\n\n" if problems else "")
                + "\n".join("· " + t for t in infos),
                parent=self.root)
        else:
            if problems:
                self.log_output("启动自检：发现 %d 个要留意的地方（见上）" % len(problems))
            else:
                self.log_output(T("启动自检通过 ✓（用时 {x} 秒）", x=secs))

    # ---------- ★ 修复重复文件记录（老版本 UNC 路径大小写遗留问题）----------
    def _do_merge_duplicate_paths(self):
        """🧹 合并「同一个文件存了两条记录」的历史遗留问题。

        症状：自动规则/手工明明打了标签，中间列表的标签列却不显示；
        标签库里双击跳转，跳出来的文件也不显示标签。
        原因：老版本对网盘 UNC 路径没做小写归一，同一个文件存了两条
        记录（原始大小写 / 全小写），标签只挂在其中一条上，
        而界面查标签统一用 norm()（小写），所以只看到没标签的那条。
        """
        try:
            stat = self.store.merge_duplicate_paths(apply=False)
        except Exception as exc:
            messagebox.showerror("检查失败", str(exc), parent=self.root)
            return
        if not (stat.get("groups") or stat.get("renamed")):
            messagebox.showinfo(
                "修复重复文件记录",
                "没有发现重复的文件记录，也没有写法不规范（大小写不一致）\n"
                "的路径，不需要修复。",
                parent=self.root)
            return
        if not messagebox.askyesno(
                "修复重复文件记录",
                f"发现 {stat['groups']} 组「同一个文件存了两条记录」：\n\n"
                f"  · 要合并掉的重复记录：{stat['removed']} 条\n"
                f"  · 要并过去的标签关联：{stat['moved_tags']} 条\n"
                f"  · 要并过去的分类归属：{stat['moved_cats']} 条\n"
                f"  · 要改写成规范路径（大小写归一）：{stat['renamed']} 条\n\n"
                f"合并后，这些文件上的标签就能正常显示了。\n"
                f"建议先关掉其它正在写库的窗口，然后再点「是」。",
                parent=self.root):
            return
        self.begin_activity("正在合并重复的文件记录…")
        self.log_output(
            f"修复重复文件记录：{stat['groups']} 组 / {stat['removed']} 条")

        def worker():
            st = None
            try:
                st = self.store.merge_duplicate_paths(apply=True)
                self.log_output(
                    f"合并完成：删除重复记录 {st['removed']} 条，"
                    f"搬迁标签 {st['moved_tags']} 条，"
                    f"改写规范路径 {st['renamed']} 条")
            except Exception as exc:
                self.log_problem(f"合并重复记录失败：{exc}", level="error")
            try:
                self._ui_threadsafe(self._on_merge_duplicates_done, st)
            except Exception as exc:
                note_swallowed(T("worker(_on_merge_duplicates_done)：回主线程通知失败"),
                               exc, level="warn")

        threading.Thread(target=worker, daemon=True).start()

    def _on_merge_duplicates_done(self, stat):
        """修复重复记录跑完后的界面刷新。"""
        self.end_activity()
        if stat is None:
            messagebox.showerror("修复失败",
                                 "合并重复记录时出错，详见下方日志。",
                                 parent=self.root)
            return
        self._last_cat_refresh_ts = 0.0
        try:
            self.refresh_categories()
            self.refresh_tags()
        except Exception:
            pass
        # 当前视图重新载入一次（标签列马上变正常）
        try:
            if self.view_mode == "cat" and self.current_cat_id:
                self.show_category(self.current_cat_id)
            elif self.view_mode == "all":
                self.show_all_files()
            elif self.view_mode == "filter":
                self._load_current_page()
            else:
                self.load_directory(self.current_dir)
        except Exception:
            pass
        self.set_status(
            f"修复重复文件记录：删除 {stat['removed']} 条重复记录")
        messagebox.showinfo(
            "修复完成",
            f"已合并 {stat['groups']} 组重复的文件记录：\n\n"
            f"  · 删除重复记录：{stat['removed']} 条\n"
            f"  · 搬迁标签关联：{stat['moved_tags']} 条\n"
            f"  · 搬迁分类归属：{stat['moved_cats']} 条\n"
            f"  · 改写规范路径：{stat['renamed']} 条\n\n"
            f"同一个文件现在只剩一条记录了，标签应该都能正常显示。",
            parent=self.root)

    # ---------- ★ v25：搜索视图的进出（含子目录搜索 / 关键字搜索共用） ----------
    def _cancel_recursive_scan(self, invalidate_cache=True):
        """作废还在跑的「含子目录搜索」。

        - token +1：迟到的扫描结果回来时会被丢掉
        - invalidate_cache：连目录树缓存一起丢掉（切视图 / 重扫目录时用）
        """
        self._recursive_token = getattr(self, "_recursive_token", 0) + 1
        self._recursive_active = False
        self._recursive_roots = []
        try:
            self.file_list.search_external = False
        except Exception:
            pass
        if invalidate_cache:
            self._recursive_cache = None

    def _search_scan_roots(self):
        """含子目录搜索该扫哪些目录 —— 跟现在列表显示的视图保持一致。

        - 打开某个文件夹（dir）→ 就扫这个文件夹
        - 分类库 / 全部文件 / 搜索结果 → 扫这些文件所在的目录
          （合并去重；被别的根包住的子目录会被去掉）
        返回 (roots, 说明文字)
        """
        spec = self._view_spec or {}
        kind = spec.get("kind")
        if self.view_mode == "dir" or kind == "dir":
            d = str(self.current_dir) if self.current_dir else ""
            return ([d] if d else []), "当前文件夹"
        try:
            all_paths = self._current_view_paths()
        except Exception:
            all_paths = []
        dirs = []
        seen = set()
        for p in all_paths:
            d = os.path.dirname(p)
            if d and d not in seen:
                seen.add(d)
                dirs.append(d)
        # ★ 这些文件基本都在同一棵树下时，直接用它们的公共祖先当
        #   唯一基点（否则几十上百个目录要一个一个扫，网盘上等到哭）
        if len(dirs) > 1:
            try:
                common = os.path.commonpath(dirs)
                if path_depth(common) >= 4:
                    note = f"（{len(dirs)} 个目录合并成公共目录）"
                    dirs = [common]
                else:
                    note = ""
            except Exception:
                note = ""
        else:
            note = ""
        roots, truncated = collapse_roots(dirs, RECURSIVE_MAX_ROOTS)
        label = {"cat": "当前分类里这些文件所在目录",
                 "all": "全部文件所在目录",
                 "paths": "当前结果所在目录"}.get(kind, "当前视图的文件目录")
        if note:
            label += note
        if truncated:
            label += f"（目录太多，只扫最靠上的 {RECURSIVE_MAX_ROOTS} 个）"
        return roots, label

    def _begin_search_view(self):
        """★ v25：搜索要换视图了 —— 记下现在的视图，并清掉遗留的标签筛选。

        否则会出现两种「结果不正常」：
          1) 上一次的「整库标签筛选」把搜索结果悄悄砍一刀；
          2) 清空搜索后回不到原来的分类 / 全部文件（跑到某个文件夹去）。
        """
        if self._search_return_state is None:
            spec = self._tag_filter_base_spec or self._view_spec
            state = {
                "spec": dict(spec) if isinstance(spec, dict) else None,
                "view_mode": self.view_mode,
                "cat_id": self.current_cat_id,
                "dir": str(self.current_dir) if self.current_dir else None,
                "filter_ids": set(self.file_list.filter_tag_ids or ()),
                "filter_match_all": bool(self.file_list.filter_match_all),
                "had_filter": self._tag_filter_base_spec is not None,
            }
            if (state["spec"] or {}).get("kind") == "paths" \
                    and not state["had_filter"]:
                state["spec"] = None   # 上一次就是搜索结果，别记它
            self._search_return_state = state
        if self.file_list.filter_tag_ids:
            self.file_list.set_tag_filter(set())
        self._tag_filter_base_spec = None

    def _restore_view_after_search(self):
        """清空搜索 → 回到搜索前的视图。返回是否还原成功。"""
        st = self._search_return_state
        self._search_return_state = None
        self._cancel_recursive_scan(invalidate_cache=True)
        if not st:
            return False
        spec = st.get("spec") or {}
        kind = spec.get("kind") or st.get("view_mode")
        try:
            if kind == "cat" and st.get("cat_id") is not None:
                self.show_category(st["cat_id"])
            elif kind == "all":
                self.show_all_files()
            elif kind == "dir" and st.get("dir"):
                self.load_directory(st["dir"])
            elif kind == "paths" and spec:
                self._view_spec = spec
                self._page = 0
                self._load_current_page()
            else:
                return False
        except Exception as exc:
            self.log_problem(f"还原搜索前的视图失败：{exc}", level="warn")
            return False
        # 把搜索前选中的标签筛选放回去（整个视图范围下会自动重算）
        ids = st.get("filter_ids") or set()
        if ids:
            self.file_list.set_tag_filter(ids, st.get("filter_match_all"))
            self._invalidate_tag_scope()
        self.set_status(T("已退出搜索，回到原来的视图"))
        return True

    def _on_global_search(self, keyword):
        """在分类或全部文件视图中进行全局搜索"""
        if not keyword:
            # 清空搜索 → 先试着还原搜索前的视图
            if self._restore_view_after_search():
                return
            if self.view_mode == "dir":
                self.file_list.search_external = False
                self.file_list._apply_search_filter()
            elif self.view_mode == "cat" and self.current_cat_id:
                self.show_category(self.current_cat_id)
            elif self.view_mode == "all":
                self.show_all_files()
            return

        if self.view_mode == "dir":
            # 当前文件夹：就是本地按「文件名/标签/路径」开关过滤
            self.file_list.search_external = False
            self.file_list._apply_search_filter()
            return

        # ★ v25：换搜索视图前先把原视图记下来、并清掉遗留的标签筛选
        self._begin_search_view()
        # 查库实现的是"路径含关键字"，本地的「文件名/标签/路径」开关
        # 仍然负责把结果再收窄一点（跟平时在分类里搜索一致）
        self.file_list.search_external = False
        if self.view_mode == "cat" and self.current_cat_id:
            cats = {c["id"]: c for c in self.store.all_categories()}
            cat_name = cats.get(self.current_cat_id, {}).get("name", "")
            paths = self.store.search_files_in_category(self.current_cat_id, keyword)
            # ★ 2026-10-06：标题里带上**找到几个** —— 外面每个正经搜索
            #   都有这个数，用户才知道「该继续打字收窄，还是已经够了」。
            #   原来只有状态栏闪一下（很容易被后面的消息盖掉）。
            self.list_title.config(
                text=f"分类搜索：{keyword}　找到 {len(paths)} 个")
            self._invalidate_tag_scope()
            self._view_spec = {"kind": "paths", "paths": paths}
            self._page = 0
            self._load_current_page()
            self.set_status(f"在分类「{cat_name}」中搜索 \"{keyword}\"：找到 {len(paths)} 个文件")
        elif self.view_mode == "all":
            paths = self.store.search_all_files(keyword)
            self.list_title.config(
                text=f"全部文件搜索：{keyword}　找到 {len(paths)} 个")
            self._invalidate_tag_scope()
            self._view_spec = {"kind": "paths", "paths": paths}
            self._page = 0
            self._load_current_page()
            self.set_status(f"在所有文件中搜索 \"{keyword}\"：找到 {len(paths)} 个文件")
        else:
            # 其他视图（比如搜索结果里再搜）：退回本地过滤
            self.file_list.search_external = False
            self.file_list._apply_search_filter()

    # ---------- ★ 文件列表：含子目录搜索 ----------
    def _on_recursive_search(self, keyword):
        """FileList 的"含子目录"模式触发（按回车）。"""
        if not keyword:
            # 清除搜索 → 还原搜索前的视图
            self._cancel_recursive_scan(invalidate_cache=False)
            self._restore_view_after_search()
            return

        # ★ v25：分类 / 全部文件 / 搜索结果视图里，库里本来就存着完整
        #   路径，直接按完整路径查库就等于「含子目录」——秒回，
        #   不必去扫盘（分类里的文件散在好几个盘时，扫盘要几分钟）。
        kind = (self._view_spec or {}).get("kind")
        if self.view_mode != "dir" and kind != "dir":
            self.log_output(
                f"含子目录搜索：按完整路径查库「{keyword}」（不用扫盘）")
            self._on_global_search(keyword)
            self.list_title.config(text=f"含子目录搜索：{keyword}")
            return

        roots, label = self._search_scan_roots()
        if not roots:
            messagebox.showinfo(
                "没有可搜索的目录",
                "当前列表里没有可以递归搜索的目录。\n\n"
                "先打开一个文件夹，或者选中一个分类库再搜。",
                parent=self.root)
            return
        self._begin_search_view()
        # ★ 每次回车都算新一轮：token 换掉，旧扫描回来也不认
        self._cancel_recursive_scan(invalidate_cache=False)
        self._recursive_active = True
        token = self._recursive_token
        self._recursive_roots = list(roots)
        key = "|".join(sorted(roots))
        # ★ v25：每次回车都重新扫一遍（以前是复用旧缓存，用户刚
        #   下载/删掉的文件搜不到，结果看着「不正常」）。
        self.begin_activity("扫描当前目录树…")
        self.log_output(
            f"含子目录搜索：扫描 {len(roots)} 个目录（{label}）")
        for r in roots[:6]:
            self.log_output(f"    · {r}")

        def worker():
            rows = []
            truncated = False
            try:
                for base in roots:
                    if self._recursive_token != token:
                        break
                    for root, _dirs, files in os.walk(base):
                        if self._recursive_token != token:
                            break
                        for fn in files:
                            rows.append(os.path.join(root, fn))
                            if len(rows) >= RECURSIVE_MAX_FILES:
                                truncated = True
                                break
                        if truncated:
                            break
                    if truncated:
                        break
            except Exception as exc:
                self.log_problem(f"目录树扫描失败：{exc}", level="error")
            try:
                self._ui_threadsafe(self._on_recursive_scan_done,
                                    token, key, rows, keyword, truncated)
            except Exception as exc:
                note_swallowed(T("worker(_on_recursive_scan_done)：回主线程通知失败"),
                               exc, level="warn")

        threading.Thread(target=worker, daemon=True).start()

    def _on_recursive_scan_done(self, token, key, paths, keyword,
                                truncated=False):
        """目录树扫完了。token 对不上 → 这轮已经作废（清空了搜索 / 换了视图）。"""
        if token != self._recursive_token or not self._recursive_active:
            self.log_output(T("含子目录搜索：这轮扫描已作废，结果丢掉"))
            return
        self.end_activity()
        self._recursive_cache = {"key": key, "paths": paths,
                                 "ts": time.time()}
        self.log_output(f"含子目录搜索：扫描到 {len(paths)} 个文件")
        if truncated:
            self.log_problem(
                f"目录树太大，只看了前 {RECURSIVE_MAX_FILES} 个文件，"
                f"结果可能不全", level="warn")
        self._apply_recursive_filter(keyword)

    def _apply_recursive_filter(self, keyword):
        cache = self._recursive_cache
        if not cache:
            return
        paths = cache["paths"]
        kw = (keyword or "").strip().lower()
        if kw:
            paths = [p for p in paths
                     if kw in os.path.basename(p).lower()]
        # 切换成"筛选"视图
        self.list_title.config(text=T("搜索结果（含子目录）"))
        self.list_info.config(text=f"关键字：{keyword or '（空）'}")
        # ★ 关键字这里已经筛过了，别再让 FileList 按开关二次过滤
        self.file_list.search_external = True
        self._invalidate_tag_scope()
        self._view_spec = {"kind": "paths", "paths": list(paths)}
        self._page = 0
        self._load_current_page()
        self.set_status(
            f"含子目录搜索：{len(paths)} 个结果")

    def toggle_dir_cache(self):
        self.dir_cache_enabled = not self.dir_cache_enabled
        state = "开" if self.dir_cache_enabled else "关"
        self.set_status(f"目录缓存：{state}")
        if self.current_dir:
            self.load_directory(self.current_dir)

    def refresh_current_dir(self):
        if not self.current_dir:
            return
        try:
            self.store.clear_dir_cache(str(self.current_dir))
        except Exception as _e:
            note_swallowed(T("重扫当前目录前清缓存失败（可能扫的还是旧结果）"), _e)
        self.load_directory(self.current_dir)
        self.set_status(f"{self.current_dir}    已清缓存并重扫")

    def clear_all_dir_cache(self):
        if not messagebox.askyesno(
                "确认", "确定清除所有目录缓存吗？\n"
                       "（下次打开每个文件夹会重新扫描一次）",
                parent=self.root):
            return
        try:
            self.store.clear_dir_cache()
            self.set_status(T("已清除全部目录缓存"))
        except Exception as exc:
            messagebox.showerror("错误", str(exc), parent=self.root)

    def open_index_manager(self):
        # 非阻塞打开：可以一边看索引管理，一边操作主窗口
        IndexManagerDialog(self.root, self.store, app=self)

    def on_file_select(self):
        self._apply_stats_display()
        # ★ v25 补丁8：顺手更新右侧预览窗格（只读；窗格没显示就跳过，省事）
        try:
            pv = getattr(self, "preview", None)
            if pv is None:
                return
            if not self.preview_frame.winfo_ismapped():
                return
            sel = list(self.file_list.get_selection() or [])
            if len(sel) == 1:
                pv.show_path(sel[0])
            elif len(sel) > 1:
                pv.show_multi(len(sel))
            else:
                pv.clear()
        except Exception as _e:
            note_swallowed(T("更新预览窗格失败"), _e)

    def on_file_double(self, path, is_dir):
        if not path:
            return
        if is_dir:
            self.load_directory(path)
        else:
            self.open_path(path)

    def on_file_right_click(self, event, path):
        """右键：选中某一行 → 弹「文件菜单」；点在空白处 → 弹「空白处菜单」。

        ★★★ 2026-10-07 **修「空文件夹里右键没反应」**（用户报，待清算 #5）★★★
          ★ 原来这里开头就是 `if not path: return` ——
            而 `FileList._on_right` 在"没点到某一行"时**也直接 return** ——
            **两道门都关着** → **空文件夹里（一行都没有）右键 = 完全没反应**。
            （文件少、下面一大片空白时，在空白处右键同样没反应。）
          ★ 现在：`path` 是 `None` 时走「**空白处菜单**」——
            给的是"对整个当前目录做的事"，而不是"对某个文件做的事"：
              · 新建文件夹 / 新建文本文件
              · 在资源管理器里打开当前目录
              · 刷新 / 全选
              · 粘贴（剪贴板里有东西时才可用）
            ★ 为什么这些放在空白处菜单：这是所有文件管理器的**通用习惯**
              （Windows 资源管理器、macOS 访达都是这样），用户不用学。
        """
        if not path:
            # ★ 空白处 → 弹"对这个目录"的菜单
            try:
                self._popup_blank_menu(event)
            except Exception as _e:
                note_swallowed(T("空白处右键菜单失败"), _e, quiet=True)
            return
        self._rebuild_cat_submenu()
        try:
            self.menu.entryconfigure(
                "从当前分类移除",
                state="normal" if self.view_mode == "cat" else "disabled")
        except Exception:
            pass
        self.menu.tk_popup(event.x_root, event.y_root)

    def _popup_blank_menu(self, event):
        """★ 在"空白处"右键时弹出的菜单（对整个当前目录的操作）。

        ★★ 2026-10-07 新增（用户报「资源管理器新建的空文件夹 →
          在本程序里无法右键」，待清算 #5）。

        ★ 为什么要单独一个菜单（而不是复用 `self.menu`）：
          那个菜单里全是"对选中文件做的事"（打标签 / 重命名 / 删除…），
          空白处**没有选中文件**，那些项点了也没意义 ——
          **摆一堆点不了的东西比不弹更糟**。
        ★ 所以这里只放"对目录做的事"，而且**每一项都真的能用**。
        ★ 每次现建现用（`tk.Menu` 很轻），免得跟主菜单的状态打架。

        ★★ 2026-10-07 **又踩一个"名字不存在"**：
          我第一版写的是 `self.file_list.current_dir` ——
          **`FileList` 里根本没有这个属性**（翻遍了它的 `__init__`，
          只记了 `selected_paths` / `last_clicked_path`）。
          → `getattr(..., None)` 永远 `None` → 菜单里"新建/打开资源管理器"
            **全是灰的**（又一个"不报错、就是不给你用"）。
          ★ **正确的来源是主程序自己的 `self.current_dir`**（见 32312 行）。
        """
        cur = None
        # ★ 先问主程序自己（这是真来源），FileList 那里没有这个属性
        for attr in ("current_dir", "_current_dir"):
            try:
                v = getattr(self, attr, None)
                if v:
                    cur = str(v)
                    break
            except Exception:
                continue
        # ★★ 2026-10-07 **又踩一个"名字不存在"**：这里原来写的是
        #   `m_tk.Menu(...)` —— **本程序里没有 `m_tk` 这个别名**
        #   （用的是 `import tkinter as tk`）。
        #   → `NameError` 被外层 except 吞掉 → 菜单**建不出来**，
        #     而账本里只留一句"空白处右键菜单失败"。
        #   ★ 这类错误我这一轮踩了三次（`_clip_files` / `file_list.current_dir`
        #     / `m_tk`），共同点都是**名字不存在 + 异常被吞**。
        #   ★ 所以：**写新代码引用别的东西之后，一定要核一遍名字存不存在。**
        m = tk.Menu(self.root, tearoff=0)
        # ---- 新建 ----
        try:
            m.add_command(label=T("📁 新建文件夹…"),
                          command=lambda: self._blank_new_folder(cur))
        except Exception:
            pass
        try:
            m.add_command(label=T("📄 新建文本文件…"),
                          command=lambda: self._blank_new_file(cur))
        except Exception:
            pass
        m.add_separator()
        # ---- 目录级操作 ----
        try:
            m.add_command(label=T("🔄 刷新"),
                          command=lambda: self.refresh_all())
        except Exception:
            pass
        try:
            m.add_command(label=T("⬜ 全选"),
                          command=lambda: self._select_all_files())
        except Exception:
            pass
        m.add_separator()
        try:
            m.add_command(
                label=T("📂 在资源管理器里打开"),
                command=lambda: self._open_in_explorer(cur),
                state=("normal" if cur else "disabled"))
        except Exception:
            pass
        try:
            m.add_command(
                label="📋 粘贴到这儿（Ctrl+V）",
                command=lambda: self.paste_into_current(),
                state=("normal" if self._clipboard_has_files() else "disabled"))
        except Exception:
            pass
        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            try:
                m.grab_release()
            except Exception:
                pass

    # ---- 空白处菜单用到的几个小动作（每个都单独兜底）----

    def _clipboard_has_files(self):
        """剪贴板里有没有"能粘贴的文件"（用来决定"粘贴"这一项灰不灰）。

        ★★ 2026-10-07 注意：**本程序自己的剪贴板变量叫 `_clip`**
          （不是 `_clip_files`）—— 它是 `{"paths": [...], "cut": bool}` 这样一个字典。
          ★ 我第一版写成了 `_clip_files`，**那个名字根本不存在** →
            `getattr(..., None)` 永远返回 `None` → "粘贴"这一项**永远是灰的**。
            这是那种"不报错、就是不给你用"的静默失效。
          ★ 现在按真名 `_clip` 判断，并且**两种形状都认**
            （dict / list），免得以后改了形状又悄悄失效。
        """
        try:
            cb = getattr(self, "_clip", None)
            if not cb:
                return False
            if isinstance(cb, dict):
                return bool(cb.get("paths"))
            if isinstance(cb, (list, tuple, set)):
                return len(cb) > 0
            return False
        except Exception:
            return False

    def _select_all_files(self):
        """全选当前列表里的文件。

        ★★ 2026-10-07 注意：**真名是 `select_all_rows()`** ——
          我第一版写的 `self.file_list.select_all()` **不存在**，
          虽然下面有兜底（手工设 selected_paths），
          但那是"重新实现一遍"，不如直接调现成的（它还管了别的状态）。
        """
        try:
            self.file_list.select_all_rows()
            return
        except Exception:
            pass
        try:
            paths = [r["path"] for r in self.file_list.rows]
            self.file_list.selected_paths = set(paths)
            self.file_list._redraw()
            if self.file_list.on_select:
                self.file_list.on_select()
        except Exception as _e:
            note_swallowed(T("全选失败"), _e, quiet=True)

    def _open_in_explorer(self, path=None):
        """在 Windows 资源管理器里打开某个目录。"""
        try:
            target = path or self._current_dir()
            if not target:
                return
            import subprocess
            subprocess.Popen(["explorer", str(target)])
        except Exception as _e:
            note_swallowed(T("在资源管理器里打开失败"), _e)

    def _current_dir(self):
        """★★ 问出"现在在哪个目录" —— **唯一来源**，别处不要自己猜。

        ★★ 2026-10-07 为什么专门立一个方法：
          我这一轮**连踩三次同类坑**，全是"名字不存在"：
            · `self._clip_files`（真名 `_clip`）
            · `self.file_list.current_dir`（**`FileList` 根本没这个属性**）
            · `m_tk.Menu`（真名 `tk`）
          ★ 前两个都是 `getattr(..., None)` 拿到 `None` →
            **代码静默走错分支**（菜单项全灰 / 弹"先打开一个文件夹"）。
          ★ 所以现在**只留一个地方回答这个问题**（`self.current_dir`，
            那是主程序在 `load_directory` 里真正设的），
            别处一律调这个方法 —— 以后要改也只改一处。
        """
        # ★★ 2026-10-07 注意这个元组里**不能放 `_current_dir`**！
        #   它是**本方法自己的名字** —— `getattr(self, "_current_dir")`
        #   拿到的是**方法对象**（永远为真）→ 会直接 `return str(方法)`
        #   → 拿到一串 `<bound method ...>` 而不是路径，**还会把后面
        #     真正的兜底全跳过**。★ 这是那种"看着有值、其实是垃圾"的坑。
        for attr in ("current_dir", "_cur_dir", "cur_dir"):
            try:
                v = getattr(self, attr, None)
                # ★ 多一道"像不像路径"的检查 —— 万一以后又有人往这个元组里
                #   塞了个非路径的属性，也不会被当成目录用。
                if v and isinstance(v, (str, os.PathLike)):
                    return str(v)
            except Exception:
                continue
        # ★ 实在没有，退一步问列表那边（万一以后给它加了这个属性）
        #   ★★ 注意：这里**必须写 `getattr` 挨个问**，
        #     千万不能调 `self._current_dir()`（那就是**自己调自己** → 无限递归）！
        #     （我第一版批量替换时把这一句也换掉了，实测发现 → 已改回。）
        try:
            v = getattr(self.file_list, "current_dir", None)
            if v:
                return str(v)
        except Exception:
            pass
        return None

    def _blank_new_folder(self, cur=None):
        """在当前目录新建一个文件夹（弹个小输入框问名字）。"""
        try:
            base = cur or self._current_dir()
            if not base:
                messagebox.showinfo("新建文件夹", T("先打开一个文件夹。"),
                                    parent=self.root)
                return
            name = self._ask_one_line("新建文件夹", "文件夹名字：", "新建文件夹")
            if not name:
                return
            name = str(name).strip()
            if not name:
                return
            # ★ 防呆：不许带路径分隔符（免得用户写出目录外面去）
            for ch in ("\\", "/", ":", "*", "?", '"', "<", ">", "|"):
                name = name.replace(ch, "_")
            target = os.path.join(base, name)
            if os.path.exists(target):
                messagebox.showwarning("新建文件夹",
                                       "已经有同名的了：\n%s" % name,
                                       parent=self.root)
                return
            os.makedirs(target, exist_ok=False)
            self.log_output(T("已新建文件夹：{x}", x=target))
            try:
                self.refresh_all()
            except Exception:
                pass
        except Exception as _e:
            note_swallowed(T("新建文件夹失败"), _e)
            try:
                messagebox.showerror("新建文件夹", "建不了：%s" % _e,
                                     parent=self.root)
            except Exception:
                pass

    def _blank_new_file(self, cur=None):
        """在当前目录新建一个空文本文件。"""
        try:
            base = cur or self._current_dir()
            if not base:
                messagebox.showinfo("新建文件", T("先打开一个文件夹。"),
                                    parent=self.root)
                return
            name = self._ask_one_line("新建文本文件", "文件名：", "新建文本.txt")
            if not name:
                return
            name = str(name).strip()
            if not name:
                return
            for ch in ("\\", "/", ":", "*", "?", '"', "<", ">", "|"):
                name = name.replace(ch, "_")
            if "." not in name:
                name += ".txt"
            target = os.path.join(base, name)
            if os.path.exists(target):
                messagebox.showwarning("新建文件",
                                       "已经有同名的了：\n%s" % name,
                                       parent=self.root)
                return
            with open(target, "x", encoding="utf-8"):
                pass
            self.log_output(T("已新建文件：{x}", x=target))
            try:
                self.refresh_all()
            except Exception:
                pass
        except Exception as _e:
            note_swallowed(T("新建文件失败"), _e)
            try:
                messagebox.showerror("新建文件", "建不了：%s" % _e,
                                     parent=self.root)
            except Exception:
                pass

    # ---------- ★ v25 补丁23：右键「属性」 ----------
    def show_properties(self, path=None):
        """打开「属性」窗口（大小 / 数量 / 占比 / 时间 / 权限 / 分享 / 收藏）。

        ★ 全部是只读查询：不写数据库、不改文件、不删任何东西。
        """
        if not path:
            sel = list(self.file_list.get_selection() or [])
            if not sel:
                messagebox.showinfo("属性", T("先选中一个文件或文件夹。"),
                                    parent=self.root)
                return
            path = sel[0]
        try:
            PropsDialog(self.root, self, self.store, path)
        except Exception as exc:
            messagebox.showerror("属性", "打不开属性窗口：%s" % exc,
                                 parent=self.root)

    def _rebuild_cat_submenu(self):
        self.cat_menu.delete(0, "end")
        cats = self.store.all_categories()
        if not cats:
            self.cat_menu.add_command(label=T("（暂无分类，先去左侧新建）"),
                                      state="disabled")
            return
        for c in cats:
            self.cat_menu.add_command(
                label=c["name"],
                command=lambda cid=c["id"], n=c["name"]:
                    self.add_selection_to_category(cid, n))

    def open_path(self, path):
        """打开文件 / 文件夹。

        ★ v25 补丁：库里存的 UNC 网盘路径是小写的（norm 里做了
          normcase），CloudDrive 这类网盘对大小写敏感时会报
          WinError 1203「网络路径键入不正确」。先用目录缓存把大小写
          还原成磁盘上的真名，再交给系统打开。
        """
        if not path:
            return
        # ★ v25 补丁2：库里的路径可能还指着「改名前」的网盘挂载，
        #   先换成当前挂载名，再多试一遍，免得直接弹「打开失败」。
        cands = []
        for p0 in (path, remap_net_path(path)):
            if not p0:
                continue
            try:
                real = self.store.canonical_path(p0)
            except Exception:
                real = p0
            for p in (real, p0):
                if p and p not in cands:
                    cands.append(p)
        err = None
        for p in cands:
            try:
                if sys.platform.startswith("win"):
                    os.startfile(p)  # noqa
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", p])
                else:
                    subprocess.Popen(["xdg-open", p])
                return
            except Exception as exc:
                err = exc
        hint = net_error_hint(err)
        msg = str(err)
        if hint:
            msg = f"{msg}\n\n{hint}"
        messagebox.showerror("打开失败", msg, parent=self.root)

    def open_selected(self):
        path = self.file_list.get_single_selection()
        if not path:
            return
        self.open_path(path)

    def reveal_selected(self):
        path = self.file_list.get_single_selection()
        if not path:
            return
        folder = path if os.path.isdir(path) else os.path.dirname(path)
        self.open_path(folder)

    def clear_selected_tags(self):
        paths = self.file_list.get_selection()
        if not paths:
            return
        if not messagebox.askyesno("确认", f"清除所选 {len(paths)} 个文件的全部标签？"):
            return
        for path in paths:
            self.store.clear_file_tags(path)
        self.refresh_tags()
        self.refresh_rows_tags()

    def remove_selected_tags(self):
        """★★ v26（2026-10-01）：右键「去除文件上的标签…」。

        把选中文件身上的标签全列出来，你勾哪些就去掉哪些，
        确认一次才真的动手。标签本身不会被删掉。
        """
        paths = list(self.file_list.get_selection() or [])
        if not paths:
            messagebox.showinfo("去除标签", T("先选中文件。"), parent=self.root)
            return
        try:
            dlg = RemoveFileTagsDialog(self.root, self, self.store, paths)
            self.root.wait_window(dlg)
            chosen = dlg.result
        except Exception as exc:
            messagebox.showerror("去除标签", "打不开窗口：%s" % exc,
                                 parent=self.root)
            return
        if not chosen:
            return
        total = 0
        # ★ 2026-10-06：撤销记录里要存**标签名**（id 会变、名字才是人看得懂的），
        #   所以这里先把 id 翻成名字，再去删。
        _name_of = {}
        try:
            for _tid in (chosen or []):
                _row = self.store.tag_by_id(_tid)
                if _row:
                    _name_of[_tid] = _row["name"]
        except Exception:
            _name_of = {}
        _hit = []
        for p in paths:
            try:
                _n = self.store.remove_file_tag_ids(p, chosen)
                total += _n
                if _n:
                    for _tid in (chosen or []):
                        _nm = _name_of.get(_tid)
                        if _nm:
                            _hit.append((p, _nm))
            except Exception as exc:
                note_swallowed(T("去除标签失败：{x}", x=p), exc)
        # 删完之后重新同步一下继承标签（父级还在的话该补回来）
        try:
            for p in paths:
                fid = self.store._fid(p, create=False)
                if fid is not None:
                    self.store.resync_file(fid)
        except Exception as exc:
            note_swallowed(T("去除标签后同步失败"), exc)
        self.refresh_tags()
        self.refresh_rows_tags()
        if _hit:
            self.undo_record("tag_remove", _hit)
        self.set_status("已从 %d 个文件上去掉 %d 个标签（共 %d 条）"
                        % (len(paths), len(chosen), total))

    def add_file_tags_to_box(self):
        """★★ v26（2026-10-01）：右键「把标签全部加入标签盒」。

        把选中文件身上的所有标签一次性全塞进标签盒，
        方便你接下来拖到别的文件上。（不动任何数据，只是把标签放进盒子）
        """
        paths = list(self.file_list.get_selection() or [])
        if not paths:
            messagebox.showinfo("标签盒", T("先选中文件。"), parent=self.root)
            return
        try:
            info = self.store.tags_for_paths(paths) or {}
        except Exception as exc:
            messagebox.showerror("标签盒", "读标签失败：%s" % exc,
                                 parent=self.root)
            return
        want = {}
        for p in paths:
            for rec in (info.get(p) or []):
                try:
                    want[int(rec[0])] = rec[1]
                except Exception:
                    continue
        if not want:
            messagebox.showinfo("标签盒", T("这些文件上一个标签都没有。"),
                                parent=self.root)
            return
        if not getattr(self, "tagbox", None):
            try:
                self.toggle_tagbox()
            except Exception:
                pass
        box = getattr(self, "tagbox", None)
        if box is None:
            messagebox.showinfo("标签盒", T("标签盒打不开。"), parent=self.root)
            return
        try:
            have = set(box.box_ids())
        except Exception:
            have = set()
        added = 0
        for tid, name in want.items():
            if tid in have:
                continue
            try:
                box.add_tag(tid, name)
                added += 1
            except Exception as exc:
                note_swallowed(T("把标签放进标签盒失败"), exc)
        try:
            box.deiconify()
            box.lift()
        except Exception:
            pass
        self.set_status("已把 %d 个标签放进标签盒（%d 个本来就在里面）"
                        % (added, len(want) - added))

    def refresh_tags(self):
        self.tag_thumb.reload(self.store)

    def _on_tags_dropped(self, tag_names, x_root, y_root):
        """★★ v26（2026-10-01）：一次拖**好几个**标签到文件上。

        标签盒里多选了几个标签再往文件列表拖时走这里 ——
        每一个够得着的文件，都会被打上这一批标签。
        """
        names = [n for n in (tag_names or []) if n]
        if not names:
            return
        try:
            left = self.file_list.winfo_rootx()
            top = self.file_list.winfo_rooty()
            right = left + self.file_list.winfo_width()
            bottom = top + self.file_list.winfo_height()
        except Exception:
            return
        if not (left <= x_root <= right and top <= y_root <= bottom):
            self.set_status(T("把标签拖到文件列表上才能打标签"))
            return
        paths = list(self.file_list.get_selection() or [])
        if not paths:
            return
        ok = 0
        _hit = []          # ★ 2026-10-06：记撤销
        for p in paths:
            for nm in names:
                try:
                    self.store.add_tag_to_file(p, nm)
                    ok += 1
                    _hit.append((p, nm))
                except Exception as exc:
                    note_swallowed(T("批量打标签失败"), exc)
        self.refresh_tags()
        self.refresh_rows_tags()
        if _hit:
            self.undo_record("tag_add", _hit)
        self.set_status("已给 %d 个文件打上 %d 个标签（共 %d 次）"
                        % (len(paths), len(names), ok))

    def _on_tag_dropped(self, tag_name, x_root, y_root):
        try:
            left = self.file_list.winfo_rootx()
            top = self.file_list.winfo_rooty()
            right = left + self.file_list.winfo_width()
            bottom = top + self.file_list.winfo_height()
        except Exception:
            left = top = right = bottom = 0

        inside = left <= x_root <= right and top <= y_root <= bottom
        if not inside:
            return

        selected = self.file_list.get_selection()
        target_path = self.file_list.get_path_at_y(y_root, x_root)

        if target_path and target_path not in selected:
            targets = [target_path]
        elif selected:
            targets = list(selected)
        elif target_path:
            targets = [target_path]
        else:
            return

        added_auto = set()
        _hit = []          # ★ 2026-10-06：记撤销
        for path in targets:
            info = self.store.add_tag_to_file(path, tag_name)
            _hit.append((path, tag_name))
            for a in info.get("ancestors") or []:
                added_auto.add(a)

        self.refresh_tags()
        self.refresh_rows_tags()
        if _hit:
            self.undo_record("tag_add", _hit)

        extra = ""
        if added_auto:
            extra = f"（附带上级：{'、'.join(sorted(added_auto))}）"

        if len(targets) == 1:
            self.set_status(
                f"已给「{os.path.basename(targets[0])}」添加标签「{tag_name}」{extra}")
        else:
            self.set_status(
                f"已给 {len(targets)} 个文件添加标签「{tag_name}」{extra}")

    def _on_tag_right_click(self, event, tid, name):
        m = tk.Menu(self, tearoff=0)
        m.add_command(label=f"标签：{name}", state="disabled")
        m.add_separator()
        m.add_command(label=T("查看它的文件"),
                      command=lambda: self.show_files_with_tag(tid, name))
        m.add_separator()
        m.add_command(label=T("重命名…"), command=lambda: self.rename_tag(tid))
        m.add_command(label=T("更换颜色…"), command=lambda: self.recolor_tag(tid))
        m.add_separator()
        m.add_command(label=T("在星图里打开"), command=self.open_tag_tree)
        m.tk_popup(event.x_root, event.y_root)

    def _on_tag_double_click(self, tid, name):
        self.show_files_with_tag(tid, name)

    def show_files_with_tag(self, tid, name):
        paths = self.store.find_files([name], match_all=True)
        self.view_mode = "filter"
        self.current_cat_id = None
        self._cancel_recursive_scan(invalidate_cache=True)
        self._search_return_state = None
        self._clear_stats_filter()
        self._reset_category_hidden_tags()
        self.list_title.config(text=f"标签「{name}」的文件")
        self.path_var.set(f"标签：{name}")
        self.list_info.config(text=f"按标签：{name}")
        self._invalidate_tag_scope()
        self._view_spec = {"kind": "paths", "paths": paths}
        self._page = 0
        self._load_current_page()
        self.sidebar.set_selected(None, None)
        self.set_status(f"标签「{name}」→ {self._page_total} 个文件")

    def rename_tag(self, tid):
        row = None
        for r in self.store.all_tags():
            if r[0] == tid:
                row = r
                break
        if row is None:
            return
        name = row[1]
        new_name = SimpleInputDialog(self.root, "重命名标签", initial=name).result
        if not new_name or new_name == name:
            return
        try:
            self.store.rename_tag(tid, new_name)
        except Exception as exc:
            messagebox.showerror("错误", str(exc))
            return
        self.refresh_tags()
        self.refresh_rows_tags()

    def recolor_tag(self, tid):
        color = "#3498db"
        for r in self.store.all_tags():
            if r[0] == tid:
                color = r[2]
                break
        _rgb, hexv = colorchooser.askcolor(color=color, title=T("选择标签颜色"))
        if not hexv:
            return
        self.store.set_tag_color(tid, hexv)
        self.refresh_tags()
        self.refresh_rows_tags()

    def open_tag_tree(self):
        # ★ v25 补丁42：把 app 也传进去 —— 星图要用它找到「标签盒」，
        #   才能实现「Shift + 拖标签 → 拖进标签盒」和右键「放进标签盒」。
        StarGraphEditor(self.root, self.store,
                        on_saved=self._on_star_saved, app=self)
        # 窗口关闭后整体刷新一次
        self.refresh_tags()
        self.refresh_rows_tags()
        self.refresh_categories()
        if self.view_mode == "cat" and self.current_cat_id:
            self.show_category(self.current_cat_id)

    def _on_star_saved(self):
        """星图保存时立即刷新右侧缩略图和中间列表。"""
        try:
            self.refresh_tags()
            self.refresh_rows_tags()
            self.refresh_categories()
            if self.view_mode == "cat" and self.current_cat_id:
                self.show_category(self.current_cat_id)
        except Exception:
            pass

    def resync_now(self):
        info = self.store.resync_all_file_tags()
        added = info.get("added", 0)
        removed = info.get("removed", 0)
        files_affected = info.get("files_affected", 0)
        self.refresh_tags()
        self.refresh_rows_tags()
        self.refresh_categories()
        if self.view_mode == "cat" and self.current_cat_id:
            self.show_category(self.current_cat_id)
        if added or removed:
            self.set_status(
                f"同步完成：{files_affected} 个文件被更新"
                f"（新增 {added} 条、移除 {removed} 条）")
            messagebox.showinfo(
                "同步完成",
                f"已按标签结构重新同步所有文件：\n\n"
                f"  受影响文件：{files_affected} 个\n"
                f"  新增关联：{added} 条\n"
                f"  移除关联：{removed} 条",
                parent=self.root)
        else:
            self.set_status(T("同步完成：所有文件都是最新的，无需改动"))
            messagebox.showinfo("同步完成", T("所有文件的标签链都是最新的。"),
                                parent=self.root)

    def reassign_colors(self):
        if not messagebox.askyesno(
                "重新分配颜色",
                "把所有标签的配色重新按 HSL 黄金比例分配一遍吗？\n"
                "（每个标签都会拿到一个视觉上更分散、更好看的新颜色）"):
            return
        n = self.store.reassign_all_tag_colors()
        self.refresh_tags()
        self.refresh_rows_tags()
        self.set_status(f"已为 {n} 个标签重新分配配色")

    def export_tags_structure(self):
        try:
            EXPORT_DIR.mkdir(parents=True, exist_ok=True)
            n = self.store.export_tags_structure(TAGS_FILE)
        except Exception as exc:
            messagebox.showerror("导出失败", str(exc), parent=self.root)
            return
        self.set_status(f"已导出 {n} 个标签结构到：{TAGS_FILE}")
        messagebox.showinfo(
            "导出成功",
            f"已导出 {n} 个标签的结构（支持多父级）到：\n\n{TAGS_FILE}",
            parent=self.root)

    def export_file_tags(self):
        try:
            EXPORT_DIR.mkdir(parents=True, exist_ok=True)
            n = self.store.export_file_tags(FILE_TAGS_FILE)
        except Exception as exc:
            messagebox.showerror("导出失败", str(exc), parent=self.root)
            return
        self.set_status(f"已导出 {n} 个文件的标签信息到：{FILE_TAGS_FILE}")
        messagebox.showinfo(
            "导出成功",
            f"已导出 {n} 个文件的标签信息（仅手动标签）到：\n\n{FILE_TAGS_FILE}",
            parent=self.root)

    def import_tags_structure(self):
        path = filedialog.askopenfilename(
            title=T("选择标签结构文件"),
            initialdir=str(EXPORT_DIR),
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")])
        if not path:
            return
        if not messagebox.askyesno(
                "确认导入",
                "导入标签结构会：\n"
                "  · 创建缺失的标签\n"
                "  · 更新已存在标签的颜色\n"
                "  · 根据文件里的 parents 重建图关系（支持多父级）\n"
                "  · 导入完自动同步所有文件的标签链\n\n"
                "已导入标签的原有关系会被重建。继续吗？",
                parent=self.root):
            return
        try:
            info = self.store.import_tags_structure(path, auto_resync=True)
        except Exception as exc:
            messagebox.showerror("导入失败", str(exc), parent=self.root)
            return
        self.refresh_tags()
        self.refresh_rows_tags()
        self.refresh_categories()
        if self.view_mode == "cat" and self.current_cat_id:
            self.show_category(self.current_cat_id)

        resync = info.get("resync") or {}
        added = resync.get("added", 0)
        removed = resync.get("removed", 0)
        files_affected = resync.get("files_affected", 0)
        self.set_status(
            f"标签结构已导入：新建 {info['created']}、更新 {info['updated']}、"
            f"关联 {info['linked']}；同步影响 {files_affected} 个文件")
        messagebox.showinfo(
            "导入成功",
            f"标签结构已导入：\n\n"
            f"  文件中共有标签：{info['total_in_file']} 个\n"
            f"  新建标签：{info['created']} 个\n"
            f"  更新颜色：{info['updated']} 个\n"
            f"  建立父子关系：{info['linked']} 条\n\n"
            f"已自动同步所有文件的标签链：\n"
            f"  受影响文件：{files_affected} 个\n"
            f"  新增关联：{added} 条\n"
            f"  移除关联：{removed} 条",
            parent=self.root)

    def import_file_tags(self):
        path = filedialog.askopenfilename(
            title=T("选择文件标签信息文件"),
            initialdir=str(EXPORT_DIR),
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")])
        if not path:
            return
        skip = messagebox.askyesno(
            "是否跳过不存在的文件？",
            "如果原路径的文件已经不存在，是否跳过？\n\n"
            "  · 是 → 只导入磁盘上仍存在的文件（推荐）\n"
            "  · 否 → 无论磁盘上是否存在都记录到数据库",
            parent=self.root)
        try:
            info = self.store.import_file_tags(path, skip_missing=skip)
        except Exception as exc:
            messagebox.showerror("导入失败", str(exc), parent=self.root)
            return
        self.refresh_tags()
        self.refresh_rows_tags()
        self.refresh_categories()
        if self.view_mode == "cat" and self.current_cat_id:
            self.show_category(self.current_cat_id)

        self.set_status(
            f"文件标签信息已导入：{info['files']} 个文件、新增 {info['added_tags']} 条关联"
            f"（跳过 {info['skipped']}）")
        messagebox.showinfo(
            "导入成功",
            f"文件标签信息已导入：\n\n"
            f"  文件中共有文件：{info['total_in_file']} 个\n"
            f"  实际导入文件：{info['files']} 个\n"
            f"  新增标签关联：{info['added_tags']} 条\n"
            f"  跳过（不存在或无标签）：{info['skipped']} 个\n\n"
            f"注意：导入只做添加，不会删除文件上已有的标签。",
            parent=self.root)

    def open_export_dir(self):
        try:
            EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            messagebox.showerror("创建目录失败", str(exc), parent=self.root)
            return
        self.open_path(str(EXPORT_DIR))

    def migrate_settings_now(self):
        """★ v26：**加了二次确认**。

        原来这个菜单项**点一下就直接把设置文件搬走了** ——
        虽然它只是挪文件、不删数据，但它是**改配置**的操作，
        菜单里名字又长，用户很容易手滑点到。
        （这个是「用识图扫菜单」时才发现的：菜单项点下去弹的是
          「设置已迁移」而不是「要不要迁移」。）
        """
        try:
            full = _full_settings_path()
            if not messagebox.askyesno(
                    "迁移设置文件",
                    "把「完整设置文件」搬到数据目录里去吗？\n\n"
                    f"  现在的位置：{BOOTSTRAP_SETTINGS_PATH}\n"
                    f"  要搬到：    {full}\n\n"
                    "★ 这是「搬家」不是「删除」——\n"
                    "  C 盘会留一个几十字节的小文件（只记数据目录位置），\n"
                    "  你的标签、规则、数据库都不会动。\n\n"
                    "★ 搬完可能要重启程序才彻底生效。",
                    parent=self.root, default="no"):
                return
        except Exception:
            pass
        ok, msg = migrate_settings_to_data_dir()
        if ok:
            full = _full_settings_path()
            messagebox.showinfo(
                "设置已迁移",
                f"完整设置文件现在位于：\n{full}\n\n"
                f"C 盘只剩一个几十字节的引导文件：\n{BOOTSTRAP_SETTINGS_PATH}\n\n"
                "（它只记录数据目录的位置，改不了、也不用管）",
                parent=self.root)
            self.set_status(T("设置文件已迁移到数据目录"))
        else:
            messagebox.showinfo("提示", msg, parent=self.root)

    def show_data_dir(self):
        full = _full_settings_path()
        messagebox.showinfo(
            "当前数据位置",
            f"数据库：\n{DB_PATH}\n\n"
            f"导出目录：\n{EXPORT_DIR}\n\n"
            f"完整设置文件：\n{full}\n\n"
            f"引导文件（只存 data_dir，几十字节）：\n"
            f"{BOOTSTRAP_SETTINGS_PATH}",
            parent=self.root)

    def change_data_dir(self, *a, **k):
        # ★★ 转发到 `AIxiede拆分开/程序分块/面板_缓存设置.py`
        #   ★ 保留同名方法 = **所有调用方不用改**（稳定接口）
        return _面板缓存设置.change_data_dir(self, *a, **k)

            
    def apply_filter(self):
        selected_ids = self.tag_thumb.selected_ids
        if not selected_ids:
            messagebox.showinfo("提示",
                                "请先在右侧标签星图缩略图里单击选择标签（Ctrl 可多选）")
            return
        name_map = {r[0]: r[1] for r in self.store.all_tags()}
        names = [name_map[tid] for tid in selected_ids if tid in name_map]
        if not names:
            return
        paths = self.store.find_files(names, match_all=self.match_all_var.get())
        self.view_mode = "filter"
        self.current_cat_id = None
        self._cancel_recursive_scan(invalidate_cache=True)
        self._search_return_state = None
        self._clear_stats_filter()
        self._reset_category_hidden_tags()
        self.list_title.config(text=T("筛选结果"))
        self.path_var.set("筛选结果")
        self.list_info.config(text=T("筛选：") + " + ".join(names))
        self._invalidate_tag_scope()
        self._view_spec = {"kind": "paths", "paths": paths}
        self._page = 0
        self._load_current_page()
        self.set_status(
            f"筛选：{' + '.join(names)}    →  {self._page_total} 个结果")

    def clear_filter(self):
        self.load_directory(self.current_dir)
        self.sidebar.set_selected("all", None)
        self.tag_thumb.selected_ids.clear()
        self.tag_thumb._redraw()

    def scan_current_view_tags(self):
        """对当前文件列表里显示的文件跑一遍自动标签规则。
           在后台线程执行，主界面不卡。"""
        paths = [r["path"] for r in self.file_list.rows]
        if not paths:
            messagebox.showinfo("提示", T("当前列表里没有文件"), parent=self.root)
            return
        self.log_output(f"手动扫描当前列表 {len(paths)} 个文件的标签")
        self.begin_activity(f"为当前 {len(paths)} 个文件打标签")

        def worker():
            total = len(paths)
            changed_all = 0
            batch = 50
            try:
                for i in range(0, total, batch):
                    chunk = paths[i:i + batch]
                    try:
                        changed_all += self.store.sync_auto_tags_for_paths(chunk)
                    except Exception as e:
                        self.log_problem(f"批次 {i} 失败：{e}", level="warn")
                    self.log_progress(
                        f"已处理 {min(i + batch, total)} / {total}"
                        f"（累计更新 {changed_all}）")
                self.log_output(
                    f"当前列表扫描完成：{changed_all} 个文件被更新")
            except Exception as exc:
                self.log_problem(f"扫描失败：{exc}", level="error")
            try:
                self._ui_threadsafe(self._on_current_view_scan_done)
            except Exception as exc:
                note_swallowed(T("worker(_on_current_view_scan_done)：回主线程通知失败"),
                               exc, level="warn")

        threading.Thread(target=worker, daemon=True).start()

    def _on_current_view_scan_done(self):
        self.end_activity()
        try:
            self.refresh_tags()
            self.refresh_rows_tags()
            self.refresh_categories()
            self.set_status(T("当前列表已重新打标签"))
        except Exception as exc:
            # ★★ 2026-10-03：原来这里只 print，错误完全不会显示给用户，
            #   连日志面板都不进。改成走 log_problem，至少能在「🔔 问题」面板看见。
            self.log_problem(f"扫描完成回调失败：{exc}", level="error")

    def open_auto_rules(self):
        # 只打开对话框；要不要同步由用户自己按里面的按钮决定
        AutoTagRulesDialog(self.root, self.store, app=self)


    def _do_apply_name_rules(self):
        """手动把文件名规则应用到所有已记录的文件。"""
        n = len(self.store.get_auto_name_rule_tag_ids())
        if n == 0:
            self.set_status(T("文件名自动标签规则：未勾选任何标签"))
            return
        self.begin_activity(f"应用文件名规则（{n} 个标签）…")
        self.log_output(
            f"文件名自动标签规则：勾选了 {n} 个标签，开始全量应用")

        def worker():
            try:
                total = self.store.resync_all_file_tags_with_name()
                self.log_output(f"文件名规则应用完成：{total} 个文件被更新")
            except Exception as exc:
                self.log_problem(f"文件名规则应用失败：{exc}", level="error")
            try:
                self._ui_threadsafe(self._on_full_sync_done)
            except Exception as exc:
                note_swallowed(T("worker(_on_full_sync_done)：回主线程通知失败"),
                               exc, level="warn")

        threading.Thread(target=worker, daemon=True).start()

    def _on_full_sync_done(self):
        self.end_activity()
        self.refresh_tags()
        self.refresh_rows_tags()
        self.refresh_categories()
        # ★ v24：标签可能变了 → 整库标签统计作废重算
        self._invalidate_tag_scope()
        if self.view_mode == "cat" and self.current_cat_id:
            self.show_category(self.current_cat_id)

    def clear_hidden_tags(self):
        try:
            self.file_list.clear_hidden_tags()
            self.set_status(T("已恢复全部被屏蔽的标签"))
        except Exception as exc:
            print(exc)

    def clear_tag_filter(self):
        try:
            self.file_list._clear_tag_filter()
            self.set_status(T("已清除标签筛选"))
        except Exception as exc:
            print(exc)

    # ==================================================================
    #  ★ v25：闲时任务（鼠标 / 键盘空闲够久 → 悄悄跑一遍）
    # ==================================================================
    def _setup_idle_jobs(self):
        """挂上「用户有没有在动」的探针 + 定时检查（每 30 秒看一眼）。"""
        self._last_input_ts = time.monotonic()
        self._idle_jobs_running = set()
        for seq in ("<Any-KeyPress>", "<Any-ButtonPress>", "<Motion>",
                    "<MouseWheel>", "<Button-4>", "<Button-5>"):
            try:
                self.root.bind_all(seq, self._note_input, add="+")
            except Exception:
                pass
        self._idle_tick_job = None
        try:
            cfg = load_idle_settings()
            if cfg["rules_enabled"] or cfg["index_enabled"]:
                self.log_output(
                    "☁ 闲时任务已开启：鼠标 / 键盘空闲够久会自动跑一次"
                    "（在「自动标签规则」/「索引管理」窗口里可以关掉）")
        except Exception:
            pass
        self._idle_tick()

    def _note_input(self, event=None):
        """任何鼠标 / 键盘动作都算「人在」。（很轻，只记一个时间戳）"""
        try:
            self._last_input_ts = time.monotonic()
        except Exception:
            pass

    def _idle_seconds(self):
        try:
            return time.monotonic() - self._last_input_ts
        except Exception:
            return 0.0

    def _idle_tick(self):
        try:
            self._check_idle_jobs()
        except Exception:
            pass
        try:
            self._idle_tick_job = self.root.after(30000, self._idle_tick)
        except Exception:
            self._idle_tick_job = None

    def _refresh_idle_state(self):
        """对话框里改了「闲时自动跑」设置后调用（写日志 + 下次 tick 生效）。"""
        try:
            cfg = load_idle_settings()
            self.log_output(
                f"☁ 闲时任务设置：自动标签规则 "
                f"{'开' if cfg['rules_enabled'] else '关'}"
                f"（空闲 {cfg['rules_minutes']} 分钟） / 索引扫描 "
                f"{'开' if cfg['index_enabled'] else '关'}"
                f"（空闲 {cfg['index_minutes']} 分钟）")
        except Exception:
            pass

    def _any_scan_dialog_open(self):
        try:
            for w in self.root.winfo_children():
                if isinstance(w, ScanProgressDialog):
                    return True
        except Exception:
            pass
        return False

    def _check_idle_jobs(self):
        """到点了就悄悄跑一次（不弹窗、限速、你一回来就停）。"""
        cfg = load_idle_settings()
        idle = self._idle_seconds()
        if idle < 60:
            return
        busy = (int(getattr(self, "_activity_count", 0)) > 0
                or INDEX_SCAN_EVENT.is_set()
                or self._any_scan_dialog_open()
                or bool(self._idle_jobs_running))
        if busy:
            return
        now = time.time()
        if (cfg["rules_enabled"]
                and idle >= cfg["rules_minutes"] * 60
                and now - cfg["rules_last"] >= IDLE_RULES_GAP_SEC
                and self._idle_rules_todo()):
            self._start_idle_rules_job()
            return
        if (cfg["index_enabled"]
                and idle >= cfg["index_minutes"] * 60
                and now - cfg["index_last"] >= IDLE_INDEX_GAP_SEC):
            self._start_idle_index_job()

    def _auto_rule_scopes(self):
        """闲时跑自动标签规则要用的范围（启用 + 填了作用范围的规则）。"""
        scopes = []
        try:
            rules = self.store.all_auto_rules()
        except Exception:
            rules = []
        for r in rules:
            if not r.get("enabled"):
                continue
            sp = (r.get("scope_path") or "").strip()
            if not sp:
                continue
            for line in sp.split("\n"):
                s = line.strip()
                if s and s not in scopes:
                    scopes.append(s)
        return scopes

    def _idle_rules_todo(self):
        """闲时跑自动标签规则有没有活可干（有可用范围，或勾了文件名规则）。"""
        try:
            if self.store.get_auto_name_rule_tag_ids():
                return True
        except Exception:
            pass
        return bool(self._idle_rule_scopes_safe())

    def _idle_rule_scopes_safe(self, log=False):
        """★ v25：闲时跑用的范围 —— 把「和本地索引/记录对不上」的范围剔除。

        手动扫描前会弹窗确认（范围写错会把旧标签清掉），
        闲时是悄悄跑的，不能弹窗，所以这里直接跳过对不上的范围。
        """
        scopes = []
        skipped = []
        for s in self._auto_rule_scopes():
            try:
                n = self.store.scope_known_file_count(s)
            except Exception:
                n = 0
            if n:
                scopes.append(s)
            else:
                skipped.append(s)
        if skipped and log:
            try:
                self.log_output(
                    "☁ 闲时任务：跳过 " + str(len(skipped)) +
                    " 个「已知文件 0 个」的作用范围（和索引写法对不上，"
                    "建议到「自动标签规则」里点「✔ 检查」看一眼）：" +
                    " ; ".join(skipped[:3]))
            except Exception:
                pass
        return scopes

    # ---------- 闲时：自动标签规则 ----------
    def _start_idle_rules_job(self):
        self._idle_jobs_running.add("rules")
        try:
            self.log_output(T("☁ 闲时任务：开始按自动标签规则慢慢跑一遍…"))
        except Exception:
            pass
        threading.Thread(target=self._idle_rules_worker,
                         daemon=True).start()

    def _idle_rules_worker(self):
        """① 应用文件名规则；② 按启用规则的「作用范围」扫描打标签。

        ★ 限速 + 每批检查「你回来了没有」：一回来立刻收工。
        """
        total = 0
        changed = 0
        stopped = False
        try:
            try:
                n_name = len(self.store.get_auto_name_rule_tag_ids())
            except Exception:
                n_name = 0
            if n_name:
                try:
                    changed += int(
                        self.store.resync_all_file_tags_with_name(
                            pause=IDLE_RULES_PAUSE,
                            cancel=(lambda: self._idle_seconds()
                                    < IDLE_STOP_WITHIN_SEC)) or 0)
                except Exception as _e:
                    note_swallowed(T("闲时任务：同步文件名的标签链失败"), _e)
            for scope in self._idle_rule_scopes_safe(log=True):
                if self._idle_seconds() < IDLE_STOP_WITHIN_SEC:
                    stopped = True
                    break
                try:
                    paths = list(self.store.files_under_scope(scope)
                                 .get("paths") or [])
                except Exception:
                    paths = []
                for i in range(0, len(paths), IDLE_RULES_CHUNK):
                    if self._idle_seconds() < IDLE_STOP_WITHIN_SEC:
                        stopped = True
                        break
                    chunk = paths[i:i + IDLE_RULES_CHUNK]
                    try:
                        with self.store.bulk():
                            changed += int(
                                self.store.sync_auto_tags_for_paths(chunk)
                                or 0)
                    except Exception as _e:
                        note_swallowed(T("闲时任务：给一批文件打自动标签失败"), _e)
                    total += len(chunk)
                    try:
                        time.sleep(IDLE_RULES_PAUSE)
                    except Exception:
                        pass
                if stopped:
                    break
        except Exception:
            pass
        try:
            self._ui_threadsafe(self._on_idle_rules_done,
                                total, changed, stopped)
        except Exception as exc:
            note_swallowed(T("worker(_on_idle_rules_done)：回主线程通知失败"),
                           exc, level="warn")

    def _on_idle_rules_done(self, total, changed, stopped):
        self._idle_jobs_running.discard("rules")
        try:
            save_idle_settings(rules_last=time.time())
        except Exception:
            pass
        msg = (f"☁ 闲时任务：自动标签规则跑完（处理 {total} 个文件，"
               f"{changed} 个文件的标签有变化"
               f"{'；你回来了，提前收工' if stopped else ''}）")
        try:
            self.log_output(msg)
            self.set_status(msg)
        except Exception:
            pass
        try:
            self.refresh_tags()
            self.refresh_rows_tags()
            self.refresh_categories()
            self._invalidate_tag_scope()
        except Exception:
            pass
        self._refresh_dialog_hints()

    # ---------- 闲时：索引扫描 ----------
    def _start_idle_index_job(self):
        if INDEX_SCAN_EVENT.is_set():
            return
        INDEX_SCAN_EVENT.set()
        self._idle_jobs_running.add("index")
        try:
            self.log_output(
                "☁ 闲时任务：开始慢慢重扫索引根目录"
                "（顺手把文件大小补全，列表里就不会再是「?」了）…")
        except Exception:
            pass
        threading.Thread(target=self._idle_index_worker,
                         daemon=True).start()

    def _idle_index_worker(self):
        roots_done = 0
        dirs = 0
        files = 0
        stopped = False
        # ★ v25 补丁17：闲时扫描也优先走 CloudDrive2 本地接口。
        #   以前这一趟是「隔着挂载盘一个个摸」，网盘要摸 20~30 分钟；
        #   走 API 之后几分钟就完了，少折腾网盘（也少撞限流）。
        api_client = None
        try:
            api_client, _why = cd_api_client_from_settings()
            try:
                self.log_output(T("☁ 闲时任务：") + _why)
            except Exception:
                pass
        except Exception:
            api_client = None
        try:
            try:
                ids = [r["id"] for r in self.store.all_index_roots()
                       if r.get("enabled")]
            except Exception:
                ids = []
            for rid in ids:
                if self._idle_seconds() < IDLE_STOP_WITHIN_SEC:
                    stopped = True
                    break
                res = scan_index_roots(
                    self.store, [rid],
                    cancel_flag=(lambda: self._idle_seconds()
                                 < IDLE_STOP_WITHIN_SEC),
                    delay=IDLE_INDEX_PAUSE,
                    api_client=api_client)
                if res:
                    _rid, _p, d, f, _err = res[0]
                    dirs += d
                    files += f
                roots_done += 1
        except Exception as _e:
            note_swallowed(T("闲时任务：索引扫描失败"), _e)
        finally:
            try:
                if api_client is not None:
                    api_client.close()
            except Exception:
                pass
            INDEX_SCAN_EVENT.clear()
        try:
            self._ui_threadsafe(self._on_idle_index_done,
                                roots_done, dirs, files, stopped)
        except Exception as exc:
            note_swallowed(T("worker(_on_idle_index_done)：回主线程通知失败"),
                           exc, level="warn")

    def _on_idle_index_done(self, roots_done, dirs, files, stopped):
        self._idle_jobs_running.discard("index")
        try:
            save_idle_settings(index_last=time.time())
        except Exception:
            pass
        msg = (f"☁ 闲时任务：索引扫描跑完（{roots_done} 个根目录 / "
               f"{dirs} 个目录 / {files} 个文件"
               f"{'；你回来了，提前收工' if stopped else ''}）")
        try:
            self.log_output(msg)
            self.set_status(msg)
        except Exception:
            pass
        # 当前目录重新读一次本地缓存（新文件 / 大小立刻可见）
        try:
            if self.view_mode == "dir" and self.current_dir:
                self.load_directory(self.current_dir)
        except Exception:
            pass
        self._refresh_dialog_hints()

    def _refresh_dialog_hints(self):
        """刷一下打开着的「自动标签规则」/「索引管理」里的闲时信息。"""
        try:
            children = list(self.root.winfo_children())
        except Exception:
            return
        for w in children:
            if not isinstance(w, (AutoTagRulesDialog, IndexManagerDialog)):
                continue
            try:
                w._refresh_idle_hint()
            except Exception:
                pass
            try:
                w._reload()
            except Exception:
                pass

    def on_close(self):
        # ★ v25 补丁14：关窗前先把「还在排队的后台扫描」掐掉 ——
        #   以前后台线程扫完会 root.after() 回主线程，如果这时窗口已经销毁，
        #   Tk 会直接崩（表现为关窗时闪退）。这里先立个牌子再收摊。
        # ★ v25 补丁18：牌子改成两块 —— 一块给自己（self._closing），
        #   一块给后台线程看（模块级 APP_CLOSING），并且稍微等一下正在
        #   跑的「目录比对」线程，免得它正好在这一刻往界面回话。
        global APP_CLOSING
        APP_CLOSING = True
        self._closing = True
        # ★★ 2026-10-03：关窗之前**把各分区宽度记下来**（用户要求
        #   「关了程序再开还是我拉好的比例」）。
        # ★★ 2026-10-05：关窗 = 最靠谱的记账时机（此刻窗口早就摆稳了，
        #   抄到的就是屏幕上真实的比例），所以在这里**显式打开闸门**。
        try:
            self._pane_layout_ready = True
            self._save_pane_sizes()
        except Exception:
            pass
        # ★★ 2026-10-07 新增：记住"这次是不是最大化的"。
        #   ★ 为什么要记：用户要求"默认最大化打开"，
        #     但如果他**自己按了还原/调小了窗口**，下次不该硬把它拉回去 ——
        #     那是"跟他对着干"。所以关窗时看一眼当前状态，存下来。
        #   · "zoomed"     = 最大化（Windows）
        #   · "normal"     = 普通窗口
        #   ★ 存的是"下次还用不用最大化"，所以 zoomed → True。
        try:
            _st = str(self.root.state() or "")
            if _st in ("zoomed", "iconic"):
                save_ui_setting("start_maximized", True)
            elif _st == "normal":
                save_ui_setting("start_maximized", False)
        except Exception:
            pass
        try:
            for _ in range(20):          # 最多等 1 秒
                if getattr(self, "_bg_scan_running_dir", None) is None:
                    break
                time.sleep(0.05)
        except Exception:
            pass
        try:
            if getattr(self, "_bg_scan_timer", None) is not None:
                self.root.after_cancel(self._bg_scan_timer)
        except Exception:
            pass
        # ★ 2026-10-03：把「记住分区大小」那个延时任务也掐掉
        try:
            if getattr(self, "_pane_save_job", None) is not None:
                self.root.after_cancel(self._pane_save_job)
                self._pane_save_job = None
        except Exception:
            pass
        # ★★ 2026-10-06：还有那个「等你停手再搜」的搜索任务 ——
        #   不掐掉的话，关窗那一刻它可能刚好到点，就去查一个
        #   正在关闭的数据库（白忙一场，还可能记一条假报错）。
        try:
            fl = getattr(self, "file_list", None)
            if fl is not None:
                fl._cancel_search_debounce()
        except Exception:
            pass
        # ★★ 2026-10-06：关窗前把「用法记录」缓冲里剩的写盘 ——
        #   不写的话，最后那几条（往往正是关窗时出的问题）就丢了。
        #   ★ 但**限时**：最多等 0.5 秒，等不到就走人
        #     （绝不能因为记账把「关不掉窗口」那个老毛病又弄回来）。
        try:
            _usage_flush_async()
            time.sleep(0.05)
        except Exception:
            pass
        # ★★ 2026-10-03：**等「启动自检」那条后台线程收工**（最多 3 秒）。
        #   实测：它正在查库时，主线程把数据库连接一关，sqlite3 会把进程
        #   带崩（访问违规 -1073741819，用 faulthandler 抓到栈才看清）。
        #   （TagStore.close() 现在也会排队等锁，这里是双保险。）
        #   ★★ 2026-10-06：3 秒 → **1 秒**。理由：这一步是**在主线程里等**，
        #     等多久界面就僵多久（用户看到的就是「点了叉关不掉」）。
        #     而且下面 TagStore.close() 已经改成「最多等 1.5 秒、等不到就走」，
        #     两处加起来最坏 2.5 秒 —— 再久用户就要骂人了。
        #     实测（故意让后台握着数据库锁不放）：修之前退不出去（僵 20 秒），
        #     修之后 1~2.5 秒就正常退出，而且**一条数据都没丢**。
        try:
            th = getattr(self, "_selfcheck_thread", None)
            if th is not None and th.is_alive():
                th.join(1.0)
        except Exception:
            pass
        try:
            self._bg_scan_pending_dir = None
        except Exception:
            pass
        # ★ v25 补丁18：先把文件列表里的缩略图「干净地放掉」，再销毁窗口。
        #   实测发现：瀑布流（大图标）模式下打开一个文件夹、过一会儿再关窗，
        #   程序会闪退（退出码 -1073741819）。原因是缩略图是 PIL 的图片对象，
        #   如果它在 Tk 已经销毁之后才被回收，PIL 会去碰已经没了的 Tk，
        #   直接把进程带崩。所以关窗前：先清空画布 → 清掉缩略图缓存 →
        #   强制回收一次 —— 这样图片都在 Tk 还活着的时候被正常释放。
        try:
            # ★ 先「退出瀑布流」并把列表清空：瀑布流那一屏会同时拿着几十张
            #   缩略图 / 图标（PIL + shell 取图），关窗时最容易在这儿出事。
            self.file_list.set_layout_mode("list")
            self.file_list.set_rows([])
        except Exception:
            pass
        try:
            self.file_list.canvas.delete("all")
        except Exception:
            pass
        try:
            self.file_list.clear_thumbnail_cache()
        except Exception:
            pass
        try:
            import gc as _gc
            _gc.collect()
        except Exception:
            pass
        # ★ v25 补丁4：关窗这一步原来没做保护 —— 万一关数据库或销毁窗口时
        #   出错，异常会被 Tk 吞掉，表现就是「点了窗口的 X 却关不掉」。
        #   现在无论如何都会 destroy，失败也会记一笔。
        global _SWALLOW_SINK
        _SWALLOW_SINK = None      # 窗口要关了，之后的提示改打印到控制台
        # ★ v25 补丁18：把「往界面排活儿」这条路整个封掉。
        #   以前各种后台线程（看门狗、分类数字、闲时任务、复制粘贴…）都有可能
        #   在这一刻调 root.after() 回主线程；窗口一销毁，Tk 就崩（关窗闪退）。
        #   现在把 after / after_cancel 换成空操作：谁再调用都石沉大海，
        #   绝对不会碰已经销毁的窗口。
        try:
            self.root.after = lambda *a, **k: None
            self.root.after_cancel = lambda *a, **k: None
        except Exception:
            pass
        try:
            self.store.close()
        except Exception as _e:
            note_swallowed(T("退出时关闭数据库失败"), _e)
        try:
            self.root.destroy()
        except Exception as _e:
            note_swallowed(T("退出时关闭窗口失败"), _e)


# ==========================================================================
def _enable_dpi_awareness():
    """★ v25 补丁40：让 Windows 不要把咱们的窗口「拉伸放大」。

    用户抱怨「整个软件 dpi 还是很低，看着哪哪都是糊的」——**根子在这**：
      你这台机器真实屏幕是 2560x1440，但 Windows 设了 150% 缩放，
      于是系统**假装**屏幕只有 1707x960。
      程序如果**不声明自己懂 DPI**（不是 DPI-aware），Windows 就会：
        1) 按 1707x960 让程序画好；
        2) 再把画好的位图**整体放大 1.5 倍**贴到 2560x1440 的屏上。
      放大出来的东西必然是糊的 —— 这就是「哪哪都糊」的真正原因，
      跟字体、跟 tk scaling 都没关系。

    修法：启动时先声明「我懂 DPI」，Windows 就不再替我们拉伸了。
    声明之后程序拿到的是**真实像素**（2560x1440），字和图都是原生清晰度。
    代价：界面元素会变小 —— 所以下面 _auto_ui_scale() 会自动把
    缩放调到一个合适的值补回来。

    三种声明方式从新到旧依次尝试（Win10 1703+ → Win8.1 → Vista+）。
    ★ 注意：调用前必须先把参数类型声明清楚（argtypes/restype）。
      不声明的话 ctypes 会按 32 位整数传，`SetProcessDpiAwarenessContext`
      收到的是个被截断的假句柄，**调用会静默失败**（返回 0 但不报错），
      界面照样糊 —— 这个坑我实测踩过一次。
    """
    try:
        import ctypes
        import ctypes.wintypes as wt
    except Exception:
        return False
    # ① Win10 1703 以后：Per-Monitor V2（最好，缩放改动能实时跟）
    try:
        fn = ctypes.windll.user32.SetProcessDpiAwarenessContext
        fn.restype = wt.BOOL
        fn.argtypes = [wt.HANDLE]
        # -4 = DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
        if fn(ctypes.c_void_p(-4)):
            return True
    except Exception:
        pass
    # ② Win8.1：按显示器各自 DPI
    try:
        fn2 = ctypes.windll.shcore.SetProcessDpiAwareness
        fn2.restype = ctypes.c_long
        fn2.argtypes = [ctypes.c_int]
        if fn2(2) == 0:          # 0 = S_OK
            return True
    except Exception:
        pass
    # ③ Vista 起就有：整个进程一个 DPI
    try:
        fn3 = ctypes.windll.user32.SetProcessDPIAware
        fn3.restype = wt.BOOL
        fn3.argtypes = []
        if fn3():
            return True
    except Exception:
        pass
    return False


# 这个必须在**创建任何窗口之前**调用一次（放在模块加载时最保险）
DPI_AWARE = _enable_dpi_awareness()


def _screen_dpi_scale():
    """★ 补丁40：问 Windows「这台机器现在的缩放是多少」。

    返回 1.0 / 1.25 / 1.5 / 1.75 / 2.0 这种倍数。
    读不到就返回 1.0（不影响使用）。
    """
    try:
        import ctypes
        # 已经声明过 DPI-aware 之后，这个值才是真实的
        try:
            dpi = int(ctypes.windll.user32.GetDpiForSystem())
        except Exception:
            hdc = ctypes.windll.user32.GetDC(0)
            dpi = int(ctypes.windll.gdi32.GetDeviceCaps(hdc, 88))
        if dpi and dpi > 0:
            s = dpi / 96.0
            # 归到最常见的几档，免得出现 1.4999 这种怪值
            for v in (1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0):
                if abs(s - v) < 0.06:
                    return v
            return round(s, 2)
    except Exception:
        pass
    return 1.0


def _auto_ui_scale():
    """★ 补丁40：按屏幕缩放自动挑一个合适的「界面缩放」。

    声明 DPI-aware 之后，界面是按真实像素画的，元素会显得小；
    这里按系统缩放补回来：150% 的屏 → 界面缩放用 1.5，看着就跟
    「别人家正常缩放的软件」一样大，而且是**原生清晰度**不糊。

    ★ v25 补丁41：**有一个必须防的坏值。**
      这个函数是补丁40 引入的，它把结果存进了设置文件；结果用户这边
      存下来的是 2.0 —— 而屏幕真实的缩放是 1.5。
      2.0 意味着「字体按 200% 画」，界面会明显偏大、行距被撑开，
      字看着就不匀。根源是：**「存过的值」不一定是对的**
      （可能是旧版本算错的、被打断写坏的）。
      所以现在加一道**范围校验**：存过的值如果明显偏离屏幕真实缩放
      （差得超过 0.3），就当它不可信、不用它，改回按屏幕算。
      用户真想自己调，程序里有「界面缩放」设置窗口，那里存的会让
      他立刻看到效果，不会出现「存了个怪值自己还不知道」的情况。

    ★★ v26 再次修正（2026-10-01，用户反馈「调整界面缩放那个功能现在
       被锁死在 150%，改了重开程序也没用」）：
       上一版（补丁41）加的那道「范围校验」**下手太重了** ——
         if real and abs(v - real) > 0.3:  pass   # 忽略用户存的值
       本意是防「旧版本算错的 2.0」，可副作用是：
       **只要手动调的值和屏幕缩放差得远一点，就会被无声无息地丢掉**，
       每次启动都退回「按屏幕算」（150% 的屏就是 1.5）。
       你把缩放调成 100% → 存进去了 → 下次启动又被改回 150%，
       看起来就是「改了没用、被锁死」。

       现在分得清「坏值」和「你故意调的」：
         · 设置文件里有 **ui_scale_user_set 标记**（= 你在设置窗口手动调过）
           → **无条件听你的**，一个字都不改；
         · 没那个标记（= 从没手动调过）才走旧逻辑：
           和屏幕真实值差得远就认为不可信，改按屏幕算；
         · 两种情况都必须落在合法范围内（免得出现 0.1 倍这种怪值）。
    """
    try:
        raw = _load_full_settings()
        if isinstance(raw, dict) and "ui_scale" in raw:
            v = float(raw.get("ui_scale") or DEFAULT_UI_SCALE)
            # ★★ v26（2026-10-01）：**你手动调过就完全听你的。**
            #   以前这里不区分「坏值」和「你故意调的」——只要和屏幕缩放
            #   差得超过 0.3 就丢掉，于是调了也白调（表现就是被锁死在 150%）。
            #   现在先看有没有「手动设过」的标记：有就直接返回，一个字不改。
            if raw.get("ui_scale_user_set"):
                if MIN_UI_SCALE <= v <= MAX_UI_SCALE:
                    return v
            try:
                real = _screen_dpi_scale()
            except Exception:
                real = None
            # 存的值和屏幕真实值差太多 → 认为是坏值，忽略它
            if real and abs(v - real) > 0.3:
                pass          # 往下走，用屏幕真实值
            elif MIN_UI_SCALE <= v <= MAX_UI_SCALE:
                return v
    except Exception:
        pass
    try:
        s = _screen_dpi_scale()
        if 0.8 <= s <= 4.0:
            return s
    except Exception:
        pass
    return DEFAULT_UI_SCALE


def _tk_scaling_for(ui_scale):
    """★ v25 补丁41：把「界面缩放倍数」换算成 Tk 要的那个 scaling 值。

    ★ 这是个**必须换算**的地方，以前直接传倍数，是错的。
      Tk 的 `tk scaling` 要的是「**一个点等于几个像素**」，
      标准 DPI（96）对应的是 96/72 ≈ 1.333。
      也就是说：
        · 屏幕 100%  → 应该传 1.333（不是 1.0）
        · 屏幕 150%  → 应该传 2.0  （不是 1.5）
        · 屏幕 200%  → 应该传 2.667（不是 2.0）
      原来直接传倍数，等于**每一档都传小了 2/3**，
      所以界面上各种细节（行距、内边距）会和字体对不上 ——
      用户说的「字体大小不均匀」有一半是这里贡献的。
      现在按正确的公式换算：scaling = ui_scale * 96 / 72。
    """
    try:
        v = float(ui_scale) * 96.0 / 72.0
        # 保险：别把界面撑到离谱
        return max(1.0, min(4.0, v))
    except Exception:
        return 96.0 / 72.0


def _i18n_check_cli():
    """★ **多语言自检**（命令行）：现在什么语言、翻了多少、还差哪些。

    ★ 用法：`python AIxiede.py --i18n-check`

    ★ 为什么要做成命令行（不是一个窗口）：
      · 翻译是**开发时**的活儿 —— 命令行**看得清、能复制**，
        而且**能把"还差哪些"直接存成文件**给翻译的人。
      ★ 做成窗口反而麻烦（还得点开、还得截图）。
    """
    print("=" * 66)
    print("  多语言自检")
    print("=" * 66)
    try:
        if _i18n is None:
            print("  ★ i18n 模块**没导进来** —— 看看 "
                  "`AIxiede拆分开\\程序分块\\i18n.py` 在不在。")
            print("     原因：%r" % (globals().get("_I18N_ERR"),))
            return
        print("  可用语言:")
        for code, label, path in _i18n.available_languages():
            mark = "  ← 当前" if code == _i18n.current_language() else ""
            print("     %-10s %-16s %s%s" % (code, label, path, mark))
        print()
        # ★ 逐句试翻（用一个"测试包"）
        samples = ["取消", "确定", "刷新", "标签盒", "选择标签颜色",
                   "不存在的句子XYZ"]
        print("  试翻几句（看机制通不通）:")
        for s in samples:
            print("     %-20s → %s" % (s, T(s)))
        print()
        # ★ 覆盖率：拿真清单算
        try:
            import io as _io
            import json as _json
            lp = os.path.join(_HERE, "测试残留", "_待翻译清单.json")
            if os.path.isfile(lp):
                terms = _json.loads(
                    _io.open(lp, encoding="utf-8").read())["terms"]
                from collections import Counter
                by = Counter(v["cat"] for v in terms.values())
                # ★★ 2026-10-08 修（实测发现）：**覆盖率要看"目标语言"的进度**，
                #   不能看"当前语言"。
                #   ★ 为什么：当前语言是中文时，`zh_CN.json` 里**故意没有**
                #     那 754 条（原文就是中文，不用存）→ 算出来**全是 0%**，
                #     看着像"啥都没翻"，其实**是算错了对象**。
                #   → 改成：**当前语言是中文就看英文表**（那是"下一步要翻的"）；
                #     否则看当前语言的表。
                cur_code = _i18n.current_language()
                look = "en_US" if cur_code.startswith("zh") else cur_code
                cur = {}
                for code, label, path in _i18n.available_languages():
                    if code == look:
                        try:
                            cur = _json.loads(
                                _io.open(path, encoding="utf-8").read())
                        except Exception:
                            cur = {}
                print("  ★ 下面是 **%s** 的翻译进度"
                      % ("英文（en_US）" if look == "en_US" else look))
                done_all = tot = 0
                print("  翻译进度（对照 %d 句清单）:" % len(terms))
                for c in [x for x, _ in by.most_common()]:
                    keys = [k for k, v in terms.items() if v["cat"] == c]
                    d = len([k for k in keys if k in cur])
                    done_all += d
                    tot += len(keys)
                    print("     %-10s %4d 句，翻了 %3d（%3.0f%%）"
                          % (c, len(keys), d, d * 100.0 / max(1, len(keys))))
                print("     " + "-" * 42)
                print("     %-10s %4d 句，翻了 %3d（%3.0f%%）"
                      % ("合计", tot, done_all,
                         done_all * 100.0 / max(1, tot)))
                print()
                print("  ★★ 没翻的会**显示中文**（框架的安全网），不会空白。")
                print("  ★ 想帮忙翻：编辑 `语言\\<语言代码>.json`，"
                      "加一行 `\"中文\": \"译文\",` 即可 —— **不用懂代码**。")
            else:
                print("  （没找到待翻译清单，跳过覆盖率统计）")
        except Exception as _e2:
            print("  （算覆盖率失败：%r）" % (_e2,))
    except Exception as _e:
        print("  ★ 自检出错：%r" % (_e,))
    print("=" * 66)


def main():
    # ★★★ 2026-10-08 **初始化多语言**（读设置里的语言 → 设翻译表）★★★
    #   ★ 放在这里的原因：**所有依赖都齐了** ——
    #     `load_ui_setting` 定义好了、`i18n` 也已经导入。
    #   ★ 失败不影响启动（界面显示中文）。
    try:
        _init_i18n()
    except Exception:
        pass
    # ★ `--i18n-check`：**看现在翻了多少、还差哪些**
    #   ★ 为什么要有这个开关：754 句是长期活儿，
    #     得有个"仪表盘"才知道进展（也方便给别人看"欢迎来翻"）。
    try:
        if "--i18n-check" in sys.argv:
            _i18n_check_cli()
            return
    except Exception:
        pass
    # ★★★ 2026-10-08 **发之前自检**（用户特别强调的隐私）★★★
    #   ★ 用法：`python AIxiede.py --check-privacy`
    #     —— 检查"程序目录有没有数据文件"+"exe 有没有夹带私人痕迹"
    #   ★ 为什么要做成命令行开关：
    #     打包脚本要**自动**跑它（人总是会忘），
    #     而且将来做成"一键发布"也用它。
    try:
        import sys as _sys
        if "--check-privacy" in _sys.argv:
            print(privacy_report())
            return
    except Exception:
        pass
    # ★ v25 补丁13：拖放要用的 tkinterdnd2 需要用它的 Tk() 启动窗口
    #   （没装这个库就退回普通 tk.Tk()，其它功能照旧）。
    root = None
    if HAS_DND:
        try:
            root = TkinterDnD.Tk()
        except Exception:
            root = None
    if root is None:
        root = tk.Tk()
    # ★★ v26（2026-10-03）：用已经建好的 Tk 根探测字体 —— 避免再单独
    #   建一个 Tk 根专门用来探测（实测可省 ~92ms 启动时间）。
    #   探测成功后，模块级 FONT / BOLD 两个全局变量会被自动覆盖成真值；
    #   探测失败时保持 fallback（"TkDefaultFont" / "normal"），不抛错。
    try:
        _pick_font_family(probe_root=root)
    except Exception:
        pass
    ui_scale = _auto_ui_scale()
    try:
        # ★ v25 补丁41：这里以前直接把「倍数」当 scaling 传，是错的 ——
        #   Tk 的 scaling 是「一个点=几个像素」，96dpi 对应 96/72≈1.333。
        #   直接传 1.5 等于按 112% 画、传 2.0 等于按 150% 画，
        #   界面细节（行距/内边距）和字体对不上 → 看着「大小不均匀」。
        #   现在统一走 _tk_scaling_for() 正确换算。
        root.tk.call("tk", "scaling", _tk_scaling_for(ui_scale))
        # ★★ v26：把菜单 / 各类控件的字体统一成同一个字号
        #   （不这么做的话，菜单是 9、右下角按钮是 14，看着就不匀称）。
        #   详见 apply_unified_fonts() 里的说明。
        try:
            apply_unified_fonts(root)
        except Exception as _e:
            note_swallowed(T("统一字体失败（界面可能大小不一）"), _e)
    except Exception:
        pass
    app = FileTaggerApp(root, ui_scale=ui_scale)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
