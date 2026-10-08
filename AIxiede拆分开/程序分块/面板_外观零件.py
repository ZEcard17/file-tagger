# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「外观零件」这组方法。

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


# ======================================================================
#  ★★★ 2026-10-08：**背景图 + "假毛玻璃"**（用户要的美化效果）
# ======================================================================
# ==========================================================================
#  ★★★ 要向主程序借的名字（★ 搬方法组的**关键**，错题本 #166）★★★
#  --------------------------------------------------------------------------
#  ★ 搬走的方法用了一堆**主程序自己造的东西**（`theme_get` / `T` / 常量…）。
#    这些**新文件里没有** → ★★ 一调那个方法就 `NameError` ——
#    而且**平时看不出来**（只有真点到那个按钮才炸）。
#  ★ 做法跟拆类一样：主程序启动时把「自己」交进来（`_set_app`）。
# ==========================================================================
_MUTABLE = ['THEME_NAME']
_NEED = ['BG_MODES', 'FileList', 'T', 'THEME_NAME', '_set_native_dark', '_style_all_widgets', '_themes_now', 'apply_themed', 'average_color_of_image', 'blend_color_over', 'load_ui_setting', 'note_swallowed', 'theme_get']
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


def _theme_bg_spec(app):
    """★ 从当前皮肤里读"美化项"（图 / 模式 / 模糊 / 面板透明感）。

    ★ 皮肤里这些键都是**可选**的 —— 没有就表示"不启用背景图"：
        `background_image` / `background_mode` / `background_blur`
        `panel_alpha`
    ★ 返回 `(图片路径, 模式, 模糊半径, 面板透明感 0~100)`；
      没有图就返回 `(None, ..., 0)`。

    ★★ 2026-10-08：**再读一处** —— 用户在「设置 → 背景图」里手选的那张。
      ★ 优先级：**用户手选的 > 皮肤自带的**
        （用户刚选完图，当然该用他的；皮肤自带的只是"默认长相"）。
      ★ 为什么要两处：用户说「他们挺喜欢搞个图片当背景」——
        **最自然的用法是"我自己挑一张"**，不该逼他先做一套皮肤。
    """
    try:
        th = _themes_now()
        path = str(th.get("background_image") or "").strip()
        mode = str(th.get("background_mode") or "cover").strip().lower()
        try:
            blur = float(th.get("background_blur") or 0)
        except Exception:
            blur = 0.0
        try:
            pa = float(th.get("panel_alpha") or 0)
        except Exception:
            pa = 0.0
        # ★ 用户手选的优先（存在 custom_themes 的 `__background__` 里）
        try:
            data = load_ui_setting("custom_themes", None)
            if isinstance(data, dict):
                u = data.get("__background__") or {}
                if isinstance(u, dict) and u.get("background_image"):
                    path = str(u.get("background_image") or "").strip()
                    mode = str(u.get("background_mode") or mode).lower()
                    try:
                        blur = float(u.get("background_blur") or blur)
                    except Exception:
                        pass
                    try:
                        pa = float(u.get("panel_alpha") or pa)
                    except Exception:
                        pass
        except Exception:
            pass
        if mode not in BG_MODES:
            mode = "cover"
        return (path or None, mode, max(0.0, blur),
                max(0.0, min(100.0, pa)))
    except Exception:
        return (None, "cover", 0.0, 0.0)


def _apply_panel_blend(app):
    """★★ **面板色"看着半透明"** —— 这一步不做，背景图基本看不见。

    ★ 为什么需要（实测出来的）：
      Tk 的控件**没有透明这回事** —— 面板有底色就是实色，
      **背景图只有"控件之间的缝"能露出来**。
      → 所以要让"看着像半透明"，只能**把面板色往图片的颜色上调**。

    ★ 怎么做：
      ① 取背景图的**平均色**（缩到 1x1，最省事也最准）
      ② 把"面板色"按 `panel_alpha` 混进这个平均色
         · `panel_alpha=0`   → 面板是原来的实色（看不出背景图）
         · `panel_alpha=60`  → 面板明显偏图片色（像透了一层）
         · `panel_alpha=100` → 面板几乎就是图片色（**字可能看不清**）
      ③ 把混好的颜色**临时覆盖到主题表里** ——
         这样"所有读 `theme_get()` 的地方"**自动**用上新颜色，
         **不用改任何调用方**（跟自定义皮肤一个套路）。

    ★★ 为什么是"临时覆盖"而不是"改皮肤表本身"：
      皮肤表是**共享的**（`light` / `dark` 就一份）——
      直接改它会把"原配色"弄丢（切回去就回不来了）。
      → 所以先把**原始色存一份**，混完写进"当前皮肤"；
        换皮肤 / 关背景图时**恢复**（见 `_restore_panel_colors`）。
    """
    path, _mode, blur, pa = app._theme_bg_spec()
    # ★ 先把上次混过的恢复（不然越混越偏）
    app._restore_panel_colors()
    if not path or pa <= 0:
        return
    try:
        avg = average_color_of_image(path, blur)
        if not avg:
            return
        th = _themes_now()
        # ★ 要调的"面板类"颜色（这几块正好是"盖在背景上的面"）
        keys = ("win_bg", "card_bg", "panel_bg", "panel_bg2", "text_bg",
                "canvas_bg", "stripe_bg")
        saved = {}
        k = pa / 100.0
        for key in keys:
            try:
                old = th.get(key)
                if not old:
                    continue
                saved[key] = old             # ★ 存原始色（恢复用）
                th[key] = blend_color_over(old, avg, k)
            except Exception:
                pass
        # ★ 存起来，换皮肤时恢复
        app._blended_saved = saved
    except Exception as _e:
        note_swallowed(T("调和面板色失败（背景图会看不太出来）"), _e)


# ---------- ★★ 2026-10-03：分栏条「看得见 + 拖得着」 ----------
def _style_sashes(app):
    """把四个大分区之间的分栏条画清楚一点（Tk 默认那一条几乎看不见）。

    ★★ 2026-10-06：现在这里只是「按当前皮肤摆一次」的**薄薄一层** ——
      真正的样式表在 `_style_all_widgets()` 里（那边连按钮、滚动条、
      输入框、文件树、菜单全都一起管），皮肤一换整片都会跟着换。
      这样做的好处：以后加皮肤只要多写一张颜色表，不用改这里。
    """
    try:
        _style_all_widgets(app.root, THEME_NAME)
    except Exception as _e:
        note_swallowed(T("给界面套皮肤失败（会用 Tk 默认外观）"), _e)
    # ★★★ 2026-10-07 **修「状态栏那排按钮的彩色时有时无」**（用户报）★★★
    #   用户原话：「撤销 / 标签盒 / 标签库 / 标签条 / 预览 / 顶部 / 网盘
    #   **是彩色的，然后点了几下就又不彩了**，问题什么的也又变白了」。
    #
    #   ★ 真因（实测追出来的）：
    #     `_make_tone_styles()`（注册 `ToneTag.TButton` 那五个样式）
    #     **只在两个地方被调**：
    #       ① 建状态栏按钮的那一刻（`_build_status_bar` 里）
    #       ② 换皮肤之后（`_retheme_custom_parts` 里，行 ~27890）
    #     —— **`_apply_theme()` 这条路上没有它！**
    #     而 `_apply_theme()` 会调 `_style_all_widgets()`，
    #     那里重设了 `TButton` 的基础样式 ——
    #     **把刚注册的五个色调样式覆盖/冲掉了**。
    #
    #   ★ 实测证据：
    #       启动后立刻查 → `ToneTag.TButton configure = {}`（**空的！**）
    #       手动再调一次 `_make_tone_styles()` → `bg=#3b3050` ✔
    #     → 所以：**启动时没颜色；切一次皮肤才有颜色；
    #       之后某个操作又走 `_apply_theme` → 颜色又没了。**
    #       这跟用户描述的"时有时无"**完全对得上**。
    #
    #   ★ 修法：**在 `_style_all_widgets()` 之后立刻重注册一次** ——
    #     保证基础样式先铺好、再盖上我们的色调样式（顺序不能反）。
    try:
        app._make_tone_styles()
    except Exception as _e:
        note_swallowed(T("状态栏按钮分组底色注册失败"), _e, quiet=True)
    # ★★ 2026-10-06：**把标题栏 / 菜单栏染深**。
    #   ★★ 这里踩过一个坑，写清楚：一开始就在这儿直接调，**没生效**
    #      （截图看标题栏还是白的）。原因是：
    #      `_build_ui()` 跑在 `mainloop()` **之前**，这时候窗口
    #      **还没映射到屏幕上**，DWM 拿它没办法 —— 调用返回 0（成功）
    #      但不起作用，**是那种最坑的"静默失败"**。
    #      （对照实验：单独写个小窗口，先 `root.update()` 再调，
    #        标题栏立刻变深 (24,24,24) —— 证明接口本身没问题。）
    #   ★ 正解：**等窗口真的显示出来再调**。用 `after(0, ...)`
    #     把这件事推到事件循环里去（那时窗口已经映射好了）。
    #     `after(0)` 而不是延迟几百毫秒：尽量早点染，
    #     免得用户看见"先白一下再变黑"。
    try:
        _dark_now = (THEME_NAME == "dark")
        app.root.after(0, lambda d=_dark_now: _set_native_dark(
            app.root, d))
    except Exception as _e:
        note_swallowed(T("标题栏/菜单栏没能染成深色（老系统上正常）"), _e,
                       quiet=True)


def _retheme_custom_parts(app):
    """★★ 换皮肤后，把「代码自己画颜色」的那几块重新画一遍。

    它们不是普通控件（颜色不是控件属性，是画上去的），
    上面那套「扫控件换色」扫不到 —— 必须自己重画。这里逐块叫一下，
    每一块单独包 try：**坏一块不影响别的**。
    这也是本程序一贯的写法（见「出错必留痕」那段）。
    """

    # ★★ 2026-10-07 新增：把**登记过的 Toplevel** 的底色刷一遍。
    #   为什么需要：`tk.Toplevel` 是原生窗口，底色不跟 ttk 主题走；
    #   建的时候设了 `bg=`，但**窗口开着切主题**时不会自己变 ——
    #   必须在这里再刷一次，否则"切了夜间、那个窗口还是白的"。
    #
    # ★★ 2026-10-08 增强：**不光刷底色，还要问窗口"你自己要不要重刷"**。
    #   ★ 为什么（用户报「索引管理切换夜间皮肤显示不对」，待清算 #8-②）：
    #     有些窗口（比如 `IndexManagerDialog`）**里面大量用原生 tk 控件**
    #     （`tk.Text` / `tk.Frame`）—— 它们的颜色是"建的时候设死的"，
    #     光刷**窗口自己**的底色**不够**，里面的控件还是旧配色。
    #   ★ 所以定一个约定：**窗口想要跟着皮肤变，就实现一个
    #     `_apply_theme()`**（无参数）—— 这里发现就调它。
    #     ★ 这样"怎么刷"由窗口自己决定，主程序不用知道它的内部结构
    #       （这也是"留接口"的思路，用户前面提过）。
    try:
        for _w in list(getattr(app, "_theme_windows", []) or []):
            try:
                if not _w.winfo_exists():
                    continue
                try:
                    _w.configure(bg=theme_get("win_bg"))
                except Exception:
                    pass
                # ★ 问窗口"你自己要不要重刷"
                _fn = getattr(_w, "_apply_theme", None)
                if callable(_fn):
                    try:
                        _fn()
                    except Exception:
                        pass
            except Exception:
                pass
    except Exception:
        pass
    # 顺手把「其他类自己建的窗口」也刷一下（它们把引用挂在 _theme_windows
    # 上的方式一样，只是 app 不是主程序 —— 那就在各自的类里处理，
    # 这里只管主程序自己开的那些）。

    # ★★ 2026-10-07 新增：**底部「输出 / 问题 / 进度」这三个 tk.Text**
    #   必须在这里重刷颜色！
    #   ★★ 为什么（这是个"第一次打开是白的、第二次才好"的怪 bug）：
    #     `_build_log_panel()` 在 **26840 行**被调，
    #     而"读出用户存的皮肤 + 套上去"在 **27116 ~ 27300 行** ——
    #     **也就是说：建这三个 Text 的时候，主题还是"白天"** →
    #     它们拿到了白底深字 → 后面套夜间时，
    #     `_retheme_tree()` 那套"扫控件换色"**扫不到 tk.Text 的文字色**
    #     （它只按"原始单据"翻颜色，而这几个控件的底色被别的逻辑改过），
    #     于是**第一次开就是白的**。
    #   ★ 第二次打开为什么好：设置文件里已经有 theme=dark，
    #     启动时 `THEME_NAME` 一开始就是 dark → 建 Text 时直接拿到深色。
    #   ★ 修法：**在这儿显式重刷一遍**（不依赖那套自动扫描）——
    #     这几个控件的颜色本来就从 `theme_get` 取，重设一次就对了。
    try:
        for _t, _bgkey in ((getattr(app, "_text_output", None),
                            "panel_bg2"),
                           (getattr(app, "_text_problems", None),
                            "panel_bg"),
                           (getattr(app, "_text_progress", None),
                            "panel_bg")):
            if _t is None:
                continue
            try:
                _t.configure(bg=theme_get(_bgkey), fg=theme_get("fg"),
                             insertbackground=theme_get("fg"),
                             selectbackground=theme_get("select_bg"),
                             highlightbackground=theme_get("line"))
            except Exception:
                pass
    except Exception:
        pass
    # ★ 顺带把「进程/问题/输出」的页签底也刷一下（ttk.Notebook 内部部件）
    try:
        if getattr(app, "_log_nb", None) is not None:
            app._log_nb.configure(style="TNotebook")
            for _f in app._log_nb.winfo_children():
                try:
                    _f.configure(style="TFrame")
                except Exception:
                    pass
    except Exception:
        pass

    # ★★ 2026-10-07 新增：**先把"登记过角色"的控件按当前皮肤刷一遍**。
    #   这是新的统一机制（见 `register_themed` 的说明）——
    #   以后新增控件只要 `register_themed(w, "card")`，这里自动管。
    try:
        apply_themed()
    except Exception:
        pass

    # ★★ 2026-10-08 新增：**换皮肤时也让图标尺寸重新按字高算一遍**。
    #   为什么换皮肤要重算图标：本程序换皮肤时会走
    #   `_style_all_widgets`（重设各种 ttk 样式、字体），
    #   **字高有可能跟着变**（不同主题下可能选到不同的字体度量）——
    #   而图标尺寸是**按字高算的**（待清算 #16 的修法），
    #   不清缓存就会"字变了、图标还是旧的"。
    #   ★ 一行成本，换"永远齐平"。
    try:
        FileList.refresh_icon_sizes()
    except Exception:
        pass

    # ★★ 2026-10-08 新增：**悬浮球也跟着换皮肤**。
    #   ★ 它是个**无边框独立窗口**，主程序那套"扫控件换色"扫不到它
    #     （跟 `IndexManagerDialog` 是同一个道理，见错题本 #123）——
    #     所以定个约定：**窗口想跟着皮肤变，就实现 `apply_theme()`**。
    #   ★★★ 2026-10-08 **后来改了**（用户选 B B B）★★★
    #     ★ 用户原话：「有球自己的皮肤也有主界面的皮肤，
    #       **两个都搞好入口**，但是**是完全不一样的**，你可别搞混了啊」
    #       然后他选了：② 球默认独立 ③ **永远不跟**主界面
    #     → 所以这里**不再**调球的 `apply_theme()`
    #       （球自己那套皮肤归 `set_ball_style()` 管）。
    #     ★ 但我**保留**这个调用位置、只是注释掉 —— 万一以后
    #       用户想加一个"球跟随主界面"的选项，**改一行就能回来**。
    #       （"留位置、不提前造"）
    # try:
    #     _fb = getattr(app, "floating_ball", None)
    #     if _fb is not None:
    #         _fb.apply_theme()
    # except Exception:
    #     pass

    # 文件列表 / 瀑布流（底色、文件名颜色、网格线都是画上去的）
    try:
        # ★★ 2026-10-07 **修一个一直在报错的 bug**（账本里 8 次）★★
        #   原来这里写的是 `app.list_frame._redraw()` ——
        #   而 `list_frame` 只是个 **ttk.Frame 空容器**（27242 行建的），
        #   **它没有 `_redraw` 方法** → 每次都抛
        #     `AttributeError: 'Frame' object has no attribute '_redraw'`
        #   → 被下面那个 except 吞掉 → **文件列表的夜间配色从来没刷上**。
        #   ★ 真正的列表对象是 `app.file_list`（一个 `FileList`，
        #     它才有 `_redraw`，见 10255 行）。
        #   ★ 后果（用户报的）：切皮肤后**文件列表还是白底黑字**；
        #     而且这段一报错，**后面该刷的（状态栏/底部面板）也跟着断**。
        lf = getattr(app, "file_list", None) or getattr(app, "list_frame", None)
        if lf is not None and hasattr(lf, "_redraw"):
            lf._redraw()
    except Exception as _e:
        note_swallowed(T("换皮肤：重画文件列表失败"), _e, quiet=True)
    # 左侧分类库的每条（名字、图标底色是画上去的）
    try:
        sb = getattr(app, "sidebar", None)
        if sb is not None and hasattr(sb, "_redraw_header"):
            sb._redraw_header()
    except Exception:
        pass
    # 预览窗格（画布底、类型信息、翻页条）
    try:
        pv = getattr(app, "preview", None)
        if pv is not None:
            if hasattr(pv, "_repaint_theme"):
                pv._repaint_theme()
    except Exception as _e:
        note_swallowed(T("换皮肤：重画预览区失败"), _e, quiet=True)
    # 标签条（胶囊的底色是按标签颜色算的，得重刷）
    try:
        app._restyle_tagbar()
    except Exception:
        pass
    # 状态栏
    try:
        app._on_status_bar_config()
    except Exception:
        pass
    # ★★ 2026-10-07 新增：状态栏那排按钮的**分组底色**要重刷。
    #   为什么必须放这儿：ttk 样式的颜色是**注册时定死的** ——
    #   不重注册的话，从浅色切到夜间，那排按钮**还是白底**，
    #   在深色状态栏上像贴了几块膏药。
    try:
        app._make_tone_styles()
        # 样式名没变（还是 ToneTag.TButton 那些），重注册即可生效 ——
        # 不用重新给按钮挂 style。但**已经挂在按钮上的引用**要更新一下
        # （ttk 是按名字查样式的，所以其实自动就生效了）。
    except Exception:
        pass
    # ★★ 2026-10-07 新增：「文件 · 共 N · 未打标签 N · 仅中间标签 N」这几个
    #   标签。**用户报的"夜间看着不够亮、有时候黑了东点西点又好了"就是这个** ——
    #   它们的颜色原来是写死的、而且**从没登记过换皮肤重刷**，
    #   所以切到夜间它们不变，得靠某个偶然的重画才补上。
    try:
        app._retheme_stats_labels()
    except Exception:
        pass


def _make_tone_styles(app):
    """★ 给状态栏按钮注册"带底色"的 ttk 样式（按色调分组）。

    ★★ 2026-10-07 新增。用户要求：「给按钮增加底色什么的」，
      并且**按功能分组配色**：
        · 标签盒 / 标签库 / 标签条 → **一个色调**（紫，都是"标签"）
        · 预览 / 顶部             → **一个色调**（蓝，都是"看/布局"）
        · 网盘                    → **一个色调**（青，"数据来源"）
        · 问题                    → **一个色调**（橙红，"要你看的"）
        · 撤销                    → 单独一个（灰黄，"补救"）

    ★★ 为什么不能直接 `configure(background=...)`：
      **ttk 的 clam 主题不吃 background** —— 试过，`w.configure(
      background="#xxx")` 一点反应都没有（ttk 控件的颜色由 style 决定）。
      **正确做法：每个色调注册一个 `xxx.TButton` 样式**，
      再用 `style=` 挂到按钮上。这也是 ttk 唯一的正规路子。

    ★ 深浅两套都要注册（切皮肤时一起换）—— 所以这里读 `theme_get`，
      并且在 `apply_theme` 之后会**重跑一遍**（见 `_retheme_custom_parts`）。
    """
    try:
        st = ttk.Style()
    except Exception:
        return {}
    dark = (str(theme_get("name") or "") == "dark")
    # 每个色调：底色 / 悬停色 / 文字色
    #   ★ 夜间用"深一点的底色 + 亮一点的字"，浅色反过来 ——
    #     不然夜间会刺眼、浅色会糊（老毛病了，见错题本 #75）。
    if dark:
        spec = {
            "tag":     ("#3b3050", "#4a3d63", "#d9cdf0"),   # 紫
            "layout":  ("#26384f", "#2f4460", "#bcd6f5"),   # 蓝
            "net":     ("#1f3f3c", "#2a514d", "#a8ded6"),   # 青
            "problem": ("#4a2f26", "#5c3a2e", "#f0bda8"),   # 橙红
            "undo":    ("#3d3a26", "#4d4a30", "#e8dfae"),   # 灰黄
        }
    else:
        spec = {
            "tag":     ("#e8ddf7", "#dccbf2", "#4a2f7a"),   # 紫
            "layout":  ("#dcebfb", "#c9e0f7", "#1e4b80"),   # 蓝
            "net":     ("#d4f0ec", "#bfe6e0", "#0f5a52"),   # 青
            "problem": ("#fbe3da", "#f7d0c2", "#8a3a1e"),   # 橙红
            "undo":    ("#f5eecb", "#eee3b0", "#6b5a12"),   # 灰黄
        }
    out = {}
    for tone, (bg, hv, fgc) in spec.items():
        name = "Tone%s.TButton" % tone.capitalize()
        try:
            st.configure(name, background=bg, foreground=fgc,
                         borderwidth=0, focuscolor=bg, relief="flat",
                         padding=(8, 4))
            # 悬停 / 按下 / 禁用 三态都要给，不然一悬停就变回灰白
            st.map(name,
                   background=[("pressed", hv), ("active", hv),
                               ("disabled", bg)],
                   foreground=[("disabled", theme_get("fg_dim"))],
                   relief=[("pressed", "flat"), ("active", "flat")])
            out[tone] = name
        except Exception:
            continue
    return out
