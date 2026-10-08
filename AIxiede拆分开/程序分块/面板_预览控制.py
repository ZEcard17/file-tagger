# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「预览控制」这组方法。

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
_NEED = ['QuickPreview', 'T', 'note_swallowed', 'save_ui_setting']
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


def _preview_index(app):
    """预览窗格在 paned 里排第几（没显示就返回 -1）。"""
    try:
        panes = [str(p) for p in app.paned.panes()]
        return panes.index(str(app.preview_frame))
    except Exception:
        return -1


def toggle_preview(app):
    """★ v25 补丁8：显示 / 隐藏右侧预览窗格（默认隐藏、宽度可拖、会记住）。

    ★★ 2026-10-07 补：**跟 `toggle_sidebar` 一样，先把现状钉住**。
      用户报「点右侧区域标签库开关、预览开关应该还是这样」——
      意思是**右侧这两个开关也有"比例被重置"的毛病**。
      ★ 原来这里：
        · 关的时候**自己算了一遍宽度**（那段 `_preview_index()` 的逻辑），
          但它只在 `idx >= 0` 且算出来 120~2000 之间才记 —— **容易漏**；
        · 开的时候只 `_layout_right_panes()`，**没有"先记住现状"这一步**。
      ★ 现在统一：**开头先 `_remember_pane_now()`**（一次记全三个面板），
        关 / 开都受益，代码也少一大段。
    """
    try:
        # ★ 先把"现在各面板的宽度"钉住（关 / 开都用得上）
        try:
            app._remember_pane_now()
        except Exception:
            pass
        # ★★ 2026-10-07：标记"**正在重排分区**" —— 重排会把 sashpos
        #   改成 Tk 自己的值（实测 320→395），而本方法结尾安排的
        #   `after(400, _save_pane_sizes)` 会**如实记下那个错值**，
        #   把用户拖的宽度覆盖掉。
        #   → 重排期间不写盘（`_save_pane_sizes` 里会检查这个标记）。
        #   ★ 700 毫秒后才解除 —— 要比那个 400 毫秒的延迟保存晚。
        try:
            app._pane_rearranging = True
            app.root.after(700, lambda: setattr(app, "_pane_rearranging", False))
        except Exception:
            pass
        if app.preview_frame.winfo_ismapped():
            # ★ 补丁41：先改状态，再按新状态整体重排（不要单独 forget，
            #   免得出现「forget 了但状态没跟上」的不一致）
            app._preview_visible = False
            app._reinsert_tag_frame()
            app._preview_btn.config(text=T("📄 预览 ▲"))
            # ★★ 2026-10-07：**关也要把宽度摆回去** —— 全撤重加之后 Tk
            #   会把剩下的面板重新分，别的面板宽度就被挤动了
            #   （实测：关标签库，分类库 320 → 395）。
            try:
                app.root.update_idletasks()
            except Exception:
                pass
            app._restore_pane_widths()
            try:
                app.root.after(60, app._restore_pane_widths)
            except Exception:
                pass
            app.set_status(T("预览窗格：已隐藏"))
        else:
            # ★ v25 补丁41：这里原来是 paned.insert(idx, ...) 按序号硬塞。
            #   实测 ttk.PanedWindow 的 insert 索引**不能超过当前面板数**，
            #   而序号又是按「最终应该有 4 个面板」算的 —— 于是只要此刻
            #   少挂了一个面板就直接抛 "Slave index 2 out of bounds"，
            #   被 except 吞掉之后表现就是「点预览没反应」。
            #   现在统一走 _reinsert_tag_frame()：全撤掉、按正确顺序
            #   重加一遍，永远不可能越界。
            app._preview_visible = True
            app._reinsert_tag_frame()
            app._preview_btn.config(text=T("📄 预览 ▼"))
            app.set_status(T("预览窗格：已显示（选中文件即可预览，拖分隔线调宽度）"))
            # ★ 跟分类库一样：**等 Tk 把布局算完再摆宽度**，并补一次
            #   （踩过：`paned.add()` 之后立刻 `sashpos()` 会被夹成 0）
            try:
                app.root.update_idletasks()
            except Exception:
                pass
            # ★★★ 2026-10-07 **顺序：先让它摆右边比例，最后拿记住的值盖** ★★★
            #   `_layout_right_panes()` 是"按当前 sashpos 反推"摆的 ——
            #   而全撤重加之后 sashpos 已经是 Tk 的值（实测分类库 320→395），
            #   **所以它会把用户拖的宽度推回去**。
            #   → 让它先摆（它管"预览/标签库占多少"），
            #     **最后 `_restore_pane_widths()` 拿记下来的值盖一遍**，
            #     它才是最终说话的那个。
            app._layout_right_panes()
            app._restore_pane_widths()
            try:
                app.root.after(120, app._restore_pane_widths)
            except Exception:
                pass
        save_ui_setting("preview_visible", app._preview_visible)
    except Exception as _e:
        note_swallowed(T("切换预览窗格失败"), _e)


def toggle_taglib(app):
    """★ v25 补丁8：显示 / 隐藏右侧的「标签库（星图缩略图）」整列。

    ★★ 2026-10-07 补：**跟 `toggle_sidebar` / `toggle_preview` 一样，
      开头先把现状钉住**。
      ★ 原来这里**关的时候一行都没记宽度**（对比 `toggle_preview` 还记了
        一点）→ 用户拉好标签库宽度、关一次、再开就**回到默认值**。
    """
    try:
        # ★ 先把"现在各面板的宽度"钉住
        try:
            app._remember_pane_now()
        except Exception:
            pass
        # ★★ 2026-10-07：标记"**正在重排分区**" —— 重排会把 sashpos
        #   改成 Tk 自己的值（实测 320→395），而本方法结尾安排的
        #   `after(400, _save_pane_sizes)` 会**如实记下那个错值**，
        #   把用户拖的宽度覆盖掉。
        #   → 重排期间不写盘（`_save_pane_sizes` 里会检查这个标记）。
        #   ★ 700 毫秒后才解除 —— 要比那个 400 毫秒的延迟保存晚。
        try:
            app._pane_rearranging = True
            app.root.after(700, lambda: setattr(app, "_pane_rearranging", False))
        except Exception:
            pass
        if app.tag_frame.winfo_ismapped():
            # ★ 补丁41：同 toggle_preview —— 改状态 + 整体重排
            app._taglib_visible = False
            app._reinsert_tag_frame()
            app._taglib_btn.config(text=T("🔖 标签库 ▲"))
            # ★★ 2026-10-07：**关也要把宽度摆回去** —— 全撤重加之后 Tk
            #   会把剩下的面板重新分，别的面板宽度就被挤动了
            #   （实测：关标签库，分类库 320 → 395）。
            try:
                app.root.update_idletasks()
            except Exception:
                pass
            app._restore_pane_widths()
            try:
                app.root.after(60, app._restore_pane_widths)
            except Exception:
                pass
            app.set_status(T("标签库：已隐藏"))
        else:
            # ★ v25 补丁41：**这里原来是 app.paned.add(...)，
            #   那是「追加到最后一位」—— 但标签库本该排在
            #   「分类库│文件列表│预览窗格│标签库」的第 4 位。
            #   于是关掉预览、再开标签库，标签库就跑到预览窗格
            #   该在的位置上了；接着 _layout_right_panes 按固定
            #   序号去挪分隔条，越界 → 日志里那条
            #   「切换预览窗格失败：TclError: Slave index 2 out of bounds」。
            #   现在改成按**正确的次序**插进去（和初始化时的顺序一致）。
            # ★★ 2026-10-07 修「标签库关开之后宽度变 0 / 面板消失」★★
            #   **顺序错了**：原来是
            #       app._reinsert_tag_frame()      # ← 这时读到的还是 False！
            #       app._taglib_visible = True     # ← 才设 True（太晚）
            #   → `_reinsert_tag_frame()` 里按 `_taglib_visible` 判断要不要插，
            #     读到 False → **标签库根本没被插回去**（实测：panes 里没有它，
            #     而 visible 标志已经是 True —— 两边不一致）。
            #   ✅ 必须**先设标志、再重排**（`toggle_sidebar` 就是这么写的，
            #     所以它是好的）。
            app._taglib_visible = True
            app._reinsert_tag_frame()
            app._taglib_btn.config(text=T("🔖 标签库 ▼"))
            app.set_status(T("标签库：已显示"))
            # ★ 等 Tk 算完布局再摆宽度（理由同 toggle_preview）
            try:
                app.root.update_idletasks()
            except Exception:
                pass
            # ★★★ 2026-10-07 **顺序：先摆右边比例，最后拿记住的值盖** ★★★
            #   理由同 `toggle_preview` —— `_layout_right_panes()` 会
            #   按 Tk 重排后的 sashpos（395）把用户拖的 320 推回去。
            app._layout_right_panes()
            app._restore_pane_widths()
            try:
                app.root.after(120, app._restore_pane_widths)
            except Exception:
                pass
        save_ui_setting("taglib_visible", app._taglib_visible)
        # ★ 2026-10-03：宽度变了也记一下
        try:
            app.root.after(400, app._save_pane_sizes)
        except Exception:
            pass
    except Exception as _e:
        note_swallowed(T("切换标签库显示失败"), _e)


# ---------------- ★★ 2026-10-06：空格快速预览（Quick Look）----------------
def _quick_preview_init(app):
    """开机时把「快速预览」准备好（不弹窗，只建对象）。"""
    try:
        app.quick_preview = QuickPreview(app)
    except Exception as _e:
        app.quick_preview = None
        note_swallowed(T("快速预览没建起来（空格键会没反应）"), _e, quiet=True)


def toggle_quick_preview(app):
    """菜单 / 空格键都走这里。

    ★★ 2026-10-07 修「快速预览没有开关的设置，只有开」（用户报）：
      查证结果：**开关功能本身是好的**（实测 is_open 能 关→开→关→开）。
      ★ 真正的原因有两个：
        ① 菜单名字叫「快速预览（**空格键**）」—— 看着像"快捷键说明"，
           **不像一个能开能关的开关**。→ 已改名「快速预览窗」，
           并且它现在**带状态圆点**（绿=开着 / 红=关着）。
        ② **没选中文件时点它，什么都不发生** ——
           `QuickPreview.open()` 里只有一句
           `set_status(T("先选中一个文件……"))`，
           而状态栏那行字很小、很容易没注意 →
           **用户以为"点了没反应、只能开"**。
           → 现在改成**弹一个明确的提示框**，告诉他要先选文件。
    """
    qp = getattr(app, "quick_preview", None)
    if qp is None:
        messagebox.showinfo(
            "快速预览",
            "快速预览没能启用。\n\n"
            "（多半是程序内部出了点小问题，不影响其它功能。）",
            parent=app.root)
        return
    # ★ 要"开"之前先检查：有没有选中文件 —— 没选就明确告诉他
    try:
        _will_open = not qp.is_open()
    except Exception:
        _will_open = False
    if _will_open:
        try:
            _cur = qp._current_path()
        except Exception:
            _cur = None
        if not _cur:
            messagebox.showinfo(
                "快速预览",
                "先**在文件列表里点一个文件**，再用快速预览。\n\n"
                "（也可以直接按空格键 —— 一样要先选中文件）",
                parent=app.root)
            try:
                app.set_status(T("快速预览：先在列表里点一个文件"))
            except Exception:
                pass
            return
    try:
        qp.toggle()
    except Exception as _e:
        note_swallowed(T("快速预览开关失败"), _e)
        messagebox.showwarning("快速预览", "打不开预览窗：%s" % _e,
                               parent=app.root)
    # ★ 开关完刷一下菜单圆点（让"绿/红"立刻反映真实状态）
    try:
        app._refresh_menu_states()
    except Exception:
        pass


def on_quick_preview_key(app, event=None):
    """★ 空格键入口。

    ★★ 两个务必：
      ① **正在输入框里打字时不能抢空格** —— 否则你在搜索框打不出空格，
         这是最容易被骂的那种 bug。所以先问 `_focus_is_input()`。
      ② **快速预览窗开着的时候，空格归它管**（用来关窗）。
         如果这里也响应，就会「关了又开」，来回抽搐。
    """
    try:
        if app._focus_is_input():
            return None
    except Exception:
        pass
    qp = getattr(app, "quick_preview", None)
    if qp is not None and qp.is_open():
        # 预览窗自己绑了空格（负责关掉），这里不再插手
        return None
    app.toggle_quick_preview()
    return "break"


def toggle_hover_preview(app):
    """★ 补丁27：鼠标悬停预览 开 / 关。"""
    try:
        app.hover.toggle()
    except Exception as exc:
        messagebox.showerror("悬停预览", "切换失败：%s" % exc,
                             parent=app.root)


def toggle_tagbar(app):
    """★ v25 补丁7：显示 / 隐藏标签条（默认隐藏）。

    标签条现在是**整条底部面板**（横跨整个窗口，和「🔔 问题 / 📋 输出」
    一样），不再挤在文件列表那一列里。
    """
    try:
        vis = not getattr(app.file_list, "tagbar_visible", False)
        app.file_list.set_tagbar_visible(vis)
        app._tagbar_btn.config(
            text=T("🏷 标签条 ▼") if vis else T("🏷 标签条 ▲"))
        app.set_status(T("标签条：已显示") if vis
                        else "标签条：已隐藏（点右下角「🏷 标签条」再看）")
    except Exception as _e:
        note_swallowed(T("切换标签条显示失败"), _e)
