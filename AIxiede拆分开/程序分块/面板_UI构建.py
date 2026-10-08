# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「UI构建」这组方法。

★★★ 这批的搬法**跟前面 13 个类不一样**（★ 看这里再动手）：
   · 前面：**整个类**搬走，主程序 `import` 一下就行（类有自己的 self）
   · 这里：搬的是**主类的方法** —— 它们原来是 `def xxx(self)`，
           现在改成 `def xxx(app)`，**函数体里的 `self.` 全换成 `app.`**，
           ★ 其余**一个字没改**。

★★★ 为什么原封不动地保留方法名（★ 这是重点）：
   主类里**留着一个同名方法**，它现在只是"一行转发"：
       def xxx(self, *a, **k):
           return _mod.xxx(self, *a, **k)
   → **所有调用方（菜单、按钮、别的 self.方法）一个字都不用改**。
   ★★ 判据：**"稳定接口"** —— 外面看到的还是 `app.xxx()`。

★★ 变量命名说明（★ 别被 `app` 绕晕）：
   这里 `app` **就是原来的 `self`** —— 也就是 `FileTaggerApp` 实例。
   改名只是为了"提醒读者：这不是一个普通的类方法"。
"""

import os
import sys
import re
import time
import json
import threading
import queue
import subprocess
import shutil
import datetime

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, colorchooser

try:
    from PIL import Image, ImageTk
except Exception:
    Image = ImageTk = None


# ==========================================================================
#  ★★★ 要向主程序借的名字（★ 搬方法组的**关键**，错题本 #166）★★★
#  --------------------------------------------------------------------------
#  ★ 搬走的方法用了一堆**主程序自己造的东西**（`theme_get` / `T` / 常量…）。
#    这些**新文件里没有** → ★★ 一调那个方法就 `NameError` ——
#    而且**平时看不出来**（只有真点到那个按钮才炸）。
#  ★ 做法跟拆类一样：主程序启动时把「自己」交进来（`_set_app`）。
# ==========================================================================
_MUTABLE = ['DB_PATH']
_NEED = ['CategorySidebar', 'DB_PATH', 'Path', 'T', 'Tooltip', '_apply_theme_constants', '_heartbeat_start', '_load_custom_themes', '_usage_init', 'load_ui_setting', 'note_swallowed', 'theme_get', 'theme_has']
_APP = None


class _Borrowed:
    """★★ 借「会变的东西」的代理（★ 每次读回主程序现取）。

    ★★★ `__call__` 不能少（错题本 #160）：**函数也会被借**，
      少了它 `T("…")` 直接 TypeError，而且会被上层 except 吞掉。
    """

    def __init__(self, name, default=None):
        object.__setattr__(self, "_n", name)
        object.__setattr__(self, "_d", default)

    def _v(self):
        if _APP is not None:
            try:
                return getattr(_APP, object.__getattribute__(self, "_n"))
            except Exception:
                pass
        return object.__getattribute__(self, "_d")

    def __call__(self, *a, **k):
        return self._v()(*a, **k)

    def __getattr__(self, k):
        return getattr(self._v(), k)

    def __getitem__(self, k):
        return self._v()[k]

    def __setitem__(self, k, v):
        self._v()[k] = v

    def __iter__(self):
        return iter(self._v())

    def __len__(self):
        return len(self._v())

    def __bool__(self):
        return bool(self._v())

    def __eq__(self, o):
        return self._v() == o

    def __ne__(self, o):
        return self._v() != o

    def __hash__(self):
        return hash(self._v())

    def __str__(self):
        return str(self._v())

    def __repr__(self):
        return repr(self._v())

    def __int__(self):
        return int(self._v())

    def __float__(self):
        return float(self._v())

    def __index__(self):
        return int(self._v())

    def __contains__(self, x):
        return x in self._v()

    def __add__(self, o):
        return self._v() + o

    def __radd__(self, o):
        return o + self._v()

    def get(self, *a, **k):
        return self._v().get(*a, **k)

    def keys(self):
        return self._v().keys()

    def values(self):
        return self._v().values()

    def items(self):
        return self._v().items()


def _set_app(app):
    """主程序启动时调一下：把「自己」交进来，顺便把要借的名字填上。"""
    global _APP
    # ★★ 保护模块自己的 `__file__`（错题本 #165）
    _own = __file__
    _APP = app
    _fill()
    globals()["__file__"] = _own


def _fill():
    """从主程序身上把需要的名字取过来。"""
    if _APP is None:
        return
    g = globals()
    for _n in _NEED:
        try:
            # ★★★ 无条件装代理（错题本 #168 v3）
            g[_n] = _Borrowed(_n)
        except Exception:
            pass


# ---------- 兜底（★ 它会吃掉错误，所以要专门测"用的哪一份"）----------
def _fallback():
    g = globals()
    for _n in _NEED:
        if g.get(_n) is None:
            g[_n] = _Borrowed(_n)


_fallback()


def _ui_status_buttons(app, status_bar):
    """从 `_build_ui` 里抽出来的一节（2026-10-08）。

    ★ `_build_ui` 原来 485 行，按**控件分组**抽成小方法。

    ★ 本节：状态栏那一排按钮（撤销 + 右侧 8 个：问题/输出/网盘/顶部/预览/标签条/标签库/标签盒）
    """

    try:
        _tones = app._make_tone_styles()
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
    app._undo_btn = _mk_btn(
        status_bar, "undo", T("↶ 撤销"),
        "撤销上一步（Ctrl+Z）／没东西可撤时是灰的",
        app.undo_do, "undo")
    app._undo_btn.configure(state="disabled")
    try:
        app._undo_btn.pack(side="left", padx=(6, 10))
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
    app._problem_btn = _mk_btn(
        status_bar, "problem", T("🔔 问题 0"),
        "打开「问题」面板（里面还有 输出 / 进度 两页）",
        lambda: app._toggle_log_panel("problems"), "problem")
    app._problem_btn.pack(side="right", padx=(_GAP_OUT, 10))
    # ★ 「输出」按钮删掉了（用户要求）—— 点开"问题"面板里就有输出页。
    #   这里保留一个名字上的空位说明，防止以后有人又加回来。
    app._output_btn = None

    # C 组：网盘
    app._net_btn = _mk_btn(
        status_bar, "net", "",
        "切换网盘浏览方式：索引（快）／真实（慢但最新）",
        app.toggle_net_browse, "net")
    app._net_btn.pack(side="right", padx=(_GAP_IN, 0))
    app._update_net_btn()

    # B 组：顶部
    app._topbar_btn = _mk_btn(
        status_bar, "top", T("▲ 顶部"),
        "显示 / 隐藏顶部工具栏",
        app.toggle_top_bar, "layout")
    app._topbar_btn.pack(side="right", padx=(_GAP_IN, _GAP_OUT))
    # B 组：预览
    app._preview_btn = _mk_btn(
        status_bar, "preview", T("📄 预览 ▲"),
        "显示 / 隐藏右侧预览窗格",
        app.toggle_preview, "layout")
    app._preview_btn.pack(side="right", padx=(_GAP_IN, 0))

    # A 组：标签条
    app._tagbar_btn = _mk_btn(
        status_bar, "tagbar", T("🏷 标签条 ▲"),
        "显示 / 隐藏标签条",
        app.toggle_tagbar, "tag")
    app._tagbar_btn.pack(side="right", padx=(_GAP_IN, _GAP_OUT))
    # A 组：标签库
    app._taglib_btn = _mk_btn(
        status_bar, "taglib", T("🔖 标签库 ▲"),
        "显示 / 隐藏右侧「标签库（星图缩略图）」",
        app.toggle_taglib, "tag")
    app._taglib_btn.pack(side="right", padx=(_GAP_IN, 0))
    # A 组：标签盒
    app._tagbox_btn = _mk_btn(
        status_bar, "tagbox", T("🗃 标签盒 ▲"),
        "显示 / 隐藏底部的标签盒",
        app.toggle_tagbox, "tag")
    app._tagbox_btn.pack(side="right", padx=(_GAP_IN, 0))

    # ★ 补丁42：窗口一窄就自动把按钮收成「只有图标」
    try:
        status_bar.bind("<Configure>", app._on_status_bar_config)
    except Exception:
        pass

    # 启动卡顿检测
    # ★★ 2026-10-06：真正的「打卡」交给一个**纯计算线程**（不碰界面），
    #   这样界面一忙就不会误判成「卡住」，也就不会出现
    #   「越卡越报、越报越卡」的死循环。
    app._heartbeat = time.time()
    try:
        _heartbeat_start()
    except Exception:
        pass
    # ★ v25 补丁25：快捷键改成「可自定义」。
    #   这里不再把按键写死，而是交给 _setup_shortcuts()：
    #   它按快捷键表（用户可以自己改，存在设置里）去绑定，
    #   改完立刻生效，不用重启程序。
    app._shortcut_binds = {}     # 动作键 -> 当前绑定的按键
    app._setup_shortcuts()
    # ★★ 2026-10-06：把「撤销记录本」准备好
    #   （会把上次关程序前的记录读回来 —— 关了再开还能撤）
    try:
        app._undo_init()
    except Exception as _e:
        note_swallowed(T("初始化撤销记录失败（本次开程序撤不了上次的事）"), _e,
                       quiet=True)
    # ★★ 2026-10-06：把「快速预览」准备好（空格键用它）
    app._quick_preview_init()
    # ★★ 2026-10-06：把「用法记录」（听诊器）准备好。
    #   ★ 只能在这儿 init —— 要等 DB_PATH 定下来才知道数据目录在哪。
    #     放在这一步**前面**的话，开机那一串报错就记不上了。
    try:
        _usage_init(str(Path(DB_PATH).parent / ".file_tagger_usage.jsonl"))
    except Exception as _e:
        note_swallowed(T("初始化用法记录失败（这次不记日志）"), _e, quiet=True)
    app.root.after(200, app._heartbeat_tick)
    threading.Thread(target=app._stuck_watchdog, daemon=True).start()

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


def _ui_main_panes(app):
    """从 `_build_ui` 里抽出来的一节（2026-10-08）。

    ★ `_build_ui` 原来 485 行，按**控件分组**抽成小方法。

    ★ 本节：主分栏（PanedWindow + 四个 Frame + 挂上 文件列表/预览/标签面板）
    """
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
    app._style_sashes()
    app.paned = ttk.Panedwindow(app.root, orient="horizontal")
    app.paned.pack(fill="both", expand=True, padx=8, pady=(0, 6))
    # 鼠标在分栏条附近 → 光标变成「可以左右拖」的样子
    try:
        app.paned.bind("<Motion>", app._on_paned_motion, add="+")
        app.paned.bind("<Leave>", app._on_paned_leave, add="+")
    except Exception as _e:
        note_swallowed(T("安装分栏条鼠标提示失败"), _e)

    # ★ 四块各自加一圈淡边，一眼能看出「这里是一块」
    app.sidebar = CategorySidebar(app.paned, app)
    app.list_frame = ttk.Frame(app.paned, style="Card.TFrame")
    # ★ v25 补丁8：右侧预览窗格（方案 A：分类库|文件列表|预览|标签库）
    #   默认隐藏、宽度可拖，点状态栏「📄 预览」按钮才出现。
    app.preview_frame = ttk.Frame(app.paned, style="Card.TFrame")
    app.tag_frame = ttk.Frame(app.paned, padding=(10, 0, 0, 0),
                               style="Card.TFrame")
    try:
        # 左边那块是 tk.Frame —— 用高亮边框给它画一圈
        app.sidebar.configure(highlightthickness=1,
                               highlightbackground=theme_get("line"),
                               highlightcolor=theme_get("line"))
    except Exception:
        pass

    app.paned.add(app.sidebar, weight=0)
    app.paned.add(app.list_frame, weight=5)
    app.paned.add(app.preview_frame, weight=0)
    app.paned.add(app.tag_frame, weight=0)

    app._build_file_list(app.list_frame)
    app._build_preview_panel(app.preview_frame)
    app._build_tag_panel(app.tag_frame)


def _ui_top_toolbar_row1(app):
    """从 `_build_ui` 里抽出来的一节（2026-10-08）。

    ★ 原来 `_build_ui` 是个 485 行的巨型装配方法，
      按**控件分组**抽成小方法 —— 这样「哪块界面归哪段代码」一眼对上。

    ★ 本节：顶部工具栏第 1 行（收起侧栏 / 目录框 / 浏览 / 上一级 / 刷新 / 后退 / 前进）
    """
    app._top_bar = ttk.Frame(app.root, padding=(10, 8, 10, 0))
    app._top_bar.pack(fill="x")

    app.toggle_btn = ttk.Button(app._top_bar, text="◀", width=3,
                                 command=app.toggle_sidebar)
    app.toggle_btn.pack(side="left", padx=(0, 6))

    ttk.Label(app._top_bar, text=T("目录")).pack(side="left", padx=(0, 6))
    app.path_var = tk.StringVar()
    entry = ttk.Entry(app._top_bar, textvariable=app.path_var)
    # ★ 不再 fill="x", expand=True —— 那样它会把后面的按钮全挤出去。
    #   给一个够用的固定宽度（宽度单位是字符数），后面的按钮就都有位置。
    entry.pack(side="left", fill="x", expand=True)
    entry.bind("<Return>", lambda e: app.load_directory(
        app._clean_path_input(app.path_var.get())))

    # ★ 这几个按钮从右往左排，保证它们在窗口变窄时**最后**才被影响
    ttk.Button(app._top_bar, text=T("刷新"), command=app.refresh_all).pack(
        side="right", padx=(4, 0))
    app._nav_fwd_btn = ttk.Button(app._top_bar, text=T("前进 ▶"), width=7,
                                   command=app.go_forward)
    app._nav_fwd_btn.pack(side="right", padx=(4, 0))
    app._nav_back_btn = ttk.Button(app._top_bar, text=T("◀ 后退"), width=7,
                                    command=app.go_back)
    app._nav_back_btn.pack(side="right", padx=(6, 0))
    ttk.Button(app._top_bar, text=T("上一级"), command=app.go_up).pack(
        side="right", padx=4)
    ttk.Button(app._top_bar, text=T("浏览…"), command=app.choose_dir).pack(
        side="right", padx=(6, 0))


def _ui_top_toolbar_row2(app):
    """从 `_build_ui` 里抽出来的一节（2026-10-08）。

    ★ 原来 `_build_ui` 是个 485 行的巨型装配方法，
      按**控件分组**抽成小方法 —— 这样「哪块界面归哪段代码」一眼对上。

    ★ 本节：顶部工具栏第 2 行（位置：盘符 + 常用位置 + ⭐ 收藏）
    """
    # ---- 第 2 行：位置（盘符 / 常用位置 / ⭐）----
    app._top_bar2 = ttk.Frame(app.root, padding=(10, 2, 10, 4))
    app._top_bar2.pack(fill="x")
    ttk.Label(app._top_bar2, text=T("位置")).pack(side="left", padx=(38, 4))
    app._drive_var = tk.StringVar()
    app._drive_cbo = ttk.Combobox(app._top_bar2, textvariable=app._drive_var,
                                   width=6, state="readonly")
    app._drive_cbo.pack(side="left")
    app._drive_cbo.bind("<<ComboboxSelected>>", app._on_drive_pick)

    app._place_var = tk.StringVar()
    app._place_cbo = ttk.Combobox(app._top_bar2, textvariable=app._place_var,
                                   width=22, state="readonly")
    app._place_cbo.pack(side="left", padx=(4, 0))
    app._place_cbo.bind("<<ComboboxSelected>>", app._on_place_pick)
    ttk.Button(app._top_bar2, text=T("⭐ 收藏当前位置"), width=14,
               command=app._add_bookmark).pack(side="left", padx=(6, 0))

    # ★ 日志面板先 pack（在状态栏上方）
    app._build_log_panel()

    # ★ v25 补丁4：把「被吞掉的异常」接到日志面板上。
    #   以前 except: pass 的地方出错没人知道；现在这类提示会
    #   出现在「🔔 问题」面板 + 状态栏，方便查「点了没反应」。
    global _SWALLOW_SINK
    _SWALLOW_SINK = app.log_problem
    # ★★ 2026-10-05「先加说话」：额外装一道「出错必留痕」的保险。
    #   用户抱怨「卡死 / 显示不全 / 改着改着功能没了」，根子之一是
    #   六百多处「出错装没事」。上面这个 sink 只有**主动登记**的地方
    #   才会走；这里再补两手，让**没登记的**也能被看见：
    #     ① 后台线程里没被抓住的出错（线程崩了界面还在，最像「卡死」）
    #     ② 主循环里没被抓住的出错
    #   两手都只「记一笔」，绝不改变程序原有行为。
    try:
        app._install_error_spy()
    except Exception as _e:
        note_swallowed(T("装「出错必留痕」保险失败"), _e, quiet=True)
