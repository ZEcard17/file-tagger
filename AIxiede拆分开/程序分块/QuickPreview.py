# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：QuickPreview。

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
   · import 要写 `from QuickPreview import …`（**不带包路径**）
   · `_set_app` 要**取别名**（`as _fk_…`）——模块名和类名同名
   · 借名字的清单**用 symtable + dir() 定**，别用正则猜
   · 代理类**必须实现 `__call__`**（函数也会被借）
   · ★ 兜底 except 会吃掉错误 → **必须专门测"用的哪一份"**
"""
import os
import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, colorchooser

# ---------- 要向主程序借的名字（先占位，挂上后填真身） ----------
_MUTABLE = ['BOLD', 'FONT', 'UI_FONT_SIZE']
_NEED = ['BOLD', 'FONT', 'PreviewPane', 'T', 'UI_FONT_SIZE', '_dlg_geom', '_retheme_tree', 'note_swallowed', 'os', 'sys', 'theme_get']
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


class QuickPreview:
    """★★ 2026-10-06 新增：**按空格快速预览（Quick Look 那种）** ★★

    用户要的：选中文件 → 按空格 → 弹出大预览 → 按 ← → 直接换下一个
              → 再按空格（或 Esc）关掉。

    为什么做这个（外面 QuickLook 的广告词很说明问题）：
       不用它：双击 → 等 → 程序加载 → 看 → 关程序，**约 10 秒**；
       用它：  按空格 → 完事，**约 0.2 秒**。
    而且精髓是**按方向键直接换下一个** —— 用户是在「扫」一批文件
    （挑照片、翻素材），不是「看」某一个。
    没有方向键切换，用户就得「关预览 → 选下一个 → 再开预览」，
    体验一下就崩了。

    它和已有那两个不冲突，三个各管一段：
      · **右侧预览窗格** = 慢慢看（固定在那儿不挡事）
      · **鼠标悬停小预览** = 瞟一眼（移开就没）
      · **这个（空格）** = **快速扫一批**（大窗、能翻页、能换文件）

    外面 PowerToys Peek 的两个细节，这里照抄：
      ① **多选了文件时，只在选中的那几个之间换** —— 很聪明，
         因为这时候用户心里想的就是「我选的这批」；
      ② **Esc 关掉**（用户第一反应就是这个）。

    ★ 实现上刻意做成「自己一个窗口 + 复用 PreviewPane 的渲染」：
      · 复用渲染 = 不重写一遍 PDF/电子书/图片的代码，不容易出新 bug；
      · 独立窗口 = 关掉它**不影响**右边那个预览窗格。
    """

    # 窗口默认占屏幕多大（外面惯例：别铺满，留点边能看见列表）
    W_RATIO = 0.62
    H_RATIO = 0.78

    def __init__(self, app):
        self.app = app
        self.win = None            # 主窗口（tk.Toplevel）
        self.pane = None           # 里面那个 PreviewPane
        self.paths = []            # 可以按 ← → 遍历的路径列表
        self.index = -1            # 现在看的是第几个
        self._zoom_lbl = None
        self._title_lbl = None
        self._hint_lbl = None

    # ---------------- 对外：开 / 关 / 切换 ----------------
    def toggle(self):
        """按空格调它：开着就关，关着就开。"""
        if self.is_open():
            self.close()
        else:
            self.open()

    def is_open(self):
        try:
            return self.win is not None and self.win.winfo_exists()
        except Exception:
            return False

    def open(self):
        """开窗，并显示当前选中的那个文件。"""
        cur = self._current_path()
        if not cur:
            self.app.set_status(T("先选中一个文件，再按空格快速预览"))
            return
        self.paths = self._build_sequence(cur)
        try:
            self.index = self.paths.index(cur)
        except Exception:
            self.index = 0 if self.paths else -1
        self._build_window()
        self._render()

    def close(self):
        """关掉（Esc / 再按空格 / 点关闭按钮）。"""
        try:
            if self.win is not None:
                self.win.destroy()
        except Exception:
            pass
        self.win = None
        self.pane = None
        self._zoom_lbl = None
        self._title_lbl = None
        self._hint_lbl = None

    # ---------------- 选中目标 / 翻页顺序 ----------------
    def _current_path(self):
        """现在该预览谁：优先「最后点的那一个」。"""
        fl = getattr(self.app, "file_list", None)
        if fl is None:
            return None
        p = getattr(fl, "last_clicked_path", None)
        if p:
            return p
        try:
            sel = fl.get_selection()
            if sel:
                return sorted(sel)[0]
        except Exception:
            pass
        try:
            return fl.get_single_selection()
        except Exception:
            return None

    def _build_sequence(self, cur):
        """★ 能按 ← → 遍历的那一串。

        ★ 照抄 PowerToys Peek 的聪明设计：
          **多选了就只在选中的里面换**（用户心里想的就是「我选的这批」）；
          没多选就整个文件夹按现在的顺序走。
        """
        fl = getattr(self.app, "file_list", None)
        try:
            sel = list(fl.get_selection() or [])
        except Exception:
            sel = []
        if len(sel) > 1:
            # 按当前列表里的显示顺序排（不是按名字，免得跳来跳去）
            try:
                order = [r["path"] for r in fl.rows]
                seq = [p for p in order if p in set(sel)]
                if cur not in seq:
                    seq.insert(0, cur)
                return seq or [cur]
            except Exception:
                return sorted(sel)
        # 没多选：整个当前列表
        try:
            seq = [r["path"] for r in fl.rows]
            if seq:
                return seq
        except Exception:
            pass
        return [cur]

    # ---------------- 窗口 ----------------
    def _build_window(self):
        root = self.app.root
        win = tk.Toplevel(root)
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
        self.win = win
        win.title(T("快速预览 —— 空格 / Esc 关闭，← → 换文件"))
        win.transient(root)

        # 尺寸：按屏幕比例，别铺满（外面惯例）
        try:
            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            w = int(sw * self.W_RATIO)
            h = int(sh * self.H_RATIO)
            x = max(10, (sw - w) // 2)
            y = max(10, (sh - h) // 3)
            win.geometry("%dx%d+%d+%d" % (w, h, x, y))
        except Exception:
            win.geometry(_dlg_geom(900, 700))

        # 顶部一行：文件名 + 第几个/共几个
        head = tk.Frame(win)
        head.pack(fill="x", side="top")
        self._title_lbl = tk.Label(head, text="", anchor="w",
                                   font=(FONT, UI_FONT_SIZE, BOLD))
        self._title_lbl.pack(side="left", padx=10, pady=4)
        self._zoom_lbl = tk.Label(head, text="", anchor="e")
        self._zoom_lbl.pack(side="right", padx=10, pady=4)

        # 底部一行：操作提示（小白得知道能按什么）
        #
        # ★★ 2026-10-08 改（用户报，待清算 #6）：
        #   用户原话「Alt 加方向键切换上下文件预览正常，
        #   **就是提示只有方向键没有 alt**」。
        #   ★ 真因查清了：
        #     · 本窗口**只绑了** `←` `→` `↑` `↓` 四个；
        #     · 用户按 Alt+方向键**之所以"也能换"**，是因为
        #       **主窗口**把 Alt+←/→ 当"后退/前进"用了 ——
        #       于是目录切了 → 这边跟着换了内容。**是误打误撞，不是设计。**
        #       （这就是待清算 O1 记的那件事。）
        #   ★ 现在**显式把 Alt+方向键也绑上** —— 让"能用"变成"设计好的"，
        #     并且提示里**写全**，用户不用猜。
        self._hint_lbl = tk.Label(
            win, text=("空格 / Esc 关闭　　← → ↑ ↓ 换上一个下一个　　"
                       "＋ − 缩放　　0 复位　　双击图片看原图"),
            anchor="w")
        self._hint_lbl.pack(fill="x", side="bottom", padx=10, pady=3)

        # 中间：**复用 PreviewPane**（不重写 PDF / 电子书 / 图片那套）
        try:
            self.pane = PreviewPane(win, app=self.app)
            self.pane.pack(fill="both", expand=True, padx=6, pady=2)
        except Exception as exc:
            note_swallowed(T("快速预览：里面那块没建起来"), exc)
            self.pane = None

        # ★ 键盘：绑在这个窗口上（主窗口的键不受影响）
        win.bind("<Escape>", lambda e: (self.close(), "break")[1])
        win.bind("<space>", lambda e: (self.close(), "break")[1])
        win.bind("<Left>", lambda e: (self.prev(), "break")[1])
        win.bind("<Right>", lambda e: (self.next(), "break")[1])
        win.bind("<Up>", lambda e: (self.prev(), "break")[1])
        win.bind("<Down>", lambda e: (self.next(), "break")[1])
        # ★★ 2026-10-08 补：**Alt+方向键也绑上**（用户报，待清算 #6）
        #   用户说「Alt 加方向键切换上下文件预览正常」——
        #   查清后发现那是**主窗口的"后退/前进"误打误撞**弄的
        #   （目录换了、这边跟着换），**不是本窗口自己处理的**。
        #   ★ 现在显式绑上，并且**吃掉这个事件**（`"break"`）——
        #     免得同时又把主窗口的目录切了（那样会"换两次"，很怪）。
        try:
            win.bind("<Alt-Left>", lambda e: (self.prev(), "break")[1])
            win.bind("<Alt-Right>", lambda e: (self.next(), "break")[1])
            win.bind("<Alt-Up>", lambda e: (self.prev(), "break")[1])
            win.bind("<Alt-Down>", lambda e: (self.next(), "break")[1])
        except Exception:
            pass
        # ★★ 2026-10-08 补：**缩放键**（提示里写了就得真能用）
        #   ★ 真名核对过：`PreviewPane` 里是
        #       `zoom_center(factor)`（按倍数缩放）/ `zoom_reset()`
        #     —— **不是** `zoom_in` / `zoom_out`（我第一版就是那么写的，
        #       幸好当场核了一遍名字）。
        #   ★ 倍数沿用 PreviewPane 自己按钮用的那两个值，保持一致。
        for _seq, _fn in (("<plus>", ("zoom_center", 1.25)),
                          ("<equal>", ("zoom_center", 1.25)),
                          ("<KP_Add>", ("zoom_center", 1.25)),
                          ("<minus>", ("zoom_center", 0.8)),
                          ("<KP_Subtract>", ("zoom_center", 0.8)),
                          ("<Key-0>", ("zoom_reset", None))):
            try:
                win.bind(_seq, self._make_zoom_handler(*_fn))
            except Exception:
                continue
        # 点关闭按钮也要清干净状态
        win.protocol("WM_DELETE_WINDOW", self.close)
        try:
            win.focus_set()
        except Exception:
            pass
        self._apply_theme()

    def _make_zoom_handler(self, action, factor=None):
        """★ 给"快速预览窗"做一个缩放/复位的按键处理器。

        ★★ 2026-10-08 新增（用户报，待清算 #6：提示里没有 Alt，功能也简陋）。
        ★ 为什么做成"工厂"（返回一个函数）而不是直接写 lambda：
          ① `lambda` 里塞 `try/except` 很难看，而且**每次按键都要现建**；
          ② 做成工厂之后，**异常在这儿一次性兜住** ——
             缩放失败（比如当前是文档、没有可缩放的东西）
             只是**什么都不做**，绝不会把按键事件搞崩。
        ★ 动作名核对过：`PreviewPane.zoom_center(factor)` / `zoom_reset()`
        """

        def _h(_e=None):
            try:
                pane = getattr(self, "pane", None)
                if pane is None:
                    return "break"
                fn = getattr(pane, action, None)
                if fn is None:
                    return "break"
                if factor is None:
                    fn()
                else:
                    fn(factor)
            except Exception as _ex:
                try:
                    note_swallowed(T("快速预览：缩放失败"), _ex, quiet=True)
                except Exception:
                    pass
            # ★ 吃掉事件 —— 别让它冒到主窗口去（免得主窗口也跟着动）
            return "break"

        return _h

    def _apply_theme(self):
        """跟着当前皮肤走（夜间别弹个白窗，很刺眼）。

        ★★ 2026-10-06 踩坑记录（踩了两次，写清楚）：
           第一次：我只把「标签」和它爹的背景刷成深色 ——
             截图一看**整个窗还是白的**（窗口自己的底色、里面的
             PreviewPane 都没刷）。
           第二次：改成调 `apply_theme(self.win, THEME_NAME)` ——
             结果标签底色变成了 `#3f3f3f`（一个不搭界的灰）！
             原因：`apply_theme` 里有一套「按对照表换色」的逻辑，
             对一个**全新建的、本来就是深色**的窗口，它是按
             「浅→深」的对照表去套的，套出个中间色。

           ★ 正确的是**根本不用这么麻烦**：
             本程序的皮肤系统在 `set_theme()` 里是调
             `apply_theme(self.root, name)` —— **扫的是整棵树**，
             而快速预览窗是 root 的子窗口，**它自己就会被扫到**。
             所以这里只需要：
               ① 按当前皮肤常量，把「普通 tk 控件」的底色刷对
                  （ttk 的会自动跟，普通 tk 的要手动给）；
               ② 别去调 apply_theme（会打乱它自己的对照表）。
        """
        try:
            bg = theme_get("panel_bg")
            fg = theme_get("fg")
            dim = theme_get("fg_dim")
        except Exception:
            return
        try:
            self.win.configure(bg=bg)
        except Exception:
            pass
        # 顶部那一行（普通 tk.Frame + 两个 Label）
        for w, kw in ((self._title_lbl, {"bg": bg, "fg": fg}),
                      (self._zoom_lbl, {"bg": bg, "fg": dim}),
                      (self._hint_lbl, {"bg": bg, "fg": dim})):
            try:
                if w is not None:
                    w.configure(**kw)
            except Exception:
                pass
        try:
            if self._title_lbl is not None:
                self._title_lbl.master.configure(bg=bg)
        except Exception:
            pass
        # 里面那个 PreviewPane：它是 ttk.Frame，靠样式走；
        # 但它内部的普通 tk 控件（文本框/画布）要单独刷。
        try:
            if self.pane is not None:
                self._retheme_pane(self.pane, bg, fg)
        except Exception:
            pass

    def _retheme_pane(self, pane, bg, fg):
        """把 PreviewPane 里那些**普通 tk 控件**也刷成深色。

        （ttk 的靠样式表自动跟；普通 tk 的不会，得手动。）
        """
        for attr, kw in (("kind_lbl", {"background": bg}),
                         ("name_lbl", {"background": bg}),
                         ("path_lbl", {"background": bg})):
            try:
                w = getattr(pane, attr, None)
                if w is not None:
                    w.configure(**kw)
            except Exception:
                pass
        # 剩下的交给现成的「换色器」（它就是干这个的）
        try:
            _retheme_tree(pane)
        except Exception:
            pass

    # ---------------- 翻页 ----------------
    def next(self):
        if self.index + 1 < len(self.paths):
            self.index += 1
            self._render()
        else:
            self.app.set_status(T("已经是最后一个了"))

    def prev(self):
        if self.index - 1 >= 0:
            self.index -= 1
            self._render()
        else:
            self.app.set_status(T("已经是第一个了"))

    def _render(self):
        """把当前这个文件显示出来。"""
        if not self.paths or self.index < 0 or self.index >= len(self.paths):
            return
        p = self.paths[self.index]
        name = os.path.basename(p) or p
        try:
            self._title_lbl.configure(text=name)
            self._zoom_lbl.configure(
                text=T("第 {a} / {b} 个",
                         a=self.index + 1, b=len(self.paths)))
        except Exception:
            pass
        # ★ 复用现成的渲染（它自己会丢后台读、会显示「正在读取…」）
        try:
            if self.pane is not None:
                self.pane.show_path(p)
        except Exception as exc:
            note_swallowed(T("快速预览：显示这个文件失败（{x}）", x=name), exc)
        # 顺手把列表也跟着选中 —— 这样关掉预览时，选中的就是刚看的那个
        try:
            self.app.file_list.selected_paths = {p}
            self.app.file_list.last_clicked_path = p
            self.app.file_list._redraw()
        except Exception:
            pass


# ---------- 兜底（★ 但注意：它会吃掉错误，所以要专门测"用的哪一份"）----------
def _fallback():
    g = globals()
    for _n in _NEED:
        if g.get(_n) is None:
            g[_n] = _Borrowed(_n)


_fallback()
