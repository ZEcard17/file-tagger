# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「导航」这组方法。

★★★ 搬法（跟"搬独立类"不同）：方法体搬来，`def xxx(self)` 改成
   `def xxx(app)`，函数体里 `self.` 全换成 `app.`，其余一个字不改。
   主类里**留一行同名转发** → 所有调用方不用改（稳定接口）。
"""

import os
import re
import sys
import time

import tkinter as tk
from tkinter import ttk, messagebox, filedialog


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


_MISS = object()
_NEED = ['T', 'note_swallowed']
_APP = None


def _set_app(app):
    """主程序启动时把「自己」交进来。"""
    global _APP
    _own = __file__
    _APP = app
    _fill()
    globals()["__file__"] = _own


def _fill():
    """★★★ 一律装成代理（错题本 #168 v3）—— 读的时候才现取。"""
    if _APP is None:
        return
    g = globals()
    for _n in _NEED:
        try:
            g[_n] = _Borrowed(_n)
        except Exception:
            pass


def _fallback():
    g = globals()
    for _n in _NEED:
        if g.get(_n) is None:
            g[_n] = _Borrowed(_n)


_fallback()


def go_back(app):
    """后退（Alt+←）。"""
    app._nav_to_pos(getattr(app, "_nav_pos", 0) - 1)


def go_forward(app):
    """前进（Alt+→）。"""
    app._nav_to_pos(getattr(app, "_nav_pos", 0) + 1)


def go_up(app):
    parent = app.current_dir.parent
    if parent != app.current_dir:
        app.load_directory(parent)


def navigate_to_path(app, path):
    """★★ 2026-01-26：文件树节点双击 → 跳转到对应目录

    ★★ 2026-10-04 修复（小马留下的坑）：它自己拼了一份「跳转」流程，
      可是**拼错了两个地方** —— 双击目录树里的目录，文件列表**出不来内容**：
        · `app.current_dir` 没更新（程序别的地方都认这个属性，
          不更新的话「当前在看哪个文件夹」还是老地方）；
        · `app._view_spec` 写成了 {"kind": "dir", "dir": path}，
          可是程序里别处一律用 **"path"** 这个键 —— 键名不对，
          下一页就取不到目录、列表一直是空的。
        · 也没做「上一次还在跑的搜索要作废」等收尾（_load_directory 里都有）。
      现在直接**转交给正规的 load_directory()** —— 双击目录树
      就和在文件列表里双击文件夹、或在地址栏敲路径**完全一样**。
    """
    if not path or not os.path.isdir(path):
        return
    try:
        app.load_directory(str(path))
    except Exception as _e:
        note_swallowed(T("从文件目录树跳转失败"), _e)


def _nav_record(app, path):
    """走了一个新目录 → 记进历史（后退/前进用）。"""
    try:
        p = str(path)
    except Exception:
        return
    if getattr(app, "_nav_hist", None) is None:
        app._nav_hist = []
        app._nav_pos = -1
    # 正在「后退/前进」的路上，就不要再记一遍
    if getattr(app, "_nav_going", False):
        return
    if app._nav_pos >= 0 and app._nav_hist[app._nav_pos] == p:
        return
    app._nav_hist = app._nav_hist[:app._nav_pos + 1]
    app._nav_hist.append(p)
    if len(app._nav_hist) > 60:
        app._nav_hist = app._nav_hist[-60:]
    app._nav_pos = len(app._nav_hist) - 1
    app._update_nav_buttons()


def _nav_to_pos(app, pos):
    hist = getattr(app, "_nav_hist", []) or []
    if not (0 <= pos < len(hist)):
        return
    app._nav_pos = pos
    app._nav_going = True
    try:
        app.load_directory(hist[pos])
    finally:
        app._nav_going = False
    app._update_nav_buttons()


def _update_nav_buttons(app):
    try:
        hist = getattr(app, "_nav_hist", []) or []
        pos = getattr(app, "_nav_pos", -1)
        app._nav_back_btn.state(["!disabled"] if pos > 0 else ["disabled"])
        app._nav_fwd_btn.state(
            ["!disabled"] if pos < len(hist) - 1 else ["disabled"])
    except Exception:
        pass


def choose_dir(app):
    chosen = filedialog.askdirectory(initialdir=str(app.current_dir))
    if chosen:
        app.load_directory(chosen)


# ---------------- ★ v25 补丁13：导航（后退/前进/盘符/常用位置）----------------
@staticmethod
def _clean_path_input(text):
    """地址栏里手输的路径：去掉引号/空格，如果给的是文件就进它所在的文件夹。

    （从资源管理器复制路径过来常常带一对引号，或者直接粘的是一个文件路径。）
    """
    t = (text or "").strip().strip('"').strip("'").strip()
    if not t:
        return t
    try:
        if os.path.isfile(t):
            return os.path.dirname(t)
    except Exception:
        pass
    return t
