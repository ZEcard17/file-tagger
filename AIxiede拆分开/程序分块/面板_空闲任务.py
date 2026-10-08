# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「空闲任务」这组方法。

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


# ==================================================================
#  ★ v25：闲时任务（鼠标 / 键盘空闲够久 → 悄悄跑一遍）
# ==================================================================
# ==========================================================================
#  ★★★ 要向主程序借的名字（★ 搬方法组的**关键**，错题本 #166）★★★
#  --------------------------------------------------------------------------
#  ★ 搬走的方法用了一堆**主程序自己造的东西**（`theme_get` / `T` / 常量…）。
#    这些**新文件里没有** → ★★ 一调那个方法就 `NameError` ——
#    而且**平时看不出来**（只有真点到那个按钮才炸）。
#  ★ 做法跟拆类一样：主程序启动时把「自己」交进来（`_set_app`）。
# ==========================================================================
_MUTABLE = []
_NEED = ['IDLE_INDEX_GAP_SEC', 'IDLE_RULES_CHUNK', 'IDLE_RULES_GAP_SEC', 'IDLE_RULES_PAUSE', 'IDLE_STOP_WITHIN_SEC', 'INDEX_SCAN_EVENT', 'T', 'load_idle_settings', 'note_swallowed', 'save_idle_settings']
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


def _setup_idle_jobs(app):
    """挂上「用户有没有在动」的探针 + 定时检查（每 30 秒看一眼）。"""
    app._last_input_ts = time.monotonic()
    app._idle_jobs_running = set()
    for seq in ("<Any-KeyPress>", "<Any-ButtonPress>", "<Motion>",
                "<MouseWheel>", "<Button-4>", "<Button-5>"):
        try:
            app.root.bind_all(seq, app._note_input, add="+")
        except Exception:
            pass
    app._idle_tick_job = None
    try:
        cfg = load_idle_settings()
        if cfg["rules_enabled"] or cfg["index_enabled"]:
            app.log_output(
                "☁ 闲时任务已开启：鼠标 / 键盘空闲够久会自动跑一次"
                "（在「自动标签规则」/「索引管理」窗口里可以关掉）")
    except Exception:
        pass
    app._idle_tick()


def _idle_seconds(app):
    try:
        return time.monotonic() - app._last_input_ts
    except Exception:
        return 0.0


def _idle_tick(app):
    try:
        app._check_idle_jobs()
    except Exception:
        pass
    try:
        app._idle_tick_job = app.root.after(30000, app._idle_tick)
    except Exception:
        app._idle_tick_job = None


def _refresh_idle_state(app):
    """对话框里改了「闲时自动跑」设置后调用（写日志 + 下次 tick 生效）。"""
    try:
        cfg = load_idle_settings()
        app.log_output(
            f"☁ 闲时任务设置：自动标签规则 "
            f"{'开' if cfg['rules_enabled'] else '关'}"
            f"（空闲 {cfg['rules_minutes']} 分钟） / 索引扫描 "
            f"{'开' if cfg['index_enabled'] else '关'}"
            f"（空闲 {cfg['index_minutes']} 分钟）")
    except Exception:
        pass


def _check_idle_jobs(app):
    """到点了就悄悄跑一次（不弹窗、限速、你一回来就停）。"""
    cfg = load_idle_settings()
    idle = app._idle_seconds()
    if idle < 60:
        return
    busy = (int(getattr(app, "_activity_count", 0)) > 0
            or INDEX_SCAN_EVENT.is_set()
            or app._any_scan_dialog_open()
            or bool(app._idle_jobs_running))
    if busy:
        return
    now = time.time()
    if (cfg["rules_enabled"]
            and idle >= cfg["rules_minutes"] * 60
            and now - cfg["rules_last"] >= IDLE_RULES_GAP_SEC
            and app._idle_rules_todo()):
        app._start_idle_rules_job()
        return
    if (cfg["index_enabled"]
            and idle >= cfg["index_minutes"] * 60
            and now - cfg["index_last"] >= IDLE_INDEX_GAP_SEC):
        app._start_idle_index_job()


def _idle_rules_todo(app):
    """闲时跑自动标签规则有没有活可干（有可用范围，或勾了文件名规则）。"""
    try:
        if app.store.get_auto_name_rule_tag_ids():
            return True
    except Exception:
        pass
    return bool(app._idle_rule_scopes_safe())


def _idle_rule_scopes_safe(app, log=False):
    """★ v25：闲时跑用的范围 —— 把「和本地索引/记录对不上」的范围剔除。

    手动扫描前会弹窗确认（范围写错会把旧标签清掉），
    闲时是悄悄跑的，不能弹窗，所以这里直接跳过对不上的范围。
    """
    scopes = []
    skipped = []
    for s in app._auto_rule_scopes():
        try:
            n = app.store.scope_known_file_count(s)
        except Exception:
            n = 0
        if n:
            scopes.append(s)
        else:
            skipped.append(s)
    if skipped and log:
        try:
            app.log_output(
                "☁ 闲时任务：跳过 " + str(len(skipped)) +
                " 个「已知文件 0 个」的作用范围（和索引写法对不上，"
                "建议到「自动标签规则」里点「✔ 检查」看一眼）：" +
                " ; ".join(skipped[:3]))
        except Exception:
            pass
    return scopes


# ---------- 闲时：自动标签规则 ----------
def _start_idle_rules_job(app):
    app._idle_jobs_running.add("rules")
    try:
        app.log_output(T("☁ 闲时任务：开始按自动标签规则慢慢跑一遍…"))
    except Exception:
        pass
    threading.Thread(target=app._idle_rules_worker,
                     daemon=True).start()


def _idle_rules_worker(app):
    """① 应用文件名规则；② 按启用规则的「作用范围」扫描打标签。

    ★ 限速 + 每批检查「你回来了没有」：一回来立刻收工。
    """
    total = 0
    changed = 0
    stopped = False
    try:
        try:
            n_name = len(app.store.get_auto_name_rule_tag_ids())
        except Exception:
            n_name = 0
        if n_name:
            try:
                changed += int(
                    app.store.resync_all_file_tags_with_name(
                        pause=IDLE_RULES_PAUSE,
                        cancel=(lambda: app._idle_seconds()
                                < IDLE_STOP_WITHIN_SEC)) or 0)
            except Exception as _e:
                note_swallowed(T("闲时任务：同步文件名的标签链失败"), _e)
        for scope in app._idle_rule_scopes_safe(log=True):
            if app._idle_seconds() < IDLE_STOP_WITHIN_SEC:
                stopped = True
                break
            try:
                paths = list(app.store.files_under_scope(scope)
                             .get("paths") or [])
            except Exception:
                paths = []
            for i in range(0, len(paths), IDLE_RULES_CHUNK):
                if app._idle_seconds() < IDLE_STOP_WITHIN_SEC:
                    stopped = True
                    break
                chunk = paths[i:i + IDLE_RULES_CHUNK]
                try:
                    with app.store.bulk():
                        changed += int(
                            app.store.sync_auto_tags_for_paths(chunk)
                            or 0)
                except Exception as _e:
                    note_swallowed(T("闲时任务：给一批文件打自动标签失败"), _e)
                total += len(chunk)
                try:
                    time.sleep(IDLE_RULES_PAUSE)
                except Exception:
                    pass
            if stopped:
                break
    except Exception:
        pass
    try:
        app._ui_threadsafe(app._on_idle_rules_done,
                            total, changed, stopped)
    except Exception as exc:
        note_swallowed(T("worker(_on_idle_rules_done)：回主线程通知失败"),
                       exc, level="warn")


def _on_idle_rules_done(app, total, changed, stopped):
    app._idle_jobs_running.discard("rules")
    try:
        save_idle_settings(rules_last=time.time())
    except Exception:
        pass
    msg = (f"☁ 闲时任务：自动标签规则跑完（处理 {total} 个文件，"
           f"{changed} 个文件的标签有变化"
           f"{'；你回来了，提前收工' if stopped else ''}）")
    try:
        app.log_output(msg)
        app.set_status(msg)
    except Exception:
        pass
    try:
        app.refresh_tags()
        app.refresh_rows_tags()
        app.refresh_categories()
        app._invalidate_tag_scope()
    except Exception:
        pass
    app._refresh_dialog_hints()
