# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「撤销」这组方法。

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
_MUTABLE = []
_NEED = ['T', '_undo_label', '_面板文件操作', 'note_swallowed']
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



    # ★★★ 2026-10-09 补齐协议（错题本 #185）★★★
    #   ★★ 原来缺 **比较大小**（`__lt__` 等四个）——
    #     真出过事：`app._idle_seconds() < IDLE_STOP_WITHIN_SEC`
    #     → `float < _Borrowed` →
    #     `TypeError: '<' not supported between instances of 'float' and '_Borrowed'`
    #   ★★★ 判据：**代理会被当成什么用，你猜不到** ——
    #     所以别一个个补，要**对着完整清单查一遍**
    #     （工具：`工具\代理协议检查.py`）。
    #   ★ 每次读都回主程序现取（`_v()`），所以「转给真值去做」最不容易错。


    def __lt__(self, o):
            return self._v() < o


    def __le__(self, o):
            return self._v() <= o


    def __gt__(self, o):
            return self._v() > o


    def __ge__(self, o):
            return self._v() >= o


    def __mul__(self, o):
            return self._v() * o

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


def _undo_init(app, *a, **k):
    # ★★ 转发到 `AIxiede拆分开/程序分块/面板_文件操作.py`
    #   ★ 保留同名方法 = **所有调用方不用改**（稳定接口）
    return _面板文件操作._undo_init(app, *a, **k)


def _undo_save_soon(app, *a, **k):
    # ★★ 转发到 `AIxiede拆分开/程序分块/面板_文件操作.py`
    #   ★ 保留同名方法 = **所有调用方不用改**（稳定接口）
    return _面板文件操作._undo_save_soon(app, *a, **k)


def undo_record(app, *a, **k):
    # ★★ 转发到 `AIxiede拆分开/程序分块/面板_文件操作.py`
    #   ★ 保留同名方法 = **所有调用方不用改**（稳定接口）
    return _面板文件操作.undo_record(app, *a, **k)


def undo_do(app):
    """★ 按 Ctrl+Z：把最后一条反着执行一遍。**要告诉用户撤了什么。**"""
    try:
        if not app._undo_stack:
            app.set_status(T("没有可以撤销的操作了"))
            return
        rec = app._undo_stack[-1]
    except Exception:
        return
    kind = rec.get("kind")
    items = rec.get("items") or []
    label = _undo_label(rec)
    try:
        res = app._undo_apply(kind, items)
        # ★ 兼容两种返回：新的三元组 / 老的二元组
        if isinstance(res, tuple) and len(res) >= 3:
            ok, msg, failed = res[0], res[1], (res[2] or [])
        else:
            ok, msg, failed = res[0], res[1], []
    except Exception as _e:
        note_swallowed(T("撤销失败"), _e)
        messagebox.showwarning("撤销没成功",
                               "这一步没能撤销：\n\n%s" % _e,
                               parent=app.root)
        return
    if not ok:
        # ★ 撤不了就**如实说**，并且把这条从记录本里拿掉
        #   （免得用户每次按都失败，以为是程序坏了）
        app._undo_stack.pop()
        app._undo_save_soon()
        app._undo_update_btn()
        messagebox.showwarning(
            "撤销没成功",
            "这一步撤不回来了。\n\n%s\n\n"
            "（已经把它从「可撤销」列表里去掉，免得每次按都失败）" % msg,
            parent=app.root)
        app.set_status(T("撤销失败：{x}", x=msg))
        app.log_problem(T("撤销失败：{x}（{y}）", x=label, y=msg), level="warn")
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
                parent=app.root)
        except Exception:
            pass
        try:
            app.log_problem(
                "撤销只成功一部分：%s —— 失败项：%s"
                % (label, "；".join(str(x) for x in failed[:5])),
                level="warn")
        except Exception:
            pass
        # 半成功：挪进重做栈没意义（还有东西没回来），直接丢掉这条
        app._undo_stack.pop()
        app._undo_save_soon()
        app._undo_update_btn()
        app.set_status(T("已撤销（部分）：{x}", x=msg))
        return
    # 成功：从「可撤销」挪到「可重做」
    app._undo_stack.pop()
    app._undo_redo_stack.append(rec)
    app._undo_save_soon()
    app._undo_update_btn()
    if msg:
        app.set_status(T("已撤销：{x}（{y}）", x=label, y=msg))
    else:
        app.set_status(T("已撤销：{x}", x=label))
    try:
        app.log_output(T("↶ 已撤销：{x}", x=label))
    except Exception:
        pass


def _undo_apply(app, *a, **k):
    # ★★ 转发到 `AIxiede拆分开/程序分块/面板_文件操作.py`
    #   ★ 保留同名方法 = **所有调用方不用改**（稳定接口）
    return _面板文件操作._undo_apply(app, *a, **k)


def _undo_update_btn(app, *a, **k):
    # ★★ 转发到 `AIxiede拆分开/程序分块/面板_文件操作.py`
    #   ★ 保留同名方法 = **所有调用方不用改**（稳定接口）
    return _面板文件操作._undo_update_btn(app, *a, **k)


def on_undo_key(app, event=None):
    """Ctrl+Z 的入口（在输入框里打字时不抢键）。"""
    try:
        if app._focus_is_input():
            return None
    except Exception:
        pass
    app.undo_do()
    return "break"
