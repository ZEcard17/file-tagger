# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：ScanProgressDialog。

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

    # ★★★ 补全「代理协议」（错题本 #171）——
    #   ★ 之前只实现了常用几个，结果 `open(_USAGE_PATH)` 炸了：
    #     `TypeError: ... where __fspath__ returns a str, not '_Borrowed'`
    #   ★★ 判据：**代理会被当成什么用，你猜不到** ——
    #     宁可多实现几个（多余的方法不会被调用，不占开销）。
    def __fspath__(self):
        return os.fspath(self._v())

    def __bytes__(self):
        return bytes(self._v())

    def __format__(self, spec):
        return format(self._v(), spec)

    def __abs__(self):
        return abs(self._v())

    def __neg__(self):
        return -self._v()

    def __pos__(self):
        return +self._v()

    def __invert__(self):
        return ~self._v()

    def __round__(self, n=None):
        return round(self._v()) if n is None else round(self._v(), n)

    def __sub__(self, o):
        return self._v() - o

    def __rsub__(self, o):
        return o - self._v()

    def __truediv__(self, o):
        return self._v() / o

    def __floordiv__(self, o):
        return self._v() // o

    def __mod__(self, o):
        return self._v() % o

    def __pow__(self, o):
        return self._v() ** o

    def __rmul__(self, o):
        return o * self._v()

    def __and__(self, o):
        return self._v() & o

    def __or__(self, o):
        return self._v() | o

    def __xor__(self, o):
        return self._v() ^ o

    def __lshift__(self, o):
        return self._v() << o

    def __rshift__(self, o):
        return self._v() >> o

    def __enter__(self):
        return self._v().__enter__()

    def __exit__(self, *a):
        return self._v().__exit__(*a)

    def __next__(self):
        return next(self._v())

    def __copy__(self):
        import copy as _c
        return _c.copy(self._v())

    def __deepcopy__(self, memo):
        import copy as _c
        return _c.deepcopy(self._v(), memo)



_MISS = object()   # 哨兵：区分「取不到」和「取到 None」
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

class ScanProgressDialog(tk.Toplevel):
    """扫描进度的独立窗口，可以最小化，主界面不会被锁住。"""
    def __init__(self, master, store, scopes, on_finish=None):
        super().__init__(master)
        self.on_finish = on_finish
        self.title("正在扫描")
        self.geometry("560x230")
        self.minsize(480, 210)
        self.store = store
        self.scopes = [s.strip() for s in (scopes or []) if s.strip()]
        self.result = None    # (total_files, changed_files)

        self._cancel_flag = False
        self._finished = False
        self._queue = queue.Queue()
        self._walk_done = False
        self._all_paths = []
        self._total = 0
        self._processed = 0

        body = ttk.Frame(self, padding=14)
        body.pack(fill="both", expand=True)

        self.stage_lbl = ttk.Label(body, text="正在枚举文件…",
                                   font=(FONT, UI_FONT_SIZE, BOLD))
        self.stage_lbl.pack(anchor="w", pady=(0, 4))

        self.detail_lbl = ttk.Label(body, text="", foreground="#666",
                                    wraplength=520, justify="left")
        self.detail_lbl.pack(anchor="w", pady=(0, 8))

        self.pb = ttk.Progressbar(body, mode="indeterminate", length=520)
        self.pb.pack(fill="x", pady=(0, 6))
        self.pb.start(12)

        self.count_lbl = ttk.Label(body, text="", foreground="#888")
        self.count_lbl.pack(anchor="w", pady=(0, 8))

        btn_row = ttk.Frame(body)
        btn_row.pack(fill="x")
        self.cancel_btn = ttk.Button(btn_row, text="取消",
                                     command=self._on_cancel)
        self.cancel_btn.pack(side="right")
        ttk.Button(btn_row, text="最小化",
                   command=self._minimize).pack(side="right", padx=6)

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = master.winfo_rootx() + (master.winfo_width() - w) // 2
        y = master.winfo_rooty() + (master.winfo_height() - h) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        self.transient(master)

        # 启动工作线程（★ v23：枚举走索引、打标签也在后台线程里做）
        self._worker = threading.Thread(
            target=self._work_worker, daemon=True)
        self._worker.start()
        self.after(60, self._poll)

        # ★ 不阻塞主界面：不再 wait_window

    # ---------------- 工作线程：先枚举（索引优先），再打标签 ----------------
    def _work_worker(self):
        try:
            all_paths = []
            n_index = 0
            n_live = 0
            for scope in self.scopes:
                if self._cancel_flag:
                    break
                found = []
                try:
                    found = list(self.store.files_under_scope(scope)
                                 .get("paths") or [])
                except Exception as exc:
                    self._queue.put(("info", f"读本地索引失败：{exc}"))
                    found = []
                if found:
                    n_index += len(found)
                    self._queue.put(
                        ("info", f"索引命中：{scope} → {len(found)} 个文件"))
                else:
                    self._queue.put(
                        ("info", f"索引里没有 {scope}，改为实时遍历磁盘"
                                 f"（网盘会很慢）…"))
                    found = self._walk_live(scope)
                    n_live += len(found)
                    self._queue.put(
                        ("info", f"实时遍历完成：{scope} → {len(found)} 个文件"))
                all_paths.extend(found)
                self._queue.put(("found", (len(all_paths), str(scope))))
            if self._cancel_flag:
                self._queue.put(("cancelled", None))
                return
            self._total = len(all_paths)
            self._all_paths = all_paths
            self._queue.put(("tag_start", (self._total, n_index, n_live)))
            self._tag_all()
        except Exception as exc:
            self._queue.put(("error", str(exc)))

    def _walk_live(self, scope):
        """索引/记录里都没有时才用的兜底：实时遍历磁盘（网盘很慢）"""
        out = []
        try:
            if not os.path.isdir(scope):
                return out
            for root, _dirs, files in os.walk(scope):
                if self._cancel_flag:
                    break
                for fn in files:
                    out.append(os.path.join(root, fn))
                    if len(out) % 500 == 0:
                        self._queue.put(("found", (len(out), root)))
        except Exception as exc:
            self._queue.put(("info", f"遍历失败：{scope} - {exc}"))
        return out

    def _tag_all(self):
        """在后台线程里分批打标签（数据库操作完全不占主线程）"""
        total = len(self._all_paths or [])
        step = 200
        changed_all = 0
        for i in range(0, total, step):
            if self._cancel_flag:
                self._queue.put(("cancelled", None))
                return
            chunk = self._all_paths[i:i + step]
            try:
                with self.store.bulk():
                    changed_all += self.store.sync_auto_tags_for_paths(chunk)
            except Exception as exc:
                self._queue.put(("info", f"第 {i + 1} 个起的批次失败：{exc}"))
            try:
                cur = os.path.basename(chunk[-1]) if chunk else ""
            except Exception:
                cur = ""
            self._queue.put(("tag_progress",
                             (min(i + step, total), total, cur, changed_all)))
        self._queue.put(("tag_done", (total, changed_all)))

    # ---------------- 主线程：轮询消息 ----------------
    def _poll(self):
        try:
            while True:
                kind, payload = self._queue.get_nowait()
                self._handle(kind, payload)
                if self._finished:
                    return
        except queue.Empty:
            pass
        if not self._finished:
            self.after(60, self._poll)

    def _handle(self, kind, payload):
        if kind == "info":
            try:
                self.detail_lbl.config(text=str(payload)[:170])
            except Exception:
                pass
            try:
                app = self.master
                if hasattr(app, "log_output"):
                    app.log_output(str(payload))
            except Exception:
                pass
        elif kind == "found":
            n, scope = payload
            self.count_lbl.config(
                text=f"已找到 {n} 个文件…  {str(scope)[:60]}")
        elif kind == "tag_start":
            total, n_index, n_live = payload
            try:
                self.pb.stop()
            except Exception:
                pass
            if total == 0:
                self._finish(0, 0)
                return
            self.pb.config(mode="determinate",
                           maximum=max(1, total), value=0)
            self.stage_lbl.config(text="正在打标签…")
            self.detail_lbl.config(
                text=f"索引 {n_index} 个 / 实时遍历 {n_live} 个    "
                     + "，".join(self.scopes)[:120])
            self.count_lbl.config(text=f"0 / {total}")
            try:
                app = self.master
                if hasattr(app, "log_output"):
                    app.log_output(
                        f"扫描打标签：共 {total} 个文件"
                        f"（索引 {n_index} 个 / 实时遍历 {n_live} 个）")
            except Exception:
                pass
        elif kind == "tag_progress":
            done, total, cur, changed = payload
            self._processed = done
            try:
                self.pb.config(value=done)
            except Exception:
                pass
            if len(cur) > 42:
                cur = cur[:40] + "…"
            self.count_lbl.config(text=f"{done} / {total}    {cur}")
            if done % 400 < 1 or done >= total:
                try:
                    app = self.master
                    if hasattr(app, "log_progress"):
                        app.log_progress(
                            f"扫描进度：{done} / {total}"
                            f"（标签有变化 {changed} 个）    {cur}")
                except Exception:
                    pass
        elif kind == "tag_done":
            total, changed = payload
            try:
                app = self.master
                if hasattr(app, "log_output"):
                    app.log_output(
                        f"扫描打标签完成：{total} 个文件，"
                        f"{changed} 个文件的标签有变化")
            except Exception:
                pass
            self._finish(total, changed)
        elif kind == "error":
            self._finished = True
            try:
                self.pb.stop()
            except Exception:
                pass
            cb = self.on_finish
            try:
                self.destroy()
            except Exception:
                pass
            try:
                messagebox.showerror("扫描出错", payload, parent=None)
            except Exception:
                pass
            if cb:
                try:
                    cb((0, 0))
                except Exception:
                    pass
        elif kind == "cancelled":
            self._finished = True
            try:
                self.pb.stop()
            except Exception:
                pass
            self.result = (0, 0)
            cb = self.on_finish
            try:
                self.destroy()
            except Exception:
                pass
            if cb:
                try:
                    cb((0, 0))
                except Exception:
                    pass

    def _finish(self, total, processed):
        self._finished = True
        try:
            self.pb.stop()
        except Exception:
            pass
        self.result = (total, processed)
        cb = self.on_finish
        try:
            self.destroy()
        except Exception:
            pass
        if cb:
            try:
                cb(self.result)
            except Exception:
                pass

    # ---------------- 交互 ----------------
    def _on_cancel(self):
        if self._cancel_flag:
            return
        self._cancel_flag = True
        try:
            self.stage_lbl.config(text="正在取消…")
        except Exception:
            pass

    def _minimize(self):
        try:
            self.iconify()
        except Exception:
            pass


