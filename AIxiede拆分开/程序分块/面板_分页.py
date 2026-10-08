# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「分页」这组方法。

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
_NEED = ['FILE_PAGE_SIZE', 'Path', 'T']
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
                g[_n] = _Borrowed(_n) if _n in _MUTABLE else _v
        except Exception:
            pass


# ---------- 兜底（★ 它会吃掉错误，所以要专门测"用的哪一份"）----------
def _fallback():
    g = globals()
    for _n in _NEED:
        if g.get(_n) is None:
            g[_n] = _Borrowed(_n)


_fallback()


def _load_current_page(app):
    """根据 _view_spec 载入当前页的数据。"""
    spec = app._view_spec
    if not spec:
        return
    kind = spec.get("kind")
    ps = FILE_PAGE_SIZE
    pg = app._page

    try:
        if kind == "dir":
            all_paths = spec.get("all_paths") or []
            total = len(all_paths)
            page_paths = all_paths[pg * ps:(pg + 1) * ps]
            with_loc = False
        elif kind == "all":
            total = app.store.all_files_count()
            page_paths = app.store.all_files_page(ps, pg * ps)
            with_loc = True
        elif kind == "cat":
            cid = spec["cid"]
            total = app.store.files_in_category_count(cid)
            page_paths = app.store.files_in_category_page(
                cid, ps, pg * ps)
            with_loc = True
        elif kind == "paths":
            all_paths = spec.get("paths") or []
            total = len(all_paths)
            page_paths = all_paths[pg * ps:(pg + 1) * ps]
            with_loc = True
        else:
            return
    except Exception as exc:
        app.set_status(f"载入失败：{exc}")
        app.log_problem(f"载入页面失败（{kind}）：{exc}",
                         level="error")
        return

    spec["total"] = total
    app._page_total = total

    app._populate_paths_page(page_paths, with_location=with_loc)
    app._update_page_ui()


def _populate_paths_page(app, paths, with_location=True):
    """只载入一页文件（不做全量查询、不做全量标签）
       ★ 不 stat 任何文件（网盘 stat 会走网络，几秒就卡住了）"""
    # ★ v22：自动打标签已改成「手动启动」。
    #   打开文件夹 / 打开分类库时，这里不再自动跑自动标签规则；
    #   只有点工具栏的「🏷 重读标签」（或菜单「🏷 重读标签…」）
    #   才会按「自动标签规则」把标签更新一遍。
    #   v21 及以前这里是受 auto_scan_on_open 控制的自动扫描，现在已取消。

    try:
        tag_map = app.store.tags_for_paths(paths)
    except Exception:
        tag_map = {}

    spec = app._view_spec or {}
    entries_map = spec.get("entries_map") or {}

    # ★ 目录视图：直接用 entries_map
    #   其他视图：批量从 dir_cache 表查一次（纯 SQLite，不碰磁盘）
    dir_meta_lookup = {}
    if not entries_map:
        try:
            dir_meta_lookup = app.store.lookup_paths_meta(paths)
        except Exception:
            dir_meta_lookup = {}

    rows = []
    for p in paths:
        path = Path(p)
        name = path.name
        is_dir = False
        size = "?"
        size_bytes = None

        meta = entries_map.get(name)
        if meta is None:
            meta = dir_meta_lookup.get(p)

        if meta is not None:
            is_dir = meta[0]
            if is_dir:
                size = ""
                size_bytes = -1
            else:
                sz = meta[1]
                if sz is not None:
                    size_bytes = sz
                    size = app.human_size(sz)
                else:
                    size = "?"
        else:
            # ★ 完全没缓存：按文件名猜，绝不 stat
            is_dir = ("." not in name)
            if is_dir:
                size = ""
                size_bytes = -1
            else:
                size = "?"
                size_bytes = None

        rows.append({
            "path": p,
            "name": name,
            "kind": "文件夹" if is_dir else app.file_kind(name),
            "size": size,
            "size_bytes": size_bytes,
            "location": str(path.parent) if with_location else "",
            "tags": tag_map.get(p, []),
        })
    app._base_rows = rows
    app._refresh_file_list_from_base()


def _update_page_ui(app):
    try:
        total = app._page_total or 0
        ps = FILE_PAGE_SIZE
        n_pages = max(1, (total + ps - 1) // ps)
        page_disp = app._page + 1
        if total == 0:
            app.page_info_lbl.config(text=T("共 0 项"))
        else:
            app.page_info_lbl.config(
                text=T("第 {a} / {b} 页    共 {c} 项",
                                              a=page_disp, b=n_pages, c=total))
        if app._page <= 0:
            app.page_prev_btn.state(["disabled"])
        else:
            app.page_prev_btn.state(["!disabled"])
        if app._page >= n_pages - 1:
            app.page_next_btn.state(["disabled"])
        else:
            app.page_next_btn.state(["!disabled"])
    except Exception:
        pass


def _page_prev(app):
    if app._page <= 0:
        return
    app._page -= 1
    app._load_current_page()


def _page_next(app):
    ps = FILE_PAGE_SIZE
    total = app._page_total or 0
    n_pages = max(1, (total + ps - 1) // ps)
    if app._page >= n_pages - 1:
        return
    app._page += 1
    app._load_current_page()


def _page_jump(app):
    try:
        n = int((app.page_jump_var.get() or "").strip())
    except Exception:
        return
    ps = FILE_PAGE_SIZE
    total = app._page_total or 0
    n_pages = max(1, (total + ps - 1) // ps)
    n = max(1, min(n_pages, n))
    app._page = n - 1
    app._load_current_page()
