# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「空白区菜单」这组方法。

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
_NEED = ['Path', 'T', '_unique_target_path', 'load_ui_setting', 'note_swallowed']
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


def _do_new_folder(app):
    """在当前文件夹里新建一个文件夹（名字重复就自动加 (2)、(3)…）。"""
    if not app.current_dir:
        messagebox.showinfo("提示", T("先打开一个文件夹再说。"), parent=app.root)
        return
    base = str(app.current_dir)
    name = "新建文件夹"
    i = 1
    while os.path.exists(os.path.join(base, name)):
        i += 1
        name = "新建文件夹 (%d)" % i
    newp = os.path.join(base, name)
    try:
        os.mkdir(newp)
    except Exception as exc:
        messagebox.showerror("新建失败", str(exc), parent=app.root)
        return
    app.log_output(T("新建文件夹：{x}", x=newp))
    app.set_status(T("已新建文件夹：{x}", x=name))
    app.refresh_current_dir()


def on_new_folder_key(app, event=None):
    if app._focus_is_input():
        return None
    app._do_new_folder()
    return "break"


def _refresh_places(app):
    """「常用位置」下拉：盘符 + 桌面/下载/文档 + 你收藏的 + 索引根目录。"""
    try:
        if getattr(app, "_places", None) is None:
            app._places = {}
        app._places = {}
        adds = []
        for d in app._drives():
            adds.append(("💽 " + d, d))
        # ★★ 2026-10-08：**别再写死 E 盘**（要打包发别人用）——
        #   原来"桌面/下载"写的是 `E:\桌面` / `E:\下载`，
        #   别人电脑上**根本没有 E 盘**（或者没这两个文件夹）→
        #   `os.path.isdir` 为假 → **这两项直接消失**（不算崩，但少了）。
        #   ★ 改成**问 Windows 要**（`USERPROFILE` / `HOMEDRIVE`）：
        #     · 桌面 → `%USERPROFILE%\Desktop`
        #       ★ 中文系统上文件夹真名是"桌面"，但**路径还是 Desktop**
        #         （Windows 用 `desktop.ini` 做显示名，路径不变）——
        #         所以 `Desktop` 是对的。
        #     · 下载 → `%USERPROFILE%\Downloads`
        #   ★ 还**保留老的 E 盘**兜底：本机用户习惯了 E:\桌面，
        #     两边都试，哪个存在加哪个（**可逆**，不破坏现状）。
        _home = Path.home()
        for label, p in (("🖥 桌面", str(_home / "Desktop")),
                         ("🖥 桌面", r"E:\桌面"),
                         ("⬇ 下载", str(_home / "Downloads")),
                         ("⬇ 下载", r"E:\下载"),
                         ("📄 文档", str(_home / "Documents")),
                         ("🏠 主目录", str(_home))):
            if os.path.isdir(p):
                adds.append((label, p))
        for b in (load_ui_setting("nav_bookmarks", []) or []):
            if isinstance(b, str) and os.path.isdir(b):
                adds.append(("⭐ " + os.path.basename(b.rstrip("\\")) or b, b))
        try:
            for r in app.store.all_index_roots():
                adds.append(("📚 索引 " + (r["path"] or ""), r["path"]))
        except Exception:
            pass
        vals = []
        for label, p in adds:
            if label in app._places:
                continue
            app._places[label] = p
            vals.append(label)
        app._drive_cbo.configure(values=app._drives())
        app._place_cbo.configure(values=vals[:40])
    except Exception as _e:
        note_swallowed(T("刷新「常用位置」下拉失败"), _e)


def _on_place_pick(app, event=None):
    label = (app._place_var.get() or "").strip()
    p = (app._places or {}).get(label)
    if p:
        app.load_directory(p)


def _on_drop_files(app, event):
    """资源管理器拖过来的文件/文件夹 → 复制到当前文件夹。"""
    try:
        raw = event.data or ""
        items = app.file_list.tk.splitlist(raw)
    except Exception:
        items = []
    items = [str(x) for x in items if x]
    if not items:
        return
    if not app.current_dir:
        messagebox.showinfo("提示", T("先打开一个文件夹，再把东西拖进来。"),
                            parent=app.root)
        return
    target = str(app.current_dir)
    names = [(os.path.basename(p.rstrip("\\")) or p) for p in items]
    preview = "、".join(names[:4]) + ("…" if len(names) > 4 else "")
    if not messagebox.askyesno(
            "拖进来了 %d 项" % len(items),
            "要把这 %d 项**复制到**：\n%s\n\n  内容：%s\n\n"
            "（是复制，不会动原来的文件）" % (len(items), target, preview),
            parent=app.root):
        return
    app.begin_activity("正在复制拖进来的 %d 项…" % len(items))
    app.log_output("拖放复制：%d 项 → %s" % (len(items), target))

    def worker():
        done, errs = [], []
        for src in items:
            try:
                name = os.path.basename(src.rstrip("\\")) or src
                is_dir = os.path.isdir(src)
                dst = _unique_target_path(target, name, is_dir)
                if is_dir:
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                done.append(dst)
            except Exception as exc:
                errs.append("%s：%s" % (os.path.basename(str(src)), exc))
        try:
            app._ui_threadsafe(app._drop_done, target, done, errs)
        except Exception as exc:
            note_swallowed(T("worker(_drop_done)：回主线程通知失败"),
                           exc, level="warn")

    threading.Thread(target=worker, daemon=True).start()


def _drop_done(app, target, done, errs):
    app.end_activity()
    app.log_output("拖放完成：复制了 %d 项" % len(done))
    app.set_status("已把拖进来的 %d 项复制到 %s%s"
                    % (len(done), os.path.basename(target.rstrip("\\")) or target,
                       "" if not errs else "（%d 项失败）" % len(errs)))
    if errs:
        app.log_problem("拖放复制失败：%s" % "；".join(errs[:3]), level="error")
        messagebox.showwarning("有没复制成功的",
                               "这些没成功：\n\n%s" % "\n".join(errs[:5]),
                               parent=app.root)
    try:
        app.load_directory(target)
    except Exception as _e:
        note_swallowed(T("拖放后刷新界面失败"), _e)


def _popup_blank_menu(app, event):
    """★ 在"空白处"右键时弹出的菜单（对整个当前目录的操作）。

    ★★ 2026-10-07 新增（用户报「资源管理器新建的空文件夹 →
      在本程序里无法右键」，待清算 #5）。

    ★ 为什么要单独一个菜单（而不是复用 `app.menu`）：
      那个菜单里全是"对选中文件做的事"（打标签 / 重命名 / 删除…），
      空白处**没有选中文件**，那些项点了也没意义 ——
      **摆一堆点不了的东西比不弹更糟**。
    ★ 所以这里只放"对目录做的事"，而且**每一项都真的能用**。
    ★ 每次现建现用（`tk.Menu` 很轻），免得跟主菜单的状态打架。

    ★★ 2026-10-07 **又踩一个"名字不存在"**：
      我第一版写的是 `app.file_list.current_dir` ——
      **`FileList` 里根本没有这个属性**（翻遍了它的 `__init__`，
      只记了 `selected_paths` / `last_clicked_path`）。
      → `getattr(..., None)` 永远 `None` → 菜单里"新建/打开资源管理器"
        **全是灰的**（又一个"不报错、就是不给你用"）。
      ★ **正确的来源是主程序自己的 `app.current_dir`**（见 32312 行）。
    """
    cur = None
    # ★ 先问主程序自己（这是真来源），FileList 那里没有这个属性
    for attr in ("current_dir", "_current_dir"):
        try:
            v = getattr(app, attr, None)
            if v:
                cur = str(v)
                break
        except Exception:
            continue
    # ★★ 2026-10-07 **又踩一个"名字不存在"**：这里原来写的是
    #   `m_tk.Menu(...)` —— **本程序里没有 `m_tk` 这个别名**
    #   （用的是 `import tkinter as tk`）。
    #   → `NameError` 被外层 except 吞掉 → 菜单**建不出来**，
    #     而账本里只留一句"空白处右键菜单失败"。
    #   ★ 这类错误我这一轮踩了三次（`_clip_files` / `file_list.current_dir`
    #     / `m_tk`），共同点都是**名字不存在 + 异常被吞**。
    #   ★ 所以：**写新代码引用别的东西之后，一定要核一遍名字存不存在。**
    m = tk.Menu(app.root, tearoff=0)
    # ---- 新建 ----
    try:
        m.add_command(label=T("📁 新建文件夹…"),
                      command=lambda: app._blank_new_folder(cur))
    except Exception:
        pass
    try:
        m.add_command(label=T("📄 新建文本文件…"),
                      command=lambda: app._blank_new_file(cur))
    except Exception:
        pass
    m.add_separator()
    # ---- 目录级操作 ----
    try:
        m.add_command(label=T("🔄 刷新"),
                      command=lambda: app.refresh_all())
    except Exception:
        pass
    try:
        m.add_command(label=T("⬜ 全选"),
                      command=lambda: app._select_all_files())
    except Exception:
        pass
    m.add_separator()
    try:
        m.add_command(
            label=T("📂 在资源管理器里打开"),
            command=lambda: app._open_in_explorer(cur),
            state=("normal" if cur else "disabled"))
    except Exception:
        pass
    try:
        m.add_command(
            label="📋 粘贴到这儿（Ctrl+V）",
            command=lambda: app.paste_into_current(),
            state=("normal" if app._clipboard_has_files() else "disabled"))
    except Exception:
        pass
    try:
        m.tk_popup(event.x_root, event.y_root)
    finally:
        try:
            m.grab_release()
        except Exception:
            pass


def _blank_new_folder(app, cur=None):
    """在当前目录新建一个文件夹（弹个小输入框问名字）。"""
    try:
        base = cur or app._current_dir()
        if not base:
            messagebox.showinfo("新建文件夹", T("先打开一个文件夹。"),
                                parent=app.root)
            return
        name = app._ask_one_line("新建文件夹", "文件夹名字：", "新建文件夹")
        if not name:
            return
        name = str(name).strip()
        if not name:
            return
        # ★ 防呆：不许带路径分隔符（免得用户写出目录外面去）
        for ch in ("\\", "/", ":", "*", "?", '"', "<", ">", "|"):
            name = name.replace(ch, "_")
        target = os.path.join(base, name)
        if os.path.exists(target):
            messagebox.showwarning("新建文件夹",
                                   "已经有同名的了：\n%s" % name,
                                   parent=app.root)
            return
        os.makedirs(target, exist_ok=False)
        app.log_output(T("已新建文件夹：{x}", x=target))
        try:
            app.refresh_all()
        except Exception:
            pass
    except Exception as _e:
        note_swallowed(T("新建文件夹失败"), _e)
        try:
            messagebox.showerror("新建文件夹", "建不了：%s" % _e,
                                 parent=app.root)
        except Exception:
            pass


def _blank_new_file(app, cur=None):
    """在当前目录新建一个空文本文件。"""
    try:
        base = cur or app._current_dir()
        if not base:
            messagebox.showinfo("新建文件", T("先打开一个文件夹。"),
                                parent=app.root)
            return
        name = app._ask_one_line("新建文本文件", "文件名：", "新建文本.txt")
        if not name:
            return
        name = str(name).strip()
        if not name:
            return
        for ch in ("\\", "/", ":", "*", "?", '"', "<", ">", "|"):
            name = name.replace(ch, "_")
        if "." not in name:
            name += ".txt"
        target = os.path.join(base, name)
        if os.path.exists(target):
            messagebox.showwarning("新建文件",
                                   "已经有同名的了：\n%s" % name,
                                   parent=app.root)
            return
        with open(target, "x", encoding="utf-8"):
            pass
        app.log_output(T("已新建文件：{x}", x=target))
        try:
            app.refresh_all()
        except Exception:
            pass
    except Exception as _e:
        note_swallowed(T("新建文件失败"), _e)
        try:
            messagebox.showerror("新建文件", "建不了：%s" % _e,
                                 parent=app.root)
        except Exception:
            pass
