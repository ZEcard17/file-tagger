# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：StarGraphEditor。

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
   · import 要写 `from StarGraphEditor import …`（**不带包路径**）
   · `_set_app` 要**取别名**（`as _fk_…`）—— 模块名和类名同名
   · 借名字清单**用 symtable + dir() 定**，别用正则猜
   · 代理类**必须实现 `__call__`**（函数也会被借）
   · ★ 兜底 except 会吃掉错误 → **必须专门测"用的哪一份"**
"""
import queue
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, colorchooser

# ---------- 要向主程序借的名字 ----------
_MUTABLE = ['BOLD', 'FONT', 'UI_FONT_SIZE']
_NEED = ['BOLD', 'FONT', 'SimpleInputDialog', 'T', 'TagPickerDialog', 'UI_FONT_SIZE', '_TNode', '_dlg_geom', '_dlg_size', 'deque', 'make_search_label', 'note_swallowed', 'register_themed', 'text_color_for', 'theme_get']
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
                # ★★★ 一律包代理（错题本 #168）：
                #   模块的桩可能跑在**主程序还没定义这个名字**之前，
                #   所以「启动时取快照」必然借不到。
                #   ★ 代理是**读的时候才现取**，什么时候定义都不影响。
                g[_n] = _Borrowed(_n)
        except Exception:
            pass


class StarGraphEditor(tk.Toplevel):
    """层级式星图 v25（★ 补丁37 做了三件事）：

      · **GeoGebra 手感**：缩放时**字号和节点大小不变**，只改变标签之间的
        距离；「⤢ 摊开一点」按钮可以把现有布局按 1.25 倍摊开（可反复点）。
      · **上下游条**：窗口底部一整条显示选中标签的父级 / 子级，
        并且有两个按钮「＋ 加父级标签…／＋ 加子级标签…」（点进去可勾选、
        可搜索、可滚轮）。
      · **标签宽度按各自字数**：不再所有标签都跟最长的那个一样宽。
    """

    NODE_PAD_X = 12
    NODE_PAD_Y = 6
    # ★ v25 补丁40：用户要「像 GeoGebra 那样能无限放大缩小画布」。
    #   原来只允许 30% ~ 250%，稍微拉两下就到头了。
    #   ★★ v25 补丁42：用户说「缩放限制还是不够大，不能放大到特别大，
    #      我希望可以是无限的」。
    #      这里说明一下为什么做不到**真无限**，以及我是怎么尽量做大的：
    #        · Tk 画布的坐标是有限精度的（内部是 32 位浮点），
    #          世界坐标 × 缩放倍数如果超过 10^7 左右，坐标就会溢出、
    #          线条乱飞甚至不画出来 —— 那不是「无限」，那是坏掉。
    #        · 所以正确做法是「**按当前画布内容动态算一个安全上限**」：
    #          内容最远只铺到多少世界坐标，就用它反推「还能放多大」。
    #          这样就等于「只要还画得下，就能一直放大」。
    #      下面这两个常量只是**兜底的硬边界**（动态上限算不出来时才用）：
    #        MIN 0.05 → 0.01（能缩到 1%，差不多是「整棵树尽收眼底」）
    #        MAX 8.0  → 100.0（能放大 100 倍，配合动态上限可到几百倍）
    MIN_SCALE = 0.01
    MAX_SCALE = 100.0
    # Tk 画布坐标的安全上界（留足余量，实测 1e7 左右开始出问题）
    SAFE_COORD = 2.0e6
    DEFAULT_EDGE_COLOR = "#b8c2d6"
    MAX_HISTORY = 50

    # ★★ 2026-10-07 新增：**按层级给连线配色 + 粗细**。
    #   用户报：「上下游标签的颜色不够丰富，然后上级和下级标签之间
    #   没有分割线帮助强调视觉区别」。
    #   ★ 原来所有连线都是同一个 `DEFAULT_EDGE_COLOR` —— 看不出第几层。
    #   ★ 现在：(颜色, 线粗) 按层循环取用，越往下越深越粗。
    #     颜色挑的都是**中间调** —— 深浅两套皮肤都看得清（跟图标一个思路）。
    EDGE_PALETTE = [
        ("#7fa8d8", 1.4),      # 第 1 层：浅蓝
        ("#8f7fd8", 1.7),      # 第 2 层：浅紫
        ("#d88f7f", 2.0),      # 第 3 层：浅橙
        ("#7fd8a8", 2.3),      # 第 4 层：浅绿
        ("#d8c07f", 2.6),      # 第 5 层：浅金
        ("#c07fd8", 2.9),      # 第 6 层：浅紫红
    ]
    # 层数徽章开关（默认开）
    _show_depth_badge = True

    def __init__(self, master, store, on_saved=None, app=None):
        super().__init__(master)
        self.title("标签星图")
        self.geometry(_dlg_geom(1240, 800))
        self.minsize(*_dlg_size(760, 500, minimum=(760, 500)))
        self.resizable(True, True)
        self.store = store
        self.on_saved = on_saved
        # ★ v25 补丁42：主程序引用（用来找「标签盒」——
        #   实现 Shift+拖 / 右键「放进标签盒」）
        self.app = app
        # Shift 拖进标签盒用的状态
        self._shift_box_drag = False
        self._shift_box_started = False
        self._press_xroot = 0
        self._press_yroot = 0
        self.saved = False
        self.propagated = None
        self.dirty = False

        self.nodes = {}
        self.edges = set()
        self.drag_node = None
        self.hover_node = None
        self.selected_node = None
        self.selected_node_ids = set()

        # 视图
        self.scale = 1.0
        self._view_x = 0.0
        self._view_y = 0.0
        self._space_down = False
        self._pan_active = False
        self._pan_last = None

        self._drag_dx = 0
        self._drag_dy = 0
        self._ctrl_drag = False
        self._drag_offsets = {}    # ★ tid -> (dx, dy)：多选拖动时用
        # ★ v25 补丁37：GeoGebra 手感 —— 缩放时字号/节点大小不变，只拉开距离
        self.geo_font = True
        self._node_h = 26.0
        self._node_font_size = 10

        self._maximized = False
        self._normal_geometry = None
        self._topmost = False

        self.search_text = ""
        self._search_matches = set()
        # ★ 2026-10-07：搜索"当前跳到第几个" —— -1 表示还没跳过。
        #   （见 `_goto_next_match` 那一段说明）
        self._match_index = -1

        # 线颜色
        self.custom_line_colors = {}
        self.picker_mode = False
        self.picker_color = None
        self.hover_edge = None
        self.selected_edge = None      # (pid, cid) 或 None

        # 撤销 / 重做
        self._undo_stack = []
        self._redo_stack = []

        # 框选
        self._rect_selecting = False
        self._rect_start = None
        self._rect_id = None

        self._build_ui()
        self._reload()
        # 初始状态压入 undo 栈
        self._push_undo(silent=True)

        self.wait_window(self)

    def _build_ui(self):
        # ---------- 工具栏 ----------
        bar = ttk.Frame(self, padding=(10, 8, 10, 4))
        bar.pack(fill="x")
        ttk.Button(bar, text=T("＋ 新建根标签"),
                   command=self._new_root_tag).pack(side="left")
        ttk.Button(bar, text=T("＋ 新建子标签"),
                   command=self._new_child_tag).pack(side="left", padx=4)
        ttk.Button(bar, text=T("重命名"),
                   command=self._rename_selected).pack(side="left", padx=4)
        ttk.Button(bar, text=T("标签颜色"),
                   command=self._recolor_selected).pack(side="left", padx=4)
        ttk.Button(bar, text=T("删除"),
                   command=self._delete_selected).pack(side="left", padx=4)

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)

        # 对齐
        ttk.Button(bar, text=T("⇤ 左对齐"),
                   command=self._align_left).pack(side="left", padx=4)
        ttk.Button(bar, text=T("↔ 同一水平线"),
                   command=self._align_center_h).pack(side="left", padx=4)
        ttk.Button(bar, text=T("↕ 上下等距"),
                   command=self._space_vertically).pack(side="left", padx=4)

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)

        # 缩放
        ttk.Button(bar, text="🔍+", width=4,
                   command=lambda: self._zoom_at_center(1.15)).pack(side="left")
        ttk.Button(bar, text="🔍-", width=4,
                   command=lambda: self._zoom_at_center(1 / 1.15)).pack(side="left", padx=2)
        ttk.Button(bar, text=T("重置视图"),
                   command=self._reset_view).pack(side="left", padx=2)

        self._pin_btn = ttk.Button(bar, text=T("📌 置顶"), width=8,
                                   command=self._toggle_topmost)
        self._pin_btn.pack(side="left", padx=(8, 4))
        ttk.Button(bar, text=T("🖵 最大化"), width=8,
                   command=self._toggle_maximize).pack(side="left", padx=2)
        # ★ v25 补丁37：缩放时字号不变（GeoGebra 那种手感）/ 跟着变大变小
        self._geo_btn = ttk.Button(bar, text=T("🔒 字不变"), width=10,
                                   command=self._toggle_geo_font)
        self._geo_btn.pack(side="left", padx=2)
        ttk.Button(bar, text=T("⤢ 摊开一点"), width=10,
                   command=self._spread_distances).pack(side="left", padx=2)
        self.scale_lbl = ttk.Label(bar, text="100%")
        self.scale_lbl.pack(side="left", padx=6)

        # ---------- 线颜色行 ----------
        cbar = ttk.Frame(self, padding=(10, 0, 10, 4))
        cbar.pack(fill="x")
        ttk.Label(cbar, text=T("线颜色：")).pack(side="left")

        ttk.Button(cbar, text=T("🖌 给选中线改色"),
                   command=self._color_selected_edge).pack(side="left", padx=4)

        self._picker_btn = tk.Label(cbar, text=T("🎨 取色器"), padx=10, pady=2,
                                    font=(FONT, UI_FONT_SIZE), cursor="hand2",
                                    borderwidth=1, relief="solid",
                                    bg=theme_get("line"), fg=theme_get("fg_dim"),
                                    highlightbackground=theme_get("line"))
        self._picker_btn.pack(side="left", padx=(4, 6))
        self._picker_btn.bind("<Button-1>", lambda e: self._toggle_picker())

        self._picker_state_lbl = ttk.Label(
            cbar, text=T("（未开启）"), foreground=theme_get("fg_dim"))
        self._picker_state_lbl.pack(side="left", padx=4)

        ttk.Button(cbar, text=T("清除自定义线色"), width=14,
                   command=self._clear_all_custom_colors).pack(
            side="left", padx=(8, 0))

        # 显示当前选中线的状态
        self.edge_info_lbl = ttk.Label(cbar, text="",
                                       foreground=theme_get("fg_dim"))
        self.edge_info_lbl.pack(side="left", padx=8)

        # ---------- 搜索行 ----------
        sbar = ttk.Frame(self, padding=(10, 0, 10, 4))
        sbar.pack(fill="x")
        make_search_label(sbar, "搜索标签：").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(sbar, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True)
        # ★ 2026-10-07：回车 = **下一个**（跟缩略图那套一致）；
        #   ↓ / ↑ 也能翻。原来回车只是"跳到第一个"。
        self.search_entry.bind("<Return>", lambda e: self._goto_next_match())
        self.search_entry.bind("<Down>", lambda e: self._goto_next_match())
        self.search_entry.bind("<Up>", lambda e: self._goto_prev_match())
        self.search_var.trace_add("write", lambda *a: self._do_search())
        ttk.Button(sbar, text=T("清除"), width=6,
                   command=self._clear_search).pack(side="left", padx=(6, 0))
        # ★★ 2026-10-07 新增：**上一个 / 下一个 三角按钮**
        #   （用户报「标签星图上的搜索没有上下跳转三角按钮」）
        ttk.Button(sbar, text="▲", width=3,
                   command=self._goto_prev_match).pack(side="left", padx=(6, 0))
        ttk.Button(sbar, text="▼", width=3,
                   command=self._goto_next_match).pack(side="left", padx=(2, 0))
        # ★ 保留"跳转到第一个"（习惯用它的人还在）—— 放在三角按钮后面
        ttk.Button(sbar, text=T("第一个"), width=8,
                   command=self._goto_first_match).pack(side="left", padx=(6, 0))
        self.search_info_lbl = ttk.Label(sbar, text="", foreground=theme_get("ok"))
        self.search_info_lbl.pack(side="left", padx=8)

        # ---------- 提示 ----------
        hint = ttk.Label(
            self,
            text=T("拖动 A → B：B 成为 A 的父级（框选多个后整组拖过去 = 一次全挂上）"
                   "  |  Ctrl + 拖动 A → B：删除关系"
                   "  |  点空白处拖出方框：框选多个节点"
                   "  |  框选后拖动其中任何一个：整组一起移动"
                   "  |  点线：选中该线，然后用「给选中线改色」"
                   "  |  空格 + 拖动平移；Ctrl + 滚轮缩放。"),
            foreground=theme_get("fg_dim"), padding=(10, 0, 10, 4))
        hint.pack(fill="x")

        # ---------- 画布 ----------
        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True, padx=10, pady=(0, 4))

        # ★ v25 补丁37：底部「上下游标签」整条 —— 和主界面底部那条标签条
        #   一个位置、一种感觉（用户要求：不要窝在右下角小框里看不清）。
        rel = tk.Frame(self, bg=theme_get("panel_bg"), highlightthickness=1,
                       highlightbackground=theme_get("line"))
        try:
            register_themed(rel, "panel")   # ★ 常驻控件 → 换皮肤时跟着刷
        except Exception:
            pass
        rel.pack(side="bottom", fill="x", padx=10, pady=(0, 6))
        head = tk.Frame(rel, bg=theme_get("panel_bg"))
        try:
            register_themed(head, "panel")   # ★ 常驻控件 → 换皮肤时跟着刷
        except Exception:
            pass
        head.pack(fill="x", padx=8, pady=(5, 2))
        tk.Label(head, text=T("上下游标签："), bg=theme_get("panel_bg"), fg=theme_get("fg"),
                 font=(FONT, UI_FONT_SIZE, BOLD)).pack(side="left")
        self.relation_lbl = tk.Label(head, text="（在星图上点一个标签，"
                                                "这里就显示它的上下游）",
                                     bg=theme_get("panel_bg"), fg=theme_get("fg_dim"),
                                     font=(FONT, UI_FONT_SIZE), anchor="w", justify="left")
        self.relation_lbl.pack(side="left", padx=(4, 10))
        self._rel_up_btn = ttk.Button(head, text=T("＋ 加父级标签…"), width=14,
                                      command=lambda: self._pick_relation("up"))
        self._rel_up_btn.pack(side="right")
        self._rel_down_btn = ttk.Button(head, text=T("＋ 加子级标签…"), width=14,
                                        command=lambda: self._pick_relation("down"))
        self._rel_down_btn.pack(side="right", padx=4)
        # ★ v25 补丁42：用户要的「去除上下游关系」功能。
        #   点一下 → 每个上下游标签前面多出一个复选框 →
        #   勾好点「确定去除」→ 弹窗问「是否确认去除这些关系？」→ 确认才真删。
        self._rel_del_btn = ttk.Button(head, text=T("✂ 去除关系…"), width=12,
                                       command=self._toggle_relation_remove)
        self._rel_del_btn.pack(side="right", padx=4)
        # 「去除模式」开着的时候，下半行换成「☑ 标签 + 确定/取消」
        self._rel_removing = False
        self._rel_checked = set()       # 勾中的 (pid, cid) 关系对
        self._rel_ok_btn = None
        self._rel_cancel_btn = None
        # 下面一行：把父级 / 子级直接列出来（标签多了会自动换行）
        self.rel_tags = tk.Frame(rel, bg=theme_get("panel_bg"))
        try:
            register_themed(self.rel_tags, "panel")   # ★ 常驻控件 → 换皮肤时跟着刷
        except Exception:
            pass
        self.rel_tags.pack(fill="x", padx=8, pady=(0, 6))

        self.canvas = tk.Canvas(wrap, bg=theme_get("panel_bg2"), highlightthickness=1,
                                highlightbackground=theme_get("line"), takefocus=True)
        try:
            register_themed(self.canvas, "panel2")   # ★ 常驻控件 → 换皮肤时跟着刷
        except Exception:
            pass
        hsb = ttk.Scrollbar(wrap, orient="horizontal", command=self._on_xscroll)
        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self._on_yscroll)
        self.canvas.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)
        hsb.pack(side="bottom", fill="x")
        vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", self._on_mouse_wheel)
        self.canvas.bind("<Button-5>", self._on_mouse_wheel)
        self.canvas.bind("<Button-2>", self._on_middle_press)
        self.canvas.bind("<B2-Motion>", self._on_middle_motion)
        self.canvas.bind("<ButtonRelease-2>", self._on_middle_release)
        self.canvas.bind("<Double-1>", self._on_double)

        self.bind("<KeyPress-space>", self._on_space_down)
        self.bind("<KeyRelease-space>", self._on_space_up)
        self.bind("<KeyPress-plus>", lambda e: self._zoom_at_center(1.15))
        self.bind("<KeyPress-equal>", lambda e: self._zoom_at_center(1.15))
        self.bind("<KeyPress-minus>", lambda e: self._zoom_at_center(1 / 1.15))
        self.bind("<F11>", lambda e: self._toggle_maximize())
        self.bind("<Control-f>", lambda e: self.search_entry.focus_set())
        self.bind("<Control-t>", lambda e: self._toggle_topmost())
        self.bind("<Control-p>", lambda e: self._toggle_picker())
        self.bind("<Control-z>", lambda e: self._undo())
        self.bind("<Control-y>", lambda e: self._redo())
        self.bind("<Control-Shift-Z>", lambda e: self._redo())
        self.canvas.bind("<Control-MouseWheel>", self._on_ctrl_wheel)
        self.canvas.bind("<KeyPress-space>", self._on_space_down)
        self.canvas.bind("<KeyRelease-space>", self._on_space_up)

        # ---------- 底部按钮行 ----------
        btns = ttk.Frame(self, padding=(10, 4, 10, 10))
        btns.pack(fill="x")

        self.status_lbl = ttk.Label(btns, text="", foreground=theme_get("ok"))
        self.status_lbl.pack(side="left")

        self.undo_btn = ttk.Button(btns, text=T("↶ 撤销"), width=8,
                                   command=self._undo, state="disabled")
        self.undo_btn.pack(side="left", padx=(12, 2))
        self.redo_btn = ttk.Button(btns, text=T("↷ 恢复"), width=8,
                                   command=self._redo, state="disabled")
        self.redo_btn.pack(side="left", padx=2)

        # ★ 红底保存按钮
        self.save_btn = tk.Button(
            btns, text=T("💾 保存"), width=12,
            bg="#e74c3c", fg="white",
            activebackground="#c0392b", activeforeground="white",
            font=(FONT, UI_FONT_SIZE, BOLD), relief="raised", bd=2,
            cursor="hand2", command=self._save)
        self.save_btn.pack(side="right")

        ttk.Button(btns, text=T("关闭"), width=8,
                   command=self._cancel).pack(side="right", padx=6)

        self.protocol("WM_DELETE_WINDOW", self._on_window_close)
        self.canvas.focus_set()
            # ---------------- 置顶 / 最大化 ----------------
    def _toggle_topmost(self):
        self._topmost = not self._topmost
        try:
            self.attributes("-topmost", self._topmost)
        except Exception:
            pass
        try:
            self._pin_btn.config(
                text=("📌 已置顶" if self._topmost else "📌 置顶"))
        except Exception:
            pass

    def _toggle_maximize(self):
        if self._maximized:
            try:
                self.state('normal')
            except Exception:
                pass
            if self._normal_geometry:
                try:
                    self.geometry(self._normal_geometry)
                except Exception:
                    pass
            self._maximized = False
        else:
            try:
                self._normal_geometry = self.geometry()
            except Exception:
                self._normal_geometry = None
            ok = False
            try:
                self.state('zoomed')
                ok = True
            except tk.TclError:
                ok = False
            except Exception:
                ok = False
            if not ok:
                try:
                    w = self.winfo_screenwidth()
                    h = self.winfo_screenheight()
                    self.geometry(f"{w}x{h}+0+0")
                except Exception:
                    pass
            self._maximized = True

    # ---------------- 状态快照 / 撤销 / 重做 ----------------
    def _snapshot(self):
        positions = {}
        for tid, n in self.nodes.items():
            positions[tid] = (round(n.x, 1), round(n.y, 1))
        return {
            "positions": positions,
            "edges": set(self.edges),
            "custom_line_colors": dict(self.custom_line_colors),
        }

    def _push_undo(self, silent=False):
        try:
            snap = self._snapshot()
        except Exception:
            return
        # 避免连续两次相同快照
        if self._undo_stack:
            last = self._undo_stack[-1]
            if (last["positions"] == snap["positions"]
                    and last["edges"] == snap["edges"]
                    and last["custom_line_colors"] == snap["custom_line_colors"]):
                if not silent:
                    self._refresh_undo_redo_buttons()
                return
        self._undo_stack.append(snap)
        if len(self._undo_stack) > self.MAX_HISTORY:
            self._undo_stack.pop(0)
        self._redo_stack.clear()
        self._refresh_undo_redo_buttons()

    def _restore_snapshot(self, snap):
        if snap is None:
            return
        # 位置
        for tid, (x, y) in snap["positions"].items():
            n = self.nodes.get(tid)
            if n is not None:
                n.x = x
                n.y = y
        # 边
        self.edges = set(snap["edges"])
        for n in self.nodes.values():
            n.parents = []
            n.children = []
        for pid, cid in self.edges:
            p = self.nodes.get(pid)
            c = self.nodes.get(cid)
            if p is not None and c is not None:
                p.children.append(c)
                c.parents.append(p)
        # 线颜色
        self.custom_line_colors = dict(snap["custom_line_colors"])
        # 清掉选中（可能已经不存在）
        self.selected_node_ids = {t for t in self.selected_node_ids
                                  if t in self.nodes}
        if self.selected_node is not None and self.selected_node.tag_id not in self.nodes:
            self.selected_node = None
        if self.selected_edge is not None and self.selected_edge not in self.edges:
            self.selected_edge = None

    def _undo(self):
        if len(self._undo_stack) <= 1:
            return
        current = self._undo_stack.pop()
        self._redo_stack.append(current)
        target = self._undo_stack[-1]
        self._restore_snapshot(target)
        self.dirty = True
        self._update_edge_info_label()
        self._update_scrollregion()
        self._redraw()
        self._refresh_undo_redo_buttons()
        self.set_status_hint("已撤销")

    def _redo(self):
        if not self._redo_stack:
            return
        target = self._redo_stack.pop()
        self._undo_stack.append(target)
        self._restore_snapshot(target)
        self.dirty = True
        self._update_edge_info_label()
        self._update_scrollregion()
        self._redraw()
        self._refresh_undo_redo_buttons()
        self.set_status_hint("已恢复")

    def _refresh_undo_redo_buttons(self):
        try:
            if len(self._undo_stack) > 1:
                self.undo_btn.config(state="normal")
            else:
                self.undo_btn.config(state="disabled")
            if self._redo_stack:
                self.redo_btn.config(state="normal")
            else:
                self.redo_btn.config(state="disabled")
        except Exception:
            pass

    # ---------------- 搜索 ----------------
    def _do_search(self):
        q = (self.search_var.get() or "").strip().lower()
        self.search_text = q
        if not q:
            self._search_matches = set()
            self.search_info_lbl.config(text="")
            self._redraw()
            return
        matches = set()
        for n in self.nodes.values():
            if q in (n.name or "").lower():
                matches.add(n.tag_id)
        self._search_matches = matches
        # ★ 2026-10-07：搜索内容变了 → 把"当前跳到第几个"**重置**，
        #   否则改完搜索词还停在上一次的序号上（容易越界/跳得莫名其妙）。
        self._match_index = -1
        if matches:
            self.search_info_lbl.config(text=f"匹配 {len(matches)} 个")
        else:
            self.search_info_lbl.config(text=T("无匹配"))
        self._redraw()

    def _clear_search(self):
        self.search_var.set("")

    # ==================================================================
    #  ★★ 2026-10-07 新增：**上一个 / 下一个匹配**（用户报「标签星图上的
    #     搜索没有上下跳转三角按钮」）。
    #  ------------------------------------------------------------------
    #  ★ 为什么以前只有"跳转到第一个"：
    #    搜索行里只挂了 `_goto_first_match`，**没有"下一个"的概念** ——
    #    匹配到 8 个也只能看第 1 个，剩下 7 个没法翻。
    #  ★ 现在补齐：
    #    · `_match_order` —— 匹配到的标签**排好序**（按层级/顺序/名字），
    #      这样"下一个"的顺序**稳定**（不会每次跳的顺序都不一样）。
    #    · `_match_index` —— 当前在第几个。
    #    · ▲ = 上一个，▼ = 下一个（**循环**：最后一个再按回到第一个）。
    #    · 回车 = 下一个（跟缩略图那套一致）。
    #    · 右上角显示 `3/8`（第几个 / 共几个）。
    #  ★ 参考实现：`TagThumbnail` 里那套（那个已经做对了）。
    # ==================================================================
    def _search_match_order(self):
        """把当前匹配的标签**排好序**（层级 → 顺序 → 名字），返回 tag_id 列表。"""
        try:
            hits = [n for n in self.nodes.values()
                    if n.tag_id in (self._search_matches or set())]
            hits.sort(key=lambda x: (getattr(x, "depth", 0),
                                     getattr(x, "sort_order", 0),
                                     (x.name or "").lower()))
            return [n.tag_id for n in hits]
        except Exception:
            return []

    def _goto_next_match(self):
        """▼ 跳到**下一个**匹配（到末尾就绕回第一个）。"""
        order = self._search_match_order()
        if not order:
            return
        cur = getattr(self, "_match_index", -1)
        nxt = 0 if cur < 0 else (cur + 1) % len(order)
        self._goto_match_index(nxt)

    def _goto_prev_match(self):
        """▲ 跳到**上一个**匹配（到开头就绕到最后一个）。"""
        order = self._search_match_order()
        if not order:
            return
        cur = getattr(self, "_match_index", -1)
        prv = (len(order) - 1) if cur < 0 else (cur - 1) % len(order)
        self._goto_match_index(prv)

    def _goto_match_index(self, idx):
        """跳到第 idx 个匹配 —— 居中显示 + 更新 `3/8` 那个进度。"""
        order = self._search_match_order()
        if not order:
            return
        try:
            idx = max(0, min(len(order) - 1, int(idx)))
        except Exception:
            idx = 0
        self._match_index = idx
        target = self.nodes.get(order[idx])
        if target is None:
            return
        # ★ 复用本类已有的居中方法（`_center_on_node`），不重复实现
        self._center_on_node(target)
        try:
            self.search_info_lbl.config(
                text="%d/%d" % (idx + 1, len(order)))
        except Exception:
            pass

    def _goto_first_match(self):
        """跳到第一个匹配。

        ★ 2026-10-07：**改成走 `_goto_match_index(0)`** ——
          原来这里自己实现了一遍"居中"逻辑（40 行），
          而新的 ▲▼ 也要居中 → 复制两份迟早会改歪一处。
          现在只剩一份居中逻辑（`_center_on_node` + `_goto_match_index`）。
        """
        self._goto_match_index(0)

    # ---------------- 数据加载 ----------------
    def _reload(self, keep_positions=True):
        """从库里重建节点/关系。

        ★ v25 补丁：keep_positions=True（默认）时，先记下屏幕上现在的
          位置，重建后放回去 —— 否则「新建标签 / 连父子关系 / 改名 /
          改色」这些操作都会把还没点保存的布局冲回数据库里那套旧位置。
        """
        self.update_idletasks()
        keep = {}
        if keep_positions:
            for tid, n in (self.nodes or {}).items():
                try:
                    keep[tid] = (float(n.x), float(n.y))
                except Exception:
                    pass
        tags, relations = self.store.all_tags_with_relations()
        self.nodes = {}
        for tid, name, color, cnt, so in tags:
            self.nodes[tid] = _TNode(tid, name, color, cnt, so)
        for n in self.nodes.values():
            n.parents = []
            n.children = []
        self.edges = set()
        for pid, cid in relations:
            if pid in self.nodes and cid in self.nodes:
                self.edges.add((pid, cid))
                self.nodes[pid].children.append(self.nodes[cid])
                self.nodes[cid].parents.append(self.nodes[pid])

        # 清理已经不存在的线色
        self.custom_line_colors = {
            k: v for k, v in self.custom_line_colors.items() if k in self.edges
        }
        self._compute_sizes()

        # ★ 从数据库加载位置
        positions = self.store.get_all_tag_positions()
        self._apply_positions(positions)
        # ★ 再把「屏幕上原来的位置」盖回去（新标签才用库里的位置）
        for tid, (x, y) in keep.items():
            n = self.nodes.get(tid)
            if n is not None:
                n.x, n.y = x, y
        self._fallback_layout_missing()

        # ★ 从数据库加载线颜色
        try:
            saved_colors = self.store.get_all_edge_colors()
        except Exception:
            saved_colors = {}
        self.custom_line_colors = {
            k: v for k, v in saved_colors.items() if k in self.edges
        }

        self._update_scrollregion()
        self._update_edge_info_label()
        self._redraw()
        self._refresh_undo_redo_buttons()
        # ★ 窗口尺寸还没稳的时候，稍后再算一次
        self.after(50, self._update_scrollregion)
        self.after(200, self._update_scrollregion)

    def _apply_positions(self, positions):
        for tid, n in self.nodes.items():
            if tid in positions:
                x, y = positions[tid]
                n.x = float(x)
                n.y = float(y)

    def _fallback_layout_missing(self):
        """对没有保存过位置的节点，做"层级自动布局"。

        ★★ 2026-10-03：之前这里就是把一堆没位置的标签从 (30, 30) 起一排
          竖着堆 —— **完全没有 v21 公告里说的"无父级在最左列、越深越靠右"
          的层级自动布局**。结果就是新装 / 没拖过 / 第一次打开星图时，
          8 个标签全堆在 (200, 30~310) 那一坨，连线扭得跟毛线团一样。

          现在的算法（按"树状分层"）：
            1) 求每个节点的 depth（最长父级链 +1；无父级 = 0）；
            2) 按列（depth）从左到右铺，每列内按 sort_order、再按 name 排；
            3) 列内每个节点占"该列里之前所有节点里 max(y+h+gap) + row_gap"
               的位置 —— 简单但**保证不重叠**；
            4) 不强求父子水平对齐（做了反而划不清子树），用连线天然关联。
        """
        missing = [n for n in self.nodes.values()
                   if n.x == 0 and n.y == 0 and n.w > 0]
        if not missing:
            return

        # 已经被排进「有位置」集合的：以其右下角右侧 200 px 为 fallback 起点
        already = [n for n in self.nodes.values()
                   if not (n.x == 0 and n.y == 0) and n.w > 0]
        start_x = 60.0
        start_y = 60.0
        if already:
            start_x = max(n.x + n.w for n in already) + 200

        col_w = 200.0        # 列间距（世界坐标）
        row_gap = 16.0

        # 按 depth 分桶
        max_depth = 0
        buckets = {}
        for n in missing:
            d = int(n.depth)
            if d > max_depth:
                max_depth = d
            buckets.setdefault(d, []).append(n)
        # 每桶按 sort_order / name 升序
        for d in buckets:
            buckets[d].sort(key=lambda n: (n.sort_order, n.name.lower()))

        # 每列当前 y 游标（每列独立，避免重叠）
        y_cursor = {}        # depth -> y
        for d in range(max_depth + 1):
            y_cursor[d] = start_y

        for d in range(max_depth + 1):
            col_nodes = buckets.get(d) or []
            for n in col_nodes:
                n.x = start_x + d * col_w
                n.y = y_cursor[d]
                y_cursor[d] += n.h + row_gap

    def _compute_sizes(self):
        depth = {}
        roots = [n for n in self.nodes.values() if not n.parents]
        queue = deque()
        for r in roots:
            depth[r.tag_id] = 0
            queue.append(r)
        while queue:
            cur = queue.popleft()
            for c in cur.children:
                d = depth[cur.tag_id] + 1
                if c.tag_id not in depth or d > depth[c.tag_id]:
                    depth[c.tag_id] = d
                    queue.append(c)
        for n in self.nodes.values():
            if n.tag_id not in depth:
                depth[n.tag_id] = 0
        for n in self.nodes.values():
            n.depth = depth.get(n.tag_id, 0)
            # ★★ 2026-10-03：字号**统一**成 UI_FONT_SIZE（用户要求「每个有
            #   文字的地方都和右下角按钮一样大」）。以前是「越深的标签字越小」
            #   （16 → 9），看着一层比一层小、不匀称。
            fs = UI_FONT_SIZE
            n.font_size = fs
            f = tkfont.Font(family=FONT, size=fs, weight=BOLD)
            f2 = tkfont.Font(family=FONT, size=UI_FONT_SIZE)
            tw = f.measure(n.name)
            tw2 = f2.measure(f"  {n.count}")
            n.w = tw + tw2 + self.NODE_PAD_X * 2 + 16
            n.h = fs + self.NODE_PAD_Y * 2 + 6

    def _update_scrollregion(self):
        if not self.nodes:
            min_x, min_y = 0.0, 0.0
            max_x, max_y = 1000.0, 700.0
        else:
            min_x = min((n.x for n in self.nodes.values()), default=0.0)
            min_y = min((n.y for n in self.nodes.values()), default=0.0)
            max_x = max((n.x + n.w for n in self.nodes.values()), default=500.0)
            max_y = max((n.y + n.h for n in self.nodes.values()), default=400.0)
        # 四周留空白，同时保证原点 (0,0) 也在范围里
        min_x = min(0.0, min_x - 100.0)
        min_y = min(0.0, min_y - 100.0)
        max_x = max_x + 200.0
        max_y = max_y + 200.0
        self.canvas.configure(
            scrollregion=(min_x * self.scale, min_y * self.scale,
                          max_x * self.scale, max_y * self.scale))

    # ---------------- 视图/坐标 ----------------
    def _world_to_screen(self, wx, wy):
        # ★ 世界坐标 -> canvas 坐标。Tk 的 Canvas 会自动根据滚动位置
        #   做偏移绘制，所以这里只做缩放，绝不再减 _view_x / _view_y。
        return wx * self.scale, wy * self.scale

    def _screen_to_world(self, sx, sy):
        # ★ 传入的是 canvas 坐标（由 canvasx/canvasy 得到）
        return sx / self.scale, sy / self.scale

    def _on_xscroll(self, *args):
        self.canvas.xview(*args)
        self._view_x = self.canvas.canvasx(0)
        self._redraw()

    def _on_yscroll(self, *args):
        self.canvas.yview(*args)
        self._view_y = self.canvas.canvasy(0)
        self._redraw()

    def _reset_view(self):
        self.scale = 1.0
        self.scale_lbl.config(text="100%")
        self._update_scrollregion()
        try:
            self.canvas.xview_moveto(0)
            self.canvas.yview_moveto(0)
        except Exception:
            pass
        try:
            self.update_idletasks()
        except Exception:
            pass
        self._view_x = self.canvas.canvasx(0)
        self._view_y = self.canvas.canvasy(0)
        self._redraw()

    # ---------------- ★ v25 补丁37：GeoGebra 手感 / 上下游条 ----------------
    def _toggle_geo_font(self):
        """切换「缩放时字号不变」/「字号跟着缩放」。"""
        self.geo_font = not bool(getattr(self, "geo_font", True))
        try:
            self._geo_btn.config(
                text=("🔒 字不变" if self.geo_font else "🔍 字随缩放"))
        except Exception:
            pass
        self._redraw()
        self.set_status_hint("字体：%s" % (
            "缩放时不变（字看得清，只有距离在变）" if self.geo_font
            else "跟着缩放一起变大变小"))

    def _spread_distances(self):
        """把标签之间「摊开」一些（以整体中心为基准放大坐标，可反复点）。"""
        try:
            if not self.nodes:
                return
            xs = [n.x for n in self.nodes.values()]
            ys = [n.y for n in self.nodes.values()]
            cx = (min(xs) + max(xs)) / 2.0
            cy = (min(ys) + max(ys)) / 2.0
            for n in self.nodes.values():
                n.x = cx + (n.x - cx) * 1.25
                n.y = cy + (n.y - cy) * 1.25
            self.dirty = True
            self._update_scrollregion()
            self._redraw()
            self.set_status_hint("已把标签摊开 1.25 倍（可以反复点）")
        except Exception as exc:
            try:
                note_swallowed(T("摊开标签失败"), exc)
            except Exception:
                pass

    def _selected_tag_id(self):
        try:
            if len(self.selected_node_ids) == 1:
                return next(iter(self.selected_node_ids))
        except Exception:
            pass
        try:
            if self.selected_node is not None:
                return self.selected_node.tag_id
        except Exception:
            pass
        return None

    def _parents_children(self, tid):
        """★ v25 补丁40：改成显示**完整的上下游链**，不只一层。

        用户说「上下游标签没把所有上级标签显示出来」—— 原来这里只找
        「直接父级」（pid, tid）这一层的线，所以一个标签如果有爷爷、
        太爷爷，那些都看不见。现在改成：
          · 上游 = **所有祖先**（父 → 祖父 → 曾祖父…一路往上）；
          · 下游 = **所有后代**（子 → 孙 → 曾孙…一路往下）；
          · 每个都带上「隔了几层」，用缩进 / 角标区分远近。
        这样一眼就能看出这个标签在整个体系里的位置。
        """
        ups, downs = [], []

        def _walk(start, up=True):
            """广度优先往上/往下走，记下 (id, 名字, 层数)。"""
            seen = {start}
            out = []
            frontier = [(start, 0)]
            guard = 0
            while frontier and guard < 5000:
                guard += 1
                cur, depth = frontier.pop(0)
                for pid, cid in self.edges:
                    if up and cid == cur:
                        nxt = pid
                    elif (not up) and pid == cur:
                        nxt = cid
                    else:
                        continue
                    if nxt in seen:
                        continue          # 防环
                    seen.add(nxt)
                    n = self.nodes.get(nxt)
                    if n is not None:
                        out.append((nxt, n.name, depth + 1))
                        frontier.append((nxt, depth + 1))
            return out

        ups = _walk(tid, up=True)
        downs = _walk(tid, up=False)
        # 按「层数」排：近的在前
        ups.sort(key=lambda x: (x[2], x[1]))
        downs.sort(key=lambda x: (x[2], x[1]))
        return ups, downs

    def _refresh_relation_bar(self):
        """底部「上下游标签」条：换选中 / 改关系后都要刷一次。"""
        try:
            for w in self.rel_tags.winfo_children():
                w.destroy()
        except Exception:
            return
        # ★ 补丁42：「确定去除 / 全选」那排按钮也要跟着重建
        try:
            if getattr(self, "_rel_action_row", None) is not None:
                self._rel_action_row.destroy()
        except Exception:
            pass
        self._rel_action_row = None
        tid = self._selected_tag_id()
        if tid is None:
            n_sel = len(getattr(self, "selected_node_ids", ()) or ())
            self.relation_lbl.config(
                text=(T("已选中 {n} 个标签（选一个看它的上下游）",
                        n=n_sel)
                      if n_sel > 1 else
                      T("（在星图上点一个标签，这里就显示它的上下游）")))
            return
        node = self.nodes.get(tid)
        if node is None:
            return
        ups, downs = self._parents_children(tid)
        if getattr(self, "_rel_removing", False):
            self.relation_lbl.config(
                text=T("【{x}】勾选要去掉的上下游关系（勾好点下面「✔ 确定去除」）",
                       x=node.name))
        else:
            self.relation_lbl.config(
                text=T("【{a}】 上游（所有上级）{b} 个 · 下游（所有下级）{c} 个",
                       a=node.name, b=len(ups), c=len(downs)))
        self._rel_row("上级", ups, "#5b8def", direction="up")
        self._rel_row("下级", downs, "#e67e22", direction="down")
        self._update_rel_action_buttons()

    def _rel_row(self, label, items, color, direction="up"):
        """一条：『上级： [标签][标签]…』（标签多了自动换行）。

        ★ 补丁40：现在 items 里是 (id, 名字, 层数)。层数 >1 的会
        加上「·2层」这种小角标，一眼看出远近。

        ★ 补丁42：「去除关系」模式开着时，每个标签前面多一个复选框。
        """
        try:
            row = tk.Frame(self.rel_tags, bg=theme_get("panel_bg"))
            row.pack(fill="x", anchor="w", pady=1)
            tk.Label(row, text=label + "：", bg=theme_get("panel_bg"), fg=theme_get("fg_dim"),
                     font=(FONT, UI_FONT_SIZE, BOLD)).pack(side="left")
            if not items:
                tk.Label(row, text=T("（没有）"), bg=theme_get("panel_bg"), fg=theme_get("fg_dim"),
                         font=(FONT, UI_FONT_SIZE)).pack(side="left")
                return
            root_tid = self._selected_tag_id()
            for _i, item in enumerate(items[:60]):
                try:
                    tid, nm, depth = item[0], item[1], item[2]
                except Exception:      # 兼容老的两元组
                    tid, nm = item[0], item[1]
                    depth = 1
                lbl = " %s " % nm
                if depth > 1:
                    lbl = " %s ·%d层 " % (nm, depth)
                if self._rel_removing:
                    # 勾选模式：标签前面放复选框
                    #   关系对的方向：上级 = (对方, 我)；下级 = (我, 对方)
                    if direction == "up":
                        pair = (int(tid), int(root_tid))
                    else:
                        pair = (int(root_tid), int(tid))
                    var = tk.BooleanVar(value=(pair in self._rel_checked))

                    def _toggle(v=var, p=pair):
                        if v.get():
                            self._rel_checked.add(p)
                        else:
                            self._rel_checked.discard(p)
                    cb = tk.Checkbutton(
                        row, text=lbl, variable=var, command=_toggle,
                        bg=theme_get("panel_bg"), fg=theme_get("danger"),
                        activebackground=theme_get("panel_bg"),
                        font=(FONT, UI_FONT_SIZE), padx=2, pady=0,
                        selectcolor="white", cursor="hand2")
                    cb.pack(side="left", padx=2)
                else:
                    tag = tk.Label(row, text=lbl, bg=color, fg="white",
                                   font=(FONT, UI_FONT_SIZE), padx=4, pady=1,
                                   cursor="hand2")
                    tag.pack(side="left", padx=2)
                    tag.bind("<Button-1>",
                             lambda e, t=tid: self._focus_node(t))
            if len(items) > 60:
                tk.Label(row, text=T("…还有 {x} 个", x=len(items) - 60),
                         bg=theme_get("panel_bg"), fg=theme_get("fg_dim"),
                         font=(FONT, UI_FONT_SIZE)).pack(side="left", padx=4)
        except Exception:
            pass

    # ---------------- ★ v25 补丁42：去除上下游关系 ----------------
    def _toggle_relation_remove(self):
        """进入 / 退出「去除关系」模式（每个上下游标签前出现复选框）。"""
        tid = self._selected_tag_id()
        if tid is None:
            messagebox.showinfo("去除关系", "先在星图上点一个标签，"
                                            "再点这个按钮。", parent=self)
            return
        self._rel_removing = not bool(getattr(self, "_rel_removing", False))
        self._rel_checked = set()
        try:
            if self._rel_removing:
                self._rel_del_btn.configure(text=T("✕ 取消"))
                self.relation_lbl.config(
                    text=T("【勾选要去掉的关系】勾好点下面「✔ 确定去除」"))
            else:
                self._rel_del_btn.configure(text=T("✂ 去除关系…"))
        except Exception:
            pass
        self._refresh_relation_bar()
        self._update_rel_action_buttons()

    def _update_rel_action_buttons(self):
        """在 rel_tags 下面挂一排「确定去除 / 全选 / 取消」。"""
        try:
            if getattr(self, "_rel_action_row", None) is not None:
                self._rel_action_row.destroy()
        except Exception:
            pass
        self._rel_action_row = None
        if not self._rel_removing:
            return
        try:
            row = tk.Frame(self.rel_tags.master, bg=theme_get("panel_bg"))
            row.pack(fill="x", padx=8, pady=(0, 6))
            self._rel_action_row = row
            ttk.Button(row, text=T("✔ 确定去除"), width=12,
                       command=self._confirm_remove_relations).pack(side="left")
            ttk.Button(row, text=T("全选"), width=6,
                       command=lambda: self._check_all_relations(True)
                       ).pack(side="left", padx=4)
            ttk.Button(row, text=T("全不选"), width=8,
                       command=lambda: self._check_all_relations(False)
                       ).pack(side="left", padx=4)
            ttk.Button(row, text=T("✕ 取消"), width=8,
                       command=self._toggle_relation_remove
                       ).pack(side="left", padx=4)
            tk.Label(row, text=T("（去完关系记得点上面的「💾 保存」）"),
                     bg=theme_get("panel_bg"), fg=theme_get("fg_dim"),
                     font=(FONT, UI_FONT_SIZE)).pack(side="left", padx=8)
        except Exception:
            pass

    def _check_all_relations(self, on):
        """全部勾上 / 全部取消勾选。"""
        tid = self._selected_tag_id()
        if tid is None:
            return
        ups, downs = self._parents_children(tid)
        if on:
            self._rel_checked = set()
            for (t, _n, _d) in ups:
                self._rel_checked.add((int(t), int(tid)))
            for (t, _n, _d) in downs:
                self._rel_checked.add((int(tid), int(t)))
        else:
            self._rel_checked = set()
        self._refresh_relation_bar()
        self._update_rel_action_buttons()

    def _confirm_remove_relations(self):
        """点「确定去除」→ 弹窗确认 → 真删。"""
        pairs = set(getattr(self, "_rel_checked", set()) or set())
        if not pairs:
            messagebox.showinfo("去除关系", T("还没有勾选任何标签。"), parent=self)
            return
        tid = self._selected_tag_id()
        node = self.nodes.get(tid) if tid is not None else None
        me = node.name if node else "?"
        names = []
        for (p, c) in sorted(pairs):
            pn = self.nodes.get(p)
            cn = self.nodes.get(c)
            names.append("%s → %s" % (pn.name if pn else p,
                                      cn.name if cn else c))
        # ★ 用户要的确认弹窗
        msg = ("确定要**去除**下面这些上下游关系吗？\n\n"
               + "\n".join("  · " + n for n in names[:20])
               + (("\n  …还有 %d 条" % (len(names) - 20))
                  if len(names) > 20 else "")
               + "\n\n★ 只是去掉「【%s】和它们之间的父子关系」，\n"
                 "  标签本身和文件上的标签都不受影响。\n"
                 "★ 去掉之后要点上面的「💾 保存」才会真正生效。" % me)
        if not messagebox.askyesno("确认去除关系", msg, parent=self,
                                   default="no"):
            return
        ok = 0
        fail = []
        for (pid, cid) in pairs:
            try:
                self.store.remove_tag_relation(int(pid), int(cid))
                self.edges.discard((int(pid), int(cid)))
                ok += 1
            except Exception as exc:
                fail.append("%s→%s: %s" % (pid, cid, exc))
        # 关系变了 → 重画 + 收掉「去除模式」
        self.dirty = True
        self._rel_removing = False
        self._rel_checked = set()
        try:
            self._rel_del_btn.configure(text=T("✂ 去除关系…"))
        except Exception:
            pass
        self._update_rel_action_buttons()
        self._update_scrollregion()
        self._redraw()
        self._refresh_relation_bar()
        self._update_rel_action_buttons()
        self.set_status_hint("已去除 %d 条关系%s —— 记得点「💾 保存」"
                             % (ok, ("，%d 条失败" % len(fail)) if fail else ""))
        if fail:
            messagebox.showwarning("部分失败", "\n".join(fail[:8]), parent=self)

    def _put_into_tagbox(self, node):
        """★ v25 补丁42：把星图上的一个标签放进「标签盒」。

        用户要「从标签星图直接拖拽标签到标签盒」——
        拖的入口是 **Shift + 拖**（见 _on_press），这里给一个菜单版的，
        不用拖也能放进去。
        盒子没开着的话，顺手帮你打开。
        """
        try:
            if node is None:
                return
            app = getattr(self, "app", None)
            if app is None:
                messagebox.showinfo(
                    "标签盒", "没能找到主窗口（这个星图不是从主程序打开的）。",
                    parent=self)
                return
            tb = getattr(app, "tagbox", None)
            if tb is None:
                messagebox.showinfo(
                    "标签盒", "标签盒还没初始化好，关掉星图重开一次程序试试。",
                    parent=self)
                return
            # 盒子没显示 → 先帮你打开
            try:
                if not getattr(app, "tagbox_visible", False):
                    app.toggle_tagbox()
            except Exception:
                pass
            tb.add_tag(node.tag_id, node.name)
            self.set_status_hint("已把「%s」放进标签盒" % node.name)
        except Exception as exc:
            try:
                messagebox.showwarning("标签盒", "放进去失败了：%s" % exc,
                                       parent=self)
            except Exception:
                pass

    def _focus_node(self, tid):
        """把某个标签挪到视野中央（点上下游标签时用）。"""
        try:
            n = self.nodes.get(tid)
            if n is None:
                return
            self.selected_node_ids = {tid}
            self.selected_node = n
            self._center_on_node(n)
            self._redraw()
        except Exception:
            pass

    def _center_on_node(self, node):
        try:
            cw = max(1, self.canvas.winfo_width())
            ch = max(1, self.canvas.winfo_height())
            region = [float(x) for x in
                      str(self.canvas.cget("scrollregion")).split()]
            x0, y0, x1, y1 = region
            W = max(1.0, x1 - x0)
            H = max(1.0, y1 - y0)
            vcx = (node.x + node.w / 2) * self.scale - cw / 2
            vcy = (node.y + node.h / 2) * self.scale - ch / 2
            self.canvas.xview_moveto(max(0.0, min(1.0, (vcx - x0) / W)))
            self.canvas.yview_moveto(max(0.0, min(1.0, (vcy - y0) / H)))
        except Exception:
            pass

    def _pick_relation(self, mode):
        """「＋ 加父级标签… / ＋ 加子级标签…」按钮。"""
        tid = self._selected_tag_id()
        if tid is None:
            messagebox.showinfo(
                "提示", "先在星图上点一个标签，再用这两个按钮给它加"
                        "父级 / 子级。", parent=self)
            return
        node = self.nodes.get(tid)
        if node is None:
            return
        try:
            # ★ v25 补丁38（bug 修复）：这里原来调的是 `TagPickDialog` ——
            #   程序里**根本没有这个类**（真名是 TagPickerDialog，而且
            #   老版本只支持单选、只返回一个标签名字）。所以按「＋ 加父级/
            #   子级标签…」永远只会弹一句「打不开勾选窗口」，功能是废的。
            #   现在改成：真的那个窗口 + 多选模式 + 排除自己/祖先/后代。
            try:
                _all = self.store.all_tags()
            except Exception:
                _all = []
            # 不能选：自己 + 自己的祖先（加父级时防成环）
            _ex = {tid} | set(self._ancestors_of(tid))
            if mode == "down":
                # 加子级时，自己的后代也不能选（同样会成环）
                try:
                    _ex |= set(self._descendants_of(tid))
                except Exception:
                    pass
            dlg = TagPickerDialog(
                self, _all, current="",
                multi=True, exclude_ids=_ex,
                title=("给「%s」加父级标签" % node.name if mode == "up"
                       else "给「%s」加子级标签" % node.name))
            ids = dlg.result or []
        except Exception as exc:
            try:
                messagebox.showerror("打不开勾选窗口", str(exc), parent=self)
            except Exception:
                pass
            return
        if not ids:
            return
        n = 0
        for other in ids:
            try:
                if mode == "up":
                    self.store.add_tag_relation(other, tid)
                else:
                    self.store.add_tag_relation(tid, other)
                n += 1
            except Exception as exc:
                try:
                    note_swallowed(T("加标签关系失败"), exc)
                except Exception:
                    pass
        if n:
            self.dirty = True
            self._reload()
            self._push_undo()
            self.set_status_hint("已加 %d 个%s标签（关系线已画到星图上）"
                                 % (n, "父级" if mode == "up" else "子级"))

    def _ancestors_of(self, tid):
        """往上找所有祖先（加父级时避开，免得接出环）。"""
        out = set()
        stack = [tid]
        while stack:
            cur = stack.pop()
            for pid, cid in self.edges:
                if cid == cur and pid not in out:
                    out.add(pid)
                    stack.append(pid)
        return out

    def _descendants_of(self, tid):
        """★ v25 补丁38：往下找所有后代（加子级时避开，免得接出环）。

        （原来只有 _ancestors_of，加子级那一边没做防环检查 ——
          这会让「给 A 加子级 B」里的 B 有可能选到 A 自己的后代，
          接出一个环，星图上那条线就来回绕。）
        """
        out = set()
        stack = [tid]
        while stack:
            cur = stack.pop()
            for pid, cid in self.edges:
                if pid == cur and cid not in out:
                    out.add(cid)
                    stack.append(cid)
        return out

    # ---------------- 绘制 ----------------
    def _redraw(self):
        c = self.canvas
        c.delete("all")
        self._node_boxes = getattr(self, "_node_boxes", [])
        self._node_boxes = []
        s = self.scale

        # ★ v25 补丁40：线条的毛病修一下。
        #   原来每根线的「弯曲控制点」用的是 max(30.0, 水平距离*0.45) ——
        #   那个 30 是**屏幕像素**、而且是**最小**值，不是跟着缩放走的。
        #   后果：缩小到 30% 的时候，两个标签在屏幕上只隔十几像素，
        #   控制点却硬要往外推 30 像素 —— 线就变成了来回乱扭的怪线
        #   （用户说的「线条看着不太对」就是这个）。
        #   现在：
        #     · 弯曲量按「两点的实际水平距离」算（不设像素下限，
        #       但按缩放后的距离给一个合理比例）；
        #     · 两点离得很近时直接画直线（省得扭来扭去）；
        #     · 线宽也保证至少 1.5 像素，缩小了也看得见。
        # ★ v25 补丁41：连线必须和「节点实际画出来的样子」对齐。
        #   之前这里用的是 n.x / n.w / n.h（**世界坐标**，会随缩放放大缩小），
        #   但节点本身在「星图手感」模式下是**屏幕尺寸固定**的
        #   （见下面 _redraw 里 geo 那段：h = self._node_h，宽度按字数重算）。
        #   两套尺寸对不上，后果就是：
        #     · 刚打开（100%）时线头线尾刚好贴着方块，看着没问题；
        #     · 一缩放，方块在屏幕上没变小，线却跟着世界坐标一起缩，
        #       于是线头缩进方块里/飘到方块外面 —— 用户说的
        #       「线条只适配刚打开时的效果」就是这个。
        #   现在：连线的端点按**节点在屏幕上的真实方块**来算，
        #   缩放多少都和方块严丝合缝。
        def _node_screen_box(n, geo):
            """节点在屏幕上的真实方块 (x, y, w, h)。"""
            x, y = self._world_to_screen(n.x, n.y)
            if geo:
                h = self._node_h
                # 和 _redraw 里算 w 的公式**必须一模一样**
                w = max(70.0, n.w * (h / max(n.h, 1.0)))
            else:
                w, h = n.w * s, n.h * s
            return x, y, w, h

        def _edge_points(pa, pb):
            """算出「从 pa 右边连到 pb 左边」那条曲线的 4 个点（屏幕坐标）。"""
            geo_now = bool(getattr(self, "geo_font", True))
            ax, ay, aw, ah = _node_screen_box(pa, geo_now)
            bx, by, bw, bh = _node_screen_box(pb, geo_now)
            # 起点 = pa 方块右边中点；终点 = pb 方块左边中点
            ax = ax + aw
            ay = ay + ah / 2
            by = by + bh / 2
            dx = bx - ax
            dy = by - ay
            span = (dx * dx + dy * dy) ** 0.5
            # 离得近 → 直线（不然会扭）
            if span < 24:
                return ax, ay, ax + dx / 3, ay, ax + dx * 2 / 3, by, bx, by
            # ★ 补丁41：弯曲量完全按两点的实际距离来定，
            #   **不再有 6 像素这个固定下限**（它就是「缩小后线条乱扭」的元凶：
            #   缩到 5% 时两点在屏幕上只隔几像素，控制点却硬要往外推 6 像素）。
            #   距离太近的情况上面已经走直线分支了，这里按比例给就够。
            bend = min(abs(dx) * 0.45, span * 0.5)
            bend = max(bend, span * 0.15)
            return (ax, ay, ax + bend, ay, bx - bend, by, bx, by)

        # 1) 热区线（透明但可点击）
        for (pid, cid) in self.edges:
            p = self.nodes.get(pid)
            ch = self.nodes.get(cid)
            if p is None or ch is None:
                continue
            x1, y1, cx1, cy1, cx2, cy2, x2, y2 = _edge_points(p, ch)
            hot = c.create_line(x1, y1, cx1, cy1, cx2, cy2, x2, y2,
                                fill=theme_get("panel_bg2"),
                                width=max(10, 12 * s),
                                smooth=True,
                                capstyle="round")
            c.tag_bind(hot, "<Button-1>",
                       lambda e, p=pid, c_=cid: self._on_edge_left_click(p, c_))
            c.tag_bind(hot, "<Button-3>",
                       lambda e, p=pid, c_=cid: self._on_edge_right(e, p, c_))
            c.tag_bind(hot, "<Enter>",
                       lambda e, p=pid, c_=cid: self._on_edge_enter(p, c_))
            c.tag_bind(hot, "<Leave>",
                       lambda e, p=pid, c_=cid: self._on_edge_leave(p, c_))

        # 2) 可见线
        for (pid, cid) in self.edges:
            p = self.nodes.get(pid)
            ch = self.nodes.get(cid)
            if p is None or ch is None:
                continue
            x1, y1, cx1, cy1, cx2, cy2, x2, y2 = _edge_points(p, ch)

            color = self._get_edge_color(pid, cid)
            # ★ 2026-10-07：线宽**按层级**取（原来写死 1.8）——
            #   跟颜色配套，越深的层越粗，"层级感"一眼就有。
            #   （见 `_get_edge_width` 的说明）
            width_px = self._get_edge_width(pid, cid)
            if self.hover_edge == (pid, cid):
                width_px = 3.2
            if self.selected_edge == (pid, cid):
                color = "#f39c12"
                width_px = 4.0
            if self.picker_mode and self.picker_color is None \
                    and self.hover_edge == (pid, cid):
                color = "#e67e22"

            if self.search_text:
                pid_match = pid in self._search_matches
                cid_match = cid in self._search_matches
                if not (pid_match or cid_match):
                    color = theme_get("line")

            # ★ 补丁40：线宽下限从 1 提到 1.5（缩小后线不会细到看不见）
            c.create_line(x1, y1, cx1, cy1, cx2, cy2, x2, y2,
                          fill=color, width=max(1.5, width_px * s),
                          smooth=True, arrow="last",
                          arrowshape=(10 * s, 12 * s, 4 * s))

        # 3) 节点
        #   ★ 补丁37：**GeoGebra 手感** —— 缩放时字号和节点高度不变，
        #     变的只有标签之间的距离；宽度按**各自的字数**算
        #     （不再所有标签都跟最长的那个一样宽）。
        geo = bool(getattr(self, "geo_font", True))
        for n in self.nodes.values():
            # ★ 补丁41：这里改用 _node_screen_box()，和上面算连线端点的是
            #   **同一个函数** —— 以后谁改了尺寸公式都不会再出现
            #   「方块和线对不上」。
            x, y, w, h = _node_screen_box(n, geo)
            if geo:
                fs = self._node_font_size
            else:
                fs = max(7, int(n.font_size * s))
            selected = (n.tag_id in self.selected_node_ids
                        or self.selected_node is n)
            hover = (self.hover_node is n)
            is_match = (n.tag_id in self._search_matches)
            faded = bool(self.search_text) and not is_match

            c.create_rectangle(x + 3, y + 3, x + w + 3, y + h + 3,
                               fill=theme_get("line"), outline="")

            # ★★ 2026-10-07 修「选中框颜色不够亮，夜间看不清自己选的是哪个」
            #   （用户报的）。
            #   **原来**：`outline = "#2c3e50"` —— 一个**写死的深蓝黑**。
            #   浅色底上勉强看得见；**夜间模式（深底）上几乎跟背景糊在一起**，
            #   所以用户"看不清自己选的是什么"。
            #   ★ 而且它是**写死的** —— 切皮肤也不会跟着变
            #     （这跟错题本 #70 的 "rowheight 写死 22" 是同一类毛病）。
            #   **现在**：改用主题里的 `accent`，夜间是亮蓝 #7aa7e8，看得清；
            #   并且**加粗到 4 像素** + 描一圈亮边，保证任何底色上都挑得出来。
            if selected:
                outline = theme_get("accent")
            elif is_match:
                outline = theme_get("warn")
            elif hover:
                outline = theme_get("accent")
            else:
                outline = theme_get("card_bg")
            width = 4 if selected else (3 if is_match else 2)
            if not geo:
                width = max(2, width * s)
            fill_color = n.color
            if faded:
                fill_color = self._fade_color(n.color)
            c.create_rectangle(x, y, x + w, y + h,
                               fill=fill_color, outline=outline, width=width)
            fg = text_color_for(fill_color)
            pad = 12 if geo else self.NODE_PAD_X * s
            c.create_text(x + pad, y + h / 2, text=n.name,
                          anchor="w", fill=fg,
                          font=(FONT, fs, BOLD))
            c.create_text(x + w - (10 if geo else 10 * s), y + h / 2,
                          text=str(n.count),
                          anchor="e", fill=fg,
                          font=(FONT, max(7, fs - 2)))
            self._node_boxes.append((x, y, x + w, y + h,
                                     n.tag_id, n.name, n.color))

        # 4) 框选矩形
        if self._rect_selecting and self._rect_id is not None:
            pass  # 已经在拖动时绘制

        # 5) 底部「上下游标签」条（选中变了就刷新）
        try:
            self._refresh_relation_bar()
        except Exception:
            pass

    @staticmethod
    def _fade_color(hex_color, factor=0.65):
        try:
            h = hex_color.lstrip("#")
            r = int(h[0:2], 16)
            g = int(h[2:4], 16)
            b = int(h[4:6], 16)
            r = int(r + (255 - r) * factor)
            g = int(g + (255 - g) * factor)
            b = int(b + (255 - b) * factor)
            return "#%02x%02x%02x" % (r, g, b)
        except Exception:
            return theme_get("line")

    def _get_edge_color(self, pid, cid):
        """★ 取一条连线的颜色。

        ★★ 2026-10-07 修（用户报「上下游标签的颜色不够丰富，
           上级和下级标签之间没有分割线帮助强调视觉区别」）：
          原来**没手动染过色的线一律返回 `DEFAULT_EDGE_COLOR`** ——
          也就是**所有线同一个颜色**，光看线**完全分不出是第几层**。
          ★ 现在：按**父节点的层级**从 `EDGE_PALETTE` 取色 ——
            第 1 层一种、第 2 层一种……越往下越深（粗细由 `_edge_width` 管）。
          ★ 手动染过色的**优先用手动色**（那是用户自己挑的，不能盖掉）。
        """
        if (pid, cid) in self.custom_line_colors:
            return self.custom_line_colors[(pid, cid)]
        # 按"父节点在第几层"取色
        try:
            p = self.nodes.get(pid)
            d = int(getattr(p, "depth", 0) or 0)
            if d < 0:
                d = 0
            pal = self.EDGE_PALETTE
            return pal[d % len(pal)][0]
        except Exception:
            return self.DEFAULT_EDGE_COLOR

    def _get_edge_width(self, pid, cid):
        """★ 这条线该多粗 —— 跟颜色配套（越深的层越粗，层级感更强）。

        ★ 手动染过色的线**保持原来的粗细**（1.4），别跟着层数变 ——
          不然用户染了色之后线突然变粗，会以为出问题了。
        """
        if (pid, cid) in self.custom_line_colors:
            return 1.4
        try:
            p = self.nodes.get(pid)
            d = int(getattr(p, "depth", 0) or 0)
            if d < 0:
                d = 0
            pal = self.EDGE_PALETTE
            return pal[d % len(pal)][1]
        except Exception:
            return 1.4

    def _node_at_world(self, wx, wy, exclude=None):
        # ★ v25 补丁：exclude 可以是一个节点，也可以是一组节点
        #   （整组拖动时，别把组里别的成员当成落点）
        skip = set()
        if exclude is not None:
            if isinstance(exclude, (set, list, tuple)):
                skip = set(exclude)
            else:
                skip = {exclude}
        # 反向遍历：后添加 / 后画的（新建的）节点优先命中
        for n in reversed(list(self.nodes.values())):
            if n in skip:
                continue
            if n.x <= wx <= n.x + n.w and n.y <= wy <= n.y + n.h:
                return n
        return None

    def _drag_group(self, dragged):
        """★ v25 补丁：这一拖实际会动 / 会被挂过去的标签组。

        点的是选中集里的一个 → 整组；否则只有它自己。
        """
        out = []
        if dragged is None:
            return out
        if (len(self.selected_node_ids) > 1
                and dragged.tag_id in self.selected_node_ids):
            for tid in self.selected_node_ids:
                n = self.nodes.get(tid)
                if n is not None:
                    out.append(n)
        if dragged not in out:
            out = [dragged] + out
        return out

    def _drop_target(self, dragged, group=None):
        """★ v25 补丁：松手时会压在哪个标签上。

        整组拖动时，组里任何一个标签的中心压到别人身上都算 ——
        这样把一堆标签拖到某个父级上，就能一次全挂上去。
        """
        group = self._drag_group(dragged) if group is None else group
        cand = [dragged] + [n for n in group if n is not dragged]
        for c in cand:
            if c is None:
                continue
            t = self._node_at_world(c.x + c.w / 2, c.y + c.h / 2,
                                    exclude=group)
            if t is not None:
                return t
        return None

    def _node_at_screen(self, sx, sy, exclude=None):
        wx, wy = self._screen_to_world(sx, sy)
        return self._node_at_world(wx, wy, exclude=exclude)

    def _viewport_center_world(self):
        """当前视口中心对应的世界坐标（新建节点时定位在屏幕正中央）。"""
        try:
            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()
        except Exception:
            cw, ch = 0, 0
        if cw <= 1:
            cw = 800
        if ch <= 1:
            ch = 600
        cx = self.canvas.canvasx(cw // 2)
        cy = self.canvas.canvasy(ch // 2)
        return cx / self.scale, cy / self.scale

    # ---------------- 滚轮/平移 ----------------
    def _on_mouse_wheel(self, event):
        if event.state & 0x0004:
            factor = 1.15 if (event.delta > 0 or event.num == 4) else (1 / 1.15)
            self._zoom_at(event.x, event.y, factor)
            return "break"
        if event.num == 4:
            d = -3
        elif event.num == 5:
            d = 3
        else:
            d = -3 if event.delta > 0 else 3
        self.canvas.yview_scroll(d, "units")
        self._view_y = self.canvas.canvasy(0)
        self._redraw()

    def _on_ctrl_wheel(self, event):
        factor = 1.15 if event.delta > 0 else (1 / 1.15)
        self._zoom_at(event.x, event.y, factor)
        return "break"

    def _zoom_at_center(self, factor):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        self._zoom_at(w // 2, h // 2, factor)

    def _max_scale_now(self):
        """★ v25 补丁42：**按当前内容算一个「还画得下」的最大缩放**。

        用户要「无限放大」。真无限做不到（Tk 画布坐标是有限精度的，
        世界坐标 × 缩放超过约 10^7 就会溢出、线条乱飞）。
        但可以做到「**只要内容还画得下，就一直能放大**」：
          内容最远的那个点的世界坐标有多大 → 乘多少倍会碰到安全上限
          → 那个倍数就是现在能放的最大倍数。

        结果和 MAX_SCALE 取小的那个（MAX_SCALE 是兜底硬边界）。
        """
        try:
            span = 0.0
            for n in self.nodes.values():
                span = max(span, abs(float(n.x)) + abs(float(n.w)),
                           abs(float(n.y)) + abs(float(n.h)))
            if span <= 1.0:
                return self.MAX_SCALE            # 内容还没铺开，直接用硬边界
            limit = self.SAFE_COORD / span
            # ★ 至少允许放大 50 倍。为什么要这个下限：
            #   就算内容铺得很开（比如整棵树横跨 50 万单位），
            #   你也还是想「凑近看某一个小角落」—— 缩放到 50 倍的时候
            #   最远的那个点会碰到画布安全边界，但**你看的那一小块**
            #   完全没问题（Tk 是只画可见部分的）。
            return max(50.0, min(self.MAX_SCALE, limit))
        except Exception:
            return self.MAX_SCALE

    def _zoom_at(self, sx, sy, factor):
        # ★ v25 补丁42：上限改成**动态**的（见 _max_scale_now）。
        _hi = self._max_scale_now()
        new_scale = max(self.MIN_SCALE, min(_hi, self.scale * factor))
        if abs(new_scale - self.scale) < 1e-6:
            return
        # 鼠标在 canvas 坐标里的位置
        cx = self.canvas.canvasx(sx)
        cy = self.canvas.canvasy(sy)
        # 对应的世界坐标
        wx = cx / self.scale
        wy = cy / self.scale
        # 切换缩放
        self.scale = new_scale
        self.scale_lbl.config(text=f"{int(self.scale * 100)}%")
        self._update_scrollregion()
        # 让 (wx, wy) 缩放后仍然出现在鼠标位置
        try:
            region = self.canvas.cget("scrollregion")
            x0, y0, x1, y1 = map(float, str(region).split())
            W = max(1.0, x1 - x0)
            H = max(1.0, y1 - y0)
            view_cx = wx * new_scale - sx
            view_cy = wy * new_scale - sy
            fx = (view_cx - x0) / W
            fy = (view_cy - y0) / H
            self.canvas.xview_moveto(max(0.0, min(1.0, fx)))
            self.canvas.yview_moveto(max(0.0, min(1.0, fy)))
        except Exception:
            pass
        self._view_x = self.canvas.canvasx(0)
        self._view_y = self.canvas.canvasy(0)
        self._redraw()

    def _on_space_down(self, event):
        self._space_down = True
        try:
            self.canvas.configure(cursor="fleur")
        except Exception:
            pass
        return "break"

    def _on_space_up(self, event):
        self._space_down = False
        if not self._pan_active:
            try:
                self.canvas.configure(
                    cursor="crosshair" if self.picker_mode else "")
            except Exception:
                pass

    def _on_middle_press(self, event):
        self._pan_active = True
        self._pan_last = (event.x, event.y)
        try:
            self.canvas.configure(cursor="fleur")
        except Exception:
            pass

    def _on_middle_motion(self, event):
        if not self._pan_active or self._pan_last is None:
            return
        dx = event.x - self._pan_last[0]
        dy = event.y - self._pan_last[1]
        self._pan_last = (event.x, event.y)
        self._view_x -= dx
        self._view_y -= dy
        self._apply_view_offset()

    def _on_middle_release(self, event):
        self._pan_active = False
        self._pan_last = None
        if not self._space_down:
            try:
                self.canvas.configure(
                    cursor="crosshair" if self.picker_mode else "")
            except Exception:
                pass

    def _apply_view_offset(self):
        try:
            region = self.canvas.cget("scrollregion")
            x0, y0, x1, y1 = map(float, str(region).split())
            W = max(1.0, x1 - x0)
            H = max(1.0, y1 - y0)
            fx = (self._view_x - x0) / W
            fy = (self._view_y - y0) / H
            self.canvas.xview_moveto(max(0.0, min(1.0, fx)))
            self.canvas.yview_moveto(max(0.0, min(1.0, fy)))
        except Exception:
            pass
        self._redraw()

    # ---------------- 鼠标交互 ----------------
    def _on_press(self, event):
        self.canvas.focus_set()
        sx = self.canvas.canvasx(event.x)
        sy = self.canvas.canvasy(event.y)

        if self._space_down:
            self._pan_active = True
            self._pan_last = (event.x, event.y)
            try:
                self.canvas.configure(cursor="fleur")
            except Exception:
                pass
            return

        node = self._node_at_screen(sx, sy)

        if node is None:
            # 空白处：开始框选
            self._rect_selecting = True
            self._rect_start = (sx, sy)
            if self._rect_id is not None:
                try:
                    self.canvas.delete(self._rect_id)
                except Exception:
                    pass
                self._rect_id = None
            # 未按 Ctrl 则清空已有选择
            ctrl = bool(event.state & 0x0004)
            if not ctrl:
                self.selected_node_ids.clear()
                self.selected_node = None
                self._redraw()
            self.drag_node = None
            self._drag_offsets = {}
            self._ctrl_drag = False
            return

        # 点击节点
        self.drag_node = node
        self._ctrl_drag = bool(event.state & 0x0004)
        wx, wy = self._screen_to_world(sx, sy)
        self._drag_dx = wx - node.x
        self._drag_dy = wy - node.y

        ctrl = bool(event.state & 0x0004)
        shift = bool(event.state & 0x0001)

        # ★ v25 补丁42：**Shift + 拖节点 = 把它拖进标签盒**
        #   （用户要「从标签星图直接拖拽标签到标签盒」）。
        #   为什么用 Shift：星图里「按住拖动」本来是**移动节点位置**的，
        #   直接拿它当「拖进盒子」会变成「你每挪一下标签就被塞进盒子一次」。
        #   这里只在**按下时就按住 Shift** 的情况下切换成「拖进盒子」；
        #   不按 Shift 的时候 Shift 仍然是原来的「加选」。
        #   （右键菜单里也有「放进标签盒」，两种方式随便用哪个。）
        self._shift_box_drag = bool(shift)
        self._shift_box_started = False
        self._press_xroot = event.x_root
        self._press_yroot = event.y_root

        if ctrl:
            if node.tag_id in self.selected_node_ids:
                self.selected_node_ids.discard(node.tag_id)
            else:
                self.selected_node_ids.add(node.tag_id)
        elif shift:
            self.selected_node_ids.add(node.tag_id)
        else:
            if node.tag_id not in self.selected_node_ids:
                self.selected_node_ids = {node.tag_id}

        self.selected_node = node
        self.selected_edge = None
        self._update_edge_info_label()

        # ★ 记录拖动偏移
        # 如果被点的节点在已选中集里，整组一起拖动；否则只拖这一个
        self._drag_offsets = {}
        if node.tag_id in self.selected_node_ids and \
                len(self.selected_node_ids) > 1:
            for tid in self.selected_node_ids:
                n = self.nodes.get(tid)
                if n is not None:
                    self._drag_offsets[tid] = (wx - n.x, wy - n.y)
        else:
            self._drag_offsets[node.tag_id] = (wx - node.x, wy - node.y)

        self._redraw()

    def _on_motion(self, event):
        if self._pan_active and self._pan_last is not None:
            dx = event.x - self._pan_last[0]
            dy = event.y - self._pan_last[1]
            self._pan_last = (event.x, event.y)
            self._view_x -= dx
            self._view_y -= dy
            self._apply_view_offset()
            return

        sx = self.canvas.canvasx(event.x)
        sy = self.canvas.canvasy(event.y)

        # 拖动节点
        if self.drag_node is not None:
            # ★ v25 补丁42：**Shift + 拖 = 拖进标签盒**，不是移动节点。
            #   一旦动了 6 像素以上，就通知标签盒开始盯鼠标；
            #   这一路都不挪节点位置（松手时盒子会自己判断要不要收）。
            if getattr(self, "_shift_box_drag", False):
                if not getattr(self, "_shift_box_started", False):
                    if (abs(event.x_root - getattr(self, "_press_xroot",
                                                   event.x_root)) < 6
                            and abs(event.y_root - getattr(self, "_press_yroot",
                                                           event.y_root)) < 6):
                        return
                    self._shift_box_started = True
                    _n = self.drag_node
                    try:
                        if getattr(self, "app", None) is not None and \
                                getattr(self.app, "tagbox", None):
                            self.app.tagbox.begin_watch_drag(
                                _n.tag_id, _n.name, _n.color)
                    except Exception:
                        pass
                    self.set_status_hint("拖到「标签盒」窗口上松手 = 放进盒子")
                return
            wx, wy = self._screen_to_world(sx, sy)
            if self._drag_offsets:
                for tid, (dx, dy) in self._drag_offsets.items():
                    n = self.nodes.get(tid)
                    if n is not None:
                        n.x = wx - dx
                        n.y = wy - dy
            else:
                self.drag_node.x = wx - self._drag_dx
                self.drag_node.y = wy - self._drag_dy
            # ★ 拖动过程中就实时刷新滚动范围，防止把节点拖出去后滚不到
            self._update_scrollregion()
            self._redraw()
            dcx = self.drag_node.x + self.drag_node.w / 2
            dcy = self.drag_node.y + self.drag_node.h / 2
            node = self._drop_target(self.drag_node)
            if node is not self.hover_node:
                self.hover_node = node
                self._redraw()
            return

        # 拖动框选矩形
        if self._rect_selecting and self._rect_start is not None:
            x0, y0 = self._rect_start
            if self._rect_id is not None:
                try:
                    self.canvas.delete(self._rect_id)
                except Exception:
                    pass
            self._rect_id = self.canvas.create_rectangle(
                x0, y0, sx, sy,
                outline="#3498db", width=2, dash=(4, 3),
                fill="#3498db")
            try:
                self.canvas.itemconfigure(self._rect_id, stipple="gray25")
            except Exception:
                pass
            return

        # 鼠标移动（更新 hover）
        node = self._node_at_screen(sx, sy)
        if node is not self.hover_node:
            self.hover_node = node
            try:
                if node:
                    self.canvas.configure(cursor="hand2")
                else:
                    self.canvas.configure(
                        cursor="crosshair" if self.picker_mode else "")
            except Exception:
                pass
            self._redraw()

    def _on_release(self, event):
        # ★ v25 补丁42：如果是「Shift + 拖进标签盒」这一路 ——
        #   交给标签盒判断松手位置在不在它身上，然后收工（不动节点位置）。
        if getattr(self, "_shift_box_drag", False):
            self._shift_box_drag = False
            started = getattr(self, "_shift_box_started", False)
            self._shift_box_started = False
            self.drag_node = None
            self._drag_offsets = {}
            self._ctrl_drag = False
            if started:
                try:
                    tb = getattr(self.app, "tagbox", None) \
                        if getattr(self, "app", None) else None
                    if tb is not None:
                        tb.end_watch_drag(event.x_root, event.y_root)
                except Exception:
                    pass
            try:
                self.canvas.configure(
                    cursor="crosshair" if self.picker_mode else "")
            except Exception:
                pass
            self._redraw()
            self._refresh_relation_bar()
            return

        if self._pan_active:
            self._pan_active = False
            self._pan_last = None
            if not self._space_down:
                try:
                    self.canvas.configure(
                        cursor="crosshair" if self.picker_mode else "")
                except Exception:
                    pass
            return

        # 结束框选
        if self._rect_selecting:
            sx = self.canvas.canvasx(event.x)
            sy = self.canvas.canvasy(event.y)
            if self._rect_start is not None:
                x0, y0 = self._rect_start
                wx0, wy0 = self._screen_to_world(x0, y0)
                wx1, wy1 = self._screen_to_world(sx, sy)
                lx, rx = sorted([wx0, wx1])
                ty, by = sorted([wy0, wy1])
                ctrl = bool(event.state & 0x0004)
                if not ctrl:
                    self.selected_node_ids.clear()
                for n in self.nodes.values():
                    # 节点中心在矩形内即选中
                    ncx = n.x + n.w / 2
                    ncy = n.y + n.h / 2
                    if lx <= ncx <= rx and ty <= ncy <= by:
                        self.selected_node_ids.add(n.tag_id)
            if self._rect_id is not None:
                try:
                    self.canvas.delete(self._rect_id)
                except Exception:
                    pass
                self._rect_id = None
            self._rect_selecting = False
            self._rect_start = None
            self.selected_node = None
            self._redraw()
            self.set_status_hint(f"已选中 {len(self.selected_node_ids)} 个标签")
            return

        dragged = self.drag_node
        ctrl = self._ctrl_drag
        drag_offsets = dict(self._drag_offsets) if self._drag_offsets else {}
        self.drag_node = None
        self.hover_node = None
        self._ctrl_drag = False
        self._drag_offsets = {}
        try:
            self.canvas.configure(
                cursor="crosshair" if self.picker_mode else "")
        except Exception:
            pass
        if dragged is None:
            return

        # 判断落点（★ v25 补丁：整组拖动时组里任一节点压到别人身上都算）
        group = self._drag_group(dragged)
        target = self._drop_target(dragged, group)

        if target is None:
            # 拖到空白：保留位置
            self.dirty = True
            self._push_undo()
            n_moved = len(drag_offsets) if drag_offsets else 1
            if n_moved > 1:
                self.set_status_hint(f"已移动 {n_moved} 个标签")
            else:
                self.set_status_hint(f"「{dragged.name}」已移动")
            return

        # ★ v25 补丁：整组一起改成「挂在落点标签下面」
        sources = [n for n in group if n.tag_id != target.tag_id]
        if not sources:
            self._redraw()
            return

        if ctrl:
            removed = []
            for src in sources:
                if (target.tag_id, src.tag_id) in self.edges:
                    self.store.remove_tag_relation(target.tag_id, src.tag_id)
                    self.custom_line_colors.pop(
                        (target.tag_id, src.tag_id), None)
                    removed.append(src.name)
            if removed:
                self._reload()
                self.dirty = True
                self._push_undo()
                if len(removed) == 1:
                    self.set_status_hint(
                        f"已删除：「{target.name}」不再是「{removed[0]}」的父级")
                else:
                    self.set_status_hint(
                        f"已删除：「{target.name}」不再是这 "
                        f"{len(removed)} 个标签的父级"
                        f"（{'、'.join(removed)}）")
            else:
                self.set_status_hint(
                    f"「{target.name}」和这些标签之间本来就没有父子关系")
                self._redraw()
            return

        added, existed, cycled = [], [], []
        for src in sources:
            if (target.tag_id, src.tag_id) in self.edges:
                existed.append(src.name)
                continue
            if not self.store.add_tag_relation(target.tag_id, src.tag_id):
                cycled.append(src.name)
                continue
            added.append(src.name)

        if added:
            self._reload()
            self.dirty = True
            self._push_undo()
        else:
            self._redraw()

        if len(sources) == 1 and added:
            node_new = self.nodes.get(dragged.tag_id)
            n_parents = len(node_new.parents) if node_new else 0
            self.set_status_hint(
                f"已添加：「{target.name}」现在是「{dragged.name}」的父级"
                f"（{dragged.name} 现在共有 {n_parents} 个父级）")
        else:
            parts = []
            if added:
                parts.append(f"已把 {len(added)} 个标签挂到「{target.name}」"
                             f"下面（{'、'.join(added)}）")
            if existed:
                parts.append(f"{len(existed)} 个本来就有关系")
            if cycled:
                parts.append(f"{len(cycled)} 个会造成循环、已跳过"
                             f"（{'、'.join(cycled)}）")
            if not parts:
                parts.append("没有可建立的父子关系")
            self.set_status_hint("；".join(parts))
        if cycled:
            messagebox.showwarning(
                "有标签没能挂上",
                f"这些标签会造成循环（目标已经是它们的后代），已跳过：\n\n"
                f"· " + "\n· ".join(cycled),
                parent=self)

    def set_status_hint(self, text):
        try:
            self.status_lbl.config(text=text)
            self.status_lbl.after(3500,
                                  lambda: self.status_lbl.config(text=""))
        except Exception:
            pass

    # ---------------- 线的交互 ----------------
    def _on_edge_enter(self, pid, cid):
        if self.hover_edge != (pid, cid):
            self.hover_edge = (pid, cid)
            self._redraw()

    def _on_edge_leave(self, pid, cid):
        if self.hover_edge == (pid, cid):
            self.hover_edge = None
            self._redraw()

    def _on_edge_left_click(self, pid, cid):
        if self.picker_mode:
            if self.picker_color is None:
                # 取色
                self.picker_color = self._get_edge_color(pid, cid)
                self._picker_state_lbl.configure(
                    text=f"（已取色 {self.picker_color}，点另一条线染色）",
                    foreground=theme_get("ok"))
                self.set_status_hint(
                    f"已取色 {self.picker_color}，现在点另一条线给它染上这个颜色")
                self._redraw()
            else:
                # 染色
                self.custom_line_colors[(pid, cid)] = self.picker_color
                self.dirty = True
                self._push_undo()
                self.set_status_hint(f"已染色 {self.picker_color}")
                self.picker_color = None
                self._toggle_picker()
            return "break"

        # 非取色模式：选中这条线
        self.selected_edge = (pid, cid)
        self.selected_node = None
        self.selected_node_ids.clear()
        self._update_edge_info_label()
        self._redraw()
        return "break"

    def _update_edge_info_label(self):
        try:
            if self.selected_edge is None:
                self.edge_info_lbl.config(text="")
                return
            pid, cid = self.selected_edge
            p = self.nodes.get(pid)
            c_ = self.nodes.get(cid)
            if p is None or c_ is None:
                self.edge_info_lbl.config(text="")
                return
            color = self._get_edge_color(pid, cid)
            self.edge_info_lbl.config(
                text=f"已选中线：{p.name} → {c_.name}   颜色 {color}")
        except Exception:
            pass

    def _on_edge_right(self, event, pid, cid):
        m = tk.Menu(self, tearoff=0)
        m.add_command(label=T("🎨 复制这条线的颜色"),
                      command=lambda: self._copy_edge_color(pid, cid))
        if self.picker_color:
            m.add_command(
                label=f"✅ 贴到这个线（{self.picker_color}）",
                command=lambda: self._paste_edge_color(pid, cid))
        m.add_command(label=T("🖌 给这条线改色…"),
                      command=lambda: self._color_edge(pid, cid))
        m.add_separator()
        m.add_command(label=T("↺ 恢复默认色"),
                      command=lambda: self._reset_edge_color(pid, cid))
        m.add_separator()
        m.add_command(
            label=T("删除这条父子关系"),
            command=lambda: self._delete_edge(pid, cid))
        m.tk_popup(event.x_root, event.y_root)

    def _color_edge(self, pid, cid):
        cur = self._get_edge_color(pid, cid)
        _rgb, hexv = colorchooser.askcolor(
            color=cur, title=T("选择线颜色"), parent=self)
        if not hexv:
            return
        self.custom_line_colors[(pid, cid)] = hexv
        self.dirty = True
        self._push_undo()
        self._update_edge_info_label()
        self._redraw()

    def _color_selected_edge(self):
        if self.selected_edge is None:
            messagebox.showinfo(
                "提示",
                "请先在画布上点一条线来选中它，再点这个按钮。",
                parent=self)
            return
        pid, cid = self.selected_edge
        self._color_edge(pid, cid)

    def _copy_edge_color(self, pid, cid):
        self.picker_color = self._get_edge_color(pid, cid)
        self.picker_mode = True
        self._picker_btn.configure(bg="#2ecc71", fg="white",
                                   highlightbackground="#27ae60")
        self._picker_state_lbl.configure(
            text=f"（已取色 {self.picker_color}，点另一条线染色）",
            foreground=theme_get("ok"))
        try:
            self.canvas.configure(cursor="crosshair")
        except Exception:
            pass
        self.set_status_hint(
            f"已取色 {self.picker_color}，现在点另一条线给它染上这个颜色")
        self._redraw()

    def _paste_edge_color(self, pid, cid):
        if not self.picker_color:
            return
        self.custom_line_colors[(pid, cid)] = self.picker_color
        self.dirty = True
        self._push_undo()
        self.set_status_hint(f"已染色 {self.picker_color}")
        self.picker_color = None
        self._toggle_picker()
        self._redraw()

    def _reset_edge_color(self, pid, cid):
        if (pid, cid) in self.custom_line_colors:
            del self.custom_line_colors[(pid, cid)]
            self.dirty = True
            self._push_undo()
            self.set_status_hint("已恢复这条线的默认颜色")
            self._update_edge_info_label()
            self._redraw()

    def _toggle_picker(self):
        self.picker_mode = not self.picker_mode
        self.picker_color = None
        if self.picker_mode:
            self._picker_btn.configure(bg="#2ecc71", fg="white",
                                       highlightbackground="#27ae60")
            self._picker_state_lbl.configure(
                text=T("（开启：先点一条线取色）"), foreground=theme_get("ok"))
            try:
                self.canvas.configure(cursor="crosshair")
            except Exception:
                pass
        else:
            self._picker_btn.configure(bg=theme_get("line"), fg=theme_get("fg_dim"),
                                       highlightbackground=theme_get("line"))
            self._picker_state_lbl.configure(
                text=T("（未开启）"), foreground=theme_get("fg_dim"))
            try:
                self.canvas.configure(cursor="")
            except Exception:
                pass
        self._redraw()

    def _clear_all_custom_colors(self):
        if not self.custom_line_colors:
            return
        if not messagebox.askyesno(
                "确认",
                f"清除所有手动染色的线（{len(self.custom_line_colors)} 条）？\n"
                "（线会恢复成默认颜色）",
                parent=self):
            return
        self.custom_line_colors.clear()
        self.dirty = True
        self._push_undo()
        self._update_edge_info_label()
        self._redraw()
        self.set_status_hint("已清除所有自定义线颜色")

    def _delete_edge(self, pid, cid):
        p = self.nodes.get(pid)
        ch = self.nodes.get(cid)
        if p is None or ch is None:
            return
        if not messagebox.askyesno(
                "确认删除关系",
                f"删除「{p.name}」→「{ch.name}」这条父子关系吗？\n"
                "（标签本身都会保留）",
                parent=self):
            return
        self.store.remove_tag_relation(pid, cid)
        self.custom_line_colors.pop((pid, cid), None)
        self.selected_edge = None
        self._reload()
        self.dirty = True
        self._push_undo()
        self.set_status_hint(f"已删除：「{p.name}」不再是「{ch.name}」的父级")

    # ---------------- 右键空白 / 节点 ----------------
    def _on_right_click(self, event):
        sx = self.canvas.canvasx(event.x)
        sy = self.canvas.canvasy(event.y)
        node = self._node_at_screen(sx, sy)

        if node is None:
            m = tk.Menu(self, tearoff=0)
            m.add_command(label=T("新建根标签"), command=self._new_root_tag)
            m.add_separator()
            m.add_command(label=T("左对齐选中标签"),
                          command=self._align_left)
            m.add_command(label=T("让选中标签排成同一水平线"),
                          command=self._align_center_h)
            m.add_command(label=T("上下等距排列选中标签"),
                          command=self._space_vertically)
            m.add_separator()
            m.add_command(label=T("重置视图"), command=self._reset_view)
            m.tk_popup(event.x_root, event.y_root)
            return

        # 如果右键的节点不在选择集里，就把选择切到它
        if node.tag_id not in self.selected_node_ids:
            self.selected_node_ids = {node.tag_id}
        self.selected_node = node
        self.selected_edge = None
        self._redraw()

        m = tk.Menu(self, tearoff=0)
        m.add_command(label=T("新建子标签"),
                      command=lambda n=node: self._new_child_of(n))
        m.add_command(label=T("重命名…"), command=self._rename_selected)
        m.add_command(label=T("更换颜色…"), command=self._recolor_selected)
        m.add_separator()
        # ★ v25 补丁42：把标签放进「标签盒」（用户要的「从标签星图拖到标签盒」，
        #   这里给一个菜单版的入口，比拖更省事、也不会误触）。
        m.add_command(label=T("🗃 放进标签盒"),
                      command=lambda n=node: self._put_into_tagbox(n))
        m.add_separator()
        m.add_command(label=T("移除所有父级"),
                      command=self._remove_all_parents)
        m.add_command(label=T("移除所有子级"),
                      command=self._remove_all_children)
        m.add_separator()
        m.add_command(label=T("删除标签"), command=self._delete_selected)
        m.tk_popup(event.x_root, event.y_root)

    def _on_double(self, event):
        sx = self.canvas.canvasx(event.x)
        sy = self.canvas.canvasy(event.y)
        node = self._node_at_screen(sx, sy)
        if node:
            self.selected_node = node
            self.selected_node_ids = {node.tag_id}
            self._rename_selected()

    # ---------------- 对齐 / 等距 ----------------
    def _selected_nodes(self):
        return [n for n in self.nodes.values()
                if n.tag_id in self.selected_node_ids]

    def _align_left(self):
        nodes = self._selected_nodes()
        if len(nodes) < 2:
            messagebox.showinfo("提示", T("请先用鼠标框选至少两个标签。"),
                                parent=self)
            return
        # 用最左的 x 作为对齐目标
        target_x = min(n.x for n in nodes)
        for n in nodes:
            n.x = target_x
        self.dirty = True
        self._push_undo()
        self._redraw()
        self.set_status_hint(f"已左对齐 {len(nodes)} 个标签")

    def _align_center_h(self):
        """让所有被选中标签的竖直中心对齐到同一条水平线上（摆成一行）"""
        nodes = self._selected_nodes()
        if len(nodes) < 2:
            messagebox.showinfo("提示", T("请先用鼠标框选至少两个标签。"),
                                parent=self)
            return
        top = min(n.y for n in nodes)
        bottom = max(n.y + n.h for n in nodes)
        cy = (top + bottom) / 2.0
        for n in nodes:
            n.y = cy - n.h / 2.0
        self.dirty = True
        self._push_undo()
        self._redraw()
        self.set_status_hint(f"已让 {len(nodes)} 个标签排成同一水平线")

    def _space_vertically(self):
        nodes = self._selected_nodes()
        if len(nodes) < 2:
            messagebox.showinfo("提示", T("请先用鼠标框选至少两个标签。"),
                                parent=self)
            return
        # 取选中节点最靠上的 y 作为起点，向下依次排列，间距按平均高度
        nodes_sorted = sorted(nodes, key=lambda n: (n.y, n.x))
        top = min(n.y for n in nodes)
        bottom = max(n.y + n.h for n in nodes)
        total_h = sum(n.h for n in nodes_sorted)
        n_gaps = max(1, len(nodes_sorted) - 1)
        gap = max(10.0, (bottom - top - total_h) / n_gaps)

        y = top
        for n in nodes_sorted:
            n.y = y
            y += n.h + gap
        self.dirty = True
        self._push_undo()
        self._redraw()
        self.set_status_hint(f"已对 {len(nodes)} 个标签做上下等距排列")

    # ---------------- 编辑操作 ----------------

    def _new_root_tag(self):
        name = SimpleInputDialog(self, "新建根标签").result
        if not name:
            return
        try:
            self.store.create_tag(name)
        except Exception as exc:
            messagebox.showerror("错误", str(exc), parent=self)
            return
        tid = self.store.tag_id_by_name(name)
        if tid is not None:
            # ★ 放在视口正中央：直接叠在最上层，只需要拖这一个新标签
            x, y = self._viewport_center_world()
            self.store.set_tag_position(tid, x, y)
        self._reload()
        self.dirty = True
        self._push_undo()

    def _new_child_tag(self):
        if not self.selected_node_ids:
            messagebox.showinfo("提示", T("请先点击一个标签作为父级"), parent=self)
            return
        parent = self.nodes.get(next(iter(self.selected_node_ids)))
        if parent is None:
            return
        self._new_child_of(parent)

    def _new_child_of(self, parent):
        name = SimpleInputDialog(self, f"新建「{parent.name}」的子标签").result
        if not name:
            return
        try:
            self.store.create_tag(name)
        except Exception as exc:
            messagebox.showerror("错误", str(exc), parent=self)
            return
        tid = self.store.tag_id_by_name(name)
        if tid is None:
            return
        self.store.add_tag_relation(parent.tag_id, tid)
        # ★ 同样放在视口正中央：叠在最上层，只拖这一个
        x, y = self._viewport_center_world()
        self.store.set_tag_position(tid, x, y)
        self._reload()
        self.dirty = True
        self._push_undo()

    def _rename_selected(self):
        if not self.selected_node_ids:
            return
        # 单个节点才允许改名（多选就不改了）
        if len(self.selected_node_ids) > 1:
            messagebox.showinfo("提示", T("一次只能重命名一个标签"), parent=self)
            return
        tid = next(iter(self.selected_node_ids))
        n = self.nodes.get(tid)
        if n is None:
            return
        new_name = SimpleInputDialog(self, "重命名标签", initial=n.name).result
        if not new_name or new_name == n.name:
            return
        try:
            self.store.rename_tag(tid, new_name)
        except Exception as exc:
            messagebox.showerror("错误", str(exc), parent=self)
            return
        self._reload()
        self.dirty = True
        self._push_undo()

    def _recolor_selected(self):
        if not self.selected_node_ids:
            return
        # 多选时统一改色
        tids = list(self.selected_node_ids)
        n0 = self.nodes.get(tids[0])
        if n0 is None:
            return
        _rgb, hexv = colorchooser.askcolor(
            color=n0.color, title=T("选择标签颜色"), parent=self)
        if not hexv:
            return
        for tid in tids:
            self.store.set_tag_color(tid, hexv)
        self._reload()
        self.dirty = True
        self._push_undo()

    def _remove_all_parents(self):
        if not self.selected_node_ids:
            return
        total = 0
        for tid in list(self.selected_node_ids):
            n = self.nodes.get(tid)
            if n is not None:
                total += len(n.parents)
        if total == 0:
            return
        if not messagebox.askyesno(
                "确认",
                f"移除选中标签的所有父级关系吗？（共 {total} 条）\n"
                "（连线会被删除，标签本身保留）",
                parent=self):
            return
        for tid in list(self.selected_node_ids):
            n = self.nodes.get(tid)
            if n is None:
                continue
            for p in list(n.parents):
                self.store.remove_tag_relation(p.tag_id, n.tag_id)
                self.custom_line_colors.pop((p.tag_id, n.tag_id), None)
        self._reload()
        self.dirty = True
        self._push_undo()

    def _remove_all_children(self):
        if not self.selected_node_ids:
            return
        total = 0
        for tid in list(self.selected_node_ids):
            n = self.nodes.get(tid)
            if n is not None:
                total += len(n.children)
        if total == 0:
            return
        if not messagebox.askyesno(
                "确认",
                f"移除选中标签的所有子级关系吗？（共 {total} 条）\n"
                "（连线会被删除，子标签本身保留）",
                parent=self):
            return
        for tid in list(self.selected_node_ids):
            n = self.nodes.get(tid)
            if n is None:
                continue
            for c in list(n.children):
                self.store.remove_tag_relation(n.tag_id, c.tag_id)
                self.custom_line_colors.pop((n.tag_id, c.tag_id), None)
        self._reload()
        self.dirty = True
        self._push_undo()

    def _delete_selected(self):
        if not self.selected_node_ids:
            return
        names = []
        for tid in self.selected_node_ids:
            n = self.nodes.get(tid)
            if n is not None:
                names.append(n.name)
        if not names:
            return
        if len(names) == 1:
            msg = f"确定删除标签「{names[0]}」吗？\n（它和父级/子级的关系会被删除，但相关标签本身保留）"
        else:
            msg = f"确定删除 {len(names)} 个标签吗？\n" + "、".join(names)
        if not messagebox.askyesno("确认删除", msg, parent=self):
            return
        for tid in list(self.selected_node_ids):
            self.store.delete_tag(tid, keep_parents=True)
            self.store.clear_tag_position(tid)
            for k in list(self.custom_line_colors.keys()):
                if k[0] == tid or k[1] == tid:
                    del self.custom_line_colors[k]
        self.selected_node_ids.clear()
        self.selected_node = None
        self.selected_edge = None
        self._reload()
        self.dirty = True
        self._push_undo()

    # ---------------- 保存 ----------------
    def _save(self, silent=False):
        """保存位置 + 关系 + 线颜色。默认弹出成功提示。"""
        try:
                        # 保存位置
            positions = {}
            for tid, n in self.nodes.items():
                positions[tid] = (n.x, n.y)
            self.store.set_tag_positions_bulk(positions)
            # ★ 保存线颜色
            self.store.set_edge_colors_bulk(self.custom_line_colors)
            # 同步所有文件的标签链
            self.propagated = self.store.resync_all_file_tags()
            self.dirty = False
            self.saved = True
        except Exception as exc:
            messagebox.showerror("保存失败", str(exc), parent=self)
            return False

        if not silent:
            messagebox.showinfo(
                "保存成功",
                "标签星图已保存：\n\n"
                "  · 所有标签的位置\n"
                "  · 所有父子关系\n"
                "  · 所有自定义线颜色\n"
                "  · 所有文件的标签链已同步\n\n"
                "窗口不会关闭，可以继续编辑。",
                parent=self)
            self.set_status_hint("已保存")

        # ★ 通知外部（例如右侧缩略图）实时刷新
        if self.on_saved:
            try:
                self.on_saved()
            except Exception:
                pass
        return True

    # ---------------- 关闭 ----------------
    def _on_window_close(self):
        if self.dirty:
            ans = messagebox.askyesnocancel(
                "未保存的修改",
                "当前星图还有未保存的修改。\n\n"
                "  · 是 → 保存并关闭\n"
                "  · 否 → 不保存直接关闭\n"
                "  · 取消 → 返回继续编辑",
                parent=self)
            if ans is None:
                return
            if ans:
                if not self._save(silent=True):
                    return
        self.destroy()

    def _cancel(self):
        self._on_window_close()


# ---------- 兜底（★ 它会吃掉错误，所以要专门测"用的哪一份"）----------
def _fallback():
    g = globals()
    for _n in _NEED:
        if g.get(_n) is None:
            g[_n] = _Borrowed(_n)


_fallback()
