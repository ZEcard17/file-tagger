# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：TagBoxPicker。

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



    # ★★★ 2026-10-09 补齐协议（错题本 #185）★★★
    #   ★★ 原来缺 **比较大小**（`__lt__` 等四个）——
    #     真出过事：`app._idle_seconds() < IDLE_STOP_WITHIN_SEC`
    #     → `float < _Borrowed` →
    #     `TypeError: '<' not supported between instances of 'float' and '_Borrowed'`
    #   ★★★ 判据：**代理会被当成什么用，你猜不到** ——
    #     所以别一个个补，要**对着完整清单查一遍**
    #     （工具：`工具\代理协议检查.py`）。
    #   ★ 每次读都回主程序现取（`_v()`），所以「转给真值去做」最不容易错。


    def __rmul__(self, o):
            return o * self._v()


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


    def __round__(self, n=None):
            return round(self._v(), n) if n else round(self._v())


    def __abs__(self):
            return abs(self._v())


    def __next__(self):
            return next(self._v())


    def __neg__(self):
            return -self._v()


    def __pos__(self):
            return +self._v()


    def __invert__(self):
            return ~self._v()


    def __bytes__(self):
            return bytes(self._v())


    def __fspath__(self):
            return os.fspath(self._v())


    def __format__(self, spec):
            return format(self._v(), spec)


    def __copy__(self):
            return self._v()


    def __enter__(self):
            return self._v().__enter__()


    def __exit__(self, *a):
            return self._v().__exit__(*a)

_MISS = object()   # 哨兵：区分「取不到」和「取到 None」
_NEED = ['enable_wheel_scroll', 'note_swallowed']
_SIBLINGS = ['AutoNameRulesDialog', 'CategoryDialog', 'CategoryHiddenTagsDialog', 'CategoryItem', 'CategorySidebar', 'CategoryTagLinkDialog', 'PreviewPane', 'RemoveFileTagsDialog', 'ScanProgressDialog', 'ShortcutDialog', 'SimpleInputDialog', 'TagBoxGridDialog', 'TagBoxPicker', 'TagPickerDialog', 'UIScaleDialog']
_APP = None
enable_wheel_scroll = None
note_swallowed = None




# ==========================================================================
#  ★★★ 2026-10-08 **多语言**：模块里的界面文字也走 T() ★★★
#  --------------------------------------------------------------------------
#  ★ 为什么"向主程序要"（而不是自己 `from i18n import T`）：
#    · 那样**语言表就有两套**了 —— 用户切语言时可能**不同步**
#    · ★★ 统一"向主程序要"：**只有一处知道当前语言**（主程序的 i18n）
#    ★ 而本模块**已经有** `_need()`（向主程序借名字的通道），
#      所以这里**只是多要一个 `T`**，不引入新机制。
#
#  ★★ 为什么要有那个 `except` 兜底：
#    万一主程序还没接上（`_set_app` 没调），或者 `T` 取不到，
#    **也要返回原文**（能看），**不能报错**（界面上的字不该让程序崩）。
# ==========================================================================
def T(text, **kw):
    """★ 向主程序要翻译（取不到就返回原文 —— 界面永远能看）。"""
    try:
        f = _need("T")
        if f is not None:
            return f(text, **kw)
    except Exception:
        pass
    try:
        return str(text).format(**kw) if kw else str(text)
    except Exception:
        return str(text)

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

class TagBoxPicker(tk.Toplevel):
    """★ 补丁26：从「用得最多的标签」里勾选放进标签盒。"""

    def __init__(self, master, box):
        super().__init__(master)
        self.box = box
        self.store = box.store
        self.title("把标签放进标签盒")
        self.geometry("560x600")
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
                  foreground="#777").pack(anchor="w", pady=(0, 6))

        # ★ v25 补丁39（用户提的）：这个窗口**原来没有搜索框** —— 标签有
        #   两百多个，想找一个只能一行行往下翻，非常难用。现在加一个，
        #   边打边筛（按标签名，不区分大小写）。
        sbar = ttk.Frame(body)
        sbar.pack(fill="x", pady=(0, 6))
        ttk.Label(sbar, text=T("🔍 搜索标签：")).pack(side="left")
        self.search_var = tk.StringVar()
        _se = ttk.Entry(sbar, textvariable=self.search_var)
        _se.pack(side="left", fill="x", expand=True, padx=(4, 4))
        _se.focus_set()
        self.search_var.trace_add("write", lambda *a: self._load())
        ttk.Button(sbar, text=T("清除"), width=6,
                   command=lambda: self.search_var.set("")).pack(side="left")
        self.count_lbl = ttk.Label(body, text="", foreground="#16a085")
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
            note_swallowed("标签盒：读「用得最多的标签」失败", exc)
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
                      foreground="#999").pack(anchor="w", pady=6)

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


