# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：HoverPreview。

★ 代码**原样搬运**，一个字没改，只是换了个文件放。

★★ 拆文件的规矩（所有分块文件都照这个写）★★
   ① **Python 自带的东西直接 import**（tk、ttk、os、sys…）——不绕弯。
   ② **只有主程序自己造的东西才向主程序借**（FONT、note_swallowed 这类）。
      而且**不在开头 import 主程序**——两边互相 import 会让 Python
      报错、程序打不开。借法是主程序启动时把「自己」交进来（_set_app）。
   ③ 借来的名字做成**模块级变量**，这样下面的代码**一个字都不用改**。
   ④ 借不到就用兜底值，**不能因为主程序改了个名字就整个打不开**。
   ⑤ ★★ **运行时会变的常量必须用「代理」**（_Borrowed）——
      启动时抄一份的话，**切主题/改缩放之后模块里还是旧值**。

★★ 这个类是什么（从主程序的 docstring 抄的）：
   鼠标悬停在文件上时的「小预览窗」（移开就消失）。
"""
import os
import sys

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, colorchooser

try:
    from PIL import Image, ImageTk
except Exception:
    Image = ImageTk = None

# ---------- 要向主程序借的名字（先占位，挂上后填真身） ----------
_MUTABLE = ['APP_CLOSING', 'HAS_FITZ', 'HAS_PIL', 'UI_FONT_SIZE', 'UI_FONT_SIZE_SMALL']
_NEED = ['APP_CLOSING', 'BOLD', 'BOOK_EXTS', 'FONT', 'HAS_FITZ', 'HAS_PIL', 'IMAGE_EXTS', 'INDEX_SCAN_EVENT', 'T', 'UI_FONT_SIZE', 'UI_FONT_SIZE_SMALL', 'VIDEO_EXTS', 'book_load', 'datetime', 'fmt_size', 'get_pdf_page_pil', 'get_video_thumbnail_pil', 'load_ui_setting', 'pdf_page_count', 'save_ui_setting']
_APP = None


class _Borrowed:
    """★★ 借「**会变的**变量」用的代理（★ 每次读都回主程序现取）。

    ★ 为什么不能直接抄一份：
      像 `THEME_NAME` / `UI_SCALE` 这些**运行时会变** ——
      启动时抄过来，切主题之后**模块里还是旧值**，
      表现在界面上就是"**这一块没跟着变色**"（错题本踩过）。
    ★★ 判据：**"借的是'值'还是'会变的东西'？"** ——
      后者必须用代理。
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
        # ★★★ 必须实现这个 —— 因为**函数也会被借**（T / fmt_size / …）
        #   ★ 少了它：`T("…")` → **TypeError: '_Borrowed' object is not callable**
        #   ★★ 而这个错**会被上层 except 吞掉** → 表现是"悬停预览不工作"，
        #      **一点报错都看不到**（错题本 #143 的教科书案例）。
        return self._v()(*a, **k)

    def __getattr__(self, k):
        return getattr(self._v(), k)

    def __getitem__(self, k):
        return self._v()[k]

    def __iter__(self):
        return iter(self._v())

    def __len__(self):
        return len(self._v())

    def __bool__(self):
        return bool(self._v())

    def __eq__(self, o):
        return self._v() == o

    def __hash__(self):
        return hash(self._v())

    def __str__(self):
        return str(self._v())

    def __repr__(self):
        return repr(self._v())

    def __int__(self):
        return int(self._v())

    def __index__(self):
        return int(self._v())

    def __contains__(self, x):
        return x in self._v()

    def get(self, *a, **k):
        return self._v().get(*a, **k)

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
        if _n in g and isinstance(g[_n], _Borrowed):
            continue
        try:
            # ★★ 会变的 → 代理（每次读现取）
            _v = getattr(_APP, _n, None)
            if _v is not None:
                # ★★★ 一律包代理（错题本 #168）：
                #   模块的桩可能跑在**主程序还没定义这个名字**之前，
                #   所以「启动时取快照」必然借不到。
                #   ★ 代理是**读的时候才现取**，什么时候定义都不影响。
                g[_n] = _Borrowed(_n)
        except Exception:
            pass



class HoverPreview:
    """★ v25 补丁27：鼠标悬停在文件上时的「小预览窗」（移开就消失）。

    它和右侧那个「预览窗格」不冲突：
      · 预览窗格 = 你点一下文件，右边固定显示内容；
      · 这个 = 鼠标**停住 0.6 秒**就飘一个小窗给你瞄一眼，移开就没，
        不想看就完全不用管它。

    设置键：
      hover_preview        —— 总开关（默认开）
      hover_preview_delay  —— 停多久才弹（默认 0.6 秒）
    """

    def __init__(self, app):
        self.app = app
        self.enabled = bool(load_ui_setting("hover_preview", True))
        try:
            self.delay_ms = int(float(
                load_ui_setting("hover_preview_delay", 0.6)) * 1000)
        except Exception:
            self.delay_ms = 600
        if self.delay_ms < 150:
            self.delay_ms = 150
        if self.delay_ms > 3000:
            self.delay_ms = 3000
        self.win = None
        self._job = None
        self._path = None
        self._photo = None
        self._last_xy = (0, 0)
        self._img_lbl = None
        self._txt = None
        self._busy = False

    # ---------- 悬停检测 ----------
    def on_motion(self, event):
        """文件列表里鼠标动了就调这个（很轻，不会卡）。"""
        if not self.enabled:
            return
        try:
            x_root = event.x_root
            y_root = event.y_root
        except Exception:
            return
        self._last_xy = (x_root, y_root)
        path = None
        try:
            path = self.app.file_list.get_path_at_y(y_root, x_root)
        except Exception:
            path = None
        if not path:
            self._cancel()
            return
        if path == self._path and self.win is not None:
            return
        self._cancel()
        self._path = path
        try:
            self._job = self.app.root.after(self.delay_ms, self._show_now)
        except Exception:
            self._job = None

    def on_leave(self, event=None):
        """鼠标离开文件列表 → 收窗。"""
        self._cancel()

    def _cancel(self):
        if self._job is not None:
            try:
                self.app.root.after_cancel(self._job)
            except Exception:
                pass
            self._job = None
        self._hide_window()

    def _hide_window(self):
        if self.win is not None:
            try:
                self.win.destroy()
            except Exception:
                pass
            self.win = None
        self._photo = None

    # ---------- 弹窗 ----------
    def _show_now(self):
        self._job = None
        path = self._path
        if not path or self._busy or APP_CLOSING:
            return
        try:
            if not os.path.exists(path):
                return
        except Exception:
            return
        # 别打扰正在忙的时候
        try:
            if INDEX_SCAN_EVENT.is_set():
                return
        except Exception:
            pass
        self._busy = True
        try:
            self._build_window(path)
        finally:
            self._busy = False

    def _build_window(self, path):
        ext = os.path.splitext(path)[1].lower()
        is_img = ext in IMAGE_EXTS
        is_vid = ext in VIDEO_EXTS
        is_pdf = (ext == ".pdf") and HAS_FITZ
        is_book = ext in BOOK_EXTS
        # ★★ 2026-10-03：用户要求「鼠标悬停的缩略图再大一些，最好大个两倍」——
        #   这里原来固定 380x300，现在放大到 760x600（正好两倍），
        #   同时按屏幕尺寸收一收，免得小屏幕上顶出边。
        max_w, max_h = 760, 600
        try:
            _sw = self.app.root.winfo_screenwidth()
            _sh = self.app.root.winfo_screenheight()
            max_w = int(min(max_w, max(360, _sw * 0.55)))
            max_h = int(min(max_h, max(260, _sh * 0.60)))
        except Exception:
            pass
        text_only = not (is_img or is_vid or is_pdf or is_book)
        win = tk.Toplevel(self.app.root)
        win.overrideredirect(True)
        try:
            win.attributes("-topmost", True)
        except Exception:
            pass
        # ★ 补丁27：小窗别超出屏幕（文本长了会撑得很高）
        try:
            max_h = min(max_h, win.winfo_screenheight() - 80)
        except Exception:
            pass
        frame = tk.Frame(win, bg="#222", bd=1, relief="solid")
        frame.pack(fill="both", expand=True)
        title = tk.Label(frame, text=os.path.basename(path), bg="#222",
                         fg="#eee", font=(FONT, UI_FONT_SIZE, BOLD),
                         anchor="w", justify="left", wraplength=max_w - 16)
        title.pack(fill="x", padx=6, pady=(4, 2))
        body = tk.Frame(frame, bg="#222")
        body.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        self._img_lbl = None
        self._txt = None
        shown = False

        if is_img and HAS_PIL:
            try:
                from PIL import Image, ImageTk  # type: ignore
                im = Image.open(path)
                im.thumbnail((max_w - 12, max_h))
                self._photo = ImageTk.PhotoImage(im)
                self._img_lbl = tk.Label(body, image=self._photo, bg="#222")
                self._img_lbl.pack()
                shown = True
            except Exception as exc:
                self._info_in(body, "（这张图打不开：%s）" % str(exc)[:60])
                shown = True
        elif is_pdf:
            # ★ 补丁28：PDF 也给它画第一页出来（鼠标一停就能瞄一眼）
            im = None
            try:
                im = get_pdf_page_pil(path, 0, max_w - 12, max_h - 24)
            except Exception:
                im = None
            if im is not None:
                try:
                    from PIL import ImageTk  # type: ignore
                    self._photo = ImageTk.PhotoImage(im)
                    self._img_lbl = tk.Label(body, image=self._photo, bg="#222")
                    self._img_lbl.pack()
                    npages = pdf_page_count(path)
                    tk.Label(body, text="📄 PDF 第 1 页 · 共 %d 页" % npages,
                             bg="#222", fg="#9cf", font=(FONT, UI_FONT_SIZE_SMALL)).pack()
                    shown = True
                except Exception:
                    im = None
            if not shown:
                self._info_in(body, "📄 PDF（这一页画不出来，双击可以打开）")
                shown = True
        elif is_book:
            # ★ 补丁29：电子书 —— 悬停时给一小段开头文字
            head_txt = ""
            try:
                _t, chapters = book_load(path)
                if chapters:
                    head_txt = chapters[0][:600]
            except Exception:
                head_txt = ""
            if head_txt:
                tk.Label(body, text=head_txt, bg="#222", fg="#ddd",
                         font=(FONT, UI_FONT_SIZE), justify="left", anchor="nw",
                         wraplength=max_w - 16).pack(fill="both", expand=True)
                tk.Label(body, text=T("📖 电子书（点一下能在右边整页看）"),
                         bg="#222", fg="#9cf", font=(FONT, UI_FONT_SIZE_SMALL)).pack()
            else:
                self._info_in(body, "📖 电子书\n（读不出来，双击可以用系统"
                                    "阅读器打开）")
            shown = True
        elif is_vid and HAS_PIL:
            im = None
            try:
                im = get_video_thumbnail_pil(path, max_w - 12)
            except Exception:
                im = None
            if im is not None:
                try:
                    from PIL import ImageTk  # type: ignore
                    self._photo = ImageTk.PhotoImage(im)
                    self._img_lbl = tk.Label(body, image=self._photo, bg="#222")
                    self._img_lbl.pack()
                    tk.Label(body, text=T("▶ 视频"), bg="#222",
                             fg="#9cf", font=(FONT, UI_FONT_SIZE_SMALL)).pack()
                    shown = True
                except Exception:
                    im = None
            if not shown:
                self._info_in(body, "▶ 视频\n（系统没给这张封面，双击可以播放）")
                shown = True

        if not shown or text_only:
            # 文本 / 其它：显示前 2KB 文字或信息
            info = self._quick_text(path)
            if info is None:
                info = ""
            self._txt = tk.Label(body, text=info or "（没有可预览的内容）",
                                 bg="#222", fg="#ddd", font=(FONT, UI_FONT_SIZE),
                                 justify="left", anchor="nw",
                                 wraplength=max_w - 16)
            self._txt.pack(fill="both", expand=True)
            # ★ 补丁27：限制小窗高度（文本长了别撑破屏幕），超了就在窗里滚动
            try:
                if self._txt.winfo_reqheight() > max_h - 40:
                    self._txt.pack_forget()
                    cvv = tk.Canvas(body, bg="#222", width=max_w - 14,
                                    height=max_h - 40, highlightthickness=0)
                    sbv = ttk.Scrollbar(body, orient="vertical",
                                        command=cvv.yview)
                    cvv.configure(yscrollcommand=sbv.set)
                    sbv.pack(side="right", fill="y")
                    cvv.pack(side="left", fill="both", expand=True)
                    inner = tk.Frame(cvv, bg="#222")
                    cvv.create_window((0, 0), window=inner, anchor="nw")
                    tk.Label(inner, text=info, bg="#222", fg="#ddd",
                             font=(FONT, UI_FONT_SIZE), justify="left", anchor="nw",
                             wraplength=max_w - 30).pack()
                    inner.bind("<Configure>",
                               lambda e, c=cvv: c.configure(
                                   scrollregion=c.bbox("all")))
                    self._txt = inner
            except Exception:
                pass
            shown = True

        # 位置：鼠标右下方，靠边就翻到另一侧
        try:
            win.update_idletasks()
            w = win.winfo_reqwidth()
            h = win.winfo_reqheight()
            sw = win.winfo_screenwidth()
            sh = win.winfo_screenheight()
            x = self._last_xy[0] + 18
            y = self._last_xy[1] + 18
            if x + w > sw - 8:
                x = max(8, self._last_xy[0] - w - 18)
            if y + h > sh - 8:
                y = max(8, self._last_xy[1] - h - 18)
            win.geometry("+%d+%d" % (x, y))
        except Exception:
            pass
        self.win = win

    def _info_in(self, parent, text):
        tk.Label(parent, text=text, bg="#222", fg="#ddd", font=(FONT, UI_FONT_SIZE),
                 justify="left", wraplength=360, anchor="nw").pack(
            fill="both", expand=True)

    def _quick_text(self, path):
        """文本类返回前几 KB；其它返回一句信息（都很快，不读大文件）。"""
        ext = os.path.splitext(path)[1].lower()
        text_exts = {".txt", ".md", ".py", ".json", ".log", ".ini", ".bat",
                     ".csv", ".xml", ".yml", ".yaml", ".html", ".htm", ".js",
                     ".css", ".c", ".cpp", ".h", ".java", ".sh", ".cfg",
                     ".conf", ".toml", ".rst", ".sql", ".tsv", ".srt", ".sub"}
        if ext not in text_exts:
            try:
                st = os.stat(path)
                return ("%s\n\n大小：%s\n修改：%s" % (
                    os.path.basename(path),
                    fmt_size(st.st_size),
                    datetime.fromtimestamp(st.st_mtime).strftime(
                        "%Y-%m-%d %H:%M")))
            except Exception:
                return os.path.basename(path)
        try:
            with open(path, "rb") as f:
                raw = f.read(2048)
        except Exception as exc:
            return "（读不出来：%s）" % str(exc)[:60]
        if b"\x00" in raw:
            return "（这是个二进制文件）"
        for enc in ("utf-8", "gbk", "utf-16"):
            try:
                return raw.decode(enc)[:1200]
            except Exception:
                continue
        return raw.decode("utf-8", errors="replace")[:1200]

    # ---------- 开关 ----------
    def set_enabled(self, on):
        self.enabled = bool(on)
        try:
            save_ui_setting("hover_preview", self.enabled)
        except Exception:
            pass
        if not self.enabled:
            self._cancel()

    def toggle(self):
        self.set_enabled(not self.enabled)
        try:
            self.app.set_status(
                "鼠标悬停预览：%s（把鼠标停在文件上 %d 毫秒就弹小窗）"
                % ("已开启" if self.enabled else "已关闭",
                   int(self.delay_ms)))
        except Exception:
            pass


# ==========================================================================
#  ★ v25：公共小工具（鼠标滚轮 / 索引扫描）
# ==========================================================================


# ---------- 兜底：主程序没挂上也不能崩（★ 界面能看 > 精确） ----------
def _fallback():
    g = globals()
    for _n in _NEED:
        if g.get(_n) is None:
            g[_n] = _Borrowed(_n)


_fallback()
