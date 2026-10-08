# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「标签操作」这组方法。

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
_MUTABLE = ['EXPORT_DIR']
_NEED = ['CategoryHiddenTagsDialog', 'CategoryTagLinkDialog', 'EXPORT_DIR', 'FILE_TAGS_FILE', 'RemoveFileTagsDialog', 'SimpleInputDialog', 'StarGraphEditor', 'T', 'TAGS_FILE', 'TagBoxPicker', 'note_swallowed', 'save_ui_setting']
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


def _reinsert_tag_frame(app):
    """★ v25 补丁41：把右侧面板按正确顺序摆好。

    ★ 为什么不用 paned.insert()？
      实测（就是这条日志的元凶）：
        · ttk.PanedWindow 的 insert / forget **索引语义和 panes()
          返回的列表对不上** —— forget 一个中间面板之后，
          再 insert 到「看起来正确」的序号，Tk 会直接抛
          "Slave index N out of bounds"；
        · 而且 insert 的序号**不能超过当前面板数**，按 4 个面板
          算出来的位置去插，一旦此刻只挂着 2 个就必爆。
      这个报错原来被 except 吞掉、只记了一条「切换预览窗格失败」，
      但真实后果是**面板没插进去**（预览窗格点了没反应）。

    ★ 所以改成最笨也最可靠的办法：**全撤掉、按正确顺序重加一遍**。
      ttk.PanedWindow 一共就 4 个面板，重加一次的开销可以忽略
      （实测几十微秒），换来的是永远不可能越界。
    顺序：分类库 → 文件列表 → 预览窗格 → 标签库
          （不在的那几个自动跳过）
    """
    wanted = [app.sidebar, app.list_frame, app.preview_frame,
              app.tag_frame]

    def _in_paned(w):
        """这个面板现在是不是挂在 paned 上。"""
        try:
            return str(w) in [str(p) for p in app.paned.panes()]
        except Exception:
            return False

    # ★ 分类库「应不应该显示」用**记忆**判断：
    #   第一次调用时记下它当时在不在，以后就照这个记忆走。
    #   为什么：_reinsert_tag_frame 会先全撤再重加，撤完那一刻
    #   「在不在」当然变成 False —— 如果每次都现查，第一次撤完
    #   分类库就永久消失了（实测踩过这个坑）。
    if not hasattr(app, "_sidebar_wanted"):
        app._sidebar_wanted = _in_paned(app.sidebar)
    visible = {
        str(app.sidebar): bool(app._sidebar_wanted),
        # ★ 文件列表**必须永远在**（它是主界面，丢了就什么都点不了）
        str(app.list_frame): True,
        str(app.preview_frame): bool(
            getattr(app, "_preview_visible", False)),
        str(app.tag_frame): bool(
            getattr(app, "_taglib_visible", True)),
    }
    # 先全撤掉（只撤真的挂着的，免得 Tk 报 "not managed"）
    for w in list(app.paned.panes()):
        try:
            app.paned.forget(w)
        except Exception:
            pass
    # 再按正确顺序加回来
    for w in wanted:
        if not visible.get(str(w), False):
            continue
        try:
            weight = 5 if w is app.list_frame else 0
            app.paned.add(w, weight=weight)
        except Exception as _e:
            note_swallowed(T("重新排列右侧面板失败"), _e)


def toggle_tagbox(app):
    app.tagbox_visible = not getattr(app, "tagbox_visible", False)
    try:
        save_ui_setting("tagbox_visible", bool(app.tagbox_visible))
    except Exception:
        pass
    app._pack_tagbox()
    try:
        app.set_status(
            "标签盒：%s" % ("已显示（独立窗口，可拖动 / 缩放 / 置顶）"
                           if app.tagbox_visible else "已收起"))
    except Exception:
        pass


def open_tagbox_picker(app):
    """从标签库勾选放进标签盒（菜单/按钮都走这里）。"""
    try:
        TagBoxPicker(app.root, app.tagbox)
    except Exception as exc:
        messagebox.showerror("标签盒", "打不开勾选窗口：%s" % exc,
                             parent=app.root)


def refresh_rows_tags(app):
    paths = [r["path"] for r in app.file_list.rows]
    if not paths:
        return
    # ★ v22：这里不再自动跑自动标签规则（改为手动点「🏷 重读标签」），
    #   只按数据库里已有的标签刷新显示。
    tag_map = app.store.tags_for_paths(paths)
    app.file_list.refresh_all_tags(tag_map)
    for r in app._base_rows:
        if r["path"] in tag_map:
            r["tags"] = tag_map[r["path"]]
    # ★ v26：标签真的变了 → 把统计缓存作废，下次重新算
    app._stats_cache_key = None
    app._apply_stats_display()
    try:
        app.refresh_categories()
        app.refresh_tags()
    except Exception:
        pass


def link_category_tags(app, cid, name):
    dlg = CategoryTagLinkDialog(app.root, app.store, cid, name)
    if not dlg.saved:
        return
    app.refresh_categories()
    if app.view_mode == "cat" and app.current_cat_id == cid:
        app.show_category(cid)
    n = len(app.store.linked_tag_ids(cid))
    app.set_status(f"分类「{name}」已关联 {n} 个标签超链接")


def show_category_tag_links(app, cid, name):
    linked = app.store.linked_tag_ids(cid)
    if not linked:
        messagebox.showinfo("已关联标签",
                            f"分类「{name}」尚未关联任何标签",
                            parent=app.root)
        return
    tag_map = {t[0]: t[1] for t in app.store.all_tags()}
    names = [tag_map.get(t, f"#{t}") for t in linked]
    messagebox.showinfo("已关联标签",
                        f"分类「{name}」关联了 {len(names)} 个标签：\n\n"
                        + "\n".join("· " + n for n in names),
                        parent=app.root)


# ---------- ★ 分类的"打开时自动屏蔽标签" ----------
def edit_category_hidden_tags(app, cid, name):
    dlg = CategoryHiddenTagsDialog(app.root, app.store, cid, name)
    if not dlg.saved:
        return
    n = len(app.store.get_category_hidden_tags(cid))
    if n:
        app.set_status(f"分类「{name}」已设置 {n} 个打开时自动屏蔽的标签")
    else:
        app.set_status(f"分类「{name}」不再自动屏蔽任何标签")
    if app.view_mode == "cat" and app.current_cat_id == cid:
        app.show_category(cid)


def add_selection_to_category(app, cid, cname):
    paths = app.file_list.get_selection()
    if not paths:
        return
    n = 0
    for path in paths:
        app.store.add_file_to_category(cid, path)
        n += 1
    app.refresh_categories()
    if app.view_mode == "cat":
        app.show_category(app.current_cat_id)
    app.set_status(f"已把 {n} 项添加到分类「{cname}」")


def _tag_base_spec(app):
    """标签筛选前的原始视图规格（没在筛选时就是当前视图）。"""
    return app._tag_filter_base_spec or app._view_spec or {}


def _on_tag_scope_changed(app, scope):
    if scope == "view":
        app._start_tag_scope_scan()
        app.set_status(T("标签条作用范围：整个视图（正在统计标签…）"))
    else:
        try:
            app.file_list.set_tag_scope_stats(None)
        except Exception:
            pass
        if app._restore_tag_filter_view():
            app.set_status(T("标签条作用范围：当前页（已还原视图）"))
        else:
            app.set_status(T("标签条作用范围：当前页"))


def _on_tag_filter_view(app):
    """FileList 在「整个视图」范围下点了标签 → 重建文件列表。"""
    app._apply_tag_scope_filter()


def _restore_tag_filter_view(app):
    """找出被标签筛选替换掉的原始视图并还原。"""
    if app._tag_filter_base_spec is None:
        return False
    app._view_spec = app._tag_filter_base_spec
    app._tag_filter_base_spec = None
    app._page = 0
    app._load_current_page()
    return True


def _refresh_current_dir_tags(app):
    """🏷 重读标签：按「自动标签规则」把当前视图的文件更新一遍。

    v22 起自动标签规则不再自动执行，只有这里（以及
    「⚙ 自动标签规则…」窗口里的扫描按钮）才会真正跑一遍。
    """
    paths = app._current_view_paths()
    if not paths:
        # 兜底：当前视图没有文件时，退回「所有已记录文件」
        try:
            paths = list(app.store.all_files())
        except Exception:
            paths = []
    if not paths:
        messagebox.showinfo("提示", T("当前没有可更新标签的文件"),
                            parent=app.root)
        return
    if not messagebox.askyesno(
            "重读标签",
            f"按「自动标签规则」重新扫描并更新标签？\n\n"
            f"本次范围：当前视图的 {len(paths)} 个文件\n"
            f"（数据量大时可能需要较长时间）"):
        return
    app.begin_activity(f"正在更新 {len(paths)} 个文件的标签…")
    app.log_output(
        f"重读标签（手动触发自动规则）：{len(paths)} 个文件")
    
    def worker():
        total = len(paths)
        changed_all = 0
        step = 300
        try:
            for i in range(0, total, step):
                chunk = paths[i:i + step]
                try:
                    changed_all += app.store.sync_auto_tags_for_paths(
                        chunk)
                except Exception as exc:
                    app.log_problem(
                        f"第 {i + 1} 个起的批次失败：{exc}",
                        level="warn")
                app.log_progress(
                    f"已处理 {min(i + step, total)} / {total}"
                    f"（累计更新 {changed_all}）")
            app.log_output(
                f"重读标签完成：{changed_all} 个文件的标签有变化")
        except Exception as exc:
            app.log_problem(f"重读标签失败：{exc}", level="error")
        try:
            app._ui_threadsafe(app._on_manual_retag_done,
                                changed_all, total)
        except Exception as exc:
            note_swallowed(T("worker(_on_manual_retag_done)：回主线程通知失败"),
                           exc, level="warn")
            
    threading.Thread(target=worker, daemon=True).start()


def clear_selected_tags(app):
    paths = app.file_list.get_selection()
    if not paths:
        return
    if not messagebox.askyesno("确认", f"清除所选 {len(paths)} 个文件的全部标签？"):
        return
    for path in paths:
        app.store.clear_file_tags(path)
    app.refresh_tags()
    app.refresh_rows_tags()


def remove_selected_tags(app):
    """★★ v26（2026-10-01）：右键「去除文件上的标签…」。

    把选中文件身上的标签全列出来，你勾哪些就去掉哪些，
    确认一次才真的动手。标签本身不会被删掉。
    """
    paths = list(app.file_list.get_selection() or [])
    if not paths:
        messagebox.showinfo("去除标签", T("先选中文件。"), parent=app.root)
        return
    try:
        dlg = RemoveFileTagsDialog(app.root, app, app.store, paths)
        app.root.wait_window(dlg)
        chosen = dlg.result
    except Exception as exc:
        messagebox.showerror("去除标签", "打不开窗口：%s" % exc,
                             parent=app.root)
        return
    if not chosen:
        return
    total = 0
    # ★ 2026-10-06：撤销记录里要存**标签名**（id 会变、名字才是人看得懂的），
    #   所以这里先把 id 翻成名字，再去删。
    _name_of = {}
    try:
        for _tid in (chosen or []):
            _row = app.store.tag_by_id(_tid)
            if _row:
                _name_of[_tid] = _row["name"]
    except Exception:
        _name_of = {}
    _hit = []
    for p in paths:
        try:
            _n = app.store.remove_file_tag_ids(p, chosen)
            total += _n
            if _n:
                for _tid in (chosen or []):
                    _nm = _name_of.get(_tid)
                    if _nm:
                        _hit.append((p, _nm))
        except Exception as exc:
            note_swallowed(T("去除标签失败：{x}", x=p), exc)
    # 删完之后重新同步一下继承标签（父级还在的话该补回来）
    try:
        for p in paths:
            fid = app.store._fid(p, create=False)
            if fid is not None:
                app.store.resync_file(fid)
    except Exception as exc:
        note_swallowed(T("去除标签后同步失败"), exc)
    app.refresh_tags()
    app.refresh_rows_tags()
    if _hit:
        app.undo_record("tag_remove", _hit)
    app.set_status("已从 %d 个文件上去掉 %d 个标签（共 %d 条）"
                    % (len(paths), len(chosen), total))


def add_file_tags_to_box(app):
    """★★ v26（2026-10-01）：右键「把标签全部加入标签盒」。

    把选中文件身上的所有标签一次性全塞进标签盒，
    方便你接下来拖到别的文件上。（不动任何数据，只是把标签放进盒子）
    """
    paths = list(app.file_list.get_selection() or [])
    if not paths:
        messagebox.showinfo("标签盒", T("先选中文件。"), parent=app.root)
        return
    try:
        info = app.store.tags_for_paths(paths) or {}
    except Exception as exc:
        messagebox.showerror("标签盒", "读标签失败：%s" % exc,
                             parent=app.root)
        return
    want = {}
    for p in paths:
        for rec in (info.get(p) or []):
            try:
                want[int(rec[0])] = rec[1]
            except Exception:
                continue
    if not want:
        messagebox.showinfo("标签盒", T("这些文件上一个标签都没有。"),
                            parent=app.root)
        return
    if not getattr(app, "tagbox", None):
        try:
            app.toggle_tagbox()
        except Exception:
            pass
    box = getattr(app, "tagbox", None)
    if box is None:
        messagebox.showinfo("标签盒", T("标签盒打不开。"), parent=app.root)
        return
    try:
        have = set(box.box_ids())
    except Exception:
        have = set()
    added = 0
    for tid, name in want.items():
        if tid in have:
            continue
        try:
            box.add_tag(tid, name)
            added += 1
        except Exception as exc:
            note_swallowed(T("把标签放进标签盒失败"), exc)
    try:
        box.deiconify()
        box.lift()
    except Exception:
        pass
    app.set_status("已把 %d 个标签放进标签盒（%d 个本来就在里面）"
                    % (added, len(want) - added))


def refresh_tags(app):
    app.tag_thumb.reload(app.store)


def _on_tags_dropped(app, tag_names, x_root, y_root):
    """★★ v26（2026-10-01）：一次拖**好几个**标签到文件上。

    标签盒里多选了几个标签再往文件列表拖时走这里 ——
    每一个够得着的文件，都会被打上这一批标签。
    """
    names = [n for n in (tag_names or []) if n]
    if not names:
        return
    try:
        left = app.file_list.winfo_rootx()
        top = app.file_list.winfo_rooty()
        right = left + app.file_list.winfo_width()
        bottom = top + app.file_list.winfo_height()
    except Exception:
        return
    if not (left <= x_root <= right and top <= y_root <= bottom):
        app.set_status(T("把标签拖到文件列表上才能打标签"))
        return
    paths = list(app.file_list.get_selection() or [])
    if not paths:
        return
    ok = 0
    _hit = []          # ★ 2026-10-06：记撤销
    for p in paths:
        for nm in names:
            try:
                app.store.add_tag_to_file(p, nm)
                ok += 1
                _hit.append((p, nm))
            except Exception as exc:
                note_swallowed(T("批量打标签失败"), exc)
    app.refresh_tags()
    app.refresh_rows_tags()
    if _hit:
        app.undo_record("tag_add", _hit)
    app.set_status("已给 %d 个文件打上 %d 个标签（共 %d 次）"
                    % (len(paths), len(names), ok))


def _on_tag_dropped(app, tag_name, x_root, y_root):
    try:
        left = app.file_list.winfo_rootx()
        top = app.file_list.winfo_rooty()
        right = left + app.file_list.winfo_width()
        bottom = top + app.file_list.winfo_height()
    except Exception:
        left = top = right = bottom = 0

    inside = left <= x_root <= right and top <= y_root <= bottom
    if not inside:
        return

    selected = app.file_list.get_selection()
    target_path = app.file_list.get_path_at_y(y_root, x_root)

    if target_path and target_path not in selected:
        targets = [target_path]
    elif selected:
        targets = list(selected)
    elif target_path:
        targets = [target_path]
    else:
        return

    added_auto = set()
    _hit = []          # ★ 2026-10-06：记撤销
    for path in targets:
        info = app.store.add_tag_to_file(path, tag_name)
        _hit.append((path, tag_name))
        for a in info.get("ancestors") or []:
            added_auto.add(a)

    app.refresh_tags()
    app.refresh_rows_tags()
    if _hit:
        app.undo_record("tag_add", _hit)

    extra = ""
    if added_auto:
        extra = f"（附带上级：{'、'.join(sorted(added_auto))}）"

    if len(targets) == 1:
        app.set_status(
            f"已给「{os.path.basename(targets[0])}」添加标签「{tag_name}」{extra}")
    else:
        app.set_status(
            f"已给 {len(targets)} 个文件添加标签「{tag_name}」{extra}")


def _on_tag_right_click(app, event, tid, name):
    m = tk.Menu(app, tearoff=0)
    m.add_command(label=f"标签：{name}", state="disabled")
    m.add_separator()
    m.add_command(label=T("查看它的文件"),
                  command=lambda: app.show_files_with_tag(tid, name))
    m.add_separator()
    m.add_command(label=T("重命名…"), command=lambda: app.rename_tag(tid))
    m.add_command(label=T("更换颜色…"), command=lambda: app.recolor_tag(tid))
    m.add_separator()
    m.add_command(label=T("在星图里打开"), command=app.open_tag_tree)
    m.tk_popup(event.x_root, event.y_root)


def _on_tag_double_click(app, tid, name):
    app.show_files_with_tag(tid, name)


def show_files_with_tag(app, tid, name):
    paths = app.store.find_files([name], match_all=True)
    app.view_mode = "filter"
    app.current_cat_id = None
    app._cancel_recursive_scan(invalidate_cache=True)
    app._search_return_state = None
    app._clear_stats_filter()
    app._reset_category_hidden_tags()
    app.list_title.config(text=f"标签「{name}」的文件")
    app.path_var.set(f"标签：{name}")
    app.list_info.config(text=f"按标签：{name}")
    app._invalidate_tag_scope()
    app._view_spec = {"kind": "paths", "paths": paths}
    app._page = 0
    app._load_current_page()
    app.sidebar.set_selected(None, None)
    app.set_status(f"标签「{name}」→ {app._page_total} 个文件")


def rename_tag(app, tid):
    row = None
    for r in app.store.all_tags():
        if r[0] == tid:
            row = r
            break
    if row is None:
        return
    name = row[1]
    new_name = SimpleInputDialog(app.root, "重命名标签", initial=name).result
    if not new_name or new_name == name:
        return
    try:
        app.store.rename_tag(tid, new_name)
    except Exception as exc:
        messagebox.showerror("错误", str(exc))
        return
    app.refresh_tags()
    app.refresh_rows_tags()


def recolor_tag(app, tid):
    color = "#3498db"
    for r in app.store.all_tags():
        if r[0] == tid:
            color = r[2]
            break
    _rgb, hexv = colorchooser.askcolor(color=color, title=T("选择标签颜色"))
    if not hexv:
        return
    app.store.set_tag_color(tid, hexv)
    app.refresh_tags()
    app.refresh_rows_tags()


def open_tag_tree(app):
    # ★ v25 补丁42：把 app 也传进去 —— 星图要用它找到「标签盒」，
    #   才能实现「Shift + 拖标签 → 拖进标签盒」和右键「放进标签盒」。
    StarGraphEditor(app.root, app.store,
                    on_saved=app._on_star_saved, app=app)
    # 窗口关闭后整体刷新一次
    app.refresh_tags()
    app.refresh_rows_tags()
    app.refresh_categories()
    if app.view_mode == "cat" and app.current_cat_id:
        app.show_category(app.current_cat_id)


def export_tags_structure(app):
    try:
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        n = app.store.export_tags_structure(TAGS_FILE)
    except Exception as exc:
        messagebox.showerror("导出失败", str(exc), parent=app.root)
        return
    app.set_status(f"已导出 {n} 个标签结构到：{TAGS_FILE}")
    messagebox.showinfo(
        "导出成功",
        f"已导出 {n} 个标签的结构（支持多父级）到：\n\n{TAGS_FILE}",
        parent=app.root)


def export_file_tags(app):
    try:
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        n = app.store.export_file_tags(FILE_TAGS_FILE)
    except Exception as exc:
        messagebox.showerror("导出失败", str(exc), parent=app.root)
        return
    app.set_status(f"已导出 {n} 个文件的标签信息到：{FILE_TAGS_FILE}")
    messagebox.showinfo(
        "导出成功",
        f"已导出 {n} 个文件的标签信息（仅手动标签）到：\n\n{FILE_TAGS_FILE}",
        parent=app.root)


def import_tags_structure(app):
    path = filedialog.askopenfilename(
        title=T("选择标签结构文件"),
        initialdir=str(EXPORT_DIR),
        filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")])
    if not path:
        return
    if not messagebox.askyesno(
            "确认导入",
            "导入标签结构会：\n"
            "  · 创建缺失的标签\n"
            "  · 更新已存在标签的颜色\n"
            "  · 根据文件里的 parents 重建图关系（支持多父级）\n"
            "  · 导入完自动同步所有文件的标签链\n\n"
            "已导入标签的原有关系会被重建。继续吗？",
            parent=app.root):
        return
    try:
        info = app.store.import_tags_structure(path, auto_resync=True)
    except Exception as exc:
        messagebox.showerror("导入失败", str(exc), parent=app.root)
        return
    app.refresh_tags()
    app.refresh_rows_tags()
    app.refresh_categories()
    if app.view_mode == "cat" and app.current_cat_id:
        app.show_category(app.current_cat_id)

    resync = info.get("resync") or {}
    added = resync.get("added", 0)
    removed = resync.get("removed", 0)
    files_affected = resync.get("files_affected", 0)
    app.set_status(
        f"标签结构已导入：新建 {info['created']}、更新 {info['updated']}、"
        f"关联 {info['linked']}；同步影响 {files_affected} 个文件")
    messagebox.showinfo(
        "导入成功",
        f"标签结构已导入：\n\n"
        f"  文件中共有标签：{info['total_in_file']} 个\n"
        f"  新建标签：{info['created']} 个\n"
        f"  更新颜色：{info['updated']} 个\n"
        f"  建立父子关系：{info['linked']} 条\n\n"
        f"已自动同步所有文件的标签链：\n"
        f"  受影响文件：{files_affected} 个\n"
        f"  新增关联：{added} 条\n"
        f"  移除关联：{removed} 条",
        parent=app.root)


def import_file_tags(app):
    path = filedialog.askopenfilename(
        title=T("选择文件标签信息文件"),
        initialdir=str(EXPORT_DIR),
        filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")])
    if not path:
        return
    skip = messagebox.askyesno(
        "是否跳过不存在的文件？",
        "如果原路径的文件已经不存在，是否跳过？\n\n"
        "  · 是 → 只导入磁盘上仍存在的文件（推荐）\n"
        "  · 否 → 无论磁盘上是否存在都记录到数据库",
        parent=app.root)
    try:
        info = app.store.import_file_tags(path, skip_missing=skip)
    except Exception as exc:
        messagebox.showerror("导入失败", str(exc), parent=app.root)
        return
    app.refresh_tags()
    app.refresh_rows_tags()
    app.refresh_categories()
    if app.view_mode == "cat" and app.current_cat_id:
        app.show_category(app.current_cat_id)

    app.set_status(
        f"文件标签信息已导入：{info['files']} 个文件、新增 {info['added_tags']} 条关联"
        f"（跳过 {info['skipped']}）")
    messagebox.showinfo(
        "导入成功",
        f"文件标签信息已导入：\n\n"
        f"  文件中共有文件：{info['total_in_file']} 个\n"
        f"  实际导入文件：{info['files']} 个\n"
        f"  新增标签关联：{info['added_tags']} 条\n"
        f"  跳过（不存在或无标签）：{info['skipped']} 个\n\n"
        f"注意：导入只做添加，不会删除文件上已有的标签。",
        parent=app.root)


def scan_current_view_tags(app):
    """对当前文件列表里显示的文件跑一遍自动标签规则。
       在后台线程执行，主界面不卡。"""
    paths = [r["path"] for r in app.file_list.rows]
    if not paths:
        messagebox.showinfo("提示", T("当前列表里没有文件"), parent=app.root)
        return
    app.log_output(f"手动扫描当前列表 {len(paths)} 个文件的标签")
    app.begin_activity(f"为当前 {len(paths)} 个文件打标签")

    def worker():
        total = len(paths)
        changed_all = 0
        batch = 50
        try:
            for i in range(0, total, batch):
                chunk = paths[i:i + batch]
                try:
                    changed_all += app.store.sync_auto_tags_for_paths(chunk)
                except Exception as e:
                    app.log_problem(f"批次 {i} 失败：{e}", level="warn")
                app.log_progress(
                    f"已处理 {min(i + batch, total)} / {total}"
                    f"（累计更新 {changed_all}）")
            app.log_output(
                f"当前列表扫描完成：{changed_all} 个文件被更新")
        except Exception as exc:
            app.log_problem(f"扫描失败：{exc}", level="error")
        try:
            app._ui_threadsafe(app._on_current_view_scan_done)
        except Exception as exc:
            note_swallowed(T("worker(_on_current_view_scan_done)：回主线程通知失败"),
                           exc, level="warn")

    threading.Thread(target=worker, daemon=True).start()


def clear_hidden_tags(app):
    try:
        app.file_list.clear_hidden_tags()
        app.set_status(T("已恢复全部被屏蔽的标签"))
    except Exception as exc:
        print(exc)


def clear_tag_filter(app):
    try:
        app.file_list._clear_tag_filter()
        app.set_status(T("已清除标签筛选"))
    except Exception as exc:
        print(exc)
