# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「网盘维护」这组方法。

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
_NEED = ['T', '_cd_pb', '_ensure_net_aliases_loaded', '_面板扫描索引', 'cd_api_client_from_settings', 'is_remote_path', 'note_swallowed', 'prune_orphan_dir_cache']
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
            # ★★★ 无条件装代理（错题本 #168 v3）
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


def _update_net_btn(app):
    try:
        idx = (getattr(app, "net_browse_mode", "index") == "index")
        # ★★ v26：**width 别按「字符数」硬算 —— 中文字/emoji 会不够宽。**
        #   用户反馈：「右下角『网盘:索引』显示不全，『引』字有部分被隐藏」。
        #   实测：tk scaling=2.0 下这个按钮的 `width=9` 是按
        #   **9 个西文字符**量出来的，而 `🧭 网盘:索引` 里
        #   emoji 和汉字都比西文字符宽 —— 结果**文字右边被切掉**。
        #   现在改成 **width=0（表示由内容自己决定）**，
        #   让 ttk 按真实文字宽度算，绝对不会切。
        if getattr(app, "_status_icons_mode", False):
            txt = "🧭索" if idx else "🧭真"
            app._net_btn.config(text=txt, width=4)
        else:
            app._net_btn.config(
                text=T("🧭 网盘:索引") if idx else T("🧭 网盘:真实"), width=0)
    except Exception:
        pass


def _apply_net_root_fixes(app, *a, **k):
    # ★★ 转发到 `AIxiede拆分开/程序分块/面板_扫描索引.py`
    #   ★ 保留同名方法 = **所有调用方不用改**（稳定接口）
    return _面板扫描索引._apply_net_root_fixes(app, *a, **k)


def _do_heal_net_paths(app):
    """☁ 把库里指向「失效的旧网盘挂载名」的记录改成当前挂载名。

    症状：网盘（CloudDrive 这类）改名 / 重装系统后重新挂载，
    双击网盘文件没反应或报错，只有本地文件能打开；
    重建索引也不管用（索引只补目录缓存，改不了文件表里的路径）。

    ★ 2026-10-03 重写：**先把「打算怎么改」摆给你看，你确认了再动**。
      现挂载名不再是死写在代码里的，而是程序自己
      「拿库里几个真实文件去几个候选挂载上试探」认出来的。
    """
    _ensure_net_aliases_loaded()
    app.begin_activity("正在检查网盘挂载名…（会去网盘点几个文件看看，稍等）")
    try:
        plan = app.store.plan_net_heal()
    except Exception as exc:
        app.end_activity()
        messagebox.showerror("检查失败", str(exc), parent=app.root)
        return
    app.end_activity()
    roots = list(getattr(app.store, "last_net_roots", []) or [])

    if not plan:
        messagebox.showinfo(
            "修复网盘路径",
            "库里存的文件路径，用的挂载名现在**都还连得上** —— "
            "没有需要修的东西。\n\n"
            "如果你现在双击网盘文件确实打不开，请先确认：\n"
            "  · 网盘客户端（CloudDrive2）在运行、已经登录；\n"
            "  · 这个网盘在 CloudDrive2 里处于「已挂载」状态。",
            parent=app.root)
        return

    lines = []
    todo_n = 0
    for item in plan:
        lines.append("  · 旧挂载名（现在连不上）：%s" % item["old"])
        lines.append("      库里有多少条：%d 条" % item["count"])
        if item["new"]:
            lines.append("      程序认出的现挂载名：%s" % item["new"])
            lines.append("      怎么认出来的：%s" % item["how"])
            todo_n += item["count"]
        else:
            lines.append("      程序**没认出来** → 这次不动它（宁可不动，也不能改错）")
        lines.append("")
    if roots:
        lines.append("另外，索引里还挂着一个连不上的旧目录：")
        for r in roots:
            if r["action"] == "delete":
                lines.append("  · %s（新的已经在索引里了 → 建议删掉这一条）"
                             % r["path"])
            else:
                lines.append("  · %s → 改成 %s" % (r["path"], r["new"]))
        lines.append("")

    if todo_n <= 0:
        messagebox.showinfo(
            "修复网盘路径",
            "找到连不上的旧挂载名，但**没能认出现在换成哪个挂载名了**，"
            "所以这次一条都没改（改错路径会把标签弄丢，宁可不改）。\n\n"
            + "\n".join(lines) +
            "\n请先确认网盘客户端在运行、网盘已挂载，然后再点一次这个菜单。",
            parent=app.root)
        return

    if not messagebox.askyesno(
            "修复网盘路径（先看清单）",
            "打算这样改：\n\n" + "\n".join(lines) +
            "\n一共要改 %d 条文件路径。\n\n"
            "改完之后这些文件的标签就恢复正常了，也能双击打开\n"
            "（标签本身不会丢，只是路径换了写法）。\n\n"
            "现在就改吗？" % todo_n,
            parent=app.root):
        return

    app.begin_activity("正在修复网盘路径…")
    try:
        n = app.store.heal_net_paths(plan=plan)
    except Exception as exc:
        app.end_activity()
        messagebox.showerror("修复失败", str(exc), parent=app.root)
        return
    root_done = []
    if roots:
        try:
            root_done = app._apply_net_root_fixes(roots)
        except Exception as _e:
            note_swallowed(T("修复网盘路径：处理索引根目录失败"), _e)
    app.end_activity()

    rep = getattr(app.store, "last_net_report", {}) or {}
    learned = [d for d in rep.get("done", []) if d.get("how") == "自动认出"]
    app.log_output("网盘路径修复：改了 %d 条%s" %
                    (n, ("，跳过多余 %d 条" % rep.get("skipped"))
                     if rep.get("skipped") else ""))
    app._last_cat_refresh_ts = 0.0
    try:
        app.refresh_categories()
        app.refresh_tags()
    except Exception:
        pass
    try:
        if app.view_mode == "cat" and app.current_cat_id:
            app.show_category(app.current_cat_id)
        elif app.view_mode == "all":
            app.show_all_files()
        elif app.view_mode == "filter":
            app._load_current_page()
        else:
            app.load_directory(app.current_dir)
    except Exception:
        pass

    if n:
        extra = ""
        if learned:
            extra += "\n\n★ 程序顺便记下了新的挂载名对照关系：\n" + "\n".join(
                "   %s  →  %s" % (d["old"], d["new"]) for d in learned) + \
                "\n（以后网盘再改名，程序会自己认、不用再点这个菜单）"
        if root_done:
            extra += "\n\n索引根目录也顺手处理了：\n" + "\n".join(
                "   " + x for x in root_done)
        if rep.get("skipped"):
            extra += ("\n\n有 %d 条没改：新路径上已经有记录了（撞车），"
                      "硬改会把标签弄丢，所以跳过了。" % rep["skipped"])
        app.set_status(f"修复网盘路径：改了 {n} 条")
        messagebox.showinfo(
            "修复完成",
            "已把 %d 条文件路径换成现在的网盘挂载名。\n\n"
            "现在双击这些网盘文件应该能正常打开了。%s" % (n, extra),
            parent=app.root)
    else:
        app.set_status(T("修复网盘路径：没有需要修的"))
        messagebox.showinfo(
            "修复网盘路径",
            "没有需要修复的记录（可能刚才那次已经改过了）。",
            parent=app.root)


def _do_prune_orphan_dirs(app):
    """🧹 清理索引里的「幽灵目录」（网盘里已经删掉的目录留下的空壳）。

    ★ 只删目录缓存（列表用的那份），**不动 files 表、绝不动标签**。
    """
    roots = []
    try:
        for r in app.store.all_index_roots():
            p = str(r["path"])
            try:
                if is_remote_path(p):
                    roots.append(p)
            except Exception:
                pass
    except Exception as exc:
        messagebox.showerror("清理幽灵目录", "读索引根失败：%s" % exc,
                             parent=app.root)
        return
    if not roots:
        messagebox.showinfo(
            "清理幽灵目录",
            "没有网盘索引根，没什么可清的。\n\n"
            "（这个功能是给「网盘里删掉的目录还留在索引里」用的）",
            parent=app.root)
        return
    if not messagebox.askyesno(
            "清理幽灵目录",
            "要清理这些索引根里的「幽灵目录」吗？\n\n"
            + "\n".join("  · " + p for p in roots)
            + "\n\n说明：幽灵目录 = 网盘里已经删掉、但索引里还留着空壳的目录"
              "（点开就报「目录读不到」的那种）。\n"
              "**只清目录缓存，你的标签一个字都不会动。**",
            parent=app.root):
        return
    app.begin_activity("清理幽灵目录…")
    total_dirs = 0
    total_rows = 0
    for p in roots:
        n_dirs, n_rows = prune_orphan_dir_cache(app.store, p)
        total_dirs += n_dirs
        total_rows += n_rows
        app.log_output(f"清理幽灵目录：{p} → 清掉 {n_dirs} 个目录（{n_rows} 行）")
    app.end_activity()
    app.set_status(f"清理幽灵目录：共清掉 {total_dirs} 个目录（{total_rows} 行）")
    messagebox.showinfo(
        "清理幽灵目录",
        f"清理完成 ✓\n\n清掉 {total_dirs} 个幽灵目录，共 {total_rows} 行目录缓存。\n"
        + ("（没有发现幽灵目录，索引是干净的）\n" if total_dirs == 0 else "")
        + "\n标签、分类、文件记录都没动。",
        parent=app.root)


def _do_expire_net_dir_cache(app):
    """☁ 让 CloudDrive2 忘掉网盘的目录缓存（下次读的就是最新的）。

    为什么需要：为了让「反复扫索引」变快，CloudDrive2 自己的目录缓存
    有效期被设成了 10 分钟（原来是 40 秒）。这期间它给你的目录列表是
    缓存里的 —— 你在网盘里刚加/删的东西可能要等一会儿才出现。
    点这个菜单就立刻把缓存清掉，下次扫描 / 浏览读的就是最新的。
    """
    client, why = cd_api_client_from_settings()
    if client is None:
        messagebox.showwarning(
            "让网盘缓存过期",
            "没连上 CloudDrive2，所以清不了。\n\n" + why
            + "\n\n（在「界面 → 📚 索引管理…」窗口里可以填令牌）",
            parent=app.root)
        return
    try:
        roots = []
        try:
            for r in app.store.all_index_roots():
                p = str(r["path"])
                try:
                    if is_remote_path(p):
                        roots.append(p)
                except Exception:
                    pass
        except Exception:
            pass
        if not roots:
            messagebox.showinfo("让网盘缓存过期", T("没有网盘索引根。"),
                                parent=app.root)
            return
        if not messagebox.askyesno(
                "让网盘缓存过期",
                "让 CloudDrive2 忘掉这些网盘目录的缓存吗？\n\n"
                + "\n".join("  · " + p for p in roots)
                + "\n\n（清掉之后，下次扫描 / 浏览读的就是网盘上最新的内容，"
                  "第一遍会慢一点，属正常）",
                parent=app.root):
            return
        app.begin_activity("正在让网盘目录缓存过期…")
        ok = 0
        for p in roots:
            cd = None
            try:
                cd = client.cd_path_of(p)
            except Exception:
                cd = None
            if not cd:
                continue
            try:
                client.stub.ForceExpireDirCache(
                    _cd_pb.FileRequest(path=cd), timeout=60,
                    metadata=client._md())
                ok += 1
                app.log_output(f"已让目录缓存过期：{cd}")
            except Exception as exc:
                app.log_problem(f"让 {cd} 缓存过期失败：{str(exc)[:120]}",
                                 level="warn")
        app.end_activity()
        app.set_status(f"网盘目录缓存已过期（{ok}/{len(roots)}）")
        messagebox.showinfo(
            "让网盘缓存过期",
            f"处理完成：{ok} / {len(roots)} 个网盘根已让缓存过期。\n\n"
            "现在去扫索引或浏览网盘，读到的就是最新的了。",
            parent=app.root)
    finally:
        try:
            client.close()
        except Exception:
            pass


# ---------- ★ 修复重复文件记录（老版本 UNC 路径大小写遗留问题）----------
def _do_merge_duplicate_paths(app):
    """🧹 合并「同一个文件存了两条记录」的历史遗留问题。

    症状：自动规则/手工明明打了标签，中间列表的标签列却不显示；
    标签库里双击跳转，跳出来的文件也不显示标签。
    原因：老版本对网盘 UNC 路径没做小写归一，同一个文件存了两条
    记录（原始大小写 / 全小写），标签只挂在其中一条上，
    而界面查标签统一用 norm()（小写），所以只看到没标签的那条。
    """
    try:
        stat = app.store.merge_duplicate_paths(apply=False)
    except Exception as exc:
        messagebox.showerror("检查失败", str(exc), parent=app.root)
        return
    if not (stat.get("groups") or stat.get("renamed")):
        messagebox.showinfo(
            "修复重复文件记录",
            "没有发现重复的文件记录，也没有写法不规范（大小写不一致）\n"
            "的路径，不需要修复。",
            parent=app.root)
        return
    if not messagebox.askyesno(
            "修复重复文件记录",
            f"发现 {stat['groups']} 组「同一个文件存了两条记录」：\n\n"
            f"  · 要合并掉的重复记录：{stat['removed']} 条\n"
            f"  · 要并过去的标签关联：{stat['moved_tags']} 条\n"
            f"  · 要并过去的分类归属：{stat['moved_cats']} 条\n"
            f"  · 要改写成规范路径（大小写归一）：{stat['renamed']} 条\n\n"
            f"合并后，这些文件上的标签就能正常显示了。\n"
            f"建议先关掉其它正在写库的窗口，然后再点「是」。",
            parent=app.root):
        return
    app.begin_activity("正在合并重复的文件记录…")
    app.log_output(
        f"修复重复文件记录：{stat['groups']} 组 / {stat['removed']} 条")

    def worker():
        st = None
        try:
            st = app.store.merge_duplicate_paths(apply=True)
            app.log_output(
                f"合并完成：删除重复记录 {st['removed']} 条，"
                f"搬迁标签 {st['moved_tags']} 条，"
                f"改写规范路径 {st['renamed']} 条")
        except Exception as exc:
            app.log_problem(f"合并重复记录失败：{exc}", level="error")
        try:
            app._ui_threadsafe(app._on_merge_duplicates_done, st)
        except Exception as exc:
            note_swallowed(T("worker(_on_merge_duplicates_done)：回主线程通知失败"),
                           exc, level="warn")

    threading.Thread(target=worker, daemon=True).start()


def _on_merge_duplicates_done(app, stat):
    """修复重复记录跑完后的界面刷新。"""
    app.end_activity()
    if stat is None:
        messagebox.showerror("修复失败",
                             "合并重复记录时出错，详见下方日志。",
                             parent=app.root)
        return
    app._last_cat_refresh_ts = 0.0
    try:
        app.refresh_categories()
        app.refresh_tags()
    except Exception:
        pass
    # 当前视图重新载入一次（标签列马上变正常）
    try:
        if app.view_mode == "cat" and app.current_cat_id:
            app.show_category(app.current_cat_id)
        elif app.view_mode == "all":
            app.show_all_files()
        elif app.view_mode == "filter":
            app._load_current_page()
        else:
            app.load_directory(app.current_dir)
    except Exception:
        pass
    app.set_status(
        f"修复重复文件记录：删除 {stat['removed']} 条重复记录")
    messagebox.showinfo(
        "修复完成",
        f"已合并 {stat['groups']} 组重复的文件记录：\n\n"
        f"  · 删除重复记录：{stat['removed']} 条\n"
        f"  · 搬迁标签关联：{stat['moved_tags']} 条\n"
        f"  · 搬迁分类归属：{stat['moved_cats']} 条\n"
        f"  · 改写规范路径：{stat['renamed']} 条\n\n"
        f"同一个文件现在只剩一条记录了，标签应该都能正常显示。",
        parent=app.root)
