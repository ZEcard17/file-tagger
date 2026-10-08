# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「统计显示」这组方法。

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
_NEED = ['T', 'note_swallowed', 'theme_get']
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
            _v = getattr(_APP, _n, None)
            if _v is not None:
                # ★★★ 一律包代理（错题本 #168）：
                #   模块的桩可能跑在**主程序还没定义这个名字**之前，
                #   所以「启动时取快照」必然借不到。
                #   ★ 代理是**读的时候才现取**，什么时候定义都不影响。
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


def _retheme_stats_labels(app):
    """把「文件 / 共 N / 未打标签 N / 仅中间标签 N」那一排的颜色刷成当前皮肤。

    ★★ 2026-10-07 新增。为什么要单独立一个方法：
      这排标签是**主界面最常瞄到**的几个字（每次看列表都在），
      但它们的颜色以前是**写死的**（"#555" / 深红 / 深黄），
      而且**没登记进换皮肤流程** —— 于是：
        · 夜间模式下"共 N"是深灰，**看不太见**
        · 切皮肤后它们**不跟着变**（用户说的"有时候黑了，东点西点又好了"）
      ★ 这跟错题本 #70（rowheight 写死 22）是同一类病根：
        **写死 + 漏登记**。凡是"自己指定颜色"的控件，都要问两句：
          ① 颜色是 theme_get 取的吗？  ② 换皮肤时会重刷吗？
    """
    for nm, key in (("stat_total_lbl", "fg"),
                    ("stat_untagged_lbl", "danger"),
                    ("stat_mid_lbl", "warn")):
        w = getattr(app, nm, None)
        if w is None:
            continue
        try:
            col = theme_get(key)
            # ttk.Label 用 configure(foreground=)，tk.Label 用 config(fg=)
            try:
                w.configure(foreground=col)
            except Exception:
                w.configure(fg=col)
            # ★ tk.Label 还得自己改底色（ttk 的不需要）
            try:
                w.configure(background=theme_get("panel_bg"))
            except Exception:
                pass
        except Exception as _e:
            try:
                note_swallowed(T("换皮肤：刷统计标签失败（{x}）", x=nm), _e,
                               quiet=True)
            except Exception:
                pass
    # 列表标题「文件」两个字是 ttk.Label，跟着主题走，这里不用管


def _safe_list_title(app, text):
    """★ 补丁37：标题里**绝不能以省略号结尾**。

    实测过：标题文本以「…」结尾时，Tk 会把整个标签当成「竖直书写」——
    控件请求尺寸会变成 4 像素宽、几百万像素高，把文件列表挤成 1 像素；
    而 1 像素的画布收不到鼠标事件 → 单击选不中文件。
    所以标题里统一把结尾的省略号去掉。
    """
    try:
        t = str(text or "")
        while t and t[-1] in "…⋯":
            t = t[:-1]
        return t.rstrip() or "文件"
    except Exception:
        return "文件"


def _apply_stats_display(app):
    """把「共 N 个 / 未打标签 N / 仅中间标签 N」这几个数字刷到界面上。

    ★★ v26：**这里以前每点一次文件都要重算一遍 800 个文件的标签统计。**
      实测（图本分类 800 行）：`tag_stats_for_paths` 一次要 0.04 秒左右，
      而它是**跟着 `on_file_select` 走的** —— 也就是说
      **你每点一个文件、每框选一次，它都要跑一遍**。
      一屏点十几下就攒出明显的卡顿感。
      ★ 关键：这几个数字只跟「当前列表里有哪些文件」有关，
        **跟你选中了哪个文件完全没关系**。
        所以这里缓存上一次的结果（用文件列表的指纹判断），
        列表没变就直接用缓存，一点活都不干。
    """
    paths = [r["path"] for r in app._base_rows]
    if not paths:
        app.stat_total_lbl.config(text="")
        app.stat_untagged_lbl.config(text="")
        app.stat_mid_lbl.config(text="")
        app._stats_cache_key = None
        return
    key = (len(paths), paths[0], paths[-1])
    cached = getattr(app, "_stats_cache", None)
    if cached is not None and getattr(app, "_stats_cache_key", None) == key:
        total, untagged, mid_only = cached
    else:
        total, untagged, mid_only = app.store.tag_stats_for_paths(paths)
        app._stats_cache = (total, untagged, mid_only)
        app._stats_cache_key = key
    if app.stats_filter == "untagged":
        app.stat_total_lbl.config(text=T("共 {n}    【仅显示未打标签】", n=total))
    elif app.stats_filter == "mid_only":
        app.stat_total_lbl.config(
        text=T("共 {n}    【仅显示仅中间标签】", n=total))
    else:
        app.stat_total_lbl.config(text=T("共 {n} 项", n=total))
    app.stat_untagged_lbl.config(
        text=T("未打标签 {n}", n=untagged) if untagged else "")
    app.stat_mid_lbl.config(
        text=f"仅中间标签 {mid_only}" if mid_only else "")


def toggle_stats_filter(app, mode):
    if app.stats_filter == mode:
        app.stats_filter = None
    else:
        app.stats_filter = mode
    app._refresh_file_list_from_base()


def _clear_stats_filter(app):
    app.stats_filter = None
