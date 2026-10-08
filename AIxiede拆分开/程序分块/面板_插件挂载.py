# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「插件挂载」这组方法。

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


# ======================================================================
#  ★★★ 2026-10-08：**插件菜单**（用户要"配合插件入口"）
# ======================================================================
# ==========================================================================
#  ★★★ 要向主程序借的名字（★ 搬方法组的**关键**，错题本 #166）★★★
#  --------------------------------------------------------------------------
#  ★ 搬走的方法用了一堆**主程序自己造的东西**（`theme_get` / `T` / 常量…）。
#    这些**新文件里没有** → ★★ 一调那个方法就 `NameError` ——
#    而且**平时看不出来**（只有真点到那个按钮才炸）。
#  ★ 做法跟拆类一样：主程序启动时把「自己」交进来（`_set_app`）。
# ==========================================================================
_MUTABLE = []
_NEED = ['T', 'note_swallowed', 'plugin_menu_entries', 'plugin_menu_items']
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


def _attach_plugin_menus(app):
    """★ 把插件想加的菜单**挂到主菜单上**（"问表要东西"）。

    ★ 为什么是一个单独的方法（而不是塞在 `_build_menu` 里）：
      `_build_menu` 跑在**插件加载之前**（菜单要先生出来，
      插件才能往上挂）—— 所以**加载完插件后要再挂一次**。
      ★ 这也是"预留入口"的做法：**主程序不认识任何插件**，
        只是"问 `plugin_menu_entries()` 要一份清单，照着挂"。

    ★ 什么时候被调：
      ① 启动、插件加载完之后（见 `__init__`）
      ② 以后如果做"运行时启用插件"，再来一遍就行

    ★ 每一块单独 try —— 一个插件菜单挂失败，不影响别的、也不影响主程序。
    """
    try:
        # ---- ① 插件要的**顶层菜单** ----
        for pname, label, items in plugin_menu_entries():
            try:
                sub = tk.Menu(app.menubar, tearoff=0)
                for it in (items or []):
                    try:
                        if it is None:
                            sub.add_separator()
                            continue
                        text, cmd = it
                        sub.add_command(label=str(text), command=cmd)
                    except Exception:
                        pass
                if sub.index("end") is None:
                    continue        # 空的就不挂（免得点开一片空白）
                app.menubar.add_cascade(label=str(label), menu=sub)
            except Exception as _e:
                note_swallowed(T("挂插件菜单「{x}」失败", x=pname), _e)
        # ---- ①.5 ★ 插件可能注册了**自己的皮肤** → 把皮肤菜单重刷一遍 ----
        #   ★ 为什么需要（实测踩的）：
        #     皮肤菜单是**建菜单时**列一遍的，那会儿插件**还没加载**，
        #     它注册的配色**列不出来**（实测：进了 `_THEMES`，菜单里却没有）。
        #     ★ 虽然我给它挂了 `postcommand`（每次点开重列），
        #       但**这里再刷一次更稳** —— 万一 `postcommand` 在某些
        #       Tk 版本上不灵，这里也兜住了。
        #     ★ "两处都做"是刻意的：用户要的就是"留冗余、方便以后改"。
        try:
            _tm = getattr(app, "_theme_menu", None)
            if _tm is not None:
                app._fill_theme_menu(_tm)
        except Exception:
            pass
        # ---- ② 插件要"插进已有菜单"的项 ----
        #   ★ 按菜单名找：主菜单里 cget("label") 等于它的那个
        for pname, mlabel, ilabel, cmd in plugin_menu_items():
            try:
                target = None
                n = app.menubar.index("end")
                if n is None:
                    continue
                for i in range(n + 1):
                    try:
                        if str(app.menubar.entrycget(i, "label")) == str(mlabel):
                            target = app.menubar.nametowidget(
                                app.menubar.entrycget(i, "menu"))
                            break
                    except Exception:
                        continue
                if target is None:
                    # ★ 找不到那个菜单 → 就加到主菜单最外层（别把插件吃掉）
                    app.menubar.add_command(label=str(ilabel), command=cmd)
                else:
                    target.add_separator()
                    target.add_command(label=str(ilabel), command=cmd)
            except Exception as _e:
                note_swallowed(T("插插件菜单项「{x}」失败", x=pname), _e)
    except Exception as _e:
        note_swallowed(T("挂插件菜单失败"), _e)


# ========== ★★ 2026-10-05「先加说话」：出错必留痕 ==========
def _install_error_spy(app):
    """装一道「出错必留痕」的保险。

    用户抱怨的三件事——卡死 / 显示不全 / 改着改着功能没了——
    查下来根子之一是程序里 624 处 `except Exception: pass`
    （出错装没事）。它们不可能一条条手改，所以这里装两手「探照灯」：

    ● ① **后台线程**里没被抓住的出错
          线程一崩，界面还在那儿好好地转 —— 用户看到的就是「卡死」。
          以前这种错**完全没人知道**。现在会记进「问题」面板。
    ● ② **界面回调**里没被抓住的出错
          点按钮、画列表这类回调出错，以前也是悄悄没了。

    ★ 三条铁律（很重要，别破坏）：
      1. **只记一笔，绝不改变原有行为** —— 原 hook 该调还调；
      2. **自己绝不能再抛异常** —— 全程 try 包住，出问题就闭嘴；
      3. **不拖慢程序** —— 只在真出错时才干活，平时零开销。
    """
    if getattr(app, "_error_spy_on", False):
        return
    app._error_spy_on = True

    # ---------- ① 后台线程的兜底 ----------
    try:
        _old_hook = threading.excepthook

        def _thread_hook(args):
            try:
                tname = getattr(args.thread, "name", "?")
                note_swallowed(
                    f"后台线程「{tname}」出错了（界面可能因此没反应）",
                    args.exc_value if args.exc_value is not None
                    else RuntimeError(str(args.exc_type)),
                    level="error")
            except Exception:
                pass
            try:
                _old_hook(args)
            except Exception:
                pass

        threading.excepthook = _thread_hook
    except Exception:
        pass

    # ---------- ② 界面回调的兜底 ----------
    # ★★★ 2026-10-05 **回退了这一手，别再装回来** ★★★
    #   教训（实测踩到的）：以前这里写了
    #       _old_report = tk.Tk.report_callback_exception
    #       tk.Tk.report_callback_exception = _new_report
    #   本意是「界面回调出错也能留痕」，结果**装上去之后
    #   分栏条拖不动了**——用户原话「现在直接没法拖动区域了」。
    #   原因：这是**替换 Tk 全局的出错处理**，等于在所有窗口的
    #   事件路上多拐了一道；这台机器上 Tk 的鼠标事件本来就敏感
    #   （见文件开头「鼠标事件 state 的 0x8 不是 Alt」那条实测），
    #   多拐一道就把拖拽打断了。
    #   ★ 结论：**不要在 Tk 全局上动手脚**。界面出错要留痕，
    #     改用别的路子（局部登记 / 后台线程兜底），绝不碰全局。
    #   只保留下面 ① 后台线程兜底 —— 那个是线程级的，不碰界面，
    #   实测不影响任何交互。
    pass

    # ---------- ③ 开机做个轻轻的体检 ----------
    try:
        app.root.after(1500, app._startup_health_check)
    except Exception:
        pass
