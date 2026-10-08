# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：UIScaleDialog。

★ 代码**原样搬运**，一个字没改，只是换了个文件放。

★★ 拆文件的规矩（所有分块文件都照这个写）★★
   ① **Python 自带的东西直接 import**（tk、ttk、os、sys…）——不绕弯。
   ② **只有主程序自己造的东西才向主程序借**（FONT、note_swallowed 这类）。
      而且**不在开头 import 主程序**——两边互相 import 会让 Python
      报错、程序打不开。借法是主程序启动时把「自己」交进来（_set_app）。
   ③ 借来的名字做成**模块级变量**，这样下面的代码**一个字都不用改**。
   ④ 借不到就用兜底值，**不能因为主程序改了个名字就整个打不开**。
"""

import os
import sys
import time
import threading
import queue

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, colorchooser

# ---------- 要向主程序借的名字（先占位，挂上后填真身） ----------
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



_MISS = object()   # 哨兵：区分「取不到」和「取到 None」
_NEED = ['BOLD', 'DEFAULT_UI_SCALE', 'FONT', 'MAX_UI_SCALE', 'MIN_UI_SCALE', 'UI_FONT_SIZE']
_SIBLINGS = ['AutoNameRulesDialog', 'CategoryDialog', 'CategoryHiddenTagsDialog', 'CategoryItem', 'CategorySidebar', 'CategoryTagLinkDialog', 'PreviewPane', 'RemoveFileTagsDialog', 'ScanProgressDialog', 'ShortcutDialog', 'SimpleInputDialog', 'TagBoxGridDialog', 'TagBoxPicker', 'TagPickerDialog', 'UIScaleDialog']
_APP = None
BOLD = None
DEFAULT_UI_SCALE = None
FONT = None
MAX_UI_SCALE = None
MIN_UI_SCALE = None
UI_FONT_SIZE = None


def _set_app(app):
    """主程序启动时调一下：把「自己」交进来，顺便把要借的名字填上。"""
    global _APP
    _APP = app
    _fill()
    _link_siblings()


def _fill():
    """从主程序身上把需要的名字取过来，填进本模块的同名变量。"""
    if _APP is None:
        return
    g = globals()
    for _n in _NEED:
        try:
            # ★★★ 用哨兵 + 代理（错题本 #168）
            # ★★★ 无条件装上代理（错题本 #168 v3）：
            #   当时**没有这个值**（主程序还没定义到那一行）也照样装 ——
            #   代理是**读的时候**才回主程序取，所以什么时候定义都不影响。
            #   ★ 这就是"代理"和"快照"的根本区别：
            #     快照必须"当场有"，代理只要"用的时候有"。
            g[_n] = _Borrowed(_n)
        except Exception:
            pass





# ---------- 「兄弟文件互相认识」 ----------
def _link_siblings():
    """去同一批拆出来的兄弟文件里，找本文件用到的类。

    ★ 为什么需要：拆出来之后，有的类要用别的拆出来的类
      （比如 CategorySidebar 要用 CategoryItem）。
      原来它们都在一个大文件里，随便用；拆开后就得互相找一下。
    ★ ★ 正确做法：**把每个兄弟文件都试着导入一遍**，然后看它有没有
      本文件缺的类。找不到也不报错（万一那个文件没拆过来，不影响别的）。
    """
    try:
        import importlib
        g = globals()
        my = __name__
        for _sib in _SIBLINGS:
            if _sib == my:
                continue
            # 本文件已经用过这个类了吗（值为 None 说明还没填）
            if g.get(_sib, "缺") is not None and g.get(_sib, "缺") != "缺":
                continue
            try:
                _m = importlib.import_module(_sib)
            except Exception:
                continue
            _cls = getattr(_m, _sib, None)
            if _cls is not None:
                g[_sib] = _cls
    except Exception:
        pass

def _grab(name, default=None):
    """临时借一个名字（借不到用 default）。"""
    if _APP is not None:
        v = getattr(_APP, name, None)
        if v is not None:
            return v
    return default


def _ensure():
    """保证借来的名字都有值（第一次用到时兜一下）。"""
    global _APP
    if _APP is None:
        # 还没挂上 —— 试着从「已经在跑的主程序」那儿拿（通常拿得到）
        try:
            import sys as _s
            for _m in list(_s.modules.values()):
                if _m is not None and getattr(_m, '__name__', '') == 'AIxiede':
                    _set_app(_m)
                    break
        except Exception:
            pass
    else:
        _fill()
    _link_siblings()
    _link_siblings()
    _link_siblings()

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

        ttk.Label(body, text="选择界面缩放比例：",
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
        ttk.Label(custom_row, text="自定义：").pack(side="left")
        e = ttk.Entry(custom_row, textvariable=self.custom_var, width=8)
        e.pack(side="left")
        ttk.Label(custom_row,
                  text=f"（{int(MIN_UI_SCALE*100)}% ~ {int(MAX_UI_SCALE*100)}%）",
                  foreground="#888").pack(side="left", padx=6)

        self.custom_var.trace_add("write", self._on_custom_change)

        ttk.Separator(body).pack(fill="x", pady=10)
        ttk.Label(
            body,
            text="提示：改完后点「确定」，会提示你重启程序。\n"
                 "重启后所有字体、行高、按钮都会按新比例显示。",
            foreground="#666", justify="left").pack(anchor="w")

        btns = ttk.Frame(body)
        btns.pack(fill="x", pady=(14, 0))
        ttk.Button(btns, text="确定", command=self._ok).pack(side="right")
        ttk.Button(btns, text="取消", command=self._cancel).pack(side="right", padx=6)
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
#  主应用
# ==========================================================================
