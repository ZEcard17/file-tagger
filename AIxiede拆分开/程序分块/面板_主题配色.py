# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「主题配色」这组方法。

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
_MUTABLE = ['THEME_NAME']
_NEED = ['T', 'THEME_NAME', 'apply_theme', 'apply_theme_names', 'make_background_layer', 'note_swallowed', 'save_ui_setting', 'theme_get', 'theme_has']
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


def _fill_theme_menu(app, menu):
    """★★ 把"现在有哪些皮肤"**重新列一遍**（每开一次菜单跑一次）。

    ★★ 为什么需要"每次重建"（实测踩出来的）：
      · 菜单是**程序启动时**建的；
      · 而插件是**建完菜单之后**才加载的 ——
        插件注册的皮肤**在那时还不存在** → 菜单里**列不出来**。
      · 实测：插件注册的配色**确实进了 `_THEMES`**（`apply_theme_names()`
        能看到它），**但菜单里看不到** —— 因为菜单是"建的时候拍了个快照"。
    ★ 修法：**每次点开菜单重新问一遍** ——
      · 插件的皮肤自动出现
      · 以后"运行时装皮肤"也自动出现
      · 这段代码**永远不用改**（这就是"接口"的价值）
    ★ 为什么先 `delete(0, "end")` 再建：
      不删的话每开一次就**多一份**（菜单越来越长）。
    """
    try:
        menu.delete(0, "end")
    except Exception:
        pass
    try:
        names = apply_theme_names()
    except Exception:
        names = [("light", "light"), ("dark", "dark")]
    _ICON = {"light": "☀ ", "dark": "🌙 "}
    for key, lbl in names:
        try:
            menu.add_radiobutton(
                label=_ICON.get(key, "🎨 ") + lbl,
                value=key, variable=app.theme_var,
                command=lambda k=key: app.set_theme(k))
        except Exception:
            pass


def _apply_background(app):
    """★★ **铺背景图**（用户要的"搞个图片当背景"）。

    ★ 什么时候调：
      ① 启动时（`__init__` 里，界面建好之后）
      ② 换皮肤时（皮肤可能带自己的背景图）
      ③ 用户手动"选一张背景图"时

    ★ 怎么铺：
      · 用 `make_background_layer()` 铺在 **`app.root` 的最底层**
      · 然后**把主界面那几块"抬上来"** ——
        不然图会盖住 `paned`（因为 `place` 的层级可能比 `pack` 高）
      ★ `layer.lower()` 已经压到底了，但 Tk 的 `place` / `pack`
        **混用时层级不完全可靠** → 所以这里**再显式 `lift()` 一次**主块。

    ★★ 失败兜底：图读不了（被删了/挪了）→
      `make_background_layer` 会铺一块**兜底色**（不会露出一片白，
      夜间模式下那会很难看 —— 用户报过好几次）。
    """
    path, mode, blur, _pa = app._theme_bg_spec()
    # ★ 先把旧的背景层拆掉（换皮肤/换图时不能叠着）
    try:
        old = getattr(app, "_bg_layer", None)
        if old is not None:
            old.destroy()
    except Exception:
        pass
    app._bg_layer = None
    if not path:
        return
    try:
        fallback = theme_get("win_bg")
        layer = make_background_layer(app.root, path, mode, blur,
                                      fallback_bg=fallback)
        app._bg_layer = layer
        if layer is None:
            return
        # ★ 把主界面抬到图上（不然图盖住内容）
        for nm in ("_top_bar", "_top_bar2", "paned"):
            try:
                w = getattr(app, nm, None)
                if w is not None:
                    w.lift()
            except Exception:
                pass
        # ★ 状态栏也要抬（它在最底下那一行）
        try:
            for ch in app.root.winfo_children():
                if ch is not layer:
                    try:
                        # ★ 只抬"直接子控件"里不是背景层的那几个
                        ch.lift()
                    except Exception:
                        pass
        except Exception:
            pass
        app._apply_panel_blend()
    except Exception as _e:
        note_swallowed(T("铺背景图失败"), _e)


def _refresh_menu_states(app):
    """★ 把每个开关项的圆点和颜色刷成当前状态。

    ★ 什么时候调：
      · 菜单要弹出来之前（`postcommand`，见菜单构造处）
      · 任何一个开关切换之后
    这样用户**打开菜单的那一瞬间**看到的就是真实状态。

    ★★ 用**记下来的项序号**定位（`app._menu_state_map`），
      不按 label 找 —— 因为本函数**会改 label**，
      按 label 找的话刷一次之后就再也找不到了（踩过）。
    """
    try:
        reg = getattr(app, "_menu_state_map", None) or []
        reg2 = getattr(app, "_menu_state_map2", None) or []
    except Exception:
        return
    for menu, items in ((getattr(app, "_m_switches", None), reg),
                        (getattr(app, "_m_settings", None), reg2)):
        if menu is None:
            continue
        for item in items:
            # 兼容两种登记格式：3 元组用外层菜单，4 元组自带菜单
            if len(item) == 4:
                idx, getter, name, menu_use = item
            else:
                idx, getter, name = item
                menu_use = menu
            try:
                on = bool(getter())
            except Exception:
                continue
            col = app.COLOR_ON if on else app.COLOR_OFF
            try:
                menu_use.entryconfigure(
                    idx,
                    label="%s %s" % (app.DOT_ON if on else app.DOT_OFF,
                                     name),
                    foreground=col)
            except Exception:
                continue


# ---------- ★★ 2026-10-06：皮肤（白天 / 夜间） ----------
def set_theme(app, name, save=True):
    """换皮肤：整片界面立刻变。

    用户要求：「写套夜间皮肤，现在这个不开灯有点闪」。

    ★★ 2026-10-08 改成**支持任意已注册的皮肤**（用户要"预留自定义皮肤入口"）：
      原来这里写的是 `if name not in ("light", "dark")` ——
      **皮肤名硬编码**，以后加了自定义皮肤**会被这里打回去**（变回 light）。
      → 改成问 `theme_has(name)`（它读 `_THEMES`）。
      ★ 这样 `register_theme("my_skin", {...})` 一注册，
        这里就**自动认得**，一行都不用改。
    """
    try:
        if not theme_has(name):
            name = "light"
        app.set_status(T("正在换皮肤…"))
        apply_theme(app.root, name)
        # ★ 换完皮肤后，把「靠自己重画」的那几块重新画一遍 ——
        #   它们不是普通控件，颜色是代码画上去的，扫控件扫不到。
        for fn in (app._retheme_custom_parts,):
            try:
                fn()
            except Exception as _e:
                note_swallowed(T("换皮肤：重画自定义区块失败"), _e, quiet=True)
        try:
            if hasattr(app, "theme_var"):
                app.theme_var.set(name)
        except Exception:
            pass
        if save:
            try:
                save_ui_setting("theme", name)
            except Exception as _e:
                note_swallowed(T("记住皮肤设置失败（下次打开可能变回白天）"), _e,
                               level="warn")
        app.set_status("皮肤已切换：%s"
                        % ("夜间 🌙（晚上不刺眼）" if name == "dark"
                           else "白天 ☀"))
        try:
            app.log_output("🎨 已切换皮肤：%s"
                            % ("夜间" if name == "dark" else "白天"))
        except Exception:
            pass
        return True
    except Exception as _e:
        note_swallowed(T("换皮肤失败"), _e)
        return False


def toggle_theme(app):
    """一键在白天 / 夜间之间来回切。"""
    cur = "dark" if THEME_NAME == "light" else "light"
    app.set_theme(cur)
