# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：ShortcutDialog。

★ 代码**原样搬运**，一个字没改，只是换了个文件放。

★★ 拆文件的规矩（所有分块文件都照这个写）★★
   ① **Python 自带的东西直接 import**（tk、ttk、os、sys…）——不绕弯。
   ② **只有主程序自己造的东西才向主程序借**（FONT、note_swallowed 这类）。
      而且**不在开头 import 主程序**——两边互相 import 会让 Python
      报错、程序打不开。借法是主程序启动时把「自己」交进来（_set_app）。
   ③ 借来的名字做成**模块级变量**，这样下面的代码**一个字都不用改**。
   ④ 借不到就用兜底值，**不能因为主程序改了个名字就整个打不开**。
   ⑤ ★★ **运行时会变的用「代理」**（_Borrowed）—— 每次读都回主程序现取。

★★ 拆出来的坑（错题本 #158~#164，★ 别重演）：
   · import 要写 `from ShortcutDialog import …`（**不带包路径**）
   · `_set_app` 要**取别名**（`as _fk_…`）—— 模块名和类名同名
   · 借名字清单**用 symtable + dir() 定**，别用正则猜
   · 代理类**必须实现 `__call__`**（函数也会被借）
   · ★ 兜底 except 会吃掉错误 → **必须专门测"用的哪一份"**
"""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, colorchooser

# ---------- 要向主程序借的名字 ----------
_MUTABLE = ['BOLD', 'FONT', 'UI_FONT_SIZE', 'UI_FONT_SIZE_SMALL']
_NEED = ['BOLD', 'FONT', 'SHORTCUT_DEFS', 'T', 'UI_FONT_SIZE', 'UI_FONT_SIZE_SMALL', '_alt_down', '_dlg_geom', '_dlg_size', '_tree_row_height', 'load_shortcut_map', 'save_shortcut_map', 'theme_get']
_APP = None


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


def _set_app(app):
    """主程序启动时调一下：把「自己」交进来，顺便把要借的名字填上。"""
    global _APP
    _APP = app
    _fill()


def _fill():
    """从主程序身上把需要的名字取过来，填进本模块的同名变量。"""
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


class ShortcutDialog(tk.Toplevel):
    """★ v25 补丁25：「快捷键管理」窗口 —— 想改哪个键，点一下就行。

    用法（很简单）：
      1) 「💾 保存」= 保存并立刻生效（不用重启程序）
      2) 双击某一行（或者选中后点「⌨ 按下新键…」）= 弹个小窗，直接按键盘
         上你想用的那个键，按完点确定
      3) 或者用右边的下拉框，从「Ctrl+S」这种列表里挑一个
      4) 「恢复默认」= 全部回到出厂设置
    """

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.title("快捷键管理")
        self.geometry(_dlg_geom(880, 600))
        self.minsize(*_dlg_size(760, 480, minimum=(760, 480)))
        self.transient(master)
        self.vars = {}
        self.action_of_item = {}
        self.map = load_shortcut_map()

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(
            body,
            text=T("想改哪个键：① 双击那一行直接按键，或 ② 选中后从右边的下拉框里挑。\n"
                    "留空 = 不用快捷键（比如你不想让 F2 改文件名，就把它清空）。"),
            justify="left", foreground=theme_get("fg_dim")).pack(anchor="w", pady=(0, 6))

        mid = ttk.Frame(body)
        mid.pack(fill="both", expand=True)
        cols = ("action", "key")
        self.tree = ttk.Treeview(mid, columns=cols, show="headings", height=16)
        # ★★ 2026-10-07 补：这棵树没给 style → 系统默认行高(约20)装不下字
        #   → 字被上下切掉（用户报「字体比行高长」）。按字体算行高。
        try:
            _st_Shortcut = ttk.Style()
            _st_Shortcut.configure("Shortcut.Treeview",
                background=theme_get("card_bg"),
                foreground=theme_get("fg"),
                fieldbackground=theme_get("card_bg"),
                rowheight=_tree_row_height(),
                font=(FONT, UI_FONT_SIZE_SMALL))
            _st_Shortcut.configure("Shortcut.Treeview.Heading",
                font=(FONT, UI_FONT_SIZE_SMALL, BOLD))
            self.tree.configure(style="Shortcut.Treeview")
        except Exception:
            pass
        self.tree.heading("action", text=T("功能"))
        self.tree.heading("key", text=T("当前按键"))
        self.tree.column("action", width=420, anchor="w")
        self.tree.column("key", width=200, anchor="center")
        sb = ttk.Scrollbar(mid, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self._capture())
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._on_pick())

        pick = ttk.Frame(body)
        pick.pack(fill="x", pady=(8, 0))
        ttk.Label(pick, text=T("选中项的按键：")).pack(side="left")
        self.key_var = tk.StringVar(value="")
        self.key_box = ttk.Combobox(pick, textvariable=self.key_var,
                                    values=SHORTCUT_KEY_CHOICES, width=18)
        self.key_box.pack(side="left", padx=6)
        self.key_box.bind("<<ComboboxSelected>>", lambda e: self._apply_pick())
        ttk.Button(pick, text=T("⌨ 按下新键…"),
                   command=self._capture).pack(side="left", padx=6)
        ttk.Button(pick, text=T("清空这个键"),
                   command=self._clear_one).pack(side="left", padx=(0, 6))
        self.warn_lbl = ttk.Label(pick, text="", foreground=theme_get("warn"))
        self.warn_lbl.pack(side="left", padx=8)

        btns = ttk.Frame(body)
        btns.pack(fill="x", pady=(10, 0))
        ttk.Button(btns, text=T("💾 保存并生效"),
                   command=self._save).pack(side="left")
        ttk.Button(btns, text=T("恢复默认"),
                   command=self._reset).pack(side="left", padx=6)
        ttk.Button(btns, text=T("关闭"),
                   command=self.destroy).pack(side="right")
        self.bind("<Escape>", lambda e: self.destroy())
        self._reload_rows()

    # ---------- 列表 ----------
    def _reload_rows(self):
        self.tree.delete(*self.tree.get_children())
        self.action_of_item = {}
        for name, label, default in SHORTCUT_DEFS:
            cur = self.map.get(name, "")
            mark = "（默认）" if cur == default else (
                "（已改）" if cur else "（不用）")
            iid = self.tree.insert("", "end",
                                   values=(label, (cur or "—") + " " + mark))
            self.action_of_item[iid] = name
        kids = self.tree.get_children()
        if kids:
            self.tree.selection_set(kids[0])

    def _selected_action(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.action_of_item.get(sel[0])

    def _on_pick(self):
        name = self._selected_action()
        if not name:
            return
        self.key_var.set(self.map.get(name, ""))

    def _apply_pick(self):
        name = self._selected_action()
        if not name:
            return
        self.map[name] = self.key_var.get().strip()
        self._check_conflict()
        self._reload_rows()

    def _clear_one(self):
        name = self._selected_action()
        if not name:
            return
        self.map[name] = ""
        self._reload_rows()

    # ---------- 按键捕获 ----------
    def _capture(self):
        name = self._selected_action()
        if not name:
            return
        label = dict((d[0], d[1]) for d in SHORTCUT_DEFS).get(name, name)
        cap = tk.Toplevel(self)
        # ★★ 2026-10-07：Toplevel 是**原生窗口**，底色不跟 ttk 主题走 ——
        #   不设 bg 就用系统默认（白/浅灰），那就是"小窗口夜间还是白的"的根因。
        try:
            cap.configure(bg=theme_get("win_bg"))
            # ★ 登记一下，切主题时由 _retheme_custom_parts 统一刷新
            _reg = getattr(self, "_theme_windows", None)
            if _reg is None:
                _reg = self._theme_windows = []
            _reg.append(cap)
        except Exception:
            pass
        cap.title("按下新键")
        cap.transient(self)
        cap.resizable(False, False)
        ttk.Label(cap, text="给「%s」指定按键。\n\n请直接按键盘上你想用的那个键"
                            "（可以带 Ctrl / Alt / Shift）。" % label,
                  justify="left").pack(padx=16, pady=(14, 6), anchor="w")
        show = tk.StringVar(value="（还没按）")
        ttk.Label(cap, textvariable=show, foreground=theme_get("ok"),
                  font=(FONT, UI_FONT_SIZE, BOLD)).pack(padx=16, pady=6)
        bb = ttk.Frame(cap)
        bb.pack(fill="x", padx=16, pady=(6, 14))
        got = {"seq": None, "key": None}
        order = ["Control", "Alt", "Shift"]

        def _pretty(seq):
            s = seq.strip("<>")
            parts = [p for p in s.split("-") if p]
            mods, main = [], []
            for p in parts:
                if p in order:
                    mods.append(p)
                else:
                    main.append(p)
            mods.sort(key=lambda m: order.index(m))
            name_map = {"Control": "Ctrl", "Escape": "Esc",
                        "Prior": "PageUp", "Next": "PageDown",
                        "Left": "Left", "Right": "Right", "Up": "Up",
                        "Down": "Down"}
            mm = [name_map.get(m, m) for m in mods]
            mn = "".join(name_map.get(x, x) for x in main)
            return "+".join(mm + [mn]) if mn else None

        def on_key(e):
            seq = e.keysym
            if seq in ("??",):
                return "break"
            # 单独的修饰键：继续等真正的主键
            if seq in ("Control_L", "Control_R", "Alt_L", "Alt_R",
                       "Shift_L", "Shift_R", "Win_L", "Win_R",
                       "Super_L", "Super_R", "Caps_Lock", "Num_Lock"):
                show.set("（继续按：Ctrl / Alt 之后还要按一个字母或功能键）")
                return "break"
            parts = []
            if e.state & 0x0004:
                parts.append("Control")
            # ★ 2026-10-03 修正：别用 0x0008 判 Alt —— 那一位在这台机器上
            #   永远是亮的（实测「什么都不按」也是 0x8），会让录下来的
            #   快捷键**凭空多出一个 Alt**（按 Ctrl+A 录成 Ctrl+Alt+A）。
            #   真正按 Alt 时多出来的是 0x20000。详见 _alt_down()。
            if _alt_down(e.state):
                parts.append("Alt")
            if e.state & 0x0001:
                parts.append("Shift")
            pretty_main = seq
            if isinstance(seq, str) and len(seq) == 1 and seq.isalpha():
                pretty_main = seq.upper()       # 统一记成大写
            # 修饰键要按 Ctrl→Alt→Shift 排；tkinter 的事件状态位其实顺序相反
            parts = [p for p in ("Control", "Alt", "Shift") if p in parts]
            pretty = "+".join(["Ctrl" if p == "Control" else p
                               for p in parts] + [pretty_main])
            got["key"] = pretty if pretty != "Escape" else None
            show.set("你按的是：" + pretty + "（按 Esc 取消，按回车确定）")
            return "break"

        def ok(_e=None):
            if got["key"] is None:
                return
            self.map[name] = got["key"]
            self._check_conflict()
            cap.destroy()
            self._reload_rows()

        def cancel(_e=None):
            cap.destroy()

        cap.bind("<Key>", on_key)
        cap.bind("<Return>", ok)
        cap.bind("<Escape>", cancel)
        ttk.Button(bb, text=T("确定"), command=ok).pack(side="right")
        ttk.Button(bb, text=T("取消"), command=cancel).pack(side="right", padx=6)
        try:
            cap.grab_set()
            cap.focus_force()
        except Exception:
            pass

    # ---------- 冲突检查 / 保存 ----------
    def _check_conflict(self):
        seen = {}
        dups = []
        for name, label, _d in SHORTCUT_DEFS:
            k = self.map.get(name, "")
            if not k:
                continue
            if k in seen:
                dups.append("%s ↔ %s 都绑了 %s"
                            % (seen[k][1], label, k))
            else:
                seen[k] = (name, label)
        if dups:
            self.warn_lbl.config(text=T("⚠ 有重复：") + "；".join(dups[:2]))
        else:
            self.warn_lbl.config(text="")

    def _save(self):
        save_shortcut_map(self.map)
        try:
            self.app._apply_shortcuts()
            self.app.set_status(T("快捷键已保存并生效"))
            self.app.log_output("快捷键已更新：" + "，".join(
                "%s=%s" % (dict((d[0], d[1]) for d in SHORTCUT_DEFS).get(k, k),
                           v or "（不用）")
                for k, v in self.map.items() if v))
        except Exception as exc:
            messagebox.showwarning("快捷键", "保存了，但应用时出错：%s" % exc,
                                   parent=self)
        self._reload_rows()

    def _reset(self):
        self.map = {name: default for name, _l, default in SHORTCUT_DEFS}
        self._reload_rows()
        self.warn_lbl.config(text=T("已改成出厂设置（还要点「💾 保存并生效」才生效）"))




# ---------- 兜底（★ 它会吃掉错误，所以要专门测"用的哪一份"）----------
def _fallback():
    g = globals()
    for _n in _NEED:
        if g.get(_n) is None:
            g[_n] = _Borrowed(_n)


_fallback()
