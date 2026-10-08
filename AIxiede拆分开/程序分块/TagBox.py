# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：TagBox。

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
   · import 要写 `from TagBox import …`（**不带包路径**）
   · `_set_app` 要**取别名**（`as _fk_…`）—— 模块名和类名同名
   · 借名字清单**用 symtable + dir() 定**，别用正则猜
   · 代理类**必须实现 `__call__`**（函数也会被借）
   · ★ 兜底 except 会吃掉错误 → **必须专门测"用的哪一份"**
"""
import queue
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, colorchooser

# ---------- 要向主程序借的名字 ----------
_MUTABLE = ['BOLD', 'FONT', 'UI_FONT_SIZE', 'UI_FONT_SIZE_SMALL']
_NEED = ['BOLD', 'DND_FILES', 'FONT', 'HAS_DND', 'T', 'TagBoxGridDialog', 'TagBoxPicker', 'UI_FONT_SIZE', 'UI_FONT_SIZE_SMALL', '_dlg_size', 'load_ui_setting', 'note_swallowed', 'save_ui_setting', 'theme_get']
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


class TagBox(tk.Toplevel):
    """★ 标签盒：独立置顶小窗口，可以拖到任何地方、随意缩放。

    怎么用：
      · 点标签 = 给选中的文件打标签
      · 从盒子里把标签拖到文件列表上 = 给那些文件打标签
      · 右键标签：移出盒子 / 固定 / 取消固定
      · 把文件从资源管理器拖到盒子上 = 用盒子里的标签给它们打标签
    """

    def __init__(self, master, app, store):
        super().__init__(master)
        self.app = app
        self.store = store
        self._drag = None
        self._geo_job = None

        self.title("标签盒")
        try:
            geo = load_ui_setting("tagbox_geometry", "") or "880x120+120+120"
        except Exception:
            geo = "880x120+120+120"
        try:
            self.geometry(geo)
        except Exception:
            pass
        self.minsize(*_dlg_size(320, 100, minimum=(320, 100)))
        self.resizable(True, True)
        self._topmost = bool(load_ui_setting("tagbox_topmost", True))
        try:
            self.attributes("-topmost", self._topmost)
        except Exception:
            pass
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Configure>", self._on_configure)

        # ★★ v26（2026-10-01）：**顶部这一行按钮以前会被挤爆。**
        #   实测：窗口 900 像素，而这一行 4 个按钮 + 说明文字要 1061 像素 ——
        #   Tk 不报错，只是把最后面的按钮**压成 1 像素宽**（也就是完全看不见），
        #   倒数第二个被从 197 压到 141（文字被切掉一截）。
        #   这跟之前主工具栏「位置下拉框变成 1 像素」是同一类毛病。
        #   改法（跟主工具栏学）：
        #     · 全部去掉 width（= 0），让按钮宽度由文字自己决定，不会被压；
        #     · 说明文字缩短，省出空间；
        #     · 用两行放：第一行说明 + 置顶，第二行全是按钮。
        #   这样窗口再窄也只是按钮换行，不会「消失」。
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=6, pady=(6, 2))
        line1 = ttk.Frame(bar)
        line1.pack(fill="x")
        ttk.Label(line1, text=T("标签盒：点标签 / 拖标签到文件上 = 打标签"),
                  foreground=theme_get("fg_dim")).pack(side="left")
        self._top_var = tk.BooleanVar(value=self._topmost)
        ttk.Checkbutton(line1, text=T("置顶"), variable=self._top_var,
                        command=self._toggle_topmost).pack(side="left", padx=8)

        line2 = ttk.Frame(bar)
        line2.pack(fill="x", pady=(3, 0))
        # 按钮一律 width=0（按内容自适应），绝不写死宽度 —— 写死就会被压扁
        ttk.Button(line2, text=T("＋ 从标签库勾选"),
                   command=self._open_picker).pack(side="left")
        ttk.Button(line2, text=T("▦ 分格设置"),
                   command=self._open_grid_setup).pack(side="left", padx=4)
        ttk.Button(line2, text=T("一键打给选中文件"),
                   command=self._apply_to_selection).pack(side="right")
        ttk.Button(line2, text=T("清空盒子"),
                   command=self._clear_box).pack(side="right", padx=4)

        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        self.canvas = tk.Canvas(wrap, highlightthickness=1,
                                highlightbackground=theme_get("line"), bg=theme_get("card_bg"))
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self._font = tkfont.Font(family=FONT, size=UI_FONT_SIZE, weight=BOLD)
        # ★★ v26（2026-10-01）：框选 + 多选。
        #   _sel_ids     —— 当前被选中的标签 id（画蓝边）
        #   _marq        —— 正在拉框时的状态（起点/终点）
        #   _pill_boxes  —— 上一次画完之后每个方块的位置（框选判定用它）
        #   _drag        —— 拖拽状态（支持"一批一起走"）
        self._sel_ids = set()
        self._marq = None
        self._pill_boxes = []
        self._press_info = None
        self._drag_multi = None

        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Button-3>", self._on_right)
        # ★★ v26：键盘也能清空选中（按 Esc），方便
        self.canvas.bind("<Escape>", lambda e: self._clear_selection())
        self.canvas.focus_set()
        self.canvas.bind("<Configure>", lambda e: self._redraw())
        try:
            if HAS_DND:
                self.canvas.drop_target_register(DND_FILES)
                self.canvas.dnd_bind("<<Drop>>", self._on_files_dropped)
        except Exception:
            pass

    # ---------------- 窗口几何 / 置顶 ----------------
    def _on_configure(self, event):
        if event.widget is not self:
            return
        if self._geo_job is not None:
            try:
                self.after_cancel(self._geo_job)
            except Exception:
                pass
        self._geo_job = self.after(500, self._save_geo)

    def _save_geo(self):
        self._geo_job = None
        try:
            save_ui_setting("tagbox_geometry", self.geometry())
        except Exception:
            pass

    def _toggle_topmost(self):
        self._topmost = bool(self._top_var.get())
        try:
            self.attributes("-topmost", self._topmost)
            save_ui_setting("tagbox_topmost", self._topmost)
        except Exception:
            pass

    def _on_close(self):
        try:
            self._save_geo()
            save_ui_setting("tagbox_visible", False)
            self.app.tagbox_visible = False
            self.app._update_tagbox_btn()
        except Exception:
            pass
        self.withdraw()

    # ---------------- 数据 ----------------
    def _fixed_ids(self):
        try:
            return set(self.store.tag_box_ids())
        except Exception:
            return set()

    def _session_ids(self):
        v = load_ui_setting("tag_box_ids", None)
        if not isinstance(v, list):
            return []
        out = []
        for x in v:
            try:
                out.append(int(x))
            except Exception:
                pass
        return out

    def _save_session(self, ids):
        try:
            save_ui_setting("tag_box_ids", [int(i) for i in ids])
        except Exception:
            pass

    def box_ids(self):
        out = []
        for i in list(self._fixed_ids()) + self._session_ids():
            if i not in out:
                out.append(i)
        return out

    # ---------------- ★★ v26（2026-10-01）：横/竖分格 ----------------
    #
    #  用户原话：「想给标签盒增加个横/竖分格的功能，让用户自己选择将哪些
    #  标签放进标签盒的哪些格子里，格子用户可以随意增加，不设上限
    #  （其实可能上限10就满足大部分人的需要了）」。
    #
    #  设计：
    #    · 分格布局存成一个字典：{"dir": "h" 或 "v", "cells": [[id,...], ...]}
    #      - "h" = 横着切（左右几个格子，竖着排）；"v" = 竖着切（上下几格）
    #      - cells 是每个格子里的标签 id 列表，顺序就是你看到的顺序
    #    · 没设置过分格时（cells 为空），走**老样子**：自动换行铺满。
    #      这样老用户完全感觉不到变化。
    #    · 格子数不设上限（你要 10 个也行、要 20 个也行）。
    def _read_layout(self):
        """读出分格配置。没配过就返回 None（= 老样子自动排列）。"""
        v = load_ui_setting("tag_box_layout", None)
        if not isinstance(v, dict):
            return None
        d = v.get("dir")
        cells = v.get("cells")
        if d not in ("h", "v") or not isinstance(cells, list) or not cells:
            return None
        out = []
        for cell in cells:
            lst = []
            for x in (cell or []):
                try:
                    lst.append(int(x))
                except Exception:
                    pass
            out.append(lst)
        return {"dir": d, "cells": out}

    def _write_layout(self, layout):
        try:
            save_ui_setting("tag_box_layout", layout)
        except Exception as _e:
            try:
                note_swallowed(T("保存标签盒分格设置失败"), _e)
            except Exception:
                pass

    def _open_grid_setup(self):
        try:
            TagBoxGridDialog(self, self)
        except Exception as exc:
            messagebox.showerror("标签盒分格", "打不开设置窗口：%s" % exc,
                                 parent=self)

    # ---------------- ★ v25 补丁42：从标签库 / 标签星图「拖标签进来」 ----------------
    #
    #  用户反馈：「现在无法从标签库和标签星图上直接拖拽标签到标签盒」。
    #  查下来：原来只有**反向**那一半是通的（从标签盒拖出去 → 拖到文件上
    #  打标签）；**正向**（从别处拖进盒子）从来没实现过。
    #
    #  为什么不用 tkinterdnd2 做？因为那个库是「跟操作系统要拖放」的，
    #  只能传**文件路径**，传不了「这是哪个标签」。硬要传就得在磁盘上
    #  造临时文件，又脏又容易和杀毒软件打架。
    #
    #  所以用一个更简单也更稳的办法：**标签盒自己盯着鼠标**。
    #  拖动开始时通知盒子「我拖着标签 N 在走」，盒子每 60 毫秒看一眼
    #  鼠标在不在自己身上；在的话就高亮，松手就收进来。
    #  这样不管是从标签库拖、从星图拖、还是以后别的地方拖，都能用。
    def begin_watch_drag(self, tid, name, color=None):
        """别处开始拖标签了 → 让盒子盯着鼠标，准备接收。"""
        try:
            self._watch = {
                "tid": int(tid), "name": name, "color": color,
                "hot": False,
            }
            self._watch_tick()
        except Exception:
            pass

    def end_watch_drag(self, x_root=None, y_root=None):
        """拖动结束了。如果松手的位置在盒子上 → 收进盒子。"""
        w = getattr(self, "_watch", None)
        self._watch = None
        self._watch_hot(False)
        if not w:
            return False
        if x_root is None or y_root is None:
            try:
                x_root, y_root = self.winfo_pointerxy()
            except Exception:
                return False
        if self._point_inside(x_root, y_root):
            try:
                self.add_tag(w["tid"], w["name"])
                self.app.set_status(
                    "已放进标签盒：%s（从标签库/星图拖进来的）" % w["name"])
            except Exception:
                pass
            return True
        return False

    def _point_inside(self, x_root, y_root):
        """这个屏幕坐标是不是落在盒子窗口上。"""
        try:
            if not self.winfo_ismapped():
                return False
            x0 = self.winfo_rootx()
            y0 = self.winfo_rooty()
            x1 = x0 + self.winfo_width()
            y1 = y0 + self.winfo_height()
            return x0 <= x_root <= x1 and y0 <= y_root <= y1
        except Exception:
            return False

    def _watch_tick(self):
        """每 60 毫秒看一眼鼠标在不在盒子上（只在拖动期间跑）。"""
        w = getattr(self, "_watch", None)
        if not w:
            self._watch_hot(False)
            return
        try:
            x, y = self.winfo_pointerxy()
            inside = self._point_inside(x, y)
        except Exception:
            inside = False
        self._watch_hot(inside)
        try:
            self.after(60, self._watch_tick)
        except Exception:
            pass

    def _watch_hot(self, on):
        """鼠标悬在盒子上时，给个明显的高亮边框 —— 让人知道「松手就收进去」。"""
        try:
            if bool(getattr(self, "_watch_hot_now", False)) == bool(on):
                return
            self._watch_hot_now = bool(on)
            if on:
                self.canvas.configure(highlightthickness=3,
                                      highlightbackground="#27ae60")
            else:
                self.canvas.configure(highlightthickness=1,
                                      highlightbackground=theme_get("line"))
        except Exception:
            pass

    def add_tag(self, tid, name=None):
        tid = int(tid)
        ids = self._session_ids()
        if tid not in ids:
            ids.append(tid)
        self._save_session(ids)
        self._redraw()
        try:
            self.app.set_status(T("已放进标签盒：{x}", x=(name or tid)))
        except Exception:
            pass

    def add_tag_fixed(self, tid, name=None):
        tid = int(tid)
        try:
            self.store.tag_box_add(tid)
        except Exception as exc:
            messagebox.showwarning("标签盒", "加不进「固定」：%s" % exc, parent=self)
            return
        self._redraw()
        try:
            self.app.set_status(T("已固定进标签盒：{x}", x=(name or tid)))
        except Exception:
            pass

    def remove_tag(self, tid):
        """★ v26 修正：从盒子里移出一个标签。

        用户反馈：「标签盒里的标签有时候没法右键踢除，右键『从盒子里
        移出去』没用、还在里面」。查出来的原因是**两份名单脱钩**：

          · 名单 A = 真正在盒子里的标签（tag_box 表 + tag_box_ids 设置）
          · 名单 B = 「分格配置」里记的标签（tag_box_layout 设置）

        原来这个方法只改名单 A，**没改名单 B**；而画标签盒时读的
        恰恰是名单 B —— 于是被移出的标签**照旧被画在屏幕上**，
        看起来就是「移不掉」。

        现在：**A、B 一起改**，屏幕上和实际里的就永远一致了。
        """
        tid = int(tid)
        ids = [i for i in self._session_ids() if i != tid]
        self._save_session(ids)
        try:
            self.store.tag_box_remove(tid)
        except Exception:
            pass
        # ★★ 同步从「分格配置」里删掉（否则下次 _redraw 会把它画回来）
        try:
            layout = self._read_layout()
            if layout:
                cells = [list(c) for c in layout["cells"]]
                for cell in cells:
                    while tid in cell:
                        cell.remove(tid)
                self._write_layout({"dir": layout["dir"], "cells": cells})
        except Exception as _e:
            try:
                note_swallowed(T("标签盒：从分格配置里删标签失败"), _e)
            except Exception:
                pass
        self._redraw()

    def _clear_box(self):
        if not self.box_ids():
            return
        if not messagebox.askyesno(
                "清空标签盒",
                "把盒子里的标签都移出去吗？\n（标签本身和文件上的标签都不受影响）",
                parent=self):
            return
        self._save_session([])
        try:
            self.store.tag_box_clear()
        except Exception:
            pass
        self._redraw()

    # ---------------- 画 ----------------
    def _redraw(self):
        """★★ v26（2026-10-01）：重写。现在支持三种画法 ——

        ① 没设过分格 → 老样子：标签从左到右自动换行铺满；
        ② 横格（dir="h"）：盒子左右切成 N 条，每条竖着排标签；
        ③ 竖格（dir="v"）：盒子上下切成 N 层，每层横着排标签。

        另外还负责：
          · 被选中的标签（框选/多选出来的）画一圈**粗蓝边**；
          · 分格的格子画浅灰虚线，一眼能看出分成几格。
        """
        c = self.canvas
        try:
            c.delete("all")
        except Exception:
            return
        f = self._font
        pad_x, pad_y = 14, 7
        h = f.metrics("linespace") + pad_y * 2
        try:
            W = max(c.winfo_width(), 200)
            H = max(c.winfo_height(), 60)
        except Exception:
            W = 400
            H = 120
        self._pill_boxes = []          # ★ 记下每个标签方块的位置，给框选用
        # ★★ v26（2026-10-01）：同时记下**每个格子的范围**，
        #   这样「把标签拖进某个格子」才知道松手的位置落在哪一格。
        self._cell_boxes = []

        ids = self.box_ids()
        if not ids:
            # ★★ v26 修正（用户反馈：「没标签的时候设置分格，看不到格线，
            #   只有加入标签后才有」）：
            #
            #   原因：以前盒子里一个标签都没有时**直接 return 了** ——
            #   后面那段「画格子」的代码根本走不到。于是你看到的就是
            #   「设了 3 格但屏幕上什么都没有」（其实配置已经存进去了）。
            #
            #   现在改成：
            #     ① 顺手把分格配置里残留的幽灵标签清掉（上一个补丁做的）；
            #     ② **如果设过分格，也照样把格子框画出来** ——
            #        空的格子也要看得见，这样「先设格、再往里拖标签」
            #        这个流程才走得通。
            try:
                _lay = self._read_layout()
                if _lay:
                    _has_ghost = False
                    for _c in _lay.get("cells") or []:
                        if _c:
                            _has_ghost = True
                            break
                    if _has_ghost:
                        self._write_layout(
                            {"dir": _lay["dir"],
                             "cells": [[] for _ in _lay["cells"]]})
                    # ---- 画空的格子框（和「有标签」时一样的画法） ----
                    _cells = _lay["cells"]
                    _n = max(1, len(_cells))
                    _GAP = 8
                    if _lay["dir"] == "h":
                        # 横着分：左右几条，每条一格
                        _cw = max(90, int((W - _GAP * (_n + 1)) / _n))
                        for _i in range(_n):
                            _x0 = _GAP + _i * (_cw + _GAP)
                            _x1 = _x0 + _cw
                            _y1 = max(H - _GAP, _GAP + h + 8)
                            c.create_rectangle(_x0, _GAP, _x1, _y1,
                                               outline=theme_get("line"),
                                               dash=(3, 3))
                            c.create_text((_x0 + _x1) // 2,
                                          (_GAP + _y1) // 2,
                                          text="第 %d 格" % (_i + 1),
                                          fill=theme_get("line"),
                                          font=(FONT, UI_FONT_SIZE_SMALL))
                            try:
                                self._cell_boxes.append(
                                    {"i": _i, "x0": _x0, "y0": _GAP,
                                     "x1": _x1, "y1": _y1})
                            except Exception:
                                pass
                    else:
                        # 竖着分：上下几层
                        _ch = max(h + 8, int((H - _GAP * (_n + 1)) / _n))
                        for _i in range(_n):
                            _y0 = _GAP + _i * (_ch + _GAP)
                            _y1 = _y0 + _ch
                            _x1 = max(W - _GAP, _GAP + 60)
                            c.create_rectangle(_GAP, _y0, _x1, _y1,
                                               outline=theme_get("line"),
                                               dash=(3, 3))
                            c.create_text(_x1 // 2, (_y0 + _y1) // 2,
                                          text="第 %d 格" % (_i + 1),
                                          fill=theme_get("line"),
                                          font=(FONT, UI_FONT_SIZE_SMALL))
                            try:
                                self._cell_boxes.append(
                                    {"i": _i, "x0": _GAP, "y0": _y0,
                                     "x1": _x1, "y1": _y1})
                            except Exception:
                                pass
            except Exception as _e:
                try:
                    note_swallowed(T("标签盒：清理幽灵分格标签失败"), _e)
                except Exception:
                    pass
            # ★ 空盒子时的提示：如果分了格，就放到「最下面」那一行，
            #   不去跟格子里的「第 N 格」文字抢位置；
            #   没分格就还是原来那样放顶部。
            try:
                if self._cell_boxes:
                    c.create_text(10, H - 14, anchor="sw",
                                  fill=theme_get("fg_dim"), font=(FONT, UI_FONT_SIZE),
                                  text="（盒子是空的：点上面「＋ 从标签库勾选…」，"
                                       "或者把标签库里的标签拖到想放的格子里）")
                else:
                    c.create_text(10, 14, anchor="nw", fill=theme_get("fg_dim"),
                                  font=(FONT, UI_FONT_SIZE),
                                  text="（盒子是空的：点上面「＋ 从标签库勾选…」，"
                                       "或者把标签库里的标签拖到这里）")
            except Exception:
                pass
            try:
                c.configure(scrollregion=(0, 0, max(W, 200),
                                          max(H, 80) + 12))
            except Exception:
                pass
            return

        layout = self._read_layout()
        if not layout:
            # ---------- ① 老样子：自动换行 ----------
            x, y = 8, 8
            max_bottom = y + h
            for tid in ids:
                row = self._tag_row(tid)
                if not row:
                    continue
                name = row["name"]
                color = row["color"] or "#3498db"
                w = f.measure(name) + pad_x * 2
                if x + w > W - 10 and x > 8:
                    x = 8
                    y += h + 6
                self._draw_pill(c, tid, name, color, x, y, w, h)
                x += w + 6
                max_bottom = max(max_bottom, y + h)
            try:
                c.configure(scrollregion=(0, 0, max(W, 200), max_bottom + 12))
            except Exception:
                pass
            return

        # ---------- ② / ③ 分格 ----------
        # ★★ v26 关键修复（用户反馈「标签有时候没法右键踢除 / 标签盒显示的
        #   标签和文件的标签不符」）：
        #
        #   分格配置（cells）和「真正在盒子里的标签」（ids）是**两份名单**。
        #   原来它们会脱钩：
        #     · 「从盒子里移出去」只改 ids，没改 cells；
        #     · 而这里画标签盒时读的却是 cells。
        #   后果：
        #     · 被移出去的标签照旧被画出来（看起来「踢不掉」）；
        #     · 「一键打给选中文件」读的又是 ids（所以它是正常的）。
        #   这就正好对应你说的两个现象。
        #
        #   修法：画之前先把两份名单**对齐** ——
        #     · cells 里不在 ids 里的  → 丢掉（它已经被移出盒子了）；
        #     · ids 里不在 cells 里的  → 兜底加到最后一格（新加进来的）。
        #   顺便把对齐后的结果**写回分格配置** —— 免得历史脏数据一直
        #   传下去（你之前遇到的那个「显示和文件不符」就是这么来的）。
        _id_set = set(ids)
        cells = [list(c) for c in layout["cells"]]
        for _c in cells:
            _c[:] = [t for t in _c if t in _id_set]
        n = max(1, len(cells))
        placed = set()
        for cell in cells:
            placed.update(cell)
        extra = [t for t in ids if t not in placed]
        if extra:
            cells[-1] = list(cells[-1]) + extra
        # 把对齐后的结果写回配置（这样下次打开 / 切窗口都不会再拿到脏数据）
        try:
            _old_cells = layout.get("cells") or []
            _need_write = False
            if len(_old_cells) != len(cells):
                _need_write = True
            else:
                for _a, _b in zip(_old_cells, cells):
                    if list(_a) != list(_b):
                        _need_write = True
                        break
            if _need_write:
                self._write_layout({"dir": layout["dir"], "cells": cells})
        except Exception as _e:
            try:
                note_swallowed(T("标签盒：回写分格配置失败"), _e)
            except Exception:
                pass

        GAP = 8
        if layout["dir"] == "h":
            # 横着切：每格宽度 = (总宽 - 间隔) / 格数，竖直方向各自排
            cw = max(90, int((W - GAP * (n + 1)) / n))
            max_bottom = H
            for i, cell in enumerate(cells):
                cx0 = GAP + i * (cw + GAP)
                cx1 = cx0 + cw
                # ★ 记下这一格的范围（拖进来时要用）
                try:
                    self._cell_boxes.append({"i": i, "x0": cx0, "y0": GAP,
                                             "x1": cx1,
                                             "y1": max(H - GAP, GAP + h + 8)})
                except Exception:
                    pass
                # 格子边框（浅灰虚线）
                c.create_rectangle(cx0, GAP, cx1, max(H - GAP, GAP + h + 8),
                                   outline=theme_get("line"), dash=(3, 3),
                                   tags=("cell",))
                # ★★ 逐行排：每个标签只画一次
                #   （第一版写成了每行都重新遍历整个格子，
                #     结果 16 个标签画出 1808 个方块 —— 已修）
                queue = list(cell)
                x, y = cx0 + 4, GAP + 4
                while queue:
                    row_used = False
                    rest = []
                    for tid in queue:
                        row = self._tag_row(tid)
                        if not row:
                            continue
                        name = row["name"]
                        color = row["color"] or "#3498db"
                        w = f.measure(name) + pad_x * 2
                        if w > cx1 - cx0 - 6:
                            w = cx1 - cx0 - 6
                        # 这一行放不下了 → 留到下一行
                        if x + w > cx1 - 4:
                            rest.append(tid)
                            continue
                        self._draw_pill(c, tid, name, color, x, y, w, h)
                        x += w + 6
                        row_used = True
                    queue = rest
                    y += h + 4
                    x = cx0 + 4
                    # ★★ v26 修正：**一行都放不下（格子太窄）时，不要 break！**
                    #   用户反馈：「标签盒里的标签有时候没法右键踢除」。
                    #   原因就在这里：以前一 break，这一格剩下的标签
                    #   **既不画、也不进 _pill_boxes** —— 它们看不见、点不到，
                    #   右键就落在空白上，弹出的菜单里没有「移出盒子」。
                    #   现在改成：硬把队首那个标签放上去（宽度缩到格子宽度），
                    #   保证盒子里**每个标签都有位置、都能被点到**。
                    if not row_used and queue:
                        _tid0 = queue[0]
                        _r0 = self._tag_row(_tid0)
                        if _r0:
                            _w0 = max(20, cx1 - cx0 - 6)
                            self._draw_pill(c, _tid0, _r0["name"],
                                            _r0["color"] or "#3498db",
                                            cx0 + 2, y, _w0, h)
                            y += h + 4
                        queue = queue[1:]
                        continue
                max_bottom = max(max_bottom, y)
            try:
                c.configure(scrollregion=(0, 0, W, max_bottom + 12))
            except Exception:
                pass
        else:
            # 竖着切：每格高度 = (总高 - 间隔) / 格数，横向排（不够就换行）
            ch = max(h + 8, int((H - GAP * (n + 1)) / n))
            max_bottom = H
            for i, cell in enumerate(cells):
                cy0 = GAP + i * (ch + GAP)
                cy1 = cy0 + ch
                # ★ 记下这一格的范围（拖进来时要用）
                try:
                    self._cell_boxes.append({"i": i, "x0": GAP, "y0": cy0,
                                             "x1": max(W - GAP, GAP + 60),
                                             "y1": cy1})
                except Exception:
                    pass
                c.create_rectangle(GAP, cy0, max(W - GAP, GAP + 60), cy1,
                                   outline=theme_get("line"), dash=(3, 3),
                                   tags=("cell",))
                x, y = GAP + 4, cy0 + 4
                for tid in cell:
                    row = self._tag_row(tid)
                    if not row:
                        continue
                    name = row["name"]
                    color = row["color"] or "#3498db"
                    w = f.measure(name) + pad_x * 2
                    if x + w > W - GAP - 4:
                        x = GAP + 4
                        y += h + 4
                    # ★★ v26 修正：**格子装不下时不要 break！**
                    #   用户反馈：「标签盒里的标签有时候没法右键踢除」。
                    #   原因就在这里：以前一 break，这一格里**剩下的标签
                    #   既不画、也不进 _pill_boxes** —— 看不见、点不到，
                    #   右键落在空白上，菜单里当然没有「移出盒子」。
                    #   现在改成：**继续画，超出格子也无所谓** ——
                    #   反正画布可以往下滚，至少你能点得到它们。
                    self._draw_pill(c, tid, name, color, x, y, w, h)
                    x += w + 6
                # ★ 记录真实底部（原来固定用 cy1 会漏掉超出格子的部分）
                max_bottom = max(max_bottom, cy1, y + h + 4)
            try:
                c.configure(scrollregion=(0, 0, W, max_bottom + 12))
            except Exception:
                pass

    def _tag_row(self, tid):
        try:
            return self.store.tag_by_id(tid)
        except Exception:
            return None

    def _draw_pill(self, c, tid, name, color, x, y, w, h):
        """画一个标签方块。被选中的话加一圈蓝边。"""
        sel = tid in getattr(self, "_sel_ids", set())
        c.create_rectangle(
            x, y, x + w, y + h, fill=color,
            outline=("#1a73e8" if sel else ""),
            width=(3 if sel else 1),
            tags=("pill", "t%d" % tid))
        c.create_text(x + w / 2, y + h / 2, text=name, fill="white",
                      font=self._font, tags=("pill", "t%d" % tid))
        try:
            self._pill_boxes.append({"tid": tid, "x0": x, "y0": y,
                                     "x1": x + w, "y1": y + h})
        except Exception:
            pass

    def _hit(self, event):
        """鼠标底下是哪个标签方块。"""
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        # ★ 先用我们自己记的方块位置（列表/分格模式都准）
        for b in reversed(list(getattr(self, "_pill_boxes", []) or [])):
            if b["x0"] <= cx <= b["x1"] and b["y0"] <= cy <= b["y1"]:
                row = self._tag_row(b["tid"])
                if row:
                    return (b["tid"], row["name"], row["color"])
        # 兜底：还是用画布自己的命中测试
        try:
            items = self.canvas.find_overlapping(cx - 1, cy - 1, cx + 1, cy + 1)
        except Exception:
            items = ()
        for it in reversed(list(items)):
            for t in self.canvas.gettags(it):
                if t.startswith("t") and t[1:].isdigit():
                    tid = int(t[1:])
                    row = self._tag_row(tid)
                    if row:
                        return (tid, row["name"], row["color"])
        return None

    # ---------------- ★★ v26：框选 / 多选 ----------------
    def _items_in_rect(self, x0, y0, x1, y1):
        """框住的标签 id 集合。"""
        hit = set()
        for b in (getattr(self, "_pill_boxes", []) or []):
            if (b["x1"] > x0 and b["x0"] < x1
                    and b["y1"] > y0 and b["y0"] < y1):
                hit.add(b["tid"])
        return hit

    def _draw_marquee_rect(self):
        m = getattr(self, "_marq", None)
        if not m or not m.get("started"):
            return
        x0, y0 = min(m["x0"], m["x1"]), min(m["y0"], m["y1"])
        x1, y1 = max(m["x0"], m["x1"]), max(m["y0"], m["y1"])
        try:
            if m.get("rect") is None:
                m["rect"] = self.canvas.create_rectangle(
                    x0, y0, x1, y1, outline="#1a73e8", width=1, dash=(4, 3),
                    tags=("marq",))
            else:
                self.canvas.coords(m["rect"], x0, y0, x1, y1)
                self.canvas.tag_raise(m["rect"])
        except Exception:
            m["rect"] = None

    def _clear_selection(self):
        if self._sel_ids:
            self._sel_ids = set()
            self._redraw()
            try:
                self.app.set_status(T("标签盒：已取消选中"))
            except Exception:
                pass

    def _marquee_apply(self):
        m = getattr(self, "_marq", None)
        if not m:
            return
        x0, y0 = min(m["x0"], m["x1"]), min(m["y0"], m["y1"])
        x1, y1 = max(m["x0"], m["x1"]), max(m["y0"], m["y1"])
        hit = self._items_in_rect(x0, y0, x1, y1)
        if m.get("ctrl"):
            self._sel_ids |= hit
        else:
            self._sel_ids = set(hit)
        # 重画（会清掉虚线框），所以先记好再补回来
        m["rect"] = None
        self._redraw()
        self._draw_marquee_rect()

    # ---------------- 拖出去（支持多选一起拖） ----------------
    def _on_press(self, event):
        self.canvas.focus_set()
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        hit = self._hit(event)
        ctrl = bool(event.state & 0x0004)
        if hit:
            tid = hit[0]
            # ★★ v26：点一个已经在"多选"里的标签 → 整批一起拖；
            #   点一个没选的标签（没按 Ctrl）→ 只选它、拖它。
            if ctrl:
                if tid in self._sel_ids:
                    self._sel_ids.discard(tid)
                else:
                    self._sel_ids.add(tid)
                self._redraw()
                return
            if tid not in self._sel_ids:
                self._sel_ids = {tid}
                self._redraw()
            batch = sorted(self._sel_ids) or [tid]
            self._press_info = {"tid": tid, "ctrl": ctrl}
            self._drag = {"tid": tid, "name": hit[1], "color": hit[2],
                          "started": False, "win": None, "batch": batch,
                          "x0": event.x_root, "y0": event.y_root}
            return
        # 点空白 → 开始拉框
        self._sel_ids = set() if not ctrl else set(self._sel_ids)
        self._drag = None
        self._marq = {"x0": cx, "y0": cy, "x1": cx, "y1": cy,
                      "ctrl": ctrl, "started": False, "rect": None}

    def _on_motion(self, event):
        m = getattr(self, "_marq", None)
        if m:
            cx = self.canvas.canvasx(event.x)
            cy = self.canvas.canvasy(event.y)
            m["x1"], m["y1"] = cx, cy
            if not m["started"]:
                if abs(cx - m["x0"]) < 4 and abs(cy - m["y0"]) < 4:
                    return
                m["started"] = True
            self._marquee_apply()
            return
        d = self._drag
        if not d:
            return
        if not d["started"]:
            if abs(event.x_root - d["x0"]) < 5 and abs(event.y_root - d["y0"]) < 5:
                return
            d["started"] = True
            n = len(d.get("batch") or [1])
            label = d["name"] if n <= 1 else "%s 等 %d 个" % (d["name"], n)
            d["win"] = self._make_drag_window(label, d["color"])
        if d["win"] is not None:
            try:
                d["win"].geometry("+%d+%d" % (event.x_root + 14,
                                              event.y_root + 14))
            except Exception:
                pass

    def _remove_many(self, tids):
        """★★ v26（2026-10-01）：**一次把好几个标签踢出标签盒。**

        用户要的：「现在无法框选后一起踢除」。框选/Ctrl 多选之后，
        右键菜单里就有这一项，一次全清掉。
        （只从盒子里移出去，标签本身、文件上的标签都不受影响）
        """
        tids = [int(t) for t in (tids or [])]
        if not tids:
            return
        names = []
        for t in tids:
            r = self._tag_row(t)
            if r:
                names.append(r["name"])
        shown = "、".join(names[:10]) + ("…" if len(names) > 10 else "")
        if not messagebox.askyesno(
                "移出标签盒",
                "把选中的这 %d 个标签移出标签盒吗？\n\n%s\n\n"
                "（标签本身、文件上的标签都不受影响，只是盒子看不见它们了）"
                % (len(tids), shown), parent=self):
            return
        # 从格子配置里也摘掉，免得它们还占着格子
        try:
            if self._read_layout():
                self._remove_from_cells(tids)
        except Exception:
            pass
        ids = [i for i in self._session_ids() if i not in set(tids)]
        self._save_session(ids)
        for t in tids:
            try:
                self.store.tag_box_remove(t)
            except Exception:
                pass
        self._sel_ids = set()
        self._redraw()
        try:
            self.app.set_status("已把 %d 个标签移出标签盒" % len(tids))
        except Exception:
            pass

    def _toggle_sel(self, tid):
        """右键菜单用：把某个标签加进/移出"已选中"这一批。"""
        if tid in self._sel_ids:
            self._sel_ids.discard(tid)
        else:
            self._sel_ids.add(tid)
        self._redraw()

    def _cell_at(self, x, y):
        """鼠标（画布坐标）落在第几个格子里？不在任何格子里返回 None。"""
        for b in (getattr(self, "_cell_boxes", []) or []):
            if b["x0"] <= x <= b["x1"] and b["y0"] <= y <= b["y1"]:
                return b["i"]
        return None

    def _assign_to_cell(self, tids, cell_i):
        """★★ v26（2026-10-01）：**把一批标签归到第 cell_i 格。**

        用户要的就是这个：分格只管数量，具体谁进哪一格**用手拖**。
        规则：
          · 先把这批标签从它们原来所在的格子里摘掉；
          · 再追加到目标格子末尾；
          · 存盘 + 重画。
        """
        layout = self._read_layout()
        if not layout:
            return False
        tids = [int(t) for t in (tids or [])]
        if not tids:
            return False
        if cell_i < 0 or cell_i >= len(layout["cells"]):
            return False
        cells = [list(c) for c in layout["cells"]]
        for cell in cells:
            for t in tids:
                while t in cell:
                    cell.remove(t)
        for t in tids:
            cells[cell_i].append(t)
        self._write_layout({"dir": layout["dir"], "cells": cells})
        self._redraw()
        try:
            self.app.set_status("已把 %d 个标签放进第 %d 格" % (len(tids), cell_i + 1))
        except Exception:
            pass
        return True

    def _remove_from_cells(self, tids):
        """★★ v26：**把一批标签从所有格子里拿出来**（盒子里的标签还在）。"""
        layout = self._read_layout()
        if not layout:
            return False
        tids = [int(t) for t in (tids or [])]
        if not tids:
            return False
        cells = [list(c) for c in layout["cells"]]
        for cell in cells:
            for t in tids:
                while t in cell:
                    cell.remove(t)
        self._write_layout({"dir": layout["dir"], "cells": cells})
        self._redraw()
        try:
            self.app.set_status("已把 %d 个标签从格子里拿出来" % len(tids))
        except Exception:
            pass
        return True

    def _try_drop_into_cell(self, tids, ex, ey):
        """松手时判断：是不是拖到某个格子里了？是就归格，返回 True。

        注意：坐标要转成画布坐标（event.x 是控件坐标）。
        """
        try:
            cx = self.canvas.canvasx(ex)
            cy = self.canvas.canvasy(ey)
        except Exception:
            return False
        # 先看是不是还在盒子范围内 —— 拖到外面就是「拖出去打标签」
        try:
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
        except Exception:
            return False
        if not (0 <= cx <= w and 0 <= cy <= h):
            return False
        if not self._read_layout():
            return False
        ci = self._cell_at(cx, cy)
        if ci is None:
            return False
        # ★ 拖到某个格子 = 归这一格（不是打标签）
        return self._assign_to_cell(tids, ci)


    def _make_drag_window(self, name, color):
        try:
            win = tk.Toplevel(self)
            win.overrideredirect(True)
            try:
                win.attributes("-topmost", True)
            except Exception:
                pass
            tk.Label(win, text="  " + name, bg=color or "#3498db",
                     fg="white", font=(FONT, UI_FONT_SIZE, BOLD),
                     padx=8, pady=3).pack()
            return win
        except Exception:
            return None

    def _on_release(self, event):
        # ---------- 先处理"拉框" ----------
        m = getattr(self, "_marq", None)
        if m:
            self._marq = None
            try:
                if m.get("rect") is not None:
                    self.canvas.delete(m["rect"])
            except Exception:
                pass
            if m.get("started"):
                self._marquee_apply()
                try:
                    self.app.set_status("标签盒：选中 %d 个标签"
                                        "（按 Ctrl 点可以加减，"
                                        "拖它们到文件上 = 一起打标签）"
                                        % len(self._sel_ids))
                except Exception:
                    pass
            else:
                # 点空白没动 = 取消选中
                if self._sel_ids and not m.get("ctrl"):
                    self._clear_selection()
            return

        # ---------- 再处理"拖出去" ----------
        d = self._drag
        self._drag = None
        if not d:
            return
        if d["win"] is not None:
            try:
                d["win"].destroy()
            except Exception:
                pass
        if not d["started"]:
            # 没拖动 = 点了一下 → 给选中文件打标签
            self._apply_one(d["tid"], d["name"])
            return
        # ★★ v26（2026-10-01）：**松手时先看看是不是「拖到某个格子里」。**
        #   用户要的是「具体有哪些标签要被放进对应的格子，希望能直接拖动
        #   放进」。所以：只要松手位置还在盒子范围内，就按格子归属处理，
        #   而不是傻乎乎地去给文件打标签。
        batch = list(d.get("batch") or [d["tid"]])
        if self._try_drop_into_cell(batch, event.x, event.y):
            return
        # ★★ v26：拖出去时，把"选中的这一批"全都打上
        names = []
        for tid in batch:
            r = self._tag_row(tid)
            if r:
                names.append(r["name"])
        if not names:
            names = [d["name"]]
        try:
            self.app._on_tags_dropped(names, event.x_root, event.y_root)
        except AttributeError:
            # 主程序还没有批量版 → 退化成一个个来（不会出错）
            for nm in names:
                try:
                    self.app._on_tag_dropped(nm, event.x_root, event.y_root)
                except Exception:
                    pass
        except Exception as exc:
            try:
                self.app.set_status(T("拖放打标签失败：{x}", x=exc))
            except Exception:
                pass

    def _on_right(self, event):
        hit = self._hit(event)
        if not hit:
            # 点空白右键 → 给个"全不选"菜单
            m = tk.Menu(self, tearoff=0)
            m.add_command(label="已选中 %d 个标签" % len(self._sel_ids),
                          state="disabled")
            m.add_separator()
            m.add_command(label=T("✖ 取消选中"),
                          command=self._clear_selection)
            m.add_command(label=T("▦ 分格设置…"),
                          command=self._open_grid_setup)
            try:
                m.tk_popup(event.x_root, event.y_root)
            finally:
                try:
                    m.grab_release()
                except Exception:
                    pass
            return
        tid, name, _color = hit
        m = tk.Menu(self, tearoff=0)
        m.add_command(label="标签：%s" % name, state="disabled")
        m.add_separator()
        m.add_command(label=T("✖ 从盒子里移出去"),
                      command=lambda: self.remove_tag(tid))
        m.add_command(label=T("📌 固定（换视图也在）"),
                      command=lambda: self.add_tag_fixed(tid, name))
        m.add_command(label=T("取消固定"),
                      command=lambda: (self.store.tag_box_remove(tid),
                                       self._redraw()))
        m.add_separator()
        m.add_command(label=T("给选中的文件打上这个标签"),
                      command=lambda: self._apply_one(tid, name))
        # ★★ v26：多选相关的操作
        m.add_separator()
        # ★★ v26（2026-10-01）：用户要的「框选后一起踢除 / 一起放进某格」。
        #   只要当前选了一批（_sel_ids 非空），菜单里就直接给出批量操作，
        #   不用你一个一个点。
        _sel = sorted(getattr(self, "_sel_ids", set()) or [])
        if len(_sel) > 1:
            m.add_command(
                label="✖ 把选中的这 %d 个一起移出盒子" % len(_sel),
                command=lambda s=_sel: self._remove_many(s))
            layout = self._read_layout()
            if layout:
                sub = tk.Menu(m, tearoff=0)
                for i in range(len(layout["cells"])):
                    sub.add_command(
                        label="放进第 %d 格" % (i + 1),
                        command=lambda ci=i, s=_sel:
                            self._assign_to_cell(s, ci))
                m.add_cascade(label="➡ 把选中的这 %d 个一起放进…" % len(_sel),
                              menu=sub)
                m.add_command(
                    label="✖ 把这 %d 个从格子里拿出来" % len(_sel),
                    command=lambda s=_sel: self._remove_from_cells(s))
            m.add_separator()
        m.add_command(label="☑ 选中它（Ctrl+点可以多选）",
                      command=lambda: self._toggle_sel(tid))
        # 单个标签也能直接归到某一格
        layout1 = self._read_layout()
        if layout1:
            sub1 = tk.Menu(m, tearoff=0)
            for i in range(len(layout1["cells"])):
                sub1.add_command(
                    label="放进第 %d 格" % (i + 1),
                    command=lambda ci=i: self._assign_to_cell([tid], ci))
            m.add_cascade(label="➡ 把「%s」放进…" % name, menu=sub1)
        m.add_command(label=T("✖ 取消全部选中"),
                      command=self._clear_selection)
        m.add_command(label=T("▦ 分格设置…"),
                      command=self._open_grid_setup)
        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            try:
                m.grab_release()
            except Exception:
                pass

    # ---------------- 打标签 ----------------
    def _apply_one(self, tid, name):
        paths = list(self.app.file_list.get_selection() or [])
        if not paths:
            self.app.set_status(T("先选中文件，再从标签盒里点标签（或拖到文件上）"))
            return
        n = 0
        _hit = []          # ★ 2026-10-06：真正打上的，用来记撤销
        for p in paths:
            try:
                self.store.add_tag_to_file(p, name)
                n += 1
                _hit.append((p, name))
            except Exception as exc:
                try:
                    note_swallowed(T("标签盒：打标签失败"), exc)
                except Exception:
                    pass
        try:
            self.app.refresh_tags()
            self.app.refresh_rows_tags()
        except Exception:
            pass
        if _hit:
            self.app.undo_record("tag_add", _hit)
        self.app.set_status(T("已给 {x} 个文件打上「{y}」", x=n, y=name))

    def _apply_to_selection(self):
        ids = self.box_ids()
        if not ids:
            self.app.set_status(T("标签盒是空的"))
            return
        paths = list(self.app.file_list.get_selection() or [])
        if not paths:
            self.app.set_status(T("先选中文件，再点「一键打给选中文件」"))
            return
        names = []
        for tid in ids:
            try:
                row = self.store.tag_by_id(tid)
            except Exception:
                row = None
            if row:
                names.append(row["name"])
        if not names:
            return
        if not messagebox.askyesno(
                "标签盒",
                "给选中的 %d 个文件打上这 %d 个标签？\n\n%s"
                % (len(paths), len(names), "、".join(names[:12])
                   + ("…" if len(names) > 12 else "")), parent=self):
            return
        ok = 0
        _hit = []          # ★ 2026-10-06：记撤销
        for p in paths:
            for nm in names:
                try:
                    self.store.add_tag_to_file(p, nm)
                    ok += 1
                    _hit.append((p, nm))
                except Exception:
                    pass
        try:
            self.app.refresh_tags()
            self.app.refresh_rows_tags()
        except Exception:
            pass
        if _hit:
            self.app.undo_record("tag_add", _hit)
        self.app.set_status("已给 %d 个文件打上 %d 个标签（共 %d 次）"
                            % (len(paths), len(names), ok))

    def _on_files_dropped(self, event):
        try:
            data = event.data or ""
            paths = self.app._parse_dnd_paths(data) if hasattr(
                self.app, "_parse_dnd_paths") else None
        except Exception:
            paths = None
        if not paths:
            return
        ids = self.box_ids()
        if not ids:
            self.app.set_status(T("标签盒是空的：先把标签放进来"))
            return
        names = []
        for tid in ids:
            try:
                row = self.store.tag_by_id(tid)
            except Exception:
                row = None
            if row:
                names.append(row["name"])
        n = 0
        _hit = []          # ★ 2026-10-06：记撤销
        for p in paths:
            for nm in names:
                try:
                    self.store.add_tag_to_file(p, nm)
                    n += 1
                    _hit.append((p, nm))
                except Exception:
                    pass
        try:
            self.app.refresh_tags()
            self.app.refresh_rows_tags()
        except Exception:
            pass
        if _hit:
            self.app.undo_record("tag_add", _hit)
        self.app.set_status("拖进来的 %d 个文件已打上 %d 个标签（共 %d 次）"
                            % (len(paths), len(names), n))

    def _open_picker(self):
        try:
            TagBoxPicker(self, self)
        except Exception as exc:
            messagebox.showerror("标签盒", "打不开勾选窗口：%s" % exc, parent=self)




# ---------- 兜底（★ 它会吃掉错误，所以要专门测"用的哪一份"）----------
def _fallback():
    g = globals()
    for _n in _NEED:
        if g.get(_n) is None:
            g[_n] = _Borrowed(_n)


_fallback()
