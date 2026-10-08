# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「日志状态」这组方法。

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
_MUTABLE = ['APP_CLOSING', 'FONT', 'UI_FONT_SIZE']
_NEED = ['APP_CLOSING', 'FONT', 'T', 'UI_FONT_SIZE', '_usage_note', 'note_swallowed']
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


def set_status(app, text):
    # ★★ 2026-10-03：**后台线程也能直接调**（之前只在主线程用）。
    #   原因：log_problem → set_status 这条路会在 _stuck_watchdog
    #   （后台线程，每秒跑一次）里被触发，app.status.config 直接
    #   在后台线程碰 Tk 控件，关窗瞬间偶发 -1073741819 崩溃。
    #   现在：先看是不是主线程，不在主线程就走 _ui_threadsafe 包一下。
    if (threading.current_thread() is not threading.main_thread()
            and getattr(app, "_ui_threadsafe", None) is not None
            and not APP_CLOSING):
        try:
            app._ui_threadsafe(app.set_status, text)
            return
        except Exception:
            pass     # 主程序关了 / 信箱满了 —— 退回去按原代码继续（再撞死也比丢字好）
    # ★★ v25 补丁42：**状态栏文字太长会把右边那排按钮挤出窗口。**
    #   用户反馈：「最下面那一行经常因为『统计分类中』左边黑灰文字
    #   重复又太长，导致有不少按钮被挤掉了不显示」。
    #   原因：app.status 是个没宽度上限的 ttk.Label，左边文字越长，
    #   它占的地方越大；右边那 7 个按钮是 pack(side="right") 的，
    #   位置被挤到窗口外面去了。
    #   修法：**按窗口实际宽度动态算能放多少字**（不是写死一个数）——
    #   窗口窄就少显示几个字，窗口宽就多显示。超出的部分进「📋 输出」。
    t = str(text or "")
    if len(t) > 6:
        try:
            avail = app._status_avail_px()
            if avail > 0:
                # 用真字体量一次：这段文字要多少像素
                f = tkfont.Font(family=FONT, size=UI_FONT_SIZE)
                if f.measure(t) > avail:
                    # 逐字砍到放得下（两端夹逼，很快就出来）
                    lo, hi = 1, len(t)
                    while lo < hi:
                        mid = (lo + hi + 1) // 2
                        if f.measure(t[:mid] + "…") <= avail:
                            lo = mid
                        else:
                            hi = mid - 1
                    t = t[:max(1, lo)] + "…"
                    try:
                        app.log_output(str(text))   # 全文进输出面板
                    except Exception:
                        pass
        except Exception:
            # 量不出来就退回「按字数硬截」
            if len(t) > 58:
                t = t[:57] + "…"
    try:
        app.status.config(text=t)
    except Exception:
        pass
    # ★ v25 补丁10：把「当前视图信息」显示在状态栏消息的**右边**。
    #   （以前是塞到标签条最右端；用户要求挪到这儿。）
    #   ★ 补丁42：它也必须**按剩余宽度截断** —— 实测它单独能占
    #     423 像素，正好把最左边那两个按钮（网盘 / 标签盒）顶出窗口。
    try:
        info = app._view_info_text(text)
        if info is not None:
            app._view_info_lbl.config(text=app._fit_view_info(info))
    except Exception:
        pass


# ---------- ★★ 2026-10-03：后台线程「回主线程」的安全通道 ----------
def _ui_threadsafe(app, fn, *a):
    """从**后台线程**把一件事交回主线程做 —— 绝不卡住、绝不丢。

    ★ 为什么不能用 app.root.after()：实测（在假家目录里把程序跑起来，
      用真鼠标真点击测的时候发现的）后台线程调 `root.after()` 会在
      tkinter 内部的 createcommand 上**卡死** —— Tcl 解释器同一时刻
      只允许一个线程碰它；主线程正在事件循环里的时候，后台线程这一步
      就可能永远等下去（线程还活着，但永远不会返回）。

      卡住的后果特别隐蔽、也特别烦：
        · `_bg_scan_worker`（后台扫目录）干完活要 root.after 回一句
          「扫完了」—— 这步一卡，主程序里「正在扫描」那个标记
          （_bg_scan_running_dir）就**永远挂着**，
          于是**以后打开任何没有缓存的文件夹都不会再扫，列表一直空着**。
        · log_output 也一样，卡一次就少一批日志。
      （实测就是这么复现的：新目录永远停在「首次扫描中…」。）

    ★ 现在改成走「信箱」：后台线程只往一个 Python 列表里塞东西
      （加锁，不碰 Tcl，绝不会卡）；主线程每 60 毫秒把信箱取空。
    """
    if APP_CLOSING or getattr(app, "_closing", False):
        return
    try:
        with app._ui_queue_lock:
            app._ui_queue.append((fn, a))
    except Exception:
        pass


def log_output(app, text):
    line = f"[{app._now_str()}] {text}"
    app._output_lines += 1
    if not app._ui_alive():
        return
    try:
        app._ui_threadsafe(app._append_to_text, app._text_output, line)
    except Exception as exc:
        # ★★ 2026-10-03：之前 except: pass，_ui_threadsafe 失败就静默丢日志。
        #   改成至少记一笔 warn，方便排查「为什么某段日志没出现」。
        note_swallowed(T("log_output：回主线程写「输出」面板失败"), exc,
                       level="warn")


def log_progress(app, text):
    line = f"[{app._now_str()}] {text}"
    app._progress_lines += 1
    if not app._ui_alive():
        return
    try:
        app._ui_threadsafe(app._append_to_text, app._text_progress, line)
    except Exception as exc:
        note_swallowed(T("log_progress：回主线程写「进度」面板失败"), exc,
                       level="warn")


def log_problem(app, text, level="warn"):
    """level: warn / error / info"""
    line = f"[{app._now_str()}] {text}"
    app._problem_count += 1
    # ★★ 2026-10-06：顺手记进「用法记录」（听诊器）。
    #   ★ 放在 `_ui_alive()` 检查**前面** —— 关窗那一刻报的问题
    #     也得记上（那正是最容易出问题的时候）。
    #   ★★ 但**要防重复记**：`note_swallowed` 也会把同一件事弹到
    #     「问题」面板、从而走到这里。不防的话同一个错会被记两次，
    #     汇总出来的次数直接翻倍（实测踩到了）。
    #     判据：这条 text 是不是刚从 note_swallowed 过来的。
    try:
        if not app._log_problem_is_echo(text):
            _usage_note("problem", text, level=level,
                        extra=app._usage_view_hint())
    except Exception:
        pass
    if not app._ui_alive():
        return
    # ★★ 2026-10-07 修「**问题按钮的颜色/数字第一次变化有延迟**」（用户报）★★
    #   ★ 真因（实测量出来的）：
    #     `_update_problem_badge` 原来**只走 `_ui_threadsafe`**（信箱），
    #     而主线程**每 60 毫秒**才把信箱取空一次 →
    #     所以点出一个错之后，**按钮上的数字要等最多 60ms 才变**。
    #     实测：
    #       立刻(5ms 后) → text 还是「问题 1」（**没变**）
    #       120ms 后    → 才变成「问题 2」
    #     ★ 用户看到的"延迟"就是这个。
    #
    #   ★ 修法：**如果当前就在主线程，直接改，立刻生效**；
    #     只有真从后台线程来的时候才走信箱（那时必须走，见
    #     `_ui_threadsafe` 的说明：后台线程碰 Tcl 会卡死）。
    #     ★ 这也是本程序里已有的写法（搜 `current_thread() is
    #       threading.main_thread` 能找到同样的判断）。
    _on_main = False
    try:
        _on_main = (threading.current_thread()
                    is threading.main_thread())
    except Exception:
        _on_main = False
    try:
        app._ui_threadsafe(app._append_to_text, app._text_problems,
                            line, level)
        if _on_main:
            # ★ 就在主线程 —— 立刻刷，别等那 60 毫秒
            app._update_problem_badge()
            try:
                app._text_problems.see("end")
            except Exception:
                pass
        else:
            app._ui_threadsafe(app._update_problem_badge)
    except Exception as exc:
        note_swallowed(T("log_problem：回主线程写「问题」面板失败"), exc,
                       level="warn")
    try:
        app.set_status(f"⚠ {text}")
    except Exception:
        pass


# ---------------- ★ 右下角活动指示器 ----------------
def begin_activity(app, text="处理中…"):
    """开始一个后台任务，右下角显示转圈动画。"""
    try:
        app._activity_count += 1
        app._activity_texts.append(text or "处理中…")
        app._activity_stack.append((text or "处理中…", time.time()))
        app._refresh_activity_ui()
        app._start_spinner()
        app.log_progress(f"▶ 开始：{text}")
    except Exception:
        pass


def end_activity(app):
    """结束一个后台任务；计数归零后自动隐藏。"""
    try:
        if app._activity_count > 0:
            app._activity_count -= 1
        if app._activity_texts:
            app._activity_texts.pop()
        name, t0 = ("?", time.time())
        if app._activity_stack:
            name, t0 = app._activity_stack.pop()
        dt = time.time() - t0
        if dt >= 1.0:
            app.log_progress(f"✓ 完成：{name}（{dt:.1f} 秒）")
        else:
            app.log_progress(f"✓ 完成：{name}")
        if dt >= 3.0:
            app.log_problem(
                f"「{name}」耗时 {dt:.1f} 秒（偏慢）", level="warn")
        app._refresh_activity_ui()
    except Exception:
        pass


# ---------- ★ v24：标签条作用范围（当前页 / 整个视图）----------
def _invalidate_tag_scope(app):
    """基础视图换了 / 标签变了 → 整库标签统计作废。"""
    app._tag_scope_cache = None
    app._tag_scope_cache_key = None
    app._tag_scope_scan_key = None
    # 注意：不清 _tag_scope_inflight —— 同一个视图正在统计时不要重复开线程
    app._tag_filter_base_spec = None
    try:
        app.file_list.set_tag_scope_stats(None)
    except Exception:
        pass
    # 当前若在「整个视图」范围，顺手重新统计（异步，避免打断视图切换）
    if getattr(app.file_list, "tag_scope", "page") == "view":
        try:
            app.root.after(1, app._start_tag_scope_scan)
        except Exception:
            pass
