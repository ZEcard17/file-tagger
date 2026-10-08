# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：TagPickerDialog。

★ 代码**原样搬运**，一个字没改，只是换了个文件放。

★★ 拆文件的规矩（所有分块文件都照这个写）★★
   ① **Python 自带的东西直接 import**（tk、ttk、os、sys…）——不绕弯。
   ② **只有主程序自己造的东西才向主程序借**（FONT、note_swallowed 这类）。
      而且**不在开头 import 主程序**——两边互相 import 会让 Python
      报错、程序打不开。借法是主程序启动时把「自己」交进来（_set_app）。
   ③ 借来的名字做成**模块级变量**，这样下面的代码**一个字都不用改**。
   ④ 借不到就用兜底值，**不能因为主程序改了个名字就整个打不开**。
"""

import os
import sys
import time
import threading
import queue

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, colorchooser

# ---------- 要向主程序借的名字（先占位，挂上后填真身） ----------
_NEED = ['FONT', 'UI_FONT_SIZE', 'enable_wheel_scroll']
_SIBLINGS = ['AutoNameRulesDialog', 'CategoryDialog', 'CategoryHiddenTagsDialog', 'CategoryItem', 'CategorySidebar', 'CategoryTagLinkDialog', 'PreviewPane', 'RemoveFileTagsDialog', 'ScanProgressDialog', 'ShortcutDialog', 'SimpleInputDialog', 'TagBoxGridDialog', 'TagBoxPicker', 'TagPickerDialog', 'UIScaleDialog']
_APP = None
FONT = None
UI_FONT_SIZE = None
enable_wheel_scroll = None




# ==========================================================================
#  ★★★ 2026-10-08 **多语言**：模块里的界面文字也走 T() ★★★
#  --------------------------------------------------------------------------
#  ★ 为什么"向主程序要"（而不是自己 `from i18n import T`）：
#    · 那样**语言表就有两套**了 —— 用户切语言时可能**不同步**
#    · ★★ 统一"向主程序要"：**只有一处知道当前语言**（主程序的 i18n）
#    ★ 而本模块**已经有** `_need()`（向主程序借名字的通道），
#      所以这里**只是多要一个 `T`**，不引入新机制。
#
#  ★★ 为什么要有那个 `except` 兜底：
#    万一主程序还没接上（`_set_app` 没调），或者 `T` 取不到，
#    **也要返回原文**（能看），**不能报错**（界面上的字不该让程序崩）。
# ==========================================================================
def T(text, **kw):
    """★ 向主程序要翻译（取不到就返回原文 —— 界面永远能看）。"""
    try:
        f = _need("T")
        if f is not None:
            return f(text, **kw)
    except Exception:
        pass
    try:
        return str(text).format(**kw) if kw else str(text)
    except Exception:
        return str(text)

def _set_app(app):
    """主程序启动时调一下：把「自己」交进来，顺便把要借的名字填上。"""
    global _APP
    _APP = app
    _fill()
    _link_siblings()
    _link_siblings()
    _link_siblings()


def _fill():
    """从主程序身上把需要的名字取过来，填进本模块的同名变量。"""
    if _APP is None:
        return
    g = globals()
    for _n in _NEED:
        try:
            _v = getattr(_APP, _n, None)
            if _v is not None:
                g[_n] = _v
        except Exception:
            pass





# ---------- 「兄弟文件互相认识」 ----------
def _link_siblings():
    """去同一批拆出来的兄弟文件里，找本文件用到的类。

    ★ 为什么需要：拆出来之后，有的类要用别的拆出来的类
      （比如 CategorySidebar 要用 CategoryItem）。
      原来它们都在一个大文件里，随便用；拆开后就得互相找一下。
    ★ ★ 正确做法：**把每个兄弟文件都试着导入一遍**，然后看它有没有
      本文件缺的类。找不到也不报错（万一那个文件没拆过来，不影响别的）。
    """
    try:
        import importlib
        g = globals()
        my = __name__
        for _sib in _SIBLINGS:
            if _sib == my:
                continue
            # 本文件已经用过这个类了吗（值为 None 说明还没填）
            if g.get(_sib, "缺") is not None and g.get(_sib, "缺") != "缺":
                continue
            try:
                _m = importlib.import_module(_sib)
            except Exception:
                continue
            _cls = getattr(_m, _sib, None)
            if _cls is not None:
                g[_sib] = _cls
    except Exception:
        pass

def _grab(name, default=None):
    """临时借一个名字（借不到用 default）。"""
    if _APP is not None:
        v = getattr(_APP, name, None)
        if v is not None:
            return v
    return default


def _ensure():
    """保证借来的名字都有值（第一次用到时兜一下）。"""
    global _APP
    if _APP is None:
        # 还没挂上 —— 试着从「已经在跑的主程序」那儿拿（通常拿得到）
        try:
            import sys as _s
            for _m in list(_s.modules.values()):
                if _m is not None and getattr(_m, '__name__', '') == 'AIxiede':
                    _set_app(_m)
                    break
        except Exception:
            pass
    else:
        _fill()
    _link_siblings()
    _link_siblings()
    _link_siblings()

class TagPickerDialog(tk.Toplevel):
    """从已有标签里挑一个（带搜索框）。"""

    def __init__(self, master, all_tags, current="", multi=False, title=None,
                 exclude_ids=None):
        super().__init__(master)
        self.title(title or ("选择标签（可多选）" if multi else "选择标签"))
        self.geometry("420x560")
        self.minsize(340, 400)
        # ★ v25 补丁38（bug 修复）：这个窗口以前**只能单选**，而且只返回
        #   一个「标签名字」（字符串）。可是星图里的「＋ 加父级标签… /
        #   ＋ 加子级标签…」按钮需要的是**一批标签 id**，而且还得能排除
        #   掉自己 / 自己的祖先。原来那边调的是一个**根本不存在的类**
        #   `TagPickDialog` —— 一按就 NameError，被 except 包着，弹一句
        #   「打不开勾选窗口」，**功能等于废的**。
        #   现在给这个窗口加了：
        #     · multi=True   → 变成多选（勾选），result 是 id 的列表
        #     · exclude_ids  → 这些 id 不显示（用来排除自己/祖先/后代）
        #     · title        → 自定义标题
        #   单选老用法（result 是标签名字符串）完全不变。
        self.multi = bool(multi)
        self.result = None
        self.all_tags = list(all_tags or [])
        try:
            self._exclude = set(int(x) for x in (exclude_ids or []))
        except Exception:
            self._exclude = set()
        # 多选模式下勾中的 id（name -> id 的映射下面 _render 里建）
        self._checked = set()
        self._name2id = {}
        if self.multi:
            for t in self.all_tags:
                try:
                    if str(t[1]) == str(current or ""):
                        self._checked.add(int(t[0]))
                except Exception:
                    pass

        body = ttk.Frame(self, padding=10)
        body.pack(fill="both", expand=True)

        sbar = ttk.Frame(body)
        sbar.pack(fill="x", pady=(0, 6))
        ttk.Label(sbar, text=T("🔍 搜索标签：")).pack(side="left")
        self.search_var = tk.StringVar()
        e = ttk.Entry(sbar, textvariable=self.search_var)
        e.pack(side="left", fill="x", expand=True, padx=(4, 4))
        e.focus_set()
        self.search_var.trace_add("write", lambda *a: self._render())

        self.count_lbl = ttk.Label(body, text="", foreground="#16a085")
        self.count_lbl.pack(anchor="w", pady=(0, 4))

        wrap = ttk.Frame(body)
        wrap.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(wrap, highlightthickness=1,
                                highlightbackground="#cccccc", bg="white")
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg="white")
        self._win_id = self.canvas.create_window(
            (0, 0), window=self.inner, anchor="nw")
        self.inner.bind(
            "<Configure>",
            lambda ev: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))
        self.canvas.bind(
            "<Configure>",
            lambda ev: self.canvas.itemconfigure(self._win_id, width=ev.width))
        self.canvas.bind("<MouseWheel>", self._wheel)
        self.canvas.bind("<Button-4>", self._wheel)
        self.canvas.bind("<Button-5>", self._wheel)
        # ★ v25：鼠标停在标签文字上也能滚（不用去拖进度条）
        enable_wheel_scroll(self, self.canvas)

        btns = ttk.Frame(body)
        btns.pack(fill="x", pady=(8, 0))
        if self.multi:
            ttk.Button(btns, text=T("确定"),
                       command=self._ok).pack(side="right")
            ttk.Button(btns, text=T("取消"),
                       command=self._cancel).pack(side="right", padx=6)
            ttk.Button(btns, text=T("全不选"),
                       command=self._none).pack(side="left")
        else:
            ttk.Button(btns, text=T("取消"),
                       command=self._cancel).pack(side="right")
        self.bind("<Escape>", lambda ev: self._cancel())
        if self.multi:
            self.bind("<Return>", lambda ev: self._ok())
        else:
            self.bind("<Return>", lambda ev: self._pick_first())
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        self._render()

        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = master.winfo_rootx() + (master.winfo_width() - w) // 2
        y = master.winfo_rooty() + (master.winfo_height() - h) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def _visible_tags(self):
        q = (self.search_var.get() or "").strip().lower()
        out = []
        for t in self.all_tags:
            name = t[1] if len(t) > 1 else ""
            # ★ 补丁38：多选模式下，被排除的 id（自己 / 祖先 / 后代）不显示
            if self._exclude:
                try:
                    if int(t[0]) in self._exclude:
                        continue
                except Exception:
                    pass
            if q and q not in (name or "").lower():
                continue
            out.append(t)
        return out

    def _render(self):
        for w in self.inner.winfo_children():
            w.destroy()
        self._name2id = {}
        tags = self._visible_tags()
        for t in tags:
            try:
                self._name2id[str(t[1])] = int(t[0])
            except Exception:
                pass
        if not tags:
            tk.Label(self.inner, text=T("（没有匹配的标签）"),
                     bg="white", fg="#999").pack(pady=16)
            self.count_lbl.config(text="")
            return
        extra = ""
        if self.multi:
            extra = "  ·  已勾选 %d 个" % len(self._checked)
        if self.search_var.get().strip():
            self.count_lbl.config(
                text=f"显示 {len(tags)} / {len(self.all_tags)}{extra}")
        else:
            self.count_lbl.config(text=f"共 {len(tags)} 个标签{extra}")

        for t in tags:
            tid, name, color = t[0], t[1], t[2]
            cnt = t[3] if len(t) > 3 else 0
            try:
                tid_i = int(tid)
            except Exception:
                tid_i = None
            row = tk.Frame(self.inner, bg="white", cursor="hand2")
            row.pack(fill="x")
            if self.multi:
                # ★ 补丁38：多选模式 —— 前面放个 ☑ / ☐，点一下切换
                mark = "☑" if tid_i in self._checked else "☐"
                lbl = tk.Label(row, text=f"{mark}  {name}   ({cnt})",
                               bg="white", fg=color or "#333",
                               anchor="w", font=(FONT, UI_FONT_SIZE), padx=8, pady=3)
            else:
                lbl = tk.Label(row, text=f"{name}   ({cnt})",
                               bg="white", fg=color or "#333",
                               anchor="w", font=(FONT, UI_FONT_SIZE), padx=8, pady=3)
            lbl.pack(fill="x")

            if self.multi:
                def _toggle(_e, ti=tid_i):
                    if ti is None:
                        return
                    if ti in self._checked:
                        self._checked.discard(ti)
                    else:
                        self._checked.add(ti)
                    self._render()
            else:
                def _pick(_e, n=name):
                    self.result = n
                    self._do_close()

            def _enter(_e, r=row, l=lbl):
                r.configure(bg="#eef4ff")
                l.configure(bg="#eef4ff")

            def _leave(_e, r=row, l=lbl):
                r.configure(bg="white")
                l.configure(bg="white")

            for w in (row, lbl):
                w.bind("<Button-1>", _toggle if self.multi else _pick)
                w.bind("<Enter>", _enter)
                w.bind("<Leave>", _leave)

    def _ok(self):
        """多选模式：确定 → result 是一串标签 id。"""
        self.result = sorted(self._checked)
        self._do_close()

    def _none(self):
        self._checked.clear()
        self._render()

    def _wheel(self, event):
        if event.num == 4:
            d = -1
        elif event.num == 5:
            d = 1
        else:
            d = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(d, "units")

    def _pick_first(self):
        tags = self._visible_tags()
        if tags:
            self.result = tags[0][1]
            self._do_close()

    def _do_close(self):
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

    def _cancel(self):
        self.result = None
        self._do_close()


