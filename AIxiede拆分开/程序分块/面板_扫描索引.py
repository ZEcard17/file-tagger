# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「扫描索引」这组方法。

★★★ 这批的搬法**跟前面 13 个类不一样**（★ 看这里再动手）：
   · 前面：**整个类**搬走，主程序 `import` 一下就行（类有自己的 self）
   · 这里：搬的是**主类的方法** —— 它们原来是 `def xxx(self)`，
           现在改成 `def xxx(app)`，**函数体里的 `self.` 全换成 `app.`**，
           ★ 其余**一个字没改**。

★★★ 为什么原封不动地保留方法名（★ 这是重点）：
   主类里**留着一个同名方法**，它现在只是"一行转发"：
       def xxx(self, *a, **k):
           return _mod.xxx(self, *a, **k)
   → **所有调用方（菜单、按钮、别的 self.方法）一个字都不用改**。
   ★★ 判据：**"稳定接口"** —— 外面看到的还是 `app.xxx()`。

★★ 变量命名说明（★ 别被 `app` 绕晕）：
   这里 `app` **就是原来的 `self`** —— 也就是 `FileTaggerApp` 实例。
   改名只是为了"提醒读者：这不是一个普通的类方法"。
"""

import os
import sys
import re
import time
import json
import threading
import queue
import subprocess
import shutil
import datetime

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, filedialog, colorchooser

try:
    from PIL import Image, ImageTk
except Exception:
    Image = ImageTk = None


# ==========================================================================
#  ★★★ 要向主程序借的名字（★ 搬方法组的**关键**，错题本 #166）★★★
#  --------------------------------------------------------------------------
#  ★ 搬走的方法用了一堆**主程序自己造的东西**（`theme_get` / `T` / 常量…）。
#    这些**新文件里没有** → ★★ 一调那个方法就 `NameError` ——
#    而且**平时看不出来**（只有真点到那个按钮才炸）。
#  ★ 做法跟拆类一样：主程序启动时把「自己」交进来（`_set_app`）。
# ==========================================================================
_MUTABLE = ['APP_CLOSING']
_NEED = ['APP_CLOSING', 'IDLE_INDEX_PAUSE', 'IDLE_STOP_WITHIN_SEC', 'INDEX_SCAN_EVENT', 'RECURSIVE_MAX_FILES', 'RECURSIVE_MAX_ROOTS', 'ScanProgressDialog', 'T', 'cd_api_client_from_settings', 'collapse_roots', 'is_gone_error', 'note_swallowed', 'path_depth', 'save_idle_settings', 'scan_index_roots']
_APP = None


class _Borrowed:
    """★★ 借「会变的东西」的代理（★ 每次读回主程序现取）。

    ★★★ `__call__` 不能少（错题本 #160）：**函数也会被借**，
      少了它 `T("…")` 直接 TypeError，而且会被上层 except 吞掉。
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



    # ★★★ 2026-10-09 补齐协议（错题本 #185）★★★
    #   ★★ 原来缺 **比较大小**（`__lt__` 等四个）——
    #     真出过事：`app._idle_seconds() < IDLE_STOP_WITHIN_SEC`
    #     → `float < _Borrowed` →
    #     `TypeError: '<' not supported between instances of 'float' and '_Borrowed'`
    #   ★★★ 判据：**代理会被当成什么用，你猜不到** ——
    #     所以别一个个补，要**对着完整清单查一遍**
    #     （工具：`工具\代理协议检查.py`）。
    #   ★ 每次读都回主程序现取（`_v()`），所以「转给真值去做」最不容易错。


    def __lt__(self, o):
            return self._v() < o


    def __le__(self, o):
            return self._v() <= o


    def __gt__(self, o):
            return self._v() > o


    def __ge__(self, o):
            return self._v() >= o


    def __mul__(self, o):
            return self._v() * o

def _set_app(app):
    """主程序启动时调一下：把「自己」交进来，顺便把要借的名字填上。"""
    global _APP
    # ★★ 保护模块自己的 `__file__`（错题本 #165）
    _own = __file__
    _APP = app
    _fill()
    globals()["__file__"] = _own


def _fill():
    """从主程序身上把需要的名字取过来。"""
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


# ---------- 兜底（★ 它会吃掉错误，所以要专门测"用的哪一份"）----------
def _fallback():
    g = globals()
    for _n in _NEED:
        if g.get(_n) is None:
            g[_n] = _Borrowed(_n)


_fallback()


def _pause_scan_placeholder(app):
    """（占位，保持方法顺序整齐 —— 没实际内容）"""
    return None


def _schedule_bg_scan(app, dir_key):
    # ★ v25 补丁18：已经知道读不到的目录（网盘里删了）就别再排了，
    #   省得每次点开都去撞一次、还刷日志。
    try:
        if dir_key in app._dead_dirs():
            return
    except Exception:
        pass
    app._bg_scan_pending_dir = dir_key
    if app._bg_scan_timer is not None:
        try:
            app.root.after_cancel(app._bg_scan_timer)
        except Exception:
            pass
    app._bg_scan_timer = app.root.after(500, app._try_start_bg_scan)


def _bg_scan_worker(app, dir_key):
    entries = []
    err = None
    try:
        with os.scandir(dir_key) as it:
            for e in it:
                name = e.name
                is_d = False
                size = None
                mtime = None
                try:
                    is_d = e.is_dir(follow_symlinks=False)
                    if not is_d:
                        try:
                            st = e.stat()
                            size = st.st_size
                            mtime = st.st_mtime
                        except OSError:
                            pass
                except OSError:
                    pass
                entries.append((name, is_d, size, mtime))
    except Exception as exc:
        err = str(exc)
    # ★ v25 补丁18：往界面回话之前先看一眼「程序是不是正在关」。
    #   关窗时如果这个线程还在跑，它 root.after() 上去会让 Tk 直接崩
    #   （表现为关窗闪退 / 进程退出码不是 0）。这里先检查、再试，
    #   宁可不刷新列表，也不能把程序带崩。
    if not APP_CLOSING:
        # ★★ 2026-10-03：这里原来写的是 app.root.after(...) ——
        #   后台线程调 root.after 偶尔会卡死在 tkinter 内部，
        #   卡住就等于「扫完了但没人知道」，列表永远空着。
        #   现在走信箱（后台线程只碰一个 Python 列表，绝不碰 Tcl）。
        app._ui_threadsafe(app._on_bg_scan_done, dir_key, entries, err)


def _on_bg_scan_done(app, dir_key, entries, err):
    app._bg_scan_running_dir = None
    # ★ v25 补丁14：关窗过程中这个回调还可能被排到队列里，进来先看一眼，
    #   窗口没了就直接返回，不要再去碰已经销毁的控件。
    if getattr(app, "_closing", False):
        return
    app.end_activity()
    plain_dir_view = app._dir_view_is_plain(dir_key)
    if err is None:
        app.log_output(T("扫描完成：{k}  共 {n} 项",
                          k=dir_key, n=len(entries)))
        try:
            app.store.save_dir_entries(dir_key, entries)
        except Exception as exc:
            app.log_problem(f"写目录缓存失败：{exc}", level="error")
        if plain_dir_view:
            app._apply_dir_entries(dir_key, entries)
            app.set_status(
                T("{k}    共 {n} 项（已刷新）",
                  k=dir_key, n=len(entries)))
    else:
        # ★ v25 补丁18：目录读不到时别再当「错误」刷屏。
        #   网盘里删除过的目录、空目录、一时读不到的目录，以前每点开
        #   一次就在「问题」面板里报一次红 —— 用户反映很烦。
        #   现在把「东西不在了」这一类单独处理：只记一句普通日志、
        #   记住这个目录别再反复去试；真的读不动（权限/网络坏）才报错。
        if is_gone_error(err):
            try:
                app._dead_dirs().add(dir_key)
            except Exception:
                pass
            app.log_output(
                f"这个目录现在读不到（网盘里可能已经删掉了）：{dir_key}"
                f"  · 已跳过，不再重试")
            if plain_dir_view:
                app.set_status(
                    f"{dir_key}    目录读不到（可能已删除），已跳过")
        else:
            app.log_problem(f"目录扫描失败：{dir_key} - {err}",
                             level="error")
            if plain_dir_view:
                app.set_status(f"目录扫描失败：{err}")
    if getattr(app, "_bg_scan_pending_dir", None):
        app._try_start_bg_scan()


# ---------- ★ v25 补丁2 / ★ 2026-10-03 重写：网盘挂载改名后的路径自愈 ----------
def _apply_net_root_fixes(app, roots):
    """顺手把「指向失效网盘的索引根目录」处理好（改名 / 删掉多余的）。

    为什么要管这个：库里那些文件的路径修好了，可「索引管理」里还挂着
    一个永远连不上的旧根目录 —— 以后每次自动索引都会去摸它、白等一场。
    """
    done = []
    for r in roots:
        try:
            if r["action"] == "delete":
                with app.store._lock:
                    with app.store.conn:
                        app.store.conn.execute(
                            "DELETE FROM index_roots WHERE id = ?", (r["id"],))
                done.append("删掉多余的旧索引根：%s" % r["path"])
            else:
                with app.store._lock:
                    with app.store.conn:
                        app.store.conn.execute(
                            "UPDATE index_roots SET path = ? WHERE id = ?",
                            (r["new"], r["id"]))
                done.append("索引根改名：%s  →  %s" % (r["path"], r["new"]))
        except Exception as _e:
            note_swallowed(T("修复网盘路径：处理索引根目录失败"), _e)
    return done


# ---------- ★ v25：搜索视图的进出（含子目录搜索 / 关键字搜索共用） ----------
def _cancel_recursive_scan(app, invalidate_cache=True):
    """作废还在跑的「含子目录搜索」。

    - token +1：迟到的扫描结果回来时会被丢掉
    - invalidate_cache：连目录树缓存一起丢掉（切视图 / 重扫目录时用）
    """
    app._recursive_token = getattr(app, "_recursive_token", 0) + 1
    app._recursive_active = False
    app._recursive_roots = []
    try:
        app.file_list.search_external = False
    except Exception:
        pass
    if invalidate_cache:
        app._recursive_cache = None


def _search_scan_roots(app):
    """含子目录搜索该扫哪些目录 —— 跟现在列表显示的视图保持一致。

    - 打开某个文件夹（dir）→ 就扫这个文件夹
    - 分类库 / 全部文件 / 搜索结果 → 扫这些文件所在的目录
      （合并去重；被别的根包住的子目录会被去掉）
    返回 (roots, 说明文字)
    """
    spec = app._view_spec or {}
    kind = spec.get("kind")
    if app.view_mode == "dir" or kind == "dir":
        d = str(app.current_dir) if app.current_dir else ""
        return ([d] if d else []), "当前文件夹"
    try:
        all_paths = app._current_view_paths()
    except Exception:
        all_paths = []
    dirs = []
    seen = set()
    for p in all_paths:
        d = os.path.dirname(p)
        if d and d not in seen:
            seen.add(d)
            dirs.append(d)
    # ★ 这些文件基本都在同一棵树下时，直接用它们的公共祖先当
    #   唯一基点（否则几十上百个目录要一个一个扫，网盘上等到哭）
    if len(dirs) > 1:
        try:
            common = os.path.commonpath(dirs)
            if path_depth(common) >= 4:
                note = f"（{len(dirs)} 个目录合并成公共目录）"
                dirs = [common]
            else:
                note = ""
        except Exception:
            note = ""
    else:
        note = ""
    roots, truncated = collapse_roots(dirs, RECURSIVE_MAX_ROOTS)
    label = {"cat": "当前分类里这些文件所在目录",
             "all": "全部文件所在目录",
             "paths": "当前结果所在目录"}.get(kind, "当前视图的文件目录")
    if note:
        label += note
    if truncated:
        label += f"（目录太多，只扫最靠上的 {RECURSIVE_MAX_ROOTS} 个）"
    return roots, label


# ---------- ★ 文件列表：含子目录搜索 ----------
def _on_recursive_search(app, keyword):
    """FileList 的"含子目录"模式触发（按回车）。"""
    if not keyword:
        # 清除搜索 → 还原搜索前的视图
        app._cancel_recursive_scan(invalidate_cache=False)
        app._restore_view_after_search()
        return

    # ★ v25：分类 / 全部文件 / 搜索结果视图里，库里本来就存着完整
    #   路径，直接按完整路径查库就等于「含子目录」——秒回，
    #   不必去扫盘（分类里的文件散在好几个盘时，扫盘要几分钟）。
    kind = (app._view_spec or {}).get("kind")
    if app.view_mode != "dir" and kind != "dir":
        app.log_output(
            f"含子目录搜索：按完整路径查库「{keyword}」（不用扫盘）")
        app._on_global_search(keyword)
        app.list_title.config(text=f"含子目录搜索：{keyword}")
        return

    roots, label = app._search_scan_roots()
    if not roots:
        messagebox.showinfo(
            "没有可搜索的目录",
            "当前列表里没有可以递归搜索的目录。\n\n"
            "先打开一个文件夹，或者选中一个分类库再搜。",
            parent=app.root)
        return
    app._begin_search_view()
    # ★ 每次回车都算新一轮：token 换掉，旧扫描回来也不认
    app._cancel_recursive_scan(invalidate_cache=False)
    app._recursive_active = True
    token = app._recursive_token
    app._recursive_roots = list(roots)
    key = "|".join(sorted(roots))
    # ★ v25：每次回车都重新扫一遍（以前是复用旧缓存，用户刚
    #   下载/删掉的文件搜不到，结果看着「不正常」）。
    app.begin_activity("扫描当前目录树…")
    app.log_output(
        f"含子目录搜索：扫描 {len(roots)} 个目录（{label}）")
    for r in roots[:6]:
        app.log_output(f"    · {r}")

    def worker():
        rows = []
        truncated = False
        try:
            for base in roots:
                if app._recursive_token != token:
                    break
                for root, _dirs, files in os.walk(base):
                    if app._recursive_token != token:
                        break
                    for fn in files:
                        rows.append(os.path.join(root, fn))
                        if len(rows) >= RECURSIVE_MAX_FILES:
                            truncated = True
                            break
                    if truncated:
                        break
                if truncated:
                    break
        except Exception as exc:
            app.log_problem(f"目录树扫描失败：{exc}", level="error")
        try:
            app._ui_threadsafe(app._on_recursive_scan_done,
                                token, key, rows, keyword, truncated)
        except Exception as exc:
            note_swallowed(T("worker(_on_recursive_scan_done)：回主线程通知失败"),
                           exc, level="warn")

    threading.Thread(target=worker, daemon=True).start()


def _on_recursive_scan_done(app, token, key, paths, keyword,
                            truncated=False):
    """目录树扫完了。token 对不上 → 这轮已经作废（清空了搜索 / 换了视图）。"""
    if token != app._recursive_token or not app._recursive_active:
        app.log_output(T("含子目录搜索：这轮扫描已作废，结果丢掉"))
        return
    app.end_activity()
    app._recursive_cache = {"key": key, "paths": paths,
                             "ts": time.time()}
    app.log_output(f"含子目录搜索：扫描到 {len(paths)} 个文件")
    if truncated:
        app.log_problem(
            f"目录树太大，只看了前 {RECURSIVE_MAX_FILES} 个文件，"
            f"结果可能不全", level="warn")
    app._apply_recursive_filter(keyword)


def _apply_recursive_filter(app, keyword):
    cache = app._recursive_cache
    if not cache:
        return
    paths = cache["paths"]
    kw = (keyword or "").strip().lower()
    if kw:
        paths = [p for p in paths
                 if kw in os.path.basename(p).lower()]
    # 切换成"筛选"视图
    app.list_title.config(text=T("搜索结果（含子目录）"))
    app.list_info.config(text=f"关键字：{keyword or '（空）'}")
    # ★ 关键字这里已经筛过了，别再让 FileList 按开关二次过滤
    app.file_list.search_external = True
    app._invalidate_tag_scope()
    app._view_spec = {"kind": "paths", "paths": list(paths)}
    app._page = 0
    app._load_current_page()
    app.set_status(
        f"含子目录搜索：{len(paths)} 个结果")


def _on_current_view_scan_done(app):
    app.end_activity()
    try:
        app.refresh_tags()
        app.refresh_rows_tags()
        app.refresh_categories()
        app.set_status(T("当前列表已重新打标签"))
    except Exception as exc:
        # ★★ 2026-10-03：原来这里只 print，错误完全不会显示给用户，
        #   连日志面板都不进。改成走 log_problem，至少能在「🔔 问题」面板看见。
        app.log_problem(f"扫描完成回调失败：{exc}", level="error")


def _any_scan_dialog_open(app):
    try:
        for w in app.root.winfo_children():
            if isinstance(w, ScanProgressDialog):
                return True
    except Exception:
        pass
    return False


# ---------- 闲时：索引扫描 ----------
def _start_idle_index_job(app):
    if INDEX_SCAN_EVENT.is_set():
        return
    INDEX_SCAN_EVENT.set()
    app._idle_jobs_running.add("index")
    try:
        app.log_output(
            "☁ 闲时任务：开始慢慢重扫索引根目录"
            "（顺手把文件大小补全，列表里就不会再是「?」了）…")
    except Exception:
        pass
    threading.Thread(target=app._idle_index_worker,
                     daemon=True).start()


def _idle_index_worker(app):
    roots_done = 0
    dirs = 0
    files = 0
    stopped = False
    # ★ v25 补丁17：闲时扫描也优先走 CloudDrive2 本地接口。
    #   以前这一趟是「隔着挂载盘一个个摸」，网盘要摸 20~30 分钟；
    #   走 API 之后几分钟就完了，少折腾网盘（也少撞限流）。
    api_client = None
    try:
        api_client, _why = cd_api_client_from_settings()
        try:
            app.log_output(T("☁ 闲时任务：") + _why)
        except Exception:
            pass
    except Exception:
        api_client = None
    try:
        try:
            ids = [r["id"] for r in app.store.all_index_roots()
                   if r.get("enabled")]
        except Exception:
            ids = []
        for rid in ids:
            if app._idle_seconds() < IDLE_STOP_WITHIN_SEC:
                stopped = True
                break
            res = scan_index_roots(
                app.store, [rid],
                cancel_flag=(lambda: app._idle_seconds()
                             < IDLE_STOP_WITHIN_SEC),
                delay=IDLE_INDEX_PAUSE,
                api_client=api_client)
            if res:
                _rid, _p, d, f, _err = res[0]
                dirs += d
                files += f
            roots_done += 1
    except Exception as _e:
        note_swallowed(T("闲时任务：索引扫描失败"), _e)
    finally:
        try:
            if api_client is not None:
                api_client.close()
        except Exception:
            pass
        INDEX_SCAN_EVENT.clear()
    try:
        app._ui_threadsafe(app._on_idle_index_done,
                            roots_done, dirs, files, stopped)
    except Exception as exc:
        note_swallowed(T("worker(_on_idle_index_done)：回主线程通知失败"),
                       exc, level="warn")


def _on_idle_index_done(app, roots_done, dirs, files, stopped):
    app._idle_jobs_running.discard("index")
    try:
        save_idle_settings(index_last=time.time())
    except Exception:
        pass
    msg = (f"☁ 闲时任务：索引扫描跑完（{roots_done} 个根目录 / "
           f"{dirs} 个目录 / {files} 个文件"
           f"{'；你回来了，提前收工' if stopped else ''}）")
    try:
        app.log_output(msg)
        app.set_status(msg)
    except Exception:
        pass
    # 当前目录重新读一次本地缓存（新文件 / 大小立刻可见）
    try:
        if app.view_mode == "dir" and app.current_dir:
            app.load_directory(app.current_dir)
    except Exception:
        pass
    app._refresh_dialog_hints()
