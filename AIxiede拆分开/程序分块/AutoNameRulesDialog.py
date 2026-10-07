# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：AutoNameRulesDialog。

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
_NEED = ['FONT', 'UI_FONT_SIZE', 'enable_wheel_scroll', 'note_swallowed', 'messagebox']
_SIBLINGS = ['AutoNameRulesDialog', 'CategoryDialog', 'CategoryHiddenTagsDialog', 'CategoryItem', 'CategorySidebar', 'CategoryTagLinkDialog', 'PreviewPane', 'RemoveFileTagsDialog', 'ScanProgressDialog', 'ShortcutDialog', 'SimpleInputDialog', 'TagBoxGridDialog', 'TagBoxPicker', 'TagPickerDialog', 'UIScaleDialog']
_APP = None
FONT = None
UI_FONT_SIZE = None
enable_wheel_scroll = None
note_swallowed = None
messagebox = None


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

class AutoNameRulesDialog(tk.Toplevel):
    """勾选一批标签：文件名里出现标签名，就自动给文件打上该标签。"""

    def __init__(self, master, store):
        super().__init__(master)
        self.title("文件名自动标签规则")
        self.geometry("500x640")
        self.minsize(420, 480)
        self.store = store
        self.saved = False

        self.all_tags = store.all_tags()      # [(id, name, color, cnt), ...]
        chosen = store.get_auto_name_rule_tag_ids()

        self.tag_vars = {}
        for tid, name, color, cnt in self.all_tags:
            self.tag_vars[tid] = tk.BooleanVar(value=(tid in chosen))

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        ttk.Label(
            body,
            text=("勾选标签后，凡是文件名里出现该标签名的文件，"
                  "会自动被打上这个标签。\n"
                  "比如勾了「报表」，那么“2024销售报表.xlsx”就会自动"
                  "获得「报表」标签。\n"
                  "保存后不会立刻生效；请在「自动标签规则」窗口里，"
                  "点「▶▶ 应用文件名规则」按钮手动跑一次。"),
            foreground="#666", justify="left",
            wraplength=460).pack(anchor="w", pady=(0, 6))

        # 搜索行
        sbar = ttk.Frame(body)
        sbar.pack(fill="x", pady=(0, 6))
        ttk.Label(sbar, text="🔍 搜索标签：").pack(side="left")
        self.search_var = tk.StringVar()
        se = ttk.Entry(sbar, textvariable=self.search_var)
        se.pack(side="left", fill="x", expand=True, padx=(4, 4))
        self.search_var.trace_add("write", lambda *a: self._render_list())
        ttk.Button(sbar, text="清除", width=6,
                   command=lambda: self.search_var.set("")
                   ).pack(side="left")

        self.search_info = ttk.Label(body, text="", foreground="#16a085")
        self.search_info.pack(anchor="w", pady=(0, 4))

        # 列表
        wrap = ttk.Frame(body)
        wrap.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(wrap, highlightthickness=1,
                                highlightbackground="#cccccc",
                                bg="white")
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg="white")
        self._win_id = self.canvas.create_window(
            (0, 0), window=self.inner, anchor="nw")
        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(self._win_id, width=e.width))

        self.canvas.bind("<MouseWheel>", self._wheel)
        self.canvas.bind("<Button-4>", self._wheel)
        self.canvas.bind("<Button-5>", self._wheel)
        # ★ v25：鼠标停在勾选框 / 标签文字上也能滚（不用去拖进度条）
        enable_wheel_scroll(self, self.canvas)

        # 底部按钮
        btns = ttk.Frame(body)
        btns.pack(fill="x", pady=(10, 0))
        ttk.Button(btns, text="保存",
                   command=self._save).pack(side="right")
        ttk.Button(btns, text="取消",
                   command=self._cancel).pack(side="right", padx=6)
        ttk.Button(btns, text="全不选",
                   command=lambda: self._set_all(False)).pack(side="left")
        ttk.Button(btns, text="全选",
                   command=lambda: self._set_all(True)).pack(side="left",
                                                             padx=4)

        self.bind("<Escape>", lambda e: self._cancel())
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        self._render_list()

        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = master.winfo_rootx() + (master.winfo_width() - w) // 2
        y = master.winfo_rooty() + (master.winfo_height() - h) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def _render_list(self):
        for w in self.inner.winfo_children():
            w.destroy()

        q = (self.search_var.get() or "").strip().lower()
        shown = 0
        for tid, name, color, cnt in self.all_tags:
            if q and q not in (name or "").lower():
                continue
            shown += 1
            row = tk.Frame(self.inner, bg="white")
            row.pack(fill="x", padx=4, pady=1)
            var = self.tag_vars[tid]
            cb = tk.Checkbutton(
                row, text="", variable=var,
                bg="white", activebackground="white",
                selectcolor="white", borderwidth=0,
                highlightthickness=0)
            cb.pack(side="left")
            lbl = tk.Label(row, text=f"{name}   ({cnt})",
                           bg="white", fg=color or "#333",
                           anchor="w", font=(FONT, UI_FONT_SIZE))
            lbl.pack(side="left", fill="x", expand=True)

            def _toggle(_e, v=var):
                v.set(not v.get())

            lbl.bind("<Button-1>", _toggle)
            row.bind("<Button-1>", _toggle)

        if shown == 0:
            tk.Label(self.inner, text="（没有匹配的标签）",
                     bg="white", fg="#999").pack(pady=16)
            self.search_info.config(text="")
        elif q:
            self.search_info.config(
                text=f"显示 {shown} / {len(self.all_tags)}")
        else:
            n_on = sum(1 for v in self.tag_vars.values() if v.get())
            if n_on:
                self.search_info.config(
                    text=f"已选 {n_on} 个标签参与文件名匹配")
            else:
                self.search_info.config(text="（没有勾选任何标签）")

    def _wheel(self, event):
        if event.num == 4:
            d = -1
        elif event.num == 5:
            d = 1
        else:
            d = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(d, "units")

    def _set_all(self, val):
        q = (self.search_var.get() or "").strip().lower()
        for tid, name, color, cnt in self.all_tags:
            if q and q not in (name or "").lower():
                continue
            self.tag_vars[tid].set(val)
        self._render_list()

    def _save(self):
        chosen = [tid for tid, v in self.tag_vars.items() if v.get()]
        # ★ v25 补丁4：同上，写库失败要让用户看见，而不是「没反应」。
        try:
            self.store.set_auto_name_rule_tag_ids(chosen)
        except Exception as _e:
            note_swallowed("保存「文件名规则」勾选失败", _e)
            messagebox.showerror(
                "保存失败",
                f"没能保存文件名规则的标签勾选：\n{_e}\n\n"
                "（可以先关掉程序再重开；如果一直失败，多半是数据库被其它"
                "窗口占用）",
                parent=self)
            return
        self.saved = True
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

    def _cancel(self):
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()


# ==========================================================================
#  ★ 星图编辑器（v21：层级自动布局 + 拖动跟手 + 曲线连线）
# ==========================================================================
# ==========================================================================
#  ★ 星图编辑器（v22：多父级修复 + 最大化按钮）
# ==========================================================================
