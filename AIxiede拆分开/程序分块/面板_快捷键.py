# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「快捷键」这组方法。

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


# ---------- ★ v25 补丁25：快捷键（可自定义） ----------
# ==========================================================================
#  ★★★ 要向主程序借的名字（★ 搬方法组的**关键**，错题本 #166）★★★
#  --------------------------------------------------------------------------
#  ★ 搬走的方法用了一堆**主程序自己造的东西**（`theme_get` / `T` / 常量…）。
#    这些**新文件里没有** → ★★ 一调那个方法就 `NameError` ——
#    而且**平时看不出来**（只有真点到那个按钮才炸）。
#  ★ 做法跟拆类一样：主程序启动时把「自己」交进来（`_set_app`）。
# ==========================================================================
_MUTABLE = []
_NEED = ['SHORTCUT_DEFS', 'T', 'load_shortcut_map', 'note_swallowed', 'shortcut_key_to_seq']
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


def _shortcut_actions(app):
    """动作键 → 具体干什么。这里是唯一把「名字」和「功能」连起来的地方。"""
    return {
        "delete": app.on_delete_key,
        "rename": app.on_rename_key,
        "select_all": app.on_select_all_key,
        "new_folder": app.on_new_folder_key,
        "copy": app.on_copy_key,
        "cut": app.on_cut_key,
        "paste": app.on_paste_key,
        "undo": app.on_undo_key,
        "nav_back": app.on_nav_back_key,
        "nav_forward": app.on_nav_forward_key,
        "toggle_tagbar": lambda e=None: app.toggle_tagbar(),
        "toggle_preview": lambda e=None: app.toggle_preview(),
        "toggle_taglib": lambda e=None: app.toggle_taglib(),
        "net_mode": lambda e=None: app.toggle_net_browse(),
        "refresh": lambda e=None: app.refresh_current_dir(),
        "search_focus": lambda e=None: app._focus_search_entry(),
        "quick_preview": app.on_quick_preview_key,
    }


def _setup_shortcuts(app):
    """第一次绑定：把设置里的按键按上。"""
    app._apply_shortcuts(first=True)


def _apply_shortcuts(app, first=False):
    """★ 补丁25：按当前的快捷键表重新绑定（改完立刻生效，不用重启）。

    先把上一次绑的**解绑**，再按新表绑 —— 否则改过的键会「新旧一起
    能用」，冲突起来很莫名其妙。
    """
    acts = app._shortcut_actions()
    # 1) 解绑上一次
    for name, seqs in list(getattr(app, "_shortcut_binds", {}).items()):
        cb = acts.get(name)
        for s in seqs:
            try:
                app.root.unbind(s)
            except Exception:
                pass
    app._shortcut_binds = {}
    # 2) 按表重新绑
    smap = load_shortcut_map()
    n_ok = 0
    _failed = []          # ★ 2026-10-06：绑不上的都攒着，最后一起告诉用户
    for name, label, _default in SHORTCUT_DEFS:
        key = smap.get(name, "")
        cb = acts.get(name)
        if not key or cb is None:
            continue
        seqs = shortcut_key_to_seq(key)
        bound = []
        for s in seqs:
            try:
                app.root.bind(s, cb, add="+")
                bound.append(s)
                n_ok += 1
            except Exception as exc:
                try:
                    note_swallowed(T("快捷键：绑定 {x}（{y}）失败", x=key, y=label),
                                   exc)
                except Exception:
                    pass
        if bound:
            app._shortcut_binds[name] = bound
        else:
            _failed.append("%s（%s）" % (label, key))
    # ★★ 2026-10-06：**绑不上要告诉用户**，不能只记进账本。
    #   踩的坑：用户报「按空格没反应」，而账本里早就写着
    #   「绑定 Space 失败」—— 但**用户根本不知道去哪儿看**，
    #   于是这个功能从做完那天起就是坏的，谁也没发现。
    #   ★ 只在**第一次**（first=True）弹，免得改一次快捷键就弹一次。
    if _failed and first:
        try:
            app.root.after(1200, lambda: messagebox.showwarning(
                "有快捷键没设上",
                "下面这些快捷键在这个系统上用不了（其它功能不受影响）：\n\n  "
                + "\n  ".join(_failed[:8])
                + "\n\n你可以在「界面 → ⌨ 快捷键管理…」里换一个键。",
                parent=app.root))
        except Exception:
            pass
    if not first:
        try:
            app.log_output(T("快捷键已重新绑定（共 {x} 个按键）", x=n_ok))
        except Exception:
            pass
    return n_ok
