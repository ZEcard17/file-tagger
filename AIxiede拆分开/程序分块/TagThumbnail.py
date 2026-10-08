# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：TagThumbnail。

★ 代码**原样搬运**，一个字没改，只是换了个文件放。

★★ 拆文件的规矩（所有分块文件都照这个写）★★
   ① **Python 自带的东西直接 import**（tk、ttk、os、sys…）——不绕弯。
   ② **只有主程序自己造的东西才向主程序借**（FONT、note_swallowed 这类）。
      而且**不在开头 import 主程序**——两边互相 import 会让 Python
      报错、程序打不开。借法是主程序启动时把「自己」交进来（_set_app）。
   ③ 借来的名字做成**模块级变量**，这样下面的代码**一个字都不用改**。
   ④ 借不到就用兜底值，**不能因为主程序改了个名字就整个打不开**。
   ⑤ ★★ **运行时会变的常量必须用「代理」**（_Borrowed）——
      启动时抄一份的话，**切主题/改缩放之后模块里还是旧值**。

★★ 拆的时候踩过的坑（错题本 #158~#161，★ 别重演）：
   · import 要写 `from TagThumbnail import …`（**不带包路径**）
   · `_set_app` 要**取别名**（`as _fk_…`）——模块名和类名同名
   · 借名字的清单**用 symtable + dir() 定**，别用正则猜
   · 代理类**必须实现 `__call__`**（函数也会被借）
   · ★ 兜底 except 会吃掉错误 → **必须专门测"用的哪一份"**
"""
import queue
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, colorchooser

# ---------- 要向主程序借的名字（先占位，挂上后填真身） ----------
_MUTABLE = ['BOLD', 'FONT', 'UI_FONT_SIZE']
_NEED = ['BOLD', 'FONT', 'T', 'UI_FONT_SIZE', '_TNode', 'deque', 'make_search_label', 'register_themed', 'text_color_for', 'theme_get']
_APP = None


class _Borrowed:
    """★★ 借"会变的东西"用的代理（★ 每次读都回主程序现取）。

    ★ 为什么不能直接抄一份：`THEME_NAME` / `HAS_PIL` 这些**运行时会变** ——
      启动时抄过来，切主题/装不装 PIL 之后**模块里还是旧值**。

    ★★★ 为什么 `__call__` 不能少（错题本 #160）：
      **函数也会被借**（`T` / `fmt_size` / …）——
      少了 `__call__`，`T("…")` 直接 `TypeError: not callable`，
      ★ 而且这个错**会被上层 except 吞掉** → 表现成"功能静默消失"。
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

    # ★★★ 这个必须有（函数要用）
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

    # ★★★ 补全「代理协议」（错题本 #171）——
    #   ★ 之前只实现了常用几个，结果 `open(_USAGE_PATH)` 炸了：
    #     `TypeError: ... where __fspath__ returns a str, not '_Borrowed'`
    #   ★★ 判据：**代理会被当成什么用，你猜不到** ——
    #     宁可多实现几个（多余的方法不会被调用，不占开销）。
    def __fspath__(self):
        return os.fspath(self._v())

    def __bytes__(self):
        return bytes(self._v())

    def __format__(self, spec):
        return format(self._v(), spec)

    def __abs__(self):
        return abs(self._v())

    def __neg__(self):
        return -self._v()

    def __pos__(self):
        return +self._v()

    def __invert__(self):
        return ~self._v()

    def __round__(self, n=None):
        return round(self._v()) if n is None else round(self._v(), n)

    def __sub__(self, o):
        return self._v() - o

    def __rsub__(self, o):
        return o - self._v()

    def __truediv__(self, o):
        return self._v() / o

    def __floordiv__(self, o):
        return self._v() // o

    def __mod__(self, o):
        return self._v() % o

    def __pow__(self, o):
        return self._v() ** o

    def __rmul__(self, o):
        return o * self._v()

    def __and__(self, o):
        return self._v() & o

    def __or__(self, o):
        return self._v() | o

    def __xor__(self, o):
        return self._v() ^ o

    def __lshift__(self, o):
        return self._v() << o

    def __rshift__(self, o):
        return self._v() >> o

    def __enter__(self):
        return self._v().__enter__()

    def __exit__(self, *a):
        return self._v().__exit__(*a)

    def __next__(self):
        return next(self._v())

    def __copy__(self):
        import copy as _c
        return _c.copy(self._v())

    def __deepcopy__(self, memo):
        import copy as _c
        return _c.deepcopy(self._v(), memo)


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
                # ★★ 会变的才用代理；**函数/常量直接拿**（★ 少一层、少一个坑）
                # ★★★ 一律包代理（错题本 #168）：
                #   模块的桩可能跑在**主程序还没定义这个名字**之前，
                #   所以「启动时取快照」必然借不到。
                #   ★ 代理是**读的时候才现取**，什么时候定义都不影响。
                g[_n] = _Borrowed(_n)
        except Exception:
            pass


class TagThumbnail(tk.Frame):
    # ★★★ 2026-10-08 **缩放范围放大**（用户要"能缩放到无限大"）★★★
    #   ★ 原来 `MIN_SCALE = 0.25` / `MAX_SCALE = 3.0` ——
    #     放到 3 倍就到顶了，用户说"不够"。
    #   ★★ 为什么不是真"无限"：Tk 画布的坐标是**浮点数**，
    #     但 scrollregion 太大会让滚动条**变得极其难用**
    #     （拖一格跳几万像素）；而且节点坐标乘以极大 scale 会**失真/溢出**。
    #   → 取一个"实际够用"的范围：**0.05 ~ 40 倍**（800 倍区间）——
    #     ★ 判据：**"无限"的实际含义是"用户试不到边"**，不是数学上的无穷。
    MIN_SCALE = 0.05
    MAX_SCALE = 40.0
    # ★★★ 2026-10-08 **画布四周留白**（用户要"画布无限大"）★★★
    #   ★ 原来 scrollregion 只按"节点范围 + 120"算 ——
    #     也就是**画布刚好裹住内容**，没有可拖的空白：
    #     节点贴边、滚不到外面、往里拖也没地方放。
    #   ★★ 改成四周留一大片空白（跟内容大小挂钩，见 `_update_scrollregion`）——
    #     这样"往外拖/往外滚"都有余地，**感觉上就是无限大**。
    CANVAS_MARGIN = 4000
    NODE_PAD = 20
    LEVEL_GAP_X = 60
    SIBLING_GAP_Y = 12

    DEFAULT_EDGE_COLOR = "#b8c2d6"


    # ★★ 2026-10-07：这两个**和 StarGraphEditor 里的同名同值**。
    #   ★ 为什么两处都有：`_redraw`（画连线/节点）在**本类**里，
    #     而它要用这份配色 —— 常量放在另一个类里会 AttributeError
    #     （然后被 except 吞掉 → 静默失效，连线颜色不变、徽章不出现）。
    #   ★ 所以：**改配色时两个类都要改**（搜 `EDGE_PALETTE` 能找到两处）。
    EDGE_PALETTE = [
        ("#7fa8d8", 1.4), ("#8f7fd8", 1.7), ("#d88f7f", 2.0),
        ("#7fd8a8", 2.3), ("#d8c07f", 2.6), ("#c07fd8", 2.9),
    ]
    _show_depth_badge = True

    def __init__(self, master, on_drop_on_file=None, on_context_menu=None,
                 on_double_click=None, app=None):
        super().__init__(master)
        # ★★ 2026-10-07 登记"我是卡片底色"（用户报「标签库的缩略图颜色
        #   在夜间模式下是灰的」）。
        #   以前它没登记 → 换皮肤时被 `_retheme_tree()` 的翻色表接管 →
        #   底色被当字色翻 → 发灰。
        try:
            register_themed(self, "card")
        except Exception:
            pass
        # ★★ v26 补丁（2026-10-03）：这里必须收下「主程序」的引用。
        #   原来构造时不收 app，可里面拖标签的时候又写
        #       if self.app is not None and getattr(self.app, "tagbox", None):
        #   而 self.app 从来没人赋过值 —— 每一次拖标签都会抛
        #   AttributeError（外面套着 try/except，所以一声不响）。
        #   后果：**从右边「标签库」把标签拖进「标签盒」这个功能一直没生效**
        #   （拖到盒子那儿松手，盒子不会亮边、也不会收下这个标签）。
        #   现在构造时就把主程序传进来，并在下面用 getattr 兜底。
        self.app = app
        self.on_drop_on_file = on_drop_on_file
        self.on_context_menu = on_context_menu
        self.on_double_click = on_double_click

        self.nodes = {}
        self.edges = set()
        self._node_boxes = []
        self._positions = {}   # ★ 从 store 加载的位置
        self.custom_line_colors = {}   # ★ 从 store 加载的线颜色

        self.scale = 1.0
        self._view_x = 0.0
        self._view_y = 0.0
        self.selected_ids = set()

        self._space_down = False
        self._pan_active = False
        self._pan_last = None
        self._press_xy = None
        self._press_node = None
        self._dragging = False
        self._drag_win = None
        self._drag_name = None
        self._drag_color = None

        self.search_text = ""
        self._search_matches = set()

        sbar = ttk.Frame(self)
        sbar.pack(fill="x", side="top", pady=(0, 4))
        make_search_label(sbar, "").pack(side="left")
        self.search_var = tk.StringVar()
        se = ttk.Entry(sbar, textvariable=self.search_var, width=11)
        se.pack(side="left", padx=(4, 0))
        self.search_entry = se
        # 回车 / ↓ = 跳到下一个匹配，↑ = 跳到上一个匹配
        se.bind("<Return>", lambda e: self._goto_next_match())
        se.bind("<Down>", lambda e: self._goto_next_match())
        se.bind("<Up>", lambda e: self._goto_prev_match())
        # 输入时高亮 + 自动跳第一个
        self.search_var.trace_add(
            "write", lambda *a: self._on_search_text_changed())
        ttk.Button(sbar, text="×", width=3,
                   command=self._clear_search).pack(side="left", padx=(4, 0))
        # ★ v24：上下箭头按钮 —— 跳到上一个 / 下一个匹配的标签
        ttk.Button(sbar, text="▲", width=3,
                   command=self._goto_prev_match).pack(side="left", padx=(4, 0))
        ttk.Button(sbar, text="▼", width=3,
                   command=self._goto_next_match).pack(side="left", padx=(2, 0))
        self.search_info_lbl = ttk.Label(sbar, text="",
                                         foreground=theme_get("ok"))
        self.search_info_lbl.pack(side="left", padx=(4, 0))

        self._match_order = []
        self._match_index = -1
        self._search_jump_job = None
        self._syncing_list = False
        self._match_list_visible = False
        self._match_list_selectable = True

        # ★ v24：搜索结果列表（搜索时出现在搜索框下面，
        #   把所有含这个字符的标签都列出来，点一下就跳过去）
        self._match_list = tk.Listbox(self, height=6, activestyle="dotbox",
                                      exportselection=False,
                                      font=(FONT, UI_FONT_SIZE), relief="flat",
                                      highlightthickness=1,
                                      highlightbackground=theme_get("line"),
                                      width=30, selectbackground=theme_get("select_bg"))
        self._match_list.bind("<<ListboxSelect>>", self._on_match_list_select)
        self._match_list.bind("<Escape>", lambda e: self._clear_search())

        body = tk.Frame(self)
        body.pack(fill="both", expand=True)
        self._body_frame = body

        self.canvas = tk.Canvas(body, bg=theme_get("panel_bg2"), highlightthickness=1,
                                highlightbackground=theme_get("line"), takefocus=True)
        try:
            register_themed(self.canvas, "panel2")   # ★ 常驻控件 → 换皮肤时跟着刷
        except Exception:
            pass
        self.vsb = ttk.Scrollbar(body, orient="vertical", command=self._on_yscroll)
        self.hsb = ttk.Scrollbar(body, orient="horizontal", command=self._on_xscroll)
        self.canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.hsb.pack(side="bottom", fill="x")
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # ★★ 2026-10-08：`<Configure>`（窗口尺寸变化）**一次拖窗能触发几十次** →
        #   用 `_redraw_soon()` 节流（错题本 #185）。
        self.canvas.bind("<Configure>", lambda e: self._redraw_soon())
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Double-1>", self._on_double)
        self.canvas.bind("<Button-3>", self._on_right)
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.canvas.bind("<Button-4>", self._on_wheel)
        self.canvas.bind("<Button-5>", self._on_wheel)
        self.canvas.bind("<Button-2>", self._on_middle_press)
        self.canvas.bind("<B2-Motion>", self._on_middle_motion)
        self.canvas.bind("<ButtonRelease-2>", self._on_middle_release)

        self.bind("<KeyPress-space>", self._on_space_down)
        self.bind("<KeyRelease-space>", self._on_space_up)
        self.canvas.bind("<KeyPress-space>", self._on_space_down)
        self.canvas.bind("<KeyRelease-space>", self._on_space_up)
        self.canvas.bind("<Enter>", lambda e: self.canvas.focus_set())

    # ---------------- 搜索 ----------------
    def _on_search_text_changed(self):
        """输入时：高亮 + 防抖后自动跳到第一个匹配。"""
        self._do_search()
        if self._search_jump_job is not None:
            try:
                self.after_cancel(self._search_jump_job)
            except Exception:
                pass
        self._search_jump_job = self.after(250, self._goto_first_match)

    def _do_search(self):
        q = (self.search_var.get() or "").strip().lower()
        self.search_text = q
        if not q:
            self._search_matches = set()
            self._match_order = []
            self._match_index = -1
            self.search_info_lbl.config(text="")
            self._update_match_list()
            self._redraw()
            return
        matches = set()
        order = []
        # ★ 按深度、sort_order 排序，这样回车跳转的顺序稳定
        for n in sorted(self.nodes.values(),
                        key=lambda x: (x.depth, x.sort_order,
                                       x.name.lower())):
            if q in (n.name or "").lower():
                matches.add(n.tag_id)
                order.append(n.tag_id)
        self._search_matches = matches
        self._match_order = order
        self._match_index = -1
        if matches:
            self.search_info_lbl.config(text=f"×{len(matches)}")
        else:
            self.search_info_lbl.config(text="×")
        self._update_match_list()
        self._redraw()

    # ---------------- ★ v24：搜索结果列表 ----------------
    def _update_match_list(self):
        """搜索框下面的结果列表：列出所有含该字符的标签。"""
        try:
            self._match_list.delete(0, "end")
        except Exception:
            return
        if not self.search_text:
            self._hide_match_list()
            return
        if not self._match_order:
            self._match_list.insert("end", "（没有匹配的标签）")
            self._match_list.itemconfig(0, foreground=theme_get("fg_dim"))
            self._match_list_selectable = False
            self._show_match_list(height=2)
            return
        self._match_list_selectable = True
        for tid in self._match_order:
            n = self.nodes.get(tid)
            if n is None:
                continue
            cnt = f"  ({n.count})" if n.count else ""
            depth = "    " * max(0, min(6, getattr(n, "depth", 0)))
            self._match_list.insert("end", f"{depth}{n.name}{cnt}")
        self._show_match_list(
            height=max(3, min(8, len(self._match_order))))

    def _show_match_list(self, height=None):
        """把结果列表放到搜索框下面（星图上方）。"""
        try:
            if height:
                self._match_list.config(height=int(height))
            if not self._match_list_visible:
                self._match_list.pack(fill="x", side="top", pady=(0, 4),
                                      before=self._body_frame)
                self._match_list_visible = True
        except Exception:
            pass
        self._sync_match_list_selection()

    def _hide_match_list(self):
        self._match_list_selectable = False
        if not self._match_list_visible:
            return
        try:
            self._match_list.pack_forget()
        except Exception:
            pass
        self._match_list_visible = False

    def _sync_match_list_selection(self):
        if not self._match_list_visible or not self._match_order:
            return
        idx = self._match_index if self._match_index >= 0 else 0
        if idx >= len(self._match_order):
            return
        self._syncing_list = True
        try:
            self._match_list.selection_clear(0, "end")
            self._match_list.selection_set(idx)
            self._match_list.activate(idx)
            self._match_list.see(idx)
        except Exception:
            pass
        finally:
            self._syncing_list = False

    def _on_match_list_select(self, event=None):
        """点结果列表里的某一行 → 跳到那个标签。"""
        if self._syncing_list or not self._match_list_selectable:
            return
        sel = self._match_list.curselection()
        if not sel:
            return
        i = int(sel[0])
        if i >= len(self._match_order):
            return
        self._goto_match_index(i)

    def _clear_search(self):
        if self._search_jump_job is not None:
            try:
                self.after_cancel(self._search_jump_job)
            except Exception:
                pass
            self._search_jump_job = None
        self.search_var.set("")
        self._hide_match_list()

    def _center_on_node(self, target):
        if target is None:
            return
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        wx_c = target.x + target.w / 2
        wy_c = target.y + target.h / 2
        try:
            region = self.canvas.cget("scrollregion")
            x0, y0, x1, y1 = map(float, str(region).split())
        except Exception:
            return
        W = max(1.0, x1 - x0)
        H = max(1.0, y1 - y0)
        view_cx = wx_c * self.scale - cw / 2
        view_cy = wy_c * self.scale - ch / 2
        fx = (view_cx - x0) / W
        fy = (view_cy - y0) / H
        self.canvas.xview_moveto(max(0.0, min(1.0, fx)))
        self.canvas.yview_moveto(max(0.0, min(1.0, fy)))
        self._view_x = self.canvas.canvasx(0)
        self._view_y = self.canvas.canvasy(0)
        self._redraw()

    def _edge_style_for(self, depth):
        """★ 第 depth 层用哪个连线颜色 / 多粗。

        ★★ 2026-10-07 新增。用户报：「上下游标签的颜色不够丰富，
          然后上级和下级标签之间没有分割线帮助强调视觉区别」。
        ★ 原来所有连线**同一个颜色** —— 看不出层级。
        ★ 现在按层给色（浅 → 深），并且越深越粗。
          · 颜色挑的是**中间调**，深浅两套皮肤都看得清（跟图标一个思路）
          · 循环取用，层数再多也不会没颜色
        """
        try:
            d = int(depth or 0)
        except Exception:
            d = 0
        if d < 0:
            d = 0
        d = d % len(self.EDGE_PALETTE)
        color, w = self.EDGE_PALETTE[d]
        return color, w

    def _draw_depth_badge(self, c, n, x, y, x1, y1, dark_bg=False):
        """★ 在节点左上角画一个「第 N 层」小徽章。

        ★★ 为什么用徽章代替"画一条分割线"：
          节点是**可以拖来拖去**的，硬画竖线很容易切到节点上，反而更乱。
          徽章跟着节点走，**不管怎么拖都不会错位**，而且一眼能看出层级。
        """
        try:
            if not bool(getattr(self, "_show_depth_badge", True)):
                return
            d = int(getattr(n, "depth", 0) or 0)
            color, _w = self._edge_style_for(d)
            txt = str(d + 1)
            # 徽章：节点左上角外侧一点点，小圆角方块 + 白字
            bx1 = x - 1
            by1 = y - 1
            bw = 17.0
            bh = 15.0
            c.create_rectangle(bx1, by1, bx1 + bw, by1 + bh,
                               fill=color, outline="", width=0)
            c.create_text(bx1 + bw / 2, by1 + bh / 2, text=txt,
                          fill="#ffffff",
                          font=(FONT, max(7, int(9)), BOLD))
        except Exception:
            pass

    def _goto_match_index(self, idx):
        """跳到第 idx 个匹配的标签（居中 + 同步结果列表选中）。"""
        if not self._match_order:
            return
        idx = max(0, min(len(self._match_order) - 1, int(idx)))
        self._match_index = idx
        n = self.nodes.get(self._match_order[idx])
        self._center_on_node(n)
        self.search_info_lbl.config(
            text=f"{idx + 1}/{len(self._match_order)}")
        self._sync_match_list_selection()

    def _goto_first_match(self):
        self._search_jump_job = None
        if not self._match_order:
            return
        self._goto_match_index(0)

    def _goto_next_match(self):
        if not self._match_order:
            return
        idx = 0 if self._match_index < 0 else (
            (self._match_index + 1) % len(self._match_order))
        self._goto_match_index(idx)

    def _goto_prev_match(self):
        if not self._match_order:
            return
        idx = (len(self._match_order) - 1 if self._match_index < 0 else
               (self._match_index - 1) % len(self._match_order))
        self._goto_match_index(idx)

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

    # ---------------- 数据加载 ----------------
    def reload(self, store):
        tags, relations = store.all_tags_with_relations()
        self.nodes = {}
        for tid, name, color, cnt, so in tags:
            self.nodes[tid] = _TNode(tid, name, color, cnt, so)
        self.edges = set()
        for pid, cid in relations:
            if pid in self.nodes and cid in self.nodes:
                self.edges.add((pid, cid))
                self.nodes[pid].children.append(self.nodes[cid])
                self.nodes[cid].parents.append(self.nodes[pid])

        self._compute_sizes()
        # ★ 从 store 加载位置
        self._positions = store.get_all_tag_positions()
        self._fallback_layout_if_needed()
        self._apply_positions()

        # ★ 从 store 加载线颜色
        try:
            saved_colors = store.get_all_edge_colors()
        except Exception:
            saved_colors = {}
        self.custom_line_colors = {
            k: v for k, v in saved_colors.items() if k in self.edges
        }

        self._update_scrollregion()
        self.after(50, self._update_scrollregion)
        self.after(200, self._update_scrollregion)

        if self.search_text:
            self._do_search()
        else:
            self._redraw()
        valid = set(self.nodes.keys())
        self.selected_ids &= valid

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
            # ★★ 2026-10-03：同上 —— 标签库缩略图里的字号也统一成
            #   UI_FONT_SIZE（以前按层级从 14 一路降到 8）。
            fs = UI_FONT_SIZE
            n.font_size = fs
            f = tkfont.Font(family=FONT, size=fs, weight=BOLD)
            f2 = tkfont.Font(family=FONT, size=UI_FONT_SIZE)
            tw = f.measure(n.name)
            tw2 = f2.measure(f"  {n.count}")
            n.w = tw + tw2 + self.NODE_PAD * 2 + 10
            n.h = fs + 14

    def _fallback_layout_if_needed(self):
        """给没有保存过位置的节点一个合理的默认位置。"""
        missing = [n for n in self.nodes.values() if n.tag_id not in self._positions]
        if not missing:
            return
        # 已有的节点放到右下角之外；否则从左上开始铺
        base_x = 30.0
        base_y = 30.0
        if self._positions:
            base_x = max((p[0] for p in self._positions.values()), default=30.0) + 200
            base_y = min((p[1] for p in self._positions.values()), default=30.0)
        y = base_y
        for n in missing:
            self._positions[n.tag_id] = (base_x, y)
            y += n.h + 16

    def _apply_positions(self):
        for tid, n in self.nodes.items():
            if tid in self._positions:
                x, y = self._positions[tid]
                n.x = float(x)
                n.y = float(y)

    def _world_to_canvas(self, wx, wy):
        # 世界坐标 -> canvas 坐标，滚动由 Tk 自动处理
        return wx * self.scale, wy * self.scale


    def _update_scrollregion(self):
        """★★★ 算画布可以滚到多大（错题本 #181）。

        ★★ 2026-10-08 改（用户要"画布无限大"）：
          原来只按"节点范围 + 120"算 —— **画布刚好裹住内容**：
            · 节点一贴边就没法再往外拖
            · 空白处想放个新节点也没地方
          ★ 现在四周留 `CANVAS_MARGIN`（4000 逻辑像素）的空白，
            而且**至少是"视口大小的两倍"** ——
            这样不管内容多少，"往外拖/往外滚"**永远有地方**。
          ★★ 判据：**"无限画布"的实际做法 = 留足够大的空白**，
            而不是真的把 scrollregion 设成无穷（滚动条会废掉）。
        """
        M = float(self.CANVAS_MARGIN)
        if not self.nodes:
            min_x, min_y = 0.0, 0.0
            max_x, max_y = 300.0, 300.0
        else:
            min_x = min((n.x for n in self.nodes.values()), default=0.0)
            min_y = min((n.y for n in self.nodes.values()), default=0.0)
            max_x = max((n.x + n.w for n in self.nodes.values()), default=200.0)
            max_y = max((n.y + n.h for n in self.nodes.values()), default=200.0)
        # ★ 四周留白：比原来那 60/120 大得多
        min_x = min(0.0, min_x - M)
        min_y = min(0.0, min_y - M)
        max_x = max_x + M
        max_y = max_y + M
        # ★★ 再保证"至少视口的两倍" ——
        #   内容很小的时候（比如只有 3 个标签），留白也要够拖
        try:
            vw = max(1, self.canvas.winfo_width())
            vh = max(1, self.canvas.winfo_height())
            need_w = (vw * 2.0) / max(self.scale, 1e-6)
            need_h = (vh * 2.0) / max(self.scale, 1e-6)
            if max_x - min_x < need_w:
                max_x = min_x + need_w
            if max_y - min_y < need_h:
                max_y = min_y + need_h
        except Exception:
            pass
        self.canvas.configure(
            scrollregion=(min_x * self.scale, min_y * self.scale,
                          max_x * self.scale, max_y * self.scale))

    def _on_xscroll(self, *args):
        self.canvas.xview(*args)
        self._view_x = self.canvas.canvasx(0)
        self._redraw()

    def _on_yscroll(self, *args):
        self.canvas.yview(*args)
        self._view_y = self.canvas.canvasy(0)
        self._redraw()

    def reset_view(self):
        self.scale = 1.0
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

    def zoom_center(self, factor):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        self._zoom_at(w // 2, h // 2, factor)

    def _zoom_at(self, sx, sy, factor):
        new_scale = max(self.MIN_SCALE, min(self.MAX_SCALE, self.scale * factor))
        if abs(new_scale - self.scale) < 1e-6:
            return
        cx = self.canvas.canvasx(sx)
        cy = self.canvas.canvasy(sy)
        wx = cx / self.scale
        wy = cy / self.scale
        self.scale = new_scale
        self._update_scrollregion()
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
        # ★★★ 缩放用 `_redraw_soon` —— Ctrl+滚轮**一次能滚好几格**，
        #   每格都全量重画的话就卡（错题本 #185）。
        self._redraw_soon()

    def _visible_world_rect(self, pad=120.0):
        """★★★ 当前**看得见的那块世界坐标**（错题本 #185）。

        ★ 为什么要它：用户报「标签星图一卡一卡的」。
          ★★ 真因：`_redraw()` 是 `delete("all")` + **把 230 个标签全画一遍** ——
            每个标签 3~5 个图元（矩形 + 层级徽章 + 名字 + 计数）+ 每条连线，
            总共 **1000+ 个 Tk 图元**；而**滚动、平移、缩放、点选**每次都重画全部 →
            ★★★ **一帧就要几万次 Tcl 调用**，肉眼就是"一卡一卡"。
        ★ 修法：**只画"看得见的那块 + 一圈余量"里的东西**（视口裁剪）。
          ★ 这和"只渲染看得见的 PDF 页"是同一个套路（预览窗格早就这么干了）。
        ★ 返回值：`(min_x, min_y, max_x, max_y)`（**世界坐标**），
          算不出来时返回 `None`（= 不裁剪，全画 —— 宁可慢也别画不出来）。
        """
        try:
            c = self.canvas
            s = max(float(self.scale), 1e-6)
            x0 = c.canvasx(0) / s - pad
            y0 = c.canvasy(0) / s - pad
            w = max(1, c.winfo_width()) / s + pad * 2
            h = max(1, c.winfo_height()) / s + pad * 2
            return (x0, y0, x0 + w, y0 + h)
        except Exception:
            return None

    def _in_rect(self, n, rect):
        """★ 节点 `n` 跟"看得见的那块"有没有交叠。`rect=None` 一律算有。"""
        if rect is None:
            return True
        try:
            x0, y0, x1, y1 = rect
            return not (n.x + n.w < x0 or n.x > x1
                        or n.y + n.h < y0 or n.y > y1)
        except Exception:
            return True

    def _redraw(self):
        c = self.canvas
        c.delete("all")
        self._node_boxes = []
        s = self.scale

        if not self.nodes:
            w = c.winfo_width() or 260
            # ★★ 2026-10-07：颜色原来**写死** "#9aa0a6"（浅色模式的次要字色），
            #   夜间在深画布上偏暗。改用主题色。
            c.create_text(w // 2, 40, text=T("（还没有标签，去星图里新建）"),
                          fill=theme_get("fg_dim"), font=(FONT, UI_FONT_SIZE))
            return

        # ★★★ 2026-10-08：**先算出"看得见的那块"**（视口裁剪，错题本 #185）
        #   ★★ 这是治"一卡一卡"的**关键一步** ——
        #     230 个标签里通常只有十几个在屏幕上，**其余的画了也白画**。
        _vis = self._visible_world_rect()
        _vis_nodes = [n for n in self.nodes.values() if self._in_rect(n, _vis)]
        _vis_ids = {n.tag_id for n in _vis_nodes}

        for (pid, cid) in self.edges:
            # ★ 连线的两端**都不在可见区**就跳过（画了也看不见）
            if _vis is not None and pid not in _vis_ids and cid not in _vis_ids:
                continue
            p = self.nodes.get(pid)
            ch = self.nodes.get(cid)
            if p is None or ch is None:
                continue
            x1, y1 = self._world_to_canvas(p.x + p.w, p.y + p.h / 2)
            x2, y2 = self._world_to_canvas(ch.x, ch.y + ch.h / 2)
            cx1 = x1 + max(15.0, abs(x2 - x1) * 0.45)
            cx2 = x2 - max(15.0, abs(x2 - x1) * 0.45)
            # ★ 优先用自定义线颜色
            if (pid, cid) in self.custom_line_colors:
                line_color = self.custom_line_colors[(pid, cid)]
                _base_w = 1.4
            else:
                # ★★ 2026-10-07 按**层级**给连线不同颜色 + 不同粗细
                #   （用户报：「上下游标签的颜色不够丰富，
                #     然后上级和下级标签之间没有分割线帮助强调视觉区别」）。
                #   原来所有连线都是**同一个色** `DEFAULT_EDGE_COLOR`
                #   —— 光靠连线**完全看不出是第几层**。
                #   ★ 现在：第几层用第几档颜色（越深越"重"），
                #     并且**越深的层线越粗** —— 扫一眼就知道走到哪一层了。
                line_color, _base_w = self._edge_style_for(p.depth)
            if self.search_text:
                pid_match = pid in self._search_matches
                cid_match = cid in self._search_matches
                if not (pid_match or cid_match):
                    line_color = theme_get("line")
                    _base_w = 1.0
            c.create_line(x1, y1, cx1, y1, cx2, y2, x2, y2,
                          fill=line_color, width=max(1, _base_w * s),
                          smooth=True, arrow="last",
                          arrowshape=(8 * s, 10 * s, 3 * s))

        # ★★ 2026-10-07 新增：**层级之间的分隔提示**（用户要的"分割线"）。
        #   为什么在画布上画虚线不好：节点位置是**拖来拖去**的，
        #   硬画一条竖线很容易切到节点上，反而更乱。
        #   ★ 改用更稳的做法：**给每个节点加一个"第几层"的小徽章**
        #     （左上角一个小圆角标签，写着 1/2/3），
        #     颜色跟该层连线同色 —— 这样"层级"一眼就看得出来，
        #     而且不管节点怎么拖都不会错位。
        try:
            _badge_on = bool(getattr(self, "_show_depth_badge", True))
        except Exception:
            _badge_on = True

        for n in self.nodes.values():
            # ★★★ 看不见的节点**直接跳过**（视口裁剪，错题本 #185）
            if not self._in_rect(n, _vis):
                continue
            x, y = self._world_to_canvas(n.x, n.y)
            w = n.w * s
            h = n.h * s
            selected = (n.tag_id in self.selected_ids)
            is_match = (n.tag_id in self._search_matches)
            faded = bool(self.search_text) and not is_match

            # ★★ 2026-10-07 同一个毛病（标签库这边也有一份）：
            #   原来 `outline = "#2c3e50"` 写死的深蓝黑，夜间看不出选中。
            #   改成跟星图一致的写法（用主题 accent + 加粗）。
            if selected:
                outline = theme_get("accent")
            elif is_match:
                outline = theme_get("warn")
            else:
                outline = theme_get("card_bg")
            ow = max(2, (4 if selected else (3 if is_match else 1.6)) * s)

            fill_color = n.color if not faded else self._fade_color(n.color)

            c.create_rectangle(x, y, x + w, y + h,
                               fill=fill_color, outline=outline, width=ow)
            # ★★ 2026-10-07：左上角画「第 N 层」小徽章（用户要的"分割/区分"）
            self._draw_depth_badge(c, n, x, y, x + w, y + h)
            # ★ 文字左边留一点，别被徽章压住
            _txt_x = (x + 22 * s) if getattr(self, "_show_depth_badge", True) \
                else (x + 8 * s)
            fg = text_color_for(fill_color)
            fs = max(7, int(n.font_size * s))
            c.create_text(_txt_x, y + h / 2, text=n.name,
                          anchor="w", fill=fg,
                          font=(FONT, fs, BOLD))
            c.create_text(x + w - 6 * s, y + h / 2, text=str(n.count),
                          anchor="e", fill=fg,
                          font=(FONT, max(7, fs - 2)))
            self._node_boxes.append((x, y, x + w, y + h,
                                     n.tag_id, n.name, n.color))

    def _node_at_canvas(self, cx, cy):
        # 反向遍历：后画的（新建的）节点优先被点中
        for (x0, y0, x1, y1, tid, name, color) in reversed(self._node_boxes):
            if x0 <= cx <= x1 and y0 <= cy <= y1:
                return (tid, name, color)
        return None

    def _on_wheel(self, event):
        if event.state & 0x0004:
            cx = self.canvas.canvasx(event.x)
            cy = self.canvas.canvasy(event.y)
            factor = 1.15 if (event.delta > 0 or event.num == 4) else (1 / 1.15)
            self._zoom_at(cx, cy, factor)
            return "break"
        if event.num == 4:
            d = -2
        elif event.num == 5:
            d = 2
        else:
            d = -2 if event.delta > 0 else 2
        self.canvas.yview_scroll(d, "units")
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
                self.canvas.configure(cursor="")
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
                self.canvas.configure(cursor="")
            except Exception:
                pass

    def _redraw_soon(self, delay=16):
        """★★★ "稍后重画一次"（合并同一帧里的多次请求，错题本 #185）。

        ★ 为什么要它：`_apply_view_offset`（空格平移）/ `_on_wheel`（滚轮）
          **每秒能触发几十上百次**，每次都 `delete("all")` + 全量重画 →
          ★★ 一次滚动能重画几十遍，**白白烧掉几十倍的 Tk 调用**。
        ★ 做法：**一帧最多重画一次**（`after(16, ...)` ≈ 60fps），
          这期间来的请求都合并掉。
        ★★ 判据：**"连续事件"要节流（throttle），不能每来一个就干一遍。**
          （同类问题：拖窗格重渲染 PDF —— 那边用的是 700ms 防抖）
        """
        try:
            if getattr(self, "_redraw_job", None) is not None:
                return                      # ★ 已经排了一个，不重复排
            self._redraw_job = self.after(delay, self._redraw_now)
        except Exception:
            # ★ 排不上就直接画（宁可慢，不能没反应）
            try:
                self._redraw()
            except Exception:
                pass

    def _redraw_now(self):
        self._redraw_job = None
        try:
            self._redraw()
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
        # ★★★ 这里原来直接 `_redraw()` —— 而它是**鼠标每动一下就调一次**，
        #   于是"空格+拖动平移"会**每毫秒重画全部节点**（错题本 #185）。
        #   改成 `_redraw_soon()`：一帧最多画一次（合并掉多余的）。
        self._redraw_soon()

    def _on_press(self, event):
        self.canvas.focus_set()
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        if self._space_down:
            self._pan_active = True
            self._pan_last = (event.x, event.y)
            try:
                self.canvas.configure(cursor="fleur")
            except Exception:
                pass
            return
        hit = self._node_at_canvas(cx, cy)
        self._press_xy = (event.x_root, event.y_root)
        self._press_node = hit
        self._dragging = False
        self._drag_name = None

    def _on_motion(self, event):
        if self._pan_active and self._pan_last is not None:
            dx = event.x - self._pan_last[0]
            dy = event.y - self._pan_last[1]
            self._pan_last = (event.x, event.y)
            self._view_x -= dx
            self._view_y -= dy
            self._apply_view_offset()
            return
        if self._press_xy is None:
            return
        dx = abs(event.x_root - self._press_xy[0])
        dy = abs(event.y_root - self._press_xy[1])
        if not self._dragging and (dx > 6 or dy > 6):
            if self._press_node is None:
                return
            self._dragging = True
            tid, name, color = self._press_node
            self._drag_name = name
            self._drag_color = color
            self._drag_tid = tid
            self._create_drag_window(event.x_root, event.y_root)
            # ★ v25 补丁42：告诉标签盒「我拖着标签在走了」——
            #   这样你可以直接把它拖进标签盒（拖进去时盒子会亮绿边）。
            try:
                _app = getattr(self, "app", None)
                if _app is not None and getattr(_app, "tagbox", None):
                    _app.tagbox.begin_watch_drag(tid, name, color)
            except Exception:
                pass
        if self._dragging:
            self._move_drag_window(event.x_root, event.y_root)

    def _on_release(self, event):
        if self._pan_active:
            self._pan_active = False
            self._pan_last = None
            if not self._space_down:
                try:
                    self.canvas.configure(cursor="")
                except Exception:
                    pass
            return
        was_dragging = self._dragging
        drag_name = self._drag_name
        self._destroy_drag_window()
        self._press_xy = None
        self._press_node = None
        self._dragging = False
        self._drag_name = None
        self._drag_color = None
        if was_dragging and drag_name:
            # ★ v25 补丁42：**先问标签盒要不要**。
            #   松手的位置如果落在标签盒上 → 收进盒子，就不再当「拖到文件上」。
            _taken = False
            try:
                _app = getattr(self, "app", None)
                tb = getattr(_app, "tagbox", None) if _app is not None else None
                if tb is not None:
                    _taken = bool(tb.end_watch_drag(event.x_root, event.y_root))
            except Exception:
                _taken = False
            if _taken:
                return
            if self.on_drop_on_file:
                self.on_drop_on_file(drag_name, event.x_root, event.y_root)
            return
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        hit = self._node_at_canvas(cx, cy)
        ctrl = bool(event.state & 0x0004)
        if hit is None:
            if not ctrl and self.selected_ids:
                self.selected_ids.clear()
                self._redraw()
            return
        tid = hit[0]
        if ctrl:
            if tid in self.selected_ids:
                self.selected_ids.discard(tid)
            else:
                self.selected_ids.add(tid)
        else:
            self.selected_ids = {tid}
        self._redraw()

    def _on_double(self, event):
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        hit = self._node_at_canvas(cx, cy)
        if hit and self.on_double_click:
            tid, name, color = hit
            self.on_double_click(tid, name)

    def _on_right(self, event):
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        hit = self._node_at_canvas(cx, cy)
        if hit and self.on_context_menu:
            tid, name, color = hit
            self.on_context_menu(event, tid, name)

    def _create_drag_window(self, x, y):
        self._destroy_drag_window()
        win = tk.Toplevel(self.winfo_toplevel())
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
        win.overrideredirect(True)
        try:
            win.attributes("-topmost", True)
        except Exception:
            pass
        tk.Label(win, text="  " + (self._drag_name or ""),
                 bg=self._drag_color or "#3498db", fg="white",
                 font=(FONT, UI_FONT_SIZE), padx=8, pady=4).pack()
        self._drag_win = win
        self._move_drag_window(x, y)

    def _move_drag_window(self, x, y):
        if self._drag_win is not None:
            try:
                self._drag_win.geometry(f"+{x + 14}+{y + 14}")
            except Exception:
                pass

    def _destroy_drag_window(self):
        if self._drag_win is not None:
            try:
                self._drag_win.withdraw()
                self._drag_win.destroy()
            except Exception:
                pass
            self._drag_win = None


# ---------- 兜底（★ 但注意：它会吃掉错误，所以要专门测"用的哪一份"）----------
def _fallback():
    g = globals()
    for _n in _NEED:
        if g.get(_n) is None:
            g[_n] = _Borrowed(_n)


_fallback()
