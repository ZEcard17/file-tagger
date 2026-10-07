# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：RemoveFileTagsDialog。

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
_NEED = ['BOLD', 'FONT', 'UI_FONT_SIZE', 'messagebox']
_SIBLINGS = ['AutoNameRulesDialog', 'CategoryDialog', 'CategoryHiddenTagsDialog', 'CategoryItem', 'CategorySidebar', 'CategoryTagLinkDialog', 'PreviewPane', 'RemoveFileTagsDialog', 'ScanProgressDialog', 'ShortcutDialog', 'SimpleInputDialog', 'TagBoxGridDialog', 'TagBoxPicker', 'TagPickerDialog', 'UIScaleDialog']
_APP = None
BOLD = None
FONT = None
UI_FONT_SIZE = None
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

class RemoveFileTagsDialog(tk.Toplevel):
    """★★ v26（2026-10-01）：右键「去除文件上的标签…」。

    用法（用户要的就是这个）：
      · 把选中文件身上的标签**全部列出来**，每个前面一个复选框；
      · 你勾哪几个，就去掉哪几个；
      · 点「确认去除」后**还会再问一次**（列出具体名字），
        你点「是」才真的动手。

    重要：只删「这些文件身上的这些标签」，
    **标签本身、标签树、别的文件都不受影响**。
    """

    def __init__(self, master, app, store, paths):
        super().__init__(master)
        self.app = app
        self.store = store
        self.paths = [p for p in (paths or []) if p]
        self.result = None

        self.title("去除文件上的标签")
        self.geometry("520x620")
        self.minsize(420, 420)
        self.transient(master)
        try:
            self.grab_set()
        except Exception:
            pass

        body = ttk.Frame(self, padding=10)
        body.pack(fill="both", expand=True)

        ttk.Label(
            body,
            text="共 %d 个文件：勾上想去掉的标签，然后点“确认去除”"
                 % len(self.paths),
            foreground="#555", wraplength=470, justify="left").pack(anchor="w")

        # 汇总这几个文件身上的所有标签（id -> （名字, 颜色, 出现次数））
        self.tag_info = {}
        self._collect()

        ctrl = ttk.Frame(body)
        ctrl.pack(fill="x", pady=(8, 4))
        ttk.Button(ctrl, text="全选", width=8,
                   command=lambda: self._set_all(True)).pack(side="left")
        ttk.Button(ctrl, text="全不选", width=8,
                   command=lambda: self._set_all(False)).pack(side="left", padx=4)
        ttk.Button(ctrl, text="只选自动标签", width=12,
                   command=self._pick_auto).pack(side="left")
        self.count_lbl = ttk.Label(ctrl, text="", foreground="#16a085")
        self.count_lbl.pack(side="right")

        wrap = ttk.Frame(body)
        wrap.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(wrap, highlightthickness=1,
                                highlightbackground="#cccccc", bg="white")
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self._font = tkfont.Font(family=FONT, size=UI_FONT_SIZE, weight=BOLD)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.canvas.bind("<Button-4>", self._on_wheel)
        self.canvas.bind("<Button-5>", self._on_wheel)
        self.canvas.bind("<Configure>", lambda e: self._render())

        foot = ttk.Frame(body)
        foot.pack(fill="x", pady=(8, 0))
        ttk.Button(foot, text="确认去除", width=14,
                   command=self._ok).pack(side="right")
        ttk.Button(foot, text="取消", width=10,
                   command=self.destroy).pack(side="right", padx=6)

        self.bind("<Escape>", lambda e: self.destroy())
        self._render()
        try:
            self.wait_visibility()
        except Exception:
            pass

    # ---------- 数据 ----------
    def _collect(self):
        """把这几个文件身上的标签汇总起来。"""
        try:
            info = self.store.tags_for_paths(self.paths) or {}
        except Exception:
            info = {}
        for p in self.paths:
            for rec in (info.get(p) or []):
                try:
                    tid, name, color = int(rec[0]), rec[1], rec[2]
                except Exception:
                    continue
                cur = self.tag_info.get(tid)
                if cur is None:
                    self.tag_info[tid] = {"name": name, "color": color,
                                          "n": 1}
                else:
                    cur["n"] += 1
        # 归类：自动（继承/规则）的放后面，手动的放前面
        self._auto_ids = set()
        try:
            ids = list(self.tag_info.keys())
            if ids:
                ph = ",".join("?" * len(ids))
                for r in self.store.conn.execute(
                        "SELECT DISTINCT tag_id FROM file_tags "
                        "WHERE is_auto <> 0 AND tag_id IN (%s)" % ph,
                        tuple(ids)):
                    self._auto_ids.add(int(r[0]))
        except Exception:
            pass
        self.checked = set()

    def _ordered(self):
        """排序：手动标签在前，然后按名字。"""
        items = []
        for tid, d in self.tag_info.items():
            items.append((0 if tid not in self._auto_ids else 1,
                          d["name"] or "", tid, d))
        items.sort(key=lambda x: (x[0], x[1]))
        return items

    def _set_all(self, on):
        self.checked = set(self.tag_info.keys()) if on else set()
        self._render()

    def _pick_auto(self):
        self.checked = set(self._auto_ids)
        self._render()

    # ---------- 画 ----------
    def _row_h(self):
        return self._font.metrics("linespace") + 14

    def _render(self):
        c = self.canvas
        try:
            c.delete("all")
        except Exception:
            return
        f = self._font
        h = self._row_h()
        W = max(c.winfo_width(), 260)
        items = self._ordered()
        if not items:
            c.create_text(12, 16, anchor="nw", fill="#999", font=(FONT, UI_FONT_SIZE),
                          text="（这些文件上没有任何标签）")
            c.configure(scrollregion=(0, 0, W, 60))
            self._sync_count()
            return
        y = 6
        for _grp, _nm, tid, d in items:
            on = tid in self.checked
            # 复选框
            c.create_rectangle(12, y + 4, 26, y + 18, outline="#5d6d7e",
                               width=1, fill="white",
                               tags=("cb", "t%d" % tid))
            if on:
                c.create_line(15, y + 11, 19, y + 16, 24, y + 5,
                              fill="#16a085", width=2,
                              tags=("cb", "t%d" % tid))
            # 颜色小块
            c.create_rectangle(34, y + 5, 46, y + 17,
                               fill=d["color"] or "#3498db", outline="",
                               tags=("cb", "t%d" % tid))
            label = d["name"]
            if tid in self._auto_ids:
                label += "（自动）"
            if d["n"] < len(self.paths):
                label += "  — %d/%d 个文件" % (d["n"],
                                                          len(self.paths))
            c.create_text(54, y + h / 2 - 4, anchor="w",
                          text=label, font=f,
                          fill="#111" if on else "#333",
                          tags=("cb", "t%d" % tid))
            c.create_line(10, y + h - 4, W - 8, y + h - 4, fill="#eee",
                          tags=("cb", "t%d" % tid))
            y += h
        c.configure(scrollregion=(0, 0, W, y + 8))
        self._sync_count()

    def _sync_count(self):
        try:
            self.count_lbl.config(
                text="已勾 %d / %d" % (len(self.checked),
                                            len(self.tag_info)))
        except Exception:
            pass

    def _on_wheel(self, event):
        d = -3 if getattr(event, "delta", 0) > 0 or event.num == 4 else 3
        self.canvas.yview_scroll(d, "units")
        self._render()

    def _on_click(self, event):
        cy = self.canvas.canvasy(event.y)
        h = self._row_h()
        idx = int((cy - 6) // h)
        items = self._ordered()
        if idx < 0 or idx >= len(items):
            return
        tid = items[idx][2]
        if tid in self.checked:
            self.checked.discard(tid)
        else:
            self.checked.add(tid)
        self._render()

    # ---------- 确认 ----------
    def _ok(self):
        if not self.checked:
            messagebox.showinfo("去除标签",
                                "你还没勾任何标签。",
                                parent=self)
            return
        names = [self.tag_info[t]["name"] for t in self.checked
                 if t in self.tag_info]
        shown = "、".join(names[:15]) + ("…" if len(names) > 15 else "")
        if not messagebox.askyesno(
                "确认去除",
                "确定要从 %d 个文件上去掉这 %d 个标签吗？\n\n%s\n\n"
                "（只去掉文件上的这些标签，\n"
                "标签本身和别的文件都不受影响）"
                % (len(self.paths), len(self.checked), shown),
                parent=self):
            return
        self.result = list(self.checked)
        self.destroy()


