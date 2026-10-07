# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：一个简单输入框对话框。

★ 代码**原样搬运**，一个字没改，只是换了个文件放。

★★ 拆文件的规矩（这个文件就是照这个写的）★★
   ① **Python 自带的东西，这里直接 import**（tk、ttk、os、sys…）——
      不绕弯、不向任何人借。
   ② **只有「主程序自己造的东西」才向主程序借**（比如 FONT、note_swallowed
      这类）。而且**不在开头 import 主程序** —— 因为主程序也要用这个类，
      两边互相 import 会让 Python 报错、程序打不开。
      借法是：主程序启动时把「自己」交进来（调 _set_app），
      用的时候再从它身上取。这样引用是**一个方向**的，绝不会死循环。
"""

import os
import sys

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser

# ---------- 「用的时候才借」 ----------
_APP = None        # 主程序模块，启动时挂上


def _set_app(app):
    """主程序启动时调一下，把「自己」交给这里。"""
    global _APP
    _APP = app





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
    """向主程序借一个东西（比如 FONT、UI_FONT_SIZE）。

    ★ 借不到就用 default（而不是直接崩）—— 拆出来的文件要**尽量皮实**，
      不能因为主程序改了个名字就让整个程序打不开。
    """
    if _APP is not None:
        v = getattr(_APP, name, None)
        if v is not None:
            return v
    import builtins
    v = getattr(builtins, name, None)
    if v is not None:
        return v
    return default


def _num(name, default):
    """借一个数字（借不到就用默认值）。"""
    try:
        v = _grab(name, None)
        return int(v) if v is not None else default
    except Exception:
        return default


class SimpleInputDialog(tk.Toplevel):
    def __init__(self, master, title="输入", initial="", values=None):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.result = None

        body = ttk.Frame(self, padding=14)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=title).pack(anchor="w", pady=(0, 6))
        self.var = tk.StringVar(value=initial)
        w = (ttk.Combobox(body, textvariable=self.var, values=values, width=30)
             if values else ttk.Entry(body, textvariable=self.var, width=30))
        w.pack(fill="x")
        w.focus_set()
        try:
            w.select_range(0, "end")
        except Exception:
            pass

        btns = ttk.Frame(body)
        btns.pack(fill="x", pady=(12, 0))
        ttk.Button(btns, text="确定", command=self._ok).pack(side="right")
        ttk.Button(btns, text="取消", command=self._cancel).pack(side="right", padx=6)

        self.bind("<Return>", lambda e: self._ok())
        self.bind("<Escape>", lambda e: self._cancel())
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self._center(master)
        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def _center(self, master):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = master.winfo_rootx() + (master.winfo_width() - w) // 2
        y = master.winfo_rooty() + (master.winfo_height() - h) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def _ok(self):
        self.result = self.var.get().strip()
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


# ==========================================================================
#  新建 / 编辑分类对话框
# ==========================================================================
