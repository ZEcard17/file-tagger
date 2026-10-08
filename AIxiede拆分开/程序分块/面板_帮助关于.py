# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「帮助关于」这组方法。

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
_MUTABLE = ['BOLD', 'DB_PATH', 'EXPORT_DIR', 'FONT', 'SETTINGS_PATH', 'UI_FONT_SIZE', 'UI_FONT_SIZE_SMALL']
_NEED = ['BOLD', 'DB_PATH', 'EXPORT_DIR', 'FONT', 'SETTINGS_PATH', 'T', 'UI_FONT_SIZE', 'UI_FONT_SIZE_SMALL', '_CREDITS_TEXT', '_HERE', '_REPO_URL', '_SPONSOR_URL', '_USAGE_PATH', '_dlg_geom', '_i18n', '_open_url', '_tree_row_height', 'note_swallowed', 'theme_get', 'usage_read', 'usage_summary']
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


def _open_lang_folder(app):
    """★ 打开 `语言/` 文件夹 —— **让别人自己能加语言**。

    ★ 为什么要给这个入口：语言文件是**纯 JSON**，
      懂一点的人**照着 `en_US.json` 加一个 `ru_RU.json` 就行** ——
      **不用改代码、不用重新打包**。
      ★ 这是"开放"的一部分：**别人能参与翻译，不需要我**。
    """
    try:
        d = ""
        if _i18n is not None:
            d = _i18n._candidates_dir()
        if not d or not os.path.isdir(d):
            d = os.path.join(_HERE, "语言")
        os.makedirs(d, exist_ok=True)
        os.startfile(d)          # ★ Windows 打开文件夹
    except Exception as _e:
        note_swallowed(T("打开语言文件夹失败"), _e)


def show_usage_log(app):
    """★★ 2026-10-07 **合并版**：「用法记录」+「体检报告」合成一个窗口。

    ★ 用户提的：「体验报告和用法记录的区别是什么，感觉可以合并」
      → 我查了，他说的"体验报告"其实是**体检报告**，两者确实是**一个东西的两半**：
        |          | 体检报告                 | 用法记录               |
        |----------|--------------------------|------------------------|
        | 数据来源 | `swallowed_report()`（内存） | `usage_read()`（落盘）  |
        | 范围     | **只管这一次开程序**       | **跨次累积**            |
        | 内容     | 哪儿出的问题 —— N 次       | 哪儿 / 次数 / 最近 / 错误 |

    ★ 用户选了**方案 B**：一个窗口、**两个页签**（本次 / 历史）。
      为什么不做成一个表：**"本次"和"跨次"是不同的东西** ——
        · 「本次」适合"我刚发现一个 bug，现在就看看"
        · 「历史」适合"哪些毛病**老**出现"
      硬合成一个表会**丢掉这个区分**，而**恰恰"老出现"才最该修**。
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
    win.title("📓 用法记录 —— 哪儿出过问题（本次 / 历史）")
    win.transient(app.root)
    try:
        win.geometry(_dlg_geom(900, 600))
    except Exception:
        pass
    outer = ttk.Frame(win, padding=10)
    outer.pack(fill="both", expand=True)

    # ★★ 2026-10-07 修（截图看出来的）：**底部按钮被挤没了**。
    #   原因：`Notebook` 先 `pack(fill="both", expand=True)` 把空间全吃掉，
    #   后面 `btns` 再 pack 就没地方了（截图里一个按钮都看不到）。
    #   ★ 正确顺序：**先把贴边的（bottom）摆好，再让中间那块 expand 去填剩下的。**
    #     这跟预览窗格那次是同一个道理（翻页条要先 pack 到底部）。
    btns = ttk.Frame(outer)
    btns.pack(side="bottom", fill="x", pady=(8, 0))

    nb = ttk.Notebook(outer)
    nb.pack(fill="both", expand=True)

    # 本次那边要用的数据先取出来（内存里的，很快）
    try:
        _this_text = app.dump_swallowed_report()
    except Exception as _e:
        _this_text = "生成报告失败：%s" % _e

    # ---------------- 页签 1：本次（原「体检报告」）----------------
    tab_now = ttk.Frame(nb, padding=10)
    nb.add(tab_now, text=T("  本次开程序  "))
    ttk.Label(
        tab_now,
        text=T("这是**这次开程序以来**记下的「没吭声的小毛病」（关窗口就清零）。\n"
                "想看「老出问题的是哪些」→ 点上面那个「历史累计」页。\n"
                "★ 把这里的内容发我即可，全是中文、不含你的文件名/路径。"),
        justify="left", font=(FONT, UI_FONT_SIZE)).pack(anchor="w",
                                                        pady=(0, 6))
    box = tk.Text(tab_now, width=76, height=20, wrap="none",
                  font=(FONT, UI_FONT_SIZE),
                  bg=theme_get("text_bg"), fg=theme_get("fg"),
                  insertbackground=theme_get("fg"),
                  relief="flat", highlightthickness=1,
                  highlightbackground=theme_get("line"))
    box.pack(fill="both", expand=True)
    box.insert("1.0", str(_this_text))
    box.configure(state="disabled")

    # ---------------- 页签 2：历史累计（原「用法记录」）----------------
    tab_hist = ttk.Frame(nb, padding=10)
    nb.add(tab_hist, text=T("  历史累计  "))

    try:
        recs = usage_read(limit=2000)
    except Exception:
        recs = []

    ttk.Label(
        tab_hist,
        text="这里记的是**跨次积累**的（关了程序也留着）——"
             "按「出现次数」从多到少排，**排最上面的就是最该修的**。\n"
             "★ 不包含文件名 / 路径 / 标签 / 搜索词。",
        justify="left", font=(FONT, UI_FONT_SIZE)).pack(anchor="w",
                                                        pady=(0, 8))
    agg = []
    try:
        agg = usage_summary()
    except Exception:
        agg = []

    if not recs and not agg:
        ttk.Label(tab_hist, text=T("（还什么都没记到 —— 挺好）"),
                  foreground=theme_get("ok"),
                  font=(FONT, UI_FONT_SIZE)).pack(anchor="w")
    else:
        wrap = ttk.Frame(tab_hist)
        wrap.pack(fill="both", expand=True)
        cols = ("where", "n", "last", "exc")
        # ★★ 2026-10-07 修「行高比字矮、文字被上下切掉」（用户报）：
        #   原来这句没给 style，于是用**系统默认行高**（约 20），
        #   装不下 14/13 号字（要 24 左右）→ 每行字被压扁。
        #   ★ 修法：跟目录树一样，注册一个带 `rowheight=_tree_row_height()`
        #     的样式再挂上（`_tree_row_height()` 是按字体算的，会跟着字号走）。
        try:
            _st = ttk.Style()
            _rh = _tree_row_height()
            _st.configure("UsageLog.Treeview",
                          background=theme_get("card_bg"),
                          foreground=theme_get("fg"),
                          fieldbackground=theme_get("card_bg"),
                          rowheight=_rh,
                          font=(FONT, UI_FONT_SIZE_SMALL))
            _st.configure("UsageLog.Treeview.Heading",
                          font=(FONT, UI_FONT_SIZE_SMALL, BOLD))
            tv = ttk.Treeview(wrap, columns=cols, show="headings", height=14,
                              style="UsageLog.Treeview")
        except Exception:
            tv = ttk.Treeview(wrap, columns=cols, show="headings", height=14)
            # ★★ 2026-10-07 补：这棵树没给 style → 系统默认行高(约20)装不下字
            #   → 字被上下切掉（用户报「字体比行高长」）。按字体算行高。
            #   ★ 这个分支是"注册样式失败时的退路"，所以复用上面那个
            #     `UsageLog.Treeview` 的名字（同样的样式，不必再注册一份）。
            try:
                _st_fb = ttk.Style()
                _st_fb.configure("UsageLog.Treeview",
                    background=theme_get("card_bg"),
                    foreground=theme_get("fg"),
                    fieldbackground=theme_get("card_bg"),
                    rowheight=_tree_row_height(),
                    font=(FONT, UI_FONT_SIZE_SMALL))
                _st_fb.configure("UsageLog.Treeview.Heading",
                    font=(FONT, UI_FONT_SIZE_SMALL, BOLD))
                tv.configure(style="UsageLog.Treeview")
            except Exception:
                pass
        for c, txt, wd in (("where", "哪儿出的问题", 360),
                           ("n", "次数", 60),
                           ("last", "最近一次", 150),
                           ("exc", "错误", 260)):
            tv.heading(c, text=txt)
            # ★ 2026-10-06：这里踩了一下 —— `column()` **没有 text 参数**，
            #   标题要用 heading() 设；column() 只管宽度和对齐。
            tv.column(c, width=wd,
                      anchor="center" if c == "n" else "w")
        for d in agg:
            try:
                tv.insert("", "end", values=(d["where"], d["n"],
                                             d["last"], d["exc"]))
            except Exception:
                continue
        sb = ttk.Scrollbar(wrap, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        tv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    # ---------------- 底部按钮（两个页签共用）----------------
    #   ★ 注意：这个 `btns` **已经在上面对 Notebook 之前 pack 好了**
    #     （必须先摆贴底的，否则会被 Notebook 的 expand 挤没）。

    def _copy_this():
        try:
            app.root.clipboard_clear()
            app.root.clipboard_append(str(_this_text))
            app.set_status(T("本次记录已复制到剪贴板"))
        except Exception as _e:
            note_swallowed(T("复制本次记录失败"), _e, quiet=True)

    def _save_this():
        try:
            p = filedialog.asksaveasfilename(
                parent=win, title=T("保存本次记录"),
                defaultextension=".txt", initialfile="用法记录-本次.txt")
            if not p:
                return
            with open(p, "w", encoding="utf-8") as f:
                f.write(str(_this_text))
            app.set_status(T("已保存到：{x}", x=p))
        except Exception as _e:
            note_swallowed(T("保存本次记录失败"), _e)

    def _open_file():
        try:
            p = _USAGE_PATH
            if p and os.path.isfile(p):
                os.startfile(os.path.dirname(p))
            else:
                messagebox.showinfo("用法记录", T("还没有记账文件。"),
                                    parent=win)
        except Exception as exc:
            messagebox.showerror("打不开", str(exc), parent=win)

    def _clear():
        if not messagebox.askyesno(
                "清空历史记录",
                "把**历史累计**的记录清掉？\n\n"
                "（「本次开程序」那一页不受影响；"
                "只是把「账本」清空，不影响程序任何功能）",
                parent=win):
            return
        try:
            if _USAGE_PATH and os.path.isfile(_USAGE_PATH):
                os.remove(_USAGE_PATH)
        except Exception:
            pass
        win.destroy()

    ttk.Button(btns, text=T("复制本次记录"), command=_copy_this).pack(
        side="left", padx=4)
    ttk.Button(btns, text=T("保存本次记录…"), command=_save_this).pack(
        side="left", padx=4)
    ttk.Button(btns, text=T("打开记账文件"), command=_open_file).pack(
        side="left", padx=4)
    ttk.Button(btns, text=T("清空历史记录"), command=_clear).pack(
        side="left", padx=4)
    ttk.Button(btns, text=T("关闭"), command=win.destroy).pack(
        side="right", padx=4)

    # ★ 顺便写进「问题」面板，这样关掉小窗还能回看（老行为保留）
    try:
        for _ln in str(_this_text).split("\n"):
            if _ln.strip():
                app.log_problem(_ln, level="info")
    except Exception:
        pass


def show_credits(app, parent=None):
    """★★★ 「关于」里的「版权与来源」详情窗。

    ★★ 为什么单独一个窗（不塞进「关于」）：
      · 版权声明**比较长**（要中英对照）—— 塞进「关于」会**挤爆**
      · ★ 而且**不是每个人都要看** —— 想看的人点一下就够

    ★ 为什么这个声明必须存在（★ 用户 2026-10-08 的要求）：
      > 「这个程序只是我提出设计的，代码全是你写的……
      >   深度求索公司也该有这程序一份版权」
      ★★ 关键那句：「**对 AI 来说每个对话窗口可能都是一次新生**」——
        它**不会来认领这份功劳**，所以**必须由人写下来**。
    """
    try:
        win = tk.Toplevel(parent or app.root)
        win.title(T("版权与来源"))
        win.transient(parent or app.root)
        win.resizable(True, True)
        try:
            win.configure(bg=theme_get("win_bg"))
        except Exception:
            pass
        try:
            _reg = getattr(app, "_theme_windows", None)
            if _reg is None:
                _reg = app._theme_windows = []
            _reg.append(win)
        except Exception:
            pass

        body = ttk.Frame(win, padding=16)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text=T("版权与来源声明"),
                  font=(FONT, UI_FONT_SIZE + 2, BOLD)).pack(anchor="w")
        ttk.Label(
            body,
            text=T("人提出、设计、验收；AI 写出全部代码。"),
            foreground=theme_get("fg_dim")).pack(anchor="w", pady=(2, 10))

        # ★ 正文：只读 Text（能选中复制、能滚）
        #   ★★ 注意：`tk.Text` **必须给 width**（错题本里踩过 ——
        #      不给就默认 80 字符宽 ≈ 884 像素，窗口"莫名其妙很宽"）
        box = tk.Text(body, width=72, height=17, wrap="word",
                      font=(FONT, UI_FONT_SIZE),
                      bg=theme_get("text_bg"), fg=theme_get("fg"),
                      relief="flat", padx=10, pady=8)
        box.pack(fill="both", expand=True)
        box.insert("1.0", T(_CREDITS_TEXT))
        box.configure(state="disabled")

        btns = ttk.Frame(body)
        btns.pack(fill="x", pady=(10, 0))
        try:
            ttk.Button(btns, text=T("打开仓库"), width=12,
                       command=lambda: _open_url(_REPO_URL)
                       ).pack(side="left")
        except Exception:
            pass
        ttk.Button(btns, text=T("确定"), width=10,
                   command=win.destroy).pack(side="right")
        try:
            win.bind("<Escape>", lambda e: win.destroy())
        except Exception:
            pass
        try:
            win.update_idletasks()
            rx = (parent or app.root).winfo_rootx()
            ry = (parent or app.root).winfo_rooty()
            rw = (parent or app.root).winfo_width()
            rh = (parent or app.root).winfo_height()
            win.geometry("+%d+%d" % (
                rx + max(0, (rw - win.winfo_reqwidth()) // 2),
                ry + max(0, (rh - win.winfo_reqheight()) // 4)))
        except Exception:
            pass
        try:
            win.grab_set()
        except Exception:
            pass
    except Exception as _e:
        note_swallowed(T("打开「版权与来源」失败"), _e)
        # 兜底：画不出来就退回系统弹窗（至少能看到内容）
        try:
            messagebox.showinfo(T("版权与来源"), T(_CREDITS_TEXT),
                                parent=parent or app.root)
        except Exception:
            pass


def show_about(app):
    """★ 关于。

    ★★ 2026-10-07：从 `messagebox.showinfo` **改成自己画的窗口**。
      为什么改：
        · 用户报「**关于对话框整片白**」—— 因为 `messagebox` 是
          **Windows 系统弹窗**，走系统 API，**颜色完全不受程序控制**
          （切夜间它也还是白的）。
        · 自己画的话就能跟主题走，还能顺便把信息排得好看点。
      ★ 顺带修：版本号原来写 **v24**，而标题栏是 **v26** —— 对不上了。
    """
    try:
        win = tk.Toplevel(app.root)
        win.title("关于")
        win.transient(app.root)
        win.resizable(False, False)
        # ★ Toplevel 是原生窗口，底色必须自己设（错题本 #92）
        try:
            win.configure(bg=theme_get("win_bg"))
        except Exception:
            pass
        # ★ 登记一下，切主题时跟着变
        try:
            _reg = getattr(app, "_theme_windows", None)
            if _reg is None:
                _reg = app._theme_windows = []
            _reg.append(win)
        except Exception:
            pass

        body = ttk.Frame(win, padding=18)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text=T("📁 文件标签管理器"),
                  font=(FONT, UI_FONT_SIZE + 3, BOLD)).pack(anchor="w")
        ttk.Label(
            body,
            text=T("带标签图结构、星图编辑、瀑布流浏览的本地文件标签工具。"),
            foreground=theme_get("fg_dim")).pack(anchor="w", pady=(4, 10))

        # ★★★ 版权与来源（2026-10-08）★★★
        #   ★ 用户要求「**一开始就醒目标明**」——
        #     所以放在**标题下面第一块**，不是最底下的小字。
        #   ★★ 为什么必须放在这里（不只是 README）：
        #     **下载 exe 的人不会去看 README，但他会点「关于」**。
        #   ★ 判据：**"声明要放在读者真正会到的地方"**。
        credit = tk.Frame(body, bg=theme_get("sel_bg") if
                          theme_get("sel_bg") else theme_get("win_bg"))
        credit.pack(fill="x", pady=(0, 12))
        tk.Label(
            credit,
            text=T("★ 代码由 AI（DeepSeek）编写 —— 人提出、设计、验收。"),
            bg=credit.cget("bg"), fg=theme_get("fg"),
            font=(FONT, UI_FONT_SIZE, BOLD),
            anchor="w", justify="left").pack(fill="x", padx=10, pady=(8, 2))
        tk.Label(
            credit,
            text=T("★ 版权由作者与深度求索（DeepSeek）共同持有。"),
            bg=credit.cget("bg"), fg=theme_get("fg_dim"),
            anchor="w", justify="left").pack(fill="x", padx=10, pady=(0, 8))
        info = [
            (T("版本"), "v26"),
            (T("当前界面缩放"), "%d%%" % int(app.ui_scale * 100)),
            (T("数据库"), str(DB_PATH)),
            (T("导出目录"), str(EXPORT_DIR)),
            (T("设置文件"), str(SETTINGS_PATH)),
        ]
        for k, v in info:
            row = ttk.Frame(body)
            row.pack(fill="x", pady=1)
            ttk.Label(row, text=k, width=12,
                      foreground=theme_get("fg_dim")).pack(side="left")
            # ★ 路径可能很长 → 用只读 Entry，能选中复制
            e = ttk.Entry(row, width=58, font=(FONT, UI_FONT_SIZE_SMALL))
            e.insert(0, v)
            e.configure(state="readonly")
            e.pack(side="left", fill="x", expand=True)

        btns = ttk.Frame(body)
        btns.pack(fill="x", pady=(14, 0))
        # ★ 版权详情入口（★ 声明正文比较长，单独一个窗看）
        ttk.Button(btns, text=T("版权与来源…"), width=14,
                   command=lambda: app.show_credits(win)
                   ).pack(side="left")
        # ★★ 支持入口（2026-10-08）
        #   ★ 为什么放在「关于」里：**这是真实用户唯一会看到的位置**
        #     （下载 exe 的人不会去翻 README）
        #   ★★ 用 `♥` 而不是 `💰` —— 前者是"心意"，后者是"要钱"，
        #     在开源项目里这个区别很重要。
        ttk.Button(btns, text=T("♥ 支持这个项目"), width=16,
                   command=lambda: _open_url(_SPONSOR_URL)
                   ).pack(side="left", padx=(6, 0))
        ttk.Button(btns, text=T("确定"), width=10,
                   command=win.destroy).pack(side="right")
        try:
            win.bind("<Escape>", lambda e: win.destroy())
            win.bind("<Return>", lambda e: win.destroy())
        except Exception:
            pass
        # 居中到主窗口
        try:
            win.update_idletasks()
            rx = app.root.winfo_rootx()
            ry = app.root.winfo_rooty()
            rw = app.root.winfo_width()
            rh = app.root.winfo_height()
            ww = win.winfo_reqwidth()
            wh = win.winfo_reqheight()
            win.geometry("+%d+%d" % (rx + (rw - ww) // 2,
                                     ry + (rh - wh) // 3))
        except Exception:
            pass
        try:
            win.grab_set()
        except Exception:
            pass
    except Exception as _e:
        note_swallowed(T("打开「关于」失败"), _e)
        # 兜底：实在画不出来就退回系统弹窗（至少能看到信息）
        try:
            messagebox.showinfo("关于", T("文件标签管理器 v26"), parent=app.root)
        except Exception:
            pass


def show_health_report(app):
    """★★ 2026-10-05「先加说话」：点菜单就能看「体检报告」。

    用户原话：「老卡死，界面有些部分经常显示不全，改来改去经常前面
    写好的功能后面没了」。这份报告的用处就是——**让程序别闷着**，
    把这些「本来没人知道」的小毛病摊开给他看。

    输出全是中文说法 + 出错次数，他能直接复制发给我。
    """
    try:
        text = app.dump_swallowed_report()
    except Exception as e:
        text = f"生成报告失败：{e}"
    try:
        # 顺手也写进「问题」面板，这样关掉小窗还能回看
        for _ln in str(text).split("\n"):
            if _ln.strip():
                app.log_problem(_ln, level="info")
    except Exception:
        pass
    try:
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
        win.title("🩺 体检报告 —— 哪些地方在偷偷出错")
        win.transient(app.root)
        fr = ttk.Frame(win, padding=10)
        fr.pack(fill="both", expand=True)
        ttk.Label(fr, text="下面是程序自己记下来的「没吭声的小毛病」。\n"
                           "次数越多越值得查；把这份内容发我即可。",
                  justify="left").pack(anchor="w", pady=(0, 6))
        box = tk.Text(fr, width=76, height=22, wrap="none",
                      font=(FONT, UI_FONT_SIZE))
        box.pack(fill="both", expand=True)
        box.insert("1.0", str(text))
        box.configure(state="disabled")
        btns = ttk.Frame(fr)
        btns.pack(fill="x", pady=(8, 0))

        def _copy():
            try:
                app.root.clipboard_clear()
                app.root.clipboard_append(str(text))
                app.set_status(T("体检报告已复制到剪贴板"))
            except Exception as _e:
                note_swallowed(T("复制体检报告失败"), _e, quiet=True)

        def _save():
            try:
                fn = filedialog.asksaveasfilename(
                    title=T("保存体检报告"), defaultextension=".txt",
                    initialfile="体检报告.txt",
                    filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
                if not fn:
                    return
                with open(fn, "w", encoding="utf-8") as f:
                    f.write(str(text))
                app.set_status(f"已保存：{fn}")
            except Exception as _e:
                note_swallowed(T("保存体检报告失败"), _e)

        ttk.Button(btns, text=T("复制到剪贴板"), command=_copy).pack(side="left")
        ttk.Button(btns, text=T("另存为文件…"), command=_save).pack(side="left", padx=6)
        ttk.Button(btns, text=T("关闭"), command=win.destroy).pack(side="right")
        win.update_idletasks()
        try:
            win.geometry("")
        except Exception:
            pass
    except Exception as _e:
        note_swallowed(T("打开体检报告窗口失败"), _e)
