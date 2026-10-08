# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「缓存设置」这组方法。

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
#  ★ 为什么搬方法组**必须**有这个（搬独立类时也得有）：
#    搬走的方法用了一堆**主程序自己造的东西**（`theme_get` / `T` /
#    各种常量…）。这些**新文件里没有** →
#    ★★ 一调那个方法就 `NameError` ——
#      而且**平时看不出来**（只有真点到那个按钮才炸）。
#  ★ 做法跟拆类一样：主程序启动时把「自己」交进来（`_set_app`）。
# ==========================================================================
_MUTABLE = ['DB_PATH', 'EXPORT_DIR', 'FONT', 'UI_FONT_SIZE']
_NEED = ['DB_PATH', 'EXPORT_DIR', 'FONT', 'Path', 'T', 'UI_FONT_SIZE', '_cache_clean_old', '_load_full_settings', '_preview_cache_dir', '_write_json_file', 'is_remote_path', 'load_ui_setting', 'save_data_dir', 'save_ui_setting', 'theme_get']
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


def _open_cache_settings(app):
    """★★ 2026-10-06：**网盘预览缓存设置**面板。

    用户要求：「弄个文件缓存设置，设置那些个网盘上的预览的时候临时
    下载在哪里，要不要无痕浏览（就是阅后即焚），还是到一段时间就
    自动清理，亦或者是文件夹超过一定大小就自动清理」。

    四项：
      ① 缓存放哪儿（可以挑盘；也能一键「用临时目录」）
      ② 无痕模式（阅后即焚）—— 每次启动换新目录，旧的自动清掉
      ③ 定时清理 —— 多久没用过的缓存就删
      ④ 超大小清理 —— 目录超过多少 MB 就删最旧的

    ★ 界面上每一项都配一句大白话说明「这选项是干嘛的」。
    """
    win = tk.Toplevel(app.root)
    # ★★ 2026-10-07：Toplevel 是**原生窗口**，底色不跟 ttk 主题走 ——
    #   不设 bg 就用系统默认（白/浅灰），那就是"小窗口夜间还是白的"的根因。
    try:
        win.configure(bg=theme_get("win_bg"))
        # ★ 登记一下，切主题时由 _retheme_custom_parts 统一刷新
        _reg = getattr(app, "_theme_windows", None)
        if _reg is None:
            _reg = app._theme_windows = []
        _reg.append(win)
    except Exception:
        pass
    win.title("📥 网盘预览缓存设置")
    win.transient(app.root)

    fr = ttk.Frame(win, padding=14)
    fr.pack(fill="both", expand=True)

    ttk.Label(
        fr, text=T("网盘文件预览时，会在本地留一份临时副本（缓存）。\n"
                 "下面四个选项决定「放哪」和「什么时候自己清掉」。"),
        justify="left", font=(FONT, UI_FONT_SIZE)).pack(anchor="w",
                                                        pady=(0, 10))

    # ---------- ① 缓存放哪儿 ----------
    box1 = ttk.LabelFrame(fr, text=T("① 缓存放哪儿"), padding=10)
    box1.pack(fill="x", pady=4)
    dir_var = tk.StringVar(
        value=str(load_ui_setting("preview_cache_dir", "") or ""))

    def _pick_dir():
        cur = dir_var.get().strip()
        d = filedialog.askdirectory(
            title=T("选一个放缓存的文件夹（建议放空间大的本地盘，比如 E 盘）"),
            initialdir=cur or None, parent=win)
        if d:
            dir_var.set(d)

    def _use_temp():
        dir_var.set("")     # 空 = 用系统临时目录

    row = ttk.Frame(box1)
    row.pack(fill="x")
    ent = ttk.Entry(row, textvariable=dir_var, width=52,
                    font=(FONT, UI_FONT_SIZE))
    ent.pack(side="left", fill="x", expand=True)
    ttk.Button(row, text=T("浏览…"), command=_pick_dir).pack(side="left", padx=4)
    ttk.Button(row, text=T("用临时目录"), command=_use_temp).pack(side="left")
    ttk.Label(box1, text=T("留空 = 用系统临时目录（推荐，省心）。"
                         "正在用的目录见下面「现在的情况」。"),
              foreground=theme_get("fg_dim")).pack(anchor="w", pady=(6, 0))

    # ---------- ② 无痕模式 ----------
    box2 = ttk.LabelFrame(fr, text=T("② 无痕模式（阅后即焚）"), padding=10)
    box2.pack(fill="x", pady=4)
    inc_var = tk.BooleanVar(
        value=bool(load_ui_setting("cache_incognito", True)))
    ttk.Checkbutton(
        box2, text=T("开启 —— 每次开程序都换一个全新的缓存目录，"
                   "上次留下的自动清掉（推荐）"),
        variable=inc_var).pack(anchor="w")
    ttk.Label(box2, text=T("不开的话：缓存会一直留着，下次看同一个文件会更快"
                         "（但也更占地方）。"),
              foreground=theme_get("fg_dim")).pack(anchor="w", pady=(4, 0))

    # ---------- ③ 定时清理 ----------
    box3 = ttk.LabelFrame(fr, text=T("③ 定时清理"), padding=10)
    box3.pack(fill="x", pady=4)
    ttl_var = tk.StringVar(
        value=str(load_ui_setting("cache_ttl_hours", 24)))
    r3 = ttk.Frame(box3)
    r3.pack(fill="x")
    ttk.Label(r3, text=T("多久没用过的缓存就自动删掉：")).pack(side="left")
    ttk.Entry(r3, textvariable=ttl_var, width=8,
              font=(FONT, UI_FONT_SIZE)).pack(side="left", padx=4)
    ttk.Label(r3, text=T("小时（填 0 = 不按时间清）")).pack(side="left")

    # ---------- ④ 超大小清理 ----------
    box4 = ttk.LabelFrame(fr, text=T("④ 超大小清理"), padding=10)
    box4.pack(fill="x", pady=4)
    maxmb_var = tk.StringVar(
        value=str(load_ui_setting("cache_max_mb", 2048)))
    r4 = ttk.Frame(box4)
    r4.pack(fill="x")
    ttk.Label(r4, text=T("缓存文件夹超过")).pack(side="left")
    ttk.Entry(r4, textvariable=maxmb_var, width=8,
              font=(FONT, UI_FONT_SIZE)).pack(side="left", padx=4)
    ttk.Label(r4, text=T("MB 就删最旧的（填 0 = 不管大小）")).pack(side="left")
    ttk.Label(box4, text=T("★ 是「删最旧的、腾到限额以下」，不会把整个目录清空。"),
              foreground=theme_get("fg_dim")).pack(anchor="w", pady=(4, 0))

    # ---------- 现在的情况 ----------
    info = ttk.LabelFrame(fr, text=T("现在的情况"), padding=10)
    info.pack(fill="x", pady=(10, 4))
    info_lbl = ttk.Label(info, text="", justify="left")
    info_lbl.pack(anchor="w")

    def _refresh_info():
        try:
            now = _preview_cache_dir()
            n = 0
            sz = 0
            for dp, dn, fs in os.walk(now):
                for f in fs:
                    try:
                        sz += os.path.getsize(os.path.join(dp, f))
                        n += 1
                    except Exception:
                        pass
            info_lbl.configure(
                text=T("正在用的缓存目录：\n{x}\n\n里面现在有 {n} 个文件，"
                       "共 {s} MB",
                       x=now, n=n, s="%.1f" % (sz / 1024 / 1024)))
        except Exception as e:
            info_lbl.configure(text="看不出来（%s）" % e)

    _refresh_info()

    # ---------- 按钮 ----------
    btns = ttk.Frame(fr)
    btns.pack(fill="x", pady=(10, 0))

    def _save():
        try:
            ttl_v = float(ttl_var.get() or 0)
        except Exception:
            messagebox.showerror("填错了", T("「定时清理」那里要填数字（小时）"),
                                 parent=win)
            return
        try:
            mb_v = float(maxmb_var.get() or 0)
        except Exception:
            messagebox.showerror("填错了", T("「超大小清理」那里要填数字（MB）"),
                                 parent=win)
            return
        d = dir_var.get().strip()
        if d:
            try:
                if is_remote_path(d) and not messagebox.askyesno(
                        "注意",
                        "你选的是网络盘目录。\n\n"
                        "缓存本来就是为了绕开网盘的慢 ——\n"
                        "放网盘上反而更慢。\n\n还是用这个吗？",
                        parent=win, default="no"):
                    return
            except Exception:
                pass
            try:
                os.makedirs(d, exist_ok=True)
            except Exception as exc:
                messagebox.showerror("建不出来",
                                     "这个目录建不出来：\n%s\n\n%s" % (d, exc),
                                     parent=win)
                return
        save_ui_setting("preview_cache_dir", d)
        save_ui_setting("cache_incognito", bool(inc_var.get()))
        save_ui_setting("cache_ttl_hours", ttl_v)
        save_ui_setting("cache_max_mb", mb_v)
        app.set_status(T("缓存设置已保存"))
        messagebox.showinfo(
            "保存好了",
            "设置已经存下来了。\n\n"
            "· 「缓存放哪儿」和「无痕模式」要**重启程序**才对当前这次生效；\n"
            "· 「定时清理」和「超大小清理」点下面的按钮就会立刻用上。",
            parent=win)
        _refresh_info()

    def _clean_now():
        try:
            msg = _cache_clean_old(force=True)
        except Exception as e:
            msg = "清理出错：%s" % e
        app.set_status(msg)
        messagebox.showinfo("清理结果", msg, parent=win)
        _refresh_info()

    def _open_dir():
        try:
            d = _preview_cache_dir()
            os.startfile(d)          # noqa: 只在 Windows 上跑
        except Exception as e:
            messagebox.showerror("打不开", str(e), parent=win)

    ttk.Button(btns, text=T("保存设置"), command=_save).pack(side="left")
    ttk.Button(btns, text=T("立刻清一次"), command=_clean_now).pack(side="left", padx=6)
    ttk.Button(btns, text=T("打开缓存文件夹"), command=_open_dir).pack(side="left")
    ttk.Button(btns, text=T("关闭"), command=win.destroy).pack(side="right")

    try:
        win.update_idletasks()
    except Exception:
        pass


def _set_preview_cache_dir(app):
    """★★ v26 新增：设置「网盘预览的本地缓存目录」。

    用户反馈：「这个缓存目录在哪里，我可不可以自己设置」——
    现在可以：点这个菜单选一个目录，之后网盘预览拷下来的临时文件
    就都放在那儿（比如放到 E 盘，不占 C 盘）。

    改完需要**重启程序**才生效（现在的缓存路径是启动时定下的）。
    """
    cur = ""
    try:
        cur = str(load_ui_setting("preview_cache_dir", "") or "")
    except Exception:
        cur = ""
    now_dir = _preview_cache_dir()
    d = filedialog.askdirectory(
        title="选择预览缓存目录（网盘文件预览时拷到这里的临时副本）\n"
              "（建议放在空间大的本地盘，比如 E 盘；不要选网络盘）",
        initialdir=cur or None,
        parent=app.root)
    if not d:
        return
    # 检查：别让用户选一个网盘目录
    try:
        if is_remote_path(d):
            if not messagebox.askyesno(
                    "注意",
                    "你选的是**网络盘**目录。\n\n"
                    "预览缓存本来就是为了绕开网盘的慢 ——\n"
                    "如果放网盘上，拷来拷去反而更慢。\n\n"
                    "还是选它吗？",
                    parent=app.root, default="no"):
                return
    except Exception:
        pass
    try:
        os.makedirs(d, exist_ok=True)
    except Exception as exc:
        messagebox.showerror("设置失败",
                             "这个目录建不出来：\n%s\n\n%s" % (d, exc),
                             parent=app.root)
        return
    save_ui_setting("preview_cache_dir", d)
    messagebox.showinfo(
        "设置成功",
        "新的预览缓存目录：\n%s\n\n"
        "现在还没生效 —— **重启程序**之后就会用这个目录。\n\n"
        "（当前正在用的目录是：\n%s）\n\n"
        "★ 旧目录里的文件不用你手动删，\n"
        "  重启程序时会自动清理。"
        % (d, now_dir),
        parent=app.root)


def change_data_dir(app):
    cur_base = DB_PATH.parent
    new_dir = filedialog.askdirectory(
        title=T("选择数据存储位置（建议本地磁盘，不要选网络盘）"),
        initialdir=str(cur_base),
        parent=app.root)
    if not new_dir:
        return
    try:
        new_base = Path(new_dir).expanduser().resolve()
    except Exception as exc:
        messagebox.showerror("错误", str(exc), parent=app.root)
        return

    if new_base == cur_base:
        messagebox.showinfo("提示", T("和当前位置相同，未做改动。"),
                            parent=app.root)
        return

    if is_remote_path(str(new_base)):
        if not messagebox.askyesno(
                "警告",
                "你选择的目录在网络盘上。\n\n"
                "SQLite 数据库放在网络盘上会非常慢，"
                "文件损坏的风险也更高。\n\n"
                "确定继续吗？",
                parent=app.root):
            return

    migrate = messagebox.askyesno(
        "数据迁移",
        "是否把现有数据（数据库 + 导出目录）搬过去？\n\n"
        "  · 是 → 复制到新位置（原文件保留）\n"
        "  · 否 → 只改位置，新位置从空开始",
        parent=app.root)

    new_db = new_base / DB_PATH.name
    new_export = new_base / EXPORT_DIR.name

    try:
        new_base.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        messagebox.showerror("错误", f"无法创建目录：\n{exc}",
                             parent=app.root)
        return

    if migrate:
        try:
            # 复制数据库
            if DB_PATH.exists():
                if new_db.exists() and not messagebox.askyesno(
                        "覆盖？",
                        f"新位置已存在数据库文件：\n{new_db}\n\n"
                        "覆盖它吗？",
                        parent=app.root):
                    return
                shutil.copy2(str(DB_PATH), str(new_db))
            # 复制导出目录
            if EXPORT_DIR.exists() and EXPORT_DIR.is_dir():
                if new_export.exists():
                    if not messagebox.askyesno(
                            "覆盖？",
                            f"新位置已存在导出目录：\n{new_export}\n\n"
                            "覆盖它吗？",
                            parent=app.root):
                        return
                    shutil.rmtree(str(new_export))
                shutil.copytree(str(EXPORT_DIR), str(new_export))
        except Exception as exc:
            messagebox.showerror("迁移失败", str(exc), parent=app.root)
            return

    # ★ 顺便把当前完整设置也复制到新位置
    try:
        old_full = _load_full_settings()
        if old_full:
            _write_json_file(new_base / ".file_tagger_settings.json",
                             old_full)
    except Exception:
        pass

    if save_data_dir(new_base):
        messagebox.showinfo(
            "需要重启",
            f"数据位置已改为：\n{new_base}\n\n"
            f"数据库：{new_db.name}\n"
            f"导出目录：{new_export.name}\n"
            f"设置文件：.file_tagger_settings.json\n\n"
            "请关闭程序并重新打开，新的位置才会生效。",
            parent=app.root)
    else:
        messagebox.showerror("保存失败",
                             "无法写入设置文件，请检查权限。",
                             parent=app.root)
