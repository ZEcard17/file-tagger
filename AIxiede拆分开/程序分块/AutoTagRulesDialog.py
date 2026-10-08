# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：AutoTagRulesDialog。

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
   · import 要写 `from AutoTagRulesDialog import …`（**不带包路径**）
   · `_set_app` 要**取别名**（`as _fk_…`）—— 模块名和类名同名
   · 借名字清单**用 symtable + dir() 定**，别用正则猜
   · 代理类**必须实现 `__call__`**（函数也会被借）
   · ★ 兜底 except 会吃掉错误 → **必须专门测"用的哪一份"**
"""
import datetime
import threading
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, colorchooser

# ---------- 要向主程序借的名字 ----------
_MUTABLE = ['BOLD', 'FONT', 'UI_FONT_SIZE_SMALL']
_NEED = ['AutoNameRulesDialog', 'AutoRuleEditDialog', 'BOLD', 'DEFAULT_IDLE_MINUTES', 'FONT', 'IDLE_MAX_MINUTES', 'IDLE_MIN_MINUTES', 'ScanProgressDialog', 'T', 'TagPickerDialog', 'UI_FONT_SIZE_SMALL', '_scope_lines', '_tree_row_height', 'check_scope_for_edit', 'confirm_scopes_for_scan', 'datetime', 'load_idle_settings', 'save_idle_settings', 'theme_get', 'threading']
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
                g[_n] = _Borrowed(_n) if _n in _MUTABLE else _v
        except Exception:
            pass


class AutoTagRulesDialog(tk.Toplevel):
    def __init__(self, master, store, app=None):
        super().__init__(master)
        self.title("自动标签规则")
        # ★★★ 2026-10-08 修「界面显示不全」（用户报，待清算 #9）★★★
        #   ★ 实测真因（量出来的）：
        #       窗口内容**请求宽度 = 1496**，而窗口只给了 **980** →
        #       **右边 516 像素被切掉**（用户看到的就是"显示不全"）。
        #   ★ 谁把宽度撑到 1496 的：**下面那个长长的说明文字** ——
        #       它是一整行没换行的长句，**又没给 `wraplength`** →
        #       Tk 按"这一行有多宽"去算请求宽度 → 1496。
        #   ★ 修法（两手都要）：
        #     ① 那个说明文字加 `wraplength`（按窗口宽度换行，见下）
        #     ② 窗口尺寸改成**"按内容请求、但夹在合理范围内"** ——
        #        不再写死 980，而是 `max(内容想要的, 最小可用宽)` 再夹上限。
        #   ★ 为什么不用简单的 `_dlg_geom(1496, ...)`：那个数字是"这台机器、
        #     这个字号"量出来的，换台机器就不对了 —— **不能写死量出来的值**。
        self.store = store
        self.app = app
        self._rule_map = {}
        self._tag_id_by_name = {}
        self._add_box_on = False

        body = ttk.Frame(self, padding=14)
        body.pack(fill="both", expand=True)

        # ★ 说明文字：加 `wraplength`，让它**跟着窗口宽度换行**，
        #   而不是把窗口撑宽。
        #   值取 760：这是"正常看着舒服"的正文宽度（约 60~70 个汉字），
        #   实际显示时 Tk 会按这个宽度折行。
        self._desc_lbl = ttk.Label(
            body,
            text=T("给符合条件的文件自动打标签。\n"
                    "「作用范围」可填多个文件夹（每行一个），留空 = 全局；"
                    "填了 = 该目录及其所有子目录。\n"
                    "「匹配方式」选“全部文件”时，作用范围内所有文件都打这个标签。"),
            foreground=theme_get("fg_dim"), justify="left",
            wraplength=760)
        self._desc_lbl.pack(anchor="w", pady=(0, 8))

        # ---------- 折叠开关 ----------
        toggle_row = ttk.Frame(body)
        toggle_row.pack(fill="x", pady=(0, 4))
        self._toggle_btn = ttk.Button(
            toggle_row, text=T("➕ 新建规则（点击展开）"),
            command=self._toggle_add_box)
        self._toggle_btn.pack(side="left")

        # ---------- 新增规则区（默认不 pack） ----------
        self._add_box = ttk.LabelFrame(body, text=T("新增规则"), padding=10)
        self._build_add_box(self._add_box)

        # ---------- 规则列表（先 pack，永远显示） ----------
        self._list_box = ttk.LabelFrame(
            body,
            text=T("已有规则（双击一行 = 编辑；选中后可用下面按钮扫描）"),
            padding=6)
        self._list_box.pack(fill="both", expand=True)

        cols = ("tag", "scope", "type", "pattern", "case", "enabled")
        self.tree = ttk.Treeview(self._list_box, columns=cols,
                                 show="headings", height=10)
        # ★★ 2026-10-07 补：这棵树没给 style → 系统默认行高(约20)装不下字
        #   → 字被上下切掉（用户报「字体比行高长」）。按字体算行高。
        try:
            _st_AutoRules = ttk.Style()
            _st_AutoRules.configure("AutoRules.Treeview",
                background=theme_get("card_bg"),
                foreground=theme_get("fg"),
                fieldbackground=theme_get("card_bg"),
                rowheight=_tree_row_height(),
                font=(FONT, UI_FONT_SIZE_SMALL))
            _st_AutoRules.configure("AutoRules.Treeview.Heading",
                font=(FONT, UI_FONT_SIZE_SMALL, BOLD))
            self.tree.configure(style="AutoRules.Treeview")
        except Exception:
            pass
        self.tree.heading("tag", text=T("标签"))
        self.tree.heading("scope", text=T("作用范围"))
        self.tree.heading("type", text=T("匹配方式"))
        self.tree.heading("pattern", text=T("匹配内容"))
        self.tree.heading("case", text=T("大小写"))
        self.tree.heading("enabled", text=T("启用"))
        self.tree.column("tag", width=110, anchor="w")
        self.tree.column("scope", width=320, anchor="w")
        self.tree.column("type", width=90, anchor="center")
        self.tree.column("pattern", width=180, anchor="w")
        self.tree.column("case", width=60, anchor="center")
        self.tree.column("enabled", width=50, anchor="center")

        sb = ttk.Scrollbar(self._list_box, orient="vertical",
                           command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.tag_configure("off", foreground=theme_get("fg_dim"))
        self.tree.bind("<Double-1>", lambda e: self._edit_selected())

        # ★ v25：闲时自动跑（鼠标 / 键盘空闲够久，后台悄悄跑一遍）
        idle_row = ttk.Frame(body)
        idle_row.pack(fill="x", pady=(8, 0))
        self._idle_cfg = load_idle_settings()
        self.idle_var = tk.BooleanVar(value=self._idle_cfg["rules_enabled"])
        ttk.Checkbutton(
            idle_row,
            text=T("☁ 闲时自动跑（扫描全部范围 + 应用文件名规则）"),
            variable=self.idle_var,
            command=self._save_idle_cfg).pack(side="left")
        ttk.Label(idle_row, text=T("鼠标 / 键盘空闲")).pack(
            side="left", padx=(10, 2))
        self.idle_min_var = tk.StringVar(
            value=str(self._idle_cfg["rules_minutes"]))
        _sp = ttk.Spinbox(idle_row, from_=IDLE_MIN_MINUTES,
                          to=IDLE_MAX_MINUTES, width=5,
                          textvariable=self.idle_min_var,
                          command=self._save_idle_cfg)
        _sp.pack(side="left")
        _sp.bind("<Return>", lambda e: self._save_idle_cfg())
        _sp.bind("<FocusOut>", lambda e: self._save_idle_cfg())
        ttk.Label(idle_row, text=T("分钟后运行（你一动鼠标它就停）")).pack(
            side="left", padx=(2, 0))
        self._idle_hint_lbl = ttk.Label(idle_row, text="",
                                       foreground=theme_get("fg_dim"))
        self._idle_hint_lbl.pack(side="left", padx=(10, 0))
        self._refresh_idle_hint()

        # ---------- 底部按钮 ----------
        #
        # ★★★ 2026-10-08 **修「界面显示不全」的真凶**（待清算 #9）★★★
        #   ★ 实测真因（把每个控件的请求宽度逐个量出来的）：
        #     这一排按钮原来**全挤在一行**（8 个按钮 + 2 个分隔条），
        #     而且最后那个「关闭」用的是 `side="right"` ——
        #     **Tk 会把"左侧那一串"和"右侧那个"摊开排**，
        #     于是这一行的**请求宽度 = 1468** →
        #     把整个窗口撑到 **1496**（用户屏幕小一点就直接被切）。
        #   ★ 修法：**排成两行**（按用途分组），每行都短。
        #     ① 第一行：对规则本身的操作（编辑 / 启用停用 / 删除）
        #     ② 第二行：扫描 / 刷新 / 文件名规则 … + **关闭**放最右
        #   ★ 为什么不干脆让它自动折行：Tk 的 `pack` **不会自动折行**，
        #     要做就得换成 grid + 手动计算 —— 对"一排按钮"来说不值得。
        #     **按用途分两行**本来也更好看、更好找。
        btns = ttk.Frame(body)
        btns.pack(fill="x", pady=(10, 0))

        # ---- 第一行：管"这条规则" ----
        row_rule = ttk.Frame(btns)
        row_rule.pack(fill="x", pady=(0, 4))
        ttk.Button(row_rule, text=T("编辑选中…"),
                   command=self._edit_selected).pack(side="left")
        ttk.Button(row_rule, text=T("启用 / 停用"),
                   command=self._toggle_selected).pack(side="left", padx=4)
        ttk.Button(row_rule, text=T("删除选中"),
                   command=self._delete_selected).pack(side="left", padx=4)
        ttk.Label(row_rule, text=T("（选中上面一行再用这些）"),
                  foreground=theme_get("fg_dim")).pack(side="left", padx=(10, 0))

        # ---- 第二行：扫描 / 刷新 / 文件名规则 / 关闭 ----
        row_run = ttk.Frame(btns)
        row_run.pack(fill="x")
        ttk.Button(row_run, text=T("▶ 扫描选中范围"),
                   command=self._scan_selected).pack(side="left")
        ttk.Button(row_run, text=T("▶▶ 扫描全部范围"),
                   command=self._scan_all).pack(side="left", padx=4)
        ttk.Button(row_run, text=T("刷新列表"),
                   command=self._reload).pack(side="left", padx=4)
        ttk.Separator(row_run, orient="vertical").pack(
            side="left", fill="y", padx=8)
        ttk.Button(row_run, text=T("📝 文件名规则…"),
                   command=self._open_name_rules).pack(side="left", padx=4)
        ttk.Button(row_run, text=T("▶▶ 应用文件名规则"),
                   command=self._apply_name_rules).pack(side="left", padx=4)

        ttk.Button(row_run, text=T("关闭"),
                   command=self.destroy).pack(side="right")

        # ★ 最后再挂上 rule_type 的联动
        self.rule_type_var.trace_add(
            "write", lambda *a: self._on_rule_type_changed())
        self._on_rule_type_changed()

        self._reload()

        # ★ 位置计算
        #
        # ★★★ 2026-10-08 修「界面显示不全」（待清算 #9）★★★
        #   ★ 原来这里写的是 `w, h = 980, 680` ——
        #     而**上面 `__init__` 开头已经用 `_dlg_geom(980, 680)` 算过一次**，
        #     这里**又用写死的 980 覆盖回去**（等于前面那次白算了）。
        #   ★ 更关键的是：980 是**拍脑袋定的**，而实测"内容真正需要
        #     多少宽度"要看字号/缩放/文字长短 —— **拍的值一定会切内容**。
        #   ★ 现在改成：**按内容算**（`winfo_reqwidth/reqheight`），
        #     再夹在"合理范围"里（不小于能用的最小值、不大于屏幕 92%）。
        #     ★ 这样内容变了、字号变了、换台机器了，**都不会再切**。
        #
        # ★★★ 2026-10-08 又修一次（第二次实测才发现）★★★
        #   ★ 第一次改完宽度对了（1496→1137），**但高度还是切了**：
        #       请求高度 **1102**，窗口只给 **720** → 底部两排按钮**看不见**。
        #   ★ 真因：**"新增规则"那个折叠框默认是收起的**，
        #     我量尺寸的时候它还没展开 → `winfo_reqheight()` 只量到了
        #     "收起状态"的高度。用户一展开，内容就超出去了。
        #   ★ 修法（**冗余**：算两遍，取大的那个）：
        #       ① 先按"当前（收起）状态"量一次
        #       ② **把折叠框临时展开**再量一次（`_add_box` 用 `pack` 摆上）
        #       ③ 取两个高度的**较大值** → 这样展开后也不会切
        #       ④ 量完**恢复原来的展开/收起状态**（不能改变用户看到的样子）
        #     ★ 宽度同理：展开后可能更宽。
        self.update_idletasks()
        try:
            # ★ 第一遍：当前状态
            req_w = int(self.winfo_reqwidth())
            req_h = int(self.winfo_reqheight())
            # ★ 第二遍：**临时展开**"新增规则"框再量一次
            _was_open = bool(getattr(self, "_add_box_on", False))
            try:
                if not _was_open:
                    # 直接 pack 上去量（不走 `_toggle_add_box`，
                    #   免得它顺手改了按钮文字/状态）
                    self._add_box.pack(fill="x", pady=(0, 6))
                    self.update_idletasks()
                    req_w = max(req_w, int(self.winfo_reqwidth()))
                    req_h = max(req_h, int(self.winfo_reqheight()))
                    self._add_box.pack_forget()
                    self.update_idletasks()
            except Exception:
                pass
            # 屏幕能放多大（留边）
            sw = int(self.winfo_screenwidth())
            sh = int(self.winfo_screenheight())
            max_w = int(sw * 0.92)
            max_h = int(sh * 0.92)
            # 最小可用（再小就没法用了）
            min_w, min_h = 780, 560
            # ★ 优先满足内容，但夹在 [最小, 屏幕内] 之间
            w = max(min_w, min(req_w, max_w))
            h = max(min_h, min(req_h, max_h))
            x = master.winfo_rootx() + (master.winfo_width() - w) // 2
            y = master.winfo_rooty() + (master.winfo_height() - h) // 3
            # ★ 别让窗口顶到屏幕外（y 可能算成负的）
            x = max(0, min(x, max(0, sw - w - 10)))
            y = max(0, min(y, max(0, sh - h - 40)))
            self.geometry("%dx%d+%d+%d" % (w, h, x, y))
            # ★ 顺手把"最小尺寸"也设成内容需要的样子 ——
            #   否则用户缩小窗口时，内容又被切
            try:
                self.minsize(min_w, min_h)
            except Exception:
                pass
        except Exception:
            pass

        try:
            self.resizable(True, True)
        except Exception:
            pass

    # ---------- 构建"新增规则"框 ----------
    def _build_add_box(self, add_box):
        r1 = ttk.Frame(add_box)
        r1.pack(fill="x", pady=2)
        ttk.Label(r1, text=T("标签："), width=8).pack(side="left")
        self.tag_var = tk.StringVar()
        self.tag_combo = ttk.Combobox(r1, textvariable=self.tag_var, width=20)
        self.tag_combo.pack(side="left")
        ttk.Button(r1, text=T("🔍 选择…"),
                   command=self._pick_tag).pack(side="left", padx=(4, 0))
        ttk.Label(r1, text=T("  匹配方式：")).pack(side="left")
        self.rule_type_var = tk.StringVar(value="text")
        ttk.Radiobutton(r1, text=T("文件名包含"), value="text",
                        variable=self.rule_type_var).pack(side="left", padx=2)
        ttk.Radiobutton(r1, text=T("扩展名"), value="ext",
                        variable=self.rule_type_var).pack(side="left", padx=2)
        ttk.Radiobutton(r1, text=T(T("全部文件")), value="*",
                        variable=self.rule_type_var).pack(side="left", padx=2)

        r_scope = ttk.Frame(add_box)
        r_scope.pack(fill="x", pady=(6, 2))
        ttk.Label(r_scope, text=T("作用范围："), width=8,
                  anchor="n").pack(side="left", anchor="n")
        self.scope_text = tk.Text(r_scope, height=3, wrap="none", width=48)
        self.scope_text.pack(side="left", fill="x", expand=True)
        btn_col = ttk.Frame(r_scope)
        btn_col.pack(side="left", padx=(4, 0), fill="y")
        ttk.Button(btn_col, text=T("浏览…"),
                   command=self._browse_scope).pack(fill="x", pady=1)
        ttk.Button(btn_col, text=T("✔ 检查"),
                   command=self._check_scope_now).pack(fill="x", pady=1)
        ttk.Button(btn_col, text=T("清空"),
                   command=self._clear_scope).pack(fill="x", pady=1)

        r2 = ttk.Frame(add_box)
        r2.pack(fill="x", pady=2)
        self._pattern_lbl = ttk.Label(r2, text=T("匹配内容："), width=8,
                                      anchor="n")
        self._pattern_lbl.pack(side="left", anchor="n")
        self.pattern_text = tk.Text(r2, height=3, wrap="none", width=48)
        self.pattern_text.pack(side="left", fill="x", expand=True)
        pbtn_col = ttk.Frame(r2)
        pbtn_col.pack(side="left", padx=(4, 0), fill="y")
        ttk.Button(pbtn_col, text=T("➕ 加一行"),
                   command=self._add_pattern_line).pack(fill="x", pady=1)
        ttk.Button(pbtn_col, text=T("清空"),
                   command=lambda: self.pattern_text.delete("1.0", "end")
                   ).pack(fill="x", pady=1)
        ttk.Label(add_box,
                  text="（每行一个；扩展名举例：pdf、docx；"
                       "文件名包含举例：报表、月报）",
                  foreground=theme_get("fg_dim")).pack(anchor="w", padx=(52, 0))

        r3 = ttk.Frame(add_box)
        r3.pack(fill="x", pady=2)
        ttk.Label(r3, text=T("作用字段：")).pack(side="left")
        self.target_var = tk.StringVar(value="name")
        ttk.Radiobutton(r3, text=T("文件名"), value="name",
                        variable=self.target_var).pack(side="left", padx=2)
        ttk.Radiobutton(r3, text=T("完整路径"), value="path",
                        variable=self.target_var).pack(side="left", padx=2)
        self.case_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(r3, text=T("区分大小写"),
                        variable=self.case_var).pack(side="left", padx=10)
        ttk.Button(r3, text=T("＋ 添加规则"),
                   command=self._add_rule).pack(side="right")

    def _toggle_add_box(self):
        if self._add_box_on:
            self._add_box.pack_forget()
            self._add_box_on = False
            self._toggle_btn.config(text=T("➕ 新建规则（点击展开）"))
        else:
            self._add_box.pack(fill="x", pady=(0, 10),
                               before=self._list_box)
            self._add_box_on = True
            self._toggle_btn.config(text=T("➖ 收起新建规则区"))

    # ---------------- ★ v25：闲时设置 ----------------
    def _save_idle_cfg(self):
        try:
            minutes = int(self.idle_min_var.get())
        except Exception:
            minutes = DEFAULT_IDLE_MINUTES
        minutes = max(IDLE_MIN_MINUTES, min(IDLE_MAX_MINUTES, minutes))
        try:
            self.idle_min_var.set(str(minutes))
        except Exception:
            pass
        try:
            save_idle_settings(rules_enabled=bool(self.idle_var.get()),
                               rules_minutes=minutes)
        except Exception:
            pass
        self._refresh_idle_hint()
        try:
            if self.app is not None:
                self.app._refresh_idle_state()
        except Exception:
            pass

    def _refresh_idle_hint(self):
        try:
            cfg = load_idle_settings()
            last = cfg.get("rules_last") or 0
            if last:
                txt = ("上次闲时跑：" + datetime.fromtimestamp(last)
                       .strftime("%m-%d %H:%M"))
            else:
                txt = T("还没闲时跑过")
            self._idle_hint_lbl.config(text=txt)
        except Exception:
            pass

    def _on_rule_type_changed(self):
        try:
            if self.rule_type_var.get() == "*":
                self._pattern_lbl.config(text=T("（忽略）"))
                try:
                    self.pattern_text.delete("1.0", "end")
                except Exception:
                    pass
            else:
                self._pattern_lbl.config(text=T("匹配内容："))
        except Exception:
            pass

    def _add_pattern_line(self):
        try:
            self.pattern_text.insert("end", "\n")
            self.pattern_text.see("end")
            self.pattern_text.focus_set()
        except Exception:
            pass

    def _get_pattern(self):
        try:
            raw = self.pattern_text.get("1.0", "end")
        except Exception:
            return ""
        lines = [l.strip() for l in raw.split("\n") if l.strip()]
        return ",".join(lines)

    def _pick_tag(self):
        try:
            tags = self.store.all_tags()
        except Exception:
            tags = []
        dlg = TagPickerDialog(self, tags, current=self.tag_var.get())
        if dlg.result:
            self.tag_var.set(dlg.result)

    def _browse_scope(self):
        d = filedialog.askdirectory(
            title=T("选择作用范围（文件夹，含所有子目录）"),
            parent=self)
        if d:
            try:
                cur = self._get_scope()
                if d in cur.split("\n"):
                    return
                self.scope_text.insert("end", d + "\n")
            except Exception:
                pass

    def _clear_scope(self):
        try:
            self.scope_text.delete("1.0", "end")
        except Exception:
            pass

    def _set_scope_text(self, scope_path):
        """★ v23：把修正后的作用范围写回输入框"""
        try:
            self.scope_text.delete("1.0", "end")
            for line in str(scope_path or "").split("\n"):
                s = line.strip()
                if s:
                    self.scope_text.insert("end", s + "\n")
        except Exception:
            pass

    def _check_scope_now(self):
        """★ v23：检查作用范围写法（写错会让扫描把旧标签清掉）"""
        scope = self._get_scope()
        if not scope:
            messagebox.showinfo(
                "检查范围",
                "还没有填作用范围（留空 = 全局，对所有文件生效）。",
                parent=self)
            return
        report = []
        bad = 0
        for s in _scope_lines(scope):
            n = self.store.scope_known_file_count(s)
            if not n:
                bad += 1
            report.append(f"  {s}  →  已知文件 {n} 个")
        if not bad:
            messagebox.showinfo(
                "检查范围", "都能对上 ✅\n\n" + "\n".join(report), parent=self)
            return
        ok, fixed = check_scope_for_edit(self, self.store, scope, "保存")
        if ok and fixed != scope:
            self._set_scope_text(fixed)
        messagebox.showinfo(
            "检查范围", "检查结果：\n" + "\n".join(report), parent=self)

    def _get_scope(self):
        try:
            raw = self.scope_text.get("1.0", "end")
        except Exception:
            return ""
        lines = [l.strip() for l in raw.split("\n") if l.strip()]
        return "\n".join(lines)

    # ---------- 列表 ----------
    def _reload(self):
        tags = self.store.all_tags()
        tag_names = [t[1] for t in tags]
        self._tag_id_by_name = {t[1]: t[0] for t in tags}
        try:
            self.tag_combo["values"] = tag_names
        except Exception:
            pass
        if tag_names and not self.tag_var.get():
            try:
                self.tag_var.set(tag_names[0])
            except Exception:
                pass

        for item in self.tree.get_children():
            self.tree.delete(item)
        self._rule_map = {}

        for r in self.store.all_auto_rules():
            rtype = r["rule_type"]
            if rtype == "text":
                type_label = "文件名"
            elif rtype == "ext":
                type_label = "扩展名"
            elif rtype == "*":
                type_label = T("全部文件")
            else:
                type_label = rtype
            scope = (r.get("scope_path") or "").strip()
            if scope:
                lines = [l.strip() for l in scope.split("\n") if l.strip()]
                scope_disp = " ; ".join(lines)
                if len(scope_disp) > 120:
                    scope_disp = scope_disp[:118] + "…"
            else:
                scope_disp = "（全局）"
            cs = "区分" if r["case_sensitive"] else "忽略"
            enabled = "✓" if r["enabled"] else "✗"
            iid = self.tree.insert(
                "", "end",
                values=(r["name"], scope_disp, type_label,
                        r["pattern"], cs, enabled),
                tags=() if r["enabled"] else ("off",))
            self._rule_map[iid] = r["id"]

        # ★ v25：一条规则都没有时，给个占位行（不然列表区一片空白）
        if not self._rule_map:
            self.tree.insert(
                "", "end",
                values=("（还没有规则）", "点上面「➕ 新建规则（点击展开）」加一条",
                        "", "", "", ""))

        # ★ v25：顺便刷一下「上次闲时跑」的时间
        if hasattr(self, "_idle_hint_lbl"):
            self._refresh_idle_hint()

    # ---------- 添加 ----------
    def _add_rule(self):
        tag_name = (self.tag_var.get() or "").strip()
        if not tag_name:
            messagebox.showwarning("提示", T("请先输入一个标签名"), parent=self)
            return
        tag_id = self._tag_id_by_name.get(tag_name)
        if tag_id is None:
            try:
                self.store.create_tag(tag_name)
                tag_id = self.store.tag_id_by_name(tag_name)
            except Exception as exc:
                messagebox.showerror("错误", str(exc), parent=self)
                return
        rule_type = self.rule_type_var.get()
        pattern = self._get_pattern()
        scope = self._get_scope()
        if rule_type != "*" and not pattern:
            messagebox.showwarning("提示", T("请输入匹配内容"), parent=self)
            return
        if rule_type == "*" and not scope:
            messagebox.showwarning(
                "提示",
                "「全部文件」规则必须至少填一个作用范围（选一个文件夹）",
                parent=self)
            return
        # ★ v23：范围写法检查（写错不但打不上标签，还会清掉旧标签）
        ok, fixed_scope = check_scope_for_edit(self, self.store, scope, "保存")
        if not ok:
            return
        if fixed_scope != scope:
            scope = fixed_scope
            self._set_scope_text(scope)
        try:
            self.store.add_auto_rule(
                tag_id, rule_type, pattern,
                target=self.target_var.get(),
                case_sensitive=bool(self.case_var.get()),
                scope_path=scope,
            )
        except Exception as exc:
            messagebox.showerror("错误", str(exc), parent=self)
            return

        if scope:
            scopes = [l.strip() for l in scope.split("\n") if l.strip()]
            ScanProgressDialog(self, self.store, scopes,
                               on_finish=self._on_scan_finished)

        try:
            self.pattern_text.delete("1.0", "end")
        except Exception:
            pass
        self._clear_scope()
        self._reload()

    # ---------- 选中 / 编辑 / 停用 / 删除 ----------
    def _selected_rule_ids(self):
        return [self._rule_map[iid]
                for iid in self.tree.selection()
                if iid in self._rule_map]

    def _edit_selected(self):
        ids = self._selected_rule_ids()
        if not ids:
            return
        if len(ids) > 1:
            messagebox.showinfo("提示", T("一次只能编辑一条规则"), parent=self)
            return
        rid = ids[0]
        all_rules = {r["id"]: r for r in self.store.all_auto_rules()}
        r = all_rules.get(rid)
        if r is None:
            return
        dlg = AutoRuleEditDialog(self, self.store, r)
        if dlg.saved:
            self._reload()

    def _toggle_selected(self):
        ids = self._selected_rule_ids()
        if not ids:
            return
        rules = {r["id"]: r for r in self.store.all_auto_rules()}
        for rid in ids:
            r = rules.get(rid)
            if r is None:
                continue
            self.store.set_auto_rule_enabled(rid, not bool(r["enabled"]))
        self._reload()

    def _delete_selected(self):
        ids = self._selected_rule_ids()
        if not ids:
            return
        if not messagebox.askyesno(
                "确认", f"确定删除选中的 {len(ids)} 条规则吗？",
                parent=self):
            return
        for rid in ids:
            self.store.delete_auto_rule(rid)
        self._reload()

    def _on_scan_finished(self, result):
        total, processed = result or (0, 0)
        try:
            self._reload()
        except Exception:
            pass
        try:
            messagebox.showinfo(
                "扫描完成",
                f"共扫描 {total} 个文件（含所有子目录），\n"
                f"其中 {processed} 个文件的标签被更新。",
                parent=self)
        except Exception:
            pass

    # ---------- 文件名规则 ----------
    def _open_name_rules(self):
        AutoNameRulesDialog(self, self.store)

    def _apply_name_rules(self):
        n = len(self.store.get_auto_name_rule_tag_ids())
        if n == 0:
            messagebox.showinfo(
                "提示",
                "还没有勾选任何文件名规则标签。\n"
                "请先点「📝 文件名规则…」选择一批标签。",
                parent=self)
            return
        if self.app is not None:
            try:
                self.app._do_apply_name_rules()
            except Exception as exc:
                messagebox.showerror("错误", str(exc), parent=self)
        else:
            def worker():
                try:
                    self.store.resync_all_file_tags_with_name()
                except Exception:
                    pass
            threading.Thread(target=worker, daemon=True).start()

    # ---------- 扫描 ----------
    def _scan_selected(self):
        ids = self._selected_rule_ids()
        if not ids:
            messagebox.showinfo("提示", T("请先选中要扫描的规则"), parent=self)
            return
        all_rules = {r["id"]: r for r in self.store.all_auto_rules()}
        scopes = []
        for rid in ids:
            r = all_rules.get(rid)
            if not r or not r["enabled"]:
                continue
            sp = (r.get("scope_path") or "").strip()
            if not sp:
                continue
            for line in sp.split("\n"):
                s = line.strip()
                if s and s not in scopes:
                    scopes.append(s)
        if not scopes:
            messagebox.showinfo(
                "提示",
                "选中的规则里没有填作用范围，无法扫描。\n"
                "（没有范围的规则只对程序已打开过的文件生效）",
                parent=self)
            return
        # ★ v23：范围里一个文件都没有时先问清楚（写错范围会把旧标签清掉）
        if not confirm_scopes_for_scan(self, self.store, scopes):
            return
        ScanProgressDialog(self, self.store, scopes,
                           on_finish=self._on_scan_finished)

    def _scan_all(self):
        rules = [r for r in self.store.all_auto_rules()
                 if r["enabled"] and (r.get("scope_path") or "").strip()]
        if not rules:
            messagebox.showinfo(
                "提示",
                "当前没有启用且带作用范围的规则。\n"
                "（只有填了“作用范围”的规则才能被批量扫描）",
                parent=self)
            return
        scopes = []
        for r in rules:
            for line in r["scope_path"].split("\n"):
                s = line.strip()
                if s and s not in scopes:
                    scopes.append(s)
        # ★ v23：范围里一个文件都没有时先问清楚
        if not confirm_scopes_for_scan(self, self.store, scopes):
            return
        ScanProgressDialog(self, self.store, scopes,
                           on_finish=self._on_scan_finished)



# ---------- 兜底（★ 它会吃掉错误，所以要专门测"用的哪一份"）----------
def _fallback():
    g = globals()
    for _n in _NEED:
        if g.get(_n) is None:
            g[_n] = _Borrowed(_n)


_fallback()
