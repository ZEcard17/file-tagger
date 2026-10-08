# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「健康检查」这组方法。

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


# ---------------- ★ 日志面板 ----------------
# ==========================================================================
#  ★★★ 要向主程序借的名字（★ 搬方法组的**关键**，错题本 #166）★★★
#  --------------------------------------------------------------------------
#  ★ 搬走的方法用了一堆**主程序自己造的东西**（`theme_get` / `T` / 常量…）。
#    这些**新文件里没有** → ★★ 一调那个方法就 `NameError` ——
#    而且**平时看不出来**（只有真点到那个按钮才炸）。
#  ★ 做法跟拆类一样：主程序启动时把「自己」交进来（`_set_app`）。
# ==========================================================================
_MUTABLE = ['UI_FONT_SIZE']
_NEED = ['AutoTagRulesDialog', 'INDEX_SCAN_EVENT', 'IndexManagerDialog', 'T', 'UI_FONT_SIZE', '_HEART', '_SWALLOW_LAST', '_bg_post', '_cache_clean_old', '_面板插件挂载', 'swallowed_report', 'theme_get']
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


def _build_log_panel(app):
    app._log_panel = ttk.Frame(app.root)
    # 初始不显示

    nb = ttk.Notebook(app._log_panel)
    nb.pack(fill="both", expand=True, padx=4, pady=(4, 2))

    app._log_nb = nb

    # 输出页
    f_out = ttk.Frame(nb)
    nb.add(f_out, text=T("输出"))
    app._text_output = tk.Text(
        f_out, wrap="none", width=48, height=10, font=("Consolas", UI_FONT_SIZE),
        bg=theme_get("panel_bg2"), fg=theme_get("fg"), borderwidth=0,
        highlightthickness=0,
        # ★ 2026-10-07 加行距（用户报「行高比字矮、字挤在一起」）：
        #   Tk Text 默认 spacing1/spacing3 都是 0 ——
        #   也就是"字多高就占多高"，**一点喘气空间都没有**。
        #   实测 Consolas 14 的 linespace = 25，紧贴着看就很挤。
        #   上下各留 2 像素，整片就松快了。
        spacing1=2, spacing3=2)
    sb1 = ttk.Scrollbar(f_out, orient="vertical",
                        command=app._text_output.yview)
    app._text_output.configure(yscrollcommand=sb1.set)
    sb1.pack(side="right", fill="y")
    app._text_output.pack(side="left", fill="both", expand=True)
    app._text_output.configure(state="disabled")

    # 问题页
    f_prob = ttk.Frame(nb)
    nb.add(f_prob, text=T("问题"))
    app._text_problems = tk.Text(
        f_prob, wrap="none", width=48, height=10, font=("Consolas", UI_FONT_SIZE),
        bg=theme_get("panel_bg"), fg=theme_get("fg"), borderwidth=0,
        highlightthickness=0, spacing1=2, spacing3=2)
    sb2 = ttk.Scrollbar(f_prob, orient="vertical",
                        command=app._text_problems.yview)
    app._text_problems.configure(yscrollcommand=sb2.set)
    sb2.pack(side="right", fill="y")
    app._text_problems.pack(side="left", fill="both", expand=True)
    app._text_problems.configure(state="disabled")
    app._text_problems.tag_configure("warn", foreground=theme_get("warn"))
    app._text_problems.tag_configure("error", foreground=theme_get("danger"))
    app._text_problems.tag_configure("info", foreground=theme_get("accent"))

    # 进度页
    f_prog = ttk.Frame(nb)
    nb.add(f_prog, text=T("进度"))
    app._text_progress = tk.Text(
        f_prog, wrap="none", width=48, height=10, font=("Consolas", UI_FONT_SIZE),
        bg=theme_get("panel_bg"), fg=theme_get("fg"), borderwidth=0,
        highlightthickness=0, spacing1=2, spacing3=2)
    sb3 = ttk.Scrollbar(f_prog, orient="vertical",
                        command=app._text_progress.yview)
    app._text_progress.configure(yscrollcommand=sb3.set)
    sb3.pack(side="right", fill="y")
    app._text_progress.pack(side="left", fill="both", expand=True)
    app._text_progress.configure(state="disabled")

    # 底部：清空 / 关闭
    bottom = ttk.Frame(app._log_panel)
    bottom.pack(fill="x", padx=4, pady=(0, 4))
    ttk.Button(bottom, text=T("清空当前"), width=10,
               command=app._clear_current_log_tab).pack(side="left")
    ttk.Button(bottom, text=T("复制全部"), width=10,
               command=app._copy_current_log_tab).pack(side="left",
                                                        padx=(4, 0))
    ttk.Button(bottom, text=T("▲ 收起"), width=8,
               command=app._hide_log_panel).pack(side="right")


def _toggle_log_panel(app, which="output"):
    if app._log_panel_visible:
        app._hide_log_panel()
        return
    app._show_log_panel(which)


def _show_log_panel(app, which="output"):
    try:
        app._log_panel.pack(fill="x", side="bottom",
                             before=app.status.master)
    except Exception:
        try:
            app._log_panel.pack(fill="x", side="bottom")
        except Exception:
            return
    app._log_panel_visible = True
    try:
        idx = {"output": 0, "problems": 1, "progress": 2}.get(which, 0)
        app._log_nb.select(idx)
    except Exception:
        pass
    try:
        app._output_btn.config(text=T("📋 输出 ▼"))
    except Exception:
        pass


def _hide_log_panel(app):
    try:
        app._log_panel.pack_forget()
    except Exception:
        pass
    app._log_panel_visible = False
    try:
        app._output_btn.config(text=T("📋 输出 ▲"))
    except Exception:
        pass


def _clear_current_log_tab(app):
    try:
        idx = app._log_nb.index(app._log_nb.select())
    except Exception:
        idx = 0
    widget = (app._text_output, app._text_problems,
              app._text_progress)[idx]
    try:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.configure(state="disabled")
    except Exception:
        pass
    if idx == 1:
        app._problem_count = 0
        app._update_problem_badge()
    if idx == 0:
        app._output_lines = 0
    if idx == 2:
        app._progress_lines = 0


def _copy_current_log_tab(app):
    try:
        idx = app._log_nb.index(app._log_nb.select())
    except Exception:
        idx = 0
    widget = (app._text_output, app._text_problems,
              app._text_progress)[idx]
    try:
        content = widget.get("1.0", "end")
        app.root.clipboard_clear()
        app.root.clipboard_append(content)
        app.set_status(T("已复制到剪贴板"))
    except Exception:
        pass


def _usage_view_hint(app):
    """★ 2026-10-06：记下「出错时用户在看哪个视图」。

    ★★ 只返回**视图种类**这种非隐私信息，绝不带路径 / 文件名 / 标签名。
       （外面查到的血泪教训：带路径的日志用户不敢发给别人看。）
    """
    try:
        vm = str(getattr(app, "view_mode", "") or "")
        m = {"dir": "文件夹", "cat": "分类", "all": T("全部文件")}
        base = m.get(vm, vm or "未知")
        if getattr(app, "net_browse_mode", "") == "real":
            base += "+网盘实时"
        return base
    except Exception:
        return ""


def _log_problem_is_echo(app, text):
    """★ 2026-10-06：判断这条「问题」是不是刚从 note_swallowed 弹过来的。

    为什么要这个：`note_swallowed` 出错时会调 `log_problem` 把话弹到
    「问题」面板 —— 于是**同一件事走了两条路进用法记录**，
    汇总出来的次数会翻倍（实测：一次错误记成 2 条）。

    ★★ 这里踩了一次，写清楚：**不能去读账本文件来判断**。
       因为 `note_swallowed` 只是把记录塞进**内存缓冲**，
       要等攒够 20 条或过 5 秒才落盘。而 log_problem 是**紧接着**
       被调用的 —— 那时候磁盘上根本没有那条 swallow 记录，
       拿文件去比对永远比不着（实测：还是记重了）。

       正确的判据在**内存**里：`note_swallowed` 更新过的
       `_SWALLOW_LAST`（"刚才谁在哪儿报的"）。拿它比一下就行。
    """
    try:
        t = str(text or "")
        if not t:
            return False
        last = _SWALLOW_LAST.get("where") or ""
        if last and t.startswith(str(last) + "："):
            return True
        return False
    except Exception:
        # ★ 判不出来就当**不是**回声（宁可多记一条，也别把真问题漏了）
        return False


def _update_problem_badge(app):
    try:
        n = app._problem_count
        if n > 0:
            app._problem_btn.config(text=T("🔔 问题 {n}", n=n))
        else:
            app._problem_btn.config(text=T("🔔 问题 0"))
    except Exception:
        pass


def _stuck_watchdog(app):
    """★ 盯着「界面卡了多久」。**报一笔这件事本身不许拖慢界面。**"""
    while True:
        try:
            time.sleep(1.0)
            # ★ v25 补丁18：窗口开始关了 → 这个线程立刻收工。
            if not app._ui_alive():
                return
            now = time.time()
            # ★★ 2026-10-06：时间戳现在来自「打卡线程」（见 _heartbeat_start）——
            #   它不依赖界面闲不闲，所以「切文件切得快」不会再被误判。
            gap = now - float(_HEART.get("stamp", now) or now)
            if gap >= 3.0 and not _HEART.get("reported"):
                # ★ 正在扫索引 / 后台比对目录时，界面短暂卡一下是正常的
                try:
                    if INDEX_SCAN_EVENT.is_set():
                        continue
                    if getattr(app, "_bg_scan_running_dir", None):
                        continue
                except Exception:
                    pass
                _HEART["reported"] = True
                msg = (f"界面无响应 {gap:.1f} 秒"
                       f"（可能正在做重活；点右下角「问题」查看日志）")
                # ★★ 关键：**只排队，不直接动手** ——
                #   直接 app.log_problem(...) 是主线程的活儿（还碰 Tk），
                #   界面正忙的时候干这个 = 火上浇油（实测一次要 1.36 秒）。
                _bg_post(app.log_problem, msg, "warn")
                _bg_post(app.log_output, msg)
        except Exception:
            pass


def _install_error_spy(app, *a, **k):
    # ★★ 转发到 `AIxiede拆分开/程序分块/面板_插件挂载.py`
    #   ★ 保留同名方法 = **所有调用方不用改**（稳定接口）
    return _面板插件挂载._install_error_spy(app, *a, **k)


def _startup_health_check(app):
    """开机后轻轻看一眼「有没有在偷偷出错」。

    故意做得非常轻：只读内存里的计数，不碰数据库、不扫盘。
    也故意**不打扰用户** —— 只写进「问题」面板，点开才看细节。

    ★★ 2026-10-06：顺手**按用户的缓存设置清一次旧缓存**（后台线程，
       绝不拖慢启动）。清理规则见「界面 → 📥 网盘预览缓存设置」。
    """
    # ★ 先丢一个后台线程去清缓存（不阻塞开机）
    try:
        import threading as _th

        def _clean():
            try:
                msg = _cache_clean_old()
                if msg and "不用清" not in msg and "很干净" not in msg:
                    app.log_problem(T("缓存清理：") + msg, level="info")
            except Exception:
                pass

        _th.Thread(target=_clean, daemon=True, name="缓存清理").start()
    except Exception:
        pass

    try:
        rep = swallowed_report()
        if not rep:
            return
        total = sum(n for _, n in rep)
        app.log_problem(
            f"本次启动发现 {len(rep)} 类「没吭声的小毛病」（共 {total} 次）。"
            f"多半不影响使用，但会积少成多 —— 需要时把这清单发我。",
            level="info")
    except Exception:
        pass


def dump_swallowed_report(app):
    """把「哪些地方在偷偷出错」整理成人话，供排查用。

    用户可能想要一份能直接发出去的清单（他自己看不懂代码，
    所以输出必须是中文说法 + 次数）。
    """
    try:
        rep = swallowed_report()
        if not rep:
            return "程序到目前为止没有发现「偷偷出错」的地方。"
        out = ["以下地方出过错（次数越多越值得查）：", ""]
        for name, n in rep[:60]:
            out.append(f"  · {name} —— {n} 次")
        if len(rep) > 60:
            out.append(f"  …还有 {len(rep) - 60} 类")
        return "\n".join(out)
    except Exception as e:
        return f"整理清单时出错：{e}"


def _refresh_dialog_hints(app):
    """刷一下打开着的「自动标签规则」/「索引管理」里的闲时信息。"""
    try:
        children = list(app.root.winfo_children())
    except Exception:
        return
    for w in children:
        if not isinstance(w, (AutoTagRulesDialog, IndexManagerDialog)):
            continue
        try:
            w._refresh_idle_hint()
        except Exception:
            pass
        try:
            w._reload()
        except Exception:
            pass
