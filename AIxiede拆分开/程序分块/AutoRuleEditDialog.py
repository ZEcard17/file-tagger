# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：AutoRuleEditDialog。

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
   · import 要写 `from AutoRuleEditDialog import …`（**不带包路径**）
   · `_set_app` 要**取别名**（`as _fk_…`）—— 模块名和类名同名
   · 借名字清单**用 symtable + dir() 定**，别用正则猜
   · 代理类**必须实现 `__call__`**（函数也会被借）
   · ★ 兜底 except 会吃掉错误 → **必须专门测"用的哪一份"**
"""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, colorchooser

# ---------- 要向主程序借的名字 ----------
_MUTABLE = []
_NEED = ['T', 'TagPickerDialog', '_dlg_geom', '_dlg_size', '_scope_lines', 'check_scope_for_edit', 'theme_get']
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


class AutoRuleEditDialog(tk.Toplevel):
    def __init__(self, master, store, rule):
        super().__init__(master)
        self.title("编辑自动标签规则")
        self.geometry(_dlg_geom(700, 420))
        self.minsize(*_dlg_size(620, 380, minimum=(620, 380)))
        self.store = store
        self.rule = rule
        self.saved = False

        body = ttk.Frame(self, padding=14)
        body.pack(fill="both", expand=True)

        tags = store.all_tags()
        tag_names = [t[1] for t in tags]
        self._tag_id_by_name = {t[1]: t[0] for t in tags}

        r1 = ttk.Frame(body)
        r1.pack(fill="x", pady=3)
        ttk.Label(r1, text=T("标签："), width=8).pack(side="left")
        self.tag_var = tk.StringVar(value=rule.get("name") or "")
        ttk.Combobox(r1, textvariable=self.tag_var,
                     values=tag_names, width=22).pack(side="left")
        ttk.Button(r1, text=T("🔍 选择…"),
                   command=self._pick_tag).pack(side="left", padx=(4, 0))
        ttk.Label(r1, text=T("  匹配方式：")).pack(side="left")
        self.rule_type_var = tk.StringVar(
            value=rule.get("rule_type") or "text")
        ttk.Radiobutton(r1, text=T("文件名包含"), value="text",
                        variable=self.rule_type_var).pack(side="left", padx=2)
        ttk.Radiobutton(r1, text=T("扩展名"), value="ext",
                        variable=self.rule_type_var).pack(side="left", padx=2)
        ttk.Radiobutton(r1, text=T(T("全部文件")), value="*",
                        variable=self.rule_type_var).pack(side="left", padx=2)

        r2 = ttk.Frame(body)
        r2.pack(fill="x", pady=(6, 0))
        ttk.Label(r2, text=T("作用范围："), width=8,
                  anchor="n").pack(side="left", anchor="n")
        self.scope_text = tk.Text(r2, height=4, wrap="none", width=48)
        self.scope_text.pack(side="left", fill="x", expand=True)
        self._fill_scope_text(rule.get("scope_path") or "")
        btn_col = ttk.Frame(r2)
        btn_col.pack(side="left", padx=(4, 0), fill="y")
        ttk.Button(btn_col, text=T("浏览…"),
                   command=self._browse_scope).pack(fill="x", pady=1)
        ttk.Button(btn_col, text=T("✔ 检查"),
                   command=self._check_scope_now).pack(fill="x", pady=1)
        ttk.Button(btn_col, text=T("清空"),
                   command=self._clear_scope).pack(fill="x", pady=1)

        ttk.Label(body, text="（每行一个路径；留空 = 全局；填了路径 = "
                             "该目录及其所有子目录）",
                  foreground=theme_get("fg_dim")).pack(anchor="w", padx=(50, 0))

        r3 = ttk.Frame(body)
        r3.pack(fill="x", pady=3)
        self._pattern_lbl = ttk.Label(r3, text=T("匹配内容："), width=8,
                                      anchor="n")
        self._pattern_lbl.pack(side="left", anchor="n")
        self.pattern_text = tk.Text(r3, height=4, wrap="none", width=48)
        self.pattern_text.pack(side="left", fill="x", expand=True)
        pbtn_col = ttk.Frame(r3)
        pbtn_col.pack(side="left", padx=(4, 0), fill="y")
        ttk.Button(pbtn_col, text=T("➕ 加一行"),
                   command=self._add_pattern_line).pack(fill="x", pady=1)
        ttk.Button(pbtn_col, text=T("清空"),
                   command=lambda: self.pattern_text.delete("1.0", "end")
                   ).pack(fill="x", pady=1)
        # 把已有的逗号分隔内容铺到多行
        try:
            for p in (rule.get("pattern") or "").split(","):
                p = p.strip()
                if p:
                    self.pattern_text.insert("end", p + "\n")
        except Exception:
            pass
        ttk.Label(body,
                  text="（每行一个；扩展名举例：pdf、docx；"
                       "文件名包含举例：报表、月报）",
                  foreground=theme_get("fg_dim")).pack(anchor="w", padx=(50, 0))

        r4 = ttk.Frame(body)
        r4.pack(fill="x", pady=3)
        ttk.Label(r4, text=T("作用字段：")).pack(side="left")
        self.target_var = tk.StringVar(value=rule.get("target") or "name")
        ttk.Radiobutton(r4, text=T("文件名"), value="name",
                        variable=self.target_var).pack(side="left", padx=2)
        ttk.Radiobutton(r4, text=T("完整路径"), value="path",
                        variable=self.target_var).pack(side="left", padx=2)
        self.case_var = tk.BooleanVar(
            value=bool(rule.get("case_sensitive")))
        ttk.Checkbutton(r4, text=T("区分大小写"),
                        variable=self.case_var).pack(side="left", padx=10)

        btns = ttk.Frame(body)
        btns.pack(fill="x", pady=(16, 0))
        ttk.Button(btns, text=T("保存修改"),
                   command=self._save).pack(side="right")
        ttk.Button(btns, text=T("取消"),
                   command=self._cancel).pack(side="right", padx=6)

        self.rule_type_var.trace_add(
            "write", lambda *a: self._on_type_changed())
        self._on_type_changed()

        self.bind("<Escape>", lambda e: self._cancel())
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        self.update_idletasks()
        # ★★★ 2026-10-08 跟 `AutoTagRulesDialog` 一样改成"**按内容算尺寸**"
        #   （待清算 #9：「编辑自动标签规则窗口」也显示不全）★★★
        #   ★ 原来这里只挪了位置（`geometry("+x+y")`），尺寸用的还是
        #     开头写死的 `_dlg_geom(700, 420)` ——
        #     而实测内容真正需要的宽度更大（两个 `tk.Text` 以前是默认 80 字符宽，
        #     已改成 48），高度也会随"作用范围/匹配内容"填多少而变。
        #   ★ 现在：按内容请求算，再夹在 [最小, 屏幕内]。
        try:
            req_w = int(self.winfo_reqwidth())
            req_h = int(self.winfo_reqheight())
            sw = int(self.winfo_screenwidth())
            sh = int(self.winfo_screenheight())
            max_w, max_h = int(sw * 0.92), int(sh * 0.92)
            min_w, min_h = 620, 420
            w = max(min_w, min(req_w, max_w))
            h = max(min_h, min(req_h, max_h))
            x = master.winfo_rootx() + (master.winfo_width() - w) // 2
            y = master.winfo_rooty() + (master.winfo_height() - h) // 3
            x = max(0, min(x, max(0, sw - w - 10)))
            y = max(0, min(y, max(0, sh - h - 40)))
            self.geometry("%dx%d+%d+%d" % (w, h, x, y))
            try:
                self.minsize(min_w, min_h)
            except Exception:
                pass
        except Exception:
            # 兜底：至少把位置摆正（原来的做法）
            try:
                w, h = self.winfo_width(), self.winfo_height()
                x = master.winfo_rootx() + (master.winfo_width() - w) // 2
                y = master.winfo_rooty() + (master.winfo_height() - h) // 3
                self.geometry("+%d+%d" % (max(x, 0), max(y, 0)))
            except Exception:
                pass
        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def _fill_scope_text(self, scope_path):
        try:
            self.scope_text.delete("1.0", "end")
            for line in (scope_path or "").split("\n"):
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
            self._fill_scope_text(fixed)
        messagebox.showinfo(
            "检查范围", "检查结果：\n" + "\n".join(report), parent=self)

    def _get_scope(self):
        try:
            raw = self.scope_text.get("1.0", "end")
        except Exception:
            return ""
        lines = [l.strip() for l in raw.split("\n") if l.strip()]
        return "\n".join(lines)

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

    def _clear_scope(self):
        try:
            self.scope_text.delete("1.0", "end")
        except Exception:
            pass

    def _on_type_changed(self):
        try:
            if self.rule_type_var.get() == "*":
                self._pattern_lbl.config(text=T("（忽略）"))
            else:
                self._pattern_lbl.config(text=T("匹配内容："))
        except Exception:
            pass

    def _browse_scope(self):
        d = filedialog.askdirectory(
            title=T("选择作用范围（文件夹，含所有子目录）"),
            parent=self)
        if d:
            try:
                cur = self._get_scope()
                if d in cur.split("\n"):
                    return
                if cur:
                    self.scope_text.insert("end", d + "\n")
                else:
                    self.scope_text.insert("end", d + "\n")
            except Exception:
                pass

    def _save(self):
        tag_name = (self.tag_var.get() or "").strip()
        if not tag_name:
            messagebox.showwarning("提示", T("标签名不能为空"), parent=self)
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
                "提示", "「全部文件」规则必须至少填一个作用范围",
                parent=self)
            return
        # ★ v23：范围写法检查（写错不但打不上标签，还会清掉旧标签）
        ok, fixed_scope = check_scope_for_edit(self, self.store, scope, "保存")
        if not ok:
            return
        if fixed_scope != scope:
            scope = fixed_scope
            self._fill_scope_text(scope)
        try:
            self.store.update_auto_rule(
                self.rule["id"], tag_id, rule_type, pattern,
                target=self.target_var.get(),
                case_sensitive=bool(self.case_var.get()),
                scope_path=scope)
        except Exception as exc:
            messagebox.showerror("错误", str(exc), parent=self)
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



# ---------- 兜底（★ 它会吃掉错误，所以要专门测"用的哪一份"）----------
def _fallback():
    g = globals()
    for _n in _NEED:
        if g.get(_n) is None:
            g[_n] = _Borrowed(_n)


_fallback()
