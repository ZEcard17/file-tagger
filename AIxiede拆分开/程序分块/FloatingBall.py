# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：FloatingBall。

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
   · import 要写 `from FloatingBall import …`（**不带包路径**）
   · `_set_app` 要**取别名**（`as _fk_…`）—— 模块名和类名同名
   · 借名字清单**用 symtable + dir() 定**，别用正则猜
   · 代理类**必须实现 `__call__`**（函数也会被借）
   · ★ 兜底 except 会吃掉错误 → **必须专门测"用的哪一份"**
"""
import threading
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, colorchooser

# ---------- 要向主程序借的名字 ----------
_MUTABLE = ['BOLD', 'FONT']
_NEED = ['BALL_SHAPES', 'BOLD', 'FONT', 'T', 'Tooltip', '_BALL_STYLES', '_disk_speed_text', '_mem_text', '_net_speed_text', 'apply_theme_names', 'ball_style_add', 'ball_style_get', 'ball_style_names', 'load_ui_setting', 'note_swallowed', 'save_ui_setting', 'theme_get']
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


class FloatingBall:
    """★ 悬浮球：一个能拖到任何地方的小圆球，左键出菜单、右键出设置。

    ★ 它**不是** Toplevel 的子类 —— 因为要 `overrideredirect(True)`（无边框），
      而那会让它脱离窗口管理器；用一个"持有 Toplevel 的普通对象"更好控制
      （也方便以后换实现，不用改调用方）。

    ★ 实测验证过的能力（动手前先试的，见错题本）：
      · `overrideredirect(True)` → 无边框 ✔
      · `attributes("-topmost", True/False)` → 置顶 ✔
      · `attributes("-alpha", 1.0/0.85/0.6/0.4)` → **透明度好使** ✔
      · 无边框下也能用 `geometry("+x+y")` 移动 ✔
    """

    # ★ 显示项（用户可多选）—— (键, 菜单里的名字, 默认开不开)
    DISPLAY_ITEMS = (
        ("hamburger", "三道杠 ☰", True),
        ("net",       "网速 ↓↑",   False),
        ("disk",      "硬盘读写 R/W", False),
        ("mem",       "内存",      False),
    )

    # ★ 透明度档位
    ALPHAS = (("100%（不透明）", 1.0),
              ("90%", 0.9),
              ("80%", 0.8),
              ("70%", 0.7),
              ("55%", 0.55))

    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.win = None
        self.canvas = None
        self._drag_off = None
        self._moved = False
        self._menu_open = False
        # ★ 显示哪些（从设置读，默认只"三道杠"）
        self.show = self._load_show()
        # ★ 透明度
        self.alpha = float(load_ui_setting("float_ball_alpha", 1.0) or 1.0)
        self.alpha = max(0.3, min(1.0, self.alpha))
        # ★ 网速/硬盘 的缓存值（由后台线程填）
        self._net_text = ""
        self._disk_text = ""
        self._mem_text = ""
        self._stat_job = None
        self._disk_job = None
        # ★★★ 2026-10-08 **球自己的皮肤**（跟主界面**完全分开**）★★★
        #   ★ 用户选的是 B B B：② 球默认就独立 ③ 永远不跟主界面
        #   → 所以这里**读自己的设置**（`ball_style`），
        #     **不读**主界面的 `theme_get`（一个都不读）。
        #   ★ 关键：`ball_style_get()` **永远返回一套能用的**
        #     （读不到就给默认蓝）—— 球是每秒要画的东西，
        #     返回 None 会让球**直接消失**（用户以为程序坏了）。
        #   ★★ 2026-10-08 **改成"两个独立的键"**（用户说"形状和颜色要分开"）：
        #       `ball_color` —— 只管颜色（fill / outline / fg）
        #       `ball_shape` —— 只管形状（circle / dot / ring / square / rect）
        #     ★ 为什么分开：原来捆在一起存成 `"颜色__形状"`，
        #       换几次之后名字滚成 `orange__circle__ring__dot…`，
        #       而且**换形状会顺手把颜色也改掉**（用户说"值不对"就是这个）。
        #     ★ 分开之后：换形状**绝不动颜色**、换颜色**绝不动形状**，
        #       存的键**永远只有两个**（不滚雪球）。
        self.color_key = self._load_color_key()
        self.shape_key = self._load_shape_key()
        self.style = self._compose_style()
        # ★★ 2026-10-08 **换行显示**（用户说"没必要非挤一行"）
        #   ★ 开着 → 每样一行（☰ / 网速 / 硬盘 / 内存 各占一行）
        #   ★ 关着 → 挤一行（原来的样子）
        try:
            self.multiline = bool(load_ui_setting("ball_multiline", False))
        except Exception:
            self.multiline = False

    # ---------------- ★ 球皮肤：颜色 / 形状 **分开管** ----------------
    def _load_color_key(self):
        """★ 读"球用哪套颜色"（独立的一个键 `ball_color`）。

        ★ 兼容老设置：以前存的是 `ball_style`（颜色和形状捆在一起的名字，
          形如 `orange__circle`）—— 这里**从老名字里把颜色部分抠出来**，
          老用户升级后**颜色不丢**。
        """
        try:
            v = load_ui_setting("ball_color", None)
            if v and v in _BALL_STYLES:
                return str(v)
        except Exception:
            pass
        # ★ 兼容老的 `ball_style`（可能是 `颜色__形状` 的形式）
        try:
            old = str(load_ui_setting("ball_style", "") or "")
            if old:
                base = old.split("__")[0]     # ★ 只取"颜色"那一半
                if base and base in _BALL_STYLES:
                    return base
                if old in _BALL_STYLES:
                    return old
        except Exception:
            pass
        return "default"

    def _load_shape_key(self):
        """★ 读"球是什么形状"（独立的一个键 `ball_shape`）。

        ★ 同样兼容老设置：老的 `ball_style` 形如 `orange__circle`，
          从里面把"形状"那一半抠出来。
        """
        _known = [s[0] for s in BALL_SHAPES]
        try:
            v = load_ui_setting("ball_shape", None)
            if v and v in _known:
                return str(v)
        except Exception:
            pass
        try:
            old = str(load_ui_setting("ball_style", "") or "")
            if "__" in old:
                tail = old.split("__")[-1]
                if tail in _known:
                    return tail
        except Exception:
            pass
        return "circle"

    def _load_show_fallback(self):
        """（占位，保持方法顺序整齐）"""
        return None

    def _compose_style(self):
        """★★ **把"颜色"和"形状"拼成一套完整样式**（`_redraw` 用的）。

        ★ 这是"分开存、合起来用"的关键一步：
          存的永远是两个独立的键，**用的时候临时拼** ——
          所以**换任何一个都不会影响另一个**。
        """
        st = ball_style_get(self.color_key)
        st["shape"] = self.shape_key
        return st

    # ---------------- 读写设置 ----------------
    def _load_show(self):
        """★ 读"显示哪些"（存成一个列表，比如 `["hamburger", "net"]`）。"""
        try:
            v = load_ui_setting("float_ball_show", None)
            if isinstance(v, (list, tuple)):
                out = [k for k in v if any(k == x[0] for x in self.DISPLAY_ITEMS)]
                if out:
                    return out
        except Exception:
            pass
        # ★ 默认：只显示三道杠（用户原话「圆球默认三道杠好」）
        return [x[0] for x in self.DISPLAY_ITEMS if x[2]]

    def _save_show(self):
        try:
            save_ui_setting("float_ball_show", list(self.show))
        except Exception:
            pass

    def _save_pos(self):
        """★ 记住球现在的位置（关掉程序下次还在那儿）。

        ★★ 存的是"**相对主窗口**"的坐标，不是屏幕坐标 ——
          这样主窗口挪了，球**跟着挪**（不会"留在屏幕别处"）。
          ★ 实测踩的坑：我第一版存的是 `winfo_x()`（**屏幕**坐标），
            结果"下次打开"如果主窗口位置变了，球就飘到别处了。
        """
        try:
            if self.win is None:
                return
            x = int(self.win.winfo_x()) - int(self.root.winfo_rootx())
            y = int(self.win.winfo_y()) - int(self.root.winfo_rooty())
            save_ui_setting("float_ball_pos", [x, y])
        except Exception as _e:
            note_swallowed(T("记住悬浮球位置失败"), _e)

    def _load_pos(self):
        """★ 读回上次的位置；**不在可见区域就拉回来**（免得球"不见了"）。"""
        try:
            v = load_ui_setting("float_ball_pos", None)
            if isinstance(v, (list, tuple)) and len(v) == 2:
                x, y = int(v[0]), int(v[1])
                sw = int(self.root.winfo_screenwidth())
                sh = int(self.root.winfo_screenheight())
                # ★ 容错：留 40 像素必须可见（不然用户找不回来）
                if -20 <= x <= sw - 40 and -20 <= y <= sh - 40:
                    return x, y
        except Exception:
            pass
        return None

    def _default_pos(self):
        """★ 第一次出现的位置：**文件列表右侧那块空白区**（用户指定的）。

        ★ 怎么算：拿"文件列表"这个控件的位置和宽度 ——
          右边就是预览/标签库那一带，往里偏一点（别贴边）。
        """
        try:
            lf = getattr(self.app, "file_list", None) or \
                 getattr(self.app, "list_frame", None)
            if lf is not None:
                lx = lf.winfo_rootx() - self.root.winfo_rootx()
                lw = max(60, lf.winfo_width())
                ly = lf.winfo_rooty() - self.root.winfo_rooty()
            else:
                lx, lw, ly = self.root.winfo_width() // 2, 200, 120
            x = lx + lw + 24
            y = ly + 24
            # ★ 别跑出窗口
            x = max(0, min(x, max(0, self.root.winfo_width() - 90)))
            y = max(0, min(y, max(0, self.root.winfo_height() - 90)))
            return int(x), int(y)
        except Exception:
            return 320, 140

    def _abs_pos(self):
        """★ 把"窗口内的相对位置"换成"屏幕坐标"。

        ★ 为什么：球是**独立置顶窗口**（无边框），它的坐标是**屏幕坐标**；
          而用户拖、记忆都用"**相对于主窗口**"更合理
          （主窗口挪了，球跟着挪，不会跑到屏幕角落去）。

        ★★ 2026-10-08 实测踩的坑（**记下来**）：
          ★ 建球的时候，主窗口**可能还没被"最大化"** ——
            实测：`root.geometry("1400x860")` 之后等一会儿，
            主窗口其实是 **2560 宽**（程序**默认最大化**，见待清算里的要求）。
          ★ 而"文件列表右边"是**按主窗口当时的宽度算的** ——
            如果算得太早，会得出一个**偏左**的位置（实测球跑到 x=84）。
          → 修法：**建完之后过一小会儿再摆一次**（等最大化落定）。
            ★ 这也是错题本 #110 那条教训的又一例：
              "**别在东西还没稳定的时候去量它**"。
        """
        try:
            rx = self.root.winfo_rootx()
            ry = self.root.winfo_rooty()
        except Exception:
            rx = ry = 0
        p = self._load_pos()
        if p is None:
            p = self._default_pos()
        return rx + int(p[0]), ry + int(p[1])

    # ---------------- 建 ----------------
    def build(self):
        """★ 把球建出来（失败返回 False，调用方会把菜单栏装回去）。"""
        try:
            self.win = tk.Toplevel(self.root)
            self.win.overrideredirect(True)      # ★ 无标题栏（不然不是"球"）
            try:
                self.win.attributes("-topmost", True)   # ★ 浮在内容上面
            except Exception:
                pass
            try:
                self.win.attributes("-alpha", self.alpha)
            except Exception:
                pass
            # ★★★ 2026-10-08 **修"球显示不全"**（用户报的）★★★
            #   ★ 两处毛病：
            #     ① `canvas.pack()` **没给 width/height** ——
            #        画布会按"内容想要多大"自适应，而 `win.geometry()`
            #        设的是另一个尺寸 → **两者打架 → 字被截掉**。
            #        → 现在**画布尺寸跟着窗口走**，而且**每次都同步**
            #          （见 `_redraw` 里的 `canvas.configure(width,height)`）。
            #     ② `bg=theme_get("win_bg")` —— **还在读主界面**！
            #        上次做"球皮肤独立"时漏了这两处（`win` 和 `canvas` 的底色），
            #        所以球的四角还露着主界面的颜色。
            #        → 现在用**球自己的 fill**。
            #        ★ 这也是"形状和颜色要分开、值不对"的一部分 ——
            #          混着主界面的色，看着就"不对"。
            try:
                _f = (self.style or {}).get("fill") or "#2c6fd1"
                self.win.configure(bg=_f)
            except Exception:
                pass
            self.canvas = tk.Canvas(self.win, highlightthickness=0,
                                    bd=0, width=60, height=60,
                                    bg=(self.style or {}).get("fill", "#2c6fd1"))
            # ★ `expand=True` 让画布**填满窗口**（不然它只占自己那点尺寸）
            self.canvas.pack(fill="both", expand=True)
            # ★ 鼠标事件
            self.canvas.bind("<Button-1>", self._on_press)
            self.canvas.bind("<B1-Motion>", self._on_drag)
            self.canvas.bind("<ButtonRelease-1>", self._on_release)
            self.canvas.bind("<Button-3>", self._on_right)
            # ★ 悬停提示（不占地方，鼠标放上去才出）
            try:
                # ★★★ 2026-10-08 修一个**看得见的丑**（用户截图截图抓到）：
                #   ★ 原来这里传的是 **lambda**，而 `Tooltip` 当时只收字符串 ——
                #     它内部 `str(text)` →
                #     `<function FloatingBall.build.<locals>.<lambda> at 0x...>`
                #   ★★★ **屏幕上真的显示了这串 Python 地址**。
                #   → 两头都修了（错题本 #174）：
                #     · `Tooltip` 改成**同时接受字符串和函数**（弹之前才现取）
                #     · ★ 这里**保持传函数** —— 因为球的提示文字**会变**
                #       （网速/内存/硬盘的数字每秒在动），
                #       传字符串的话**永远停在创建那一刻的值**。
                Tooltip(self.canvas, lambda: self._tooltip_text())
            except Exception:
                pass
            self._reposition()
            self._redraw()
            # ★★ 2026-10-08：**过一小会儿再摆一次**。
            #   ★ 为什么（实测踩的）：建球时主窗口**可能还没最大化落定** ——
            #     实测球跑到了 x=84（应该 2000 多），
            #     因为那会儿量到的"文件列表右边"是按**旧宽度**算的。
            #   → 延时重摆一次，位置就对了。
            #     ★ 只在"从没存过位置"时重摆（用户拖过的位置**不能动**）。
            try:
                if self._load_pos() is None:
                    self.root.after(900, self._settle_pos)
            except Exception:
                pass
            # ★ 启动"每秒刷网速"（只在对应用户开了的时候才真干活）
            self._tick_stats()
            self._tick_disk()
            return True
        except Exception as exc:
            try:
                note_swallowed(T("建悬浮球失败（会退回用菜单栏）"), exc)
            except Exception:
                pass
            return False

    def _ball_size(self):
        """★ 球多大 —— 按"要显示多少内容"和"球的形状"自动定。

        ★★ 2026-10-08：**加了形状的考虑**（用户要"样式"）：
          · `capsule`（胶囊/长条）—— **横向拉长**（字多也不挤）
          · `dot`（只有圆点）    —— **固定小尺寸**（最不挡事）
          · 其余                  —— 按内容宽度
        ★ 为什么 `dot` 要固定小：用户选它就是嫌挡事 ——
          如果它还是跟着内容变宽，就**失去意义了**。
        """
        try:
            need = self._content()
        except Exception:
            need = "☰"
        shape = (getattr(self, "style", None) or {}).get("shape") or "circle"
        if shape == "dot":
            # ★ 小圆点：固定 26x26（就一个点，不显示字）
            return 26, 26
        # ★ 2026-10-08：胶囊（长条）**删掉了**（用户说"胶囊不要了"）
        # ★★ 换行模式下**按"最长那一行"算宽度、"行数"算高度** ——
        #    这样球是"竖着长"而不是"横着撑"（用户要的效果）。
        rows = str(need).split("\n")
        longest = max((len(r) for r in rows), default=1)
        # 圆球 / 圆环 / 方块 / 纯方：按内容宽度（下限 52，上限 190）
        w = max(52, min(190, 22 + longest * 9))
        if len(rows) > 1:
            # ★ 多行：高度按行数长（每行约 18px），宽度至少能放下最长的
            h = max(52, min(160, 16 + len(rows) * 20))
        else:
            h = max(52, w if len(need) <= 3 else 46)
        return int(w), int(h)

    def _reposition(self):
        """★ 摆到该在的地方（改大小时也用这个，保持中心不动）。"""
        try:
            x, y = self._abs_pos()
            w, h = self._ball_size()
            self.win.geometry("%dx%d+%d+%d" % (w, h, x, y))
        except Exception:
            pass

    def _settle_pos(self):
        """★ （建球后延时调用）**等主窗口稳定了，再按"文件列表右边"摆一次**。

        ★ 只在"用户还没给过位置"时才会被调 —— 用户拖过的位置**绝不动它**。
        """
        try:
            if self.win is None:
                return
            if self._load_pos() is not None:
                return          # ★ 用户给过位置 → 不许动
            x, y = self._abs_pos()
            self.win.geometry("+%d+%d" % (x, y))
        except Exception:
            pass

    def _content(self):
        """★ 球上显示什么字（按用户选的组合拼出来）。

        ★★★ 2026-10-08 **支持换行**（用户说"没必要非挤一行"）★★★
          ★ 用户原话：
            「感觉网速、硬盘什么的可以**换行显示**，没必要非挤一行」
          ★ 为什么要换行：
            球上"网速 + 硬盘 + 内存"全打开时，一行能有 40 多个字符 →
            **球被撑成一根长条**（很难看，也挡事）。
            换行之后**高度换宽度** → 球更"方"、更小巧。
          ★ 怎么控制（`ball_multiline`，右键菜单里勾）：
            · 开 → **每样一行**（☰ / 网速 / 硬盘 / 内存 各占一行）
            · 关 → 挤一行（原来的样子）
        """
        parts = []
        if "hamburger" in self.show:
            parts.append("☰")
        if "net" in self.show:
            parts.append(self._net_text or "↓— ↑—")
        if "disk" in self.show:
            parts.append(self._disk_text or "R— W—")
        if "mem" in self.show:
            parts.append(self._mem_text or "RAM—")
        if not parts:
            return "☰"          # ★ 一个都没选 → 至少还看得见（不然球没了）
        # ★ 换行模式：一样一行（"☰" 那种纯符号不单独占一行，省地方）
        if getattr(self, "multiline", False):
            big = [p for p in parts if len(p) > 3 or p != "☰"]
            small = [p for p in parts if p not in big]
            rows = []
            if small:
                rows.append(" ".join(small))
            rows.extend(big)
            return "\n".join(rows)
        return "  ".join(parts)

    def _tooltip_text(self):
        """★ 鼠标放上去显示详细一点的（球上地方小，放不下的在这里）。"""
        lines = ["左键：出菜单", "右键：设置（皮肤 / 透明度 / 显示什么）", "拖动：放哪儿都行"]
        if "net" in self.show or "disk" in self.show or "mem" in self.show:
            lines.append("—— 实时 ——")
            if "net" in self.show:
                lines.append("网速：%s" % (self._net_text or "…"))
            if "disk" in self.show:
                lines.append("硬盘：%s" % (self._disk_text or "…"))
            if "mem" in self.show:
                lines.append("内存：%s" % (self._mem_text or "…"))
        return "\n".join(lines)

    def _redraw(self):
        """★★ 重画球（大小、颜色、文字、**形状**都按"球自己的皮肤"来）。

        ★★★ 2026-10-08 **重要改动**（用户要求"球皮肤跟主界面完全分开"）：
          ★ 原来这里是：
              `fill = theme_get("accent")`   ← **从主界面借颜色**
              `ring = theme_get("fg")`       ← 从主界面借边框色
              `bg   = theme_get("win_bg")`   ← 从主界面借底色
          → 结果：**主界面换个皮肤，球跟着变** ——
            而用户在球上点"皮肤"，改的却是**整个主界面**（他说"搞混了"）。
          ★ 现在**一个 `theme_get` 都不用了** ——
            只读 `self.style`（球自己的皮肤）：
              `fill` / `outline` / `fg` / `shape`
          ★★ 用户选的是 **B B B**：
             ② 球**默认就独立**（一开始就蓝，不管主界面）
             ③ **永远不跟**（主界面换了，球纹丝不动）
            → 所以这里**彻底断开**，一个都不借用。

        ★ 支持的**形状/样式**（用户要的"不只颜色形状，还要样式"）：
          · `circle`  圆球（最常见）
          · `capsule` 胶囊/长条（字多的时候好看）
          · `dot`     只有一个小圆点（最不挡事）
          · `ring`    空心圆环（很通透）
          · `square`  圆角方块（像按钮）
        """
        try:
            # ★★★ 2026-10-08 **根上的防护**（账本里 1 次：
            #   `AttributeError: 'NoneType' object has no attribute 'geometry'`）
            #   ★ 真因：`_redraw()` 会碰 `self.win`，而 `hide()` 会把 `self.win`
            #     置成 `None`。**球被关掉之后，任何"晚一步"的调用都会炸** ——
            #     典型是**定时器回调**（每秒读网速 / 每 6 秒读硬盘）：
            #     进函数时球还在，读数据那几毫秒里用户点了"关掉这个球"。
            #   ★★ 所以**在 `_redraw` 入口直接挡一道** ——
            #     这样"谁调的""什么时候调的"都不重要了。
            #     （调用方那几处也补了判断，两处一起更稳。）
            if self.win is None:
                return
            c = self.canvas
            if c is None:
                return
            st = self.style
            w, h = self._ball_size()
            self.win.geometry("%dx%d+%d+%d"
                              % (w, h, self.win.winfo_x(), self.win.winfo_y()))
            # ★ 球窗口自己的底色 —— **用球的 fill 当底**（不是主界面的 win_bg），
            #   否则圆角外面会露出主界面的颜色，看着像"球贴了块补丁"。
            #   ★ 但"圆球/圆点"是例外：它们**四角本来就该是空的**，
            #     所以底色调成跟球最接近的（用 fill 的近似深色）。
            # ★★ 2026-10-08：**画布尺寸必须跟窗口一致** ——
            #   不然"画布比窗口小"时字被截（用户报的"显示不全"）。
            c.configure(width=w, height=h, bg=st.get("fill") or "#2c6fd1")
            # ★ 顺手把窗口底色也刷一下（换颜色时四角要跟着变）
            try:
                self.win.configure(bg=st.get("fill") or "#2c6fd1")
            except Exception:
                pass
            c.delete("all")
            fill = st.get("fill") or "#2c6fd1"
            ring = st.get("outline") or "#ffffff"
            fg = st.get("fg") or "#ffffff"
            shape = st.get("shape") or "circle"
            # ★ 边框宽度：空心圆环要粗一点，别的 2 像素
            bw = 3 if shape == "ring" else 2
            if shape == "ring":
                # ★ 空心圆环：不填色（用底色当"透明"，视觉上就是空心的）
                c.create_oval(2, 2, w - 2, h - 2, fill="", outline=ring,
                              width=bw)
            elif shape == "rect":
                # ★★★ 2026-10-08 **纯方块（直角）** —— 用户说"没有纯方的皮肤"。
                #   ★ 为什么原来没有：`square` 那条分支用了
                #     `create_polygon(..., smooth=True)` ——
                #     **`smooth=True` 会把直角"磨圆"**！所以看到的永远是圆角。
                #   ★ 这个用 `create_rectangle` —— **四边都是直的**。
                c.create_rectangle(1, 1, w - 1, h - 1, fill=fill,
                                   outline=ring, width=bw)
            elif shape == "square":
                # ★ 圆角方块（`create_rectangle` 画不出圆角，用多边形近似）
                #   ★ 保留它是因为"圆角"也是一种样式（有人就喜欢圆角）。
                r = min(w, h) // 6
                pts = [r, 1, w - r, 1, w - 1, r, w - 1, h - r, w - r, h - 1,
                       r, h - 1, 1, h - r, 1, r]
                c.create_polygon(pts, fill=fill, outline=ring, width=bw,
                                 smooth=True)
            elif shape == "dot" and not self._menu_open:
                # ★ "只有一个小圆点"：**球的窗口也变小**（见 `_ball_size`），
                #   这里就画个实心点 —— 最不挡事。
                d = max(8, min(w, h) - 6)
                c.create_oval((w - d) / 2, (h - d) / 2,
                              (w + d) / 2, (h + d) / 2,
                              fill=fill, outline=ring, width=1)
                return
            else:
                # ★ 圆球 / 胶囊（胶囊靠"宽 > 高"自然成形，还是画椭圆）
                c.create_oval(1, 1, w - 1, h - 1, fill=fill, outline=ring,
                              width=bw)
            txt = self._content()
            # ★ 文字大小按球大小来（球小的时候字也小）
            #   ★ 多行时按"最长那一行"算（不是整串长度）——
            #     不然换行之后字号会被算得过小。
            _rows = str(txt).split("\n")
            _mx = max((len(r) for r in _rows), default=1)
            fs = 20 if _mx <= 3 else (13 if _mx <= 14 else 10)
            if len(_rows) > 1 and len(_rows) >= 3:
                fs = min(fs, 12)          # 三行以上再小一点
            c.create_text(w / 2, h / 2, text=txt, fill=fg,
                          font=(FONT, fs, BOLD),
                          justify="center")
        except Exception as _e:
            note_swallowed(T("重画悬浮球失败"), _e)

    # ---------------- 拖动 ----------------
    def _on_press(self, event):
        try:
            self._drag_off = (event.x_root - self.win.winfo_x(),
                              event.y_root - self.win.winfo_y())
            self._moved = False
        except Exception:
            self._drag_off = None

    def _on_drag(self, event):
        """★ 拖动 —— 「蒙多，想去哪就去哪」（不吸边、不限制）。"""
        try:
            if not self._drag_off:
                return
            self._moved = True
            nx = event.x_root - self._drag_off[0]
            ny = event.y_root - self._drag_off[1]
            self.win.geometry("+%d+%d" % (nx, ny))
        except Exception:
            pass

    def _on_release(self, event):
        """★ 松手：没拖动过 = 单击（出菜单）；拖过 = 记住新位置。"""
        try:
            moved = self._moved
            self._moved = False
            self._drag_off = None
            if moved:
                self._save_pos()
                return
        except Exception:
            return
        self._popup_main_menu()

    def _popup_main_menu(self):
        """★ 左键 → 弹出**主程序那个菜单**（37 个入口自动全在）。"""
        try:
            mb = getattr(self.app, "menubar", None)
            if mb is None:
                # ★ 万一没有（不该发生）—— 至少把菜单栏装回来
                try:
                    self.app._toggle_menubar()
                except Exception:
                    pass
                return
            # ★ 弹之前刷一遍状态圆点（跟原来菜单栏的行为一致）
            try:
                self.app._refresh_menu_states()
            except Exception:
                pass
            self._menu_open = True
            try:
                mb.tk_popup(self.win.winfo_rootx(),
                            self.win.winfo_rooty() + self.win.winfo_height())
            finally:
                try:
                    mb.grab_release()
                except Exception:
                    pass
                self._menu_open = False
        except Exception as _e:
            note_swallowed(T("悬浮球弹菜单失败"), _e)

    # ---------------- 右键：设置 ----------------
    # ------------------- ★ 菜单上色（左键右键统一）-------------------
    def _theme_menu(self, menu):
        """★★ **给球的菜单上色** —— ★★★ **但不要抄主菜单的 `cget`！**

        ★★★ 2026-10-08 **实测踩的坑（差点把好功能改坏）**：
          ★ 我一开始写的是"抄主菜单当前的色"：
              `bg = self.app.menubar.cget("bg")`
              `menu.configure(bg=bg)`
            **以为这样就"跟左键一致"**。
          ★★ 实测结果 —— **反而把它弄坏了**：
            ```
            未上色 cget(bg) = '#222327'        ★ 本来就是对的！
            上色后 cget(bg) = 'SystemMenu'      ★★ 我的"上色"改坏了！
            ```
          ★ 真因：**`menubar.cget("bg")` 返回的是"系统色名" `SystemMenu`，
            不是实际的颜色值**（那个名字对应的真色是 `#f0f0f0` 浅灰）。
            → 抄过来就等于**把菜单设成系统默认（浅色）**，
              于是"用我的修复"反而制造了用户报的那个"一黑一白"。
          ★★★ **真相是：球的菜单本来就已经是对的** ——
            主程序用 `root.option_add("*Menu.background", PANEL)` 给
            **所有菜单**上了色（`option_add` 的 `*Menu.*` 是**全局匹配**，
            **Toplevel 里的菜单也吃得到** —— 这点我也实测确认过）。
          → **所以正确做法是：什么都别改。**

        ★ 这个方法**现在只做一件事**：**万一真的没上色**（比如以后
          有人改了 `option_add` 的写法、或者某个 Tk 版本不灵），
          用**主题色值**补一下 —— **绝不再抄 `cget`**。
          ★ 判据：**只改"看起来还是系统默认色"的那些**，
            已经是对的**一个字都不碰**（免得像上面那样改坏）。
        """
        if menu is None:
            return
        try:
            cur = str(menu.cget("bg"))
            # ★ 已经是"真颜色"（`#rrggbb`）→ **不动它**（它已经对了）
            if cur.startswith("#"):
                return
            # ★ 是"系统色名"（`SystemMenu` 之类）→ 说明没上过色，补一下
            #   ★★ 用**主题色值**（不是 `cget`！）
            bg = theme_get("panel_bg") or theme_get("card_bg") \
                or theme_get("win_bg")
            fg = theme_get("fg") or "#d6d7db"
            abg = theme_get("select_bg") or theme_get("accent") or "#3a76c8"
            menu.configure(bg=bg, fg=fg, activebackground=abg,
                           activeforeground=fg,
                           disabledforeground=theme_get("fg_dim") or fg)
        except Exception:
            pass

    def _theme_menu_tree(self, menu, depth=0):
        """★ **递归**给菜单和所有子菜单上色（子菜单不上色还是会花）。

        ★ 为什么要递归：右键菜单里有好几个 `add_cascade`
          （球的皮肤 / 主界面皮肤 / 透明度 / 显示什么 / 形状…）——
          **它们各自是独立的 `Menu` 对象**，
          只给最外层上色的话，**点开子菜单还是白的**。
        ★ `depth` 是防呆（万一菜单互相引用，无限递归）——
          超过 6 层就停（正常最多 3 层）。
        ★ 实际起作用的是 `_theme_menu` —— 它**只补"没上过色的"**，
          已经对的**一个字都不碰**（错题本 #138 的教训）。
        """
        if menu is None or depth > 6:
            return
        self._theme_menu(menu)
        try:
            n = menu.index("end")
            if n is None:
                return
            for i in range(n + 1):
                try:
                    if str(menu.type(i)) == "cascade":
                        sub = menu.nametowidget(menu.entrycget(i, "menu"))
                        self._theme_menu_tree(sub, depth + 1)
                except Exception:
                    continue
        except Exception:
            pass

    def _on_right(self, event=None):
        """★★ 右键 → 设置菜单。

        ★★★ 2026-10-08 **重排**（用户要求："球皮肤跟主界面皮肤**别搞混**"）★★★

        ★★ 原来长这样（**就是"搞混"的根源**）：
            `皮肤 ▸ 白天 / 夜间 / 快速切换…`
          ★ 它挂在**球的菜单**里，但点下去改的是**整个主界面** ——
            用户以为在改球，结果主界面全变了。

        ★★ 现在**分成清清楚楚两块**（各管各的）：
            「⚪ 球的皮肤」   —— 只管这个球（颜色 / 形状 / 样式）
            「🎨 主界面皮肤」 —— 只管主窗口（原名叫"皮肤"，**改了名**）
          ★ 两块之间还有分隔线 —— **一眼就知道是两个东西**。
          ★ 用户选的是 B B B（球默认独立、永远不跟主界面），
            所以**球的颜色一个都不从主界面借**。
        """
        try:
            m = tk.Menu(self.win, tearoff=0)
            # ============ ① ⚪ 球的皮肤（只管球自己）============
            m_ball = tk.Menu(m, tearoff=0)
            # ★ 读**独立**的颜色键（跟形状分开）—— 见 `_load_color_key`
            cur_ball = str(getattr(self, "color_key", None) or "default")
            _var_ball = tk.StringVar(value=cur_ball)
            for key, lbl in ball_style_names():
                try:
                    m_ball.add_radiobutton(
                        label=("● " if key == cur_ball else "　") + T(lbl),
                        value=key, variable=_var_ball,
                        command=lambda k=key: self.set_ball_style(k))
                except Exception:
                    pass
            m_ball.add_separator()
            # ★ 形状（用户要的"样式"）
            m_shape = tk.Menu(m_ball, tearoff=0)
            # ★ 读**独立**的形状键（跟颜色分开）—— 见 `_load_shape_key`
            cur_shape = str(getattr(self, "shape_key", None) or "circle")
            _var_shape = tk.StringVar(value=cur_shape)
            for skey, slab, _desc in BALL_SHAPES:
                try:
                    m_shape.add_radiobutton(
                        label=("● " if skey == cur_shape else "　") + T(slab),
                        value=skey, variable=_var_shape,
                        command=lambda s=skey: self.set_ball_shape(s))
                except Exception:
                    pass
            m_ball.add_cascade(label=T("形状 / 样式"), menu=m_shape)
            m_ball.add_separator()
            m_ball.add_command(label=T("🎨 自定义颜色（底色 / 边框 / 文字）…"),
                               command=self._custom_ball_colors)
            m_ball.add_command(label=T("↩ 回到蓝色默认"),
                               command=lambda: self.set_ball_style("default"))
            m.add_cascade(label=T("⚪ 球的皮肤"), menu=m_ball)

            # ============ ② 🎨 主界面皮肤（只管主窗口）============
            m_skin = tk.Menu(m, tearoff=0)
            _var_main = self._skin_var()
            for key, lbl in apply_theme_names():
                try:
                    m_skin.add_radiobutton(
                        label=lbl, value=key, variable=_var_main,
                        command=lambda k=key: self.app.set_theme(k))
                except Exception:
                    pass
            m_skin.add_separator()
            m_skin.add_command(label=T("🌓 快速切换白天 / 夜间"),
                               command=self.app.toggle_theme)
            m_skin.add_command(label=T("🖥 调整界面缩放…"),
                               command=self.app.change_ui_scale)
            # ★ **名字写清楚**：这是主界面的，不是球的
            m.add_cascade(label=T("🎨 主界面皮肤（整界面）"), menu=m_skin)

            # ============ ③ 其余（球的设置）============
            m.add_separator()
            # ---- 透明度 ----
            m_alpha = tk.Menu(m, tearoff=0)
            for label, v in self.ALPHAS:
                mark = "● " if abs(self.alpha - v) < 0.01 else "　"
                m_alpha.add_command(
                    label=mark + label,
                    command=lambda vv=v: self._set_alpha(vv))
            m.add_cascade(label=T("透明度"), menu=m_alpha)
            # ---- ★ 显示模式（用户要的：自己选、可组合）----
            m_show = tk.Menu(m, tearoff=0)
            for key, label, _d in self.DISPLAY_ITEMS:
                on = key in self.show
                m_show.add_checkbutton(
                    label=("[✓] " if on else "[　] ") + label,
                    command=lambda k=key: self._toggle_show(k))
            m_show.add_separator()
            m_show.add_command(label=T("只显示三道杠 ☰"),
                               command=lambda: self._set_show(["hamburger"]))
            m_show.add_command(label=T("只显示网速 ↓↑"),
                               command=lambda: self._set_show(["net"]))
            m_show.add_command(label=T("只显示硬盘读写 R/W"),
                               command=lambda: self._set_show(["disk"]))
            m_show.add_command(label="三道杠 + 网速",
                               command=lambda: self._set_show(["hamburger", "net"]))
            m_show.add_command(label=T("全都要"),
                               command=lambda: self._set_show(
                                   [k for k, _l, _d in self.DISPLAY_ITEMS]))
            m_show.add_separator()
            # ★★ 2026-10-08 **换行显示**（用户说"没必要非挤一行"）★★
            #   ★ 为什么需要：全打开时一行 40 多个字符 →
            #     **球被撑成一根长条**（难看、也挡事）。
            #     换行 → **高度换宽度**，球更"方"、更小巧。
            _ml = getattr(self, "multiline", False)
            m_show.add_checkbutton(
                label=("[✓] " if _ml else "[　] ") + "换行显示（一样一行，球更小巧）",
                command=self._toggle_multiline)
            m.add_cascade(label=T("显示什么"), menu=m_show)
            # ---- 位置 ----
            m.add_separator()
            m.add_command(label=T("↩ 放回文件列表右侧（默认位置）"),
                          command=self._reset_pos)
            # ---- 菜单栏 ----
            m.add_command(
                label=("显示菜单栏（现在是藏着的）"
                       if getattr(self.app, "_menu_hidden", False)
                       else "藏起菜单栏"),
                command=self.app._toggle_menubar)
            m.add_separator()
            m.add_command(label=T("⏹ 关掉这个球（还能从「设置」菜单叫回来）"),
                          command=self.hide)
            # ★★ 2026-10-08 **先给菜单（和它所有子菜单）上色** ★★
            #   ★ 为什么（用户报的"左键和右键的底色不一样，一黑一白"）：
            #     球是**独立窗口**（用户选了"永远不跟主界面"）——
            #     左键弹的是**主程序的 menubar**（被皮肤刷过 = 深色），
            #     右键弹的是 `tk.Menu(self.win, …)` ——
            #     parent 是"球那个小窗口"，**没有任何皮肤刷过它**
            #     → 系统默认白色 → **一黑一白**。
            #   ★ 所以不是"没统一"，是"**右键菜单根本没上过色**"。
            #   ★ 要**递归**上色 —— 透明度、显示什么、球的皮肤…
            #     那些子菜单不一起弄，点开还是白的。
            try:
                self._theme_menu_tree(m)
            except Exception:
                pass
            try:
                m.tk_popup(event.x_root, event.y_root)
            finally:
                try:
                    m.grab_release()
                except Exception:
                    pass
        except Exception as _e:
            note_swallowed(T("悬浮球右键菜单失败"), _e)

    def _skin_var(self):
        """★ 皮肤的单选变量（跟主程序那个共用，免得两边不同步）。"""
        try:
            v = getattr(self.app, "theme_var", None)
            if v is not None:
                return v
        except Exception:
            pass
        if getattr(self, "_skinvar", None) is None:
            self._skinvar = tk.StringVar(
                value=str(theme_get("name") or "light"))
        return self._skinvar

    def _set_alpha(self, v):
        """★ 改透明度（立刻生效 + 记住）。"""
        try:
            self.alpha = float(v)
            self.win.attributes("-alpha", self.alpha)
            save_ui_setting("float_ball_alpha", self.alpha)
        except Exception as _e:
            note_swallowed(T("改悬浮球透明度失败"), _e)

    # ======================================================================
    #  ★★★ 2026-10-08：**球的皮肤**（用户要求：跟主界面**完全分开**）
    # ======================================================================
    def set_ball_style(self, name):
        """★ **换球自己的颜色**（**只管颜色，不动形状**）。

        ★★ 跟 `app.set_theme()` **完全是两回事**：
          · `app.set_theme()`   → 改**整个主界面**（存 `theme`）
          · `self.set_ball_style()` → **只改这个球**（存 `ball_color`）
          ★ 用户原话：「有球自己的皮肤也有主界面的皮肤…你别搞混了啊」

        ★★★ 2026-10-08 **改成"只管颜色"**（用户说"形状和颜色要分开"）：
          原来这里连形状一起换（`self.style = ball_style_get(name)`）——
          而套现成的颜色里**自带一个 shape** →
          **换个颜色，形状也被改掉了**（用户说"值不对"就是这个）。
          → 现在：**只换 `color_key`，`shape_key` 一个字都不碰**。
        """
        try:
            self.color_key = str(name)
            save_ui_setting("ball_color", self.color_key)
            # ★ **重新合成**（颜色新的 + 形状还是原来那个）
            self.style = self._compose_style()
            # ★ 形状没变 → 尺寸一般不变；但 `_reposition` 顺手也无害
            self._reposition()
            self._redraw()
        except Exception as _e:
            note_swallowed(T("换悬浮球颜色失败"), _e)

    def set_ball_shape(self, shape):
        """★ **换球的形状**（**只管形状，不动颜色**）。

        ★ 支持的形状见 `BALL_SHAPES`：
          圆球 / 只有小圆点 / 空心圆环 / 圆角方块 / **纯方块（直角）**

        ★★★ 2026-10-08 **重写**（用户说"形状和颜色要分开、值不对"）：
          ★ 原来这里是"把形状塞进当前样式、再注册成一个组合名"：
              `st = dict(self.style); st["shape"] = shape`
              `nm = "orange__circle"; save_ui_setting("ball_style", nm)`
            → 三个毛病：
              ① **换形状把颜色也一起存了**（捆着的）
              ② 名字**越滚越长**（`orange__circle__ring__dot…`）
              ③ 换颜色时对不上 → **值错乱**（用户说"值不对"）
          ★ 现在：**只改 `shape_key` 一个键**，颜色一个字都不碰。
            · 存的键**永远只有两个**（`ball_color` / `ball_shape`）
            · 换形状**绝不动颜色** ✔
            · 换颜色**绝不动形状** ✔
        ★ 形状会影响**球的大小**（圆点要小）——
          所以 `_reposition()`（它内部问 `_ball_size()`）再画。
        """
        try:
            _known = [s[0] for s in BALL_SHAPES]
            if str(shape) not in _known:
                return
            self.shape_key = str(shape)
            save_ui_setting("ball_shape", self.shape_key)
            # ★ **重新合成**（形状新的 + 颜色还是原来那个）
            self.style = self._compose_style()
            self._reposition()
            self._redraw()
        except Exception as _e:
            note_swallowed(T("换悬浮球形状失败"), _e)

    def _custom_ball_colors(self):
        """★ **自定义球的颜色**（底色 / 边框 / 文字色）。

        ★ 为什么用"三个颜色选择框"而不是"输入 #rrggbb"：
          用户是"我不懂代码"的人 —— **让他打字输入色号是不可能的**。
          `tkinter.colorchooser` 是系统自带的**取色盘**，
          点一下、挑个颜色 —— 这才叫"能用"。
        """
        try:
            from tkinter import colorchooser
            st = dict(getattr(self, "style", None) or ball_style_get("default"))
            # 依次问三个颜色（取消任何一步就停下，不改）
            for key, title in (("fill", "选【圆球底色】"),
                               ("outline", "选【边框颜色】"),
                               ("fg", "选【球上文字颜色】")):
                try:
                    rgb, hx = colorchooser.askcolor(
                        color=st.get(key) or "#2c6fd1",
                        title=title, parent=self.win)
                except Exception:
                    break
                if not hx:
                    return          # ★ 用户取消了 → 整个操作取消（不改）
                st[key] = hx
            # ★ 只注册"颜色"那部分（形状由 `shape_key` 独立管）
            st["name"] = "custom"
            st["label"] = "自定义"
            ball_style_add("custom", st, label=T("自定义颜色"))
            self.color_key = "custom"
            save_ui_setting("ball_color", "custom")
            # ★ 合成时**用当前的形状**（不是 `st` 里那个）
            self.style = self._compose_style()
            self._reposition()
            self._redraw()
        except Exception as _e:
            note_swallowed(T("自定义悬浮球颜色失败"), _e)

    def _toggle_show(self, key):
        """★ 勾/去勾一个显示项（用户要的"各种组合"）。"""
        try:
            s = list(self.show)
            if key in s:
                # ★ 不许全去掉 —— 不然球上啥都没有，用户以为坏了
                if len(s) <= 1:
                    return
                s.remove(key)
            else:
                s.append(key)
            self._set_show(s)
        except Exception:
            pass

    def _toggle_multiline(self):
        """★★ **切换"换行显示"**（用户说"没必要非挤一行"）。

        ★ 换行之后：
          · **宽度**按"最长那一行"算（不再被整串撑长）
          · **高度**按行数长
          → 全打开时球是"**竖着的小方块**"，而不是"横着的长条"
        ★ 立刻重画 + 记住（下次打开还是这样）。
        """
        try:
            self.multiline = not bool(getattr(self, "multiline", False))
            save_ui_setting("ball_multiline", self.multiline)
            self._reposition()
            self._redraw()
        except Exception as _e:
            note_swallowed(T("切换换行显示失败"), _e)

    def _set_show(self, keys):
        """★ 设置显示项（顺序按 DISPLAY_ITEMS 排，看着整齐）。"""
        try:
            order = [k for k, _l, _d in self.DISPLAY_ITEMS]
            self.show = [k for k in order if k in keys] or ["hamburger"]
            self._save_show()
            self._redraw()
            # ★ 新开了网速/硬盘 → 马上拉一次数据（不然要等一秒才出数）
            self._tick_stats()
            self._tick_disk()
        except Exception as _e:
            note_swallowed(T("改悬浮球显示内容失败"), _e)

    def _reset_pos(self):
        """★ 放回默认位置（文件列表右侧）。

        ★ 注意：**不是**"双击复位"（用户说那个没必要）——
          这是右键菜单里的一个明确选项，用户主动点的。
        ★ 为什么留这个：万一球被拖到某个别扭的地方（或者换了显示器），
          有个"一键回到正常位置"的出路。
        """
        try:
            x, y = self._default_pos()
            rx, ry = self.root.winfo_rootx(), self.root.winfo_rooty()
            self.win.geometry("+%d+%d" % (rx + x, ry + y))
            self._save_pos()
        except Exception as _e:
            note_swallowed(T("悬浮球复位失败"), _e)

    def hide(self):
        """★ 藏起球（菜单栏会被装回来 —— 保证"永远有入口"）。"""
        try:
            if self.win is not None:
                self.win.destroy()
                self.win = None
        except Exception:
            pass
        save_ui_setting("float_ball_on", False)
        try:
            if getattr(self.app, "_menu_hidden", False):
                self.app._toggle_menubar()
        except Exception:
            pass

    def show_again(self):
        """★ 把球叫回来（「设置」菜单里有入口）。"""
        try:
            save_ui_setting("float_ball_on", True)
            if self.win is None:
                if self.build():
                    return True
        except Exception:
            pass
        return self.win is not None

    # ---------------- 实时数据（网速 / 硬盘 / 内存）----------------
    def _tick_stats(self):
        """★ 每秒：网速 + 内存（**纯 ctypes，不起进程，很轻**）。

        ★ 为什么用 ctypes 而不是命令：
          命令（typeperf）每次要**起一个进程**（实测 1.26 秒），
          每秒调一次界面就废了。ctypes 是**直接读内存**，几乎不花时间。
        """
        try:
            if self.win is None:
                return
            need = ("net" in self.show) or ("mem" in self.show)
            if need:
                if "net" in self.show:
                    t = _net_speed_text()
                    if t:
                        self._net_text = t
                if "mem" in self.show:
                    t = _mem_text()
                    if t:
                        self._mem_text = t
                # ★★★ 2026-10-08 修一个真 bug（账本里 1 次，但根因会反复咬）：
                #   **这里是"定时器回调"** —— 开头那句 `if self.win is None`
                #   只能挡住"进函数时球已经关了"；
                #   ★★ 挡不住"**跑的过程中球被关掉**"（读网速/内存要几毫秒，
                #      用户正好在这几毫秒里点了球上的"关掉这个球"）→
                #      `self.win` 变成 None → `_redraw()` 里
                #      `self.win.geometry(...)` 抛
                #      `AttributeError: 'NoneType' object has no attribute 'geometry'`。
                #   ★ 为什么难发现：这句在 `except: pass` 里，
                #     **连账本都不记**（只有 `_redraw` 内部的 note_swallowed 抓到）。
                #   → 判据：**定时器回调里，碰 Tk 之前要再确认一次"东西还在"**。
                if self.win is not None:
                    self._redraw()
        except Exception:
            pass
        try:
            if self.win is not None:
                self._stat_job = self.root.after(1000, self._tick_stats)
        except Exception:
            pass

    def _tick_disk(self):
        """★ 硬盘读写：**每 5 秒**一次（Windows 限制，只能慢点）。

        ★ 为什么要放**后台线程**：`typeperf` 一次要 1.26 秒 ——
          在主线程跑界面会**卡住一秒**（用户能看出来）。
          ★ 所以：线程去跑命令 → 结果塞进队列 → 主线程 200ms 后来取。
        """
        try:
            if self.win is None:
                return
            if "disk" in self.show and not getattr(self, "_disk_busy", False):
                self._disk_busy = True
                import threading

                def _worker():
                    txt = ""
                    try:
                        txt = _disk_speed_text()
                    except Exception:
                        txt = ""
                    self._disk_result = txt
                    self._disk_busy = False

                threading.Thread(target=_worker, daemon=True).start()
                # ★ 主线程延后来取结果（不阻塞界面）
                self.root.after(1600, self._collect_disk)
        except Exception:
            pass
        try:
            if self.win is not None:
                self._disk_job = self.root.after(6000, self._tick_disk)
        except Exception:
            pass

    def _collect_disk(self):
        try:
            # ★★ 2026-10-08：这也是**定时器回调**（`_tick_disk` 里 after 起的）——
            #   球可能在这 1.6 秒里被关掉 → `self.win` 已经是 None →
            #   `_redraw()` 里 `None.geometry(...)` 抛。
            #   ★ 判据同 `_tick_stats`：**碰 Tk 之前再确认一次"球还在"**。
            if self.win is None:
                return
            t = getattr(self, "_disk_result", "")
            if t and t != self._disk_text:
                self._disk_text = t
                if self.win is not None:
                    self._redraw()
        except Exception:
            pass

    # ---------------- 主题 ----------------
    def apply_theme(self):
        """★ 换皮肤时刷球的颜色（由主程序 `_apply_theme` 调）。"""
        try:
            if self.win is None:
                return
            self.win.configure(bg=theme_get("win_bg"))
            self._redraw()
        except Exception:
            pass

    def follows_root(self):
        """★ 主窗口挪动/缩放时，球跟着走（保持"相对位置"不变）。"""
        try:
            if self.win is None:
                return
            x, y = self._abs_pos()
            self.win.geometry("+%d+%d" % (x, y))
        except Exception:
            pass




# ---------- 兜底（★ 它会吃掉错误，所以要专门测"用的哪一份"）----------
def _fallback():
    g = globals()
    for _n in _NEED:
        if g.get(_n) is None:
            g[_n] = _Borrowed(_n)


_fallback()
