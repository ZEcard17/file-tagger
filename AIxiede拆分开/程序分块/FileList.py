# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：FileList。

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
   · import 要写 `from FileList import …`（**不带包路径**）
   · `_set_app` 要**取别名**（`as _fk_…`）—— 模块名和类名同名
   · 借名字清单**用 symtable + dir() 定**，别用正则猜
   · 代理类**必须实现 `__call__`**（函数也会被借）
   · ★ 兜底 except 会吃掉错误 → **必须专门测"用的哪一份"**
"""
import os
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, colorchooser

# ---------- 要向主程序借的名字 ----------
_MUTABLE = ['APP_CLOSING', 'BOLD', 'FONT', 'HAS_PIL', 'UI_FONT_SIZE', 'UI_FONT_SIZE_SMALL']
_NEED = ['APP_CLOSING', 'BOLD', 'FONT', 'HAS_CV2', 'HAS_PIL', 'HAS_WIN32', 'IMAGE_EXTS', 'Image', 'ImageTk', 'T', 'UI_FONT_SIZE', 'UI_FONT_SIZE_SMALL', 'VIDEO_EXTS', '_alt_down', '_themes_now', 'cv2', 'dark_mode_now', 'deque', 'get_file_icon', 'icon_for_file', 'icon_for_file_dark', 'load_ui_setting', 'make_search_label', 'note_swallowed', 'os', 'register_themed', 'text_color_for', 'theme_get', 'threading', 'time', 'win32con', 'win32gui', 'win32ui']
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
                # ★★★ 一律包代理（错题本 #168）：
                #   模块的桩可能跑在**主程序还没定义这个名字**之前，
                #   所以「启动时取快照」必然借不到。
                #   ★ 代理是**读的时候才现取**，什么时候定义都不影响。
                g[_n] = _Borrowed(_n)
        except Exception:
            pass


class FileList(tk.Frame):
    HEADER_H_BASE = 30
    PAD = 10
    GAP = 8
    # ★ v25 补丁21：文件列表左右永远留白条（学 Windows 资源管理器）——
    #   这样不管文件夹多满，左右两边都有一块「空白」可以按住拉方框。
    #   左边窄一点（约 18 像素，资源管理器那条细边），右边宽一点（60）。
    SIDE_STRIP_L = 18
    SIDE_STRIP_R = 60

    # ★★ v26（2026-10-01）：**这个表的第 3 个数是「缩略图档位对应的文字大小」。**
    #   用户反馈「整个程序的字体大小能不能和右下角那些按钮一样」——
    #   右下角按钮用的是 Tk 默认字体 size=14，而这里原来最大才 22、
    #   默认（极小）只有 9，和 14 差了一大截，看着就是「大小不匀称」。
    #   现在整体上移到和 UI_FONT_SIZE 对齐：
    #     · 默认档（极小）就是 UI_FONT_SIZE；
    #     · 往后每档 +2，最大档是给「超大缩略图」配的，字也跟着大才好看。
    #   注意：这只是**列表里的文字大小**，跟着缩略图档位走；
    #   想整体调，改 UI_FONT_SIZE 就行。
    # ★★★ 2026-10-08 改成"跟着字高算"，不再写死像素 ★★★
    #   用户报：「文件列表的 **emoji 大小和字体大小总是不太匹配**」（待清算 #16）。
    #   ★ 实测真因（量出来的，铁证）：
    #       缩放 100% → 字高 25，最小档图标 22  → 差 −3  ✔ 基本齐
    #       缩放 125% → 字高 30，最小档图标 22  → 差 −8  ★ 明显小
    #       缩放 150% → 字高 36，最小档图标 22  → 差 −14 ★ 小一大截
    #     → **字在长大、图标纹丝不动**（因为像素值是写死的 22/30/44/64/96/128）。
    #   ★ 修法：**以"字高"为基准算图标大小** ——
    #     基准档（极小）= 字高（这样图标和字**天生齐平**），
    #     往后每档乘一个固定倍数（1.35 左右，六档拉开）。
    #   ★ 为什么用"字高的倍数"而不是"UI_FONT_SIZE 的倍数"：
    #     真正决定"视觉上齐不齐"的是**字高（linespace）**，不是字号 ——
    #     同一个字号在不同 DPI/字体下 linespace 不一样。
    #   ★ 有兜底：万一量不到字高（字体还没建好），退回原来的写死值。
    _ICON_STEPS = (1.0, 1.35, 1.95, 2.8, 4.2, 5.6)

    @classmethod
    def _icon_px_table(cls):
        """★ 六档图标像素 —— **按字高算**（跟着缩放走）。

        返回 [(档名, 图标像素, 字号), ...]。
        ★ 算不出来时退回一份保守的写死值（保证程序永远能跑）。
        """
        names = ("极小", "小", "中", "大", "特大", "超大")
        try:
            import tkinter.font as _tf
            f = _tf.Font(family=FONT, size=UI_FONT_SIZE)
            ls = float(f.metrics("linespace"))
        except Exception:
            ls = 0.0
        if ls <= 4:
            # 兜底：字体还没建好 —— 用一套"按 UI_FONT_SIZE 估"的值
            ls = float(UI_FONT_SIZE) + 11
        out = []
        for nm, mul in zip(names, cls._ICON_STEPS):
            px = int(round(ls * mul))
            # 夹在合理范围：最小别比字矮，最大别离谱
            px = max(int(ls), min(px, 320))
            out.append((nm, px, UI_FONT_SIZE))
        return out

    # ★★ 兼容老写法：`FileList.ICON_SIZES` 仍然可用（就是上面那个函数的结果）
    #   ★★ 2026-10-08 踩坑记录（写清楚，别再用错）：
    #     我第一版把这个做成了 `@property` —— **运行时报
    #     `TypeError: 'property' object is not iterable`**。
    #     原因：`@property` 只在**实例**上生效（`self.ICON_SIZES`）；
    #     而**类上访问**（`FileList.ICON_SIZES`）拿到的是 property 对象本身。
    #     ★ 本程序里**两处都有**：`self.icon_sizes()`（实例）
    #       和 `FileList.icon_sizes()`（类，在别的地方读档位名）。
    #     → 所以**不能用 property**，用"类方法 + 缓存"最稳。
    @classmethod
    def icon_sizes(cls):
        """★ 六档图标表的**正式入口**（类/实例都能调）。

        ★ `FileList.ICON_SIZES` / `self.ICON_SIZES` 也还能用 ——
          由一个"每次访问都算一次（带缓存）"的普通类属性兜着（见下面
          `_ICON_SIZES_FALLBACK` 的说明）。
        """
        try:
            cached = getattr(cls, "_icon_cache", None)
            if cached:
                return cached
            tbl = cls._icon_px_table()
            cls._icon_cache = tbl
            return tbl
        except Exception:
            return [("极小", 22, UI_FONT_SIZE), ("小", 30, UI_FONT_SIZE),
                    ("中", 44, UI_FONT_SIZE), ("大", 64, UI_FONT_SIZE),
                    ("特大", 96, UI_FONT_SIZE), ("超大", 128, UI_FONT_SIZE)]

    @classmethod
    def refresh_icon_sizes(cls):
        """★ 清掉缓存 —— 换了缩放/皮肤之后调一次，让图标重新按新字高算。

        ★ 为什么需要：`icon_sizes()` 会缓存（免得每次重画都建 Font 对象）。
          缩放一变、字高就变了，**必须清掉缓存**，否则还是旧尺寸。
        """
        try:
            cls._icon_cache = None
        except Exception:
            pass

    # ★★ v26：默认列宽原来加起来 **920 像素**（260+70+90+240+260），
    #   而列表实际只有 814 宽（右边还开着标签库面板时会更窄）——
    #   于是「名称」列被挤到 200 出头，**文件名左边直接被切掉**
    #   （用识图看截图才发现：`机器抉择.txt` 显示成了 `器块择.txt`）。
    #   现在按「实际可用宽度」**自动分配**（见 _auto_fit_cols），
    #   名称列永远优先拿够，剩下几列按比例分。
    DEFAULT_COL_W = {
        "name": 300,
        "kind": 70,
        "size": 90,
        "location": 200,
        "tags": 320,     # ★ 2026-10-03：240 → 320，标签列默认更宽，能显示更多标签
    }
    MIN_COL_W = {
        "name": 100, "kind": 46, "size": 60,
        "location": 80, "tags": 80,
    }

    GRID_MAX_TAG_LINES = 3

    def __init__(self, master, on_select=None, on_double=None, on_right_click=None,
                 tagbar_parent=None):
        super().__init__(master)
        # ★★ 2026-10-07 修「点了几下（切了皮肤）文件列表就变白底/浅灰字」★★
        #   真因：`FileList` 是个 `tk.Frame`，**建的时候没设 bg** ——
        #   于是它的底色靠 `_retheme_tree()` 那套「按对照表翻色」来刷。
        #   而那套逻辑是**从浅色往深色翻**的：
        #     切白天时它还是 `#1e1f22`（该变白却没变），
        #     切夜间时它变成 `#d6d7db`（**底色被当成字色翻了**）。
        #   → **每切一次皮肤颜色就偏一次**，用户看到的就是
        #     「点了几下就又不彩了 / 又变白了」。
        #   ★ 修法：**自己从主题取底色**，不依赖那套翻色表
        #     （`theme_get` 永远给的是"当前皮肤该有的正确颜色"）。
        #   ★ 同时 `_redraw()` 里也是用 `theme_get`，两边一致，不会再偏。
        try:
            self.configure(bg=theme_get("card_bg"))
        except Exception:
            pass
        self.on_select = on_select
        self.on_double = on_double
        self.on_right_click = on_right_click
        # ★ v25 补丁7：标签条改挂在「整个窗口底部」（和「🔔 问题 / 📋 输出」
        #   一个套路），不再是文件列表这一列里的一行。所以它的父窗口
        #   由外面传进来（= 主窗口）；没传就退回老做法（挂在列表自己身上）。
        self._tagbar_parent = tagbar_parent or self
        self.on_tagbar_visibility = None   # 主程序注入：真正负责 pack / pack_forget
        # ★★ v26 补丁（2026-10-03）：主程序注入「检查一下文件列表标题有没有
        #   被撑成竖直书写」的处理方法（见 _ensure_canvas_size 里的说明）。
        self.on_fix_title = None

        self.rows = []
        self._all_rows = []
        self.search_text = ""
        # ★ v25：关键字已经在主程序那边过滤过了（含子目录搜索 /
        #   分类·全部文件搜索），这里就不要再按「文件名/标签/路径」
        #   开关二次过滤一遍 —— 否则关掉「文件名」开关时结果会
        #   被过滤成空列表。
        self.search_external = False

        # ★ 三个搜索开关
        self.search_by_name = tk.BooleanVar(value=True)
        self.search_by_tag = tk.BooleanVar(value=True)
        self.search_by_location = tk.BooleanVar(value=False)

        self.selected_paths = set()
        self.last_clicked_path = None

        self.layout_mode = "list"

        self.icon_level = 0
        self.icon_px = self.icon_sizes()[0][1]
        self.base_font_size = self.icon_sizes()[0][2]

        self.font = tkfont.Font(family=FONT, size=self.base_font_size)
        # ★★ 2026-10-03：用户要求「每个有文字的地方都和右下角那些按钮
        #   （标签条 / 标签盒 / 问题…）一样大」——
        #   于是文件列表里的三种字（正文 / 次要 / 标签）**全部锁死在
        #   UI_FONT_SIZE（14）**，不再一层比一层小。
        #   （以前是 14 / 13 / 13，用户看着觉得不匀。）
        self.font_small = tkfont.Font(family=FONT, size=UI_FONT_SIZE)
        self.font_tag = tkfont.Font(family=FONT, size=UI_FONT_SIZE,
                                    weight=BOLD)
        self.font_header = tkfont.Font(family=FONT, size=UI_FONT_SIZE, weight=BOLD)

        self.col_w = dict(self.DEFAULT_COL_W)
        # ★ v25 补丁41：用户是不是**手动拖过「名称」列**的宽度。
        #   拖过就不再自动把它撑满窗口（见 _list_cols / _on_header_drag）。
        self._name_col_manual = False

        self.sort_key = None
        self.sort_asc = True

        self._thumbs = {}
        self._thumb_failed = set()
        # ★ v26：缩略图**后台加载**用的东西（见 _get_thumbnail 的说明）。
        #   _thumb_loading = 正在后台读的（避免同一个文件排好几次队）
        #   _thumb_queue   = 等着读的
        #   _thumb_running = 后台线程在不在跑（只允许一个，别开一堆抢磁盘）
        self._thumb_loading = set()
        self._thumb_queue = deque()
        self._thumb_lock = threading.Lock()
        self._thumb_running = False

        self._layout = []
        self._total_h = 0
        self._total_w = 0

        self._header_drag_col = None
        self._header_drag_start_x = 0
        self._header_drag_start_w = 0
        self._header_press_x = None
        self._header_press_col = None

        # ================= ★ 搜索栏 =================
        self._sbar = ttk.Frame(self)
        self._sbar.pack(fill="x", pady=(0, 2))
        sbar = self._sbar
        make_search_label(sbar, T("搜索文件：")).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(sbar, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(4, 0))
        self.search_var.trace_add("write", lambda *a: self._on_search_changed())
        # ★ 回车：如果打开了"含子目录"，就触发递归搜索
        self.search_entry.bind(
            "<Return>", lambda e: self._trigger_search())
        ttk.Button(sbar, text=T("清除"), width=6,
                   command=lambda: self.search_var.set("")).pack(
            side="left", padx=(4, 4))

        # ★ "含子目录"开关：打开后按回车触发主程序递归扫描
        self.search_recursive = tk.BooleanVar(value=False)
        self._toggle_rec = self._make_toggle(
            sbar, T("含子目录"), self.search_recursive)
        self.on_recursive_search = None  # 主程序注入的回调

        # 三个开关：名称、标签、路径
        self._toggle_name = self._make_toggle(
            sbar, T("文件名"), self.search_by_name)
        self._toggle_tag = self._make_toggle(
            sbar, T("标签"), self.search_by_tag)
        self._toggle_loc = self._make_toggle(
            sbar, T("文件路径"), self.search_by_location)

        self.search_info_lbl = ttk.Label(sbar, text="", foreground=theme_get("ok"))
        self.search_info_lbl.pack(side="left", padx=8)

        # ★ v25 补丁6：标签条改成「默认隐藏」—— 和「🔔 问题 / 📋 输出」一个套路，
        #   开关按钮挪到了窗口右下角状态栏（主程序里的 self._tagbar_btn）。
        #   以前这里是搜索栏右边一个绿色「🏷 标签条」小标签，占横向地方、
        #   而且跟下面那排开关挤在一起容易看错。
        self.tagbar_visible = False
        self._tagbar_info_text = ""      # 标签条最右端那行「目录 共 N 项…」
        # ★ v25 补丁11：标签条的「小缓存」—— 标签集合没变时只改样式、
        #   不销毁重建控件（Tk 销毁/重建 60 个控件实测量要 0.3~0.6 秒，
        #   而只改样式只要几毫秒。这就是「点标签就卡」的根源）。
        self._tagbar_sig = None          # 上一轮画的是什么（标签集合+宽度+范围…）
        self._tagbar_pills = {}          # {tag_id: 那个标签胶囊控件}
        self._tagbar_left = None         # 左边那一竖列（小字 + 按钮）
        self._tagbar_holder = None       # 装标签胶囊的容器
        self._tagbar_scope_btn = None    # 「范围：当前页/整个视图」按钮
        self._tagbar_mode_btn = None     # 「全部满足/任一满足」按钮
        self._tagbar_clear_btn = None    # 「清除筛选（已选 N）」
        self._tagbar_show_btn = None     # 「全部显示（已屏蔽 N）」
        # =============================================

        # ================= ★ 标签条 =================
        self.filter_tag_ids = set()
        self.filter_match_all = False
        self.hidden_tag_ids = set()
        self._tagbar_buttons = []
        # ★ v24：标签条作用范围
        #   "page" = 当前页（默认，只统计/筛选这一页，秒回）
        #   "view" = 整个视图（分类库 / 全部文件 / 搜索结果的全集，
        #            统计和筛选都交给主程序查库，后台算）
        self.tag_scope = "page"
        self.tag_scope_stats = None    # 主程序算好的整库统计
        self.tag_scope_hint = None     # 统计中/失败时的提示
        self.on_tag_scope_changed = None  # 主程序注入：范围切换通知
        self.on_tag_filter_view = None    # 主程序注入：按整库标签重建视图
        self.tagbar = tk.Frame(self._tagbar_parent, bg=theme_get("panel_bg"),
                               highlightthickness=1,
                               highlightbackground=theme_get("line"))
        try:
            register_themed(self.tagbar, "panel")   # ★ 常驻控件 → 换皮肤时跟着刷
        except Exception:
            pass
        # ★ v25 补丁37：**关键修复** —— 不管标签条的父窗口是谁，先把它从
        #   父容器的几何管理里摘出去（forget）。
        #   为什么非做不可：标签条挂在主窗口底部时，如果它「从来没被 pack
        #   过但又被当作子控件创建」，Tk 在重算几何时仍会给它留位；实测的
        #   后果是明明没显示标签条，**文件列表那一整块被挤成 1 像素高**。
        #   而画布一旦只有 1 像素，Tk 就不再往它投递鼠标事件 ——
        #   用户看到的正是「单击没法选中文件，只可以框选」（框选靠拖动，
        #   偶尔还能收到）。forget() 之后，没显示就是真的不占地方。
        try:
            self.tagbar.pack_forget()
        except Exception:
            pass
        try:
            self.tagbar.grid_forget()
        except Exception:
            pass
        try:
            self.tagbar.place_forget()
        except Exception:
            pass
        # ★ v25 补丁6/7：这里**故意不 pack** —— 默认就是隐藏的，
        #   点右下角状态栏的「🏷 标签条」按钮才会显示（见 set_tagbar_visible）。
        self._tagbar_render_job = None
        self._tagbar_last_w = 0
        self.tagbar.bind("<Configure>", self._on_tagbar_configure)
        # ============================================

        self.header = tk.Canvas(self, height=self.HEADER_H_BASE, bg=theme_get("win_bg"),
                                highlightthickness=0)
        # ★★ 2026-10-07 登记"我是窗口底色"（用户报「**名称/类型/大小/所在位置/
        #   标签** 这一行是**反色的**」）。
        #   真因：表头是个 `tk.Canvas`，`bg=theme_get("win_bg")` **只在建的时候设一次** ——
        #   换皮肤时它不跟着变（跟 sidebar / file_list 一模一样的病）。
        #   ★ 登记之后由 `apply_themed()` 按当前皮肤刷，**不走那张会翻歪的对照表**。
        try:
            register_themed(self.header, "win")
        except Exception:
            pass
        # ★ v25 补丁37：**先把文件列表本体 pack 出来，表头放最后**。
        #   为什么：表头是 height=64 的画布，而文件区域是 expand 的。
        #   pack 的规则是「先来的先占地方」——表头先 pack 就把高度吃掉了，
        #   文件区域在空间紧的时候会被压成 1 像素高；**画布一旦只有 1 像素，
        #   Tk 就不再往它投递鼠标事件** —— 表现就是用户报的
        #   「单击没法选中文件，只可以框选」（框选靠拖动，偶尔还能进来）。
        #   现在把「一定会伸缩的文件区域」放在前面，表头放最后（它高度固定，
        #   放最后也会老老实实占好自己那 64 像素）。
        # ★★ v26 修正（2026-10-01，用户反馈「文件名/路径/大小/标签那一行
        #   一直跑到最底下」）：
        #
        #   补丁37 为了让「画布别被表头挤成 1 像素」，把 body（带 expand=True）
        #   放在了 header 前面 pack。可是 pack 的规则是：
        #     **expand=True 的控件会吃掉所有剩余空间**。
        #   结果就是：body 一上来就把整个高度占满，**表头被挤到了最底下**
        #   （实测：表头 y=632，画布 y=0 —— 正好反了）。
        #
        #   正确做法（也是所有正常软件的做法）：
        #     表头 **side="top"** 先 pack（它高度固定，占多少就是多少）；
        #     文件区 side="top" + expand=True 放后面，拿剩下的全部。
        #   这样表头永远在上、画布永远在下面，而且画布不会再变 1 像素 ——
        #   因为表头的高度是**固定**的（HEADER_H_BASE），不会像标题文字
        #   那样被撑成几百万像素。
        #
        #   另外：横向滚动条改成放在 **self** 里（不是 body 里），
        #   并且**永远留在最底部**（side="bottom" 先 pack）。
        #   这样它出现/消失都不会把画布挤变形。
        body = tk.Frame(self, bg=theme_get("card_bg"))
        try:
            register_themed(body, "card")   # ★ 常驻控件 → 换皮肤时跟着刷
        except Exception:
            pass
        body.pack(side="top", fill="both", expand=True)

        # ★★ 2026-10-06：底色跟着皮肤走 —— 这个画布是**文件列表的主底**，
        #   原来写死 bg=theme_get("card_bg")，夜间模式下文件列表就是白晃晃一大片
        #   （画出来的那几行是深色，没画到的空白仍是白的，特别刺眼）。
        self.canvas = tk.Canvas(body, bg=theme_get("card_bg"),
                                highlightthickness=0, takefocus=True)
        try:
            register_themed(self.canvas, "card")   # ★ 常驻控件 → 换皮肤时跟着刷
        except Exception:
            pass
        self.vsb = ttk.Scrollbar(body, orient="vertical", command=self._on_scroll_y)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # ★★ v26 修正：**横向滚动条固定放最底部，默认隐藏。**
        #   以前它在 body 里 pack(side="bottom", before=self.canvas)，
        #   而 body 里已经有 canvas(side=left, expand) —— 两者混用
        #   会让 pack 分配高度变得很怪（实测「拉不宽」就是这个引起的）。
        #   现在放到 self 这一层：先 pack 表头 / 文件区，再 pack 它，
        #   它永远在最底下；用不着就 pack_forget，一点也不影响画布。
        self.hsb = ttk.Scrollbar(self, orient="horizontal",
                                 command=self._on_scroll_x)
        self.canvas.configure(xscrollcommand=self.hsb.set)
        self._hsb_visible = False

        self.canvas.bind("<Configure>", lambda e: self._on_canvas_config())
        self.canvas.bind("<Button-1>", self._on_click)
        # ★ v25 补丁40：把「拖动移动」和「单击空白」这两组状态在这里
        #   先初始化好。以前它们只靠 getattr 兜底，虽然能跑，但一开始
        #   读到的永远是 None / 假值，容易出错。
        self._file_drag = None        # 在文件上按住拖动时记的东西
        self._drop_hint = None        # 拖动到文件夹时顶上那条黄提示
        self._blank_click = False     # 在空白处「按一下没动」= 单击空白
        # ★★ v26（2026-10-01）：**框选完之后马上单击会被当成双击**。
        #   Tk 的双击判定是跳事件靠时间+距离的 —— 框选松手位置
        #   离上一次单击很近时，接下来那一下会被 Tk 合并成 <Double-1>，
        #   而 <Double-1> 里面的“补选中”会把框选的成果收成一个。
        #   用户看起来就是「框选了一堆之后，点哪儿都选不中」。
        #   下面这个变量记「刚框选完的时间」，在它之后的短短窗口期内，
        #   把 <Double-1> 当成普通单击处理（只选中、不打开文件）。
        #   这正好对应手感：框选完马上点一下，肯定是想选文件，
        #   不可能是想打开文件。
        self._just_marqueed_ts = 0.0   # 刚框选完的时间戳
        self.MARQUEE_CLICK_GRACE = 0.30  # 窗口期（秒）
        self.on_move_to_folder = None # 主程序注入：拖动到文件夹 = 移动
        # ★ v25 补丁18/20：鼠标拉方框多选。
        #   marquee_anywhere=False（默认）：空白处拖 = 拉框，文件上拖 = 拖文件；
        #   marquee_anywhere=True：文件上拖也能拉框。
        #   ★★ 2026-10-03：这个开关**重新接上了**（补丁31 曾经把读它的那段
        #     代码删掉，于是菜单里那一项变成「点了没用」被删了）。
        #     为什么现在必须把它接回来：以前 0x8 那一位被误当成 Alt，
        #     **随便在哪儿拖都能拉框**（用户就是这么用的）；一旦把这个 bug
        #     修掉，「在文件上拖」就变成「拖文件」了 ——
        #     用户习惯的「到处拖都能框选」会突然失灵。
        #     所以给他一个开关，两种手感都能要，默认「空白处优先」
        #     （也就是「在文件上拖 = 拖文件」，因为拖到文件夹上松手 = 移动
        #      是新功能，得让它有地方触发）。
        try:
            self.marquee_anywhere = bool(load_ui_setting("marquee_anywhere", False))
        except Exception:
            self.marquee_anywhere = False
        self.canvas.bind("<B1-Motion>", self._marquee_move, add="+")
        self.canvas.bind("<ButtonRelease-1>", self._marquee_end, add="+")
        self.canvas.bind("<Double-1>", self._on_double_click)
        self.canvas.bind("<Button-3>", self._on_right)
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.canvas.bind("<Button-4>", self._on_wheel)
        self.canvas.bind("<Button-5>", self._on_wheel)
        self.canvas.bind("<Up>", self._on_key_up)
        self.canvas.bind("<Down>", self._on_key_down)
        self.canvas.bind("<Left>", self._on_key_left)
        self.canvas.bind("<Right>", self._on_key_right)
        self.canvas.bind("<Home>", self._on_key_home)
        self.canvas.bind("<End>", self._on_key_end)

        # ★ v25 补丁37：表头在这里才 pack（放在文件区域**之后**，见上面的注释）。
        #   高度是固定的，所以放最后也不会被压掉；而文件区域是 expand 的，
        #   放前面才能保证「空间不够时不至于被压成 1 像素」。
        # ★★ v26 修正：表头改成**插到 body 前面**（也就是屏幕最上方）。
        #   Tk 的 pack 是「先 pack 的先占位置」——要让它在上边，
        #   就得在 body 之前 pack。用 before=body 明确指定顺序，
        #   不管这行代码在源码里排第几，位置都是对的。
        try:
            self.header.pack(side="top", fill="x", before=body)
        except Exception:
            self.header.pack(side="top", fill="x")
        # ★ v26 修正：**这里不再绑定 <Configure> 回调。**
        #   用户反馈「标签栏和对应的标签位置是错位的」——表头写着
        #   「标签」的地方下面其实是别的列，标签胶囊跑到了「所在位置」
        #   那一列的下面，整体往左偏了 100 多像素。
        #
        #   原因：表头（header）和内容（canvas）是两个控件，各自都有
        #   自己的 <Configure> 回调。而 `_list_cols()` 里读的是
        #   `self.canvas.winfo_width()`。窗口尺寸变化时，两个控件的
        #   <Configure> 触发顺序是**不确定**的 ——
        #     · 如果表头**先**被通知：它读到的 canvas 宽度还是旧的，
        #       按旧宽度算列位置画表头；
        #     · 紧接着内容被通知：它读到新的 canvas 宽度，按新宽度
        #       算列位置画内容。
        #   两次算出来的列位置不一样 → 表头和内容就错位了。
        #
        #   改法：**表头不再自己响应尺寸变化**，改由 `_redraw()` 在
        #   画完内容之后、按**同一时刻**的宽度顺手重画一遍（见 _redraw
        #   末尾）。这样两次算的列位置永远一致，不可能再错位。
        self.header.bind("<Button-1>", self._on_header_click)
        self.header.bind("<B1-Motion>", self._on_header_drag)
        self.header.bind("<ButtonRelease-1>", self._on_header_release)
        self.header.bind("<Motion>", self._on_header_motion)
        # 列表一建出来就量一次画布尺寸（量到 1 像素就重试，见 _ensure_canvas_size）
        try:
            self.after(200, self._ensure_canvas_size)
        except Exception:
            pass

    # ---------------- ★ 开关控件 ----------------
    def _make_toggle(self, parent, text, var, on_change=None):
        """创建一个绿色的开关标签（未选为淡灰）。返回该 label。

        ★ v25 补丁30（体检修复）：原来这里写死了 `self._on_search_changed()`，
        也就是说**所有开关点一下都会触发一次搜索过滤**。问题是这个控件
        不只用在搜索栏：以后任何地方用它，一点就会白跑一次搜索（还可能
        把视图搞乱）。现在改成「谁用谁传回调」，搜索栏的开关照旧传搜索。
        """
        lbl = tk.Label(parent, text=text, padx=8, pady=1,
                       font=(FONT, UI_FONT_SIZE), cursor="hand2",
                       borderwidth=1, relief="solid")

        def refresh():
            if var.get():
                lbl.configure(bg="#2ecc71", fg="white",
                              highlightbackground="#27ae60")
            else:
                lbl.configure(bg=theme_get("line"), fg=theme_get("fg_dim"),
                              highlightbackground=theme_get("line"))

        def on_click(event):
            var.set(not var.get())
            refresh()
            cb = on_change or self._on_search_changed
            try:
                cb()
            except Exception:
                pass

        lbl.bind("<Button-1>", on_click)
        refresh()
        lbl.pack(side="left", padx=(4, 0))
        return lbl
    # ---------------- ★ 标签条 ----------------
    def _tagbar_sig_of(self, stats):
        """★ v25 补丁11：这一轮标签条的「身份」——只有它变了才需要重建控件。

        包含：标签集合（id/名字/数量）、作用范围、是否处于筛选/屏蔽状态、
        以及宽度档位（每 40 像素一档）。选中的是哪些标签**不在**里面 ——
        换选中只改样式（几毫秒），不用重建（几百毫秒）。
        """
        try:
            stat_sig = tuple((t[0], t[1], t[3]) for t in (stats or []))
        except Exception:
            stat_sig = ()
        try:
            w = self.tagbar.winfo_width()
        except Exception:
            w = 0
        return (stat_sig, getattr(self, "tag_scope", "page"),
                int(w // 40))

    def _style_pill(self, lbl, tid, color):
        """★ v25 补丁11：按当前「选中/屏蔽」状态给一个标签胶囊上色（不重建）。"""
        selected = tid in self.filter_tag_ids
        hidden = tid in self.hidden_tag_ids
        try:
            if hidden:
                lbl.configure(bg=theme_get("line"), fg=theme_get("fg_dim"), relief="flat",
                              borderwidth=1, highlightbackground=theme_get("line"),
                              font=self._tagbar_f_strike)
            elif selected:
                bg = color or "#3498db"
                lbl.configure(bg=bg, fg=text_color_for(bg), relief="solid",
                              borderwidth=2, highlightbackground="#2c3e50",
                              font=self._tagbar_f_bold)
            else:
                bg = color or "#3498db"
                lbl.configure(bg=bg, fg=text_color_for(bg), relief="flat",
                              borderwidth=1, highlightbackground=bg,
                              font=self._tagbar_f_normal)
        except Exception:
            pass

    def _restyle_tagbar(self, stats):
        """★ v25 补丁11：标签集合没变 —— 只刷新样式和几句文字，不重建控件。

        （那三颗按钮是一直建好的，这里只管「要不要显示、文字写成什么」，
          所以屏蔽标签 / 清除筛选也不需要重建控件了。）
        """
        n_sel = len(self.filter_tag_ids)
        n_hid = len(self.hidden_tag_ids)
        for t in stats:
            tid = t[0]
            lbl = (self._tagbar_pills or {}).get(tid)
            if lbl is None:
                continue
            self._style_pill(lbl, tid, t[2])
        scope_txt = ("🗂 范围：整个视图" if self.tag_scope == "view"
                     else "📄 范围：当前页")
        for btn, txt in ((self._tagbar_scope_btn, scope_txt),
                         (self._tagbar_clear_btn,
                          "清除筛选（已选 %d）" % n_sel if n_sel else ""),
                         (self._tagbar_show_btn,
                          "全部显示（已屏蔽 %d）" % n_hid if n_hid else "")):
            if btn is None:
                continue
            try:
                if txt:
                    btn.configure(text=txt)
            except Exception:
                pass
        # 该出现的按钮 pack 上、不该出现的收起来（都不重建）
        for btn, show in ((self._tagbar_mode_btn, n_sel > 0),
                          (self._tagbar_clear_btn, n_sel > 0),
                          (self._tagbar_show_btn, n_hid > 0)):
            if btn is None:
                continue
            try:
                if show:
                    if not btn.winfo_ismapped():
                        btn.pack(fill="x", pady=1)
                else:
                    if btn.winfo_ismapped():
                        btn.pack_forget()
            except Exception:
                pass
        self._tagbar_buttons = [w for w in (self._tagbar_pills or {}).values()
                                if w.winfo_exists()]

    def set_tagbar_visible(self, visible):
        """★ v25 补丁7：显示 / 隐藏标签条（默认隐藏）。

        标签条现在挂在整个窗口底部，pack / pack_forget 由主程序负责
        （self.on_tagbar_visibility 回调），因为要控制它跟「📋 输出」面板的
        先后顺序。回调没设置时退回老做法：显示在文件列表那一列里。
        """
        self.tagbar_visible = bool(visible)
        cb = getattr(self, "on_tagbar_visibility", None)
        if cb is not None:
            try:
                cb(self.tagbar_visible)
            except Exception:
                pass
        else:
            if self.tagbar_visible:
                try:
                    self.tagbar.pack(fill="x", pady=(0, 4), after=self._sbar)
                except Exception:
                    self.tagbar.pack(fill="x", pady=(0, 4))
            else:
                try:
                    self.tagbar.pack_forget()
                except Exception:
                    pass
        if self.tagbar_visible:
            self._render_tag_bar()

    def _toggle_tagbar(self):
        """兼容旧调用：翻转一下（新按钮走 set_tagbar_visible）。"""
        self.set_tagbar_visible(not self.tagbar_visible)

    def set_dir_info(self, text):
        """★ v25 补丁10：这个方法现在**不再往标签条上写东西**了。

        补丁6/8 时它负责把「目录 共 N 项」这类信息显示到标签条最右端；
        用户后来说：这类信息显示在**状态栏消息的右边**就好（主程序
        set_status 里用 _view_info_text() + _view_info_lbl 实现），
        标签条右端那段横向空间整段让给标签。
        这个方法留着只是为了兼容老调用（比如别处万一还在调），不再有可见效果。
        """
        self._tagbar_info_text = (text or "").strip()

    def _on_tagbar_configure(self, event):
        if abs(event.width - self._tagbar_last_w) < 8:
            return
        self._tagbar_last_w = event.width
        if self._tagbar_render_job is not None:
            try:
                self.after_cancel(self._tagbar_render_job)
            except Exception:
                pass
        self._tagbar_render_job = self.after(150, self._do_tagbar_render)

    def _do_tagbar_render(self):
        self._tagbar_render_job = None
        self._render_tag_bar()


        # ---------------- ★ 标签条 ----------------
    def _collect_tag_stats(self):
        """返回 [(tid, name, color, cnt), ...]（按出现次数降序）。

        - 当前页范围：从本页 rows 里统计（默认，秒回）；
        - 整个视图范围：直接吃主程序查库算好的统计结果。
        """
        if getattr(self, "tag_scope", "page") == "view":
            return list(self.tag_scope_stats or [])
        counter = {}
        for r in self._all_rows:
            for t in (r.get("tags") or []):
                tid, name, color = t[0], t[1], t[2]
                if tid not in counter:
                    counter[tid] = [name, color, 0]
                counter[tid][2] += 1
        return sorted(
            [(tid, v[0], v[1], v[2]) for tid, v in counter.items()],
            key=lambda x: (-x[3], (x[1] or "").lower()))

    def _render_tag_bar(self):
        if not getattr(self, "tagbar_visible", True):
            return
        # ★ v25：还没排好版时（第一次渲染 winfo_width 只有 1 像素）
        #   先等一拍，否则会按 1 像素宽度换行、标签被挤成一列
        if self.tagbar.winfo_width() <= 1 and getattr(
                self, "_tagbar_retry", 0) < 5:
            self._tagbar_retry = getattr(self, "_tagbar_retry", 0) + 1
            try:
                self.after_cancel(self._tagbar_render_job)
            except Exception:
                pass
            self._tagbar_render_job = self.after(120, self._do_tagbar_render)
            return
        self._tagbar_retry = 0

        # ★ v25 补丁11：先算统计，再决定「只改样式」还是「重建控件」。
        #   Tk 销毁+重建 60 个控件实测量要 0.3~0.6 秒 —— 点一下标签就卡这么久，
        #   就是因为每次都重建。标签集合没变时只改样式（几毫秒）。
        try:
            stats = self._collect_tag_stats()
        except Exception as _e:
            note_swallowed(T("统计标签条上的标签失败"), _e)
            stats = []
        sig = self._tagbar_sig_of(stats)
        if (sig == self._tagbar_sig and self._tagbar_pills
                and self._tagbar_left is not None
                and self._tagbar_holder is not None):
            try:
                if self._tagbar_left.winfo_exists() and self._tagbar_holder.winfo_exists():
                    self._restyle_tagbar(stats)
                    return
            except Exception:
                pass

        try:
            for w in self.tagbar.winfo_children():
                w.destroy()
        except Exception:
            return
        self._tagbar_buttons = []
        self._tagbar_pills = {}
        self._tagbar_sig = sig

        # ★ v25 补丁10：左边这一竖列 = 三行提示小字 + 下面紧跟「范围 / 全部显示」按钮。
        #   用户要求：把原来贴在标签条**最右端**的「📄 范围：当前页」「全部显示
        #   （已屏蔽 4）」挪到这几行小字的**下边** —— 最右边那段横向空间就
        #   整段留给标签用，标签不容易被挤掉。
        scope_lbl = ("整个视图" if self.tag_scope == "view" else "当前页")
        left_col = tk.Frame(self.tagbar, bg=theme_get("panel_bg"))
        left_col.pack(side="left", padx=(8, 4), pady=3)
        self._tagbar_left = left_col
        tk.Label(left_col, text=T("标签："), bg=theme_get("panel_bg"), fg=theme_get("fg_dim"),
                 font=(FONT, UI_FONT_SIZE, BOLD)).pack(anchor="w")
        tk.Label(left_col, text=T("左键筛选"), bg=theme_get("panel_bg"), fg=theme_get("fg_dim"),
                 font=(FONT, UI_FONT_SIZE_SMALL)).pack(anchor="w")
        tk.Label(left_col, text=f"右键屏蔽 {scope_lbl}", bg=theme_get("panel_bg"),
                 fg=theme_get("fg_dim"), font=(FONT, UI_FONT_SIZE_SMALL)).pack(anchor="w")

        # 这几颗按钮永远显示 —— 整库统计中 / 该视图暂时没标签时也能切回「当前页」
        right_box = tk.Frame(left_col, bg=theme_get("panel_bg"))
        right_box.pack(fill="x", pady=(3, 0))

        if self.tag_scope == "view":
            scope_txt = "🗂 范围：整个视图"
            scope_fg = theme_get("ok")
        else:
            scope_txt = "📄 范围：当前页"
            scope_fg = theme_get("fg_dim")
        tk.Button(right_box, text=scope_txt,
                  font=(FONT, UI_FONT_SIZE_SMALL), relief="flat",
                  bg=theme_get("panel_bg"), fg=scope_fg, cursor="hand2",
                  activebackground=theme_get("hover_bg"),
                  anchor="w", padx=6,
                  command=self._toggle_tag_scope).pack(fill="x", pady=1)
        # ★ v25 补丁11：记住这颗按钮，将来只改文字就能切换范围（不用重建）
        self._tagbar_scope_btn = right_box.winfo_children()[-1]

        n_sel = len(self.filter_tag_ids)
        n_hid = len(self.hidden_tag_ids)

        # ★ v25 补丁11：这三颗按钮**一直建好**，只是按情况显示/隐藏 ——
        #   这样「选中标签 / 屏蔽标签」就不用重建整条标签条了（重建很慢）。
        mode_text = T("🔗 全部满足") if self.filter_match_all \
            else T("🔀 任一满足")
        btn_mode = tk.Button(right_box, text=mode_text,
                             font=(FONT, UI_FONT_SIZE_SMALL), relief="flat",
                             bg=theme_get("panel_bg"), fg="#8e44ad", cursor="hand2",
                             activebackground=theme_get("hover_bg"),
                             anchor="w", padx=6,
                             command=self._toggle_filter_match_all)
        if n_sel > 0:
            btn_mode.pack(fill="x", pady=1)
        self._tagbar_mode_btn = btn_mode

        btn_clear = tk.Button(right_box, text=f"清除筛选（已选 {n_sel}）",
                              font=(FONT, UI_FONT_SIZE_SMALL), relief="flat",
                              bg=theme_get("panel_bg"), fg="#3498db", cursor="hand2",
                              activebackground=theme_get("hover_bg"),
                              anchor="w", padx=6,
                              command=self._clear_tag_filter)
        if n_sel > 0:
            btn_clear.pack(fill="x", pady=1)
        self._tagbar_clear_btn = btn_clear

        btn_show = tk.Button(right_box, text=f"全部显示（已屏蔽 {n_hid}）",
                             font=(FONT, UI_FONT_SIZE_SMALL), relief="flat",
                             bg=theme_get("panel_bg"), fg=theme_get("warn"), cursor="hand2",
                             activebackground=theme_get("hover_bg"),
                             anchor="w", padx=6,
                             command=self._show_all_tags)
        if n_hid > 0:
            btn_show.pack(fill="x", pady=1)
        self._tagbar_show_btn = btn_show

        holder = tk.Frame(self.tagbar, bg=theme_get("panel_bg"))
        holder.pack(side="left", fill="x", expand=True, padx=2, pady=2)
        self._tagbar_holder = holder

        stats = self._collect_tag_stats()
        if not stats:
            if getattr(self, "tag_scope", "page") == "view":
                txt = self.tag_scope_hint or "（整个视图里还没有标签）"
            else:
                txt = "（当前列表里还没有标签）"
            tk.Label(holder, text=txt,
                     bg=theme_get("panel_bg"), fg=theme_get("fg_dim"),
                     font=(FONT, UI_FONT_SIZE)).pack(side="left", padx=8, pady=3)
            return

        row_frame = tk.Frame(holder, bg=theme_get("panel_bg"))
        row_frame.pack(fill="x", anchor="w")
        current_w = 0
        # ★ v25 补丁10：右边不再有按钮区了，宽度只要扣掉左边那一竖列
        try:
            used_w = left_col.winfo_reqwidth() + 44
        except Exception:
            used_w = 150
        if used_w < 60:
            used_w = 150
        max_w = max(180, self.tagbar.winfo_width() - used_w)
        # 上一轮量到的「真正可用宽度」更准，取更小的那个：
        # 宁可早一格换行，也绝不把标签裁掉
        prev_w = getattr(self, "_tagbar_holder_w", 0)
        if prev_w and prev_w > 60:
            max_w = max(180, min(max_w, prev_w - 2))

        f_normal = tkfont.Font(family=FONT, size=UI_FONT_SIZE)
        f_bold = tkfont.Font(family=FONT, size=UI_FONT_SIZE, weight=BOLD)
        f_strike = tkfont.Font(family=FONT, size=UI_FONT_SIZE, overstrike=True)
        # ★ v25 补丁11：字体对象存起来，将来「只改样式」时直接用
        self._tagbar_f_normal = f_normal
        self._tagbar_f_bold = f_bold
        self._tagbar_f_strike = f_strike

        for tid, name, color, cnt in stats:
            selected = tid in self.filter_tag_ids
            hidden = tid in self.hidden_tag_ids
            text = f" {name} ({cnt}) "

            if hidden:
                f = f_strike
            elif selected:
                f = f_bold
            else:
                f = f_normal

            tw = f.measure(text) + 22
            if current_w + tw > max_w and current_w > 0:
                row_frame = tk.Frame(holder, bg=theme_get("panel_bg"))
                row_frame.pack(fill="x", anchor="w")
                current_w = 0

            if hidden:
                bg = theme_get("line")
                fg = theme_get("fg_dim")
                hl = theme_get("line")
                relief = "flat"
                bw = 1
            elif selected:
                bg = color or "#3498db"
                fg = text_color_for(bg)
                # ★★ 2026-10-07：原来写死 "#2c3e50"（深蓝黑），
                #   夜间在深底上看不出选中。改用主题 accent。
                hl = theme_get("accent")
                relief = "solid"
                bw = 2
            else:
                bg = color or "#3498db"
                fg = text_color_for(bg)
                hl = bg
                relief = "flat"
                bw = 1

            lbl = tk.Label(row_frame, text=text, bg=bg, fg=fg,
                           font=f, padx=4, pady=1, cursor="hand2",
                           relief=relief, borderwidth=bw,
                           highlightbackground=hl)
            lbl.pack(side="left", padx=2, pady=1)
            lbl.bind("<Button-1>",
                     lambda e, t=tid: self._toggle_tag_filter(t))
            lbl.bind("<Button-3>",
                     lambda e, t=tid: self._toggle_tag_hidden(t))
            self._tagbar_buttons.append(lbl)
            self._tagbar_pills[tid] = lbl          # ★ v25 补丁11：留着复用
            current_w += tw + 4
        # ★ v25：记下这一轮真正可用的宽度，下一次换行按它来（更准）
        try:
            holder_w = holder.winfo_width()
        except Exception:
            holder_w = 0
        self._tagbar_holder_w = holder_w
        # 窗口刚变大（或第一次排版）时，这一轮用的还是旧宽度 → 标签会白白
        # 早换行；这里再排一次，最多补 2 轮，防止死循环
        if (holder_w > 60 and holder_w > max_w + 20
                and getattr(self, "_tagbar_repack", 0) < 2):
            self._tagbar_repack = getattr(self, "_tagbar_repack", 0) + 1
            try:
                self.after_cancel(self._tagbar_render_job)
            except Exception:
                pass
            self._tagbar_render_job = self.after(60, self._do_tagbar_render)
        else:
            self._tagbar_repack = 0
    # ---------------- ★ v24：标签条作用范围（当前页 / 整个视图）----------------
    def _toggle_tag_scope(self):
        self.tag_scope = "view" if self.tag_scope == "page" else "page"
        if self.tag_scope == "page":
            self.tag_scope_stats = None
            self.tag_scope_hint = None
        if self.on_tag_scope_changed is not None:
            try:
                self.on_tag_scope_changed(self.tag_scope)
            except Exception:
                pass
        self._render_tag_bar()

    def set_tag_scope_stats(self, stats, hint=None):
        """主程序算好整库标签统计后回填（stats=None 表示清空/统计中）。"""
        self.tag_scope_stats = stats
        self.tag_scope_hint = hint
        if self.tag_scope == "view":
            self._render_tag_bar()

    def show_tag_scope_hint(self, hint):
        self.tag_scope_hint = hint
        if self.tag_scope == "view":
            self._render_tag_bar()

    def _toggle_tag_filter(self, tid):
        if tid in self.filter_tag_ids:
            self.filter_tag_ids.discard(tid)
        else:
            self.filter_tag_ids.add(tid)
        if self.tag_scope == "view" and self.on_tag_filter_view is not None:
            self._render_tag_bar()
            try:
                self.on_tag_filter_view()
            except Exception:
                pass
            return
        self._render_tag_bar()
        self._apply_search_filter()

    def _clear_tag_filter(self):
        if not self.filter_tag_ids:
            return
        self.filter_tag_ids.clear()
        if self.tag_scope == "view" and self.on_tag_filter_view is not None:
            self._render_tag_bar()
            try:
                self.on_tag_filter_view()
            except Exception:
                pass
            return
        self._render_tag_bar()
        self._apply_search_filter()

    def _toggle_filter_match_all(self):
        self.filter_match_all = not self.filter_match_all
        if self.tag_scope == "view" and self.on_tag_filter_view is not None:
            self._render_tag_bar()
            try:
                self.on_tag_filter_view()
            except Exception:
                pass
            return
        self._render_tag_bar()
        self._apply_search_filter()

    def _match_tag_filter(self, r):
        # ★ 整个视图范围下，标签筛选已由主程序在"取数据"时完成，
        #   这里不再对本页重复过滤。
        if getattr(self, "tag_scope", "page") == "view":
            return True
        if not self.filter_tag_ids:
            return True
        tids = {t[0] for t in (r.get("tags") or [])}
        if self.filter_match_all:
            return self.filter_tag_ids.issubset(tids)
        return bool(self.filter_tag_ids & tids)

    def _toggle_tag_hidden(self, tid):
        if tid in self.hidden_tag_ids:
            self.hidden_tag_ids.discard(tid)
        else:
            self.hidden_tag_ids.add(tid)
        self._render_tag_bar()
        self._recompute_layout()
        self._redraw()


    def _show_all_tags(self):
        if not self.hidden_tag_ids:
            return
        self.hidden_tag_ids.clear()
        self._render_tag_bar()
        self._recompute_layout()
        self._redraw()

    def clear_hidden_tags(self):
        self._show_all_tags()

    # ---------------- ★ 搜索 ----------------
    def _on_search_changed(self):
        self.search_text = (self.search_var.get() or "").strip().lower()
        # ★ 含子目录模式
        #
        # ★★★ 2026-10-08 改（用户报「文件列表上的搜索**没法搜索子目录里的文件**」，
        #   待清算 #7）★★★
        #   ★ 原来的行为：开了"含子目录"之后，**输入时什么都不做**，
        #     只在**按回车**那一刻才去扫子目录 ——
        #     理由是"避免网盘频繁扫描"（这个理由是**对的**，别丢掉）。
        #   ★ 但用户的实际感受是：**"我打字了，它没反应"** →
        #     以为"搜不了子目录"。
        #   ★ 更好的做法（**两全其美**，现在这个）：
        #     ① 打字的时候**先按"当前目录"过滤**（纯内存，瞬间有反馈）
        #        → 用户马上看到"字打进去就有反应"，不再以为坏了；
        #     ② **停手 0.9 秒**之后再自动扩到子目录去扫
        #        → 仍然满足"不要每敲一个字就扫一次网盘"的初衷。
        #     ③ 回车 = **立刻**扫（想快的人还是按回车），这个没变。
        if self.search_recursive.get():
            if not self.search_text:
                # 清空：立刻恢复，别等
                self._cancel_search_debounce()
                self.search_external = False
                self._apply_search_filter()
                if self.on_recursive_search is not None:
                    try:
                        self.on_recursive_search("")
                    except Exception:
                        pass
                self.search_info_lbl.config(text="")
                return
            # ① 先按"当前目录"即时过滤 —— 立刻有反馈
            self.search_external = False
            try:
                self._apply_search_filter()
            except Exception:
                pass
            # ② 停手之后**自动**扩到子目录
            self.search_info_lbl.config(
                text=T("正在搜当前目录…（停手后自动搜子目录）"))
            self._search_debounce_recursive()
            return

        # ★★ 2026-10-06：**「等你停手再查」**（下详）★★
        #   本地文件夹那条路（下面那段）本来就是纯内存过滤，很快，
        #   所以**照样即时**，一点延迟都不加 —— 免得破坏现有手感。
        #   只有「交给主程序查库」那条路要防抖（分类 / 全部文件视图）。
        if getattr(self, "on_global_search", None):
            self.search_external = False
            if not self.search_text:
                # 清空要**立刻**响应（用户按了「清除」就该马上恢复原样，
                # 等 0.25 秒会显得程序没反应）
                self._cancel_search_debounce()
                self.on_global_search("")
                return
            self._search_debounce()
            return

        self._cancel_search_debounce()
        self.search_external = False
        self._apply_search_filter()
        self._update_search_info()

    # ---------------- ★★ 2026-10-06：搜索防抖（等你停手再查）----------------
    #
    #   为什么要这个：
    #     原来在「分类 / 全部文件」里搜索，**每敲一个字就查一遍数据库**。
    #     用户那个库有 43 万条，打「风光摄影」四个字 = 查 4 遍库，
    #     打字快的时候界面就一顿一顿的 —— 用户看到的「搜索卡」就是这个。
    #
    #   ★ 注意：这不是「让它变实时」，恰恰相反 ——
    #     它是**把过度实时收一收**：等你手停 0.25 秒再查一次。
    #     外面所有正经搜索都这么做（VS Code / 浏览器 / 各种搜索框），
    #     0.2~0.3 秒是行业惯例。
    #
    #   ★ 为什么是 0.25 秒：
    #     · 更短 → 还是查太多次，白防；
    #     · 更长 → 用户觉得「我打完了它怎么还不动」，显得迟钝。
    #
    #   ★ 为什么**只给查库那条路**防抖：
    #     普通文件夹里是纯内存过滤（几百条），本来就快，
    #     加延迟只会让手感变差 —— 不能为了省事一刀切。
    SEARCH_DEBOUNCE_MS = 250
    # ★★ 2026-10-08 新增：「含子目录」模式的防抖要**长得多**。
    #   为什么：上面那个 250ms 是给"纯内存过滤"用的；
    #   而"含子目录"是**真去扫目录树**（可能走网盘、可能上万文件）——
    #   打字快的人每敲一个字就扫一次会卡死。
    #   0.9 秒：够长（不等一个字就扫），又不至于让人等得难受。
    SEARCH_RECURSIVE_DEBOUNCE_MS = 900

    def _search_debounce_recursive(self):
        """★★ 「含子目录」模式下：**停手 0.9 秒后自动去搜子目录**。

        ★★ 2026-10-08 新增（用户报「文件列表上的搜索**没法搜索子目录里的
          文件**」，待清算 #7）。

        ★ 为什么单独一个（不用上面的 0.25 秒那个）：
          · 上面那个是**纯内存过滤**，0.25 秒很合适；
          · 这个是**要去扫目录树**（可能走网盘、可能很慢）——
            必须**等久一点**（0.9 秒），不然打字快的人每敲一个字就扫一次。
        ★ 为什么要有它（而不是只靠回车）：
          ★ 用户的实际感受是「**我打字了，它没反应**」→ 以为"搜不了子目录"。
          ★ 加了这一条之后：打字时**当前目录立刻过滤**（有反馈），
            停手后**自动**扩到子目录 —— **不用教用户"要按回车"**。
          ★ 回车那条路**保留**（想快的人按回车立刻扫）。
        """
        self._cancel_search_debounce()
        try:
            self._search_job = self.after(
                self.SEARCH_RECURSIVE_DEBOUNCE_MS, self._search_fire_recursive)
        except Exception:
            self._search_job = None
            self._search_fire_recursive()

    def _search_fire_recursive(self):
        """到点了：交给主程序去扫子目录。"""
        self._search_job = None
        try:
            if self.on_recursive_search is None:
                return
            self.search_text = (self.search_var.get() or "").strip().lower()
            if not self.search_text:
                return
            self.search_external = True
            try:
                self.search_info_lbl.config(text=T("正在搜子目录…"))
            except Exception:
                pass
            self.on_recursive_search(self.search_text)
        except Exception as _e:
            note_swallowed(T("含子目录搜索失败"), _e)

    def _search_debounce(self):
        """排一个「停手 0.25 秒后查一次」的任务（重复调用只会留最后一个）。"""
        self._cancel_search_debounce()
        try:
            self._search_job = self.after(
                self.SEARCH_DEBOUNCE_MS, self._search_fire)
        except Exception:
            self._search_job = None
            self._search_fire()

    def _cancel_search_debounce(self):
        """把还没到点的搜索任务掐掉。"""
        job = getattr(self, "_search_job", None)
        if job is not None:
            try:
                self.after_cancel(job)
            except Exception:
                pass
            self._search_job = None

    def _search_fire(self):
        """到点了：真的去查一次。"""
        self._search_job = None
        try:
            if getattr(self, "on_global_search", None):
                # ★ 查的时候用**最新的**搜索词（用户可能又打了一个字，
                #   但那会重新排一个任务，这里拿到的就是这个时刻的）
                self.search_text = (self.search_var.get() or "").strip().lower()
                self.on_global_search(self.search_text)
        except Exception as _e:
            note_swallowed(T("搜索失败"), _e)

    def _trigger_search(self):
        """回车时触发。含子目录模式下交给主程序递归扫描。"""
        # ★★ 2026-10-06：按回车 = 「我打完了，马上给我结果」——
        #   所以**先掐掉那个等着到点的防抖任务**，立刻查。
        #   不加这一句的话：用户按回车没反应，还得再等 0.25 秒才出结果，
        #   会以为回车坏了。
        self._cancel_search_debounce()
        if self.search_recursive.get() and self.on_recursive_search is not None:
            self.search_external = True
            self.search_text = (self.search_var.get() or "").strip().lower()
            self.on_recursive_search(self.search_text)
            return
        # 非「含子目录」模式下按回车：也立刻查一次（而不是等防抖）
        if getattr(self, "on_global_search", None) and self.search_text:
            self.search_external = False
            self.on_global_search(self.search_text)

    def _update_search_info(self):
        """搜索栏右边的「显示 N / M」（含子目录模式下也会被用来显示提示）"""
        try:
            if self.search_text:
                self.search_info_lbl.config(
                    text=f"显示 {len(self.rows)} / {len(self._all_rows)}")
            else:
                self.search_info_lbl.config(text="")
        except Exception:
            pass

    def set_tag_filter(self, ids, match_all=None):
        """★ v25：外部（主程序）直接设置标签筛选。

        搜索会重开一个视图，这时要把遗留的标签筛选清掉，免得搜索
        结果被悄悄砍一刀；清空搜索还原视图时再把它们放回去。
        """
        self.filter_tag_ids = set(ids or ())
        if match_all is not None:
            self.filter_match_all = bool(match_all)
        self._render_tag_bar()
        if self.tag_scope != "view":
            self._apply_search_filter()


    def _match_row(self, r, q):
        # 三个开关是"或"的关系：任一开启的维度匹配即命中
        # ★ v25：三个开关全关着 = 不做二次过滤（以前会变成空列表）
        if not (self.search_by_name.get() or self.search_by_tag.get()
                or self.search_by_location.get()):
            return True
        if self.search_by_name.get():
            if q in (r.get("name") or "").lower():
                return True
        if self.search_by_location.get():
            if q in (r.get("location") or "").lower():
                return True
        if self.search_by_tag.get():
            for t in (r.get("tags") or []):
                if q in (t[1] or "").lower():
                    return True
        return False

    def _apply_search_filter(self):
        q = self.search_text
        # ★ v25：search_external=True 表示关键字已经由主程序过滤过了
        #   （含子目录搜索 / 分类·全部文件搜索），这里不再重复过滤，
        #   否则关掉「文件名」开关时结果会被二次过滤成空。
        if not q or self.search_external:
            base = list(self._all_rows)
        else:
            base = [r for r in self._all_rows if self._match_row(r, q)]
        if self.filter_tag_ids:
            base = [r for r in base if self._match_tag_filter(r)]
        self.rows = self._sort_rows(base)
        valid = {r["path"] for r in self.rows}
        self.selected_paths &= valid
        keep = {r["path"] for r in self.rows}
        for k in list(self._thumbs.keys()):
            if k[0] not in keep:
                del self._thumbs[k]
        self._thumb_failed = {k for k in self._thumb_failed if k[0] in keep}
        # ★ v26：后台还没读完的、已经不在列表里的，一起丢掉 ——
        #   不然它读完了还让界面重画一次，白费功夫。
        try:
            with self._thumb_lock:
                self._thumb_queue = deque(
                    (p, k, t) for (p, k, t) in self._thumb_queue
                    if k[0] in keep)
            self._thumb_loading = {k for k in self._thumb_loading
                                   if k[0] in keep}
        except Exception:
            pass
        self._recompute_layout()
        self._render_tag_bar()
        self._redraw()
        self._update_search_info()
        if self.on_select:
            self.on_select()

    # ---------------- 配置 ----------------
    def set_layout_mode(self, mode):
        if mode not in ("list", "grid"):
            return
        if mode == self.layout_mode:
            return
        self.layout_mode = mode
        if mode == "list":
            self.header.pack(fill="x", before=self.canvas.master)
        else:
            self.header.pack_forget()
        self._recompute_layout()
        self._redraw()

    def set_icon_level(self, level, clear_cache=True):
        level = max(0, min(len(self.icon_sizes()) - 1, level))
        if level == self.icon_level:
            return
        self.icon_level = level
        self.icon_px = self.icon_sizes()[level][1]
        self.base_font_size = self.icon_sizes()[level][2]
        # ★★ 2026-10-03：字号**锁死**在 UI_FONT_SIZE，只有图标在变大变小
        #   （用户要求「不管哪一档，字都和右下角按钮一样大」）。
        self.font.configure(size=UI_FONT_SIZE)
        self.font_small.configure(size=UI_FONT_SIZE)
        self.font_tag.configure(size=UI_FONT_SIZE)
        if clear_cache:
            self._thumbs.clear()
            self._thumb_failed.clear()
        self._recompute_layout()
        self._redraw()


    def _tag_pill_half_h(self):
        line_h = self.font_tag.metrics("linespace")
        return max(8, line_h // 2 + 3)

    def _tag_pad_x(self):
        fs = self.font_tag.cget("size")
        return max(6, fs // 2 + 4)

    def _target_thumb_size(self):
        """缩略图按多大生成。

        ★ 2026-10-03：瀑布流最大档会把卡片撑宽（一排 8 个），
          这时候缩略图也要跟着变大（见 _grid_img_px）。
        """
        try:
            if self.layout_mode != "list":
                return max(16, int(self._grid_img_px()))
        except Exception:
            pass
        return max(16, self.icon_px)

    def _get_thumbnail(self, path):
        """★★ v26：**这个函数以前会把整个界面卡死。**

        原来它是**同步**的：`Image.open(path)` + `img.load()` 会把
        整个图片文件**读进来**；视频更狠，还要 `cv2.VideoCapture`
        解一帧出来。而它是被 `_redraw`（画每一行）调用的 ——
        也就是说**每重绘一次，一屏二三十个文件全部真读一遍**。

        用户有「图本」这种 5 万多张图的分类，一屏全是图片 →
        每点一下文件、每滚一下列表，主线程就被这些磁盘读取堵住几秒。
        这就是他说的「多选后单击卡住」的真正原因：
        框选时不展开、单击时会展开那一行 → 触发整表重绘 →
        一屏图片全被重新读一遍 → 卡 2 秒多。

        ★ 现在的做法：
          · **能立刻拿到的才同步取**（已经在缓存里的）；
          · 没缓存的 → 返回 None（先画个表情图标占位），
            同时**丢给后台线程去读**；读好了再让界面重画那一次。
          · 读失败 / 正在读的，用一个「正在加载」集合记住，
            不会重复排队。
        这样重绘永远是「纯画图」，不会再碰磁盘，界面就不会卡了。
        """
        if not HAS_PIL:
            return None
        ext = os.path.splitext(path)[1].lower()
        is_image = ext in IMAGE_EXTS
        is_video = ext in VIDEO_EXTS
        is_exe = (ext == ".exe")
        is_url = (ext == ".url")
        is_lnk = (ext == ".lnk")
        is_shell = is_exe or is_url or is_lnk

        if not (is_image or is_video or (is_shell and HAS_WIN32)):
            return None

        target = self._target_thumb_size()
        key = (path, target)
        # ① 缓存里有 → 直接给（这是最快的一条路）
        if key in self._thumbs:
            return self._thumbs[key]
        # ② 试过失败的 → 别再来一遍
        if key in self._thumb_failed:
            return None
        # ③ 已经在后台读了 → 先返回 None，等它读完
        if key in getattr(self, "_thumb_loading", set()):
            return None
        # ④ 没读过 → 丢给后台，本帧先画占位图标
        self._queue_thumbnail(path, key, target)
        return None

    # ---------------- ★ v26：缩略图后台加载 ----------------

    def _queue_thumbnail(self, path, key, target):
        """把一个缩略图任务丢进后台线程队列（同一个文件只排一次）。"""
        try:
            if not hasattr(self, "_thumb_loading"):
                self._thumb_loading = set()
            if not hasattr(self, "_thumb_queue"):
                self._thumb_queue = deque()
                self._thumb_lock = threading.Lock()
                self._thumb_running = False
            if key in self._thumb_loading:
                return
            self._thumb_loading.add(key)
            with self._thumb_lock:
                self._thumb_queue.append((path, key, target))
            self._start_thumb_worker()
        except Exception:
            pass

    def _start_thumb_worker(self):
        """起一个（且只有一个）后台线程慢慢读缩略图。"""
        try:
            if getattr(self, "_thumb_running", False):
                return
            self._thumb_running = True
            threading.Thread(target=self._thumb_worker, daemon=True).start()
        except Exception:
            self._thumb_running = False

    def _thumb_worker(self):
        """后台线程：一个个读，读完把结果交回主线程画。"""
        while True:
            try:
                with self._thumb_lock:
                    if not self._thumb_queue:
                        self._thumb_running = False
                        return
                    path, key, target = self._thumb_queue.popleft()
            except Exception:
                self._thumb_running = False
                return
            img = None
            try:
                img = self._load_thumb_image(path, target)
            except Exception:
                img = None
            # ★ Tk / PIL 的 PhotoImage **只能在主线程建**，
            #   所以这里只把「已经解码好的 PIL 图片」交回主线程，
            #   由主线程去 ImageTk.PhotoImage()。
            if APP_CLOSING:
                return
            # ★★ 2026-10-03：这里以前写的是 self.after(0, ...) ——
            #   后台线程调 Tk 的 after 会卡死在 tkinter 内部（Tcl 同一时刻
            #   只许一个线程碰它），于是「图片读好了」这句话送不回主线程：
            #   **瀑布流里的缩略图会一直显示成通用图标，永远等不到真图**
            #   （实测：一排 8 个格子全是图标，等了十几秒也不变）。
            #   现在走主程序那条安全信箱（后台只往 Python 列表塞东西）。
            # ★★ 2026-10-03 又加固了一道：拿不到 on_ui_call 时**宁可记一笔
            #   日志、丢掉这一次**，也**不再退回 after(0, ...)** ——
            #   because after(0, ...) 在后台线程里会卡死，
            #   丢一次远比卡死好。
            try:
                _ui = getattr(self, "on_ui_call", None)
                if _ui is not None:
                    _ui(self._on_thumb_ready, key, img)
                else:
                    try:
                        note_swallowed(
                            "文件列表缩略图：拿不到主程序的 on_ui_call，"
                            "这次回主线程的活儿被丢掉了",
                            RuntimeError("missing on_ui_call"),
                            level="error")
                    except Exception:
                        pass
            except Exception:
                pass
            # 稍微让一让，别把磁盘/CPU 占满
            time.sleep(0.01)

    def _load_thumb_image(self, path, target):
        """（后台线程里跑）把文件解码成 PIL 图片。不碰任何 Tk 东西。"""
        ext = os.path.splitext(path)[1].lower()
        is_image = ext in IMAGE_EXTS
        is_video = ext in VIDEO_EXTS
        is_exe = (ext == ".exe")
        is_shell = (ext in (".exe", ".url", ".lnk")) and HAS_WIN32
        img = None
        if is_shell:
            if is_exe:
                img = self._extract_exe_icon(path)
            else:
                img = self._extract_shell_icon(path)
        elif is_image:
            img = Image.open(path)
            img.load()
        elif is_video and HAS_CV2:
            cap = cv2.VideoCapture(path)
            if cap.isOpened():
                total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
                target_idx = max(1, total // 4) if total > 8 else 0
                cap.set(cv2.CAP_PROP_POS_FRAMES, target_idx)
                ok, frame = cap.read()
                if not ok:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ok, frame = cap.read()
                cap.release()
                if ok and frame is not None:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame)
        if img is None:
            return None
        # ★★ 2026-10-07 修「.url / .lnk 的图标调大档位也不变大」：
        #   `img.thumbnail()` **只会缩小，绝不会放大**。
        #   而 .url / .lnk / .exe 走的是「从系统取图标」那条路
        #   （`_extract_shell_icon` / `_extract_exe_icon`），
        #   系统给的**固定就那么点大**（一般 32px 上下）。
        #   于是档位调到"大/特大"时：target 明明要 96、128，
        #   thumbnail() 却只能保持 32 —— 用户看到的就是
        #   **「.url/.lnk 停在"中"档那么大、再也不长」**。
        #
        #   修法：先用 thumbnail 缩（防大图爆内存），
        #   再看**实际尺寸够不够**；不够就主动放大上去。
        #   ★ 放大用的是系统图标的放大 —— 会有点糊，但「跟着档位变大」
        #     比「纹丝不动」重要（用户要的就是它能变大）。
        #   ★ 图片/视频那条路不受影响：它们原图一般都远大于 target，
        #     thumbnail 缩完就已经接近 target，下面这个分支不会触发。
        img.thumbnail((target, target), Image.LANCZOS)
        try:
            _w, _h = img.size
            if max(_w, _h) < int(target) * 0.95:
                img = img.resize((int(target), int(target)), Image.LANCZOS)
        except Exception:
            pass
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        return img

    def _on_thumb_ready(self, key, pil_img):
        """（主线程里跑）后台读好了 → 转成 Tk 图片、记进缓存、重画一次。"""
        try:
            self._thumb_loading.discard(key)
        except Exception:
            pass
        if pil_img is None:
            try:
                self._thumb_failed.add(key)
            except Exception:
                pass
            return
        try:
            photo = ImageTk.PhotoImage(pil_img)
            self._thumbs[key] = photo
        except Exception:
            try:
                self._thumb_failed.add(key)
            except Exception:
                pass
            return
        # 读好一张就重画一次 —— 画的是内存里的图，很快（毫秒级）
        try:
            if not APP_CLOSING:
                self._redraw()
        except Exception:
            pass

    def _get_thumbnail_sync(self, path):
        """★ v26：**同步**取缩略图（老路子）。

        只给「必须当场拿到」的地方用（比如瀑布流大图标模式），
        列表模式一律走后台那条路，避免卡界面。
        """
        if not HAS_PIL:
            return None
        ext = os.path.splitext(path)[1].lower()
        is_image = ext in IMAGE_EXTS
        is_video = ext in VIDEO_EXTS
        is_shell = (ext in (".exe", ".url", ".lnk")) and HAS_WIN32
        if not (is_image or is_video or is_shell):
            return None
        target = self._target_thumb_size()
        key = (path, target)
        if key in self._thumbs:
            return self._thumbs[key]
        if key in self._thumb_failed:
            return None
        try:
            img = self._load_thumb_image(path, target)
            if img is None:
                self._thumb_failed.add(key)
                return None
            photo = ImageTk.PhotoImage(img)
            self._thumbs[key] = photo
            return photo
        except Exception:
            self._thumb_failed.add(key)
            return None

    @staticmethod
    def _extract_shell_icon(file_path, size=32):
        """用 Windows Shell 接口提取文件的系统图标（.url / .lnk 等）。"""
        if not HAS_WIN32:
            return None
        hicon = None
        hdc = None
        memdc = None
        hbmp = None
        try:
            from win32com.shell import shell, shellcon  # type: ignore
            flags = shellcon.SHGFI_ICON | shellcon.SHGFI_LARGEICON
            result = shell.SHGetFileInfo(file_path, 0, flags)
            hicon = result[1][0]
            if not hicon:
                return None

            hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
            memdc = hdc.CreateCompatibleDC()
            hbmp = win32ui.CreateBitmap()
            hbmp.CreateCompatibleBitmap(hdc, size, size)
            memdc.SelectObject(hbmp)
            win32gui.DrawIconEx(memdc.GetSafeHdc(), 0, 0, hicon, size, size,
                                0, None, win32con.DI_NORMAL)
            bmpinfo = hbmp.GetInfo()
            bmpstr = hbmp.GetBitmapBits(True)
            img = Image.frombuffer(
                "RGBA",
                (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
                bmpstr, "raw", "BGRA", 0, 1)
            return img
        except Exception:
            return None
        finally:
            try:
                if hicon:
                    win32gui.DestroyIcon(hicon)
            except Exception:
                pass
            try:
                if memdc:
                    memdc.DeleteDC()
            except Exception:
                pass
            try:
                if hdc:
                    hdc.DeleteDC()
            except Exception:
                pass
            try:
                if hbmp:
                    win32gui.DeleteObject(hbmp.GetHandle())
            except Exception:
                pass
            
    @staticmethod
    def _extract_exe_icon(exe_path, size=32):
        """从 exe 提取图标，返回 PIL.Image 或 None。仅 Windows + pywin32。"""
        if not HAS_WIN32:
            return None
        hicon = None
        hdc = None
        memdc = None
        hbmp = None
        try:
            large, small = win32gui.ExtractIconEx(exe_path, 0)
            if large:
                hicon = large[0]
            elif small:
                hicon = small[0]
            if hicon is None:
                return None

            hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
            memdc = hdc.CreateCompatibleDC()
            hbmp = win32ui.CreateBitmap()
            hbmp.CreateCompatibleBitmap(hdc, size, size)
            memdc.SelectObject(hbmp)

            win32gui.DrawIconEx(
                memdc.GetSafeHdc(), 0, 0, hicon, size, size,
                0, None, win32con.DI_NORMAL)

            bmpinfo = hbmp.GetInfo()
            bmpstr = hbmp.GetBitmapBits(True)

            img = Image.frombuffer(
                "RGBA",
                (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
                bmpstr, "raw", "BGRA", 0, 1)
            return img
        except Exception:
            return None
        finally:
            try:
                if hicon:
                    win32gui.DestroyIcon(hicon)
            except Exception:
                pass
            try:
                if memdc:
                    memdc.DeleteDC()
            except Exception:
                pass
            try:
                if hdc:
                    hdc.DeleteDC()
            except Exception:
                pass
            try:
                if hbmp:
                    win32gui.DeleteObject(hbmp.GetHandle())
            except Exception:
                pass

    def clear_thumbnail_cache(self):
        self._thumbs.clear()
        self._thumb_failed.clear()
        # ★ v26：后台队列也一起清掉（换目录时不该再读旧目录的图）
        try:
            with self._thumb_lock:
                self._thumb_queue.clear()
            self._thumb_loading.clear()
        except Exception:
            pass

    def _sort_rows(self, rows):
        if not self.sort_key:
            return rows
        k = self.sort_key
        asc = self.sort_asc

        def size_value(r):
            v = r.get("size_bytes")
            if v is None:
                return -1
            return v

        def tag_key(r):
            return "|".join(t[1].lower() for t in (r.get("tags") or []))

        if k == "size":
            keyfunc = size_value
        elif k == "tags":
            keyfunc = tag_key
        else:
            keyfunc = lambda r: (r.get(k) or "").lower()

        try:
            return sorted(rows, key=keyfunc, reverse=not asc)
        except Exception:
            return rows

    def set_sort(self, key):
        if self.sort_key == key:
            self.sort_asc = not self.sort_asc
        else:
            self.sort_key = key
            self.sort_asc = True
        self._apply_search_filter()


    def _list_cols(self):
        keys = ["name", "kind", "size", "location", "tags"]
        names = [T("名称"), T("类型"), T("大小"), T("所在位置"), T("标签")]
        # ★★ v26：**画布不够宽时，按「重要性权重」重新分配列宽。**
        #   原来列宽是死的（合计 920），而列表实际只有 788 ——
        #   Tk 不报错，只是把**名称列左边裁掉**（用识图看截图才发现：
        #   `机器抉择.txt` 显示成「器块择.txt」）。
        #   第一次改我用「按比例缩」，结果**名称列反而更窄了**（163），
        #   因为标签列的默认值是 240，按比例缩完还占 223。
        #   现在改成**按权重分**（学资源管理器）：
        #     名称列优先给够（这个最重要，谁都想先看清文件名），
        #     剩下的再按各列权重分给 类型/大小/位置/标签。
        widths = {}
        try:
            cw0 = self.canvas.winfo_width()
        except Exception:
            cw0 = 0
        keys_all = list(keys)
        gaps = self.GAP * (len(keys_all) - 1)
        left_fixed = self.PAD + self.SIDE_STRIP_L
        base_total = sum(self.col_w.get(k, 120) for k in keys_all)
        need = base_total + gaps + left_fixed + self.PAD
        if cw0 and cw0 > 60 and need > cw0:
            # 可用总宽（扣掉左边白条、间距、右内边距）
            avail = cw0 - gaps - left_fixed - self.PAD
            avail = max(240, avail)
            # 权重：名称 4，标签 2.2，位置 1.2，类型 0.7，大小 0.9
            weight = {"name": 4.0, "tags": 2.2, "location": 1.2,
                      "kind": 0.7, "size": 0.9}
            wsum = sum(weight.values())
            for k in keys_all:
                w = int(avail * weight[k] / wsum)
                w = max(self.MIN_COL_W.get(k, 50), w)
                widths[k] = w
            # ★ 名称列保底：画布越宽保底越高
            #   （画布特别窄的时候强行要 260 也没意义 —— 那时候
            #     连 260 都放不下，只会把别的列压成负数）
            name_floor = 260 if avail >= 700 else max(140, int(avail * 0.42))
            if widths["name"] < name_floor:
                shortage = name_floor - widths["name"]
                widths["name"] = name_floor
                others = [k for k in keys_all if k != "name"]
                osum = sum(weight[k] for k in others)
                for k in others:
                    cut = int(shortage * weight[k] / osum)
                    widths[k] = max(self.MIN_COL_W.get(k, 50),
                                    widths[k] - cut)
            # ★ 最后再核对一遍总宽：万一还是超了，把溢出量从最宽的列扣掉，
            #   免得 _total_w 比画布宽（那样会莫名出现横向滚动条）。
            cur = sum(widths.values())
            if cur > avail:
                over = cur - avail
                # 从「标签」开始扣，再扣「位置」，最后才动「名称」
                for k in ("tags", "location", "size", "kind", "name"):
                    if over <= 0:
                        break
                    can = widths[k] - self.MIN_COL_W.get(k, 50)
                    if can <= 0:
                        continue
                    take = min(can, over)
                    widths[k] -= take
                    over -= take
        cols = []
        # ★ v25 补丁21：列从「左白条」右边开始，左侧那条窄白条留给拉框用
        x = self.PAD + self.SIDE_STRIP_L
        for k, n in zip(keys, names):
            w = widths.get(k) or self.col_w.get(k, 120)
            cols.append((k, n, x, w))
            x += w + self.GAP
        # 记住「最后一列的右边界」：它右边那一整块（到 _total_w）都是空白，
        # 用来判断鼠标是不是按在白条上（_on_click 里要用）。
        self._cols_end = x - self.GAP
        # ★★ v25 补丁41：**「单击选不中文件」的真正元凶在这里。**
        #   上面这些列宽是**固定值**（名称 320 + 类型 90 + 大小 110 +
        #   位置 240 + 标签 220，加起来正好 980）。可是窗口一般有
        #   1400 像素宽 —— 于是「最后一列右边」到窗口右边之间，空了
        #   400 多像素的一条**死区**。在死区里点鼠标，_on_click 会把它
        #   当成「按在空白处」→ 不是选中文件，而是开始拉框，
        #   看起来就是「单击根本选不中文件」。
        #   资源管理器不是这么干的：它的「名称」列会**自动占满**剩下的
        #   宽度，列表一直铺到窗口右边，没有死区。
        #   所以这里照抄：把剩余宽度全补给「名称」列。
        #   ★ 两个保险：
        #     ① 用户**手动拖过**名称列宽度的话，就不再自动改它
        #        （尊重用户，别把人拖好的宽度又弹回去）；
        #     ② 最多补到 1600 像素，剩下的仍留作右侧白条。
        #
        # ★★ v26：**这一段（把剩余宽度补给名称列）已经并进上面那段
        #   「按权重分配」里了，这里必须删掉** —— 留着会打架：
        #   上面刚按 347 分好，这里又拿 canvas 宽度减 x 去补，
        #   结果补出一个比画布还宽的 _total_w（实测 1030 > 788），
        #   右边多出一条没用的横向滚动条。
        #   注意：删除后「点空白死区」那个老问题**不会回来** ——
        #   因为 _on_click 现在列表模式下只看纵向（见 v26 的说明），
        #   横向点哪儿都算这一行。
        return cols

    def _draw_header(self):
        if self.layout_mode != "list":
            return
        c = self.header
        c.delete("all")
        w = c.winfo_width()
        if w <= 1:
            return
        y = self.header.winfo_height() // 2
        cols = self._list_cols()
        for (k, n, x, cw) in cols:
            arrow = ""
            if self.sort_key == k:
                arrow = " ▲" if self.sort_asc else " ▼"
            text = n + arrow
            anchor = "e" if k == "size" else ("center" if k == "kind" else "w")
            tx = x + (cw - 20 if anchor == "e" else (cw // 2 if anchor == "center" else 0))
            # ★★ 2026-10-07：原来"正在排序的那一列"写死 "#2c3e50"、
            #   其它列写死 "#555" —— 两个都是深色，**夜间在深底上都看不见**
            #   （用户说"好多地方夜间字体颜色都比较深"就包括这儿）。
            #   改成用主题色：排序那列用 accent（醒目），其它用 fg。
            color = theme_get("accent") if self.sort_key == k else theme_get("fg")
            c.create_text(tx, y, text=text, anchor=anchor,
                          font=self.font_header, fill=color)
            sep_x = x + cw
            if sep_x < w - 2:
                c.create_line(sep_x, 4, sep_x, self.HEADER_H_BASE - 4,
                              fill=theme_get("line"), width=1)
        c.create_line(0, self.HEADER_H_BASE - 1, w, self.HEADER_H_BASE - 1,
                      fill=theme_get("line"))

    def _hit_header_sep(self, x):
        cols = self._list_cols()
        for (k, _n, cx, cw) in cols:
            sep_x = cx + cw
            if abs(x - sep_x) <= 4:
                return k
        return None

    def _hit_header_col(self, x):
        cols = self._list_cols()
        for (k, _n, cx, cw) in cols:
            if cx <= x <= cx + cw:
                return k
        return None

    def _on_header_motion(self, event):
        if self._header_drag_col:
            return
        k = self._hit_header_sep(event.x)
        try:
            self.header.configure(cursor="sb_h_double_arrow" if k else "")
        except Exception:
            pass

    def _on_header_click(self, event):
        sep_k = self._hit_header_sep(event.x)
        self._header_press_x = event.x
        self._header_press_col = sep_k
        if sep_k:
            self._header_drag_col = sep_k
            self._header_drag_start_x = event.x
            self._header_drag_start_w = self.col_w.get(sep_k, 120)
            try:
                self.header.configure(cursor="sb_h_double_arrow")
            except Exception:
                pass
            return
        col_k = self._hit_header_col(event.x)
        if col_k:
            self.set_sort(col_k)

    def _on_header_drag(self, event):
        if not self._header_drag_col:
            return
        dx = event.x - self._header_drag_start_x
        new_w = max(self.MIN_COL_W.get(self._header_drag_col, 60),
                    self._header_drag_start_w + dx)
        self.col_w[self._header_drag_col] = new_w
        # ★ v25 补丁41：用户**手动调过列宽**了 —— 记一笔，
        #   以后 _list_cols 就别再自动把名称列撑满（不然刚拖好又弹回去）。
        if self._header_drag_col == "name":
            self._name_col_manual = True
        self._draw_header()
        self._redraw()

    def _on_header_release(self, event):
        self._header_drag_col = None
        self._header_press_x = None
        self._header_press_col = None
        try:
            self.header.configure(cursor="")
        except Exception:
            pass

    def _grid_card_width(self):
        return max(90, self.icon_px + 36)

    def _grid_img_px(self):
        """瀑布流里「一张缩略图占多大」。

        ★ 2026-10-03 新增：在最大那一档上，卡片会被撑满整行（一排 8 个），
          这时候缩略图也跟着变大（存在 self._grid_px 里），不然会变成
          「卡片很宽、图还是小小的挤在中间」。
        """
        try:
            v = int(getattr(self, "_grid_px", 0) or 0)
        except Exception:
            v = 0
        try:
            base = int(self.icon_px)
        except Exception:
            base = 16
        return max(16, v or base)

    def _wrap_tags(self, tags, max_w):
        lines = []
        cur = []
        cur_w = 0
        pad_x = self._tag_pad_x()
        for (tid, tname, tcolor) in tags:
            if tid in self.hidden_tag_ids:
                continue
            tw = self.font_tag.measure(tname) + pad_x * 2
            if cur_w + tw > max_w and cur:
                lines.append(cur)
                cur = []
                cur_w = 0
            cur.append((tname, tcolor))
            cur_w += tw + 4
        if cur:
            lines.append(cur)
        return lines

    def _wrap_name_lines(self, text, font, max_w, max_lines=3):
        if not text:
            return [""]
        if font.measure(text) <= max_w:
            return [text]
        lines = []
        rest = text
        for line_idx in range(max_lines):
            if not rest:
                break
            if font.measure(rest) <= max_w:
                lines.append(rest)
                rest = ""
                break
            lo, hi = 0, len(rest)
            while lo < hi:
                mid = (lo + hi + 1) // 2
                suffix = "…" if line_idx == max_lines - 1 else ""
                if font.measure(rest[:mid] + suffix) <= max_w:
                    lo = mid
                else:
                    hi = mid - 1
            if lo <= 0:
                lines.append(rest[:1] + "…")
                rest = ""
                break
            lines.append(rest[:lo])
            rest = rest[lo:]
        if rest and lines:
            lines[-1] = lines[-1] + "…"
        return lines

    def _compute_grid_card_height(self, row):
        # ★ 2026-10-03：卡片宽度以**这次真正用的**为准（最大档会被撑宽）
        try:
            _cw = int(getattr(self, "_grid_card_w", 0) or 0)
        except Exception:
            _cw = 0
        max_w = (_cw or self._grid_card_width()) - 12
        h = self._grid_img_px() + 8
        name_lines = self._wrap_name_lines(row["name"], self.font, max_w, max_lines=3)
        line_h = self.font.metrics("linespace")
        h += len(name_lines) * line_h + 6
        tag_lines = self._wrap_tags(row["tags"], max_w)
        if len(tag_lines) > self.GRID_MAX_TAG_LINES:
            tag_lines = tag_lines[:self.GRID_MAX_TAG_LINES]
        pill_h = self._tag_pill_half_h() * 2
        tag_line_h = max(pill_h + 6, self.font_tag.metrics("linespace") + 6)
        if tag_lines:
            h += len(tag_lines) * tag_line_h + 6
        h += 8
        return h, name_lines, tag_lines

    def _recompute_layout(self):
        # ★★ v26：**这里加一个「用得着才重排」的短路。**
        #   背景：列表里选中**一个**「有标签」的文件时，那一行会**展开**
        #   （多显示一行标签），行高变大 26~40 像素 —— 于是它下面
        #   **所有行**的 y 坐标都得重算，整张表要重画一遍。
        #   你框选几十个（这时不展开）之后单击某一个（这时展开），
        #   就正好踩中「从多选变单个」这一下 —— 800 行的表整排整画，
        #   实测能卡 2 秒多。加上文件多、标签多，就更明显。
        #   修法：先算一下「这次重排的结果会不会和上次一样」——
        #   行的数量和每一行的展开状态都没变，就**直接用上次的结果**，
        #   别再算 800 遍、也别触发重画。
        if self.layout_mode == "list" and self._layout:
            try:
                # ★★ 2026-10-07 修一个真崩溃（账本抓到的）：
                #   `KeyError: 'expanded'` + 「画列表时中途出错（列表可能只显示一半）」
                #   已出现 5 次。
                #
                #   病根：下面这个「形状没变就沿用旧布局」的短路，
                #   只检查了 `layout_mode == "list"`，**但没检查旧布局本身
                #   是不是 list 的**。
                #   从「瀑布流」切回「列表」时，`_layout` 里还是 grid 的项
                #   （grid 项**没有 "expanded" 这个键**），如果行数恰好相同，
                #   短路就认为「形状没变」直接返回 —— 于是 `_redraw_list`
                #   拿着 grid 的项去画，撞上 `item["expanded"]` 就炸，
                #   **列表只画到一半就停住**（用户看到的就是"显示不全"）。
                #
                #   修法：短路之前先确认**旧布局确实是 list 项**。
                #   只认第一项就够（同一批布局的项格式一定一致）。
                _first = self._layout[0] if self._layout else None
                if (not isinstance(_first, dict)
                        or _first.get("kind") != "list"
                        or "expanded" not in _first):
                    # 旧布局不是 list 的（是 grid、或者是老格式）→ 必须重排
                    raise ValueError("旧布局格式对不上，强制重排")
                single = len(self.selected_paths) == 1
                if single:
                    _sel1 = next(iter(self.selected_paths))
                else:
                    _sel1 = None
                # 只有「选中是不是单个」和「哪一行展开」会改变行高
                old_single = getattr(self, "_layout_single_sel", None)
                old_exp = getattr(self, "_layout_expanded_idx", None)
                same_shape = True
                if old_single != single:
                    same_shape = False
                else:
                    if single:
                        # 单个选中 → 只有那一行可能展开
                        new_exp = None
                        for r in self.rows:
                            if r["path"] == _sel1 and r.get("tags"):
                                new_exp = r["path"]
                                break
                        if new_exp != old_exp:
                            same_shape = False
                    else:
                        # 多选 / 没选 → 一行都不展开
                        if old_exp is not None:
                            same_shape = False
                if (same_shape and len(self._layout) == len(self.rows)
                        and len(self.rows) > 0):
                    # ★★ 2026-10-07 修「调缩略图大小，行高不变、显示被挤压」：
                    #   上面算的 same_shape **只看"哪一行展开"**，
                    #   完全没看**图标大小（icon_px）**。
                    #   而列表的行高是 `max(24, icon_px+8, 字高+8)` ——
                    #   **icon_px 变了行高就必须跟着变**。
                    #   于是用户把缩略图调大时：形状判定"没变"→ 直接 return
                    #   → 行的 y 坐标还是按**旧的小行高**算的
                    #   → 图标画在大行距的位置上，**互相挤压、看着叠在一起**。
                    #
                    #   修法：把「上次重排时的 icon_px」也记下来，
                    #   跟这次的比一下，不一样就必须重排。
                    if getattr(self, "_layout_icon_px", None) != self.icon_px:
                        same_shape = False
                if (same_shape and len(self._layout) == len(self.rows)
                        and len(self.rows) > 0):
                    return          # 形状没变，沿用上次的布局
            except Exception:
                pass
        self._layout = []
        self._total_h = 0
        self._total_w = 0
        # ★★ 2026-10-07：记下「这次重排用的是多大的图标」。
        #   下次 `_recompute_layout` 的短路要靠它判断"要不要重排" ——
        #   图标大小变了行高就必须变，不能沿用旧布局。
        #   （这就是「调缩略图大小、行高不变、显示被挤压」的根因。）
        #   ★ 网格模式也受 icon_px 影响（卡片高是按图标算的），所以同一个值够用。
        try:
            self._layout_icon_px = self.icon_px
        except Exception:
            pass

        if self.layout_mode == "list":
            font_h = self.font.metrics("linespace")
            row_h = max(24, self.icon_px + 8, font_h + 8)
            y = 0
            single_sel = len(self.selected_paths) == 1
            expanded_extra = max(26, font_h + 14)
            _expanded_path = None
            for i, row in enumerate(self.rows):
                expanded = (single_sel and row["path"] in self.selected_paths
                            and bool(row["tags"]))
                if expanded:
                    _expanded_path = row["path"]
                h = (row_h + expanded_extra) if expanded else row_h
                self._layout.append({"kind": "list", "y0": y, "y1": y + h,
                                     "idx": i, "expanded": expanded})
                y += h
            # ★ 记下来，下次好判断「形状有没有变」
            self._layout_single_sel = single_sel
            self._layout_expanded_idx = _expanded_path
            self._total_h = y + 40          # ★ 补丁20：底下永远留一条空白，
                                            #   这样「拉方框」随时有地方起手
            cols = self._list_cols()
            last = cols[-1]
            # ★ v25 补丁21：右边界再加上 60 像素白条 —— 结果是「列表右边
            #   永远有一块空白」，鼠标停在那上面就能拉方框（和资源管理器一样）。
            # ★ v25 补丁41：但白条**不该比窗口还宽**。
            #   补丁41 让「名称」列自动吃满剩余宽度之后，列表本身已经
            #   铺到窗口右边了，这里再硬加 60 像素白条，_total_w 就会比
            #   画布还宽 —— 结果右边凭空多出一条**没用的横向滚动条**。
            #   ★ 用 _cols_end（_list_cols 里算出来的「最后一列右边界」）
            #     作为准绳，而不是重算 last[2]+last[3]：
            #     两者在名称列自动撑宽之后可能不一致，之前实测就出现过
            #     _cols_end(1160) > _total_w(1050) 的矛盾值。
            try:
                _cw = self.canvas.winfo_width()
            except Exception:
                _cw = 0
            # ★ v26：**别用 getattr(self, "_cols_end")**。
            #   那是上一次调 _list_cols() 留下的值，这时候可能已经过时
            #   （实测出现过 _cols_end=780 但 _total_w 却算成 1030 的情况）。
            #   直接用**刚刚这份 cols** 算，绝对一致。
            _cols_end = last[2] + last[3]
            self._cols_end = _cols_end
            _w_with_strip = _cols_end + self.PAD + self.SIDE_STRIP_R
            if _cw and _cw > 4:
                # ★ v26：**列宽超过画布时，最后再兜一次底。**
                #   为什么要这一步：_list_cols() 里判断"够不够宽"用的是
                #   它自己那一刻量到的画布宽度，而画布在**布局还没稳定**
                #   的时候会报 1 像素 —— 那一轮就不会压缩列宽，
                #   于是 _total_w 会比画布宽（实测 1030 > 319），
                #   表现就是莫名多出横向滚动条、或者最后一列被挡住。
                #   这里用**这一刻**的真实宽度再核一遍，超了就按比例缩。
                if _cols_end > _cw:
                    avail_w = _cw - (self.PAD + self.SIDE_STRIP_L
                                     + self.GAP * (len(cols) - 1))
                    if avail_w > 240:
                        ratio = avail_w / float(_cols_end - self.PAD
                                                - self.SIDE_STRIP_L)
                        nx = self.PAD + self.SIDE_STRIP_L
                        new_cols = []
                        for (k, n, cx, cw2) in cols:
                            w2 = max(self.MIN_COL_W.get(k, 50),
                                     int(cw2 * ratio))
                            new_cols.append((k, n, nx, w2))
                            nx += w2 + self.GAP
                        cols = new_cols
                        last = cols[-1]
                        _cols_end = last[2] + last[3]
                        self._cols_end = _cols_end
                        _w_with_strip = _cols_end + self.PAD + self.SIDE_STRIP_R
                self._total_w = min(_w_with_strip, _cw)
            else:
                self._total_w = _w_with_strip
        else:
            cw = self.canvas.winfo_width() or 800
            card_w = self._grid_card_width()
            col_gap = self.GAP
            usable = cw - 2 * self.PAD
            n_cols = max(1, (usable + col_gap) // (card_w + col_gap))
            # ★★ 2026-10-03：用户要求「瀑布流把缩略图拉到最大、而且是只显示
            #   文件列表区域的时候，希望**一排正好 8 个**」。
            #   做法：在**最大那一档**上把列数封顶 8 个，并且把卡片宽度
            #   撑满整行（缩略图跟着一起变大）—— 而不是左边挤一排、
            #   右边空一大片。
            self._grid_px = 0
            try:
                _is_max = int(getattr(self, "icon_level", 0)) >= len(self.icon_sizes()) - 1
            except Exception:
                _is_max = False
            if _is_max:
                # ★ 用户要求：缩略图拉到最大、而且**只显示文件列表**时，
                #   一排正好 8 个。做法：
                #     · 宽度够（每格至少 140 像素）→ 咬死 8 个，
                #       格子宽度 = 可用宽度 ÷ 8（缩略图跟着一起变大）；
                #     · 宽度不够（右边还开着预览/标签库）→ 按实际能放几个算；
                #     · 窗口特别宽时格子最多 340 像素（再宽就多排几列，
                #       免得一张图占半个屏幕）。
                _want = 8
                _fit = (usable + col_gap) // _want - col_gap
                if _fit > 340:
                    card_w = 340
                    n_cols = max(_want, int((usable + col_gap) // (card_w + col_gap)))
                    self._grid_px = max(0, card_w - 16)
                elif _fit >= 140:
                    n_cols = _want
                    card_w = max(90, _fit)
                    self._grid_px = max(0, card_w - 16)
                elif n_cols > _want:
                    n_cols = _want
            col_ys = [self.PAD] * n_cols
            # ★ 记下这一轮真正用的卡片宽度（名字换行、算高度都要用它）
            self._grid_card_w = card_w
            for i, row in enumerate(self.rows):
                c = col_ys.index(min(col_ys))
                x0 = self.PAD + c * (card_w + col_gap)
                y0 = col_ys[c]
                card_h, name_lines, tag_lines = self._compute_grid_card_height(row)
                y1 = y0 + card_h
                self._layout.append({
                    "kind": "grid",
                    "x0": x0, "y0": y0, "x1": x0 + card_w, "y1": y1,
                    "idx": i,
                    "name_lines": name_lines,
                    "tag_lines": tag_lines,
                })
                col_ys[c] = y1 + col_gap
            self._total_h = max(col_ys) + self.PAD
            self._total_w = self.PAD + n_cols * (card_w + col_gap) + self.PAD

        self.canvas.configure(
            scrollregion=(0, 0, max(self._total_w, 1), max(self._total_h, 1)))
        # ★ v26：横向滚动条按需显示（内容比画布宽才出来）
        self._sync_hscrollbar()

    def _sync_hscrollbar(self):
        """★★ v26：内容比画布宽才显示横向滚动条，否则收起来。

        ★ v26 修正：以前它 pack 在 body 里（和 canvas 同一层），
          而 canvas 是 side="left" + expand=True、它是 side="bottom"
          —— 两种方向混在一个容器里，Tk 分配高度时会
          把画布压得很奇怪（用户反馈的「拉不宽」就是这个）。
          现在它在 self 这一层，永远贴底，出现消失都不影响画布。
        """
        try:
            cw = self.canvas.winfo_width()
            need = self._total_w
            if cw <= 1:
                return
            should = need > cw + 2
            if should == getattr(self, "_hsb_visible", False):
                return
            self._hsb_visible = should
            if should:
                # side="bottom" + 不指定 before：pack 在最后 = 最底下
                self.hsb.pack(side="bottom", fill="x")
            else:
                self.hsb.pack_forget()
                try:
                    self.canvas.xview_moveto(0)
                except Exception:
                    pass
        except Exception:
            pass

    def _on_canvas_config(self):
        self._recompute_layout()
        self._redraw()

    def _ensure_canvas_size(self, tries=25):
        """★ v25 补丁37：把「画布一直只有 1x1 像素」这件事救回来。

        ★ 这是用户报的「**单击没法选中文件，只可以框选**」的真正原因：
          文件列表上方的标题一旦变成「竖直书写」（请求高度几百万像素），
          就会把文件区挤成 1 像素高。而 Tk 对**尺寸为 1 像素的画布不再
          投递鼠标事件** —— 所以单击完全没反应；框选之所以还能用，
          是因为它靠的是拖动。
        做法：① 先把标题的高度问题兜住；② 每 120 毫秒量一次画布，
        量到真实宽度就重排 + 重画。
        """
        try:
            # ★★ v26 补丁（2026-10-03）：这里原来是 `self._fix_list_title_height()`，
            #   可**文件列表（FileList）自己根本没有这个方法** —— 它只写在主程序
            #   （FileTaggerApp）那一层。于是这一行每次都会抛 AttributeError，
            #   被下面的 except 一口吞掉：**这道「标题被撑成竖直书写」的保险
            #   从装上去那天起就没生效过**（出问题时「🔔 问题」里也不会有记录）。
            #   现在改成走主程序注入进来的回调：有就调用，没有就安静跳过。
            _fix = getattr(self, "on_fix_title", None)
            if _fix is not None:
                _fix()
        except Exception:
            pass
        try:
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
        except Exception:
            return
        if w > 4 and h > 4:
            try:
                self._recompute_layout()
                self._redraw()
            except Exception:
                pass
            return
        if tries <= 0:
            return
        # 顺手请外面的 paned 再算一次分栏（尺寸没定下来多半是这里）
        if tries % 4 == 0:
            try:
                cb = getattr(self, "on_need_relayout", None)
                if cb:
                    cb()
            except Exception:
                pass
        try:
            self.after(120, lambda: self._ensure_canvas_size(tries - 1))
        except Exception:
            pass

    def set_rows(self, rows):
        self._all_rows = list(rows)
        self._apply_search_filter()      # 里面会刷新「显示 N / M」
        # ★ 补丁37：列表换内容之后，量一次画布，别让它停在 1x1
        try:
            self._ensure_canvas_size()
        except Exception:
            pass

    def refresh_all_tags(self, tag_map):
        for r in self._all_rows:
            r["tags"] = tag_map.get(r["path"], [])
        self._apply_search_filter()

    def _redraw(self):
        # ★★ v25 补丁43（现在叫 v26）：**这里原来整段代码写了两遍！**
        #   从 `c.delete("all")` 到 `_redraw_list()` 被原样复制了一份 ——
        #   也就是说每次重绘都：清空画布 → 画 800 行 → **又清空** → 再画 800 行。
        #   白白干了一倍的活（实测重绘从 0.05 秒变成 0.10 秒）。
        #   （是补丁41 改 `_total_w` 那一段时不小心留下的，当时没看出来。）
        #   用户反馈「多选后单击会卡住」有它一份。
        c = self.canvas
        c.delete("all")
        # ★★ 2026-10-07：每次重绘都**按当前皮肤重设一次底色**。
        #   为什么：切皮肤时 `_retheme_tree()` 那套「按对照表翻色」会把这个
        #   `tk.Frame` 的 bg 翻歪（实测切夜间后它变成 `#d6d7db` 浅灰——
        #   那是**字色**，不是底色）。这里用 `theme_get` 纠回来，
        #   保证无论中间被翻成什么，重绘一次就正确。
        try:
            _bg = theme_get("card_bg")
            if str(self.cget("bg")) != str(_bg):
                self.configure(bg=_bg)
        except Exception:
            pass
        w = c.winfo_width()
        # ★★ 2026-10-05「先加说话」：以前这里是 `if w <= 1: return` ——
        #   宽度一时拿不到（窗口刚建、刚最大化、切换布局的那一瞬间）
        #   就**什么都不画，直接返回**，用户看到的就是**一片空白**。
        #   这正是用户抱怨的「界面有些部分经常显示不全」的一个真凶。
        #   现在：拿不到宽度就先「量一下再说」，实在量不到就先用个
        #   保守的宽度把内容画出来 —— **宁可画得不准，也别一片空白**。
        if w <= 1:
            try:
                c.update_idletasks()
                w = c.winfo_width()
            except Exception as _e:
                note_swallowed(T("文件列表：量画布宽度失败"), _e, quiet=True)
            if w <= 1:
                try:
                    w = int(c.winfo_reqwidth()) or 0
                except Exception:
                    w = 0
            if w <= 1:
                w = 600      # 最后的兜底：给个保守宽度，**照样把内容画出来**
                try:
                    self._relayout_panes_soon()
                except Exception:
                    pass
        if not self.rows:
            msg = "（没有匹配的文件）" if self.search_text else "（这里还没有文件）"
            c.create_text(w // 2, 40, text=msg, fill=theme_get("line"), font=(FONT, UI_FONT_SIZE))
        elif self.layout_mode == "list":
            try:
                self._redraw_list()
            except Exception as _e:
                # ★★ 2026-10-05「先加说话」：以前这里没有保护 —— 画列表
                #   中途出错就**画一半停住**，用户看到的就是「显示不全」。
                #   现在不但记一笔，还**自己重试一次**：先把画布清干净，
                #   再退回「只画文件名」的简单画法，保证至少看得见东西。
                note_swallowed(T("文件列表：画列表时中途出错（列表可能只显示一半）"), _e)
                try:
                    c.delete("all")
                    self._redraw_list_fallback()
                except Exception as _e2:
                    note_swallowed(T("文件列表：退回简单画法也失败了（列表空着）"), _e2)
        else:
            try:
                self._redraw_grid()
            except Exception as _e:
                note_swallowed(T("文件列表：画瀑布流缩略图时出错（可能只显示一部分）"), _e)
                try:
                    c.delete("all")
                    self._redraw_list_fallback()
                except Exception as _e2:
                    note_swallowed(T("文件列表：退回简单画法也失败了（列表空着）"), _e2)
        # 拖动到文件夹时，顶上飘一条黄色提示
        if getattr(self, "_drop_hint", None):
            try:
                c.create_rectangle(0, 0, w, 24, fill=theme_get("find_bg"),
                                   outline="#e0c46c")
                c.create_text(8, 12, text=self._drop_hint, anchor="w",
                              fill=theme_get("warn"), font=(FONT, UI_FONT_SIZE, BOLD))
            except Exception:
                pass
        # ★ v26 修正：**画完内容，顺手把表头也重画一遍。**
        #   用户反馈「标签栏和对应的标签位置是错位的」——表头写着
        #   「标签」的地方下面其实是别的列，标签胶囊跑到了「所在位置」
        #   那一列的下面。
        #
        #   原因见 __init__ 里那段注释（表头不再自己响应尺寸变化）。
        #   这里做的就是把表头**挂在内容后面一起画**：
        #   每次 _redraw()（内容包括画完后），都按**同一时刻**的
        #   canvas 宽度重新算一遍列位置、把表头重画一遍 ——
        #   两次用的是同一个宽度、同一份 `_list_cols()` 结果，
        #   两边就永远对齐。
        try:
            if self.layout_mode == "list":
                self._draw_header()
        except Exception as _e:
            # ★★ 2026-10-05「先加说话」：以前这里是 `pass` —— 表头画不出来
            #   也没人知道，用户看到的就是「显示不全 / 表头错位」。
            #   现在记一笔，进「🔔 问题」面板。
            note_swallowed(T("文件列表：画表头失败（列表顶部可能空着或错位）"), _e)

    def _redraw_list_fallback(self):
        """★★ 2026-10-05「先加说话」：**保命画法**。

        什么时候用：正常的画法（列表 / 瀑布流）中途出错了。
        干什么：不管三七二十一，**把文件名一行一行画出来**，
               保证用户**至少能看见东西**，而不是一片空白。

        ★ 为什么要有它：用户抱怨「界面有些部分经常显示不全」。
          显示不全是结果，但如果出错之后**连退路都没有**，
          用户就只能看到一块空白、还不知道为什么。
          这个保命画法让「最坏情况」从「一片空白」变成
          「能看能点，只是朴素一点」。
        ★ 故意写得极简单（不碰缩略图、不排复杂列），
          越简单越不容易再出错。
        """
        c = self.canvas
        w = c.winfo_width() or 600
        y = 4
        try:
            c.create_text(8, y, anchor="nw",
                          text=T("⚠ 正常画法出错了，下面是保命画法（点右下角「🔔 问题」看原因）"),
                          fill=theme_get("danger"), font=(FONT, UI_FONT_SIZE, BOLD))
            y += 26
        except Exception:
            pass
        drawn = 0
        for item in self._layout:
            if drawn > 400:       # 别画太多，保证不卡
                break
            try:
                name = item.get("name") or ""
                if not name:
                    p = item.get("path") or ""
                    name = os.path.basename(p.rstrip("\\/")) or p
                c.create_text(8, y, anchor="nw", text=name,
                              fill=theme_get("fg"), font=(FONT, UI_FONT_SIZE))
            except Exception:
                pass
            y += 22
            drawn += 1
        try:
            c.configure(scrollregion=(0, 0, w, max(y + 20, 100)))
        except Exception:
            pass

    def _redraw_list(self):
        c = self.canvas
        cols = self._list_cols()
        top_y = c.canvasy(0)
        canvas_h = c.winfo_height() or 400
        for item in self._layout:
            y0 = item.get("y0")
            y1 = item.get("y1")
            if y0 is None or y1 is None:
                continue
            if y1 < top_y:
                continue
            if y0 > top_y + canvas_h:
                break
            # ★★ 2026-10-07：`expanded` 用 get 取（原来直接 item["expanded"]）。
            #   万一布局格式对不上（比如刚从瀑布流切过来），
            #   也只会**这一行画得不对**，而不是整个列表画到一半炸掉。
            #   （真正的原因已经在 _recompute_layout 里修了，
            #     这里只是"再坏也不会坏成这样"的兜底。）
            self._draw_row_list(item.get("idx", 0), y0, y1,
                                bool(item.get("expanded")), cols)
    def _redraw_grid(self):
        c = self.canvas
        top_y = c.canvasy(0)
        top_x = c.canvasx(0)
        canvas_h = c.winfo_height() or 400
        canvas_w = c.winfo_width() or 600
        for item in self._layout:
            y0 = item["y0"]
            y1 = item["y1"]
            x0 = item["x0"]
            x1 = item["x1"]
            if y1 < top_y or y0 > top_y + canvas_h:
                continue
            if x1 < top_x or x0 > top_x + canvas_w:
                continue
            self._draw_card_grid(item)

    def _ellipsize(self, text, font, max_w):
        if not text:
            return ""
        if font.measure(text) <= max_w:
            return text
        lo, hi = 0, len(text)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if font.measure(text[:mid] + "…") <= max_w:
                lo = mid
            else:
                hi = mid - 1
        return text[:lo] + "…"

    def _draw_row_list(self, i, y0, y1, expanded, cols):
        c = self.canvas
        row = self.rows[i]
        selected = row["path"] in self.selected_paths
        # ★★ 2026-10-06：这几行颜色原来是写死的（theme_get("select_bg") / theme_get("stripe_bg") / white），
        #   所以一换夜间皮肤，文件列表还是白晃晃的一大片 —— 正是
        #   用户嫌「晚上不开灯闪眼睛」的主要来源。现在全部按皮肤取。
        _th = _themes_now()
        if selected:
            bg = _th["select_bg"]
        else:
            bg = _th["stripe_bg"] if i % 2 else _th["card_bg"]
        c.create_rectangle(0, y0, max(self._total_w, c.winfo_width()), y1,
                           fill=bg, outline="")

        icon_box = self.icon_px
        icon_x = cols[0][2]
        icon_y = (y0 + y1) // 2
        is_dir = row["kind"] == "文件夹"
        thumb = None
        if not is_dir:
            thumb = self._get_thumbnail(row["path"])
        if thumb is not None:
            c.create_image(icon_x + icon_box // 2, icon_y,
                           image=thumb, anchor="center")
        else:
            # ★★ 2026-10-07 修「图标太小」：
            #   用户反馈「图标之类的大小和我们设的不一致，太小了」。
            #   查出来是**两重缩小叠加**：
            #     ① 图标 PNG 自己四周留了 9% 的白边（设计时为了缩小时不被切），
            #        实测**有效内容只占画布的 80%**；
            #     ② 我这里又乘了 0.88。
            #   两下一乘 = 0.80 × 0.88 = **70%** —— 当然显小。
            #   现在改成**按格子的 96% 出图**（留一点点缝，不至于贴边），
            #   相当于把图放大到几乎顶满格子：视觉上大了一圈。
            ico_px = max(16, int(icon_box * 0.96))
            photo = get_file_icon(row["name"], is_dir, ico_px)
            if photo is not None:
                c.create_image(icon_x + icon_box // 2, icon_y,
                               image=photo, anchor="center")
            else:
                emoji = icon_for_file(row["name"], is_dir)
                fs = max(10, int(icon_box * 0.7))
                # 深色模式下退回纯符号 + 主题前景色（emoji 不跟随前景色）
                if dark_mode_now():
                    emoji = icon_for_file_dark(row["name"], is_dir, emoji)
                    c.create_text(icon_x + icon_box // 2, icon_y, text=emoji,
                                  font=(FONT, fs), anchor="center",
                                  fill=_themes_now()["fg"])
                else:
                    c.create_text(icon_x + icon_box // 2, icon_y, text=emoji,
                                  font=("Segoe UI Emoji", fs),
                                  anchor="center")

        text_x = icon_x + icon_box + 8

        line_h = self.font.metrics("linespace")
        y_top = y0 + (max(24, self.icon_px + 8, line_h + 8) - line_h) // 2 + line_h // 2

        for (k, _n, cx, cw) in cols:
            avail = cw - 8
            if k == "name":
                x = text_x
                max_w = (cx + cw - 8) - x
                if max_w < 20:
                    continue
                v = self._ellipsize(row["name"], self.font, max_w)
                y_mid = (y0 + y1) // 2 if not expanded else y_top
                c.create_text(x, y_mid, text=v, anchor="w",
                              font=self.font, fill=_themes_now()["fg"])
            elif k == "kind":
                v = self._ellipsize(row["kind"], self.font_small, avail)
                y_mid = (y0 + y1) // 2 if not expanded else y_top
                c.create_text(cx + cw // 2, y_mid, text=v,
                              anchor="center", font=self.font_small,
                              fill=_themes_now()["fg_dim"])
            elif k == "size":
                y_mid = (y0 + y1) // 2 if not expanded else y_top
                c.create_text(cx + cw - 8, y_mid, text=row["size"], anchor="e",
                              font=self.font_small,
                              fill=_themes_now()["fg_dim"])
            elif k == "location":
                v = self._ellipsize(row["location"] or "",
                                    self.font_small, avail)
                y_mid = (y0 + y1) // 2 if not expanded else y_top
                c.create_text(cx, y_mid, text=v, anchor="w",
                              font=self.font_small,
                              fill=_themes_now()["fg_dim"])

        tag_col = None
        for (k, _n, cx, cw) in cols:
            if k == "tags":
                tag_col = (cx, cw)
                break
        if tag_col is None:
            return
        tx = tag_col[0]
        right = tag_col[0] + tag_col[1]

        pad_x = self._tag_pad_x()
        pill_hh = self._tag_pill_half_h()

        if expanded:
            ty = y1 - 8 - pill_hh
            tx = text_x
            for (tid, tname, tcolor) in row["tags"]:
                if tid in self.hidden_tag_ids:
                    continue
                tw = self.font_tag.measure(tname) + pad_x * 2
                if tx + tw > right:
                    break
                c.create_rectangle(tx, ty - pill_hh, tx + tw, ty + pill_hh,
                                   fill=tcolor, outline="")
                fg = text_color_for(tcolor)
                c.create_text(tx + tw // 2, ty, text=tname,
                              font=self.font_tag, fill=fg)
                tx += tw + 4
        else:
            y_mid = (y0 + y1) // 2
            for (tid, tname, tcolor) in row["tags"]:
                if tid in self.hidden_tag_ids:
                    continue
                if tx >= right - 16:
                    break
                tw = self.font_tag.measure(tname) + pad_x * 2
                if tx + tw > right:
                    tw = right - tx
                    if tw < pad_x * 3:
                        break
                c.create_rectangle(tx, y_mid - pill_hh,
                                   tx + tw, y_mid + pill_hh,
                                   fill=tcolor, outline="")
                fg = text_color_for(tcolor)
                c.create_text(tx + tw // 2, y_mid, text=tname,
                              font=self.font_tag, fill=fg)
                tx += tw + 4

    def _draw_card_grid(self, item):
        c = self.canvas
        i = item["idx"]
        x0 = item["x0"]
        y0 = item["y0"]
        x1 = item["x1"]
        y1 = item["y1"]
        row = self.rows[i]
        selected = row["path"] in self.selected_paths

        if selected:
            # ★ 2026-10-06：跟着皮肤走（夜间不再是一块亮蓝）
            c.create_rectangle(x0, y0, x1, y1,
                               fill=_themes_now()["select_bg"],
                               outline=_themes_now()["accent"], width=2)
        else:
            c.create_rectangle(x0, y0, x1, y1,
                               fill=_themes_now()["stripe_bg"],
                               outline=_themes_now()["line"], width=1)

        icon_box = self._grid_img_px()
        cx_center = (x0 + x1) // 2
        icon_top = y0 + 8
        is_dir = row["kind"] == "文件夹"
        thumb = None
        if not is_dir:
            thumb = self._get_thumbnail(row["path"])
        if thumb is not None:
            c.create_image(cx_center, icon_top + icon_box // 2,
                           image=thumb, anchor="center")
        else:
            # ★★ 2026-10-07：改成 96%（理由见列表那处注释 ——
            #   图标 PNG 自己四周留了 9% 白边，这里不能再缩太多）。
            ico_px = max(16, int(icon_box * 0.96))
            photo = get_file_icon(row["name"], is_dir, ico_px)
            if photo is not None:
                c.create_image(cx_center, icon_top + icon_box // 2,
                               image=photo, anchor="center")
            else:
                emoji = icon_for_file(row["name"], is_dir)
                fs = max(12, int(icon_box * 0.7))
                if dark_mode_now():
                    emoji = icon_for_file_dark(row["name"], is_dir, emoji)
                    c.create_text(cx_center, icon_top + icon_box // 2,
                                  text=emoji, font=(FONT, fs),
                                  anchor="center", fill=_themes_now()["fg"])
                else:
                    c.create_text(cx_center, icon_top + icon_box // 2,
                                  text=emoji, font=("Segoe UI Emoji", fs),
                                  anchor="center")

        max_w = (x1 - x0) - 12
        line_h = self.font.metrics("linespace")
        name_y = icon_top + icon_box + 6
        for j, ln in enumerate(item.get("name_lines") or []):
            c.create_text(cx_center, name_y + j * line_h + line_h // 2,
                          text=ln, anchor="center",
                          font=self.font, fill=theme_get("fg"))
        name_block_h = len(item.get("name_lines") or []) * line_h

        pad_x = self._tag_pad_x()
        pill_hh = self._tag_pill_half_h()
        pill_h = pill_hh * 2
        tag_line_h = max(pill_h + 6, self.font_tag.metrics("linespace") + 6)

        tag_lines = item.get("tag_lines") or []
        # ★ 卡片最多画 GRID_MAX_TAG_LINES 行标签，画不下的用「＋N」提示，
        #   免得用户以为"标签没打上"。（被屏蔽的标签不算在内）
        vis_tags = [t for t in row["tags"] if t[0] not in self.hidden_tag_ids]
        drawn = sum(len(l) for l in tag_lines)
        more = max(0, len(vis_tags) - drawn)
        if tag_lines:
            tag_y_start = name_y + name_block_h + 4
            for li, line in enumerate(tag_lines):
                widths = []
                total_w = 0
                for (tname, _tcolor) in line:
                    tw = self.font_tag.measure(tname) + pad_x * 2
                    widths.append(tw)
                    total_w += tw + 4
                total_w -= 4
                tx = cx_center - total_w // 2
                ty = tag_y_start + li * tag_line_h + tag_line_h // 2
                for idx2, (tname, tcolor) in enumerate(line):
                    tw = widths[idx2]
                    label = tname
                    if (more and li == len(tag_lines) - 1
                            and idx2 == len(line) - 1):
                        # 用「＋N」占掉最后一个位置，提示还有 N 个标签
                        label = "＋%d" % more
                        tcolor = "#c3c7cc"
                    c.create_rectangle(tx, ty - pill_hh,
                                       tx + tw, ty + pill_hh,
                                       fill=tcolor, outline="")
                    fg = text_color_for(tcolor)
                    c.create_text(tx + tw // 2, ty, text=label,
                                  font=self.font_tag, fill=fg)
                    tx += tw + 4

    def _row_at_canvas(self, cx, cy):
        # ★ v25 补丁37：列表模式下的**列**判定要宽容一点。
        #   以前要求 cx 落在「左边白条之后、最后一列之前」才认；一旦画布
        #   尺寸没量准（x 范围算小了），点哪儿都会被判成「空白」→
        #   单击永远选不中（用户报的正是这个）。现在只在**明显**超出时才
        #   当成空白，宁可多认几像素。
        for item in self._layout:
            if item["kind"] == "list":
                if item["y0"] <= cy < item["y1"]:
                    return item["idx"]
            else:
                if (item["x0"] <= cx <= item["x1"]
                        and item["y0"] <= cy <= item["y1"]):
                    return item["idx"]
        return None

    def _on_click(self, event):
        self.canvas.focus_set()
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        idx = self._row_at_canvas(cx, cy)
        # ★★ 2026-10-03 修正：**这一行是「单击选不中文件」的真正病根。**
        #   原来是 alt = (state & 0x0008) or (state & 0x20000)，
        #   可实测这台机器上「什么都没按」的时候 0x8 就是亮的
        #   （真正按 Alt 时是 0x20008）—— 于是**每一次正常单击都被当成
        #   「按住 Alt 拉框」**：单击不选中、只有真的拖一下（框选）才有反应。
        #   现在只认真正的 Alt 位（0x20000），再拿系统按键状态兜一道底。
        #   详见 _alt_down() 里的说明。
        alt = _alt_down(event.state)
        # ★★ v25 补丁41：**「单击选不中文件」在这里彻底解决。**
        #
        #   历史上这段代码反复出问题，根子在于一个错误的设计：
        #   「列表模式下，鼠标横向落在左右白条里 = 按在空白处」。
        #   可是在**列表**里，一条记录的归属完全由**纵向位置**决定 ——
        #   鼠标在这一行的 y 范围内，那点的一定是这一行，
        #   不管横向点在哪（资源管理器就是这样）。
        #   加了「横向白条也算空白」之后：窗口一宽、右边就多出一大片
        #   死区，在哪点都选不中 —— 用户抱怨了好几轮的正是这个。
        #
        #   现在改成：
        #     · 列表模式：**只看 y**，横向一律算「这一行」→ 一定能选中；
        #     · 想让「点空白清空选中 / 拉框」照旧好用，就靠**纵向**那条
        #       永远留在列表底下的空白带（_total_h 里留了 40 像素，
        #       见 _recompute_layout）。这才是正常软件的做法。
        #     · 只有明确按了 Alt 时，才把「文件上的按下」当成拉框起点。
        _ = alt  # 保留变量，下面还要用
        # 拉框判定：**纵向不在任何一行上**（= 列表下方/上方的空白）、
        # 或者按住 Alt → 拉框；按在某一行上（无 Alt）→ 走「选中 + 拖动」
        #   ★ 2026-10-03：再加一条 —— 用户选了「随处可拉」时，
        #     在文件上按下也当拉框起手（老手感）。
        start_box = bool(alt or (idx is None)
                         or getattr(self, "marquee_anywhere", False))
        if start_box:
            self._marq = {
                "x0": cx, "y0": cy, "x1": cx, "y1": cy,
                "ctrl": bool(event.state & 0x0004),
                "alt": alt,
                "base": set(self.selected_paths),
                "rect": None, "started": False,
                # ★ 记下「按在哪一行上」：万一这一下其实是想单击那一个文件
                #   （按了却没拖动），松手时按单击处理。
                "press_idx": idx,
            }
            self._file_drag = None
            self._dnd_drag_source(False)      # 拉框时先把「拖出去」临时关掉
            # ★ v25 补丁40：**在空白处点一下（没拖动）= 取消选中**。
            #   原来这里直接就 return 了，下面那段「点空白清空选中」的
            #   代码变成了**永远走不到的死代码** —— 于是框选一堆之后
            #   不知道该点哪儿才能取消，只能再去点个文件。
            #   现在：先记一个「这是空白处按下的」，等松手时如果
            #   **一动都没动**，就当成单击空白 → 清空选中；
            #   真拖了就是拉框，照旧。
            if idx is None and not alt:
                self._blank_click = True
            else:
                self._blank_click = False
            return
        self._marq = None
        self._blank_click = False
        ctrl = bool(event.state & 0x0004)
        shift = bool(event.state & 0x0001)
        path = self.rows[idx]["path"]
        # ★ v25 补丁37：**先把「按下之前那一批」记下来**，再改选中集合。
        #   顺序很关键：放后面的话，单击那一步已经把集合收成一个了，
        #   记下来的就只有 1 个 → 拖起来带不动整批
        #   （这就是「Ctrl 多选后拖动只动一个」的根源）。
        before_selected = set(self.selected_paths)
        if shift and self.last_clicked_path:
            paths = [r["path"] for r in self.rows]
            try:
                i_last = paths.index(self.last_clicked_path)
                i_now = paths.index(path)
                lo, hi = sorted((i_last, i_now))
                self.selected_paths = set(paths[lo:hi + 1])
            except ValueError:
                self.selected_paths = {path}
                self.last_clicked_path = path
        elif ctrl:
            if path in self.selected_paths:
                self.selected_paths.discard(path)
            else:
                self.selected_paths.add(path)
            self.last_clicked_path = path
        else:
            # ★ v25 补丁40：**「再点一下取消选中」这个行为删掉了。**
            #   用户反复说「没法单击选中文件，只能框选」—— 真正让他
            #   觉得「选不中」的就是这里：点一个已经选中的文件，选中
            #   会被**清空**。他点一下选中、再点一下（手抖、或者想确认
            #   一下）就没了，看起来就像「单击根本选不中」。
            #   资源管理器、绝大多数软件都不会这么干：单击 = 选中它，
            #   要取消就点空白处（空白处那条路还在）。
            self.selected_paths = {path}
            self.last_clicked_path = path
        self._recompute_layout()
        self._redraw()
        if self.on_select:
            self.on_select()
        # 记下「按下位置」，给「拖动到文件夹 = 移动」用
        #   ★ 补丁37：batch 用的是**改动之前**那一批（before_selected），
        #     不是现在这个（现在可能已经被收起成 1 个了）。
        src = list(self.selected_paths) or [path]
        self._file_drag = {
            "x0": cx, "y0": cy, "started": False,
            "path": path,          # ★ 补丁37：没拖动时收成「这一个」
            "batch": set(before_selected) or set(src),   # 拖动时整批走
            "paths": src, "target_row": None,
        }
        # ★ v25 补丁37：按下的那一刻如果**本来选了好几个**、这一下又没按
        #   Ctrl/Shift，那基本就是「想只选这一个」——先把选中收起来。
        #   为什么要在这里做：框选一批之后，如果两次点击挨得比较近，
        #   Tk 第二次按下会当成「双击」而**不发普通的 ButtonRelease**，
        #   于是「松手时收起」那一步收不到。放在按下时做就绕开了这个问题。
        #   （真拖动不受影响：一开始拖就把 batch 恢复回来。）
        if (not ctrl and not shift and len(before_selected) > 1
                and path in before_selected
                and len(self.selected_paths) > 1):
            self.selected_paths = {path}
            try:
                self._recompute_layout()
                self._redraw()
            except Exception:
                pass
            try:
                note = getattr(self, "on_log_action", None)
                if note:
                    note("单击：把选中收成「%s」" % os.path.basename(str(path)))
            except Exception:
                pass

    # ---------------- ★ v25 补丁21：临时开关「把文件拖出去」 ----------------

    def _dnd_drag_source(self, on):
        """把文件列表的「拖到资源管理器」拖放源打开 / 关掉。

        为什么需要它：装了 tkinterdnd2 之后，**在文件上按住拖动会被它接管**
        （它会把鼠标抓走），我们自己写的拉框就再也收不到动作 —— 这就是
        「按住 Alt 拉框一次也没成功」的真正原因。
        所以：要拉框之前先把它关掉，松手再打开。
        """
        try:
            types_ = globals().get("DND_FILES")
            if types_ is None:
                return
            if on:
                self.canvas.drag_source_register(1, types_)
            else:
                self.canvas.drag_source_unregister()
        except Exception:
            pass

    # ---------------- ★ v25 补丁18：鼠标拉方框（框选）多选 ----------------

    def _marquee_move(self, event):
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        m = getattr(self, "_marq", None)
        if m:
            m["x1"], m["y1"] = cx, cy
            if not m["started"]:
                if abs(cx - m["x0"]) < 4 and abs(cy - m["y0"]) < 4:
                    return
                m["started"] = True
            self._marquee_apply()
            return
        fd = getattr(self, "_file_drag", None)
        if not fd:
            return
        if not fd["started"]:
            if abs(cx - fd["x0"]) < 5 and abs(cy - fd["y0"]) < 5:
                return
            fd["started"] = True
            self._dnd_drag_source(False)     # 内部拖动时先关掉「拖出去」
            # ★ 2026-10-03：一开始拖就给出提示（原来只在「从一个文件夹上
            #   移开」的时候才给，等于第一次拖的时候屏幕上什么都没有）。
            self._drop_hint = "拖到文件夹上松手 = 移动进去"
            # ★ v25 补丁37：真的开始拖了 → 把「按住之前那一批」恢复回来，
            #   整批一起拖（和资源管理器一致）。
            #   （按下时为了让「单击只选一个」把选中收起来了，这里补回来。）
            try:
                restore = fd.get("batch") or set()
                if len(restore) > 1 and not set(
                        self.selected_paths) >= restore:
                    self.selected_paths |= set(restore)
                    fd["paths"] = list(self.selected_paths)
                    self._recompute_layout()
                    self._redraw()
            except Exception:
                pass
        tgt = None
        idx = self._row_at_canvas(cx, cy)
        if idx is not None and 0 <= idx < len(self.rows):
            r = self.rows[idx]
            if r.get("kind") == "文件夹" and r["path"] not in fd["paths"]:
                tgt = r["path"]
        if tgt != fd.get("target_row"):
            fd["target_row"] = tgt
            if tgt:
                self._drop_hint = "松手 = 把 %d 项移动到「%s」" % (
                    len(fd["paths"]),
                    os.path.basename(str(tgt).rstrip("\\")) or tgt)
            else:
                self._drop_hint = "拖到文件夹上松手 = 移动进去"
            try:
                self._redraw()
            except Exception:
                pass

    def _marquee_end(self, event):
        m = getattr(self, "_marq", None)
        self._marq = None
        fd = getattr(self, "_file_drag", None)
        self._file_drag = None
        if getattr(self, "_drop_hint", None):
            self._drop_hint = None
            try:
                self._redraw()
            except Exception:
                pass
        if m:
            self._dnd_drag_source(True)
            try:
                if m.get("rect") is not None:
                    self.canvas.delete(m["rect"])
            except Exception:
                pass
            if m.get("started"):
                # ★★ v26：记下「刚框选完」的时间。
                #   接下来 0.3 秒内如果 Tk 把下一下合并成双击，
                #   就按单击处理（详见 __init__ 里的说明）。
                self._just_marqueed_ts = time.time()
                self._marquee_apply(keep_rect=False)
            elif m.get("press_idx") is not None:
                # ★★ 2026-10-03 新增：按下的时候**确实点在某个文件上**、
                #   但到松手为止一动都没动 —— 这就是「单击选中它」。
                #   （「随处可拉」模式下按下就先起了个拉框，走到这里；
                #     不补这一段的话，点文件会像没点一样。）
                _i = m.get("press_idx")
                try:
                    if 0 <= int(_i) < len(self.rows):
                        _p = self.rows[int(_i)]["path"]
                        if m.get("ctrl"):
                            if _p in self.selected_paths:
                                self.selected_paths.discard(_p)
                            else:
                                self.selected_paths.add(_p)
                        else:
                            self.selected_paths = {_p}
                        self.last_clicked_path = _p
                        self._recompute_layout()
                        self._redraw()
                        if self.on_select:
                            self.on_select()
                except Exception as _e:
                    note_swallowed(T("单击某一行（补选中）失败"), _e)
            else:
                # ★ v25 补丁40：在空白处**按一下没动 = 单击空白 = 取消选中**。
                #   （以前这段逻辑在 _on_click 里，因为提前 return 变成了
                #     死代码，所以「框选完不知道该点哪取消选中」。）
                if getattr(self, "_blank_click", False) and not m.get("ctrl"):
                    self.selected_paths.clear()
                    self.last_clicked_path = None
                    try:
                        self._recompute_layout()
                        self._redraw()
                    except Exception:
                        pass
                    try:
                        if self.on_select:
                            self.on_select()
                    except Exception:
                        pass
            self._blank_click = False
            return
        if fd:
            self._dnd_drag_source(True)
            # ★ v25 补丁37：松手时人已经在窗口外面 = 「拖出去」，不是「拖进
            #   某个文件夹」，直接收工（让系统按拖出去处理）。
            try:
                if fd.get("started") and not fd.get("target_row") \
                        and self._pointer_left_canvas():
                    return
            except Exception:
                pass
            if fd.get("started") and fd.get("target_row"):
                cb = getattr(self, "on_move_to_folder", None)
                if cb:
                    paths = [p for p in fd["paths"]
                             if p != fd["target_row"]]
                    if paths:
                        try:
                            cb(paths, fd["target_row"])
                        except Exception as _e:
                            try:
                                note_swallowed(T("拖动移动到文件夹失败"), _e)
                            except Exception:
                                pass
                return
            # ★ v25 补丁37：**按下到松手基本没动 = 其实就是点了一下**。
            #   框选了一批之后再单个点一下某个文件，应该像资源管理器那样
            #   「只剩这一个被选中」。以前为了让「拖动带走整批」把这一步
            #   跳过了 —— 用户反馈「框选后单击并不能切换成单个文件被选中」。
            #   现在按「真的拖了没有」判断（超过 5 像素才算拖）；
            #   另外按下时如果**已经选了好几个**，同时**没按 Ctrl/Shift**，
            #   这一下也当成「点了一下」直接收起来 —— 这样即使 Tk 因为
            #   双击判定没把 Release 送到，也照样能收。
            try:
                cx = self.canvas.canvasx(event.x)
                cy = self.canvas.canvasy(event.y)
            except Exception:
                cx = cy = 0
            try:
                moved = max(abs(cx - fd.get("x0", cx)),
                            abs(cy - fd.get("y0", cy)))
            except Exception:
                moved = 0
            if not fd.get("started") or moved < 5:
                one = fd.get("path")
                before_n = len(self.selected_paths)
                # ★★ v26：**这里以前是「不管变没变都重排 + 重画一遍」。**
                #   而 `_on_click`（按下的那一下）**已经刷过一次**了 ——
                #   等于一次点击把整页文件排了两遍、画了两遍。
                #   800 行的列表上，这一下就是白白多花一倍的力气。
                #   现在：选中集合**真的变了**才刷。
                _changed = (set(self.selected_paths) != ({one} if one else set()))
                if one:
                    self.selected_paths = {one}
                    self.last_clicked_path = one
                try:
                    note = getattr(self, "on_log_action", None)
                    if note and before_n > 1:
                        note("框选后单击：把选中从 %d 项收成「%s」"
                             "（鼠标移动了 %.0f 像素）"
                             % (before_n, os.path.basename(str(one or "")),
                                moved))
                except Exception:
                    pass
                if _changed:
                    try:
                        self._recompute_layout()
                        self._redraw()
                    except Exception:
                        pass
                    if self.on_select:
                        try:
                            self.on_select()
                        except Exception:
                            pass

    def _pointer_left_canvas(self):
        """★ 补丁37：松手时鼠标是不是已经在画布外面了。"""
        try:
            px, py = self.canvas.winfo_pointerxy()
            x0 = self.canvas.winfo_rootx()
            y0 = self.canvas.winfo_rooty()
            return not (x0 <= px <= x0 + self.canvas.winfo_width()
                        and y0 <= py <= y0 + self.canvas.winfo_height())
        except Exception:
            return False

    def _marquee_rect(self):
        m = self._marq
        x0, y0 = min(m["x0"], m["x1"]), min(m["y0"], m["y1"])
        x1, y1 = max(m["x0"], m["x1"]), max(m["y0"], m["y1"])
        return x0, y0, x1, y1

    def _marquee_hits(self):
        """框住的文件路径（列表模式和瀑布流模式都能框）。"""
        x0, y0, x1, y1 = self._marquee_rect()
        hit = set()
        for item in self._layout:
            try:
                if item["kind"] == "list":
                    if item["y1"] > y0 and item["y0"] < y1:
                        hit.add(self.rows[item["idx"]]["path"])
                else:
                    if (item["x1"] > x0 and item["x0"] < x1
                            and item["y1"] > y0 and item["y0"] < y1):
                        hit.add(self.rows[item["idx"]]["path"])
            except Exception:
                continue
        return hit

    def _marquee_apply(self, keep_rect=True):
        m = getattr(self, "_marq", None)
        if not m:
            return
        hit = self._marquee_hits()
        sel = (set(m.get("base") or ()) | hit) if m.get("ctrl") else set(hit)
        x0, y0, x1, y1 = self._marquee_rect()
        if sel != self.selected_paths:
            self.selected_paths = sel
            if hit:
                try:
                    self.last_clicked_path = sorted(hit)[-1]
                except Exception:
                    pass
            # ★ _redraw() 会把画布清空（虚线框也会没），所以先丢掉旧的框 id，
            #   重画之后再补一个新的。
            m["rect"] = None
            self._recompute_layout()
            self._redraw()
            if self.on_select:
                self.on_select()
        if keep_rect and m.get("started"):
            try:
                if m.get("rect") is None:
                    m["rect"] = self.canvas.create_rectangle(
                        x0, y0, x1, y1, outline="#3b7ddd", width=1,
                        dash=(4, 3))
                else:
                    self.canvas.coords(m["rect"], x0, y0, x1, y1)
                self.canvas.tag_raise(m["rect"])
            except Exception:
                m["rect"] = None

    def _on_double_click(self, event):
        """双击：打开文件 / 进文件夹。

        ★ v25 补丁40：**先补一次「选中」**，再做双击该做的事。
        为什么：Tk 有个特性 —— 鼠标在同一处快速点第二下时，它只发
        `<Double-1>`，**不再发第二个 `<Button-1>`**。原来这里没有兜底，
        于是「点一下选中 → 再点一下（想确认或手快）→ 选中反而没了/没变化」，
        用户看起来就是「单击根本选不中文件」。
        现在双击也先把这一行选上（和资源管理器一样：双击时它也是选中的），
        再去打开。这样无论 Tk 怎么合并事件，选中的结果都是对的。
        """
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        idx = self._row_at_canvas(cx, cy)
        if idx is None:
            return
        row = self.rows[idx]
        # ★★ v26（2026-10-01）：「框选完马上单击」的修正。
        #
        #   Tk 判双击是看「两次按下的间隔 + 距离」的。
        #   框选的时候鼠标一路拖，松手的位置很可能离
        #   上一次单击很近 —— 于是紧接着的那一次点击会被
        #   Tk 当成 <Double-1>。而这个函数原来是“先把选中收成一个、
        #   再去打开文件” —— 用户只是想选中，结果文件被打开了，
        #   或者选中被反复收起变得很反常。
        #
        #   修法：框选刚结束的短瞭窗口期内，这一下**只当单击**：
        #   只把这一行选中，绝不打开文件。
        #   （真想打开的话，再点一下就行 —— 当时已经出了窗口期）。
        try:
            if (time.time() - float(getattr(self, "_just_marqueed_ts", 0.0))
                    < float(getattr(self, "MARQUEE_CLICK_GRACE", 0.3))):
                p0 = row["path"]
                if self.selected_paths != {p0}:
                    self.selected_paths = {p0}
                    self.last_clicked_path = p0
                    self._recompute_layout()
                    self._redraw()
                    if self.on_select:
                        self.on_select()
                return
        except Exception as _e:
            try:
                note_swallowed(T("框选后的点击窗口期判定失败"), _e)
            except Exception:
                pass
        # 补上「选中」这一步（双击时 Tk 没发 Button-1，这里替它做）
        try:
            p = row["path"]
            if self.selected_paths != {p}:
                self.selected_paths = {p}
                self.last_clicked_path = p
                self._recompute_layout()
                self._redraw()
                if self.on_select:
                    self.on_select()
        except Exception:
            pass
        if self.on_double:
            self.on_double(row["path"], row["kind"] == "文件夹")

    def _on_right(self, event):
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        idx = self._row_at_canvas(cx, cy)
        # ★★★ 2026-10-07 **修「空文件夹里右键没反应」**（用户报，待清算 #5）★★★
        #   ★ 真因：原来这里写
        #       idx = self._row_at_canvas(...)
        #       if idx is None:
        #           return            # ← ★ 空白处直接返回，菜单永远不出来
        #     → 于是**空文件夹**（一行都没有）里右键 = 完全没反应；
        #       文件少、下面一大片空白时，在空白处右键也没反应。
        #   ★ 修法：**空白处不再 return** —— 走「空白处右键」这一路：
        #       · 不改变当前选中（用户没点中文件，就别动他的选择）
        #       · 调 `on_right_click(event, None)` —— 让主程序弹"空白处菜单"
        #         （新建文件夹 / 粘贴 / 刷新 / 在资源管理器打开 …）
        #   ★ 判据：`idx is None` = 点在空白处（不是点在某一行的缝隙里，
        #     那由 `_row_at_canvas` 自己判断）。
        if idx is None:
            try:
                # ★ 数据行数也要带上 —— 主程序靠它决定"粘贴/新建"能不能点
                blank_ctx = {
                    "count": len(getattr(self, "rows", []) or []),
                    "dir": getattr(self, "current_dir", None),
                }
            except Exception:
                blank_ctx = {}
            try:
                if getattr(self, "on_right_click_blank", None):
                    self.on_right_click_blank(event, blank_ctx)
                elif self.on_right_click:
                    # ★ 兜底：没注入"空白处"回调时，也把 None 传过去 ——
                    #   主程序那边会识别出"path 是 None"并弹空白菜单。
                    self.on_right_click(event, None)
            except Exception as _e:
                try:
                    note_swallowed(T("空白处右键菜单失败"), _e, quiet=True)
                except Exception:
                    pass
            return
        path = self.rows[idx]["path"]
        if path not in self.selected_paths:
            self.selected_paths = {path}
            self.last_clicked_path = path
            self._recompute_layout()
            self._redraw()
            if self.on_select:
                self.on_select()
        if self.on_right_click:
            self.on_right_click(event, path)

    def _on_wheel(self, event):
        if event.num == 4:
            d = -3
        elif event.num == 5:
            d = 3
        else:
            d = -3 if event.delta > 0 else 3
        self.canvas.yview_scroll(d, "units")
        self._redraw()

    def _on_scroll_y(self, *args):
        self.canvas.yview(*args)
        self._redraw()

    def _on_scroll_x(self, *args):
        self.canvas.xview(*args)
        self._redraw()

    def _on_key_up(self, event):
        self._move_sel_list(-1)

    def _on_key_down(self, event):
        self._move_sel_list(1)

    def _on_key_left(self, event):
        if self.layout_mode == "grid":
            self._move_sel_list(-1)

    def _on_key_right(self, event):
        if self.layout_mode == "grid":
            self._move_sel_list(1)

    def _on_key_home(self, event):
        if self.rows:
            self._set_single(self.rows[0]["path"])

    def _on_key_end(self, event):
        if self.rows:
            self._set_single(self.rows[-1]["path"])

    def _move_sel_list(self, delta):
        if not self.rows:
            return
        paths = [r["path"] for r in self.rows]
        cur = self.last_clicked_path or next(iter(self.selected_paths), None)
        if cur is None:
            new_path = paths[0]
        else:
            try:
                i = paths.index(cur)
            except ValueError:
                i = 0
            i = max(0, min(len(paths) - 1, i + delta))
            new_path = paths[i]
        self._set_single(new_path)

    def _set_single(self, path):
        self.selected_paths = {path}
        self.last_clicked_path = path
        self._recompute_layout()
        self._scroll_to(path)
        self._redraw()
        if self.on_select:
            self.on_select()

    def _scroll_to(self, path):
        for item in self._layout:
            i = item["idx"]
            if self.rows[i]["path"] == path:
                y0 = item["y0"]
                y1 = item["y1"]
                canvas_h = self.canvas.winfo_height() or 400
                top = self.canvas.canvasy(0)
                total_h = max(1, self._total_h)
                if y0 < top:
                    self.canvas.yview_moveto(y0 / total_h)
                elif y1 > top + canvas_h:
                    self.canvas.yview_moveto((y1 - canvas_h) / total_h)
                return

    def get_selection(self):
        return [r["path"] for r in self.rows if r["path"] in self.selected_paths]

    def get_single_selection(self):
        sel = self.get_selection()
        return sel[0] if len(sel) == 1 else None

    def select_all_rows(self):
        """★ v25 补丁9：全选当前列表（Ctrl+A 用）。

        （原来有个 select_all()，v25 补丁3 清死代码时删掉了 —— 那时确实
          没有任何地方调用它；现在做 Ctrl+A，重新以新名字加回来。）
        """
        self.selected_paths = {r["path"] for r in self.rows}
        try:
            self._recompute_layout()
            self._redraw()
        except Exception as _e:
            note_swallowed(T("全选后重画列表失败"), _e)
        if self.on_select:
            try:
                self.on_select()
            except Exception:
                pass

    def clear_selection(self):
        """★ v25 补丁9：清空选择（点空白处用）。"""
        self.selected_paths = set()
        try:
            self._recompute_layout()
            self._redraw()
        except Exception:
            pass
        if self.on_select:
            try:
                self.on_select()
            except Exception:
                pass

    def get_path_at_y(self, y_root, x_root=None):
        try:
            canvas_top = self.canvas.winfo_rooty()
            canvas_left = self.canvas.winfo_rootx()
            cy_local = y_root - canvas_top
            cy = self.canvas.canvasy(cy_local)
            if x_root is not None:
                cx_local = x_root - canvas_left
            else:
                cx_local = 0
            cx = self.canvas.canvasx(cx_local)
            idx = self._row_at_canvas(cx, cy)
            if idx is not None:
                return self.rows[idx]["path"]
        except Exception:
            pass
        return None



# ---------- 兜底（★ 它会吃掉错误，所以要专门测"用的哪一份"）----------
def _fallback():
    g = globals()
    for _n in _NEED:
        if g.get(_n) is None:
            g[_n] = _Borrowed(_n)


_fallback()
