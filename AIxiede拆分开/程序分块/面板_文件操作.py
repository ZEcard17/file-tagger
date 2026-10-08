# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「文件操作」这组方法。

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


# ---------------- ★★ 2026-10-06：撤销（Ctrl+Z）----------------
# ==========================================================================
#  ★★★ 要向主程序借的名字（★ 搬方法组的**关键**，错题本 #166）★★★
#  --------------------------------------------------------------------------
#  ★ 搬走的方法用了一堆**主程序自己造的东西**（`theme_get` / `T` / 常量…）。
#    这些**新文件里没有** → ★★ 一调那个方法就 `NameError` ——
#    而且**平时看不出来**（只有真点到那个按钮才炸）。
#  ★ 做法跟拆类一样：主程序启动时把「自己」交进来（`_set_app`）。
# ==========================================================================
_MUTABLE = []
_NEED = ['COPY', 'DND_FILES', 'SimpleInputDialog', 'T', 'UNDO_MAX', '_ctrl_down', '_recycle_restore', '_send_to_recycle_bin', '_undo_file_path', '_unique_target_path', 'is_remote_path', 'net_error_hint', 'note_swallowed', 'remap_net_path']
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


def _undo_init(app):
    """开机时把「撤销记录本」准备好（把上次关程序前的记录读回来）。"""
    app._undo_stack = []
    app._undo_redo_stack = []
    try:
        p = _undo_file_path()
        if p and os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                app._undo_stack = data[-UNDO_MAX:]
    except Exception as _e:
        note_swallowed(T("读撤销记录失败（这次开程序撤不了上次的事）"), _e,
                       quiet=True)
    app._undo_save_soon()


def _undo_save_soon(app):
    """把撤销记录写到磁盘（**关程序再开还能撤** —— 资源管理器做不到这个）。

    ★ 放到后台线程写，绝不拖慢界面（这是本程序一贯的规矩）。
    """
    try:
        if getattr(app, "_undo_save_job", None) is not None:
            return
    except Exception:
        pass

    def _do():
        app._undo_save_job = None
        try:
            p = _undo_file_path()
            if not p:
                return
            with open(p, "w", encoding="utf-8") as f:
                json.dump(app._undo_stack[-UNDO_MAX:], f,
                          ensure_ascii=False)
        except Exception:
            pass

    try:
        app._undo_save_job = app.root.after(800, _do)
    except Exception:
        app._undo_save_job = None


def undo_record(app, kind, items, note=""):
    """★ 记一条「怎么反着做回去」。**批量动作算一条**。

    kind: "delete" / "rename" / "tag_add" / "tag_remove"
    items: 各类型要的东西（见下面注释）
    ★ 记录里**只放纯数据**（路径、名字），不放控件、不放文件句柄 ——
      因为它要写到磁盘，下次开程序还要能用。
    """
    try:
        if not items:
            return
        rec = {"kind": kind, "items": list(items),
               "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               "note": note}
        app._undo_stack.append(rec)
        if len(app._undo_stack) > UNDO_MAX:
            app._undo_stack = app._undo_stack[-UNDO_MAX:]
        app._undo_redo_stack = []      # 记了新动作，红就作废
        app._undo_save_soon()
        app._undo_update_btn()
    except Exception as _e:
        note_swallowed(T("记撤销记录失败（这一步撤不了）"), _e, quiet=True)


def _undo_apply(app, kind, items):
    """真正去执行一条反向操作。

    返回 (成功了吗, 说明文字, 失败清单)。
    ★ 2026-10-07：**加了第三个返回值「失败清单」** ——
      以前返回两个，只分"全成功/全失败"两种情况。
      但**"删了 3 个、只还原回来 1 个"**这种半成不成的，
      原来会被当成"成功"报出去（`ok>0` 就算成功）→ **等于骗人**。
      用户以为"撤销了、都回来了"，其实桌上还少两个。
      （见错题本 #14 / 待清算清单第 2 条。）
    """
    if kind == "delete":
        # items: [路径, ...]（这些已经被丢进回收站了）
        ok, errs = _recycle_restore(items)
        # ★ 部分成功也要如实说 —— 不能因为回来了一部分就报"已撤销"
        if ok == 0:
            return (False,
                    "回收站还原失败：%s"
                    % ("；".join(errs[:3]) if errs else "系统没回应"),
                    errs)
        # ★ 库里的记录也要跟着回来 —— 否则文件回来了、标签却没了。
        #   （删除时调的是 store.forget_path；这里用重新登记的办法补回。）
        #   ★ 只对**真回来了的**那几项登记（失败的本就不在，登记了是脏数据）。
        for p in items:
            try:
                if os.path.exists(p):
                    app.store.remember_paths([p])
            except Exception:
                pass
        app.refresh_current_dir()
        app.refresh_rows_tags()
        app.refresh_categories()
        if errs:
            # 半成功：**说清楚回来了几个、还差几个**
            return (True,
                    "还原 %d 项，**还有 %d 项没回来**" % (ok, len(errs)),
                    errs)
        return True, "还原 %d 项" % ok, []
    if kind == "rename":
        # items: [(新路径, 旧路径), ...]
        done = 0
        errs = []
        for new_p, old_p in items:
            try:
                if not os.path.exists(new_p):
                    errs.append("%s 已经不在了" % os.path.basename(new_p))
                    continue
                if os.path.exists(old_p):
                    errs.append("%s 那个名字已经被占了"
                                % os.path.basename(old_p))
                    continue
                os.rename(new_p, old_p)
                try:
                    app.store.move_file_path(new_p, old_p)
                except Exception:
                    pass
                done += 1
            except Exception as exc:
                errs.append("%s：%s" % (os.path.basename(str(new_p)), exc))
        if done == 0:
            return (False,
                    "；".join(errs[:3]) if errs else "没有可改回的", errs)
        app.refresh_current_dir()
        app.refresh_rows_tags()
        if errs:
            return (True,
                    "改回 %d 个，**还有 %d 个没改回**" % (done, len(errs)),
                    errs)
        return True, "改回 %d 个" % done, []
    if kind in ("tag_add", "tag_remove"):
        # items: [(路径, 标签名), ...]；tag_add 的反动作是去掉
        done = 0
        errs = []
        for path, tname in items:
            try:
                if kind == "tag_add":
                    app.store.remove_tag_from_path(path, tname)
                else:
                    app.store.add_tag_to_file(path, tname)
                done += 1
            except Exception as exc:
                errs.append("%s：%s" % (os.path.basename(str(path)), exc))
        if done == 0:
            return (False,
                    "；".join(errs[:3]) if errs else "没有可改的", errs)
        app.refresh_rows_tags()
        app.refresh_categories()
        if errs:
            return (True,
                    "改回 %d 个，**还有 %d 个没改回**" % (done, len(errs)),
                    errs)
        return True, "改回 %d 个" % done, []
    return False, "不认识这种操作", []


def _undo_update_btn(app):
    """撤销按钮 / 菜单项亮不亮。"""
    try:
        n = len(getattr(app, "_undo_stack", []) or [])
    except Exception:
        n = 0
    try:
        if n:
            app._undo_btn.config(state="normal",
                                  text="↶ 撤销 (%d)" % n)
        else:
            app._undo_btn.config(state="disabled", text=T("↶ 撤销"))
    except Exception:
        pass


def _do_rename(app, path=None):
    """重命名选中的文件 / 文件夹，并把数据库里的路径同步过去。

    ★ 为什么要同步数据库：标签是按「文件记录」挂的，路径不改的话
      改完名双击打不开、标签看着也像丢了。
    """
    if path is None:
        path = app.file_list.get_single_selection()
    if not path:
        messagebox.showinfo("提示", T("请先选中**一个**文件或文件夹（单击它）。"),
                            parent=app.root)
        return
    old_name = os.path.basename(path.rstrip("\\")) or path
    # ★ v26 修正：SimpleInputDialog 在它自己的构造函数里已经
    #   wait_window 过了（窗口关闭时构造函数才返回），这里**不要**
    #   再 wait 一次 —— 那时 dlg 已经被销毁，再等会抛
    #   TclError: bad window path name（虽然被 except 吞了，但纯属浪费）。
    dlg = SimpleInputDialog(app.root, title=T("重命名（输入新名字）"),
                            initial=old_name)
    new_name = (getattr(dlg, "result", None) or "").strip()
    if not new_name or new_name == old_name:
        return
    if any(ch in new_name for ch in '\\/:*?"<>|'):
        messagebox.showerror("不能这样改名",
                             '名字里不能有  \\ / : * ? " < > |  这些字符',
                             parent=app.root)
        return
    parent_dir = os.path.dirname(path.rstrip("\\"))
    new_path = os.path.join(parent_dir, new_name)
    if os.path.exists(new_path):
        messagebox.showerror("不能改名",
                             "这个位置已经有同名的了：\n%s" % new_path,
                             parent=app.root)
        return
    is_dir = os.path.isdir(path)
    try:
        os.rename(path, new_path)
    except Exception as exc:
        messagebox.showerror("改名失败", str(exc), parent=app.root)
        return
    n = 0
    try:
        if is_dir:
            n = app.store.rename_prefix_paths(path, new_path)
            try:
                app.store.clear_dir_cache_under(path)
            except Exception:
                pass
        else:
            n = 1 if app.store.move_file_path(path, new_path) else 0
    except Exception as exc:
        app.log_problem(T("改名成功了，但数据库里的路径没同步好：{x}", x=exc),
                         level="error")
    app.log_output(T("已改名：{x} → {y}（数据库同步 {z} 条）", x=old_name, y=new_name, z=n))
    # ★★ 2026-10-06：记一笔撤销（记「新名 → 旧名」，撤销时改回去）
    app.undo_record("rename", [(new_path, path)])
    app.set_status(T("已改名：{x} → {y}", x=old_name, y=new_name))
    app.file_list.selected_paths = {new_path}
    app.refresh_current_dir()
    app.refresh_rows_tags()


def _do_delete(app, paths=None):
    """把选中的文件 / 文件夹删到回收站（可还原），并从库里清掉它们的记录。"""
    if paths is None:
        paths = list(app.file_list.get_selection() or [])
    if not paths:
        messagebox.showinfo("提示", "请先选中要删的东西（单击 / 框选 / Ctrl+A）。",
                            parent=app.root)
        return
    n = len(paths)
    first = os.path.basename(paths[0].rstrip("\\")) or paths[0]
    extra = "" if n == 1 else "\n（还有 %d 项）" % (n - 1)

    # ★★★ 2026-10-07：**网盘上的东西，删之前就要说清楚"这个撤不回来"**。
    #
    #   背景（错题本 #14 / #67，用户亲测确认）：
    #     **网盘（CloudDrive）删文件进的是「网盘自己的回收站」，
    #       不是 Windows 回收站。**
    #     而我们的「撤销删除」走的是系统回收站（Shell.Application 的 10 号
    #     特殊目录）—— **系统回收站里根本没有它，永远找不着**。
    #
    #   为什么要在**删之前**说、而不是等用户按 Ctrl+Z 才说：
    #     · 删除是**不可逆**操作，用户有权在动手前知道后果
    #     · 等到按撤销才发现"撤不了"，东西**已经没了**，说也晚了
    #     · 这属于「会丢东西」那一类红线（见待清算清单开头）
    #
    #   ★ 只警告、不阻止 —— 用户想删还是让他删（网盘客户端里也许能找回）。
    _remote = []
    try:
        for p in paths:
            if is_remote_path(p):
                _remote.append(os.path.basename(str(p).rstrip("\\")) or str(p))
    except Exception:
        _remote = []

    if _remote:
        _shown = "\n".join("   · " + x for x in _remote[:6])
        _more = ("\n   …还有 %d 项" % (len(_remote) - 6)
                 if len(_remote) > 6 else "")
        _ask = (
            "把选中的 %d 项丢进回收站？\n\n  第一项：%s%s\n\n"
            "⚠️ 注意：这里面有 **%d 项在网盘上**：\n%s%s\n\n"
            "★ 网盘上的东西，删掉之后**本程序撤不回来** ——\n"
            "   它进的是**网盘自己的回收站**，不是 Windows 回收站，\n"
            "   我们够不着它。要找回的话，得去**网盘客户端**里找。\n\n"
            "（本地文件不受影响，本地删了照样能撤销。）\n\n"
            "还删吗？"
            % (n, first, extra, len(_remote), _shown, _more))
        _title = "删到回收站（有网盘文件，撤不回来）"
    else:
        _ask = ("把选中的 %d 项丢进回收站？\n\n  第一项：%s%s\n\n"
                "丢进回收站还能还原，不是永久删除。" % (n, first, extra))
        _title = "删到回收站"

    if not messagebox.askyesno(_title, _ask, parent=app.root):
        return
    ok, errs = 0, []
    _done_paths = []          # ★ 2026-10-06：真正删成功的，用来记撤销
    for p in paths:
        try:
            _send_to_recycle_bin(p)
        except Exception as exc:
            errs.append("%s：%s" % (p, exc))
            continue
        ok += 1
        _done_paths.append(p)
        if p in app.file_list.selected_paths:
            app.file_list.selected_paths.discard(p)
        try:
            app.store.forget_path(p)
        except Exception as _e:
            note_swallowed(T("删除后清理数据库记录失败"), _e)
        # 文件夹的话，把它下面的记录和缓存也清掉
        if os.path.isdir(os.path.dirname(p)) and "." not in os.path.basename(p):
            try:
                app.store.clear_dir_cache_under(p)
            except Exception:
                pass
    app.log_output(T("已删到回收站：{x} 项", x=ok))
    # ★★ 2026-10-06：记一笔撤销（**整批算一条** —— 按一次 Ctrl+Z 全回来）
    if _done_paths:
        app.undo_record("delete", _done_paths)
    app.set_status("已删到回收站：%d 项%s"
                    % (ok, "" if not errs else "（%d 项失败）" % len(errs)))
    if errs:
        app.log_problem("删除失败：%s" % "；".join(errs[:3]), level="error")
        messagebox.showwarning("有删不掉的",
                               "这几项没删掉：\n\n%s" % "\n".join(errs[:5]),
                               parent=app.root)
    app.refresh_current_dir()
    app.refresh_rows_tags()
    app.refresh_categories()


# ---------------- ★ v25 补丁12：复制 / 剪切 / 粘贴 ----------------
def copy_selected(app, cut=False):
    """把选中的文件/文件夹放进「程序内的剪贴板」（Ctrl+C / Ctrl+X）。"""
    paths = list(app.file_list.get_selection() or [])
    if not paths:
        messagebox.showinfo("提示", "请先选中要%s的东西（单击 / 框选 / Ctrl+A）。"
                            % ("剪切" if cut else "复制"), parent=app.root)
        return
    app._clip = {"paths": paths, "cut": bool(cut)}
    word = "剪切" if cut else "复制"
    app.set_status("已%s %d 项 —— 打开目标文件夹后按 Ctrl+V 粘贴" % (word, len(paths)))
    app.log_output("已%s %d 项：%s" % (word, len(paths),
                                    "、".join(os.path.basename(p) for p in paths[:5])
                                    + ("…" if len(paths) > 5 else "")))


def _move_paths_to_folder(app, paths, target_dir):
    """★★ 2026-10-03 新增：把文件 / 文件夹**移动**进某个文件夹。

    这是「在列表里按住一个文件，拖到某个文件夹那一行上松手」走的路
    （文件列表拖动时回调 on_move_to_folder）。**以前主程序从来没接上
    这个回调**（一直是 None），所以松手以后什么都不发生 ——
    用户说「这个我想让它真的能用」，指的就是这一步。

    ★ 一定会先弹确认框（列出要移动的东西和目标文件夹），
      因为「移动」是真的把文件从原位置挪走。
    ★ 移动完会把数据库里的路径一起改掉（标签跟着走，不会丢）。
    """
    tgt = str(target_dir or "").rstrip("\\")
    if not tgt:
        return
    srcs = []
    for p in (paths or []):
        p = str(p)
        try:
            if not p or not os.path.exists(p):
                continue
            if os.path.normcase(os.path.dirname(p.rstrip("\\"))) == os.path.normcase(tgt):
                continue                       # 本来就在这个文件夹里
            if os.path.normcase(p.rstrip("\\")) == os.path.normcase(tgt):
                continue                       # 拖到自己身上
            # 不许把文件夹拖进它自己 / 它的子目录里
            if os.path.normcase(tgt).startswith(
                    os.path.normcase(p.rstrip("\\")) + os.sep):
                continue
            srcs.append(p)
        except Exception:
            continue
    if not srcs:
        app.set_status(T("没有可移动的东西（可能本来就在那个文件夹里）"))
        return
    names = "、".join(os.path.basename(str(p).rstrip("\\")) for p in srcs[:4])
    if len(srcs) > 4:
        names += "…（共 %d 项）" % len(srcs)
    if not messagebox.askyesno(
            "移动 %d 项" % len(srcs),
            "把选中的 %d 项**移动**到：\n%s\n\n  内容：%s\n\n"
            "「移动」会把原位置的东西挪走（不是复制一份）。\n"
            "标签会跟着一起走，不会丢。\n\n确定移动吗？"
            % (len(srcs), tgt, names),
            parent=app.root):
        app.set_status(T("已取消移动"))
        return
    app.begin_activity("正在移动 %d 项…" % len(srcs))
    app.log_output("拖动移动：%d 项 → %s" % (len(srcs), tgt))

    def worker():
        done, errs = [], []
        for src in srcs:
            try:
                name = os.path.basename(str(src).rstrip("\\")) or str(src)
                is_dir = os.path.isdir(src)
                dst = _unique_target_path(tgt, name, is_dir)
                shutil.move(src, dst)
                done.append((src, dst))
            except Exception as exc:
                errs.append("%s：%s" % (os.path.basename(str(src)), exc))
        try:
            app._ui_threadsafe(app._drag_move_done, tgt, done, errs)
        except Exception as exc:
            note_swallowed(T("worker(_drag_move_done)：回主线程通知失败"),
                           exc, level="warn")

    threading.Thread(target=worker, daemon=True).start()


def _drag_move_done(app, target, done, errs):
    """（主线程）拖动移动完成 → 同步数据库路径 + 刷新界面。

    ★ 和「剪切粘贴」走的是同一套数据库动作：路径改掉、标签保留。
    """
    app.end_activity()
    for src, dst in done:
        try:
            if os.path.isdir(dst):
                app.store.rename_prefix_paths(src, dst)
            else:
                app.store.move_file_path(src, dst)
        except Exception as _e:
            note_swallowed(T("拖动移动后同步数据库路径失败"), _e)
        try:
            app.store.clear_dir_cache_under(os.path.dirname(str(src)))
        except Exception:
            pass
    n = len(done)
    app.log_output(T("拖动移动完成：{x} 项 → {y}", x=n, y=target))
    app.set_status("已移动 %d 项 → %s%s" % (
        n, os.path.basename(target.rstrip("\\")) or target,
        "" if not errs else "（%d 项失败）" % len(errs)))
    if errs:
        app.log_problem("移动失败：%s" % "；".join(errs[:3]), level="error")
        messagebox.showwarning("有没移成功的",
                               "这些没成功：\n\n%s" % "\n".join(errs[:5]),
                               parent=app.root)
    try:
        if app.view_mode == "dir" and app.current_dir:
            app.load_directory(app.current_dir)
        else:
            app.refresh_current_dir()
    except Exception as _e:
        note_swallowed(T("移动后刷新界面失败"), _e)
    try:
        app.refresh_rows_tags()
    except Exception:
        pass


def _on_drag_out(app, event):
    """把选中的文件拖出去（拖到资源管理器 = 系统当成复制）。

    ★★ 2026-10-03 重要修正 —— 这段是「拖到文件夹上松手 = 移动进去」
    一直不能用的**第二个原因**：

      系统级的「拖出去」是拖放库（tkinterdnd2）在鼠标一动就抢过去的：
      它会开一个**模态的拖动循环**，鼠标被它抓走，
      我们自己写的 `_marquee_move` / `_marquee_end` 就再也收不到动作
      —— 也就是说：**只要在文件上开始拖，程序内部就永远不知道你在拖**
      （实测：合成一次 B1-Motion，程序直接卡死不返回，因为那个拖动
       循环在等一次永远等不到的「松手」）。
      原来这里只在「正在拉框」时返回 None 挡住它；
      「正在拖文件」（_file_drag.started）时没挡 → 于是内部拖动全程失灵。

      现在：**只要是我们自己在拖（拉框 或 拖文件），就返回 None
      让拖放库靠边站**；真想拖到资源管理器，按住 Ctrl 再拖
      （保留这个老功能，免得把它彻底弄没了）。
    """
    try:
        fl = app.file_list
        if getattr(fl, "_marq", None) and fl._marq.get("started"):
            return None
        fd = getattr(fl, "_file_drag", None)
        if fd and fd.get("started") and not _ctrl_down():
            return None
    except Exception:
        pass
    try:
        paths = list(app.file_list.get_selection() or [])
        if not paths:
            return None
        return (COPY, DND_FILES, "{ %s }" % " ".join(
            "{%s}" % p for p in paths))
    except Exception:
        return None


def _clipboard_has_files(app):
    """剪贴板里有没有"能粘贴的文件"（用来决定"粘贴"这一项灰不灰）。

    ★★ 2026-10-07 注意：**本程序自己的剪贴板变量叫 `_clip`**
      （不是 `_clip_files`）—— 它是 `{"paths": [...], "cut": bool}` 这样一个字典。
      ★ 我第一版写成了 `_clip_files`，**那个名字根本不存在** →
        `getattr(..., None)` 永远返回 `None` → "粘贴"这一项**永远是灰的**。
        这是那种"不报错、就是不给你用"的静默失效。
      ★ 现在按真名 `_clip` 判断，并且**两种形状都认**
        （dict / list），免得以后改了形状又悄悄失效。
    """
    try:
        cb = getattr(app, "_clip", None)
        if not cb:
            return False
        if isinstance(cb, dict):
            return bool(cb.get("paths"))
        if isinstance(cb, (list, tuple, set)):
            return len(cb) > 0
        return False
    except Exception:
        return False


def _open_in_explorer(app, path=None):
    """在 Windows 资源管理器里打开某个目录。"""
    try:
        target = path or app._current_dir()
        if not target:
            return
        import subprocess
        subprocess.Popen(["explorer", str(target)])
    except Exception as _e:
        note_swallowed(T("在资源管理器里打开失败"), _e)


def open_path(app, path):
    """打开文件 / 文件夹。

    ★ v25 补丁：库里存的 UNC 网盘路径是小写的（norm 里做了
      normcase），CloudDrive 这类网盘对大小写敏感时会报
      WinError 1203「网络路径键入不正确」。先用目录缓存把大小写
      还原成磁盘上的真名，再交给系统打开。
    """
    if not path:
        return
    # ★ v25 补丁2：库里的路径可能还指着「改名前」的网盘挂载，
    #   先换成当前挂载名，再多试一遍，免得直接弹「打开失败」。
    cands = []
    for p0 in (path, remap_net_path(path)):
        if not p0:
            continue
        try:
            real = app.store.canonical_path(p0)
        except Exception:
            real = p0
        for p in (real, p0):
            if p and p not in cands:
                cands.append(p)
    err = None
    for p in cands:
        try:
            if sys.platform.startswith("win"):
                os.startfile(p)  # noqa
            elif sys.platform == "darwin":
                subprocess.Popen(["open", p])
            else:
                subprocess.Popen(["xdg-open", p])
            return
        except Exception as exc:
            err = exc
    hint = net_error_hint(err)
    msg = str(err)
    if hint:
        msg = f"{msg}\n\n{hint}"
    messagebox.showerror("打开失败", msg, parent=app.root)


def open_selected(app):
    path = app.file_list.get_single_selection()
    if not path:
        return
    app.open_path(path)


def reveal_selected(app):
    path = app.file_list.get_single_selection()
    if not path:
        return
    folder = path if os.path.isdir(path) else os.path.dirname(path)
    app.open_path(folder)
