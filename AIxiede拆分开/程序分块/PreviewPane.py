# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：PreviewPane。

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
   · import 要写 `from PreviewPane import …`（**不带包路径**）
   · `_set_app` 要**取别名**（`as _fk_…`）—— 模块名和类名同名
   · 借名字清单**用 symtable + dir() 定**，别用正则猜
   · 代理类**必须实现 `__call__`**（函数也会被借）
   · ★ 兜底 except 会吃掉错误 → **必须专门测"用的哪一份"**
"""
import datetime
import hashlib
import json
import os
import shutil
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, colorchooser

# ---------- 要向主程序借的名字 ----------
_MUTABLE = ['APP_CLOSING', 'BOLD', 'FONT', 'HAS_FITZ', 'HAS_PIL', 'UI_FONT_SIZE']
_NEED = ['APP_CLOSING', 'BOLD', 'BOOK_EXTS', 'FONT', 'HAS_FITZ', 'HAS_PIL', 'IMAGE_EXTS', 'T', 'Tooltip', 'UI_FONT_SIZE', 'VIDEO_EXTS', '_bg_post', '_detect_book_drm', '_drain_ui_mail', '_fitz_mod', '_preview_cache_dir', 'book_load', 'datetime', 'fmt_size', 'get_ui_icon', 'get_video_thumbnail_pil', 'is_remote_path', 'note_swallowed', 'os', 'pdf_prepare', 'render_pdf_page', 'theme_get']
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
    # ★★★ 保护模块自己的 `__file__`（错题本 #165）：
    #   `_NEED` 里**不该**有 `__file__` —— 但万一以后又混进来，
    #   这里也能兜住：**取完名字之后把它写回模块真身**。
    #   ★ 为什么重要：模块里用 `__file__` 算资源路径，
    #     被覆盖成主程序路径之后**算出来的全是错的**，
    #     而且**不报错**（找不到就当没有 → 被兜底吃掉）。
    _own_file = __file__
    _APP = app
    _fill()
    globals()["__file__"] = _own_file


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


class PreviewPane(ttk.Frame):
    """★ v25 补丁8：右侧「预览」窗格（方案 A：分类库 | 文件列表 | 预览 | 标签库）。

    - 默认隐藏：点窗口右下角状态栏的「📄 预览」按钮才出现，宽度可以拖；
    - 选中一个文件就预览：文本类看内容、图片看缩略图、其它看文件信息；
    - 只读，绝不改动任何文件。
    """

    # 当成「文本」直接读出来看的扩展名
    TEXT_EXTS = {
        ".txt", ".md", ".markdown", ".log", ".ini", ".cfg", ".conf", ".json",
        ".py", ".js", ".ts", ".html", ".htm", ".css", ".xml", ".yml", ".yaml",
        ".bat", ".cmd", ".ps1", ".sh", ".sql", ".csv", ".tsv", ".toml",
        ".c", ".h", ".cpp", ".hpp", ".java", ".go", ".rs", ".rb", ".php",
        ".srt", ".ass", ".vtt", ".nfo", ".url", ".m3u", ".reg", ".srt",
    }
    MAX_READ = 256 * 1024        # 最多读 256KB，免得一个大日志把界面卡住

    def __init__(self, master, app=None):
        super().__init__(master, padding=(10, 0, 0, 0))
        self.app = app
        self.current_path = None
        self._photo = None

        head = ttk.Frame(self)
        head.pack(fill="x")
        ttk.Label(head, text=T("预览"), font=(FONT, UI_FONT_SIZE, BOLD)).pack(side="left")
        # ★★ 2026-10-03：类型信息（「文本 · 372 B · 时间」/「PDF 连续滚动 · 共
        #   154 页…」）原来跟在「预览」后面、挤在同一行：一是左边对不齐
        #   （用户说的「拷贝到本地再打开 与 预览、正在读取 不是左边平齐的」），
        #   二是信息一长就被截掉。现在**单独占一行、左对齐**，跟下面的
        #   文件名 / 路径 / 内容全部对齐在同一条竖线上。
        self.kind_lbl = ttk.Label(self, text="", foreground=theme_get("fg_dim"),
                                  anchor="w", justify="left")
        self.kind_lbl.pack(fill="x", anchor="w", pady=(0, 1))

        self.name_lbl = ttk.Label(self, text="", foreground=theme_get("fg"),
                                  font=(FONT, UI_FONT_SIZE, BOLD),
                                  wraplength=330, justify="left", anchor="w")
        self.name_lbl.pack(fill="x", anchor="w", pady=(2, 2))
        self.path_lbl = ttk.Label(self, text="", foreground=theme_get("fg_dim"),
                                  wraplength=330, justify="left", anchor="w")
        self.path_lbl.pack(fill="x", anchor="w", pady=(0, 4))
        # 宽度变了就把换行宽度跟着调（原来死写 330 —— 窗格拉宽了文字还是
        # 窄窄一条，右边一大片空白，用户说的「空间利用率比较差」就是它）。
        try:
            self.bind("<Configure>", self._on_pane_configure, add="+")
        except Exception:
            pass

        self.img_lbl = ttk.Label(self, anchor="center")

        body = ttk.Frame(self)
        # ★ v25 补丁30（体检修复）：原来 body 一进来就 pack(expand=True)，
        #   而图片是 pack 在它**外面**的，图片一出来就把 body 挤到看不见、
        #   翻页条更是没地方放（实测 winfo_ismapped()=0）。
        #   现在改成「显示哪种内容才 pack 哪个容器」，互不打架。
        self._body = body
        self.text = tk.Text(body, wrap="word", width=34, height=12,
                            font=(FONT, UI_FONT_SIZE), padx=2, pady=6,
                            relief="flat", highlightthickness=1,
                            highlightbackground=theme_get("line"),
                            bg=theme_get("text_bg"),
                            fg=theme_get("fg"),
                            insertbackground=theme_get("fg"),
                            selectbackground=theme_get("select_bg"))
        vsb = ttk.Scrollbar(body, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=vsb.set)
        self._vsb = vsb
        self._body_packed = False
        self._show_text("")

        # 翻页条（PDF / 电子书共用，平时藏着）
        # ★ 2026-10-03：按钮的内边距收小一点，让按钮里的字**和上面那些
        #   文字左边对齐**（用户反馈「拷到本地再打开 与 预览、正在读取
        #   不是左边平齐的」）。
        self.nav_bar = ttk.Frame(self)
        self._nav_prev = ttk.Button(self.nav_bar, text=T("◀ 上一页"), width=9,
                                    padding=(2, 4))
        self._nav_prev.pack(side="left")
        self._nav_next = ttk.Button(self.nav_bar, text=T("下一页 ▶"), width=9,
                                    padding=(2, 4))
        self._nav_next.pack(side="left", padx=4)
        self._nav_info = ttk.Label(self.nav_bar, text="", anchor="w")
        self._nav_info.pack(side="left", padx=(6, 0))

        # ★★ 2026-10-07 新增：**预览缩放条**（用户要的"两个被方框包起来的加减号"）。
        #   用户原话：「Ctrl+滚轮、Ctrl +/-、和两个被方框包起来的加减号图标
        #   都是缩放交互」。
        #   ★ 为什么不塞在 nav_bar 里（第一版就塞那儿，**结果一个都不显示**）：
        #     `nav_bar` 只在 `_show_nav()`（翻页场景）里 pack，
        #     而**单张图片那条路根本不调它** → 按钮被建出来了却没人摆。
        #   ★ 现在单独一条 `_zoom_bar`，谁都能用（图片/PDF/电子书都走画布）。
        #   ★ 图标用**图片**（用户定过规矩：图标全用图片型）；
        #     取不到图就退回 "+" / "−" 文字，绝不空白（错题本 #5）。
        try:
            _zin = get_ui_icon("zoom_in", 16)
            _zout = get_ui_icon("zoom_out", 16)
        except Exception:
            _zin = _zout = None
        try:
            self._zoom_bar = ttk.Frame(self)
            ttk.Label(self._zoom_bar, text=T("缩放"), anchor="w").pack(
                side="left")
            # ➖ 缩小
            # ★★ 2026-10-07 修（截图看出来的）：原来 `width=3` 把图片**裁掉了一半**
            #   （截图里 ➖ 只剩半个蓝块）。★ 图标的按钮**别设 width** ——
            #   宽度交给图片自己撑（ttk 会用 image 的尺寸），设了 width 反而裁图。
            self._zoom_out_btn = ttk.Button(
                self._zoom_bar,
                image=(_zout if _zout is not None else ""),
                text=("" if _zout is not None else "－"),
                width=(3 if _zout is None else 0), padding=(2, 2),
                command=lambda: self.zoom_by(1 / 1.15))
            if _zout is not None:
                try:
                    self._zoom_out_btn._icon_ref = _zout
                except Exception:
                    pass
            self._zoom_out_btn.pack(side="left", padx=(6, 0))
            # 百分数（点一下 = 复位到 100%）
            self._zoom_pct_lbl = ttk.Button(
                self._zoom_bar, text="100%", width=6, padding=(2, 2),
                command=self.zoom_reset)
            self._zoom_pct_lbl.pack(side="left", padx=4)
            # ➕ 放大
            self._zoom_in_btn = ttk.Button(
                self._zoom_bar,
                image=(_zin if _zin is not None else ""),
                text=("" if _zin is not None else "＋"),
                width=(3 if _zin is None else 0), padding=(2, 2),
                command=lambda: self.zoom_by(1.15))
            if _zin is not None:
                try:
                    self._zoom_in_btn._icon_ref = _zin
                except Exception:
                    pass
            self._zoom_in_btn.pack(side="left")
            # 右边给一句"怎么用"（用户之前提过提示太少）
            try:
                ttk.Label(self._zoom_bar,
                          text=T("Ctrl+滚轮缩放 · 空格+拖动"),
                          foreground=theme_get("fg_dim")).pack(
                    side="right", padx=(0, 4))
            except Exception:
                pass
            # 悬停提示（图标按钮得说清是什么）
            try:
                Tooltip(self._zoom_out_btn, "缩小（Ctrl+滚轮下滚 / Ctrl+-）")
                Tooltip(self._zoom_in_btn, "放大（Ctrl+滚轮上滚 / Ctrl++）")
                Tooltip(self._zoom_pct_lbl, "点一下恢复 100%（Ctrl+0）")
            except Exception:
                pass
        except Exception as _e:
            try:
                note_swallowed(T("预览缩放条没建出来"), _e, quiet=True)
            except Exception:
                pass
        # ★★ v26 新增：网盘文件预取**进度条**（默认隐藏，拷贝时才出现）。
        #   用户反馈：「能不能让网盘的文件也能预览，最好还有个进度条
        #   显示加载进度，最好界面也别卡住」—— 这个进度条就是给它用的。
        self._nav_prog = ttk.Progressbar(
            self.nav_bar, mode="determinate", length=180, maximum=100)

        # ★★ v26 新增：网盘文件「本地缓存」的簿记。
        #   key   = 网盘上的原始路径
        #   value = 已经拷到本地临时目录的那个副本路径
        #   网盘文件不再硬着头皮去读网盘（要等几十秒、界面卡死），
        #   而是在后台把它拷到本地，之后所有读取都走本地副本 —— 秒开。
        self._remote_tmp = {}
        # 拷贝任务的令牌：切换文件 / 取消 时 +1，老任务看到就自己退出
        self._fetch_cancel = 0
        # ★★ v26：启动时把上次残留的缓存清掉。
        #   用户反馈：「缓存目录在哪里、能不能自己设」——
        #   现在目录可以是用户自己设的，所以**不能整个 rmtree** ——
        #   万一把它设成桌面之类的，就删了人家东西了。
        #   改成：**只删我们自己建的那种子目录** ——
        #   规则：目录名是 12 位十六进制（原路径 md5 前 12 位）。
        try:
            import shutil as _sh
            _cd = _preview_cache_dir()
            if os.path.isdir(_cd):
                for _n in os.listdir(_cd):
                    if len(_n) != 12:
                        continue
                    try:
                        int(_n, 16)
                    except Exception:
                        continue
                    _p = os.path.join(_cd, _n)
                    try:
                        if os.path.isdir(_p):
                            _sh.rmtree(_p, ignore_errors=True)
                        else:
                            os.remove(_p)
                    except Exception:
                        pass
        except Exception:
            pass

    def _on_pane_configure(self, event=None):
        """★★ 2026-10-03：窗格宽度变了 → 名字/路径的换行宽度跟着变。

        原来这两行死写 wraplength=330：窗格拉到 670 宽，文字还是只占
        330，右边一大片空着（用户说的「空间利用率比较差」）。
        现在跟着窗格宽度走（左边留 2 像素、右边留 8 像素）。
        """
        try:
            w = int(self.winfo_width()) - 12
        except Exception:
            return
        if w < 120:
            return
        if w == getattr(self, "_wrap_w", 0):
            return
        self._wrap_w = w
        for lbl in (getattr(self, "name_lbl", None),
                    getattr(self, "path_lbl", None),
                    getattr(self, "kind_lbl", None)):
            if lbl is None:
                continue
            try:
                lbl.configure(wraplength=w)
            except Exception:
                pass
        # ★★ 2026-01-26：canvas 宽度也要随窗格更新
        cv = getattr(self, "_img_cv", None)
        if cv is not None and cv.winfo_ismapped():
            try:
                cv.configure(width=max(160, w - 12))
            except Exception:
                pass

    # ---------- ★ 补丁30：统一管理「现在显示的是哪个容器」 ----------
    # ★★ 2026-10-03：用户反馈「右侧预览区域显示太割裂了、空间利用率差」。
    #   用截图放大看出来的真相：**两个容器会同时挂在窗格里** ——
    #   比如先看了一个 PDF（连滚动画布是 side="left" 铺开的），
    #   再选一个网盘大文件（要改成显示文字）时，
    #   画布**没有被收掉**，于是左边半屏是画布、右边半屏是文字框，
    #   底下那条「📥 拷到本地再打开」也被挤到剩下一半宽度、看起来像居中。
    #   原因：以前只各自 pack_forget 了自己记得的那几个控件，漏了画布和它的滚动条。
    #   现在统一走这个函数：换内容之前**先把所有容器都收起来**。
    def _repaint_theme(self):
        """★★ 2026-10-06：换皮肤之后，把预览区里「画上去」的颜色重刷一遍。

        为什么不能只靠「扫控件换色」：预览区里有一半颜色不是控件属性，
        而是**用代码画上去的**（画布底色、标题字色、翻页条按钮），
        扫控件扫不到它们，得在这儿手动重刷。
        ★ 每一块单独包 try —— 坏一块不影响别的（本程序一贯的写法）。
        """
        # ① 滚动画布（看 PDF / 图片那片）的底色
        try:
            cv = getattr(self, "_img_cv", None)
            if cv is not None:
                cv.configure(bg=theme_get("canvas_bg"),
                             highlightbackground=theme_get("line"))
        except Exception:
            pass
        # ② 提示文字 / 大纲那块文本框
        try:
            t = getattr(self, "text", None)
            if t is not None:
                t.configure(bg=theme_get("text_bg"),
                            fg=theme_get("fg"),
                            insertbackground=theme_get("fg"),
                            selectbackground=theme_get("select_bg"))
        except Exception:
            pass
        # ③ 名字 / 路径 / 类型那三行标签
        for nm in ("name_lbl", "path_lbl", "kind_lbl"):
            try:
                w = getattr(self, nm, None)
                if w is not None:
                    w.configure(bg=theme_get("card_bg"),
                                fg=(theme_get("fg") if nm == "name_lbl"
                                    else theme_get("fg_dim")))
            except Exception:
                continue
        # ④ 底下那条翻页 / 按钮栏
        for nm in ("nav_bar", "_nav_info", "_nav_prev", "_nav_next"):
            try:
                w = getattr(self, nm, None)
                if w is None:
                    continue
                try:
                    w.configure(bg=theme_get("win_bg"))
                except Exception:
                    pass
                try:
                    w.configure(fg=theme_get("fg"))
                except Exception:
                    pass
            except Exception:
                continue
        # ⑤ 外层几个容器
        for nm in ("_img_box",):
            try:
                w = getattr(self, nm, None)
                if w is not None:
                    w.configure(style="Card.TFrame")
            except Exception:
                pass

    def _hide_all_content(self):
        """换内容之前，先把所有容器都收起来。

        ★★ 2026-10-06 修「预览变空白 / 连 .txt 都看不了」★★
           用户原话：「右侧预览又有问题了，现在连 .txt 都没法预览」。
           查出来的病根：**开关和实际情况对不上** ——
             `_body`（文本框）被这里 `pack_forget()` 收走了，
             但 `_body_packed` 这个开关**还留着 True**（说「已经摆好了」）。
             等下次要看文本时，`_show_body()` 一看开关是 True，
             就**跳过「摆出来」那一步** → 内容明明读到了，
             屏幕上却**永远空白**。
           （实测就是这么复现的：`text.get()` 拿得到内容，
            但 `text.winfo_ismapped()` = 0 —— 有内容但没显示。）
           修法：这里收控件的时候，**把开关也改成「没摆」** ——
           让开关始终跟实际情况一致。

        ★★ 2026-10-06：**「两个按钮不见了」的根子也在这里** ★★
           底部那条「⬆ 回到顶部 / 🔄 重新加载」住的容器就是 `nav_bar`。
           以前这个函数会把它（连同里面的两个按钮）一起收走；
           而 PDF 那条路是先摆好按钮、再调 `_show_pdf` → `_show_img()`
           → `_hide_all_content()` —— **等于刚摆好就被收走了**。
           表现就是用户说的：「自第二次重开，那两个按钮没了」。
           ★ 现在：PDF 连续滚动模式下**不收走导航条**，
             宁可多留一条也别让按钮消失（收错了只是多一条，
             按钮没了用户就没法操作了）。
        """
        _keep_nav = bool(getattr(self, "_pdf_scroll_path", None))
        for w in (getattr(self, "img_lbl", None),
                  getattr(self, "_body", None),
                  getattr(self, "_img_box", None),
                  getattr(self, "_img_cv", None),
                  getattr(self, "_img_cv_sb", None)):
            if w is None:
                continue
            try:
                w.pack_forget()
            except Exception:
                pass
        # ★ 导航条（翻页 / 回到顶部 / 重新加载）单独处理：
        #   PDF 连续滚动时**留着**，别的地方照旧收掉。
        if not _keep_nav:
            for w in (getattr(self, "nav_bar", None),):
                if w is None:
                    continue
                try:
                    w.pack_forget()
                except Exception:
                    pass
        # ★★ 关键的一行：控件都收走了，开关也要跟着改 —— 否则下次
        #   `_show_body()` 会误以为「已经摆好了」而跳过摆放，预览一片空白。
        self._body_packed = False

    def _show_body(self):
        """显示文本区（同时收掉图片、画布和翻页条）。

        ★★ 2026-10-06 加固：不再只信 `_body_packed` 这个开关 ——
           开关出过一次错（见 `_hide_all_content` 的说明），
           结果就是「预览一片空白」。
           现在多问一句实在的：**控件现在到底在不在屏幕上**。
           只要它没显示出来，就重新摆一次 —— 这样开关偶尔记错也不怕。
        """
        self._hide_all_content()
        try:
            # ★ 多问一句实际情况（不只信开关）
            _shown = False
            try:
                _shown = bool(self.text.winfo_ismapped())
            except Exception:
                _shown = False
            if not self._body_packed or not _shown:
                self._vsb.pack(side="right", fill="y")
                self.text.pack(side="left", fill="both", expand=True)
                self._body.pack(fill="both", expand=True)
                self._body_packed = True
        except Exception as _e:
            note_swallowed(T("预览：把文本区摆出来失败（预览可能是空白）"), _e)

    def _show_img(self):
        """切到「画布显示图片」模式（收掉文本框和翻页条）。

        ★ v25 补丁37：以前这里是把图贴到一个 Label（img_lbl）上再 pack 出来，
        实测在你机器上**贴上去也看不见**（PDF 明明渲染成功了，屏幕上却是空的
        —— 这就是「pdf 只有描述没有内容」的真正原因）。现在改成往
        **Canvas.create_image** 上画：Canvas 画图这条路是可靠的。

        ★★ 2026-10-07 新增：**顺手把缩放条摆出来**。
          为什么：缩放按钮原来建在 `nav_bar` 上，而 `nav_bar` 只在
          `_show_nav()` 里 pack —— **单张图片那条路根本不调它**，
          所以按钮**一个都不显示**（截图验证时发现的）。
          ★ 教训：**控件建好了不等于显示出来了** ——
            pack 的时机要跟"这次要显示什么"对上。
        """
        self._hide_all_content()
        self._body_packed = False
        self._show_zoom_bar()

    def _show_zoom_bar(self):
        """把「预览缩放」那一小条摆出来（➖ 100% ➕）。

        ★ 单独一条、**钉在预览窗格底部**，谁都能用：
          单张图片、PDF 连续滚动、电子书……都是图片画在画布上的，
          都有缩放需求。原来塞在 `nav_bar` 里只有翻页场景才出现。
        """
        try:
            zb = getattr(self, "_zoom_bar", None)
            if zb is None:
                return
            if not zb.winfo_ismapped():
                zb.pack(side="bottom", fill="x", pady=(2, 0))
            self._zoom_label_update()
        except Exception as _e:
            try:
                note_swallowed(T("缩放条没摆出来"), _e, quiet=True)
            except Exception:
                pass

    def _zoom_label_update(self):
        """把缩放条上那个百分数刷新一下。"""
        try:
            w = getattr(self, "_zoom_pct_lbl", None)
            if w is None:
                return
            pct = int(round(float(getattr(self, "_user_zoom", 1.0) or 1.0) * 100))
            w.configure(text="%d%%" % pct)
        except Exception:
            pass

    def _img_canvas(self):
        """懒建「显示图片用」的滚动画布。

        ★★ 2026-10-03：画布外面包了一层容器（_img_box）。
          为什么：原来画布是**直接挂在窗格上、side="left"** 的，
          而底下的翻页条是 side="bottom" —— 两种方向混在同一个容器里，
          Tk 分配位置时会把翻页条挤到「画布右边那一条窄缝」里，
          于是「📥 拷到本地再打开 / ◀ 上一页」这些按钮
          看起来像是跑到中间去了（用户说的「不是左边平齐的」）。
          现在：翻页条先贴底（横跨整个窗格宽度），
          然后这个容器填满剩下的中间区域。
        """
        cv = getattr(self, "_img_cv", None)
        if cv is not None:
            return cv
        self._img_box = ttk.Frame(self)
        self._img_cv_sb = ttk.Scrollbar(self._img_box, orient="vertical")
        # ★★ 2026-10-07 新增：**横向滚动条**。
        #   为什么：放大之后图片比窗格宽，**右边的部分就看不到了**
        #   （截图里能看到：放 160% 后右边被切）。
        #   原来只有竖直滚动条，横向只能靠拖动 —— 但用户不一定知道能拖。
        #   ★ 有横向滚动条 = "看得见还有内容"，这是最省事的提示。
        self._img_cv_hsb = ttk.Scrollbar(self._img_box, orient="horizontal")
        cv = tk.Canvas(self._img_box, highlightthickness=1,
                       bg=theme_get("canvas_bg"),
                       highlightbackground=theme_get("line"))
        cv.configure(yscrollcommand=self._img_cv_sb.set,
                     xscrollcommand=self._img_cv_hsb.set)
        self._img_cv_sb.configure(command=cv.yview)
        self._img_cv_hsb.configure(command=cv.xview)
        # 摆位：先贴右边（竖条）和底边（横条），画布占剩下的
        self._img_cv_hsb.pack(side="bottom", fill="x")
        self._img_cv_sb.pack(side="right", fill="y")
        cv.bind("<MouseWheel>", self._img_cv_wheel, add="+")
        cv.bind("<Button-4>", self._img_cv_wheel, add="+")
        cv.bind("<Button-5>", self._img_cv_wheel, add="+")
        cv.bind("<Configure>", lambda e: self.after(60, self._img_refit))
        # ★★ 2026-10-07 新增：**手势拖动**（用户要的「手势拖动」）。
        #   规矩跟外面的看图软件一致：
        #     · **按住空格** + 左键拖 = 平移（光标变"四向箭头"提示可以拖）
        #     · **中键**拖 = 平移（不用按空格，更省事）
        #   ★ 为什么不直接"左键拖"就平移：左键在预览区可能还要用来点链接/选文字，
        #     而且用户明确说了是**按住空格拖动**。
        cv.bind("<ButtonPress-1>", self._img_pan_press, add="+")
        cv.bind("<B1-Motion>", self._img_pan_motion, add="+")
        cv.bind("<ButtonRelease-1>", self._img_pan_release, add="+")
        cv.bind("<ButtonPress-2>", self._img_pan_press, add="+")
        cv.bind("<B2-Motion>", self._img_pan_motion, add="+")
        cv.bind("<ButtonRelease-2>", self._img_pan_release, add="+")
        # ★ 空格按下/抬起（窗口级 —— 鼠标在预览区时按空格才生效，
        #   所以在 enter/leave 里挂/摘，免得抢了主窗口的空格预览）
        cv.bind("<Enter>", lambda e: cv.focus_set(), add="+")
        cv.bind("<KeyPress-space>", lambda e: self._preview_space(e, True),
                add="+")
        cv.bind("<KeyRelease-space>", lambda e: self._preview_space(e, False),
                add="+")
        # ★ 缩放快捷键（Ctrl+= / Ctrl+- / Ctrl+0），鼠标在预览区时才管
        cv.bind("<Control-equal>", lambda e: (self.zoom_by(1.15), "break")[1],
                add="+")
        cv.bind("<Control-plus>", lambda e: (self.zoom_by(1.15), "break")[1],
                add="+")
        cv.bind("<Control-minus>", lambda e: (self.zoom_by(1 / 1.15),
                                              "break")[1],
                add="+")
        cv.bind("<Control-Key-0>", lambda e: (self.zoom_reset(), "break")[1],
                add="+")
        self._img_cv = cv
        self._img_items = {}
        self._img_photos = {}
        return cv

    def _img_cv_wheel(self, event):
        cv = getattr(self, "_img_cv", None)
        if cv is None:
            return
        # ★★ 2026-10-07 新增：**Ctrl + 滚轮 = 缩放**（用户要的）。
        #   不按 Ctrl 就是普通的上下滚动 —— 保持原样，别抢用户的老习惯。
        try:
            ctrl = bool(event.state & 0x0004)
        except Exception:
            ctrl = False
        if ctrl:
            # 往上滚（delta>0 / num==4）= 放大
            try:
                if getattr(event, "num", None) == 4:
                    big = True
                elif getattr(event, "num", None) == 5:
                    big = False
                else:
                    big = (event.delta or 0) > 0
            except Exception:
                big = True
            self.zoom_by(1.15 if big else (1 / 1.15))
            return "break"
        try:
            if getattr(event, "num", None) == 4:
                cv.yview_scroll(-3, "units")
            elif getattr(event, "num", None) == 5:
                cv.yview_scroll(3, "units")
            else:
                cv.yview_scroll(-3 if event.delta > 0 else 3, "units")
        except Exception:
            pass
        return "break"

    # ---------- ★★ 2026-10-07 新增：预览区的**缩放 / 拖动** ----------
    def zoom_by(self, factor):
        """按倍数缩放预览内容（factor > 1 放大，< 1 缩小）。

        ★ 只能主线程调。★ 会自动把"用户缩放"钉在 0.2~8.0 之间。
        """
        try:
            cur = float(getattr(self, "_user_zoom", 1.0) or 1.0)
        except Exception:
            cur = 1.0
        new = max(0.2, min(8.0, cur * float(factor)))
        if abs(new - cur) < 1e-6:
            return
        self._user_zoom = new
        try:
            self._img_relayout()
        except Exception as _e:
            try:
                note_swallowed(T("预览缩放失败"), _e, quiet=True)
            except Exception:
                pass
        # 缩放条上的百分数也要跟着变
        try:
            self._zoom_label_update()
        except Exception:
            pass
        # 状态栏给个反馈（用户要知道现在几倍）
        try:
            self.set_status(T("预览缩放：{x}", x="%d%%" % round(new * 100)))
        except Exception:
            pass
        # 缩放之后，滚动位置尽量**保持在原来的地方**
        try:
            self._keep_view_after_zoom()
        except Exception:
            pass

    def zoom_reset(self):
        """把缩放恢复到 100%（"适应窗格"那个默认状态）。"""
        self._user_zoom = 1.0
        try:
            self._img_relayout()
        except Exception:
            pass
        try:
            self._zoom_label_update()
        except Exception:
            pass
        try:
            self.set_status(T("预览缩放：100%（适应窗格）"))
        except Exception:
            pass

    def _keep_view_after_zoom(self):
        """缩放后**尽量停在原来看到的位置**（按比例换算滚动条）。

        ★ 为什么需要：不这么做的话，一缩放滚动条就跳回顶部/最左，
          看第 50 页的时候按一下放大就回到第 1 页了，很难用。
        """
        cv = getattr(self, "_img_cv", None)
        if cv is None:
            return
        try:
            fx = cv.xview()[0]
            fy = cv.yview()[0]
        except Exception:
            return
        # 立刻重排完再定位（重排会改 scrollregion）
        try:
            cv.update_idletasks()
        except Exception:
            pass
        try:
            cv.xview_moveto(max(0.0, min(1.0, fx)))
            cv.yview_moveto(max(0.0, min(1.0, fy)))
        except Exception:
            pass

    def _img_pan_press(self, event):
        """按住**空格**（或点中键）时，在预览区按下 = 开始拖动。"""
        try:
            if not (getattr(self, "_preview_space_down", False) or
                    getattr(event, "num", None) == 2):
                return None
        except Exception:
            return None
        self._preview_pan_active = True
        self._preview_pan_last = (event.x, event.y)
        try:
            self._img_cv.configure(cursor="fleur")
        except Exception:
            pass
        return "break"

    def _img_pan_motion(self, event):
        if not getattr(self, "_preview_pan_active", False):
            return None
        last = getattr(self, "_preview_pan_last", None)
        if last is None:
            return None
        dx = event.x - last[0]
        dy = event.y - last[1]
        self._preview_pan_last = (event.x, event.y)
        cv = getattr(self, "_img_cv", None)
        if cv is None:
            return "break"
        try:
            # ★ 用 xview_scroll 的 "units" —— 一格默认很小，
            #   这里按像素换成格数（一格≈1/10 视口），手感接近"跟手"。
            cv.xview_scroll(-dx // 3, "units")
            cv.yview_scroll(-dy // 3, "units")
        except Exception:
            pass
        return "break"

    def _img_pan_release(self, event=None):
        self._preview_pan_active = False
        try:
            self._img_cv.configure(cursor="")
        except Exception:
            pass
        return "break"

    def _preview_space(self, event, down=True):
        """空格按下/抬起 —— 决定"能不能拖着走"，并换光标提示用户。"""
        try:
            self._preview_space_down = bool(down)
        except Exception:
            return None
        cv = getattr(self, "_img_cv", None)
        if cv is not None:
            try:
                cv.configure(cursor="fleur" if down else "")
            except Exception:
                pass
        # ★ 返回 "break" —— 不然空格会被当成"翻页/滚动"的默认行为
        return "break"

    def _img_refit(self):
        """窗口大小变了：按新宽度重排/重画图片。

        ★★ 2026-10-06 改（**治「拉预览区特别卡」**）★★
           用户反馈：「能拉伸但特别卡」。
           原因：上一版在这里加了一句「宽度变了就**重新渲染整个 PDF**」——
           而**拖动窗格的时候，宽度是每毫秒都在变的**，
           于是每动一下就把几百页全部重新渲染一遍 → **卡死**。
           ★ 正确做法（外面成熟软件都是这么干的）：
             ① **拖的当下**：只把已有的图**快速拉伸**一下（几乎不耗时），
                让你立刻看到宽度在变 —— 视觉上跟手。
             ② **停手之后**：等 700 毫秒没有新动静，**再重新渲染**一遍，
                把清晰的图换上（这时候只渲染「看得见的那几页」，很快）。
           这样「拖的时候跟手、松手之后变清晰」，两头都不耽误。
        """
        cv = getattr(self, "_img_cv", None)
        if cv is None or not cv.winfo_ismapped():
            return
        # ① 立刻：把现有的图按新宽度**快速拉伸**（不重新渲染，快）
        try:
            self._img_quick_rescale()
        except Exception as _e:
            note_swallowed(T("预览：快速拉伸失败"), _e, quiet=True)
        # ② 停手 700 毫秒后：再重新渲染一遍（要清晰）
        try:
            if getattr(self, "_pdf_scroll_path", None):
                if getattr(self, "_pdf_rerender_job", None) is not None:
                    try:
                        self.root.after_cancel(self._pdf_rerender_job)
                    except Exception:
                        pass

                def _later():
                    self._pdf_rerender_job = None
                    try:
                        self._pdf_rerender_if_needed()
                    except Exception:
                        pass

                self._pdf_rerender_job = self.root.after(700, _later)
        except Exception:
            pass

    def _img_quick_rescale(self):
        """★ 把画布上已有的图**按新宽度快速拉伸**（不重新渲染，很快）。

        ★ 用途：拖窗格的时候用它 —— 要的是「跟手」，
          不是「清晰」。停手之后再由 `_pdf_rerender_if_needed` 补清晰版。
        ★ 只处理**看得见的那些页** —— 几百页全处理还是会卡。
        """
        cv = getattr(self, "_img_cv", None)
        if cv is None:
            return
        try:
            avail = max(160, int(cv.winfo_width()) - 12)
        except Exception:
            return
        # 现在滚到哪儿了（只重排看得见的一段，外加前后各一屏的余量）
        try:
            top = int(cv.canvasy(0))
            vh = int(cv.winfo_height()) or 600
        except Exception:
            top, vh = 0, 600
        _allow_zoom = bool(getattr(self, "_img_allow_zoom", False))
        _zmax = 3.0 if _allow_zoom else 1.0
        try:
            from PIL import ImageTk  # type: ignore
        except Exception:
            return
        for key, rec in (self._img_items or {}).items():
            im = rec.get("pil")
            if im is None:
                continue
            y0 = rec.get("y", 0)
            h0 = rec.get("h", 0)
            # 离得远的页先跳过（省时间）
            if h0 and (y0 + h0 < top - vh or y0 > top + 2 * vh):
                continue
            try:
                iw, ih = im.size
                k = min(_zmax, avail / max(iw, 1))
                w, h = int(iw * k), int(ih * k)
                if w < 1 or h < 1:
                    continue
                rec["photo"] = ImageTk.PhotoImage(
                    im.resize((w, h)) if (w, h) != im.size else im)
                self._img_photos[key] = rec["photo"]
                if rec.get("item") is not None:
                    cv.itemconfigure(rec["item"], image=rec["photo"])
            except Exception:
                continue

    def _pdf_rerender_if_needed(self):
        """★★ 2026-10-06：预览区宽度变了 → **按新宽度重新渲染 PDF**。

        ★ 为什么要重渲染而不是简单拉伸：
          原来那张图是按「旧宽度」渲染出来的。直接放大只是把像素拉大，
          **字会糊**。重新渲染才是清晰的 —— 这正是用户要的
          「跟着预览区的拉伸一起适应」。
        ★ 防抖：宽度只变了几个像素就不折腾（免得拖窗格时狂渲染）。
        ★ 用户换了文件 / 换了一本 PDF → 靠 _content_tag 作废，不白干。
        """
        path = getattr(self, "_pdf_scroll_path", None)
        if not path:
            return False
        cv = getattr(self, "_img_cv", None)
        if cv is None:
            return False
        try:
            new_w = max(200, int(cv.winfo_width()) - 18)
        except Exception:
            return False
        old_w = int(getattr(self, "_pdf_render_width", 0) or 0)
        # ★ 防抖：宽度变化小于 60 像素就不重排（否则拖动窗格会疯狂渲染）
        if old_w and abs(new_w - old_w) < 60:
            return False
        # ★★ 2026-10-06：**只重渲染「用户现在看得见的那几页」**。
        #   几百页全部重排 = 卡死。用户其实只看得见一两页，
        #   所以只把看得见的那几页重渲染成清晰版就行，
        #   别的页等他滚过去的时候再说。
        #   （这个「只排看得见的」做法，外面那些成熟的看图/看 PDF
        #     软件都是这么干的。）
        old_w_bak = old_w
        try:
            self._pdf_render_width = new_w
            # 找出当前看得见的页
            cv2 = self._img_cv
            top = int(cv2.canvasy(0))
            vh = int(cv2.winfo_height()) or 600
            visible = []
            for key, rec in (self._img_items or {}).items():
                y0 = rec.get("y", 0)
                h0 = rec.get("h", 0) or 800
                if y0 + h0 >= top - vh and y0 <= top + 2 * vh:
                    visible.append(key)
            if not visible:
                return False
            import threading as _th

            _path = path
            _size = getattr(self, "_pdf_scroll_size", "?")
            _mt = getattr(self, "_pdf_scroll_mtime", "?")
            _tag = int(getattr(self, "_content_tag", 0))
            _w = new_w
            _keys = list(visible)

            def _work():
                # ★★ 2026-10-06 ★★ 这条路以前也是**会卡死界面**的：
                #   它在后台重新渲染完之后，用 `self._ui(_apply)` 去抢 Tcl
                #   贴图。用户切文件切得快时，就和主线程撞上了。
                #   现在改成：开文件、读页数在主线程（带超时），
                #   渲染在后台，结果用 `_bg_post` 排队 —— 一步 Tcl 都不碰。
                doc = None
                try:
                    doc, n = pdf_prepare(_path, timeout=3.0)
                    if doc is None:
                        return
                    got = {}
                    for k in _keys:
                        im = render_pdf_page(doc, int(k), max_w=_w, max_h=1200)
                        if im is not None:
                            got[k] = im
                    if not got:
                        return
                    if int(getattr(self, "_content_tag", 0)) != _tag:
                        return      # 用户已经看别的文件了 → 白干，扔掉

                    def _apply_safe(items=dict(got)):
                        if int(getattr(self, "_content_tag", 0)) != _tag:
                            return
                        for k, im in items.items():
                            rec = (self._img_items or {}).get(k)
                            if rec is None:
                                continue
                            rec["pil"] = im
                        try:
                            self._img_relayout()
                        except Exception:
                            pass
                    _bg_post(_apply_safe)
                except Exception as _e:
                    try:
                        note_swallowed(T("预览：重排可见页失败"), _e, quiet=True)
                    except Exception:
                        pass
                finally:
                    try:
                        if doc is not None:
                            doc.close()
                    except Exception:
                        pass

            _th.Thread(target=_work, daemon=True, name="PDF重排可见页").start()
            return True
        except Exception as _e:
            self._pdf_render_width = old_w_bak
            note_swallowed(T("预览：重排 PDF 可见页失败"), _e, quiet=True)
            return False

    def _img_relayout(self):
        cv = getattr(self, "_img_cv", None)
        if cv is None:
            return
        try:
            avail = max(160, int(cv.winfo_width()) - 12)
        except Exception:
            avail = 400
        y = 0
        gap = int(getattr(self, "_img_gap", 8) or 0)   # ★ 补丁39：无缝模式 gap=0
        # ★★ 2026-10-06：图片/PDF 要不要**跟着窗格放大**。
        #   用户原话：「我给 .pdf、.png、gif 之类的文档、图片弄个放大、
        #   缩小、拖动的显示选项」；并且反馈「.pdf 里的内容不会跟着预览区
        #   被拉伸的状态一起进行适应性显示」。
        #   以前这里写的是 `k = min(1.0, avail / iw)` —— **只能缩小、
        #   不能放大**，所以窗格拉宽了 PDF 还是原来那么大。
        #   现在：单张图（图片/PDF 单页）**可以放大**，最大到 3 倍；
        #   多页（PDF 连续滚动）**默认仍保持「不放大」**——
        #   因为几百页一起放大，内存吃不消，而且滚动会变得很累。
        #   这两种行为用一个开关控制：self._img_allow_zoom。
        _allow_zoom = bool(getattr(self, "_img_allow_zoom", False))
        _zmax = 3.0 if _allow_zoom else 1.0
        # ★★ 2026-10-07 新增：**用户自己按的缩放倍数**（Ctrl+滚轮 / Ctrl± / ➕➖ 图标）。
        #   用户要求：「我想给空格预览和右侧预览区都加上放大放小和手势拖动」。
        #   ★ 和上面那个 `_zmax`（"跟不跟着窗格自适应"）是**两码事**：
        #     · `_zmax` 决定"窗格拉宽时图片跟不跟着变大"（自动）
        #     · `_user_zoom` 是用户**手动**按出来的倍数（1.0 = 原始）
        #   两者相乘：最终倍数 = 自适应倍数 × 用户倍数。
        #   ★ 范围 0.2 ~ 8.0 —— 太小看不清、太大内存吃不消。
        try:
            _uz = float(getattr(self, "_user_zoom", 1.0) or 1.0)
        except Exception:
            _uz = 1.0
        _uz = max(0.2, min(8.0, _uz))
        for key, rec in sorted((self._img_items or {}).items(),
                               key=lambda kv: kv[1].get("order", 0)):
            im = rec.get("pil")
            if im is None:
                continue
            try:
                iw, ih = im.size
                # ★ 关键：min(_zmax, ...) —— _zmax=1.0 时只能缩；
                #   _zmax=3.0 时最多放大到 3 倍。
                #   ★★ 后面再乘 `_uz`（用户手动倍数）——
                #     用户放大时**要把 _zmax 的上限放开**，
                #     否则"多页 PDF 不放大"那条规矩会把用户的缩放吃掉。
                k = min(_zmax, avail / max(iw, 1)) * _uz
                w, h = int(iw * k), int(ih * k)
                if w < 1 or h < 1:
                    continue
                # ★ 保护：一页别画成几万像素（几百页会瞬间吃光内存）
                if w > 12000 or h > 12000:
                    continue
            except Exception:
                continue
            try:
                from PIL import ImageTk  # type: ignore
                rec["photo"] = ImageTk.PhotoImage(
                    im.resize((w, h)) if (w, h) != im.size else im)
                self._img_photos[key] = rec["photo"]
                if rec.get("item") is None:
                    rec["item"] = cv.create_image(6, y, anchor="nw",
                                                  image=rec["photo"])
                else:
                    cv.itemconfigure(rec["item"], image=rec["photo"])
                    cv.coords(rec["item"], 6, y)
                rec["h"] = h
                rec["w"] = w
                rec["y"] = y          # ★ 记住每页的位置（快速拉伸要用）
            except Exception:
                continue
            y += h + gap
        try:
            cv.configure(scrollregion=(0, 0, max(200, avail + 12), max(y, 100)))
        except Exception:
            pass
        # ★★ 2026-10-06：每次重排完，**顺手把「预览信箱」里排着的活儿干一遍**。
        #   为什么：预览的后台渲染（PDF 页数、图片、电子书）干完活把结果
        #   排在信箱里；本来只靠预览自己的 200 毫秒小闹钟去取。
        #   万一那个小闹钟没转起来（启动分支不同、别的窗口抢了定时器…），
        #   预览区就会一直停在「正在打开…」，页面永远不出来。
        #   现在多一条腿：只要有人在画预览，就一定顺手取一次快递。
        try:
            _drain_ui_mail(80)
        except Exception:
            pass

    def _show_pil_image(self, pil_image, size="?", mtime="?"):
        """把一张 PIL 图显示在滚动画布里（PDF / 图片共用）。

        ★★ 2026-10-06：**单张图允许跟着窗格放大**（用户要求
           「给 .pdf、.png、gif 之类的文档、图片弄个放大、缩小的显示选项」）。
           单个图片放大没负担，而且正是用户要的效果。
        """
        cv = self._img_canvas()
        self._show_img()
        try:
            self._img_cv_sb.pack(side="right", fill="y")
            cv.pack(side="left", fill="both", expand=True)
            self._img_box.pack(fill="both", expand=True)
        except Exception:
            pass
        self._img_items = {0: {"pil": pil_image, "item": None, "order": 0}}
        self._img_photos = {}
        # ★ 补丁39：单张图模式 —— 间隔归 0（不留缝）
        self._img_gap = 0
        # ★★ 单张图：**允许放大**（只影响这一张，不影响 PDF 多页那种）
        self._img_allow_zoom = True
        try:
            cv.delete("all")
        except Exception:
            pass
        self._img_relayout()
        return cv

    # ---------- ★ v25 补丁39：PDF「连续滚动」模式 ----------
    def _show_pdf_scroll(self, path, size="?", mtime="?"):
        """把 PDF **所有页竖着排成一长条**，鼠标滚轮一路往下看，页与页无缝。

        ★ 用户提的：「PDF 不应该点上一页下一页，应该能鼠标滚动看每一页、
          而且一页接着一页没有空隙」—— 就是浏览器看 PDF 那种感觉。
        做法：一次渲染前 N 页（N 由 _PDF_SCROLL_MAX 控制），按顺序画到
        现有的滚动画布上，间隔设成 0。
        如果页数很多，会先画前面一批，并在页脚写一句提示。

        ★★ 2026-10-06：**取消「只能先排前 60 页」的上限** ★★
           用户要求：「这样不用卡 60 页的上限，可以全部显示上去」。
           敢取消的原因（实测数据，用户网盘 555MB / 340 页的 PDF）：
             · 打开文档 1.34 秒
             · 渲染一页 0.08 秒（连着渲染 5 页只要 0.09 秒）
             · 跳到第 301 页渲染 0.15 秒
           也就是说 340 页全排完大约几秒钟，**完全排得起**。
           ★ 但安全措施一个都不能少（以前那 60 页就是为了防卡死）：
             · 仍然是「先渲染第 1 页 → 立刻显示 → 其余丢后台线程慢慢排」；
             · 后台每排好一页就贴一页（**边看边补**，不是等全部排完）；
             · 用户换文件就靠 _content_tag / _pdf_bg_cancel 作废这次；
             · 加了 `_PDF_SCROLL_ALL_MAX` 这个**超大保险**：
               页数超过它才截断（默认 1000 页）——
               这是防止「几千页的巨无霸」把内存吃光，不是嫌 340 页多。
        """
        if not HAS_FITZ or not HAS_PIL:
            self._show_pdf_missing()
            return
        # ★★ 2026-10-06 修「切到网盘 PDF 时卡死 + 重开后不预览」★★
        #   病根：**「打开这个 PDF」原来是在主线程里同步做的**。
        #   实测用户网盘上那本 PDF：`pymupdf.open()` 最慢 6.5 秒，
        #   这 6.5 秒里整条界面都是死的 —— 鼠标点不动、窗都关不掉，
        #   只能强杀（用户就是这么干的，然后程序留下了半死不活的状态）。
        #   ★ 现在：**开文件这件事本身也丢后台**（后台开、后台读页数、
        #     后台渲染第一页），主线程这边一步都不等，先把
        #     「正在打开…」写上去。实测：切一个网盘 PDF，主线程**瞬间返回**。
        #   ★ 后开的窗口优先（见下面 _open_bg 里那个序号判断）——
        #     切得快的时候，先点的那个不会再把后点的挤掉。
        self._pdf_open_seq = int(getattr(self, "_pdf_open_seq", 0)) + 1
        _open_seq = self._pdf_open_seq
        cv = self._img_canvas()
        self._show_img()
        self._show_nav("PDF", lambda: self._pdf_scroll_by(-1),
                       lambda: self._pdf_scroll_by(1))
        try:
            self._img_cv_sb.pack(side="right", fill="y")
            cv.pack(side="left", fill="both", expand=True)
            self._img_box.pack(fill="both", expand=True)
            cv.delete("all")
        except Exception:
            pass
        # 每页渲染成 PIL 图（页宽按画布宽度）
        try:
            w = max(200, int(cv.winfo_width()) - 18)
        except Exception:
            w = 420
        self._img_items = {}
        self._img_photos = {}
        self._img_gap = 0            # ★ 无缝：页间距 0
        # ★★ 2026-10-06：**多页 PDF 保持「不放大」**（只缩小、不放大）。
        #   原因：一次排几百页，如果每页都跟着窗格放大，内存和滚动都会很难受。
        #   （单张图片 / 单页 PDF 是允许放大的，见 _show_pil_image。）
        self._img_allow_zoom = False
        self._pdf_scroll_path = path
        self._pdf_scroll_size = size
        self._pdf_scroll_mtime = mtime
        try:
            self._pdf_render_width = int(cv.winfo_width()) - 18
        except Exception:
            self._pdf_render_width = 0
        self._pdf_bg_cancel = getattr(self, "_pdf_bg_cancel", 0) + 1
        _bg_tag = self._pdf_bg_cancel
        _ct_tag = int(getattr(self, "_content_tag", 0))
        self._pdf_scroll_total = 0
        self._pdf_scroll_got = 0
        try:
            self.kind_lbl.configure(
                text=T("PDF · 正在打开… · {x}", x=size))
        except Exception:
            pass

        def _open_bg():
            """（后台线程）开文件 → 读页数 → 渲染第一页 → 排队回主线程贴。

            ★ 这个线程里**一个界面控件都不碰**（碰了就会和主线程抢 Tcl，
              用户切得快的时候整个程序会冻死），只往信箱里排队。
            """
            alive = (lambda: (getattr(self, "_pdf_open_seq", 0) == _open_seq
                              and getattr(self, "_pdf_bg_cancel", 0) == _bg_tag
                              and getattr(self, "_content_tag", 0) == _ct_tag))
            doc = None
            try:
                if not alive():
                    return
                try:
                    doc = _fitz_mod.open(path)
                except Exception:
                    doc = None
                if doc is None:
                    if alive():
                        _bg_post(_opened_fail)
                    return
                try:
                    total = int(doc.page_count)
                except Exception:
                    total = 0
                if total <= 0:
                    try:
                        doc.close()
                    except Exception:
                        pass
                    if alive():
                        _bg_post(_opened_fail)
                    return
                # ★ 先渲染第一页（这个要 1~3 秒，正是以前卡主线程的元凶）
                im0 = render_pdf_page(doc, 0, max_w=w, max_h=900)
                if not alive():
                    return
                limit = min(total, self._PDF_SCROLL_MAX)
                _bg_post(_opened_ok, total, im0)
                # 接着排第 2..N 页
                self._pdf_bg_render_each(path, w, limit, (_bg_tag, _ct_tag),
                                         doc)
            except Exception as _e:
                try:
                    note_swallowed(T("PDF 预览：打开失败（这次没显示出来）"), _e,
                                   quiet=True)
                except Exception:
                    pass
                if alive():
                    _bg_post(_opened_fail)
            finally:
                try:
                    if doc is not None:
                        doc.close()
                except Exception:
                    pass

        def _opened_ok(total, im0):
            if (getattr(self, "_pdf_open_seq", 0) != _open_seq
                    or getattr(self, "_pdf_bg_cancel", 0) != _bg_tag):
                return
            self._pdf_scroll_total = total
            try:
                self._nav_info.config(text=T("连续滚动 · 共 {x} 页", x=total))
            except Exception:
                pass
            if im0 is not None:
                self._img_items[0] = {"pil": im0, "item": None, "order": 0}
                self._pdf_scroll_got = 1
                self._img_relayout()
            try:
                # ★★ 2026-10-07 简化（用户要求）：
                #   原来这一行是「PDF 连续滚动 · 共 103 页（后面几页正在后台
                #   加载…）· 10.2 MB」—— 太啰嗦，字号又小，看着像一堆乱码。
                #   用户原话：「感觉只保留 <文件名> + 正在后台加载… 就可以了」。
                #   所以这里**只留一句状态**，页数等信息不塞这儿
                #   （文件名在下面 name_lbl 上，别重复）。
                self.kind_lbl.configure(text=T("正在后台加载…"))
            except Exception:
                pass

        def _opened_fail():
            if (getattr(self, "_pdf_open_seq", 0) != _open_seq
                    or getattr(self, "_pdf_bg_cancel", 0) != _bg_tag):
                return
            self._show_text(self._unreadable_text(
                path, size, mtime,
                "这个 PDF 打不开。常见原因：文件加密 / 受保护、"
                "下载没下完（损坏）、网盘这会儿太慢、"
                "或者是个「假 PDF」（改过扩展名）。\n"
                "要重试，点下面的「🔄 重新加载」。"))

        threading.Thread(target=_open_bg, daemon=True,
                         name="PDF打开").start()

        # ★★ 2026-10-06：**「回到顶部 / 重新加载」这两个按钮放最后、单独包起来**。
        #   原来它们排在中间，前面一旦出岔子被 except 吞掉，
        #   这一段就整段不执行 —— 用户看到的就是「两个按钮不见了」。
        #   现在：挪到所有可能出错的活儿后面，而且两个按钮各自独立包 try，
        #   坏一个不影响另一个。（这一版把它们**一定**摆出来。）
        try:
            self._nav_prev.configure(
                text=T("⬆ 回到顶部"), width=11, state="normal",
                command=self._pdf_back_to_top)
            self._nav_prev.pack(side="left")
        except Exception as _e:
            note_swallowed(T("预览：摆『回到顶部』按钮失败"), _e, quiet=True)
        try:
            self._nav_next.configure(
                text=T("🔄 重新加载"), width=11, state="normal",
                command=self._pdf_reload)
            self._nav_next.pack(side="left", padx=(6, 0))
        except Exception as _e:
            note_swallowed(T("预览：摆『重新加载』按钮失败"), _e, quiet=True)
        return

    def _pdf_bg_done_label(self, got, total):
        """（主线程）后台把能排的页都排完了 → 把标题改成实话。

        ★★ 2026-10-07 简化（用户要求）：原来写的是
          「PDF 连续滚动 · 共 103 页 · 已排前 40 页（为了避免占太多内存
            没有全排；想看全本双击用系统默认程序打开）」
        —— 一大串，把用户不需要的"为什么"也塞进来了。
        现在只留一句**实话**，其余（怎么打开全本）已经在下面 `_nav_info`
        那儿常驻提示了，不重复。"""
        try:
            if total and got < total:
                self.kind_lbl.configure(text=T("已显示前 {x} 页", x=got))
            else:
                self.kind_lbl.configure(text=T("已全部排好"))
        except Exception:
            pass

    def _pdf_bg_render_each(self, path, width, limit, tag, doc):
        """（**后台线程**）用**已经开好的 doc** 把第 2..N 页排好、排队贴上去。

        ★★ 2026-10-06 新增。和老的 `_pdf_bg_render` 的区别：
          · 老的会**自己再开一次文件**（网盘上就是又等 1~6 秒）——
            现在开文件的那一步已经在同一个线程里做完了，直接用；
          · 老的每一页都 `self._ui(...)` 抢 Tcl（这是卡死的元凶），
            现在改成**攒 50 页一批**用 `_bg_post` 排队（纯列表操作）。
        ★ 这个函数里**一个界面控件都不许碰**。doc 由调用方负责关。
        """
        batch = {}
        BATCH_MAX = 50
        idx = 1

        def flush():
            nonlocal batch
            if not batch:
                return
            _items = dict(batch)
            batch = {}
            # ★ 一句话：**后台线程只准读数据、算东西，一个界面控件都不许碰。**
            #   （以前这里每页都调 self._ui(...) 抢 Tcl，用户切文件切得快时
            #     后台线程和主线程撞上 → 整个程序冻死。
            #     现在只往 Python 列表里排队 —— 纯列表操作，永远不会卡住。）
            _w = width

            def _apply_safe(items=_items, ww=_w):
                for kk, img in items.items():
                    try:
                        if int(kk) < int(getattr(self, "_pdf_scroll_got", 0)):
                            continue
                        self._img_items[kk] = {"pil": img, "item": None,
                                               "order": kk}
                        self._pdf_scroll_got = kk + 1
                    except Exception:
                        continue
                try:
                    self._img_relayout()
                except Exception:
                    pass
                try:
                    self._pdf_render_width = max(200, ww)
                except Exception:
                    pass

            if self._pdf_alive(tag):
                _bg_post(_apply_safe)

        try:
            n_pages = int(doc.page_count)
            for i in range(1, min(limit, n_pages)):
                if not self._pdf_alive(tag):
                    return
                im = render_pdf_page(doc, i, max_w=width, max_h=900)
                if im is None:
                    continue
                batch[idx] = im
                idx += 1
                if len(batch) >= BATCH_MAX:
                    flush()
                    try:
                        import time as _t
                        _t.sleep(0.005)
                    except Exception:
                        pass
            flush()
            if self._pdf_alive(tag):
                _bg_post(self._pdf_bg_done_label, int(idx),
                         int(getattr(self, "_pdf_scroll_total", 0) or 0))
        except Exception as _e:
            try:
                note_swallowed(T("PDF 后台渲染出错（可能后面几页没排上）"), _e,
                               quiet=True)
            except Exception:
                pass

    def _pdf_alive(self, tag):
        """这次后台渲染还算不算数（用户换文件 / 换 PDF 了就作废）。"""
        try:
            return (getattr(self, "_pdf_bg_cancel", 0) == tag[0]
                    and getattr(self, "_content_tag", 0) == tag[1])
        except Exception:
            return False

    def _pdf_bg_render(self, path, width, limit, start_index, tag):
        """★★ v26（2026-10-01）：**在后台线程里把 PDF 第 2..N 页渲染出来。**

        ★★ 2026-10-06：这条路**已经不是主力了** —— 主力是
          `_pdf_bg_render_each`（用主线程那边已经开好的文档，省掉再开一次）。
          这个函数只作兜底用（比如别处直接调它），行为照旧但改安全了。
        """
        try:
            import threading as _th
        except Exception:
            return False
        root = None
        try:
            root = self.winfo_toplevel()
        except Exception:
            return False

        def worker():
            # ★★ 2026-10-06 ★★ 这里就是**把界面卡死的真凶**：
            #   原来每渲染好一页就调 `self._ui(apply)` 去抢 Tcl。
            #   现在改成自己开文件（后台开，不碰界面）+ 攒批复用
            #   `_pdf_bg_render_each` 里那套安全写法。
            doc = None
            try:
                try:
                    doc = _fitz_mod.open(path)
                except Exception:
                    return
                self._pdf_bg_render_each(path, width, limit, tag, doc)
            except Exception:
                return
            finally:
                try:
                    if doc is not None:
                        doc.close()
                except Exception:
                    pass

        try:
            t = _th.Thread(target=worker, daemon=True,
                           name="pdf-bg-render")
            t.start()
            return True
        except Exception:
            return False

    def _pdf_back_to_top(self):
        """★★ 2026-10-06：PDF 几百页翻到一半，一下回到最顶上。

        （取代了原来那个没用的「上/下一页」按钮 —— 用户说
          「有两个上下页按钮，感觉没用，不如刷新」。）
        """
        try:
            cv = getattr(self, "_img_cv", None)
            if cv is not None:
                cv.yview_moveto(0.0)
                cv.xview_moveto(0.0)
                self.set_status(T("已回到 PDF 顶部"))
        except Exception as _e:
            note_swallowed(T("预览：回到 PDF 顶部失败"), _e, quiet=True)

    def _pdf_reload(self):
        """★★ 2026-10-06：重新加载当前 PDF（用户要的「刷新」）。

        什么时候用：万一显示不对 / 排了一半没排完 / 网盘刚才卡了一下。
        作用就是「把当前这个 PDF 从头再排一遍」。
        """
        try:
            p = getattr(self, "_pdf_scroll_path", None) or self.current_path
            if not p:
                self.set_status(T("现在没有正在看的 PDF"))
                return
            self.set_status(T("正在重新加载 PDF…"))
            self.show_path(p)
        except Exception as _e:
            note_swallowed(T("预览：重新加载 PDF 失败"), _e)

    # ★★ 2026-10-07 新增：**PreviewPane 自己的 set_status**。
    #
    #   账本抓到：`AttributeError: 'PreviewPane' object has no attribute
    #   'set_status'` —— 「重新加载 PDF」直接没反应。
    #
    #   原因：预览窗这段代码里写了 `self.set_status(...)`（共 3 处：
    #   回到顶部 / 没有 PDF / 正在重载），但 `set_status` 是**主程序
    #   （FileTaggerApp）的方法，PreviewPane 里根本没有**。
    #   → 一调用就抛 AttributeError，被 except 吞掉，
    #     用户看到的就是「点了没反应，状态栏也不提示」。
    #
    #   ★ 修法：在 PreviewPane 里补一个**转发**，把话传给主程序去显示。
    #     转发时**全程包 try** —— 万一 app 没挂上（比如单独测这个类），
    #     也不能因为它没反应而把预览功能带崩。
    def set_status(self, text):
        """把状态提示转给主程序显示（本类自己没有状态栏）。"""
        try:
            app = getattr(self, "app", None)
            if app is not None and hasattr(app, "set_status"):
                app.set_status(text)
                return
        except Exception:
            pass
        try:
            print("[预览] %s" % text)
        except Exception:
            pass

    def _pdf_scroll_by(self, pages):
        """点翻页按钮时的兜底：按「当前页高」滚一屏。"""
        cv = getattr(self, "_img_cv", None)
        if cv is None:
            return
        # 算一页大概多高（第一页的高 + 间距）
        h = 800
        try:
            rec = (self._img_items or {}).get(0)
            if rec:
                h = int(rec.get("h") or 800)
        except Exception:
            pass
        try:
            cv.yview_scroll(int(pages) * max(1, h) // 20, "units")
        except Exception:
            pass

    def _show_nav(self, info, on_prev, on_next):
        """显示翻页条（用 side=bottom 贴底，别被上边的图片/文字挡住）。"""
        try:
            self._nav_info.config(text=info)
            self._nav_prev.configure(command=on_prev)
            self._nav_next.configure(command=on_next)
            self.nav_bar.pack(side="bottom", fill="x", pady=(2, 0))
        except Exception:
            pass

    # ---------------- 内部：两种显示方式 ----------------
    def _show_text(self, s):
        # ★ 补丁30：统一走 _show_body()，不再各处自己 pack/pack_forget
        self._show_body()
        try:
            self.text.configure(state="normal")
            self.text.delete("1.0", "end")
            self.text.insert("1.0", s)
            self.text.configure(state="disabled")
        except Exception:
            pass

    def _show_image(self, path):
        # ★ 补丁37：用程序自己探测好的 HAS_PIL，别在这里直接 import ——
        #   Pillow 装在程序目录的 libs 里，直接 import 会失败，
        #   结果每个 PDF / 图片都被误判成「没装库」。
        if not HAS_PIL:
            self._show_text(T("（这台机器没装 Pillow，看不了图片缩略图）"))
            return
        try:
            from PIL import Image, ImageTk  # type: ignore
        except Exception:
            self._show_text("（这台机器没装 Pillow，看不了图片缩略图）")
            return
        try:
            im = Image.open(path)
            # ★★★ 2026-01-26：窗格宽度自适应（跟随 _on_pane_configure 的 _wrap_w）
            w = max(160, int(getattr(self, "_wrap_w", 0)) or (int(self.winfo_width()) - 30))
            if w < 160:
                w = 330
            im.thumbnail((w, 460))
            # ★ 补丁37：走画布贴图（Label 那条路在你机器上贴不出来）
            self._show_pil_image(im)
            self._photo = self._img_photos.get(0)
        except Exception as exc:
            self._show_text(T("（这张图打不开：{x}）", x=exc))

    # ---------- ★ v25 补丁29：电子书预览（EPUB / MOBI / AZW3 / FB2） ----------

    BOOK_CHARS_PER_PAGE = 2600      # 一"页"大约多少字（阅读器那种感觉）
    # ★★ 2026-10-06：**取消「只排前 60 页」的限制**（用户要求「全部显示上去」）。
    #   原来这里写 `_PDF_SCROLL_MAX = 60`，超过 60 页的 PDF 后面就排不上了。
    #   实测（用户网盘 555MB / 340 页的 PDF）：打开 1.34 秒、渲染一页
    #   0.08 秒、跳到第 301 页 0.15 秒 —— 340 页全排完也就几秒钟，
    #   **根本不需要卡 60 页**。
    #   ★ 保险：改成 1000。这不是「嫌 340 页多」，是防「几千页的巨无霸」
    #     把内存吃光（每页都有一张 PIL 图留在内存里）。
    #     真要放开，把这个数字调大即可。
    _PDF_SCROLL_MAX = 1000

    def _book_pages(self, path):
        """把书切成"页"（按字数切，缓存在 self._book_cache 里免得反复解析）。"""
        cache = getattr(self, "_book_cache", None)
        if cache and cache.get("path") == path:
            return cache.get("pages") or [], cache.get("note") or ""
        title, chapters = book_load(path)
        note = ""
        if not chapters:
            note = ("这个电子书读不出来（可能是加密的 / 或者格式比较特殊）。\n"
                    "双击可以用系统里的阅读器打开。")
            self._book_cache = {"path": path, "pages": [], "note": note}
            return [], note
        text = "\n\n".join(chapters)
        per = self.BOOK_CHARS_PER_PAGE
        pages = [text[i:i + per] for i in range(0, len(text), per)] or [""]
        if title:
            note = "书名：%s" % title
        self._book_cache = {"path": path, "pages": pages, "note": note}
        return pages, note

    def _show_book(self, path, size="?", mtime="?"):
        """★ 补丁29：把电子书当长文本显示，带「上一页 / 下一页」翻页。"""
        pages, note = self._book_pages(path)
        if not pages:
            self._show_text(note or "（读不出来）")
            try:
                self.kind_lbl.configure(
                    text=T("电子书 · {a} · {b}", a=size, b=mtime))
            except Exception:
                pass
            return
        total = len(pages)
        pg = int(getattr(self, "_book_page", 0) or 0)
        if pg >= total:
            pg = total - 1
        if pg < 0:
            pg = 0
        self._book_page = pg
        ext = os.path.splitext(path)[1].lower().lstrip(".").upper()
        head = ("%s · %s · %s" % (ext, size, mtime))
        if note:
            head = note + " · " + head
        try:
            self.kind_lbl.configure(text=head)
        except Exception:
            pass
        body = pages[pg]
        self._show_text("【%d / %d】\n%s" % (pg + 1, total, body))
        # ★ 补丁30：翻页条改用 PreviewPane 自己那一条（PDF / 电子书共用），
        #   位置固定在底部，不会被正文挡住。
        self._show_nav(T("第 {a} / {b} 页", a=pg + 1, b=total),
                       lambda: self._book_goto(-1),
                       lambda: self._book_goto(1))
        # 翻页也能用左右方向键（焦点在预览里时）
        try:
            self.bind("<Left>", lambda e: self._book_goto(-1))
            self.bind("<Right>", lambda e: self._book_goto(1))
        except Exception:
            pass

    def _book_goto(self, delta):
        """★ v26：电子书翻页 —— 有本地副本时用本地副本（快）。"""
        try:
            self._book_page = max(0, int(getattr(self, "_book_page", 0)) + delta)
        except Exception:
            self._book_page = 0
        p = getattr(self, "_cur_path", None)
        if not p:
            return
        _local = (self._remote_tmp.get(p, p)
                  if hasattr(self, "_remote_tmp") else p)
        try:
            sz = fmt_size(os.path.getsize(_local))
        except Exception:
            sz = "?"
        try:
            mt = datetime.fromtimestamp(os.path.getmtime(_local)).strftime(
                "%Y-%m-%d %H:%M")
        except Exception:
            mt = "?"
        self._show_book(_local, sz, mt)

    def _show_pdf_missing(self):
        """★ v25 补丁37：没装渲染库时，给一句「怎么装」而不是「看不了」。"""
        if not HAS_FITZ:
            self._show_text(self._pdf_missing_text())
        elif not HAS_PIL:
            self._show_text("【PDF 预览不可用】\n"
                            "这台机器上没找到图像库（Pillow）。\n\n"
                            "怎么装：程序目录下执行\n"
                            "    python -m pip install pillow -t libs\n\n"
                            "装好后重开程序。")
        else:
            self._show_text("【PDF 预览不可用】\n"
                            "渲染库在，但这个 PDF 一页都画不出来。\n"
                            "双击可以用系统默认阅读器打开它。")

    def _show_pdf(self, path, size="?", mtime="?"):
        """PDF 预览。

        ★ 补丁39：默认改成**连续滚动**（所有页竖排、滚轮一路看、页间无缝）
        —— 用户提的「不应该点上一页下一页，应该能鼠标滚动看每一页、
        一页接着一页没有空隙」。想看单页那种，设 _pdf_mode = "single"。
        """
        # ★ 补丁37：这里**不要**先试 import PIL 来判断「有没有库」——
        #   Pillow 不在这台机器的 Python 里，而在程序自己的 libs 目录里，
        #   直接 import 会失败 → 于是每个 PDF 都被说成「没装 PyMuPDF」。
        #   判断要用程序自己探测好的 HAS_FITZ / HAS_PIL 标志。
        if not HAS_FITZ or not HAS_PIL:
            self._show_pdf_missing()
            return
        if getattr(self, "_pdf_mode", "scroll") == "scroll":
            self._show_pdf_scroll(path, size, mtime)
            return
        # ★★ 2026-10-06：单页模式也改成「**开文件、渲染全部丢后台**，
        #   主线程一步都不等**」。
        #   以前这里是主线程一口气「读页数 + 渲染第一页」，网盘上的 PDF
        #   实测要 6 秒以上，那几秒整条界面都是死的。
        page = int(getattr(self, "_pdf_page", 0) or 0)
        self._content_tag = int(getattr(self, "_content_tag", 0)) + 1
        _my_tag = self._content_tag
        try:
            self.kind_lbl.configure(text=T("PDF · 正在打开…"))
        except Exception:
            pass
        w = max(200, int(self.winfo_width()) - 30)

        def _work():
            """（后台线程）开文件 → 读页数 → 渲染这一页 → 排队回主线程。"""
            doc = None
            total = 0
            im = None
            try:
                try:
                    doc = _fitz_mod.open(path)
                except Exception:
                    doc = None
                if doc is not None:
                    try:
                        total = int(doc.page_count)
                    except Exception:
                        total = 0
                    if total > 0:
                        pg = page
                        if pg >= total:
                            pg = total - 1
                        if pg < 0:
                            pg = 0
                        im = render_pdf_page(doc, pg, max_w=w, max_h=520)
            except Exception:
                im = None
            finally:
                try:
                    if doc is not None:
                        doc.close()
                except Exception:
                    pass
            # ★ 后台线程**只往信箱里排**，一个界面控件都不碰（碰了会卡死）
            _bg_post(_done, total, im)

        def _done(total, im):
            if getattr(self, "_content_tag", 0) != _my_tag:
                return
            if total <= 0:
                self._show_text(self._unreadable_text(
                    path, size, mtime,
                    "这个 PDF 打不开。常见原因：文件加密 / 受保护、"
                    "下载没下完（损坏）、网盘这会儿太慢、"
                    "或者是个「假 PDF」（改过扩展名）。"))
                return
            if im is None:
                self._show_text(self._unreadable_text(
                    path, size, mtime,
                    "这个 PDF 有 %d 页，但第 %d 页画不出来"
                    "（可能这一页是坏的）。" % (total, page + 1)))
                return
            try:
                self.kind_lbl.configure(
                    text=T("PDF 第 {a} / {b} 页 · {c}",
                           a=min(page + 1, total), b=total, c=size))
            except Exception:
                pass
            try:
                self._show_pil_image(im)
                self._photo = self._img_photos.get(0)
            except Exception as exc:
                self._show_text(T("（画不出来：{x}）", x=exc))
                return
            # ★ 补丁30：翻页按钮改用 PreviewPane 自己那一条
            self._show_nav(T("第 {a} / {b} 页",
                                 a=min(page + 1, total), b=total),
                           lambda: self._pdf_goto(-1),
                           lambda: self._pdf_goto(1))

        threading.Thread(target=_work, daemon=True, name="PDF单页渲染").start()

    def _pdf_goto(self, delta):
        """★ 补丁28 / v26：PDF 翻页（只翻页、不重新读盘）。

        ★ v26：如果这个文件已经拷到本地缓存，翻页时用**本地副本** ——
          否则 os.path.getsize 走网盘又是几秒，翻页手感很差。
        """
        try:
            self._pdf_page = max(0, int(getattr(self, "_pdf_page", 0)) + delta)
        except Exception:
            self._pdf_page = 0
        p = getattr(self, "_cur_path", None)
        if not p:
            return
        _local = (self._remote_tmp.get(p, p)
                  if hasattr(self, "_remote_tmp") else p)
        try:
            sz = fmt_size(os.path.getsize(_local))
        except Exception:
            sz = "?"
        try:
            mt = datetime.fromtimestamp(os.path.getmtime(_local)).strftime(
                "%Y-%m-%d %H:%M")
        except Exception:
            mt = "?"
        self._show_pdf(_local, sz, mt)

    @staticmethod
    def _fmt_size(n):
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if n < 1024 or unit == "TB":
                return ("%d %s" % (n, unit)) if unit == "B" else ("%.1f %s" % (n, unit))
            n /= 1024.0

    def _read_text(self, path):
        """能当文本读就返回文字内容；明显是二进制返回 None。"""
        try:
            with open(path, "rb") as f:
                raw = f.read(self.MAX_READ + 1)
        except Exception as exc:
            return "（读不出来：%s）" % exc
        more = len(raw) > self.MAX_READ
        if more:
            raw = raw[:self.MAX_READ]
        if b"\x00" in raw[:4096]:
            return None
        txt = None
        for enc in ("utf-8", "gbk", "utf-16"):
            try:
                txt = raw.decode(enc)
                break
            except Exception:
                continue
        if txt is None:
            txt = raw.decode("utf-8", errors="replace")
        if more:
            txt += "\n\n……（文件太大，这里只显示前 %d KB）" % (self.MAX_READ // 1024)
        return txt

    def _info_text(self, path, size, mtime):
        """非文本 / 非图片：给一段文件信息（含它的标签）。"""
        lines = self._head_lines(path, size, mtime)
        lines.append("标签：%s" % ("、".join(self._tags_of(path)) or "（还没有标签）"))
        ext = os.path.splitext(path)[1].lower()
        if ext in (".docx", ".xlsx", ".pptx", ".zip", ".rar",
                   ".7z", ".mp4", ".mkv", ".mp3"):
            lines.append("")
            lines.append("这种文件没法直接预览，双击可以用系统默认程序打开。")
        return "\n".join(lines)

    # ---------- ★ v25 补丁37：三种「没内容」的原因分开说 ----------
    def _head_lines(self, path, size, mtime):
        return ["名称：%s" % os.path.basename(path),
                "路径：%s" % path,
                "大小：%s" % size,
                "修改时间：%s" % mtime,
                "类型：%s" % (os.path.splitext(path)[1].lower().lstrip(".")
                              or "无扩展名")]

    def _tags_of(self, path):
        tags = []
        try:
            app = self.app
            if app is not None and getattr(app, "store", None) is not None:
                mp = app.store.tags_for_paths([path]) or {}
                for item in (mp.get(path) or []):
                    if isinstance(item, (list, tuple)) and len(item) >= 2:
                        tags.append(str(item[1]))
                    else:
                        tags.append(str(item))
        except Exception:
            pass
        return tags

    def _pdf_missing_text(self):
        return ("【PDF 预览不可用】\n"
                "这台机器上没找到 PDF 渲染库（PyMuPDF）。\n\n"
                "怎么装：程序目录下执行\n"
                "    python -m pip install pymupdf -t libs\n\n"
                "装好后重开程序就能在预览窗格里看 PDF 了。\n"
                "（双击仍然可以用系统默认阅读器打开）")

    def _unreadable_text(self, path, size, mtime, why):
        lines = self._head_lines(path, size, mtime)
        lines.append("标签：%s" % ("、".join(self._tags_of(path)) or "（还没有标签）"))
        lines.append("")
        lines.append("【预览读不出内容】")
        lines.append(why)
        lines.append("")
        lines.append("双击可以用系统默认程序打开它。")
        return "\n".join(lines)

    def _book_load_async(self, path, size, mtime, local_path):
        """★★ 2026-10-06：**后台**解析网盘电子书，界面绝不卡。

        为什么需要：电子书要「解压 + 解析」，网盘上可能慢个一两秒。
        在主线程做会让界面发僵（用户最烦的就是卡）。
        所以丢后台线程，好了再回主线程显示（走安全信箱 `_ui`）。
        """
        _my_tag = int(getattr(self, "_content_tag", 0))
        try:
            self._show_text(T("正在读取电子书…\n{x}",
                                  x=os.path.basename(path)))
        except Exception:
            pass

        def _work():
            ok = False
            err = ""
            drm = ""
            try:
                # ★★ 2026-10-07 新增：先**查清楚它到底为什么读不出**，
                #   别再列一堆"常见原因"让用户猜。
                #   ★ 用户的原话（我实测确认过）：那份《大数据时代》epub
                #     报的是"常见原因：DRM 加密…"，可**程序自己也不知道**是哪种，
                #     就把三种可能都列出来了 —— **等于没说**（错题本 #68 那条：
                #     "做不到"要说清楚为什么，别让用户猜）。
                #   ★ 怎么查（3 行就够）：epub 本质是 zip，
                #     加密的 epub 里一定有 `META-INF/encryption.xml`，
                #     里面写着是谁加的锁（比如掌阅 ZhangYue / Adobe …）。
                drm = _detect_book_drm(local_path)
                _t, _ch = book_load(local_path)
                ok = bool(_ch) and any((c or "").strip() for c in _ch)
            except Exception as exc:
                ok = False
                err = str(exc)[:120]

            def _done():
                # 期间用户换了文件 → 这次作废
                if int(getattr(self, "_content_tag", 0)) != _my_tag:
                    return
                if not ok:
                    if drm:
                        # ★ 查清楚了：就是加密电子书 —— 给**确定的话 + 出路**
                        self._show_text(self._unreadable_text(
                            path, size, mtime,
                            "这本电子书**加了版权保护（DRM）**，预览不了。\n"
                            + drm +
                            "\n这不是缺什么插件的问题 —— 正文被加密了，"
                            "解密的钥匙在发行方服务器上，\n"
                            "任何看图/看书的软件都打不开它。\n\n"
                            "想看请用**买它的那个 App**（比如掌阅 / Kindle 客户端）打开。\n"
                            "双击文件名可以用系统默认程序试着打开它。"))
                    else:
                        # 没查出 DRM → 老实说"解析失败"，但**别列一堆可能性**
                        self._show_text(self._unreadable_text(
                            path, size, mtime,
                            "这本电子书解析不出正文（**没有加密标记**，"
                            "所以多半是格式少见或文件损坏）。\n"
                            + (("（%s）\n" % err) if err else "") +
                            "\n双击文件名可以用系统默认程序打开它。"))
                    return
                try:
                    self._show_book(local_path, size, mtime)
                except Exception as _e2:
                    note_swallowed(T("预览：显示电子书失败"), _e2)

            self._ui(_done)

        try:
            import threading
            threading.Thread(target=_work, daemon=True).start()
        except Exception:
            # 起不了线程就退回同步做（慢一点但不会不出内容）
            _work()

    def _show_remote_parse_hint(self, path, size, mtime, kind):
        """★★ v26 重写：网盘上的「重文件」先不自动解析，给个按钮。

        用户要求：「能不能让网盘的文件也能预览，最好还有个进度条显示
        加载进度，最好界面也别卡住」——这一版就照着这个做：

          · 点「📥 拷到本地再打开」→ 后台线程开始拷贝（**界面不卡**）
          · 拷贝时**进度条实时显示**：已拷 25 MB / 114 MB (22%)
          · 拷完之后用本地副本打开，**秒出内容**（PDF/图片/电子书都秒开）
          · 拷过之后翻页 / 重新选中 / 拖来拖去**都不用再等**
          · 关掉程序后再开，上次残留的临时文件自动清掉（不占空间）
        """
        # ★ 2026-10-03：顶上那行类型信息别再停在「正在读取…」了
        try:
            self.kind_lbl.configure(text=T("{k} · 还在网盘上（没拷到本地）", k=kind))
        except Exception:
            pass
        self._show_text(
            "【%s · 放在网盘上，先没自动解析】\n\n"
            "名称：%s\n"
            "路径：%s\n"
            "大小：%s\n"
            "修改时间：%s\n\n"
            "为什么没自动解析：网盘上的大文件读起来可能要几十秒，\n"
            "那段时间整个程序会发僵。\n\n"
            "点下面的「📥 拷到本地再打开」就可以预览 ——\n"
            "会在**后台**悄悄拷贝（界面上有进度条，你可以接着干别的），\n"
            "拷完之后立刻显示内容；之后翻页、重新点都不用再等。\n"
            "或者直接双击用系统默认程序打开。"
            % (kind, os.path.basename(path), path, size, mtime))
        try:
            self._nav_prev.configure(
                text=T("📥 拷到本地再打开"), width=16,
                state="normal",
                command=lambda p=path: self._force_parse(p))
            self._nav_next.configure(text="…", width=3, state="disabled")
            # 进度条先藏起来（点了「拷到本地」才出现）
            try:
                self._nav_prog.pack_forget()
            except Exception:
                pass
            self._show_nav("网盘文件 · 拷到本地再打开（快）", None, None)
        except Exception:
            pass

    def _force_parse(self, path):
        """★★ v26 重写：用户点了「📥 拷到本地再打开」。

        新流程（对应「有进度条 + 界面别卡住」）：
          ① 起后台线程把网盘文件拷到系统临时目录（同名同扩展名）
          ② 拷贝时每 256KB 回调一次进度 → 主线程更新进度条
          ③ 拷完 → 主线程调 show_path（此时走本地副本，秒开）
          ④ 期间用户可以接着操作别的；切换文件就作废这次拷贝
        """
        # 取消上一次拷贝（如果有）
        self._fetch_cancel = int(getattr(self, "_fetch_cancel", 0)) + 1
        tag = self._fetch_cancel

        # 已经拷过？直接用
        if path in getattr(self, "_remote_tmp", {}):
            try:
                self.show_path(path)
            except Exception:
                pass
            return

        # 显示进度条
        try:
            self.kind_lbl.configure(text=T("正在拷贝到本地缓存…"))
            self._nav_prev.configure(
                text=T("✖ 取消"), width=8,
                command=self._cancel_fetch)
            self._nav_next.configure(text="", width=3, state="disabled")
            self._nav_info.configure(text=T("准备中…"))
            self._nav_prog.configure(mode="determinate", value=0,
                                     maximum=100)
            try:
                self._nav_prog.pack(side="left", padx=6,
                                    fill="x", expand=True)
            except Exception:
                pass
            self._show_nav("网盘文件 · 正在拷贝到本地",
                           None, None)
        except Exception:
            pass

        # 起后台线程
        try:
            threading.Thread(
                target=self._fetch_remote_worker,
                args=(path, tag),
                daemon=True).start()
        except Exception as exc:
            try:
                note_swallowed(T("网盘预览：起拷贝线程失败"), exc)
            except Exception:
                pass

    def _cancel_fetch(self):
        """用户点了「✖ 取消」——停掉这次拷贝。"""
        self._fetch_cancel = int(getattr(self, "_fetch_cancel", 0)) + 1
        try:
            self._nav_prog.pack_forget()
        except Exception:
            pass
        try:
            self.kind_lbl.configure(text="")
        except Exception:
            pass
        # 用原路径重新走一遍（会回到"要不要拷"的提示页）
        try:
            p = getattr(self, "_cur_path", None)
            if p:
                # 把本地缓存里这个 key 去掉（半截的文件不能算数）
                self._remote_tmp.pop(p, None)
                self.show_path(p)
        except Exception:
            pass

    def _ui(self, fn, *a):
        """★★ v26 补丁（2026-10-03）：把「后台线程干完活要贴图」这件事
        丢回主线程去做（Tk 的控件只能主线程碰）。

        ★ 这个方法以前**忘了写**：后台拷贝线程干完活调的是
          `self._ui(self._fetch_done, ...)`，而 PreviewPane（预览窗格）
          自己根本没有 `_ui` 这个方法（它只写在「属性」那个窗口里）。
          后果：**网盘文件拷完了却什么都不发生** —— 线程里抛的
          AttributeError 没人接（后台线程的报错不会弹窗），
          表现就是「点了『拷到本地再打开』，进度条卡在那里，内容永远不出来」。
          现在补上：和「属性」窗口里那份写法完全一样。
        ★★ 2026-10-03 又改了一道（这次才是真凶）：
          光把方法补上还不够 —— 这里原来用的是 `self.after(0, ...)`，
          而 **从后台线程调 Tk 的 after 会卡死在 tkinter 内部**
          （Tcl 解释器同一时刻只许一个线程碰；主线程正在事件循环里的时候，
           后台线程这一步就可能永远等下去）。
          实测后果：PDF 第一页永远渲染不出来 —— 预览区一片空白，
          右上角一直写着「PDF · 正在渲染第一页…」，等多久都没用
          （用户说的「网盘预览 PDF 要滚动的那种也不行」就是这个）。
          现在改成走**主程序那条安全信箱**（后台线程只往一个 Python
          列表里塞东西、不碰 Tcl，绝不会卡；主线程每 60 毫秒取一次）。
        ★★ 2026-10-03 又加固了一道：拿不到主程序那条信箱时**宁可记一笔
          日志、丢掉这一次**，也**不再退回 after(0, ...)** —— 因为
          after(0, ...) 在后台线程里会卡死，丢一次远比卡死好。
        """
        try:
            if APP_CLOSING:
                return
            if threading.current_thread() is threading.main_thread():
                fn(*a)                       # 本来就在主线程，直接做
                return
            _app = getattr(self, "app", None)
            if _app is not None and hasattr(_app, "_ui_threadsafe"):
                _app._ui_threadsafe(fn, *a)
                return
            # ★ 兜底：拿不到安全信箱时，记一笔日志，丢掉这次回调
            #   —— after(0, ...) 在后台线程会卡死，绝不能用。
            try:
                note_swallowed(
                    "PreviewPane._ui：拿不到主程序的 _ui_threadsafe，"
                    "这次回主线程的活儿被丢掉了",
                    RuntimeError("missing _ui_threadsafe"),
                    level="error")
            except Exception:
                pass
        except Exception:
            pass

    def _fetch_remote_worker(self, path, tag):
        """（**后台线程**里跑）把网盘文件拷到系统临时目录。

        目录结构：
          %TEMP%/file_tagger_cache/<md5前12位>/原文件名.原扩展名
        这样多个同名的网盘文件不会互相覆盖，扩展名保留让 PDF/电子书/图片
        都能正常识别。
        """
        import hashlib
        try:
            # ★★ v26：用 _preview_cache_dir() —— 用户可以自己设目录
            tmpdir = _preview_cache_dir()
            h = hashlib.md5(path.encode("utf-8", "replace")).hexdigest()[:12]
            subdir = os.path.join(tmpdir, h)
            os.makedirs(subdir, exist_ok=True)
            tmp_path = os.path.join(subdir, os.path.basename(path) or "tmp.bin")
        except Exception as exc:
            self._ui(self._fetch_failed, tag, path, str(exc))
            return

        # 总大小（stat 可能慢，但这一步至少让我们能显示百分比）
        total = 0
        try:
            total = os.path.getsize(path)
        except Exception:
            total = 0

        copied = 0
        try:
            with open(path, "rb") as fin, open(tmp_path, "wb") as fout:
                while True:
                    # 被取消了 / 换了目标 → 立刻收工，删掉半截文件
                    if int(getattr(self, "_fetch_cancel", 0)) != int(tag):
                        try:
                            os.remove(tmp_path)
                        except Exception:
                            pass
                        return
                    buf = fin.read(256 * 1024)
                    if not buf:
                        break
                    fout.write(buf)
                    copied += len(buf)
                    pct = int(copied * 100 / total) if total > 0 else 0
                    if pct > 100:
                        pct = 100
                    # 回主线程更新进度（Tk 控件只能主线程碰）
                    try:
                        self._ui(self._fetch_progress,
                                 tag, copied, total, pct)
                    except Exception:
                        pass
        except Exception as exc:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
            self._ui(self._fetch_failed, tag, path, str(exc))
            return

        # 拷贝成功
        self._ui(self._fetch_done, tag, path, tmp_path)

    def _fetch_progress(self, tag, copied, total, pct):
        """（主线程里跑）更新进度条文字和数值。"""
        if int(getattr(self, "_fetch_cancel", 0)) != int(tag):
            return
        try:
            self._nav_prog.configure(value=pct)
            if total > 0:
                self._nav_info.configure(
                    text=T("正在拷贝到本地缓存… {a} / {b}（{c}%）",
                           a=self._fmt_size(copied),
                           b=self._fmt_size(total), c=pct))
            else:
                self._nav_info.configure(
                    text=T("正在拷贝到本地缓存… {x}",
                           x=self._fmt_size(copied)))
        except Exception:
            pass

    def _fetch_done(self, tag, path, tmp_path):
        """（主线程里跑）拷贝完成 → 记进缓存 → 用本地副本打开。"""
        if int(getattr(self, "_fetch_cancel", 0)) != int(tag):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
            return
        try:
            self._remote_tmp[path] = tmp_path
        except Exception:
            pass
        try:
            self._nav_prog.pack_forget()
        except Exception:
            pass
        # 用**原路径**再打开一次（show_path 会走本地副本）
        try:
            self.show_path(path)
        except Exception as exc:
            try:
                note_swallowed(T("网盘预览：拷贝完成后打开失败"), exc)
            except Exception:
                pass

    def _fetch_failed(self, tag, path, err):
        """（主线程里跑）拷贝失败 → 说清楚原因。"""
        if int(getattr(self, "_fetch_cancel", 0)) != int(tag):
            return
        try:
            self._nav_prog.pack_forget()
        except Exception:
            pass
        try:
            self.kind_lbl.configure(text="")
        except Exception:
            pass
        self._show_text(
            "【拷贝到本地失败】\n\n"
            "路径：%s\n\n"
            "原因：%s\n\n"
            "常见情况：\n"
            "  · 网盘客户端没醒 / 没登录 —— 先在资源管理器里打开一次该网盘\n"
            "  · 网络断了 / 网盘限速严重 —— 隔一会儿再试\n"
            "  · 这个文件在网盘上已经删掉了\n\n"
            "直接双击仍然可以用系统默认程序打开它。" % (path, err))

    # ---------------- 对外 ----------------
    def clear(self):
        self.current_path = None
        self._photo = None
        try:
            self.name_lbl.configure(text=T("（选中一个文件，这里就会显示它）"))
            self.path_lbl.configure(text="")
            self.kind_lbl.configure(text="")
        except Exception:
            pass
        self._show_text("💡 文本/代码/图片直接看；PDF/视频看文件信息和标签（只读不改）")

    def show_multi(self, n):
        self.current_path = None
        self._photo = None
        try:
            self.name_lbl.configure(text="已选中 %d 个文件" % n)
            self.path_lbl.configure(text="")
            self.kind_lbl.configure(text="")
        except Exception:
            pass
        self._show_text("选中一个文件（单击）才能在这里看它的内容。")

    def _size_cache_get(self, local):
        """★ 从「记得的大小」里拿一份（拿不到就返回 "?", "?"）。

        ★★ 2026-10-06：为什么要缓存 —— 实测用户网盘上 `os.stat()`
          单次最慢 **1.28 秒**。这个「文件多大、什么时候改的」
          完全没必要让界面等它：先用上次量到的（同一本书大小基本不变），
          后台量到新的再换上，肉眼完全看不出差别，但界面不卡了。
        """
        try:
            c = getattr(self, "_size_cache", None)
            if c is None:
                self._size_cache = {}
                c = self._size_cache
            hit = c.get(local)
            if hit:
                return hit
        except Exception:
            pass
        # 退一步：库里/别处已经知道的，也先用着
        try:
            f = getattr(self, "_cur_row_info", None)
            if isinstance(f, dict) and f.get("size"):
                return str(f.get("size")), str(f.get("mtime") or "?")
        except Exception:
            pass
        return "?", "?"

    def _size_probe_async(self, local, tag):
        """★（后台）量一次真实的大小 / 修改时间，量好排队换上去。

        ★ 这个线程里**一个界面控件都不碰** —— 只往信箱里排队。
        """
        if not local:
            return

        def _work():
            try:
                st = os.stat(local)
                sz = "%d" % int(st.st_size)
                mt = datetime.fromtimestamp(st.st_mtime).strftime(
                    "%Y-%m-%d %H:%M")
            except Exception:
                return
            try:
                c = getattr(self, "_size_cache", None)
                if c is None:
                    self._size_cache = {}
                    c = self._size_cache
                c[local] = (self._fmt_size_raw(int(sz)), mt)
            except Exception:
                pass
            _bg_post(self._size_apply, local, int(sz), mt)

        threading.Thread(target=_work, daemon=True, name="量文件大小").start()

    @staticmethod
    def _fmt_size_raw(n):
        try:
            for unit in ("B", "KB", "MB", "GB", "TB"):
                if n < 1024 or unit == "TB":
                    return ("%.0f %s" % (n, unit) if unit == "B"
                            else "%.1f %s" % (n, unit))
                n /= 1024.0
        except Exception:
            pass
        return "?"

    def _size_apply(self, local, nbytes, mtime):
        """（主线程）把后台量到的大小换上 —— **只有当用户还看着这个文件**。"""
        try:
            if getattr(self, "_cur_local", None) != local:
                return
            txt = self._fmt_size_raw(int(nbytes))
            cur = ""
            try:
                cur = str(self.kind_lbl.cget("text") or "")
            except Exception:
                cur = ""
            if "·" in cur:
                # 形如「PDF · 123 KB · 2026-10-06 03:45」→ 只换中间那一段
                parts = [x.strip() for x in cur.split("·")]
                if len(parts) >= 3:
                    parts[1] = txt
                    try:
                        parts[2] = mtime
                    except Exception:
                        pass
                    self.kind_lbl.configure(text=" · ".join(parts))
        except Exception:
            pass

    def show_path(self, path):
        if not path:
            self.clear()
            return
        # ★★ v25 补丁42：**治「预览卡卡的」**（防重入 + 先给即时反馈）。
        # ★★ v26：**多了一个「本地副本」的路子** ——
        #   如果这个网盘文件之前已经拷到本地缓存（_remote_tmp），
        #   这里就把「读取用的路径」换成本地副本 ——
        #   然后 os.stat / PDF 渲染 / 电子书解析 / 图片解码
        #   **全都走本地**，秒开；而**显示用的路径还是原路径**，
        #   所以窗格里显示的「路径 / 标签 / 名称」一个都不会错。
        self._cur_path = path
        self._content_tag = int(getattr(self, "_content_tag", 0)) + 1
        _my_tag = self._content_tag
        self.current_path = path
        if os.path.splitext(path)[1].lower() != ".pdf":
            self._pdf_page = 0         # 换文件就回到第 1 页
        if os.path.splitext(path)[1].lower() not in BOOK_EXTS:
            self._book_page = 0        # ★ 补丁29：换书就回到第 1 页
        name = os.path.basename(path) or path
        ext = os.path.splitext(name)[1].lower()

        # ★★ v26：读取用的路径。有本地副本就用本地副本（秒开），
        #   没有就用原路径（可能是网盘，慢）。
        _local = path
        try:
            _local = self._remote_tmp.get(path, path)
        except Exception:
            _local = path
        # ★ 记住「这次读的是哪个实际路径」—— 后台量完大小回来时对象是不是它
        self._cur_local = _local

        # ★ 补丁42：先把「名字 + 路径 + 正在读取」画出来（不用等 os.stat）
        try:
            self.name_lbl.configure(text=name)
            self.path_lbl.configure(text=os.path.dirname(path))
            self.kind_lbl.configure(text=T("正在读取…"))
        except Exception:
            pass
        # ★★ 2026-10-06：**os.stat 也不许在主线程做** ★★
        #   实测（用户网盘）：`os.stat()` 单次最慢 **1.28 秒**。
        #   以前这一句在主线程里，用户每点一个网盘文件，
        #   界面就要僵 1 秒多 —— 切得快的时候（比如连着点好几个），
        #   一秒一秒叠起来，看着就是「卡住」。
        #   现在：先拿缓存过的旧信息（.pdf 这种常用大小基本不变，够用），
        #   同时在后台线程量一次真实的，量好了再悄悄更新上去。
        size, mtime = self._size_cache_get(_local)
        self._size_probe_async(_local, _my_tag)
        # ★★ 2026-10-06：**卡点探针**（临时，用来找「还有哪句在等」）★★
        #   打开：把下面这行的 False 改成 True（或者设环境变量
        #   AIXIEDE_TRACE=1），程序会把每一段花的毫秒写进
        #   `预览卡点-日志.txt`（放在程序目录）。找完就不用了。
        _trace = (os.environ.get("AIXIEDE_TRACE") == "1")
        _tmarks = []

        def _tp(name):
            if not _trace:
                return
            try:
                import time as _tm
                _tmarks.append((name, _tm.perf_counter()))
            except Exception:
                pass

        _tp("开头")

        def _trace_flush():
            """把这次 show_path 各段的毫秒数写进日志（只在排查时用）。"""
            if not _trace:
                return
            try:
                import time as _tm
                _tmarks.append(("结束", _tm.perf_counter()))
                segs = []
                for k in range(1, len(_tmarks)):
                    segs.append("%s=%.0fms" % (
                        _tmarks[k][0],
                        (_tmarks[k][1] - _tmarks[k - 1][1]) * 1000.0))
                segs.append("总计=%.0fms" % (
                    (_tmarks[-1][1] - _tmarks[0][1]) * 1000.0))
                p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "预览卡点-日志.txt")
                with open(p, "a", encoding="utf-8") as f:
                    f.write("%s  %s  %s\n"
                            % (datetime.now().strftime("%H:%M:%S"),
                               (name or "")[:40], "  ".join(segs)))
            except Exception:
                pass

        # ★★ v26 修正（治「网盘文件选中后卡住」）：
        #   原来这里用 `os.path.isdir(path)` —— 网盘路径这一下会走网络，
        #   有时候会卡几秒到几十秒（正是用户反馈的「卡住了」）。
        #   现在分两种情况：
        #     · 已经拷到本地（_has_local=True）→ 本地 isdir 秒回
        #     · 还没拷（网盘原路径）→ **不看磁盘**，只用扩展名猜：
        #         有扩展名 = 文件；没扩展名 = 目录
        _has_local = False
        try:
            _has_local = path in self._remote_tmp
        except Exception:
            _has_local = False
        if _has_local:
            try:
                _is_dir = os.path.isdir(_local)
            except Exception:
                _is_dir = False
        else:
            _is_dir = (ext == "")
        if _is_dir:
            try:
                self.kind_lbl.configure(text=T("文件夹"))
            except Exception:
                pass
            self._show_text("这是一个文件夹：\n%s\n\n双击它就能进去。" % path)
            return

        if ext in IMAGE_EXTS and HAS_PIL:
            try:
                self.kind_lbl.configure(text="图片 · %s · %s" % (size, mtime))
            except Exception:
                pass
            # ★ v26：图片解码也走本地副本
            self._show_image(_local)
            _trace_flush()
            return

        # ★★ 2026-01-26：视频预览（网盘文件无需下载，直接读缩略图）
        if ext in VIDEO_EXTS and HAS_PIL:
            try:
                self.kind_lbl.configure(text="视频 · %s · %s" % (size, mtime))
            except Exception:
                pass
            # 先显示一个「正在读取视频…」提示
            self._show_text("正在读取视频预览…")
            # 后台线程获取视频缩略图
            def _fetch_vid():
                thumb = get_video_thumbnail_pil(_local, size=480)
                # ★ 后台线程只准排队，不许碰界面（碰了会和主线程抢 Tcl）
                if thumb is None:
                    _bg_post(self._show_text,
                             "视频缩略图无法生成（视频可能损坏或编码不支持）")
                else:
                    _bg_post(self._show_pil_image, thumb, size, mtime)
            import threading
            t = threading.Thread(target=_fetch_vid, daemon=True)
            t.start()
            _trace_flush()
            return

        _remote_file = False
        try:
            _remote_file = is_remote_path(path)
        except Exception:
            _remote_file = False

        # ★★ v26：**网盘保护只在「还没拷到本地」时生效**。
        #   一旦拷好了（path in _remote_tmp），下面所有分支都正常走 ——
        #   这时候 _local 是本地临时文件，读取秒开，不需要再提示。
        _has_local = False
        try:
            _has_local = path in self._remote_tmp
        except Exception:
            _has_local = False

        if ext == ".pdf":
            if not HAS_FITZ:
                self._show_text(self._pdf_missing_text())
                return
            # ★★ 2026-10-06：**网盘 PDF 不再拦着让你先下载了** ★★
            #   用户要求：「我很想让网盘上的 .pdf 不用手动下载就能在
            #   右侧预览区预览」。
            #   以前这里写的是：网盘文件 + 没拷到本地 → 只给一个
            #   「📥 拷到本地再打开」的提示，不自动解析。
            #   为什么敢直接读（实测数据，用户网盘 555MB / 340 页的 PDF）：
            #     · 直接打开网盘上的 PDF：**1.34 秒**
            #     · 渲染第 1 页：0.08 秒；跳到第 301 页：0.15 秒
            #     · 而整个拷到本地要 7.6 秒
            #   → **直接读比拷贝还快**，所以拷贝那一步完全是多余的。
            #   ★ 还是走后台线程渲染（界面绝不卡），这一点没变。
            if _remote_file and not _has_local:
                try:
                    self.kind_lbl.configure(
                        text="PDF · 网盘直读中… · %s" % size)
                except Exception:
                    pass
            total = 0
            # ★★ 2026-10-06：**不许在主线程里为了「先知道几页」去开文件** ★★
            #   实测：网盘上开一次 PDF 要 **1~6.5 秒**。
            #   这里原来是同步 `pdf_page_count(_local)` —— 白等一场，
            #   而且下面 `_show_pdf_scroll` 还会**再开一次**。
            #   现在：直接用真正的那个通道（`_show_pdf_scroll` 会把
            #   「开文件 + 读页数 + 渲染第一页」整包丢后台），
            #   主线程一步都不等。少等一次、还少开一次文件。
            self._show_pdf(_local, size, mtime)
            _trace_flush()
            return

        if ext in BOOK_EXTS:
            # ★★ 2026-10-06：电子书也一样 —— 网盘上的**直接读**，
            #   不再拦着让你先「拷到本地」。
            #   （电子书比 PDF 小得多，直接读更没压力。）
            if _remote_file and not _has_local:
                try:
                    self.kind_lbl.configure(
                        text="电子书 · 网盘直读中… · %s" % size)
                except Exception:
                    pass
            # ★ 电子书解析比较慢（要解压 + 解析），丢后台线程做
            # ★★ 2026-10-06：**网盘的电子书一律走后台**（原来只对
            #   「认出来是网盘路径」的才走后台；实测有些挂载认不出来，
            #   于是解析卡在主线程上，一卡就是好几秒）。
            #   本地文件走后台也完全没损失，反而更快出内容。
            self._book_load_async(path, size, mtime, _local)
            _trace_flush()
            return

        if ext in self.TEXT_EXTS or ext == "":
            try:
                self.kind_lbl.configure(text="文本 · %s · %s" % (size, mtime))
            except Exception:
                pass
            body = self._read_text(_local)
            if body is None:
                self._show_text(self._info_text(path, size, mtime))
            else:
                self._show_text(body)
            return

        try:
            self.kind_lbl.configure(text="%s 文件 · %s · %s"
                                    % (ext.lstrip(".").upper(), size, mtime))
        except Exception:
            pass
        self._show_text(self._info_text(path, size, mtime))




# ---------- 兜底（★ 它会吃掉错误，所以要专门测"用的哪一份"）----------
def _fallback():
    g = globals()
    for _n in _NEED:
        if g.get(_n) is None:
            g[_n] = _Borrowed(_n)


_fallback()
