# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：PropsDialog。

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

★★ 拆的时候踩过的坑（错题本 #158~#161，★ 别重演）：
   · import 要写 `from PropsDialog import …`（**不带包路径**）
   · `_set_app` 要**取别名**（`as _fk_…`）——模块名和类名同名
   · 借名字的清单**用 symtable + dir() 定**，别用正则猜
   · 代理类**必须实现 `__call__`**（函数也会被借）
   · ★ 兜底 except 会吃掉错误 → **必须专门测"用的哪一份"**
"""
import os
import sys
import threading
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, colorchooser

# ---------- 要向主程序借的名字（先占位，挂上后填真身） ----------
_MUTABLE = ['APP_CLOSING', 'BOLD', 'FONT', 'UI_FONT_SIZE']
_NEED = ['APP_CLOSING', 'BOLD', 'FONT', 'HAS_CD_API', 'T', 'UI_FONT_SIZE', '_cd_pb', '_dir_size_from_cache', '_dlg_geom', '_dlg_size', '_progress_fraction', '_win_file_acl_info', 'cd_api_client_from_settings', 'datetime', 'fmt_size', 'is_remote_path', 'note_swallowed', 'os', 'theme_get', 'threading']
_APP = None


class _Borrowed:
    """★★ 借"会变的东西"用的代理（★ 每次读都回主程序现取）。

    ★ 为什么不能直接抄一份：`THEME_NAME` / `HAS_PIL` 这些**运行时会变** ——
      启动时抄过来，切主题/装不装 PIL 之后**模块里还是旧值**。

    ★★★ 为什么 `__call__` 不能少（错题本 #160）：
      **函数也会被借**（`T` / `fmt_size` / …）——
      少了 `__call__`，`T("…")` 直接 `TypeError: not callable`，
      ★ 而且这个错**会被上层 except 吞掉** → 表现成"功能静默消失"。
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

    # ★★★ 这个必须有（函数要用）
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
                # ★★ 会变的才用代理；**函数/常量直接拿**（★ 少一层、少一个坑）
                # ★★★ 一律包代理（错题本 #168）：
                #   模块的桩可能跑在**主程序还没定义这个名字**之前，
                #   所以「启动时取快照」必然借不到。
                #   ★ 代理是**读的时候才现取**，什么时候定义都不影响。
                g[_n] = _Borrowed(_n)
        except Exception:
            pass


class PropsDialog(tk.Toplevel):
    """右键 →「属性」：把「这个文件/文件夹的前世今生」一次列全。

    显示内容（分两段，先出快的、慢的在后台补）：
      快（几毫秒）：名称 / 类型 / 大小 / 位置 / 是不是文件夹 / 在不在索引里
      后台补（几秒）：
        · 文件夹：文件数 / 文件夹数 / 总大小 / 占父文件夹的百分比
          —— 直接用索引（dir_cache）求和，网盘也秒回
        · 本地文件：创建 / 修改 / 访问时间 + 权限（谁读、谁写、谁是所有者）
        · 网盘文件：CloudDrive2 那边的 分享 / 收藏 / 原始路径
                      + 这个文件占它所在文件夹的百分比
    所有查询都是**只读**的，不会改任何东西。
    """

    def __init__(self, master, app, store, path):
        super().__init__(master)
        self.app = app
        self.store = store
        self.path = str(path)
        self.title("属性")
        self.geometry(_dlg_geom(760, 560))
        self.minsize(*_dlg_size(620, 420, minimum=(620, 420)))
        self.transient(master)
        try:
            text_widget = None
            body = ttk.Frame(self)
            body.pack(fill="both", expand=True, padx=10, pady=10)
            wrap = ttk.Frame(body)
            wrap.pack(fill="both", expand=True)
            sb = ttk.Scrollbar(wrap, orient="vertical")
            sb.pack(side="right", fill="y")
            # ★ v25 补丁42：**wrap 从 "none" 改成 "word"**。
            #   用户反馈：「属性那里文字不能随着窗口宽度自动换行吗，
            #   看着不太方便」。原来 wrap="none" 就是不换行的意思 ——
            #   长路径只能横向拖、看不全。现在按窗口宽度自动换行。
            # ★★ 2026-10-08 补 `width=48`（原来没给 → Tk 默认 **80 字符宽**
            #   ≈ 884 像素）→ **会把整个属性窗口撑宽**。
            #   ★ 这是"窗口显示不全"的同一类病根（待清算 #9）——
            #     凡是 `tk.Text` **一定要给 width**，因为它默认是 80，
            #     比大多数窗口都宽。
            #   ★ 给了 width 也不影响"自动换行"（`wrap="word"` 照旧生效）——
            #     这里只是把"请求宽度"压到一个合理的值。
            self.txt = tk.Text(wrap, wrap="word", height=24, width=48,
                               font=(FONT, UI_FONT_SIZE), yscrollcommand=sb.set)
            self.txt.pack(side="left", fill="both", expand=True)
            sb.configure(command=self.txt.yview)
            text_widget = self.txt
            btns = ttk.Frame(body)
            btns.pack(fill="x", pady=(8, 0))
            ttk.Button(btns, text=T("刷新"), command=self._reload).pack(side="left")
            ttk.Button(btns, text=T("复制全部"), command=self._copy_all).pack(
                side="left", padx=6)
            ttk.Button(btns, text=T("关闭"), command=self.destroy).pack(side="right")
            self.bind("<Escape>", lambda e: self.destroy())
            self._lines = []
            self._append("（正在读取…）", "dim")
            self.after(30, self._reload)
        except Exception:
            pass

    # ---------- 输出辅助 ----------
    def _reset(self):
        try:
            self.txt.configure(state="normal")
            self.txt.delete("1.0", "end")
            self._lines = []
        except Exception:
            pass

    def _append(self, text, tag="normal"):
        """往窗口里加一行（tag：title / dim / warn / normal）。"""
        try:
            self.txt.configure(state="normal")
            self.txt.insert("end", str(text) + "\n", tag)
            self._lines.append(str(text))
            if tag == "title":
                self.txt.tag_configure("title", font=(FONT, UI_FONT_SIZE, BOLD))
            elif tag == "dim":
                self.txt.tag_configure("dim", foreground=theme_get("fg_dim"))
            elif tag == "warn":
                self.txt.tag_configure("warn", foreground=theme_get("warn"))
            self.txt.configure(state="disabled")
        except Exception:
            pass

    def _copy_all(self):
        try:
            self.clipboard_clear()
            self.clipboard_append("\n".join(self._lines))
            self.app.set_status(T("属性内容已复制到剪贴板"))
        except Exception:
            pass

    # ---------- 主流程 ----------
    def _reload(self):
        self._reset()
        p = self.path
        is_dir = False
        try:
            is_dir = os.path.isdir(p)
        except Exception:
            is_dir = False
        name = os.path.basename(p.rstrip("\\")) or p
        self._append("■ " + name, "title")
        self._append("─" * 60, "dim")
        try:
            self._append("类型      ：" + ("文件夹" if is_dir else
                                          (os.path.splitext(p)[1].lstrip(".").upper()
                                           + " 文件" if os.path.splitext(p)[1]
                                           else "文件")))
        except Exception:
            pass
        self._append("完整路径  ：" + p)
        try:
            remote = is_remote_path(p)
        except Exception:
            remote = False
        self._append("位置      ：" + ("网盘（网络盘）" if remote else "本地磁盘"))

        # —— 快的那部分：文件大小 / 库里的记录 ——
        try:
            if not is_dir:
                sz = os.path.getsize(p)
                self._append("大小      ：" + fmt_size(sz))
        except Exception as exc:
            self._append("大小      ：读不到（%s）" % str(exc)[:60], "dim")
        self._append("")
        self._append("【这个程序知道的】", "title")
        fid = None
        try:
            fid = self._fid()
        except Exception:
            fid = None
        if fid:
            try:
                tags = self.store.tags_of_file(fid) if hasattr(
                    self.store, "tags_of_file") else None
            except Exception:
                tags = None
            if tags:
                self._append("标签      ：" + "、".join(
                    t["name"] for t in tags[:20])
                    + ("…" if len(tags) > 20 else ""))
            else:
                self._append("标签      ：（没有标签）", "dim")
            try:
                row = self.store.conn.execute(
                    "SELECT added_at FROM files WHERE id=?", (fid,)).fetchone()
                if row and row[0]:
                    self._append("入库时间  ：" + str(row[0]).replace("T", " "))
            except Exception:
                pass
        else:
            self._append("标签      ：（这个路径还没进过库）", "dim")
        # 是不是索引里的一级/子目录
        try:
            n_sub = self.store.conn.execute(
                "SELECT COUNT(*) FROM dir_cache WHERE dir_path=?", (p,)
            ).fetchone()[0]
            self._append("索引        ："
                         + ("有，直接子项 %d 个" % n_sub if n_sub
                            else "这个目录本身没缓存（父目录列表里可能有它）"),
                         "normal" if n_sub else "dim")
        except Exception:
            pass

        # —— 慢的那部分：后台线程算，算完再补进窗口 ——
        self._append("")
        self._append("（下面这些正在后台读取，网盘可能要几秒…）", "dim")
        threading.Thread(target=self._slow_probe, args=(p, is_dir, remote),
                         daemon=True).start()

    def _fid(self):
        """取这个路径在 files 表里的 id（库里没这条记录就返回 None）。

        ★ v26 修正：这里以前写的是 `_fid(self.store, self.path)` ——
          但 `_fid` 是 TagStore（数据库类）的**方法**，不是全局函数，
          所以这一行永远抛 NameError（被 except 吞掉了，你从表面上
          看不出来）。
          后果：属性窗口里「标签」那一行永远显示「（这个路径还没进过库）」，
          哪怕这个文件明明有标签 —— 就是因为这里根本没查成功。
          现在改成正确的写法：调用数据库对象上的方法。

        ★ 传 create=False 的原因：属性窗口是**只读**的，
          不能因为"看属性"就顺手往数据库里插一条记录。
        """
        try:
            return self.store._fid(self.path, create=False)
        except Exception:
            return None

    def _ui(self, fn, *a):
        """回主线程补内容（关窗了就什么都不做）。

        ★★ v26 补丁（2026-10-03）：原来这里写的是 `self.after(0, fn, *a)`，
        但 `_slow_probe` 是后台线程（17954 行 `threading.Thread(...).start()`），
        而 **从后台线程调 Tk 的 after 会卡死在 tkinter 内部**（Tcl 解释器
        同一时刻只许一个线程碰它；主线程正在事件循环里的时候，后台线程
        这一步就可能永远等下去）。后果：用户点右键 → 属性，下面那一大块
        （包含 / 总大小 / 网盘统计 / 收藏 / 分享 / 占比 等）很可能**永远
        出不来**。现在改成走主程序那条安全信箱（和 PreviewPane._ui 一样的
        写法），没有 app / 没有 _ui_threadsafe 时**宁可记一笔日志也不
        再用 after(0, ...)** —— after(0) 是会卡死的，宁可丢一次也不能卡。
        """
        try:
            if APP_CLOSING:
                return
            _app = getattr(self, "app", None)
            if _app is not None and hasattr(_app, "_ui_threadsafe"):
                _app._ui_threadsafe(fn, *a)
                return
            # ★★ 2026-10-03：拿不到 _ui_threadsafe 时**宁可记一笔日志、丢掉这一次**，
            #   也**不再退回 after(0, ...)** —— after(0, ...) 在后台线程里会卡死，
            #   丢一次远比卡死好。
            #   之前还套了一层 except Exception: pass 把这一句的报错也吞掉，
            #   现在把它撤掉，让失败至少能落进 note_swallowed 的日志面板。
            note_swallowed(
                "PropsDialog._ui：拿不到主程序的 _ui_threadsafe，"
                "这次回主线程的活儿被丢掉了",
                RuntimeError("missing _ui_threadsafe"),
                level="error")
        except Exception as exc:
            # ★ 连 note_swallowed 都挂了时退回 stderr（控制台一定能看）
            try:
                import sys as _sys
                _sys.stderr.write(
                    f"[PropsDialog._ui fatal] {exc!r}\n")
            except Exception:
                pass
            pass

    def _slow_probe(self, p, is_dir, remote):
        """后台线程：算大小 / 数量 / 占比 / 时间 / 权限 / 分享。"""
        info = {}
        info["remote"] = bool(remote)      # ★ 补丁23：后面显示权限时要用
        # 1) 文件夹：用索引求和（快且不碰网盘）
        if is_dir:
            info["cache"] = _dir_size_from_cache(self.store, p)
        # 2) 本地文件 / 文件夹：真实的时间（网盘就不去问了，太慢）
        if not remote:
            try:
                st = os.stat(p)
                info["atime"] = st.st_atime
                info["mtime"] = st.st_mtime
                info["ctime"] = st.st_ctime
            except Exception as exc:
                info["stat_err"] = str(exc)[:80]
            if not is_dir:
                info["acl"] = _win_file_acl_info(p)
            else:
                info["acl"] = _win_file_acl_info(p)
        # 3) 网盘文件：问 CloudDrive2（分享 / 收藏 / 原始路径）
        if remote and HAS_CD_API:
            try:
                client, _why = cd_api_client_from_settings()
                if client is not None:
                    try:
                        cd = client.cd_path_of(p)
                        if cd:
                            req = _cd_pb.FileRequest(path=cd)
                            try:
                                det = client.stub.GetFileDetailProperties(
                                    req, timeout=20, metadata=client._md())
                                info["detail"] = {
                                    "files": det.totalFileCount,
                                    "folders": det.totalFolderCount,
                                    "size": det.totalSize,
                                    "fav": bool(det.isFaved),
                                    "shared": bool(det.isShared),
                                    "orig": det.originalPath,
                                }
                            except Exception as exc:
                                info["detail_err"] = str(exc)[:100]
                            try:
                                sp = client.stub.GetSpaceInfo(
                                    req, timeout=15, metadata=client._md())
                                info["space"] = (sp.totalSpace, sp.usedSpace,
                                                 sp.freeSpace)
                            except Exception:
                                pass
                    finally:
                        try:
                            client.close()
                        except Exception:
                            pass
            except Exception as exc:
                info["cd_err"] = str(exc)[:100]
        # 4) 占父级百分比（用索引算：自己 vs 父目录）
        try:
            parent = os.path.dirname(p.rstrip("\\"))
            if parent and len(parent) >= 3:
                pc = _dir_size_from_cache(self.store, parent)
                if pc and (pc[2] or 0) > 0:
                    info["parent"] = (parent, pc)
        except Exception:
            pass
        self._ui(self._fill_slow, info)

    def _fill_slow(self, info):
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return
        try:
            self.txt.configure(state="normal")
            # 删掉那句「正在读取」
            try:
                self.txt.delete("end-2l", "end-1l")
            except Exception:
                pass
            add = self._append
            add("【内容与大小】", "title")
            c = info.get("cache")
            if c is not None:
                dirs, files, byts, nosize = c
                add("包含      ：%d 个文件，%d 个文件夹" % (files, dirs))
                add("总大小    ：" + fmt_size(byts)
                    + ("（有 %d 个文件没记大小，实际可能略大）" % nosize
                       if nosize else ""))
                if files + dirs == 0:
                    add("说明      ：索引里这个文件夹是空的", "dim")
            d = info.get("detail")
            if d and (d.get("files") or d.get("folders") or d.get("size")):
                add("网盘统计  ：%d 个文件 / %d 个文件夹，合计 %s"
                    % (d.get("files", 0), d.get("folders", 0),
                       fmt_size(d.get("size", 0))))
            elif d:
                # ★ 补丁23：百度网盘这类不返回「文件夹明细」，返回 0 是正常的，
                #   别拿它当结论（上面用索引算出来的才准）。
                add("网盘统计  ：这个网盘不提供文件夹明细（以「包含 / 总大小」为准）",
                    "dim")
            if d:
                add("收藏      ：" + ("★ 已收藏" if d.get("fav") else "没有收藏"))
                add("分享      ：" + ("已分享（别人能看到）"
                                      if d.get("shared") else "没有分享"))
                if d.get("orig"):
                    add("网盘原始路径：" + str(d["orig"]))
            if info.get("detail_err"):
                add("网盘统计读不到：" + info["detail_err"], "warn")
            if info.get("cd_err"):
                add("CloudDrive2 没连上：" + info["cd_err"], "warn")
            if info.get("space"):
                t, u, f = info["space"]
                add("网盘空间  ：已用 %s / 共 %s（剩 %s）"
                    % (fmt_size(u), fmt_size(t), fmt_size(f)))
            pct = None
            pc = info.get("parent")
            if pc:
                parent, (pdirs, pfiles, pbytes, _n) = pc
                my = None
                if c is not None:
                    my = c[2]
                elif d:
                    my = d.get("size")
                if my is None:
                    try:
                        my = os.path.getsize(self.path)
                    except Exception:
                        my = None
                frac = _progress_fraction(my, pbytes)
                if frac is not None:
                    pct = frac
                    add("占父文件夹：" + "%.1f%%" % (frac * 100.0)
                        + "（父：%s，合计 %s）"
                        % (os.path.basename(parent) or parent,
                           fmt_size(pbytes)))
            if pct is None:
                add("占父文件夹：算不出来（父目录不在索引里，或没有大小记录）",
                    "dim")

            add("")
            add("【时间】", "title")
            if info.get("atime"):
                for k, label in (("ctime", "创建时间"), ("mtime", "修改时间"),
                                 ("atime", "访问时间")):
                    try:
                        add("%s：%s" % (label, datetime.fromtimestamp(
                            info[k]).strftime("%Y-%m-%d %H:%M:%S")))
                    except Exception:
                        pass
            elif info.get("stat_err"):
                add("读不到（%s）" % info["stat_err"], "dim")
            else:
                add("网盘文件不查时间（问一次要好几秒，不值得）", "dim")
            # 权限
            acl = info.get("acl") or {}
            add("")
            add("【权限】", "title")
            if acl.get("acl"):
                for line in acl["acl"]:
                    add("  " + line)
                if acl.get("owner"):
                    add("所有者    ：" + acl["owner"])
            else:
                # ★ 补丁23：网盘路径拿不到 Windows 权限；本地文件夹往往也只
                #   返回继承来的几条（单个文件才读得到「谁能读 / 谁能改」）。
                if info.get("remote"):
                    add("读不到权限信息（网盘路径没有 Windows 权限这一说）",
                        "dim")
                else:
                    add("读不到权限明细（文件夹通常只给继承来的权限，"
                        "看单个文件更清楚）", "dim")
            add("")
            add("（以上都是只读查询，程序没有改动任何东西）", "dim")
            self.txt.configure(state="disabled")
            self.txt.see("1.0")
        except Exception as exc:
            try:
                self._append("（属性读取到这里出错：%s）" % str(exc)[:120],
                             "warn")
            except Exception:
                pass


# ==========================================================================
# ★ v25 补丁25：快捷键表（用户可以自己改）
#   ----------------------------------------------------------------------
#   每一项 = (动作键, 中文说明, 默认按键)。
#   动作键是程序内部用的名字，**不要改**；中文说明是给你看的；
#   默认按键就是出厂设置，改坏了点「恢复默认」就能回来。
#   实际按键存在设置文件的 shortcut_map 里。
# ==========================================================================

# 允许用户按的键名（写进设置文件的就是这些名字）
SHORTCUT_KEY_CHOICES = [
    "", "Delete", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10",
    "Ctrl+A", "Ctrl+B", "Ctrl+C", "Ctrl+D", "Ctrl+E", "Ctrl+F", "Ctrl+G",
    "Ctrl+H", "Ctrl+I", "Ctrl+J", "Ctrl+K", "Ctrl+L", "Ctrl+M", "Ctrl+N",
    "Ctrl+O", "Ctrl+P", "Ctrl+Q", "Ctrl+R", "Ctrl+S", "Ctrl+T", "Ctrl+U",
    "Ctrl+V", "Ctrl+W", "Ctrl+X", "Ctrl+Y", "Ctrl+Z",
    "Ctrl+Shift+A", "Ctrl+Shift+C", "Ctrl+Shift+D", "Ctrl+Shift+E",
    "Ctrl+Shift+F", "Ctrl+Shift+N", "Ctrl+Shift+P", "Ctrl+Shift+R",
    "Ctrl+Shift+S", "Ctrl+Shift+T", "Ctrl+Shift+V",
    "Alt+1", "Alt+2", "Alt+3", "Alt+4", "Alt+5",
    "Alt+Left", "Alt+Right", "Alt+Up", "Alt+Down",
    "Alt+A", "Alt+C", "Alt+D", "Alt+E", "Alt+F", "Alt+N", "Alt+P",
    "Alt+R", "Alt+S", "Alt+T", "Alt+V", "Alt+X", "Alt+Z",
    "BackSpace", "Space", "Insert", "Home", "End",
]




# ---------- 兜底（★ 但注意：它会吃掉错误，所以要专门测"用的哪一份"）----------
def _fallback():
    g = globals()
    for _n in _NEED:
        if g.get(_n) is None:
            g[_n] = _Borrowed(_n)


_fallback()
