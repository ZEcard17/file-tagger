# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：IndexManagerDialog。

★ 代码**原样搬运**，一个字没改，只是换了个文件放。

★★ 拆文件的规矩（所有分块文件都照这个写）★★
   ① **Python 自带的东西直接 import**（tk、ttk、os、sys…）——不绕弯。
   ② **只有主程序自己造的东西才向主程序借**（FONT、note_swallowed 这类）。
      而且**不在开头 import 主程序**——两边互相 import 会让 Python
      报错、程序打不开。借法是主程序启动时把「自己」交进来（_set_app）。
   ③ 借来的名字做成**模块级变量**，这样下面的代码**一个字都不用改**。
   ④ 借不到就用兜底值，**不能因为主程序改了个名字就整个打不开**。
   ⑤ ★★ **运行时会变的用「代理」**（_Borrowed）—— 每次读都回主程序现取。

★★ 拆出来的坑（错题本 #158~#164，★ 别重演）：
   · import 要写 `from IndexManagerDialog import …`（**不带包路径**）
   · `_set_app` 要**取别名**（`as _fk_…`）—— 模块名和类名同名
   · 借名字清单**用 symtable + dir() 定**，别用正则猜
   · 代理类**必须实现 `__call__`**（函数也会被借）
   · ★ 兜底 except 会吃掉错误 → **必须专门测"用的哪一份"**
"""
import datetime
import os
import queue
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, colorchooser

# ---------- 要向主程序借的名字 ----------
_MUTABLE = ['BOLD', 'FONT', 'HAS_CD_API', 'UI_FONT_SIZE', 'UI_FONT_SIZE_SMALL']
_NEED = ['BOLD', 'CD_API_DEFAULT_WORKERS', 'CD_API_MAX_WORKERS', 'CD_API_MIN_WORKERS', 'CloudDriveApiClient', 'DEFAULT_IDLE_MINUTES', 'FONT', 'HAS_CD_API', 'IDLE_MAX_MINUTES', 'IDLE_MIN_MINUTES', 'INDEX_SCAN_EVENT', 'T', 'UI_FONT_SIZE', 'UI_FONT_SIZE_SMALL', '_tree_row_height', 'apply_themed', 'cd_api_client_from_settings', 'cd_api_workers', 'datetime', 'dir_scope_args', 'dir_scope_clause', 'load_idle_settings', 'load_ui_setting', 'note_swallowed', 'prune_orphan_dir_cache', 'queue', 'save_idle_settings', 'save_ui_setting', 'scan_index_roots', 'theme_get', 'threading', 'time']
_APP = None


class _Borrowed:
    """★★ 借「会变的东西」的代理（★ 每次读回主程序现取）。

    ★★★ `__call__` 不能少（错题本 #160）：**函数也会被借**，
      少了它 `T("…")` 直接 TypeError，而且**会被上层 except 吞掉**。
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

    def __lt__(self, o):
        return self._v() < o

    def __le__(self, o):
        return self._v() <= o

    def __gt__(self, o):
        return self._v() > o

    def __ge__(self, o):
        return self._v() >= o

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

    def __mul__(self, o):
        return self._v() * o

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
    _APP = app
    _fill()


def _fill():
    """从主程序身上把需要的名字取过来，填进本模块的同名变量。"""
    if _APP is None:
        return
    g = globals()
    for _n in _NEED:
        try:
            _v = getattr(_APP, _n, None)
            if _v is not None:
                g[_n] = _Borrowed(_n) if _n in _MUTABLE else _v
        except Exception:
            pass


class IndexManagerDialog(tk.Toplevel):
    """类似 Everything 的索引管理：
       - 添加/移除索引根目录
       - 后台递归扫描根目录下所有子目录，把目录项写入 dir_cache
       - 一旦索引过，打开子目录就能秒开（读本地 SQLite）

    ★ v25 补丁24：「接力式」索引扫描 ——
       扫描变成一个**可以随时中断、随时接着跑**的任务：
         · 停在半路（点「■ 停止」、关窗口、或者闲时任务被鼠标打断）时，
           已经扫到的目录**全都留在库里**，不丢；
         · 下次再点扫描（或闲时自动跑），任务记录里存着「计划要扫的目录、
           已经扫到哪、还没扫哪些」，**直接从没扫完的地方接着来**；
         · 一个根目录扫完了就从待办里划掉，不用每次从头再扫一遍。
       任务记录存在设置文件里（键 index_scan_task），所以关掉程序也在。
    """

    def __init__(self, master, store, app=None):
        super().__init__(master)
        self.title("索引管理")
        # ★★★ 2026-10-08 修「切换夜间皮肤显示不对」（用户报，待清算 #8-②）★★★
        #   ★ 实测真因：**这个窗口整个类都没"跟着皮肤走"的机制** ——
        #     它里面全是 `tk.Text` / `tk.Frame`（原生控件），
        #     那些控件的颜色**只在建的时候设一次**；
        #     而窗口是 `Toplevel`，**皮肤切换时不会自己重刷**。
        #     → 表现就是用户说的「切了夜间，这个窗口还是老样子」。
        #   ★ 而且窗口自己的底色压根没设（实测 `bg=SystemButtonFace`，
        #     那是**系统默认色**，跟主题无关）。
        #   ★ 修法（三件）：
        #     ① 窗口自己设底色 + 登记进 `_theme_windows`（切皮肤时会被刷）
        #     ② 加一个 `_apply_theme()`，把里面几个原生控件都刷一遍
        #     ③ 主程序切皮肤时**主动通知这个窗口**（见 `_retheme_custom_parts`）
        try:
            self.configure(bg=theme_get("win_bg"))
        except Exception:
            pass
        # ★ 登记：主程序切皮肤时会把 `_theme_windows` 里的窗口逐个刷底色
        try:
            _reg = getattr(app, "_theme_windows", None)
            if _reg is None and app is not None:
                _reg = app._theme_windows = []
            if _reg is not None:
                _reg.append(self)
        except Exception:
            pass
        # ★★ 尺寸：**按内容算**（跟"自动标签规则"窗口同一个修法，见错题本 #116）
        #   实测：内容请求 1657 宽，而写死的 1000 → **右边被切 657 像素**
        #   （表现："(没有扫…"、几段提示文字都被截断）
        #   ★ 不再写死数字，改成"按内容算 + 夹在合理范围"。
        self.store = store
        self.app = app

        self._root_map = {}       # iid -> root_id
        self._scan_worker = None
        self._scan_cancel = False
        self._scan_current_root_id = None
        self._queue = queue.Queue()
        self._poll_job = None
        # ★ v25 补丁38（重新修一遍）：这四个扫描状态变量原来只在
        #   _start_scan() 里才第一次赋值，可是 _poll() 每 120 毫秒跑一次、
        #   有可能在 _start_scan 之前就读到它们 → AttributeError。
        #   补丁31 修过一次，后来补丁32~37 重写这段时又被冲掉了，
        #   这次在窗口一建出来就赋初值。
        self._stopped_by_user = False
        self._scan_had_left = False
        self._round_capped = False
        self._round_left = 0

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        ttk.Label(
            body,
            text=T("把常用根目录加入索引后，打开其下任意子目录都能秒开。\n"
                   "索引只记录文件名 / 是否为目录 / 文件大小（大小是目录列表"
                   "自带的，不额外请求网盘），不下载文件内容。"),
            foreground=theme_get("fg_dim"), justify="left").pack(anchor="w", pady=(0, 8))

        # 顶部按钮
        top = ttk.Frame(body)
        top.pack(fill="x", pady=(0, 6))
        ttk.Button(top, text=T("＋ 添加根目录"),
                   command=self._add_root).pack(side="left")
        ttk.Button(top, text=T("－ 移除"),
                   command=self._remove_root).pack(side="left", padx=4)
        ttk.Separator(top, orient="vertical").pack(
            side="left", fill="y", padx=6)
        # ★★★ 2026-10-08 按用户选的「**方案 A**」重做这排按钮 ★★★
        #   ★ 用户原话：「本来应该是暂停/继续、停止 的，跟视频播放器那样
        #     三角播放，点了三角播放变 II 暂停，点了暂停变三角播放」
        #
        #   ★ 原来是两个按钮，而且**概念是错的**：
        #       `■ 停止` —— 代码注释自己写着「停止 = 暂停」，
        #         也就是它干的是**暂停**的事（进度留着、任务记录留着）；
        #       `⏯ 接力继续` —— 就是"继续"。
        #     → 于是用户**分不清"我现在是暂停了、还是彻底停了"**，
        #       再点继续时"看着像重新扫"（其实真接着扫，只是看不出来）。
        #
        #   ★ 现在（**播放器那套**）：
        #       一个**主按钮**，随状态自己变：
        #         空闲    → `▶ 开始扫描`
        #         扫描中  → `⏸ 暂停`
        #         暂停后  → `▶ 继续扫描`
        #       + 一个**独立的** `⏹ 停止`（**只有"暂停后"才亮**）——
        #         它才是真的停：**清掉这次的任务记录**，下次从头扫。
        #   ★ 为什么要"独立一个停止"而不是三态循环：
        #     播放器里"暂停"和"停止"也是**两个不同的东西** ——
        #     暂停 = 我等会儿还要看；停止 = 我不看了（进度条归零）。
        #     合在一个按钮上，用户就得"按两下才知道自己在哪"。
        self._main_btn = ttk.Button(top, text=T("▶ 扫描选中"),
                                    command=self._on_main_btn)
        self._main_btn.pack(side="left", padx=4)
        ttk.Button(top, text=T("▶▶ 扫描全部"),
                   command=self._scan_all).pack(side="left", padx=4)
        self._stop_btn = ttk.Button(top, text=T("⏹ 停止"),
                                    command=self._on_stop_btn,
                                    state="disabled")
        self._stop_btn.pack(side="left", padx=4)
        # ★ 保留旧名字（`_resume_btn`）指向同一个主按钮 ——
        #   万一别处还引用它，不至于炸（"改一处别连累别处"）
        self._resume_btn = self._main_btn
        self._task_lbl = ttk.Label(top, text="", foreground=theme_get("fg_dim"))
        self._task_lbl.pack(side="left", padx=(8, 0))
        # ★ 每次状态变化都调它，把"按钮长相 + 状态文字"一次摆对
        self._refresh_scan_ui()

        # ★ v25：底部按钮改成「先 pack + 贴底」——
        #   原来放在最后 pack，窗口一小就被挤没（「刷新列表」显示不全）
        btns = ttk.Frame(body)
        btns.pack(side="bottom", fill="x", pady=(8, 0))
        ttk.Button(btns, text=T("刷新列表"),
                   command=self._reload).pack(side="left")
        ttk.Button(btns, text=T("🔄 清空选中根目录的缓存"),
                   command=self._clear_selected_cache).pack(
            side="left", padx=6)
        ttk.Button(btns, text=T("关闭"),
                   command=self._on_close).pack(side="right")

        # ★ v25：闲时自动跑（空闲够久，后台限速悄悄重扫一遍）
        idle_row = ttk.Frame(body)
        idle_row.pack(side="bottom", fill="x", pady=(6, 0))
        self._idle_cfg = load_idle_settings()
        self.idle_var = tk.BooleanVar(value=self._idle_cfg["index_enabled"])
        ttk.Checkbutton(
            idle_row,
            text=T("☁ 闲时自动跑（缓慢重扫所有启用的根目录）"),
            variable=self.idle_var,
            command=self._save_idle_cfg).pack(side="left")
        ttk.Label(idle_row, text=T("鼠标 / 键盘空闲")).pack(
            side="left", padx=(10, 2))
        self.idle_min_var = tk.StringVar(
            value=str(self._idle_cfg["index_minutes"]))
        _sp = ttk.Spinbox(idle_row, from_=IDLE_MIN_MINUTES,
                          to=IDLE_MAX_MINUTES, width=5,
                          textvariable=self.idle_min_var,
                          command=self._save_idle_cfg)
        _sp.pack(side="left")
        _sp.bind("<Return>", lambda e: self._save_idle_cfg())
        _sp.bind("<FocusOut>", lambda e: self._save_idle_cfg())
        ttk.Label(idle_row, text=T("分钟后运行")).pack(side="left", padx=(2, 0))
        self._idle_hint_lbl = ttk.Label(idle_row, text="",
                                       foreground=theme_get("fg_dim"))
        self._idle_hint_lbl.pack(side="left", padx=(10, 0))
        self._refresh_idle_hint()

        # ★ v25 补丁17：网盘索引走 CloudDrive2 本地接口（比隔着挂载盘摸快得多）
        api_row = ttk.Frame(body)
        api_row.pack(side="bottom", fill="x", pady=(6, 0))
        self.cd_api_var = tk.BooleanVar(
            value=bool(load_ui_setting("cd_api_enabled", True)))
        ttk.Checkbutton(
            api_row,
            text=T("☁ 网盘索引走 CloudDrive2 本地接口（快很多，推荐）"),
            variable=self.cd_api_var,
            command=self._save_cd_api_cfg).pack(side="left")
        ttk.Button(api_row, text=T("🔑 填 / 换令牌…"),
                   command=self._ask_cd_token).pack(side="left", padx=8)
        ttk.Label(api_row, text=T("同时请求数")).pack(side="left", padx=(6, 2))
        self.cd_workers_var = tk.StringVar(value=str(cd_api_workers()))
        _wsp = ttk.Spinbox(api_row, from_=CD_API_MIN_WORKERS,
                           to=CD_API_MAX_WORKERS, width=3,
                           textvariable=self.cd_workers_var,
                           command=self._save_cd_api_cfg)
        _wsp.pack(side="left")
        _wsp.bind("<Return>", lambda e: self._save_cd_api_cfg())
        _wsp.bind("<FocusOut>", lambda e: self._save_cd_api_cfg())
        ttk.Label(
            api_row,
            text=T("（调大更快，也更容易撞上网盘的访问限制；默认 4）"),
            foreground=theme_get("fg_dim")).pack(side="left", padx=(6, 0))
        self._cd_api_lbl = ttk.Label(api_row, text="", foreground=theme_get("fg_dim"))
        self._cd_api_lbl.pack(side="left", padx=(8, 0))
        self._refresh_cd_api_hint()

        # 中部：左右
        middle = ttk.Panedwindow(body, orient="horizontal")
        middle.pack(fill="both", expand=True)

        # 左：根目录列表
        left = ttk.LabelFrame(middle, text=T("索引根目录"), padding=4)
        cols = ("path", "files", "dirs", "last", "enabled")
        # ★★ 2026-10-07 修「字体比行高长」（用户报）：
        #   这棵树原来**没给 style** → 用系统默认行高（约 20 像素），
        #   而字体是 13/14 号（linespace 要 22~25）→ **字的上下被切掉**
        #   （截图里 F:\ E:\ D:\ \\CloudDrive\X\ 那几行只能看到半截字）。
        #   ★ 修法：跟目录树一样，注册一个带 `rowheight=_tree_row_height()`
        #     的样式（那个函数按字体算行高，**不写死**）。
        #   ★ 为什么用独立样式名（IndexTree.*）：不跟别的树互相干扰。
        try:
            _ist = ttk.Style()
            _ist.configure("IndexTree.Treeview",
                           background=theme_get("card_bg"),
                           foreground=theme_get("fg"),
                           fieldbackground=theme_get("card_bg"),
                           rowheight=_tree_row_height(),
                           font=(FONT, UI_FONT_SIZE_SMALL))
            _ist.configure("IndexTree.Treeview.Heading",
                           font=(FONT, UI_FONT_SIZE_SMALL, BOLD))
            self.tree = ttk.Treeview(left, columns=cols,
                                     show="headings", height=16,
                                     style="IndexTree.Treeview")
        except Exception:
            self.tree = ttk.Treeview(left, columns=cols,
                                     show="headings", height=16)
            # ★★ 2026-10-07 补：这棵树没给 style → 系统默认行高(约20)装不下字
            #   → 字被上下切掉（用户报「字体比行高长」）。按字体算行高。
            try:
                _st_IndexTree = ttk.Style()
                _st_IndexTree.configure("IndexTree.Treeview",
                    background=theme_get("card_bg"),
                    foreground=theme_get("fg"),
                    fieldbackground=theme_get("card_bg"),
                    rowheight=_tree_row_height(),
                    font=(FONT, UI_FONT_SIZE_SMALL))
                _st_IndexTree.configure("IndexTree.Treeview.Heading",
                    font=(FONT, UI_FONT_SIZE_SMALL, BOLD))
                self.tree.configure(style="IndexTree.Treeview")
            except Exception:
                pass
        self.tree.heading("path", text=T("路径"))
        self.tree.heading("files", text=T("文件"))
        self.tree.heading("dirs", text=T("目录"))
        self.tree.heading("last", text=T("最后扫描"))
        self.tree.heading("enabled", text=T("启用"))
        self.tree.column("path", width=280, anchor="w")
        self.tree.column("files", width=70, anchor="e")
        self.tree.column("dirs", width=70, anchor="e")
        self.tree.column("last", width=130, anchor="center")
        self.tree.column("enabled", width=50, anchor="center")
        sb_l = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb_l.set)
        sb_l.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.tag_configure("off", foreground=theme_get("fg_dim"))
        self.tree.bind("<<TreeviewSelect>>", self._on_select_root)
        self.tree.bind("<Double-1>", lambda e: self._toggle_enabled())
        middle.add(left, weight=3)

        # 右：详情 + 进度 + 日志
        right = ttk.Frame(middle)
        middle.add(right, weight=2)

        info_box = ttk.LabelFrame(right, text=T("详情"), padding=6)
        info_box.pack(fill="x")
        self._info_lbl = ttk.Label(info_box, text=T("（未选中）"),
                                   foreground=theme_get("fg"), justify="left")
        self._info_lbl.pack(anchor="w")

        prog_box = ttk.LabelFrame(right, text=T("进度"), padding=6)
        prog_box.pack(fill="x", pady=(8, 0))
        self._prog_lbl = ttk.Label(prog_box, text=T("空闲"),
                                   foreground=theme_get("fg_dim"))
        self._prog_lbl.pack(anchor="w")
        self._prog_bar = ttk.Progressbar(prog_box, mode="determinate",
                                         length=300)
        self._prog_bar.pack(fill="x", pady=(4, 0))

        log_box = ttk.LabelFrame(right, text=T("日志"), padding=6)
        log_box.pack(fill="both", expand=True, pady=(8, 0))
        self._log = tk.Text(log_box, wrap="none", width=48, height=12,
                            font=("Consolas", UI_FONT_SIZE), bg=theme_get("panel_bg2"), fg=theme_get("fg"),
                            borderwidth=0, highlightthickness=0)
        sb_r = ttk.Scrollbar(log_box, orient="vertical",
                             command=self._log.yview)
        self._log.configure(yscrollcommand=sb_r.set)
        sb_r.pack(side="right", fill="y")
        self._log.pack(side="left", fill="both", expand=True)
        self._log.configure(state="disabled")

        # ★ v25：底部按钮块已经在上面（贴底 pack）了，这里不再重复

        self._reload()
        # ★ v25：顺手给日志区写点有用的东西（免得窗口里大片空白）
        try:
            cfg = load_idle_settings()
            self._log_write(
                "提示：双击一行 = 启用 / 停用；「▶▶ 扫描全部」= "
                "把启用的根目录全扫一遍（现在会顺带记下文件大小）")
            if cfg["index_enabled"]:
                self._log_write(
                    f"☁ 闲时自动跑：开启（鼠标 / 键盘空闲 "
                    f"{cfg['index_minutes']} 分钟后，后台慢慢扫一遍）")
            else:
                self._log_write("☁ 闲时自动跑：关闭")
        except Exception:
            pass

        self.update_idletasks()
        # ★★★ 2026-10-08 改成"按内容算尺寸"（待清算 #8-①「字显示不全」）★★★
        #   ★ 实测：内容请求 **1657** 宽，而原来写死 1000 → **右边被切 657 像素**。
        #     表现就是用户看到的：
        #       · 右上「(没有扫完的任务)」被切掉一半
        #       · 底部几段提示文字（"（调大更快…）"）也被截断
        #       · 表头「最后扫描」显示成「最后扫」
        #   ★ 为什么不直接把数字改成 1657：那是**这台机器这个字号**量出来的，
        #     换台机器/换缩放就不对了 —— **不能写死量出来的值**（错题本 #116 的教训）。
        #   ★ 现在：`winfo_reqwidth/reqheight` 再夹在 `[最小可用, 屏幕 92%]`。
        try:
            req_w = int(self.winfo_reqwidth())
            req_h = int(self.winfo_reqheight())
            sw = int(self.winfo_screenwidth())
            sh = int(self.winfo_screenheight())
            max_w, max_h = int(sw * 0.92), int(sh * 0.92)
            min_w, min_h = 820, 520
            w = max(min_w, min(req_w, max_w))
            h = max(min_h, min(req_h, max_h))
            x = master.winfo_rootx() + (master.winfo_width() - w) // 2
            y = master.winfo_rooty() + (master.winfo_height() - h) // 3
            x = max(0, min(x, max(0, sw - w - 10)))
            y = max(0, min(y, max(0, sh - h - 40)))
            self.geometry("%dx%d+%d+%d" % (w, h, x, y))
            try:
                self.minsize(min_w, min_h)
            except Exception:
                pass
        except Exception:
            # 兜底：至少把位置摆正（原来的做法）
            try:
                w, h = self.winfo_width(), self.winfo_height()
                x = master.winfo_rootx() + (master.winfo_width() - w) // 2
                y = master.winfo_rooty() + (master.winfo_height() - h) // 3
                self.geometry("+%d+%d" % (max(x, 0), max(y, 0)))
            except Exception:
                pass
        # ★ 独立窗口，不加 transient，这样才有完整的最小化/最大化按钮
        try:
            self.resizable(True, True)
        except Exception:
            pass

        self._poll_job = self.after(80, self._poll)

    # ---------------- ★ 跟着皮肤走（2026-10-08 新增） ----------------
    def _apply_theme(self):
        """★★ 把本窗口里"原生 tk 控件"的颜色按**当前皮肤**重刷一遍。

        ★★ 2026-10-08 新增（待清算 #8-②「切换夜间皮肤显示不对」）。

        ★ 为什么必须专门写一个（而不能靠主程序那套自动扫描）：
          · 这个窗口是 **`Toplevel`** —— 独立窗口，
            主程序的 `_retheme_tree(root)` **扫不到它**（不在 root 的树里）；
          · 它里面又**大量用 `tk.Text` / `tk.Frame`**（原生控件）——
            那些颜色是"建的时候设死的"，`ttk` 那套样式表管不了它们。
          ★ 两件事叠一起 → **皮肤一换，这个窗口就"留在旧皮肤里"**。

        ★ 什么时候会被调：
          ① 主程序 `_retheme_custom_parts()` 里（切皮肤时，遍历 `_theme_windows`）；
          ② 本窗口自己需要时。
          ★ 每一块都单独 `try` —— 坏一块不影响别的（本程序一贯写法）。
        """
        # ① 窗口自己
        try:
            self.configure(bg=theme_get("win_bg"))
        except Exception:
            pass
        # ② 日志 / 详情 / 进度 那三个原生 Text
        for nm, bgkey in (("_log", "panel_bg2"),
                          ("_info_text", "panel_bg"),
                          ("_prog_text", "panel_bg")):
            try:
                wdg = getattr(self, nm, None)
                if wdg is None:
                    continue
                wdg.configure(bg=theme_get(bgkey), fg=theme_get("fg"),
                              insertbackground=theme_get("fg"),
                              selectbackground=theme_get("select_bg"),
                              highlightbackground=theme_get("line"))
            except Exception:
                pass
        # ③ 那三块 `ttk.LabelFrame` 的样式（它们跟 ttk 样式表走，重设一下更稳）
        try:
            st = ttk.Style()
            for sname in ("IndexTree.Treeview", "IndexTree.Treeview.Heading"):
                pass
            st.configure("IndexTree.Treeview",
                         background=theme_get("card_bg"),
                         foreground=theme_get("fg"),
                         fieldbackground=theme_get("card_bg"))
        except Exception:
            pass
        # ④ 主程序那套"登记过角色"的控件刷新（本窗口里的也会被刷）
        try:
            apply_themed()
        except Exception:
            pass

    # ---------------- 列表 ----------------
    def _reload(self):
        """★ 重新读一遍根目录列表。

        ★★ 2026-10-08 **修一个实测挖出来的真 bug**（方案 A 测试时发现的）：
          原来这里是"**先全删光、再重建**" ——
          `tree.delete(item)` 会把**每一行的 iid 都作废**，
          而"哪些行是选中的"是记在 Tk 的 selection 里的（也是 iid）→
          **重建之后选中就没了**。
          ★ 后果（用户能感觉到的）：
            扫描一结束会自动 `_reload()` → **你刚选中的那行"啪"没了** →
            想再扫一次就得**重新点一下那一行**；
            ★ 更坑的是：`_scan_selected()` 第一步就要"有没有选中"，
              没选中就弹「请先选中要扫描的根目录」——
              用户会觉得"我明明选了，怎么还说没选"。
          ★ 修法：**记下"选中了哪几个根目录 id" → 重建 → 按 id 选回来**。
            ★ 为什么按 **id** 而不是 iid：iid 是 Tk 现编的，重建就变；
              而根目录 id 是数据库里的，**稳定**（这也是"用稳定的标识"的通用做法）。
        """
        # ① 记下现在选中的是哪些根目录（按**数据库 id**，不按 iid）
        try:
            _sel_ids = set(self._selected_roots())
        except Exception:
            _sel_ids = set()
        # ② 重建
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._root_map = {}
        for r in self.store.all_index_roots():
            last = (r.get("last_scan_at") or "—")
            if len(last) > 16:
                last = last[:16].replace("T", " ")
            enabled = "✓" if r["enabled"] else "✗"
            iid = self.tree.insert(
                "", "end",
                values=(r["path"], r["total_files"], r["total_dirs"],
                        last, enabled),
                tags=() if r["enabled"] else ("off",))
            self._root_map[iid] = r["id"]
        # ③ 把选中**按 id 选回来**
        if _sel_ids:
            try:
                keep = [iid for iid, rid in self._root_map.items()
                        if rid in _sel_ids]
                if keep:
                    self.tree.selection_set(keep)
                    try:
                        self.tree.see(keep[0])
                    except Exception:
                        pass
            except Exception:
                pass
        self._update_info()

    def _selected_roots(self):
        out = []
        for iid in self.tree.selection():
            rid = self._root_map.get(iid)
            if rid is not None:
                out.append(rid)
        return out

    def _on_select_root(self, event=None):
        self._update_info()

    def _update_info(self):
        ids = self._selected_roots()
        if not ids:
            # ★ v25：没选中时显示总览，别让详情框大片空白
            self._info_lbl.config(text=self._summary_text())
            return
        if len(ids) > 1:
            self._info_lbl.config(text=f"已选中 {len(ids)} 个根目录"
                                       f"（双击一行 = 启用 / 停用）")
            return
        rid = ids[0]
        roots = {r["id"]: r for r in self.store.all_index_roots()}
        r = roots.get(rid)
        if r is None:
            self._info_lbl.config(text=T("（已删除）"))
            return
        cached = self.store.dir_cache_meta_count_under(r["path"])
        text = (
            T("路径：{x}\n", x=r["path"]) +
            T("状态：{x}\n",
              x=(T("启用") if r["enabled"] else T("已停用"))) +
            T("已缓存目录数：{x}\n", x=cached) +
            T("上次扫描：{x}\n",
              x=(r.get("last_scan_at") or T("从未"))) +
            T("上次统计：文件 {a}  目录 {b}\n",
              a=r["total_files"], b=r["total_dirs"])
        )
        if r.get("last_error"):
            text += T("上次错误：{x}\n", x=r["last_error"])
        self._info_lbl.config(text=text)

    def _summary_text(self):
        """★ v25：没选中根目录时，详情框显示总览（不再大片空白）。"""
        try:
            roots = self.store.all_index_roots()
        except Exception:
            roots = []
        n_all = len(roots)
        n_on = sum(1 for r in roots if r.get("enabled"))
        tot_f = sum(int(r.get("total_files") or 0) for r in roots)
        tot_d = sum(int(r.get("total_dirs") or 0) for r in roots)
        try:
            cached = self.store.dir_cache_meta_count_under("")
        except Exception:
            cached = 0
        return (T("根目录：{a} 个（已启用 {b} 个）\n",
                  a=n_all, b=n_on) +
                T("已缓存目录数：{x}\n", x=cached) +
                T("索引统计：文件 {a}  目录 {b}\n",
                  a=tot_f, b=tot_d) +
                T("提示：选中左边一行看详情；双击一行 = 启用 / 停用。"))

    # ---------------- ★ v25：闲时设置 ----------------
    def _save_idle_cfg(self):
        """把「闲时自动跑」的设置写进设置文件（两个窗口共用）。"""
        try:
            minutes = int(self.idle_min_var.get())
        except Exception:
            minutes = DEFAULT_IDLE_MINUTES
        minutes = max(IDLE_MIN_MINUTES, min(IDLE_MAX_MINUTES, minutes))
        try:
            self.idle_min_var.set(str(minutes))
        except Exception:
            pass
        try:
            save_idle_settings(index_enabled=bool(self.idle_var.get()),
                               index_minutes=minutes)
        except Exception:
            pass
        self._refresh_idle_hint()
        try:
            if self.app is not None:
                self.app._refresh_idle_state()
        except Exception:
            pass

    def _refresh_idle_hint(self):
        try:
            cfg = load_idle_settings()
            last = cfg.get("index_last") or 0
            if last:
                txt = ("上次闲时跑：" + datetime.fromtimestamp(last)
                       .strftime("%m-%d %H:%M"))
            else:
                txt = T("还没闲时跑过")
            self._idle_hint_lbl.config(text=txt)
        except Exception:
            pass

    # ---------------- ★ v25 补丁17：CloudDrive2 本地接口 ----------------

    def _save_cd_api_cfg(self):
        """记住「网盘索引走不走 API」和「同时发几个请求」。"""
        try:
            save_ui_setting("cd_api_enabled", bool(self.cd_api_var.get()))
        except Exception:
            pass
        try:
            n = int(str(self.cd_workers_var.get()).strip() or CD_API_DEFAULT_WORKERS)
        except Exception:
            n = CD_API_DEFAULT_WORKERS
        if n < CD_API_MIN_WORKERS:
            n = CD_API_MIN_WORKERS
        if n > CD_API_MAX_WORKERS:
            n = CD_API_MAX_WORKERS
        try:
            self.cd_workers_var.set(str(n))
            save_ui_setting("cd_api_workers", n)
        except Exception:
            pass
        self._refresh_cd_api_hint()

    def _refresh_cd_api_hint(self):
        """在那一行右边写一句「现在是什么状态」，别让用户猜。"""
        try:
            tok = str(load_ui_setting("cd_api_token", "") or "").strip()
            if not HAS_CD_API:
                txt = "（没找到 grpcio 库，只能走挂载盘）"
            elif not tok:
                txt = T("（还没填令牌，点左边按钮填一次）")
            elif not bool(self.cd_api_var.get()):
                txt = "（已关闭，网盘索引会走挂载盘，慢）"
            else:
                txt = "令牌已保存（%s…）" % tok[:8]
            self._cd_api_lbl.config(text=txt)
        except Exception:
            pass

    def _ask_cd_token(self):
        """让用户把 CloudDrive2 的 API 令牌粘进来，并当场测一下通不通。

        令牌怎么来：浏览器打开 http://localhost:19798 →「API 令牌」页 →
        创建令牌（勾上「列出文件」这类读权限就够）→ 复制那串。
        """
        cur = str(load_ui_setting("cd_api_token", "") or "")
        tok = self._ask_one_line(
            "CloudDrive2 API 令牌",
            "把 CloudDrive2 的 API 令牌粘进来（留空 = 清掉，改走挂载盘）：\n\n"
            "获取方法：浏览器打开 http://localhost:19798 →「API 令牌」页 →\n"
            "创建令牌（勾上文件读取 / 列出这类权限）→ 复制那串粘贴到这里。",
            cur)
        if tok is None:
            return
        tok = tok.strip()
        try:
            save_ui_setting("cd_api_token", tok)
        except Exception:
            pass
        if not tok:
            self._log_write("已清空 CloudDrive2 令牌 → 网盘索引改走挂载盘扫描")
            self._refresh_cd_api_hint()
            return
        self._log_write("正在测试 CloudDrive2 本地接口…")
        client = CloudDriveApiClient(tok)
        ok = False
        try:
            ok = client.connect()
            if ok:
                self._log_write("✓ 连接成功：%s" % client.describe())
                try:
                    ms = client.mounts()
                except Exception:
                    ms = []
                if ms:
                    self._log_write("  识别到网盘挂载：" + "、".join(
                        "%s(%s)" % (n, mp or "?") for n, _s, mp in ms))
                else:
                    self._log_write("  没读到网盘挂载点（本地磁盘挂载会跳过）")
            else:
                self._log_write("✗ 连接失败：%s" % (client.last_error or "原因不明"))
        except Exception as exc:
            self._log_write("✗ 连接出错：%s" % str(exc)[:200])
        finally:
            try:
                client.close()
            except Exception:
                pass
        self._refresh_cd_api_hint()
        try:
            if ok:
                messagebox.showinfo(
                    "测试通过",
                    "CloudDrive2 连接成功 ✓\n\n"
                    "以后扫网盘索引就会走这个本地接口，比走挂载盘快很多。",
                    parent=self)
            else:
                messagebox.showwarning(
                    "测试没通过",
                    "没连上 CloudDrive2：\n%s\n\n"
                    "排查顺序：\n"
                    "1) 浏览器能打开 http://localhost:19798 吗？\n"
                    "2) 令牌是不是复制全了（一串 36 位的）？\n"
                    "3) CloudDrive2 服务在不在运行（services.msc 里找 "
                    "CloudDrive2 Service）？\n\n"
                    "连不上也不影响使用，索引会照旧走挂载盘扫描。"
                    % (client.last_error or "原因不明"), parent=self)
        except Exception:
            pass

    def _ask_one_line(self, title, prompt, initial=""):
        """★ v25 补丁17：一个「一行输入」的小窗口（不想依赖 simpledialog）。"""
        top = tk.Toplevel(self)
        # ★★ 2026-10-07：Toplevel 是**原生窗口**，底色不跟 ttk 主题走 ——
        #   不设 bg 就用系统默认（白/浅灰），那就是"小窗口夜间还是白的"的根因。
        try:
            top.configure(bg=theme_get("win_bg"))
            # ★ 登记一下，切主题时由 _retheme_custom_parts 统一刷新
            _reg = getattr(self, "_theme_windows", None)
            if _reg is None:
                _reg = self._theme_windows = []
            _reg.append(top)
        except Exception:
            pass
        top.title(title)
        top.transient(self)
        top.resizable(False, False)
        ttk.Label(top, text=prompt, justify="left").pack(
            padx=12, pady=(12, 6), anchor="w")
        var = tk.StringVar(value=str(initial or ""))
        ent = ttk.Entry(top, textvariable=var, width=56)
        ent.pack(padx=12, fill="x")
        ent.focus_set()
        ent.icursor("end")
        out = {"v": None}

        def _ok(_e=None):
            out["v"] = var.get()
            top.destroy()

        def _cancel(_e=None):
            out["v"] = None
            top.destroy()

        row = ttk.Frame(top)
        row.pack(fill="x", pady=10, padx=12)
        ttk.Button(row, text=T("确定"), command=_ok).pack(side="right")
        ttk.Button(row, text=T("取消"), command=_cancel).pack(
            side="right", padx=(0, 6))
        ent.bind("<Return>", _ok)
        top.bind("<Escape>", _cancel)
        try:
            top.grab_set()
        except Exception:
            pass
        self.wait_window(top)
        return out["v"]

    def _toggle_enabled(self):
        ids = self._selected_roots()
        if not ids:
            return
        roots = {r["id"]: r for r in self.store.all_index_roots()}
        for rid in ids:
            r = roots.get(rid)
            if r is None:
                continue
            self.store.set_index_root_enabled(rid, not bool(r["enabled"]))
        self._reload()

    # ---------------- 添加 / 移除 ----------------
    def _add_root(self):
        d = filedialog.askdirectory(title=T("选择要建立索引的根目录"),
                                    parent=self)
        if not d:
            return
        try:
            self.store.add_index_root(d)
        except Exception as exc:
            messagebox.showerror("添加失败", str(exc), parent=self)
            return
        self._reload()
        self._log_write(f"已添加根目录：{d}")

    def _remove_root(self):
        ids = self._selected_roots()
        if not ids:
            return
        if not messagebox.askyesno(
                "确认",
                f"确定移除选中的 {len(ids)} 个根目录吗？\n"
                "（会同时清掉这些根目录下的目录缓存）",
                parent=self):
            return
        for rid in ids:
            self.store.remove_index_root(rid, also_clear_cache=True)
        self._reload()
        self._log_write(f"已移除 {len(ids)} 个根目录")

    def _clear_selected_cache(self):
        ids = self._selected_roots()
        if not ids:
            return
        if not messagebox.askyesno(
                "确认",
                f"清空选中的 {len(ids)} 个根目录的所有目录缓存？\n"
                "（根目录本身保留）",
                parent=self):
            return
        roots = {r["id"]: r for r in self.store.all_index_roots()}
        for rid in ids:
            r = roots.get(rid)
            if r is None:
                continue
            self.store.clear_dir_cache_under(r["path"])
        self._reload()
        self._log_write(f"已清空 {len(ids)} 个根目录的缓存")

    # ---------------- 扫描 ----------------
    def _scan_selected(self):
        ids = self._selected_roots()
        if not ids:
            # ★★ 2026-10-08：**把话说清楚** ——
            #   原来只有一句「请先选中要扫描的根目录」，
            #   用户可能"觉得自己选了"（其实是扫描结束后选中被刷掉了，
            #   见 `_reload` 里的说明）→ 一脸茫然。
            #   ★ 现在**告诉他去哪儿点**，并且给个替代路径。
            messagebox.showinfo(
                "还没有选中",
                "请先在下面「索引根目录」那个列表里**点一下要扫的那一行**，\n"
                "然后再点这个按钮。\n\n"
                "★ 想一次扫全部？直接点旁边的「▶▶ 扫描全部」就行，\n"
                "　 那个不需要先选中。",
                parent=self)
            return
        if self._scan_worker is not None:
            messagebox.showinfo("提示", T("已有扫描正在进行"), parent=self)
            return
        # ★ 补丁24：如果该根目录有没扫完的任务，问一下是接着扫还是重头扫
        for rid in ids:
            n = self._pending_count(rid)
            if n > 0:
                if not messagebox.askyesno(
                        "接着上次继续？",
                        "这个根目录上次没扫完，还差 %d 个目录没扫。\n\n"
                        "点「是」= 接着上次没扫完的地方继续（快）；\n"
                        "点「否」= 从头重新扫一遍。" % n, parent=self):
                    self._reset_task(rid)
                break
        self._start_scan(ids)

    def _scan_all(self):
        ids = [r["id"] for r in self.store.all_index_roots()
               if r["enabled"]]
        if not ids:
            messagebox.showinfo("提示", T("没有启用的根目录"),
                                parent=self)
            return
        if self._scan_worker is not None:
            messagebox.showinfo("提示", T("已有扫描正在进行"), parent=self)
            return
        left = sum(self._pending_count(rid) for rid in ids)
        if left > 0:
            if not messagebox.askyesno(
                    "接着上次继续？",
                    "上次没扫完，合计还差 %d 个目录。\n\n"
                    "点「是」= 接着扫（快很多）；\n"
                    "点「否」= 全部从头重新扫一遍（很慢）。" % left,
                    parent=self):
                for rid in ids:
                    self._reset_task(rid)
        self._start_scan(ids)

    # ---------------- ★ v25 补丁24：接力任务记录 ----------------
    def _list_remaining_dirs(self, rid, root_path):
        """列出一个根目录下「还没扫过 / 扫过但缺内容」的目录清单（待办）。

        ★ 索引里已经缓存着「每个目录下面有什么」，所以这份清单**不用碰网盘**，
          几秒就能列全（拿它当"这次要扫哪些目录"的清单）：
            · 已经扫过的目录如果里面已经有文件，就跳过（省时间）；
            · 空的目录 / 上次没扫到的目录，重新列一遍（这正是"接力"要补的）。
        另外会顺手清一次「幽灵目录」，让清单干净。
        """
        prefix = str(root_path).rstrip("\\") + "\\"
        plow = prefix.lower()
        try:
            prune_orphan_dir_cache(self.store, prefix)
        except Exception:
            pass
        rows = []
        try:
            # ★ 补丁24：用「等于自己 或 子孙」的写法（不用 LIKE）
            rows = self.store.conn.execute(
                "SELECT dir_path, SUM(CASE WHEN is_dir=0 THEN 1 ELSE 0 END) "
                "FROM dir_cache WHERE " + dir_scope_clause() +
                " GROUP BY dir_path", dir_scope_args(prefix)).fetchall()
        except Exception as exc:
            try:
                note_swallowed(T("索引接力：列待办目录失败，这次就全量扫"), exc)
            except Exception:
                pass
            return set()
        out = set()
        seen = set()
        for r in rows:
            try:
                dp, nfiles = r[0], (r[1] or 0)
            except Exception:
                continue
            if not dp:
                continue
            seen.add(dp.rstrip("\\").lower())
            if dp.lower() == plow or dp.rstrip("\\").lower() == plow.rstrip("\\"):
                out.add(dp)                # 根目录本身总要列一次
            elif nfiles <= 0:
                out.add(dp)                # 空的 / 没扫到的目录：再列一次
        # ★ 关键：**从没扫过的目录**（父目录里列过它、但它自己没有缓存行）
        #   也要算进待办 —— 否则第一次扫描的待办会是空的。
        try:
            rows2 = self.store.conn.execute(
                "SELECT DISTINCT dir_path, name FROM dir_cache "
                "WHERE " + dir_scope_clause() + " AND is_dir=1",
                dir_scope_args(prefix)).fetchall()
            for r2 in rows2:
                try:
                    parent, nm = r2[0], r2[1]
                except Exception:
                    continue
                if not parent or not nm:
                    continue
                child = parent.rstrip("\\") + "\\" + nm
                if child.lower() not in seen:
                    out.add(child)          # 这个子目录还没有自己的缓存 → 要扫
        except Exception as exc:
            try:
                note_swallowed(T("索引接力：找「从没扫过的子目录」失败"), exc)
            except Exception:
                pass
        return out

    # ---------------- ★ v25 补丁24：接力任务记录 ----------------
    def _load_task(self):
        """读出「接力任务」记录（存在设置文件里，所以关掉程序也在）。"""
        t = load_ui_setting("index_scan_task", None)
        if not isinstance(t, dict):
            t = {}
        return t

    def _save_task(self, t):
        try:
            save_ui_setting("index_scan_task", t)
        except Exception as exc:
            try:
                note_swallowed(T("索引任务：保存接力进度失败"), exc)
            except Exception:
                pass

    def _save_progress(self, rid, left, task):
        """把「还剩哪些目录没扫」写进任务记录（关掉程序也还在）。"""
        try:
            t = self._load_task()
            key = str(rid)
            # ★★ 2026-10-03：原来这里调了两次 t.get(key) —— 一次在 isinstance 里、一次取返回值。
            #   缓存一次，避免 key 取值有副作用时被触发两次。
            v = t.get(key)
            rec = v if isinstance(v, dict) else {}
            rec["path"] = rec.get("path") or ""
            rec["queue"] = sorted(left)[:20000]
            rec["remaining"] = len(left)
            rec["progress"] = int(task.get("done") or 0)
            rec["total"] = int(task.get("goal") or 0)
            if not rec.get("started"):
                rec["started"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            t[key] = rec
            self._save_task(t)
            self._queue.put(("task_hint", None))
        except Exception as exc:
            try:
                note_swallowed(T("索引接力：保存进度失败"), exc)
            except Exception:
                pass

    def _task_of(self, rid, create=False):
        t = self._load_task()
        key = str(rid)
        r = t.get(key)
        if not isinstance(r, dict):
            if not create:
                return None
            r = {"path": "", "queue": [], "done": 0, "remaining": 0,
                 "started": "", "progress": 0}
            t[key] = r
        return r

    def _pending_count(self, rid):
        """这个根目录还有多少目录没扫完（0 = 没欠账）。"""
        r = self._task_of(rid)
        if not r:
            return 0
        return int(r.get("remaining") or 0)

    def _reset_task(self, rid):
        t = self._load_task()
        t.pop(str(rid), None)
        self._save_task(t)
        self._refresh_task_hint()

    def _finish_task(self, rid):
        self._reset_task(rid)

    def _total_dirs_of(self, rid, root_path):
        """这个根目录下索引里一共有多少个目录（用来算进度百分比）。"""
        prefix = str(root_path).rstrip("\\") + "\\"
        try:
            # ★ 补丁24：用「等于自己 或 子孙」的写法（不用 LIKE）
            row = self.store.conn.execute(
                "SELECT COUNT(DISTINCT dir_path) FROM dir_cache "
                "WHERE " + dir_scope_clause(),
                dir_scope_args(root_path)).fetchone()
            return int(row[0] or 0) if row else 0
        except Exception:
            return 0

    def _refresh_task_hint(self):
        """★ 兼容老名字 —— 现在统一走 `_refresh_scan_ui()`。"""
        self._refresh_scan_ui()

    # ================= ★★ 播放器式的扫描按钮（2026-10-08 新增）★★ =================
    def _scan_state(self):
        """★ 现在是什么状态 —— **只有三种**：`idle` / `running` / `paused`。

        ★★★ 2026-10-08 **重写**（原来靠"推断"，绕了七圈都是错的）★★★

        ★★ 为什么重写（这段教训很值钱）：
          原来这个方法是从几个标志**推断**出来的：
            `_scan_worker is not None` / `_pause_requested` / 磁盘上还剩多少
          → **它们互相打架**，修一个冒一个：
            · 只看 worker      → "按了暂停还说在扫"
            · 加"按过暂停"标志 → "真扫完了还说暂停"
            · 线程结束就清标志 → "按了暂停却说空闲"（标志被线程结束清掉了）
            · 再补"上次剩多少" → 又出新花样
          **改到第七轮还是不对** —— 这就说明**方向错了**。

        ★★ 正解：**状态就该是"明确记下来的一个值"**，
          由"**发生了什么**"直接写，**不推断**。
          ★ 播放器就是这么写的：按暂停 → `state = PAUSED`，没有什么"推断"。

        ★ 谁负责改 `_scan_state_now`（**只有这五个地方**）：
          | 什么时候 | 改成 |
          |---|---|
          | 用户按「开始 / 继续」（`_start_scan`） | `running` |
          | 用户按「暂停」（`_pause_scan`）         | `paused`  |
          | 用户按「停止」（`_on_stop_btn`）        | `idle`    |
          | 线程结束、还有剩（`_poll` 收到 done）   | `paused`  |
          | 线程结束、没剩了（`_poll` 收到 done）   | `idle`    |

        ★ 兜底：万一 `_scan_state_now` 还没被设过（窗口刚建），
          就按"磁盘上还剩多少"给个初始值 —— 这样**关掉程序再打开**，
          还能看到"上次没扫完"。
        """
        v = getattr(self, "_scan_state_now", None)
        if v in ("idle", "running", "paused"):
            return v
        # ★ 兜底（只在窗口刚建、还没发生过任何事情时走到）
        try:
            t = self._load_task()
            left = sum(int((x or {}).get("remaining") or 0)
                       for x in t.values())
            return "paused" if left > 0 else "idle"
        except Exception:
            return "idle"


    def _task_left(self):
        """★ 还有多少个目录没扫（给状态文字用）。

        ★ 只认**磁盘上的任务记录** —— 那是唯一权威。
          （原来还想"和内存里记的数取大的"，结果出现
            `已暂停（还剩 0 个目录）` 这种自相矛盾。
            ★ 教训：**同一个数字只该有一个来源**。）
        """
        try:
            t = self._load_task()
            return sum(int((v or {}).get("remaining") or 0)
                       for v in t.values())
        except Exception:
            return 0

    def _settle_state_after_scan(self):
        """★★ 扫描线程结束后，**等一小会儿**再"按事实定状态"。

        ★★ 2026-10-08 为什么需要（监视器抓出来的真凶）：
          · 任务记录是**工作线程**写的（`_save_progress`），
            而且它**在收尾时才写**"还剩多少"。
          · `_poll`（主线程）一收到"线程结束"的消息，我就去读盘 →
            **读到的是旧记录（空的）** → 以为"全扫完了" → 状态判成 idle。
          · 实测就是这样：日志明明写着「还剩 17 个目录」，
            状态却变成「空闲」。
        ★ 修法：**不立刻判**，等 600ms（线程肯定写完了）再判。
          ★ 这段时间里状态**保持用户设定的那个**（按了暂停就还是 paused），
            所以用户**看不到闪烁**。
        ★ 教训（很值钱）：
          **"线程结束了" ≠ "它干的活都落盘了"** ——
          两个线程之间"收尾写盘"和"收到结束消息"**有先后**。
          ★ 要读"另一个线程写的盘"，就得**给它一点时间**；
            更干净的做法是（以后可以改）**让线程把结果塞在结束消息里带回来**
            —— 那就完全不用等、也不会读错。
        """
        try:
            left = self._task_left()
            self._last_left = left
            # ★ 按"全局还剩多少"定状态
            _new = "paused" if left > 0 else "idle"
            # ★★ 2026-10-08 小补丁（实测发现）：**用户在这 600ms 里按过东西，
            #    就别用这次"延时判定"覆盖他** ——
            #    比如：扫描结束 → 用户立刻按「⏹ 停止」（要 idle）→
            #    600ms 后这次延时判定跑回来，又把它改回 paused
            #    （用户看到"我明明停了，它还显示暂停"）。
            #    ★ 判据：**用户操作之后就不再接受"旧的延时判定"**。
            if bool(getattr(self, "_user_acted_since_scan", False)):
                self._user_acted_since_scan = False
            else:
                self._scan_state_now = _new
        except Exception:
            pass
        self._pending_state_check = False
        try:
            self._refresh_scan_ui()
        except Exception:
            pass


    def _refresh_scan_ui(self):
        """★★ 把"按钮长相 + 状态文字"按**当前状态**一次摆对。

        ★ 三种状态（播放器那套）：
        | 状态 | 主按钮 | ⏹ 停止 | 状态文字 |
        |---|---|---|---|
        | 空闲   | `▶ 扫描选中` | 灰   | （没有没扫完的任务）|
        | 扫描中 | `⏸ 暂停`     | 灰   | 正在扫…（已扫 N）|
        | 暂停后 | `▶ 继续扫描` | **亮** | 已暂停（还剩 N，可接着扫）|

        ★ 每块都单独 try —— 坏一块不影响别的（本程序一贯写法）。
        """
        st = self._scan_state()
        # ---- 主按钮 ----
        try:
            if st == "running":
                self._main_btn.config(text=T("⏸ 暂停"), command=self._on_main_btn,
                                      state="normal")
            elif st == "paused":
                self._main_btn.config(text=T("▶ 继续扫描"),
                                      command=self._on_main_btn,
                                      state="normal")
            else:
                self._main_btn.config(text=T("▶ 扫描选中"),
                                      command=self._on_main_btn,
                                      state="normal")
        except Exception:
            pass
        # ---- 停止按钮：**只有"暂停后"才亮** ----
        try:
            self._stop_btn.config(
                state=("normal" if st == "paused" else "disabled"))
        except Exception:
            pass
        # ---- 状态文字 ----
        try:
            if st == "running":
                # 已扫多少？用实时记录的那个数（`_scan_done_now`），
                #   ★ 不要用进度条的 value —— 那是**取模**过的（`% 1000`），
                #     拿来当"已扫数量"会显示成 0~100 的假数。
                _done = int(getattr(self, "_scan_done_now", 0) or 0)
                txt = "正在扫…"
                if _done > 0:
                    txt = "正在扫…（已扫 %d 个目录）" % _done
                self._task_lbl.config(text=txt, foreground=theme_get("ok"))
            elif st == "paused":
                left = self._task_left()
                self._task_lbl.config(
                    text="⏸ 已暂停（还剩 %d 个目录 —— 点「▶ 继续扫描」接着扫）"
                         % left,
                    foreground=theme_get("warn"))
            else:
                self._task_lbl.config(text=T("（没有没扫完的任务）"),
                                      foreground=theme_get("fg_dim"))
        except Exception:
            pass

    def _on_main_btn(self):
        """★ 主按钮：按**当前状态**决定干什么（播放器那个三角/双竖线）。

        · 空闲   → 开始扫"选中的"根目录
        · 扫描中 → **暂停**
        · 暂停后 → **从断的地方接着扫**

        ★★★ 2026-10-08 实测挖出来的**竞态**（这一条很值钱）★★★
          ★ 现象：实测里同一个操作序列，**有时候"暂停"成功、有时候变成"又开始扫"**。
          ★ 真因：**"按下按钮"和"扫描结束"可能撞在同一瞬间** ——
            用户按下去时扫描刚好结束 → `_scan_state()` 返回 "idle" →
            这里就当成"空闲"→ **又开了一次扫描**（用户的感受：
            "我明明按的是暂停，它怎么又扫起来了"）。
          ★ 修法（**"刚扫过"的记忆要留一会儿**）：
            记下"上一次扫描结束的时刻"，如果**离现在很近**（1.5 秒内），
            用户按主按钮**不要去开新的扫描** ——
            ★ 但也不能什么都不做（用户可能真想再扫）。
              所以：**这次按就当"没听见"，并提示一句** ——
              比"莫名其妙又扫一遍"好得多。
            ★ 这是"**别用瞬时状态回答用户意图**"的又一个变种
              （跟错题本 #110 的 `winfo_ismapped` 是同一类病）。
        """
        st = self._scan_state()
        if st == "running":
            self._pause_scan()
            return
        if st == "paused":
            self._resume_scan()
            return
        # ★ idle：先看看"是不是刚扫完"
        try:
            _just = getattr(self, "_scan_just_finished_at", 0) or 0
            if _just and (time.time() - _just) < 1.5:
                # 刚扫完不到 1.5 秒 —— 用户多半是"想暂停，但慢了半拍"
                self._log_write("（刚才那次扫描已经结束了，所以这一下没重新开扫；"
                                "想再扫一遍请再点一次）")
                try:
                    self._task_lbl.config(
                        text=T("（刚扫完）想再扫一遍，请再点一次这个按钮"),
                        foreground=theme_get("fg_dim"))
                except Exception:
                    pass
                return
        except Exception:
            pass
        self._scan_selected()

    def _round_done_count(self):
        """★ 这次已经扫了多少个目录（进度条 value，量不到就 0）。"""
        try:
            return int(self._prog_bar.cget("value") or 0)
        except Exception:
            return 0

    def _pause_scan(self):
        """★ 「⏸ 暂停」—— 停下来，**进度全留着**，随时能接着扫。

        ★ 跟老的 `_stop_scan` 干的是同一件事（它就是"停止=暂停"），
          现在把名字改对，并**顺手刷新按钮长相**。

        ★★ 2026-10-08 实测发现：光设 `_scan_cancel` **不够** ——
          工作线程要"跑完当前目录"才会看这个标志，
          这段时间 `_scan_worker` 还不是 `None` →
          `_scan_state()` 会判成 "running" → **按钮又变回「⏸ 暂停」**，
          用户看着像"按了没反应"。
          → 所以要**同时**设 `_pause_requested`（"用户已经按过暂停了"），
            `_scan_state()` 一看到它**立刻**就说 "paused"。
        """
        self._pause_requested = True
        self._scan_cancel = True
        self._stopped_by_user = True
        # ★★ 状态机：**用户按了暂停 → 明确记成 paused**
        self._scan_state_now = "paused"
        # ★ 标记"用户刚操作过" —— 让那次"延时判定"不要覆盖他
        self._user_acted_since_scan = True
        self._log_write("⏸ 已暂停（已经扫到的都保留了，点「▶ 继续扫描」接着扫）")
        self._refresh_scan_ui()

    def _on_stop_btn(self):
        """★ 「⏹ 停止」—— **真的停**：清掉这次的任务记录，下次从头扫。

        ★ 一定要**先确认**（用户手一抖就把进度清了，很亏）。
        ★ 只清"任务记录"（`index_scan_task`）——
          **已经扫进库的目录不删**（那是成果，不是垃圾）。

        ★★ 2026-10-08 实测发现（**这是实测才抓到的**）：
          我原来只在"暂停后"（`paused`）才亮"停止"，可**扫描中**它也是
          可以点的（用户可能"不想扫了，直接停"）——
          那时如果只弹确认框、不清标记，**线程还在跑、状态还是 running**，
          看着像"点了停止没用"。
          → 所以这里**不管在哪个状态都先"暂停"**（把线程叫停），
            再清任务记录 —— 这样"停止"在任何时候都真的生效。
        """
        # ★ 不管什么状态，先把工作线程叫停（否则清完任务记录它还在写）
        try:
            if self._scan_worker is not None:
                self._pause_requested = True
                self._scan_cancel = True
                self._stopped_by_user = True
        except Exception:
            pass
        left = self._task_left()
        try:
            ok = messagebox.askyesno(
                "停止扫描",
                "「停止」会清掉这次的任务记录，下次要从头扫。\n\n"
                "（已经扫进索引的内容不会删 —— 只是「接力」的进度没了）\n\n"
                "还有 %d 个目录没扫。确定停止吗？\n\n"
                "★ 如果只是想歇一会儿、等会儿接着扫，"
                "点「关闭」或者留在这儿都行（进度会自己留着）。"
                % (left,),
                parent=self)
        except Exception:
            ok = True
        if not ok:
            return
        try:
            self._save_task({})
        except Exception:
            pass
        # ★★ 状态机：**用户按了停止 → 明确记成 idle**（任务记录也清干净了）
        self._scan_state_now = "idle"
        # ★ 标记"用户刚操作过" —— 让那次"延时判定"不要覆盖他
        self._user_acted_since_scan = True
        self._last_left = 0
        self._log_write("⏹ 已停止（任务记录已清掉，下次从头扫；已扫进索引的不受影响）")
        self._refresh_scan_ui()

    # =================================================================

    def _resume_scan(self):
        if self._scan_worker is not None:
            messagebox.showinfo("提示", T("已有扫描正在进行"), parent=self)
            return
        t = self._load_task()
        ids = []
        try:
            valid = {r["id"] for r in self.store.all_index_roots()}
        except Exception:
            valid = set()
        for k, v in t.items():
            try:
                rid = int(k)
            except Exception:
                continue
            if rid in valid and int((v or {}).get("remaining") or 0) > 0:
                ids.append(rid)
        if not ids:
            messagebox.showinfo("提示", T("没有没扫完的任务，直接点「▶▶ 扫描全部」就行。"),
                                parent=self)
            return
        # ★★★ 2026-10-08（方案 A）**把"接上了"说清楚** ★★★
        #   ★ 用户报「继续经常变成重新扫描」—— 查清后发现：
        #     **其实是真接着扫的**（任务记录里存着"还剩哪些"），
        #     但日志只有一句"接着上次没扫完的地方继续（N 个根目录）"，
        #     **看不出"从哪接、还剩多少"** → 主观上就像"重来了一遍"。
        #   ★ 现在写清楚：**从第几个接、还剩多少** ——
        #     用户一眼就能确认"它真的接上了"。
        try:
            _left = self._task_left()
            _done_hint = ""
            # 每个根目录记录里可能有"已扫多少"，凑个"已扫 N"出来
            try:
                _done = 0
                for _v in t.values():
                    _v = _v or {}
                    _d = int(_v.get("done") or 0)
                    _done += _d
                if _done > 0:
                    _done_hint = "（已扫过 %d 个，**不重扫**）" % _done
            except Exception:
                _done_hint = ""
            self._log_write(
                "▶ 继续扫描：从上次断的地方接着来 %s —— 还剩 %d 个目录没扫"
                % (_done_hint, _left))
        except Exception:
            self._log_write("接着上次没扫完的地方继续（%d 个根目录）" % len(ids))
        self._start_scan(ids)


    def _start_scan(self, ids):
        # ★ v25：和闲时自动扫描共用一个忙标志，别同时扫两遍
        if INDEX_SCAN_EVENT.is_set():
            messagebox.showinfo(
                "提示",
                "已有扫描正在进行（可能是「闲时自动跑」在后台慢慢扫）。\n"
                "你动一下鼠标 / 键盘，闲时扫描就会自己收工，稍等片刻再试。",
                parent=self)
            return
        INDEX_SCAN_EVENT.set()
        self._scan_cancel = False
        self._stopped_by_user = False
        self._scan_had_left = False
        self._round_capped = False
        self._round_left = 0
        # ★★ 2026-10-08：**清掉"用户按过暂停"的标志** ——
        #   不清的话 `_scan_state()` 会一直说 "paused"，
        #   按钮永远停在「▶ 继续扫描」上（实测踩到的坑）。
        self._pause_requested = False
        # ★ 顺手把"上次结束时还剩多少"也归零（新一轮开始了，那个数过期了）
        self._last_left = 0
        # ★★ 状态机：**用户按了开始/继续 → 明确记成 running**
        self._scan_state_now = "running"
        # ★ 标记"用户刚操作过" —— 让上一次扫描的"延时判定"不要覆盖他
        self._user_acted_since_scan = True
        self._prog_bar.config(value=0)
        self._prog_lbl.config(text=T("准备扫描…"))
        self._scan_current_root_id = None
        self._log_write(f"开始扫描 {len(ids)} 个根目录")
        self._scan_worker = threading.Thread(
            target=self._scan_worker_fn, args=(list(ids),),
            daemon=True)
        # ★ 先赋线程再 start —— 这样 `_scan_state()` 立刻能答出 "running"
        self._scan_worker.start()
        # ★★ 2026-10-08（方案 A）：**开始之后刷一次按钮长相** ——
        #   主按钮要从「▶ 扫描选中」变成「⏸ 暂停」。
        #   ★ 必须在 `_scan_worker` **赋好值之后**调，否则状态还是 idle。
        self._refresh_scan_ui()
        # ★ 再补一次（`update_idletasks` 之后）——
        #   实测发现：`start()` 刚回来时有些控件状态还没落定，
        #   多刷一次更稳（成本几乎为零）。
        try:
            self.update_idletasks()
        except Exception:
            pass
        self._refresh_scan_ui()
    def _stop_scan(self):
        """★ 兼容老名字 —— 现在走 `_pause_scan()`（"停止"原本干的就是暂停的事）。"""
        self._pause_scan()

    def _scan_worker_fn(self, ids):
        """★ v25：改用公共的 scan_index_roots（scandir + 顺手记文件大小）。

        原来用 os.walk，只记名字不记大小，跑完文件列表里全是「?」。

        ★ v25 补丁24：这里也是「接力」的地方 ——
          每个根目录开始扫之前，先把它下面**还没扫过的目录**列一份待办清单，
          写进任务记录；扫的过程中不断把「已经扫到的」从清单里划掉。
          所以：中断（点停止 / 关窗口 / 闲时被打断）之后，清单还在，
          下次接着从剩下的开始；一个根目录整个扫完，才把它的清单清掉。
        """
        try:
            roots = {r["id"]: r for r in self.store.all_index_roots()}
        except Exception:
            roots = {}
        # ★ v25 补丁17：整批扫描开始前，先按设置连一次 CloudDrive2 的本地接口。
        #   连上了 → 网盘根目录走 API（快很多、报错是人话）；
        #   连不上 / 没填令牌 → 照旧走挂载盘，并把原因写进日志（不偷偷变慢）。
        api_client = None
        try:
            api_client, why = cd_api_client_from_settings()
            self._queue.put(("info", why))
        except Exception as exc:
            api_client = None
            self._queue.put(("info", "CloudDrive2 API 初始化出错：%s → 走挂载盘扫描"
                             % str(exc)[:150]))
        try:
            for rid in list(ids or []):
                if self._scan_cancel:
                    break
                r = roots.get(rid)
                if r is None:
                    continue
                path = r["path"]
                self._queue.put(("stage", (rid, path)))
                dir_count = 0
                file_count = 0
                error = ""
                tick = {"n": 0}

                # ★ 补丁24：准备这份「还要扫哪些目录」的待办清单
                task = self._task_of(rid, create=True)
                if not task.get("goal"):
                    try:
                        task["goal"] = int(self._total_dirs_of(rid, path))
                    except Exception:
                        task["goal"] = 0
                left_list = task.get("queue") if isinstance(task.get("queue"), list) else None
                left = set(x for x in (left_list or []) if x)
                if not left:
                    left = self._list_remaining_dirs(rid, path)
                total_left = len(left)
                self._queue.put(("task", (rid, path, total_left)))
                done_list = []
                # 停不下来的话，每个根目录这一轮最多处理这么多目录
                # （剩下的留在待办里，下次「接力继续」接着扫）
                MAX_PER_ROUND = 100000
                seen_n = {"n": 0}

                def _drop(d2):
                    """把已经扫过的目录从待办里划掉（注意各种路径写法）。"""
                    for key in (d2, d2.rstrip("\\"), d2.replace("/", "\\")):
                        if key in left:
                            left.discard(key)
                            done_list.append(key)
                    g = task.get("goal") or 0
                    if g and done_list:
                        task["done"] = min(g, int(task.get("done") or 0)
                                           + len(done_list))
                        del done_list[:]

                def _progress(_rid, _root, dc, fc, cur, tick=tick):
                    tick["n"] += 1
                    seen_n["n"] += 1
                    _drop(cur)
                    if dc <= 3 or tick["n"] % 10 == 0:
                        self._queue.put(
                            ("progress", (dc, fc, cur)))
                    if tick["n"] % 10 == 0:
                        self._save_progress(rid, left, task)
                    # 这一轮干够了就停（剩下的留着下次接力，避免一口气跑太久）
                    if seen_n["n"] >= MAX_PER_ROUND:
                        self._scan_cancel = True
                        self._round_capped = True

                try:
                    res = scan_index_roots(
                        self.store, [rid],
                        cancel_flag=lambda: self._scan_cancel,
                        progress_cb=_progress,
                        api_client=api_client)
                    if res:
                        _rid, _p, dir_count, file_count, error = res[0]
                except Exception as exc:
                    error = str(exc)
                # 收尾：保存这一轮的接力进度
                try:
                    self._save_progress(rid, left, task)
                except Exception:
                    pass
                self._queue.put(
                    ("one_done",
                     (rid, path, dir_count, file_count, error,
                      len(left) if left else 0)))
        finally:
            # 无论是正常结束、报错，还是窗口被关掉，都要放开忙标志
            try:
                if api_client is not None:
                    api_client.close()
            except Exception:
                pass
            INDEX_SCAN_EVENT.clear()
            self._queue.put(("done", None))

    def _poll(self):
        try:
            while True:
                kind, payload = self._queue.get_nowait()
                if kind == "stage":
                    rid, path = payload
                    self._scan_current_root_id = rid
                    self._prog_bar.config(value=0)
                    self._prog_lbl.config(text=f"正在扫描：{path}")
                    self._log_write(f"→ 扫描：{path}")
                elif kind == "info":
                    # ★ v25 补丁17：一句话说清这次到底走 API 还是走挂载盘
                    self._log_write(str(payload))
                elif kind == "task":
                    # ★ 补丁24：这个根目录这轮还要处理多少个目录
                    rid, path, left = payload
                    self._round_left = left
                    if left:
                        self._log_write(
                            "本轮要处理 %d 个目录（接力：只扫还没扫到的）" % left)
                    else:
                        self._log_write("本轮没有待办目录（都扫过了），"
                                        "会把这棵树快速核对一遍")
                elif kind == "task_hint":
                    self._refresh_task_hint()
                elif kind == "progress":
                    dc, fc, dp = payload
                    self._prog_bar.config(value=min(100, (dc % 1000) / 10))
                    self._prog_lbl.config(
                        text=f"已处理 {dc} 目录 / {fc} 文件    当前：{dp}")
                    # ★★ 2026-10-08（方案 A）：**实时刷状态文字** ——
                    #   用户要能看到「正在扫…（已扫 N 个目录）」在往上走，
                    #   不然"它到底在不在干活"看不出来。
                    #   ★ 用记录的 `_scan_done_now`（进度条那个数是取模的，
                    #     不适合当"已扫数量"）。
                    self._scan_done_now = int(dc)
                    self._refresh_scan_ui()
                elif kind == "one_done":
                    # ★ 补丁24：多带一个「还剩多少目录没扫」
                    try:
                        rid, path, dc, fc, err, left = payload
                    except Exception:
                        rid, path, dc, fc, err = payload[:5]
                        left = 0
                    if err and (err.startswith("跳过") or err.startswith("有 ")):
                        self._log_write(
                            f"✓ 完成：{path}  目录 {dc}  文件 {fc}"
                            f"  ·  {err}")
                    elif err:
                        self._log_write(
                            f"✗ 完成（有错误）：{path}  目录 {dc}  文件 {fc}"
                            f"  错误：{err}")
                    else:
                        self._log_write(
                            f"✓ 完成：{path}  目录 {dc}  文件 {fc}")
                    if left:
                        self._log_write(
                            f"⏸ 这个根目录还没扫完：还剩 {left} 个目录 ——"
                            f"点「⏯ 接力继续」可以接着扫")
                        self._scan_had_left = True
                        if self._stopped_by_user:
                            self._log_write("（是你按的停止：进度已保存）")
                        elif self._round_capped:
                            self._log_write("（这一轮跑够了先歇一下：进度已保存，"
                                            "接着点「⏯ 接力继续」继续）")
                            self._round_capped = False
                    else:
                        self._finish_task(rid)
                        self._log_write(f"✅ {path} 整个扫完了，任务完成")
                    self._refresh_task_hint()
                elif kind == "done":
                    left_total = 0
                    try:
                        t = self._load_task()
                        left_total = sum(int((v or {}).get("remaining") or 0)
                                         for v in t.values())
                    except Exception:
                        pass
                    if left_total:
                        self._log_write(
                            f"⏸ 扫描暂停：合计还有 {left_total} 个目录没扫完"
                            f"（进度已保存）。点「▶ 继续扫描」接着扫。")
                    else:
                        self._log_write("全部扫描结束（没有欠账）")
                    self._scan_worker = None
                    self._scan_current_root_id = None
                    self._stopped_by_user = False
                    # ★★★ 2026-10-08 **这一行是"三个 bug 换来的"**（实测才想明白）★★★
                    #
                    #   ★ 我先写了 `self._pause_requested = False` ——
                    #     想"线程结束了，标志该清了" →
                    #     **把用户的意图也抹掉了**：
                    #       按暂停 → 线程几十毫秒收尾 → 标志被清 →
                    #       那一刻任务记录还没写 → left=0 → **判成 idle**
                    #       → 用户看到「我按了暂停，它却说空闲」
                    #   ★ 然后我改成"线程不许动这个标志" →
                    #     **又过头了**：扫描**真的全扫完**了，标志还留着 →
                    #       **永远显示"已暂停（还剩 0）"**（实测）
                    #
                    #   ★★ 真正对的判据：**看"还有没有活没干完"** ——
                    #      这里 `left_total` **已经算出来了**，直接用它！
                    #        · left_total > 0 → 确实没扫完 → 该显示"已暂停"
                    #        · left_total = 0 → 真扫完了   → 该显示"空闲"
                    #      `_pause_requested` 只是**补充**（线程还在收尾、
                    #      来不及算 left 的那一小段），由 `_scan_state` 兜着。
                    #   ★ 所以这里：**清掉"按过暂停"的标志** ——
                    #     因为"线程结束了"这件事本身让这个标志**该退休了**；
                    #     但**同时**把 `left_total` 记下来（`_last_left`），
                    #     给 `_scan_state()` 用来回答"到底扫完没有"。
                    #     ★ 这就是那个"时序缝隙"的正解：
                    #       **把算好的结果记下来**，而不是让后面去猜。
                    self._pause_requested = False
                    try:
                        self._last_left = int(left_total or 0)
                    except Exception:
                        self._last_left = 0
                    # ★★★ 2026-10-08 **实测第四次才想对**（监视器抓到真凶）★★★
                    #   ★ 监视器输出（`_scan_state_now` 的读/写全打出来）：
                    #       None → running   (_start_scan:26709)
                    #       running → paused (_pause_scan:26583)   ← 用户按暂停，对的
                    #       paused → idle    (_poll:26991)         ← ★ 真凶在这儿
                    #   ★ 真因：**任务记录是"工作线程"写的**（`_save_progress`），
                    #     而线程**收尾时才写**"还剩多少"。
                    #     我在 `_poll` 里"线程一结束就读盘" →
                    #     **读到的是旧记录（空的）** → `_last_left = 0` → 判成 idle。
                    #   ★ 修法：**不在这儿立刻判** ——
                    #     记一个"待确认"的时刻，**过一小会儿再判**
                    #     （那时线程肯定把记录写完了）。
                    #     ★ 这段时间里状态**保持用户设定的那个**
                    #       （按了暂停就还是 paused），不会闪。
                    #   ★ 教训（很值钱）：
                    #     **"线程结束了" ≠ "它干的活都落盘了"** ——
                    #     线程的收尾写盘和"主线程收到结束消息"之间**有先后**。
                    #     ★ 所以：**要读"另一个线程写的盘"，得给它一点时间**
                    #       （或者干脆**让线程把结果放在消息里带回来**，
                    #        这才是最干净的做法 —— 见下面 `_pending_state_check`）。
                    self._scan_just_finished_at = time.time()
                    # ★ 先按"用户意图"保持住状态，然后**延后 600ms 再按事实定**
                    try:
                        self._pending_state_check = True
                        self.after(600, self._settle_state_after_scan)
                    except Exception:
                        self._settle_state_after_scan()
                    self._prog_bar.config(value=0)
                    self._prog_lbl.config(text=T("空闲"))
                    self._reload()
                    # ★ 用统一入口刷（按钮长相 + 状态文字一次摆对）
                    self._refresh_scan_ui()
                    break
        except queue.Empty:
            pass
        if self.winfo_exists():
            self._poll_job = self.after(120, self._poll)

    # ---------------- 日志 ----------------
    def _log_write(self, text):
        try:
            line = f"[{datetime.now().strftime('%H:%M:%S')}] {text}"
            self._log.configure(state="normal")
            self._log.insert("end", line + "\n")
            self._log.see("end")
            self._log.configure(state="disabled")
        except Exception:
            pass

    # ---------------- 关闭 ----------------
    def _on_close(self):
        if self._scan_worker is not None:
            if not messagebox.askyesno(
                    "扫描进行中", "扫描尚未完成，确定关闭吗？",
                    parent=self):
                return
            self._scan_cancel = True
        try:
            if self._poll_job is not None:
                self.after_cancel(self._poll_job)
        except Exception:
            pass
        # ★ 关闭后让主列表重新查一次缓存
        try:
            if self.app is not None and getattr(self.app, "view_mode", "") == "dir":
                self.app.root.after(
                    50,
                    lambda a=self.app: a.load_directory(a.current_dir))
        except Exception:
            pass
        self.destroy()



# ---------- 兜底（★ 它会吃掉错误，所以要专门测"用的哪一份"）----------
def _fallback():
    g = globals()
    for _n in _NEED:
        if g.get(_n) is None:
            g[_n] = _Borrowed(_n)


_fallback()
