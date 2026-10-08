# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：TagBoxGridDialog。

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
class _Borrowed:
    """★★ 借「会变的东西」的代理（★ 每次读回主程序现取）。

    ★★★ `__call__` 不能少（错题本 #160）：**函数也会被借**，
      少了它 `T("…")` 直接 TypeError，而且**会被上层 except 吞掉**。
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


_MISS = object()   # 哨兵：区分「取不到」和「取到 None」
_NEED = ['BOLD', 'FONT', 'UI_FONT_SIZE', 'note_swallowed', 'save_ui_setting', 'messagebox']
_SIBLINGS = ['AutoNameRulesDialog', 'CategoryDialog', 'CategoryHiddenTagsDialog', 'CategoryItem', 'CategorySidebar', 'CategoryTagLinkDialog', 'PreviewPane', 'RemoveFileTagsDialog', 'ScanProgressDialog', 'ShortcutDialog', 'SimpleInputDialog', 'TagBoxGridDialog', 'TagBoxPicker', 'TagPickerDialog', 'UIScaleDialog']
_APP = None
BOLD = None
FONT = None
UI_FONT_SIZE = None
note_swallowed = None
save_ui_setting = None
messagebox = None


def _set_app(app):
    """主程序启动时调一下：把「自己」交进来，顺便把要借的名字填上。"""
    global _APP
    _APP = app
    _fill()
    _link_siblings()


def _fill():
    """从主程序身上把需要的名字取过来，填进本模块的同名变量。"""
    if _APP is None:
        return
    g = globals()
    for _n in _NEED:
        try:
            # ★★★ 用哨兵 + 代理（错题本 #168）
            # ★★★ 无条件装上代理（错题本 #168 v3）：
            #   当时**没有这个值**（主程序还没定义到那一行）也照样装 ——
            #   代理是**读的时候**才回主程序取，所以什么时候定义都不影响。
            #   ★ 这就是"代理"和"快照"的根本区别：
            #     快照必须"当场有"，代理只要"用的时候有"。
            g[_n] = _Borrowed(_n)
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

class TagBoxGridDialog(tk.Toplevel):
    """★★ v26（2026-10-01 重做）：标签盒「分格」设置 —— **只管数量**。

    用户反馈（第一次的版本不好用）：
      「标签盒分格能不能只设置数量，具体有哪些标签要被放进对应的格子
        我希望能直接通过在拖动的方式放入」

    所以这一版砍掉了原来那个「左边标签池 / 右边格子列表」的复杂界面，
    只留两件事：
      1. **选方向**：横着分（左右几格）/ 竖着分（上下几层）；
      2. **定几格**：点 ＋ / － 或直接填数字，想几格就几格（不设上限）。
    点「✅ 应用」之后回到标签盒，**把标签直接拖进想放的格子**就行了。

    标签怎么归格（在标签盒里做，不做在这个窗口里）：
      · 单拖：把标签拖到另一个格子里松手 → 它就归那一格；
      · 多选拖：先框选/Ctrl 多选，拖其中一个 → 这一批全归那一格；
      · 从格子里拖出去（拖到窗口外）→ 从格子里拿出来。
    """

    def __init__(self, master, box):
        super().__init__(master)
        self.box = box
        self.store = box.store
        self.app = box.app

        self.title("标签盒分格设置")
        # ★ v26 修正（用户反馈「窗口不够大，底部有内容被遮盖了，
        #   每次打开要把窗口拉大」）：
        #   初始尺寸 520x400 太小 —— 里面的内容（三个标题段 +
        #   预览图 + 两行说明 + 底部三颗按钮）加起来差不多要 435 像素，
        #   400 根本放不下，底部按钮就被挤到了窗口下边缘之外。
        #   现在调到 560x560（多给 100 多像素余量），
        #   minsize 从 340 提到 480 —— 就算窗口被拉到最小，
        #   也能把底部三颗按钮塞进去。
        self.geometry("560x560")
        self.minsize(460, 480)
        self.transient(master)

        cur = box._read_layout()
        ids = box.box_ids()
        if cur:
            self.dir_var = tk.StringVar(value=cur["dir"])
            # ★★ v26 修正（用户反馈「有幽灵标签问题」）：
            #   分格配置里可能还留着一些**已经不在盒子里**的标签 ——
            #   结果一打开这个窗口就看到「第 1 格（5 个标签）」，
            #   而盒子本体是空的（显示和实际严重不符）。
            #
            #   这里做一次对齐：
            #     · 配置里不在盒子里的 → 丢掉（这就是"幽灵"）
            #     · 盒子里有、没归格的 → 兜底塞最后一格
            #   然后把对齐后的结果**写回配置** ——
            #   以后打开就不会再看到幽灵了。
            _id_set = set(int(t) for t in ids)
            self.cells = [list(c) for c in cur["cells"]]
            for _c in self.cells:
                _c[:] = [t for t in _c if t in _id_set]
            _placed = set()
            for _c in self.cells:
                _placed.update(_c)
            _extra = [t for t in ids if t not in _placed]
            if _extra:
                self.cells[-1] = list(self.cells[-1]) + _extra
            # 回写干净的配置（如果确实变了）
            try:
                _old = cur.get("cells") or []
                _need = (len(_old) != len(self.cells))
                if not _need:
                    for _a, _b in zip(_old, self.cells):
                        if list(_a) != list(_b):
                            _need = True
                            break
                if _need:
                    save_ui_setting(
                        "tag_box_layout",
                        {"dir": cur["dir"],
                         "cells": [list(c) for c in self.cells]})
            except Exception as _e:
                try:
                    note_swallowed("标签盒分格：回写对齐后的配置失败", _e)
                except Exception:
                    pass
        else:
            self.dir_var = tk.StringVar(value="h")
            n = 3 if len(ids) >= 3 else 1
            self.cells = [[] for _ in range(n)]
            for i, t in enumerate(ids):
                self.cells[i % n].append(t)
        self.all_ids = list(ids)

        body = ttk.Frame(self, padding=14)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text="① 怎么分", font=(FONT, UI_FONT_SIZE, BOLD)).pack(anchor="w")
        row = ttk.Frame(body)
        row.pack(fill="x", pady=(4, 10))
        ttk.Radiobutton(row, text="↔ 横着分（左右几格）",
                        variable=self.dir_var, value="h",
                        command=self._render).pack(side="left", padx=(0, 14))
        ttk.Radiobutton(row, text="↕ 竖着分（上下几层）",
                        variable=self.dir_var, value="v",
                        command=self._render).pack(side="left")

        ttk.Label(body, text="② 分几格", font=(FONT, UI_FONT_SIZE, BOLD)).pack(anchor="w")
        row2 = ttk.Frame(body)
        row2.pack(fill="x", pady=(4, 10))
        ttk.Button(row2, text="－", width=3,
                   command=self._dec).pack(side="left")
        self.n_lbl = ttk.Label(row2, text="3", font=(FONT, UI_FONT_SIZE, BOLD),
                               foreground="#16a085")
        self.n_lbl.pack(side="left", padx=12)
        ttk.Button(row2, text="＋", width=3,
                   command=self._inc).pack(side="left")
        ttk.Label(row2, text="  格（想几格就几格，不设上限）",
                  foreground="#666").pack(side="left", padx=(10, 0))

        # ★★ v26 修正（用户反馈：「分格显示窗口不够大，底部有内容被遮盖了，
        #   每次打开要把窗口拉大」）：
        #
        #   原因：**Tk 的 pack 规则是「先 pack 的先占位置」** ——
        #   空间不够时，**最后 pack 的那一批控件先被挤出可视区**。
        #   原来这三颗按钮是**最后**才 pack 的，于是窗口一不够高，
        #   它们就被挤到了窗口下边缘之外（你看到的「被遮盖」）。
        #
        #   修法：**底部按钮改成最先 pack、并且用 side="bottom" 钉底。**
        #   这样无论窗口拉多小，它们都永远贴在窗口最下边、看得见、
        #   点得着；上面那些内容自己在上方想办法挤。
        #   说明文字也改成 side="bottom"（排在按钮上面一行），
        #   视觉上和原来一样，但不会再被挤掉。
        foot = ttk.Frame(body)
        foot.pack(side="bottom", fill="x", pady=(10, 0))
        ttk.Button(foot, text="✅ 应用", width=12,
                   command=self._apply).pack(side="right")
        ttk.Button(foot, text="取消", width=8,
                   command=self.destroy).pack(side="right", padx=6)
        ttk.Button(foot, text="↩ 取消分格（恢复自动排列）", width=26,
                   command=self._clear_layout).pack(side="left")

        ttk.Label(
            body,
            text="点「✅ 应用」之后回到标签盒：把标签直接拖进想放的格子就行。\n"
                 "（框选 / Ctrl 多选后拖，可以一次放一批；拖出格子就是拿出来）",
            foreground="#555", justify="left"
        ).pack(side="bottom", anchor="w", pady=(4, 0))

        # ---- ③ 预览（放在最后 pack，用它吃掉中间剩余的空间） ----
        #   ★ 说明：这里之所以放最后，是因为它用 expand=True ——
        #     expand 只会在「所有非 expand 控件都排完之后」才分配剩余空间，
        #     所以它自动是「剩余中间那一块」，不会挤掉底部的按钮。
        ttk.Label(body, text="③ 长这样",
                  font=(FONT, UI_FONT_SIZE, BOLD)).pack(anchor="w")
        self.preview = tk.Canvas(body, height=110, bg="white",
                                 highlightthickness=1,
                                 highlightbackground="#ccc")
        self.preview.pack(fill="both", expand=True, pady=(4, 10))

        self.bind("<Escape>", lambda e: self.destroy())
        self._render()

    # ---------- 格数 ----------
    def _inc(self):
        self.cells.append([])
        self._render()

    def _dec(self):
        if len(self.cells) <= 1:
            return
        last = self.cells.pop()
        # 把最后一格的标签并回倒数第二格 —— 免得标签凭空消失
        self.cells[-1] = list(self.cells[-1]) + list(last)
        self._render()

    def _render(self):
        try:
            self.n_lbl.config(text=str(len(self.cells)))
        except Exception:
            pass
        c = self.preview
        try:
            c.delete("all")
            W = max(c.winfo_width(), 240)
            H = max(c.winfo_height(), 90)
        except Exception:
            return
        n = max(1, len(self.cells))
        GAP = 6
        if self.dir_var.get() == "h":
            cw = max(24, int((W - GAP * (n + 1)) / n))
            for i in range(n):
                x0 = GAP + i * (cw + GAP)
                c.create_rectangle(x0, GAP, x0 + cw, H - GAP,
                                   fill="#eaf2fd", outline="#8ab4f8",
                                   dash=(3, 2))
                c.create_text(x0 + cw / 2, H / 2 - 8,
                              text="第 %d 格" % (i + 1), fill="#1a73e8",
                              font=(FONT, UI_FONT_SIZE))
                c.create_text(x0 + cw / 2, H / 2 + 8,
                              text="%d 个" % len(self.cells[i]),
                              fill="#666", font=(FONT, UI_FONT_SIZE))
        else:
            ch = max(16, int((H - GAP * (n + 1)) / n))
            for i in range(n):
                y0 = GAP + i * (ch + GAP)
                c.create_rectangle(GAP, y0, W - GAP, y0 + ch,
                                   fill="#eaf2fd", outline="#8ab4f8",
                                   dash=(3, 2))
                c.create_text(W / 2, y0 + ch / 2,
                              text="第 %d 格（%d 个标签）"
                                   % (i + 1, len(self.cells[i])),
                              fill="#1a73e8", font=(FONT, UI_FONT_SIZE))

    # ---------- 应用 ----------
    def _apply(self):
        # 没归格的标签兜底塞最后一格，保证「盒子里的一个都不少」
        used = set()
        for cell in self.cells:
            used.update(cell)
        for t in self.all_ids:
            if t not in used:
                self.cells[-1].append(t)
        layout = {"dir": self.dir_var.get(),
                  "cells": [list(c) for c in self.cells]}
        self.box._write_layout(layout)
        try:
            self.box._redraw()
        except Exception:
            pass
        try:
            self.app.set_status("标签盒已分成 %d 格（%s）—— 现在可以把标签拖进格子"
                                % (len(self.cells),
                                   "横着" if layout["dir"] == "h" else "竖着"))
        except Exception:
            pass
        self.destroy()

    def _clear_layout(self):
        if not messagebox.askyesno("分格", "取消分格，恢复成原来的自动排列？",
                                   parent=self):
            return
        try:
            save_ui_setting("tag_box_layout", None)
        except Exception:
            pass
        try:
            self.box._redraw()
            self.app.set_status("标签盒已恢复自动排列")
        except Exception:
            pass
        self.destroy()



