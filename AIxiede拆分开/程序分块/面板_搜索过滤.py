# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「搜索过滤」这组方法。

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
_MUTABLE = []
_NEED = ['T']
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
                g[_n] = _Borrowed(_n) if _n in _MUTABLE else _v
        except Exception:
            pass


# ---------- 兜底（★ 它会吃掉错误，所以要专门测"用的哪一份"）----------
def _fallback():
    g = globals()
    for _n in _NEED:
        if g.get(_n) is None:
            g[_n] = _Borrowed(_n)


_fallback()


def _focus_search_entry(app):
    """★ Ctrl+F：跳到搜索框。

    ★★ 2026-10-07 修「Ctrl+F 之后界面整体变淡，近视看不清」（用户报）：
      病根不在 `focus_set()` 本身，而在**它顺带触发的"全选高亮"**。
      Tk 的 Entry 一拿到焦点、如果里面有字，很多情况下会显示成
      **选中态**（浅蓝底 `select_bg` + 深灰字）——
      原来那段 `select_bg` 是 `#cfe2ff`，**一满行浅蓝铺在搜索框里**，
      用户看到的就是"界面变淡了、看不清"。
      （浅色皮肤下尤其明显；深色皮肤下 `#31456b` 也偏闷。）

      修法三件（都很轻，不引入新状态）：
        ① 拿焦点之后，**把光标放到末尾、并且清掉选中区**
           —— 这样就是"正常白底 + 光标在最后"，不再有满行高亮。
        ② 顺手 `selection_clear()`，双保险（有些 Tk 版本 ① 不够）。
        ③ 最后把当前搜索内容**报给状态栏** —— 让用户知道
           "已经跳到搜索框了、现在在搜什么"，这也算补上 #46 说的那种"反馈"。
    """
    try:
        se = app.file_list.search_entry
    except Exception:
        return
    try:
        se.focus_set()
    except Exception:
        pass
    # ① + ② 去掉"全选高亮"，光标落到末尾
    try:
        n = len(se.get() or "")
        se.icursor(n)
        se.selection_clear()
    except Exception:
        pass
    # ③ 给个反馈（不吵，只写状态栏）
    try:
        cur = (se.get() or "").strip()
        if cur:
            app.set_status(T("搜索框已聚焦，当前搜索：{x}", x=cur))
        else:
            app.set_status(T("搜索框已聚焦，输入关键字即可搜索"))
    except Exception:
        pass


def _dir_view_is_plain(app, dir_key):
    """★ v25：现在显示的到底是不是「这个目录的普通文件列表」。

    搜索（含子目录 / 关键字）、标签筛选、分类视图下都不是 ——
    这时后台目录扫描回来了也不能去改列表，否则会把搜索结果
    冲成整个目录的文件。
    """
    if app.view_mode != "dir" or not app.current_dir:
        return False
    if str(app.current_dir) != dir_key:
        return False
    spec = app._view_spec or {}
    if spec.get("kind") != "dir":
        return False
    if app._tag_filter_base_spec is not None:
        return False
    return True


# ---------- ★ 重读标签（唯一会执行自动标签规则的手动入口）----------
def _current_view_paths(app):
    """返回「当前视图」里显示的文件路径（不打分页，取全集）。

    - 打开某个文件路径（dir）→ 这个目录里的文件
    - 打开左侧某个分类库（cat）→ 这个分类里的文件
    - 全部文件（all）→ 所有已记录的文件
    - 搜索 / 筛选（paths）→ 结果里的文件
    """
    spec = app._view_spec or {}
    kind = spec.get("kind")
    try:
        if kind == "dir":
            return list(spec.get("all_paths") or [])
        if kind == "cat":
            cid = spec.get("cid")
            if cid is None:
                return []
            return list(app.store.files_in_category(cid))
        if kind == "paths":
            return list(spec.get("paths") or [])
        if kind == "all":
            return list(app.store.all_files())
    except Exception as exc:
        app.log_problem(f"取当前视图文件失败：{exc}", level="warn")
    return []


def _begin_search_view(app):
    """★ v25：搜索要换视图了 —— 记下现在的视图，并清掉遗留的标签筛选。

    否则会出现两种「结果不正常」：
      1) 上一次的「整库标签筛选」把搜索结果悄悄砍一刀；
      2) 清空搜索后回不到原来的分类 / 全部文件（跑到某个文件夹去）。
    """
    if app._search_return_state is None:
        spec = app._tag_filter_base_spec or app._view_spec
        state = {
            "spec": dict(spec) if isinstance(spec, dict) else None,
            "view_mode": app.view_mode,
            "cat_id": app.current_cat_id,
            "dir": str(app.current_dir) if app.current_dir else None,
            "filter_ids": set(app.file_list.filter_tag_ids or ()),
            "filter_match_all": bool(app.file_list.filter_match_all),
            "had_filter": app._tag_filter_base_spec is not None,
        }
        if (state["spec"] or {}).get("kind") == "paths" \
                and not state["had_filter"]:
            state["spec"] = None   # 上一次就是搜索结果，别记它
        app._search_return_state = state
    if app.file_list.filter_tag_ids:
        app.file_list.set_tag_filter(set())
    app._tag_filter_base_spec = None


def _restore_view_after_search(app):
    """清空搜索 → 回到搜索前的视图。返回是否还原成功。"""
    st = app._search_return_state
    app._search_return_state = None
    app._cancel_recursive_scan(invalidate_cache=True)
    if not st:
        return False
    spec = st.get("spec") or {}
    kind = spec.get("kind") or st.get("view_mode")
    try:
        if kind == "cat" and st.get("cat_id") is not None:
            app.show_category(st["cat_id"])
        elif kind == "all":
            app.show_all_files()
        elif kind == "dir" and st.get("dir"):
            app.load_directory(st["dir"])
        elif kind == "paths" and spec:
            app._view_spec = spec
            app._page = 0
            app._load_current_page()
        else:
            return False
    except Exception as exc:
        app.log_problem(f"还原搜索前的视图失败：{exc}", level="warn")
        return False
    # 把搜索前选中的标签筛选放回去（整个视图范围下会自动重算）
    ids = st.get("filter_ids") or set()
    if ids:
        app.file_list.set_tag_filter(ids, st.get("filter_match_all"))
        app._invalidate_tag_scope()
    app.set_status(T("已退出搜索，回到原来的视图"))
    return True


def _on_global_search(app, keyword):
    """在分类或全部文件视图中进行全局搜索"""
    if not keyword:
        # 清空搜索 → 先试着还原搜索前的视图
        if app._restore_view_after_search():
            return
        if app.view_mode == "dir":
            app.file_list.search_external = False
            app.file_list._apply_search_filter()
        elif app.view_mode == "cat" and app.current_cat_id:
            app.show_category(app.current_cat_id)
        elif app.view_mode == "all":
            app.show_all_files()
        return

    if app.view_mode == "dir":
        # 当前文件夹：就是本地按「文件名/标签/路径」开关过滤
        app.file_list.search_external = False
        app.file_list._apply_search_filter()
        return

    # ★ v25：换搜索视图前先把原视图记下来、并清掉遗留的标签筛选
    app._begin_search_view()
    # 查库实现的是"路径含关键字"，本地的「文件名/标签/路径」开关
    # 仍然负责把结果再收窄一点（跟平时在分类里搜索一致）
    app.file_list.search_external = False
    if app.view_mode == "cat" and app.current_cat_id:
        cats = {c["id"]: c for c in app.store.all_categories()}
        cat_name = cats.get(app.current_cat_id, {}).get("name", "")
        paths = app.store.search_files_in_category(app.current_cat_id, keyword)
        # ★ 2026-10-06：标题里带上**找到几个** —— 外面每个正经搜索
        #   都有这个数，用户才知道「该继续打字收窄，还是已经够了」。
        #   原来只有状态栏闪一下（很容易被后面的消息盖掉）。
        app.list_title.config(
            text=f"分类搜索：{keyword}　找到 {len(paths)} 个")
        app._invalidate_tag_scope()
        app._view_spec = {"kind": "paths", "paths": paths}
        app._page = 0
        app._load_current_page()
        app.set_status(f"在分类「{cat_name}」中搜索 \"{keyword}\"：找到 {len(paths)} 个文件")
    elif app.view_mode == "all":
        paths = app.store.search_all_files(keyword)
        app.list_title.config(
            text=f"全部文件搜索：{keyword}　找到 {len(paths)} 个")
        app._invalidate_tag_scope()
        app._view_spec = {"kind": "paths", "paths": paths}
        app._page = 0
        app._load_current_page()
        app.set_status(f"在所有文件中搜索 \"{keyword}\"：找到 {len(paths)} 个文件")
    else:
        # 其他视图（比如搜索结果里再搜）：退回本地过滤
        app.file_list.search_external = False
        app.file_list._apply_search_filter()


def apply_filter(app):
    selected_ids = app.tag_thumb.selected_ids
    if not selected_ids:
        messagebox.showinfo("提示",
                            "请先在右侧标签星图缩略图里单击选择标签（Ctrl 可多选）")
        return
    name_map = {r[0]: r[1] for r in app.store.all_tags()}
    names = [name_map[tid] for tid in selected_ids if tid in name_map]
    if not names:
        return
    paths = app.store.find_files(names, match_all=app.match_all_var.get())
    app.view_mode = "filter"
    app.current_cat_id = None
    app._cancel_recursive_scan(invalidate_cache=True)
    app._search_return_state = None
    app._clear_stats_filter()
    app._reset_category_hidden_tags()
    app.list_title.config(text=T("筛选结果"))
    app.path_var.set("筛选结果")
    app.list_info.config(text=T("筛选：") + " + ".join(names))
    app._invalidate_tag_scope()
    app._view_spec = {"kind": "paths", "paths": paths}
    app._page = 0
    app._load_current_page()
    app.set_status(
        f"筛选：{' + '.join(names)}    →  {app._page_total} 个结果")


def clear_filter(app):
    app.load_directory(app.current_dir)
    app.sidebar.set_selected("all", None)
    app.tag_thumb.selected_ids.clear()
    app.tag_thumb._redraw()
