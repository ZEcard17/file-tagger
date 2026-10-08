# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「剪切粘贴」这组方法。

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
_NEED = ['T', '_unique_target_path', '_面板空白区菜单', 'note_swallowed']
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


def paste_into_current(app):
    """把剪贴板里的东西粘贴到当前文件夹（Ctrl+V）。"""
    clip = getattr(app, "_clip", None) or {}
    srcs = [p for p in (clip.get("paths") or []) if os.path.exists(p)]
    if not clip.get("paths"):
        messagebox.showinfo("提示", "剪贴板是空的 —— 先选中东西按 Ctrl+C（复制）"
                                   "或 Ctrl+X（剪切）。", parent=app.root)
        return
    if not clip.get("paths"):
        return
    gone = len(clip["paths"]) - len(srcs)
    if not srcs:
        messagebox.showinfo("提示", T("要粘贴的东西已经不在了（可能被删掉或改名了）。"),
                            parent=app.root)
        app._clip = None
        return
    if not app.current_dir:
        messagebox.showinfo("提示", "先打开一个目标文件夹，再按 Ctrl+V 粘贴。",
                            parent=app.root)
        return
    target = str(app.current_dir)
    cut = bool(clip.get("cut"))
    word = "移动" if cut else "复制"
    extra = "" if not gone else "\n（有 %d 项已经不在了，会跳过）" % gone
    if cut and not messagebox.askyesno(
            "粘贴（移动）",
            "把剪贴板里的 %d 项**移动**到：\n%s\n\n%s"% (len(srcs), target, extra)
            + "移动会把原位置的东西挪走（不是复制一份）。",
            parent=app.root):
        return
    app.begin_activity("正在%s %d 项…" % (word, len(srcs)))
    app.log_output("开始%s %d 项 → %s" % (word, len(srcs), target))

    def worker():
        done, errs = [], []
        for src in srcs:
            try:
                name = os.path.basename(str(src).rstrip("\\")) or str(src)
                is_dir = os.path.isdir(src)
                dst = _unique_target_path(target, name, is_dir)
                if cut:
                    shutil.move(src, dst)
                elif is_dir:
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                done.append((src, dst))
            except Exception as exc:
                errs.append("%s：%s" % (os.path.basename(str(src)), exc))
        try:
            app._ui_threadsafe(app._paste_done, cut, target, done, errs)
        except Exception as exc:
            # ★★ 2026-10-03：worker 尾部 _ui_threadsafe 失败时，
            #   之前 except: pass 默默丢弃，主线程永远不知道活儿没干。
            #   现在至少留一笔 warn，方便排查。
            note_swallowed(T("worker(_paste_done)：回主线程通知失败"),
                           exc, level="warn")

    threading.Thread(target=worker, daemon=True).start()


def _paste_done(app, cut, target, done, errs):
    """粘贴完成（回主线程）：同步数据库路径 + 刷新界面。"""
    app.end_activity()
    if cut:
        # 移动过了 → 数据库里的路径要跟着改（不然标签看着像丢了）
        for src, dst in done:
            try:
                if os.path.isdir(dst):
                    app.store.rename_prefix_paths(src, dst)
                else:
                    app.store.move_file_path(src, dst)
            except Exception as _e:
                note_swallowed(T("剪切粘贴后同步数据库路径失败"), _e)
            try:
                app.store.clear_dir_cache_under(os.path.dirname(str(src)))
            except Exception:
                pass
    # 剪贴板用完了（剪切只能粘一次；复制也清掉，避免误按再粘一次）
    app._clip = None
    n = len(done)
    word = "移动" if cut else "复制"
    app.log_output(T("完成：{x} {y} 项 → {z}", x=word, y=n, z=target))
    app.set_status("已%s %d 项 → %s%s"
                    % (word, n, os.path.basename(target.rstrip("\\")) or target,
                       "" if not errs else "（%d 项失败）" % len(errs)))
    if errs:
        app.log_problem("粘贴失败：%s" % "；".join(errs[:3]), level="error")
        messagebox.showwarning("有没粘成功的",
                               "这些没成功：\n\n%s" % "\n".join(errs[:5]),
                               parent=app.root)
    try:
        if app.view_mode == "dir" and app.current_dir:
            app.load_directory(app.current_dir)
        else:
            app.refresh_current_dir()
    except Exception as _e:
        note_swallowed(T("粘贴后刷新界面失败"), _e)
    try:
        app.refresh_rows_tags()
    except Exception:
        pass


def on_copy_key(app, event=None):
    if app._focus_is_input():
        return None
    app.copy_selected(cut=False)
    return "break"


def on_cut_key(app, event=None):
    if app._focus_is_input():
        return None
    app.copy_selected(cut=True)
    return "break"


def on_paste_key(app, event=None):
    if app._focus_is_input():
        return None
    app.paste_into_current()
    return "break"


def _on_place_pick(app, *a, **k):
    # ★★ 转发到 `AIxiede拆分开/程序分块/面板_空白区菜单.py`
    #   ★ 保留同名方法 = **所有调用方不用改**（稳定接口）
    return _面板空白区菜单._on_place_pick(app, *a, **k)
