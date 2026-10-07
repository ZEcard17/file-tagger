# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：CategoryDialog。

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
_NEED = ['BOLD', 'CAT_COLORS', 'FONT']
_SIBLINGS = ['AutoNameRulesDialog', 'CategoryDialog', 'CategoryHiddenTagsDialog', 'CategoryItem', 'CategorySidebar', 'CategoryTagLinkDialog', 'PreviewPane', 'RemoveFileTagsDialog', 'ScanProgressDialog', 'ShortcutDialog', 'SimpleInputDialog', 'TagBoxGridDialog', 'TagBoxPicker', 'TagPickerDialog', 'UIScaleDialog']
_APP = None
BOLD = None
CAT_COLORS = None
FONT = None


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

class CategoryDialog(tk.Toplevel):
    AVATAR_SIZE = 48

    def __init__(self, master, title="新建分类", cat=None):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        self._preview_img = None

        cat = cat or {}
        self.color = cat.get("color") or CAT_COLORS[0]
        self.icon_type = tk.StringVar(value=cat.get("icon_type") or "text")
        self.icon_text = tk.StringVar(value=cat.get("icon") or "")
        self.icon_path = tk.StringVar(value=cat.get("icon_path") or "")
        self.name_var = tk.StringVar(value=cat.get("name", ""))

        body = ttk.Frame(self, padding=16)
        body.pack(fill="both", expand=True)

        row = ttk.Frame(body)
        row.pack(fill="x", pady=(0, 10))
        ttk.Label(row, text="分类名称", width=9).pack(side="left")
        e = ttk.Entry(row, textvariable=self.name_var, width=30)
        e.pack(side="left", fill="x", expand=True)
        e.focus_set()
        self.name_var.trace_add("write", lambda *a: self._draw_preview())

        row2 = ttk.Frame(body)
        row2.pack(fill="x", pady=(0, 8))
        ttk.Label(row2, text="头像", width=9).pack(side="left", anchor="n")

        self.preview = tk.Canvas(row2, width=self.AVATAR_SIZE, height=self.AVATAR_SIZE,
                                 highlightthickness=0, bg="white")
        self.preview.pack(side="left", padx=(0, 10))

        right = ttk.Frame(row2)
        right.pack(side="left", fill="x", expand=True)

        ttk.Radiobutton(right, text="文字 / 表情", value="text",
                        variable=self.icon_type, command=self._update).pack(anchor="w")
        self.text_entry = ttk.Entry(right, textvariable=self.icon_text, width=14)
        self.text_entry.pack(anchor="w", pady=(2, 4))
        self.icon_text.trace_add("write", lambda *a: self._draw_preview())

        ttk.Radiobutton(right, text="图片文件", value="image",
                        variable=self.icon_type, command=self._update).pack(anchor="w")
        img_row = ttk.Frame(right)
        img_row.pack(anchor="w", pady=(2, 0))
        ttk.Button(img_row, text="选择图片…", command=self._choose_image).pack(side="left")
        ttk.Button(img_row, text="清除", width=6,
                   command=self._clear_image).pack(side="left", padx=4)
        self.img_label = ttk.Label(right, text="", foreground="#888")
        self.img_label.pack(anchor="w", pady=(2, 0))

        row3 = ttk.Frame(body)
        row3.pack(fill="x", pady=(10, 0))
        ttk.Label(row3, text="主题颜色", width=9).pack(side="left")
        self.color_btn = tk.Button(row3, text="  ", bg=self.color, width=6,
                                   relief="groove", command=self._choose_color)
        self.color_btn.pack(side="left")
        self.color_hex = ttk.Label(row3, text=self.color, foreground="#666")
        self.color_hex.pack(side="left", padx=8)

        btns = ttk.Frame(body)
        btns.pack(fill="x", pady=(16, 0))
        ttk.Button(btns, text="确定", command=self._ok).pack(side="right")
        ttk.Button(btns, text="取消", command=self._cancel).pack(side="right", padx=6)

        self.bind("<Return>", lambda e: self._ok())
        self.bind("<Escape>", lambda e: self._cancel())
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self._update()

        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = master.winfo_rootx() + (master.winfo_width() - w) // 2
        y = master.winfo_rooty() + (master.winfo_height() - h) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def _update(self):
        self.text_entry.configure(
            state="normal" if self.icon_type.get() == "text" else "disabled")
        self._draw_preview()

    def _choose_image(self):
        path = filedialog.askopenfilename(
            title="选择头像图片",
            filetypes=[("图片", "*.png *.gif"), ("所有文件", "*.*")])
        if not path:
            return
        self.icon_path.set(path)
        self.icon_type.set("image")
        name = os.path.basename(path)
        self.img_label.config(text=name if len(name) <= 22 else name[:20] + "…")
        self._update()

    def _clear_image(self):
        self.icon_path.set("")
        self.img_label.config(text="")
        self._draw_preview()

    def _choose_color(self):
        _rgb, hexv = colorchooser.askcolor(color=self.color, title="选择分类颜色")
        if hexv:
            self.color = hexv
            self.color_btn.configure(bg=hexv)
            self.color_hex.config(text=hexv)
            self._draw_preview()

    def _draw_preview(self):
        c = self.preview
        c.delete("all")
        size = self.AVATAR_SIZE
        self._preview_img = None
        if self.icon_type.get() == "image" and self.icon_path.get() \
                and os.path.isfile(self.icon_path.get()):
            try:
                img = tk.PhotoImage(file=self.icon_path.get())
                w, h = img.width(), img.height()
                factor = max(1, -(-max(w, h) // size))
                if factor > 1:
                    img = img.subsample(factor, factor)
                self._preview_img = img
                c.create_image(size // 2, size // 2, image=img, anchor="center")
                return
            except Exception:
                pass
        text = self.icon_text.get().strip() or (self.name_var.get().strip() or "?")[:1]
        c.create_oval(0, 0, size, size, fill=self.color, outline="")
        c.create_text(size // 2, size // 2 + 1, text=text, fill="white",
                      font=(FONT, int(size * 0.42), BOLD))

    def _ok(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "请填写分类名称", parent=self)
            return
        self.result = {
            "name": name,
            "icon": self.icon_text.get().strip(),
            "icon_type": self.icon_type.get(),
            "icon_path": self.icon_path.get().strip(),
            "color": self.color,
        }
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

    def _cancel(self):
        self.result = None
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()


# ==========================================================================
#  分类 - 标签关联（超链接）对话框
# ==========================================================================
