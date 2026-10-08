# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「面板布局」这组方法。

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
_MUTABLE = ['BOLD', 'FONT', 'UI_FONT_SIZE', 'UI_FONT_SIZE_SMALL']
_NEED = ['BOLD', 'FONT', 'T', 'TagThumbnail', 'UI_FONT_SIZE', 'UI_FONT_SIZE_SMALL', 'theme_get']
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


def _auto_sash_sidebar(app, force=False):
    """根据左侧分类名称的最长字数，自动算一个合适的宽度。

    ★ 2026-10-03：如果上次已经记住了宽度（用户自己拖过），
      就**别再自动算了** —— 老老实实用他拉好的那个
      （他明确要求「关了程序再开还是我原来拉好的比例」）。

    ★★ 2026-10-07 修「区域开关以后的比例会自动跳成最初的」（用户报）★★
      病根（实测追出来的）：
        这里判断"分类库在不在"用的是 **`app.sidebar.winfo_ismapped()`**。
        可是**刚 `paned.add()` 插回去的那一刻，Tk 还没把它映射出来** ——
        于是这里读到的还是 `0`（不在）→ **要么直接 return、
        要么走"自动算"分支** → 用户拉好的 330 **被改成算法值 395**。
      ★ 修法：**用我们自己的 `_sidebar_wanted` 判断**（那是"打算显示吗"，
        一设就准），**不要问 Tk "现在画出来了吗"**（那个有延迟）。
      ★ 实测：改前 `sashpos(0)` 跳成 395；改后**稳定 330** ✔
    """
    def _sidebar_should_show():
        """分类库**应不应该**显示 —— 用记忆，不用 `winfo_ismapped()`。"""
        try:
            w = getattr(app, "_sidebar_wanted", None)
            if w is not None:
                return bool(w)
        except Exception:
            pass
        try:
            return bool(app.sidebar.winfo_ismapped())
        except Exception:
            return False

    if not force:
        try:
            saved = int((getattr(app, "_pane_sizes", {}) or {})
                        .get("pane_sidebar_w") or 0)
        except Exception:
            saved = 0
        if saved > 60:
            try:
                if _sidebar_should_show():
                    app.paned.sashpos(0, saved)
                return
            except Exception:
                pass
    # ★ 如果左侧分类库已经隐藏，paned 里只剩两个面板，
    #   这时 sashpos(0, ...) 会把中间和右边的分界挪走，
    #   导致右侧标签库显示得巨大 —— 直接跳过。
    if not _sidebar_should_show():
        return
    names = [T("全部文件")]
    try:
        for c in app.store.all_categories():
            n = (c.get("name") or "").strip()
            if n:
                names.append(n)
    except Exception:
        pass
    try:
        f = tkfont.Font(family=FONT, size=UI_FONT_SIZE)
        max_name_px = max(f.measure(n) for n in names)
    except Exception:
        max_name_px = 80

    # 头像 36px + 头像左右 padding (10+8) + 名字宽
    # + 计数/右边距 24 + 滚动条 16
    want = 36 + 18 + max_name_px + 24 + 16
    # 就锚在 200 附近，名字短→略窄，名字长→略宽
    want = max(185, min(215, int(want)))

    # 别超过窗口宽度的五分之一，免得挤掉中间的列表
    try:
        total = app.paned.winfo_width()
        if total > 400:
            want = min(want, int(total * 0.20))
    except Exception:
        pass

    try:
        app.paned.sashpos(0, want)
    except Exception:
        pass


def _layout_right_panes(app):
    """给右侧的面板分宽度：可能只有标签库，也可能是「预览 + 标签库」。

    ★ 不按固定 sash 序号算（隐藏/显示之后序号会变），而是按 paned 里
      实际的 pane 顺序定位，免得把分隔条设错地方。
    """
    try:
        panes = [str(p) for p in app.paned.panes()]
        total = app.paned.winfo_width()
        if total < 400:
            return
        prev = str(app.preview_frame)
        tag = str(app.tag_frame)
        # 左侧分类库现在有多宽（第一根分栏条的位置）
        try:
            sb_w = (int(app.paned.sashpos(0))
                    if app.sidebar.winfo_ismapped() else 0)
        except Exception:
            sb_w = 185
        # ★ 2026-10-03：标签库宽度也优先用「上次记住的」
        #   ★★ 2026-10-07：上限原来死钳 520 —— 跟预览窗格同一个毛病
        #     （用户拉宽了会被压回去）。改成跟着窗口比例走。
        _LIB_MAX = max(520, int(total * 0.40))
        lib_w = (min(_LIB_MAX, max(300, int(total * 0.30)))
                 if tag in panes else 0)
        try:
            _lw = int(getattr(app, "_taglib_width", 0) or 0)
            if _lw and tag in panes:
                lib_w = min(_LIB_MAX, max(240, _lw))
        except Exception:
            pass
        # ★★ 2026-10-07 修「区域宽度记不住」（用户报：
        #   「区域宽度又没法被记住了，下次打开又得重新拉好」）★★
        #   真因（实测追出来的）：`_apply_saved_pane_sizes()` **算对了**
        #   （sashpos 设成 519），但紧接着这里一句
        #       `prev_w = min(480, max(300, _pw))`
        #   **把宽度死死钳在 300~480 之间** → 用户拉宽到 630，
        #   一经过这里就被压回 480 → **看起来就是"记不住"**。
        #   （实测：apply 后 sashpos(1)=519，layout 后变成 685。）
        #   ★ 修法：**上限放宽到窗口的 45%** ——
        #     既尊重用户拉出来的宽度，又不会宽到把文件列表挤没
        #     （下面还有 list_min 那层保护，不会失控）。
        _PREV_MAX = max(480, int(total * 0.45))
        _pw = int(getattr(app, "_preview_width", 0) or 0)
        if _pw:
            prev_w = min(_PREV_MAX, max(240, _pw))
        else:
            prev_w = min(_PREV_MAX, max(300, int(total * 0.30)))
        # ★★ 2026-10-03：**文件列表不能太窄！**
        #   用户反馈「单击文件跟没有差不多」—— 其中一半原因是：
        #   预览窗格 + 标签库一开，中间的文件列表只剩 400 像素出头，
        #   文件名被截成「calibr…」「ede7…」，你根本看不出点的是哪个
        #   文件（1400 的窗口下实测只有 443 像素）。
        #   这里给文件列表兜一个下限：窗口够宽时至少 500 像素。
        list_min = 500 if total >= 1100 else max(300, int(total * 0.34))
        _avail = max(0, total - sb_w - list_min)      # 右侧总共能用多少
        # ★ 2026-10-03 再修一次：右边两块先按「它们想要的宽度」算，
        #   文件列表拿**剩下的全部**（但不能低于 list_min）。
        #   上一版把分栏条钉在 sb_w + list_min 上，结果只开标签库时
        #   标签库把整行剩下的空间全吃了（实测：列表只剩 520，
        #   标签库 680）—— 那是反的，列表才是主角。
        if tag in panes and prev in panes:
            # ★★ 2026-10-07 修「区域宽度记不住」的**真正病根** ★★
            #   （实测追出来的：窗口 1484、预览存 630、标签库存 319）
            #   原来这里写：
            #       if prev_w + lib_w > _avail:          # _avail 已扣掉 list_min
            #           prev_w = min(prev_w, max(280, _avail - 280))
            #           lib_w  = max(280, _avail - prev_w)
            #   实测：630+319=949 > _avail(799) → **预览被压到 519**。
            #   ★ 也就是说：**用户拉好的宽度每次开机都被这个公式重算掉**，
            #     而 `list_min=500` 是"不可协商的" → 用户怎么拉都白搭
            #     → 表现就是"记不住"。
            #   ★ 修法：**用户存的宽度优先**。只有"列表被压到没法看"时
            #     才收缩，而且**按比例缩**（不是把预览一刀切到 _avail-280），
            #     这样各块的比例还是用户拉的那个样子。
            _list_after = total - sb_w - prev_w - lib_w
            # ★★ 2026-10-07：列表的"实在不能低于"再放宽一点。
            #   ★ 为什么：用户**明确拉过**的宽度应该尽量尊重 ——
            #     实测窗口 1484 时：预览 600 + 标签库 380 会让列表只剩 319，
            #     而原来的保底是 488 → 于是把预览压到 497（用户想要的 600 没保住）。
            #   ★ 现在把保底降到 `total*0.22`（约 326）——
            #     列表还是"能看"的宽度（文件名不至于只剩几个字），
            #     但用户拉出来的比例**基本能保住**。
            #   ★ 注意：这是**取舍**，不是纯 bug ——
            #     窗口就这么宽，三块不可能都要。用户拉过 → 优先听用户的。
            _hard = max(280, int(total * 0.22))
            if _list_after < _hard and (prev_w + lib_w) > 0:
                # 差额按比例从"预览 + 标签库"里扣
                _cut = _hard - _list_after
                _right = float(prev_w + lib_w)
                _ratio = max(0.45, (_right - _cut) / _right)
                prev_w = max(200, int(prev_w * _ratio))
                lib_w = max(220, int(lib_w * _ratio))
            _list_w = max(200, total - sb_w - prev_w - lib_w)
            i = panes.index(prev)
            app.paned.sashpos(max(0, i - 1), min(total, sb_w + _list_w))
            app.paned.sashpos(i, min(total, sb_w + _list_w + prev_w))
        elif tag in panes:
            if _avail:
                lib_w = min(lib_w, _avail)
            _list_w = max(list_min, total - sb_w - lib_w)
            i = panes.index(tag)
            app.paned.sashpos(max(0, i - 1), min(total, sb_w + _list_w))
        elif prev in panes:
            if _avail:
                prev_w = min(prev_w, _avail)
            _list_w = max(list_min, total - sb_w - prev_w)
            i = panes.index(prev)
            app.paned.sashpos(max(0, i - 1), min(total, sb_w + _list_w))
    except Exception:
        pass


def _build_tag_panel(app, parent):
    head = ttk.Frame(parent)
    head.pack(fill="x")
    ttk.Label(head, text=T("标签库（星图缩略图）"),
              font=(FONT, UI_FONT_SIZE, BOLD)).pack(side="left")
    ttk.Button(head, text=T("重置视图"), width=8,
               command=lambda: app.tag_thumb.reset_view()).pack(side="right")

    # ★ 2026-10-03：原来三大行说明文字太占空间（290宽 wrap 后 3 行），
    #   精简成一行提示，缩略图能多用点地方。
    # ★★ 2026-10-07：颜色原来是**写死的浅色** "#9aa0a6"
    #   （那是浅色模式的次要字色）—— 夜间在深底上偏暗、而且不跟主题走。
    #   现在改成 theme_get("fg_dim")。
    ttk.Label(parent, text=T("← 拖标签到文件打标 │ 单击筛选 │ 双击查看"),
              foreground=theme_get("fg_dim"),
              font=(FONT, UI_FONT_SIZE_SMALL),
              anchor="w", justify="left").pack(anchor="w", pady=(0, 2))

    app.tag_thumb = TagThumbnail(
        parent,
        # ★★ v26 补丁（2026-10-03）：把主程序传进去 —— 不然这里面的
        #   app.app 从来没值，「从标签库拖标签进标签盒」一直是坏的。
        app=app,
        on_drop_on_file=app._on_tag_dropped,
        on_context_menu=app._on_tag_right_click,
        on_double_click=app._on_tag_double_click,
    )
    app.tag_thumb.pack(fill="both", expand=True)

    zr = ttk.Frame(parent)
    zr.pack(fill="x", pady=(6, 0))
    ttk.Button(zr, text="🔍+", width=4,
               command=lambda: app.tag_thumb.zoom_center(1.15)).pack(side="left")
    ttk.Button(zr, text="🔍-", width=4,
               command=lambda: app.tag_thumb.zoom_center(1 / 1.15)).pack(side="left", padx=2)
    ttk.Label(zr, text=T("Ctrl+滚轮缩放 / 空格+拖动平移"),
              foreground=theme_get("fg_dim")).pack(side="left", padx=6)

    r2 = ttk.Frame(parent)
    r2.pack(fill="x", pady=(6, 0))
    ttk.Button(r2, text=T("🌌 标签星图"),
               command=app.open_tag_tree).pack(fill="x")

    r2c = ttk.Frame(parent)
    r2c.pack(fill="x", pady=(4, 0))
    ttk.Button(r2c, text=T("🎨 重新分配所有标签颜色"),
               command=app.reassign_colors).pack(fill="x")

    r2b = ttk.Frame(parent)
    r2b.pack(fill="x", pady=(4, 0))
    ttk.Button(r2b, text=T("🧩 同步所有文件的标签链"),
               command=app.resync_now).pack(fill="x")

    # ★ v24：右侧面板不再放「导入 / 导出」——这功能不常用，
    #   统一走左上角「文件」菜单里的导出/导入标签结构、文件标签信息。
    sep = ttk.Separator(parent)
    sep.pack(fill="x", pady=(10, 6))

    r3 = ttk.Frame(parent)
    r3.pack(fill="x")
    ttk.Button(r3, text=T("按选中标签筛选"),
               command=app.apply_filter).pack(side="left", fill="x", expand=True)
    ttk.Button(r3, text=T("清除"), width=6,
               command=app.clear_filter).pack(side="left", padx=(4, 0))

    app.match_all_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(parent, text=T("必须同时包含所有选中的标签"),
                    variable=app.match_all_var).pack(anchor="w", pady=(4, 0))


def _view_info_text(app, text):
    """★ v25 补丁10 / v26 修正：从一句状态消息里挑出「关于当前视图的信息」。

    是这类信息就返回那句（显示到消息右边）；不是就返回 None —— 这时
    右边那块保持上一句不动（免得「标签条：已显示」把分类信息顶掉）。

    例子：
      「分类「图本」：55644 个文件（含 1 个标签超链接）（加载中…）」→ 留
      「C:\\Users\\someone    共 44 项（已刷新）」→ 留
      「标签条：已显示」→ 不留

    ★★ v26 二次修正（2026-10-01）：**上一版这里把功能改没了。**
      上一版跟 `app.status.cget("text")` 比 —— 但那个时候
      `set_status` 已经把左边状态改成新文字了，所以 `t` 永远等于 `cur`，
      `if` 永远成立、永远 return None —— 结果右边那块**再也刷不出来**。
      现在改成跟**右边这一块自己当前显示的内容**比：
        · 已经在显示同一句 → 不重复写（省地方）；
        · 内容不同 / 之前是空的 → 正常更新。
    """
    t = (text or "").strip()
    if not t:
        return None
    if t.startswith("标签条"):
        return None                     # 关于标签条自身的提示，不重复显示
    if not any(k in t for k in ("项", "个文件", "共", "目录", "分类", "路径")):
        return None
    # ★★ v26：只跟「右边这一块自己现在显示的内容」比 ——
    #   同一句就不重复写（用户反馈过「一模一样的话显示了两遍，
    #   白白占掉 400 多像素」）。
    try:
        cur = str(app._view_info_lbl.cget("text") or "").strip()
        if cur and cur == t:
            return None
    except Exception:
        pass
    # ★ v25 补丁42：太长会把右边那排按钮挤出去。收紧到 40 字，
    #   全文另存进「📋 输出」面板。
    if len(t) > 40:
        try:
            app.log_output(t)
        except Exception:
            pass
        t = t[:39] + "…"
    return t


def _fit_view_info(app, info):
    """★ v25 补丁42：把「当前视图信息」截到它真正放得下的长度。

    它和状态文字是**抢同一块地方**的：两个都是 side="left"，
    加起来超过状态栏宽度，右边那排按钮就会被顶出去。
    所以这里按「状态文字已经用了多少」算剩下的能给它多少。
    """
    try:
        f = tkfont.Font(family=FONT, size=UI_FONT_SIZE)
        total = app.status.master.winfo_width()
        if total <= 1:
            return info
        used = 0
        for name in ("_problem_btn", "_output_btn", "_tagbar_btn",
                     "_preview_btn", "_taglib_btn", "_net_btn",
                     "_tagbox_btn"):
            b = getattr(app, name, None)
            if b is None:
                continue
            try:
                used += b.winfo_reqwidth() + 8
            except Exception:
                pass
        try:
            used += app._activity_frame.winfo_reqwidth() + 16
        except Exception:
            pass
        used += 40                                   # 左右内边距
        try:
            used += f.measure(str(app.status.cget("text"))) + 20
        except Exception:
            pass
        avail = total - used
        # ★ v26：**空间紧张时干脆不显示「视图信息」** ——
        #   它和左边那句状态消息是抢同一块地方的，硬挤的结果就是
        #   右边那排按钮被顶出去（实测「标签盒」按钮会只剩几像素）。
        #   宁可少显示一块次要信息，也不能让按钮点不着。
        if avail <= 120:
            return ""                                # 地方不够，不显示
        if f.measure(info) <= avail:
            return info
        lo, hi = 1, len(info)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if f.measure(info[:mid] + "…") <= avail:
                lo = mid
            else:
                hi = mid - 1
        return info[:max(1, lo)] + "…"
    except Exception:
        return info


def _status_avail_px(app):
    """★ v25 补丁42 / v26 重写：算一下状态文字最多能占多少像素。

    算法：状态栏总宽 − 右边所有按钮的实际宽度 − 余量。

    ★ v26 改了什么、为什么要改：
      补丁42 那版在这里**硬扣了 220 像素**留给「当前视图信息」，
      再加上右边 7 个按钮（这台机器缩放 200%，每个要 138~154 像素，
      合计 1000 多），1400 的窗口一减就只剩 60 像素 ——
      只够显示「C:\\Us…」五个字符。用户看截图才发现：
      **状态栏那行什么都看不出来**。
      现在改成：
        · 不再盲目硬扣 220，而是**先按「状态文字至少要能看」给个底线**
          （至少要 220 像素，大约 10 个汉字）；
        · 「视图信息」那块改成**按剩下的空间自适应**（它自己有
          _fit_view_info 会截），不再预扣固定值；
        · 实在放不下（很窄的窗口）就返回一个合理的小值，
          而不是 60 这种几乎为 0 的数。
    """
    try:
        total = app.status.master.winfo_width()
        if total <= 1:
            return 0            # 还没量出来，这轮先不截
        used = 0
        for name in ("_problem_btn", "_output_btn", "_tagbar_btn",
                     "_preview_btn", "_taglib_btn", "_net_btn",
                     "_tagbox_btn"):
            b = getattr(app, name, None)
            if b is None:
                continue
            try:
                used += b.winfo_reqwidth() + 8
            except Exception:
                pass
        # 活动指示器（转圈 + 「统计分类中」）也占地方
        try:
            if app._activity_frame.winfo_ismapped():
                used += app._activity_frame.winfo_reqwidth() + 16
        except Exception:
            pass
        # 左右内边距 + 余量
        used += 40                                                    # v26
        avail = total - used
        # ★ 底线：至少要能显示十来个汉字（约 220 像素）。
        #   否则宁可让右边的「视图信息」少显示一点。
        if avail < 220:
            avail = min(220, max(80, total // 4))
        return avail
    except Exception:
        return 0


def _restore_pane_widths(app):
    """★★ 把"用户拖过的宽度"摆回 paned 里 —— **最终说话的那一个**。

    ★★★ 2026-10-07 新增（用户要求「**你先多弄些冗余**」，并报
      「拖动分类库的宽度，点标签库、预览什么的就刷没了」）。

    ★ 为什么需要它（这是整条链的最后一环）：
      `_reinsert_tag_frame()` 是"全撤 + 重加"，**重加之后 Tk 会按
      自己的算法把整条分栏重新分一遍**（实测：分类库 320 → **395**）。
      然后：
        · `_layout_right_panes()` 会**按这个错值**去摆（它读 sashpos）；
        · `after(400, _save_pane_sizes)` 会**把错值记下来**。
      → 结果就是"用户拖的宽度被刷没了"。
    ★ 所以必须有一个"**拿记住的值去覆盖 Tk 的值**"的动作 —— 就是这个。

    ★ 算法（**故意写得很笨，因为笨的不会错**）：
      对 paned 里的每一块，**从左往右**累计宽度，
      把每根分隔条摆到"累计到这个面板右边界"的位置上。
      · 只摆"记过的"那几块（分类库 / 预览 / 标签库）
      · 文件列表**不主动摆**（它是"剩下多少占多少"，摆它会把右边挤掉）
      · 位置必须**夹在 [上一根, 总宽] 之间**，免得越界
    ★ 踩过的坑：第一版我用了"按 key 名猜属性名"的写法，
      算出来把标签库推成 1811（布局全乱）。**这版只认固定三块**。
    """
    try:
        pw = app.paned
        panes = [str(p) for p in pw.panes()]
        if len(panes) < 2:
            return
        total = int(pw.winfo_width())
        if total <= 1:
            return
        data = dict(getattr(app, "_pane_sizes", {}) or {})

        # 三块"有记忆宽度"的面板 → 它们的 key
        KEYED = []
        for fr, key in ((getattr(app, "sidebar", None), "pane_sidebar_w"),
                        (getattr(app, "preview_frame", None),
                         "pane_preview_w"),
                        (getattr(app, "tag_frame", None),
                         "pane_taglib_w")):
            if fr is not None:
                KEYED.append((str(fr), key))

        acc = 0          # 从左边累计过来的宽度
        for i, s in enumerate(panes):
            if i == 0:
                # 第一块：它自己就是"第一根分隔条的左边"
                #   ★ 若它就是分类库且有记忆值 → 直接摆
                #
                # ★★ 2026-10-07 修「关掉侧栏之后，预览被压成 40」★★
                #   病根：分类库**不在**的时候，第一块是"文件列表"——
                #   而文件列表**我们故意不摆它**（它是"剩下多少占多少"）。
                #   可是原来的代码在这种情况下 `acc` 一直是 0 →
                #   下面摆第二块（预览）时就按 "0 + 预览宽" 去摆 →
                #   **把预览推到了最左边**（实测宽度只剩 40）。
                #   ✅ 修法：第一块如果**不是**"有记忆宽度的面板"
                #     （= 它是文件列表），就把 `acc` 设成**它当前的右边界**，
                #     让后面的面板从它右边接着算。
                _matched = False
                for fs, key in KEYED:
                    if fs == s:
                        _matched = True
                        try:
                            w = int(data.get(key) or 0)
                        except Exception:
                            w = 0
                        if w > 40:
                            acc = w
                            pw.sashpos(0, max(40, min(acc, total - 8)))
                        break
                if not _matched:
                    # 第一块是"没记忆的"（文件列表）→ 从它右边界起算
                    try:
                        acc = int(pw.sashpos(0))
                    except Exception:
                        acc = 0
                continue
            # 中间/末尾的面板
            w = 0
            for fs, key in KEYED:
                if fs == s:
                    try:
                        w = int(data.get(key) or 0)
                    except Exception:
                        w = 0
                    break
            if w <= 40:
                # 没记过的（比如文件列表）—— **不动它**，
                #   把 acc 更新成它"当前"的右边界，继续往右走
                try:
                    acc = int(pw.sashpos(i))
                except Exception:
                    pass
                continue
            acc = acc + w
            if i < len(panes) - 1:
                try:
                    lo = int(pw.sashpos(i - 1)) + 40
                    hi = total - 8
                    pw.sashpos(i, max(lo, min(acc, hi)))
                except Exception:
                    pass
    except Exception:
        pass
