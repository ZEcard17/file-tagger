# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：TagBoxPicker。

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
_NEED = ['enable_wheel_scroll', 'note_swallowed']
_SIBLINGS = ['AutoNameRulesDialog', 'CategoryDialog', 'CategoryHiddenTagsDialog', 'CategoryItem', 'CategorySidebar', 'CategoryTagLinkDialog', 'PreviewPane', 'RemoveFileTagsDialog', 'ScanProgressDialog', 'ShortcutDialog', 'SimpleInputDialog', 'TagBoxGridDialog', 'TagBoxPicker', 'TagPickerDialog', 'UIScaleDialog']
_APP = None
enable_wheel_scroll = None
note_swallowed = None


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

class TagBoxPicker(tk.Toplevel):
    """★ 补丁26：从「用得最多的标签」里勾选放进标签盒。"""

    def __init__(self, master, box):
        super().__init__(master)
        self.box = box
        self.store = box.store
        self.title("把标签放进标签盒")
        self.geometry("560x600")
        self.transient(master)
        self.vars = {}
        # ★ 补丁39：勾选状态单独存一份（tid -> 是否勾上）。
        #   搜索会把一部分标签藏起来，如果只看界面上的控件，
        #   藏起来那些的勾选就会丢 —— 所以单独记着。
        self._checked = {}

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(body, text="勾上要放进盒子的标签（按「用得最多」排序）：",
                  justify="left").pack(anchor="w")
        ttk.Label(body, text="（「固定」= 换视图也留着；不勾固定就是这次用用）",
                  foreground="#777").pack(anchor="w", pady=(0, 6))

        # ★ v25 补丁39（用户提的）：这个窗口**原来没有搜索框** —— 标签有
        #   两百多个，想找一个只能一行行往下翻，非常难用。现在加一个，
        #   边打边筛（按标签名，不区分大小写）。
        sbar = ttk.Frame(body)
        sbar.pack(fill="x", pady=(0, 6))
        ttk.Label(sbar, text="🔍 搜索标签：").pack(side="left")
        self.search_var = tk.StringVar()
        _se = ttk.Entry(sbar, textvariable=self.search_var)
        _se.pack(side="left", fill="x", expand=True, padx=(4, 4))
        _se.focus_set()
        self.search_var.trace_add("write", lambda *a: self._load())
        ttk.Button(sbar, text="清除", width=6,
                   command=lambda: self.search_var.set("")).pack(side="left")
        self.count_lbl = ttk.Label(body, text="", foreground="#16a085")
        self.count_lbl.pack(anchor="w", pady=(0, 4))

        wrap = ttk.Frame(body)
        wrap.pack(fill="both", expand=True)
        sb = ttk.Scrollbar(wrap, orient="vertical")
        sb.pack(side="right", fill="y")
        self.canvas = tk.Canvas(wrap, highlightthickness=0,
                                yscrollcommand=sb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        sb.configure(command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(
            -1 if e.delta > 0 else 1, "units"))
        # ★ 鼠标停在标签文字上也能滚（不用去拖进度条）
        try:
            enable_wheel_scroll(self, self.canvas)
        except Exception:
            pass

        self.fixed_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(body, text="固定进盒子（换视图也在）",
                        variable=self.fixed_var).pack(anchor="w", pady=(6, 4))
        btns = ttk.Frame(body)
        btns.pack(fill="x")
        ttk.Button(btns, text="确定", command=self._ok).pack(side="right")
        ttk.Button(btns, text="取消", command=self.destroy).pack(
            side="right", padx=6)
        self.bind("<Escape>", lambda e: self.destroy())
        self._load()

    def _load(self):
        """把「用得最多」的标签列出来（带搜索）。

        ★ 补丁39：原来一次全列出来、没有搜索。现在：
          · 搜索词一变就重画（边打边筛）；
          · **已经勾上的状态不会因为重画而丢** —— 勾选状态单独存在
            self.vars 里（tid -> 布尔），重画只是重新摆控件。
        """
        # 先把「上一次界面上勾了什么」收回来（重画会销毁控件）
        try:
            for tid, var in list(self.vars.items()):
                self._checked[tid] = bool(var.get())
        except Exception:
            pass
        for w in self.inner.winfo_children():
            w.destroy()
        self.vars = {}
        rows = []
        try:
            rows = self.store.tags_by_usage(limit=1000)
        except Exception as exc:
            note_swallowed("标签盒：读「用得最多的标签」失败", exc)
        q = ""
        try:
            q = (self.search_var.get() or "").strip().lower()
        except Exception:
            pass
        show = []
        for r in rows:
            nm = str(r["name"] or "")
            if q and q not in nm.lower():
                continue
            show.append(r)
        try:
            self.count_lbl.config(
                text=("显示 %d / %d 个标签" % (len(show), len(rows)))
                if q else ("共 %d 个标签" % len(rows)))
        except Exception:
            pass
        in_box = set()
        try:
            in_box = set(self.box.box_ids())
        except Exception:
            pass
        for r in show:
            tid, name, cnt = r["id"], r["name"], r.get("cnt", 0)
            if tid in self._checked:
                val = self._checked[tid]
            else:
                val = tid in in_box
            var = tk.BooleanVar(value=val)
            self.vars[tid] = var
            cb = ttk.Checkbutton(self.inner, text="%s（%d 个文件）" % (name, cnt),
                                 variable=var)
            cb.pack(anchor="w")
        if not show:
            ttk.Label(self.inner,
                      text=("（没有匹配的标签）" if q else "（读不到标签……）"),
                      foreground="#999").pack(anchor="w", pady=6)

    def _ok(self):
        fixed = bool(self.fixed_var.get())
        # ★ 补丁39：先把界面上现在的勾选收进 _checked（因为搜索会把
        #   一部分标签藏起来，直接遍历 self.vars 会漏掉被藏起来的那些）。
        try:
            for tid, var in list(self.vars.items()):
                self._checked[tid] = bool(var.get())
        except Exception:
            pass
        for tid, want in list(self._checked.items()):
            try:
                in_box = tid in self.box.box_ids()
            except Exception:
                in_box = False
            if want and not in_box:
                if fixed:
                    try:
                        self.store.tag_box_add(tid)
                    except Exception:
                        pass
                else:
                    try:
                        self.box.add_tag(tid)
                    except Exception:
                        pass
            elif not want and in_box:
                try:
                    self.box.remove_tag(tid)
                except Exception:
                    pass
        try:
            self.box._redraw()
        except Exception:
            pass
        self.destroy()


