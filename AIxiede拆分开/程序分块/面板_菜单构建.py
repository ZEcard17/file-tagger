# -*- coding: utf-8 -*-
"""从 AIxiede.py 的 `FileTaggerApp` 里搬出来的「菜单构建」这组方法。

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
_NEED = ['BALL_SHAPES', 'T', 'ball_style_names', 'note_swallowed', 'theme_get']
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


def _menu_file(app, menubar):
    # ★★ 从 `_build_menu` 里抽出来的一节（2026-10-08）——
    #   ★ 原来是个 416 行的巨型方法，按它**自带的分节**抽成小方法；
    #   ★★ 这样「一个菜单 = 一个方法」，看得清、也搬得走。
    #   ★★ `menubar` 是外面建的 → 当参数传进来。
    # ==================================================================
    #  ① 文件 —— 只管"对整个文件夹 / 程序"
    # ==================================================================
    m_file = tk.Menu(menubar, tearoff=0)
    m_file.add_command(label=T("打开文件夹…"), command=app.choose_dir)
    m_file.add_separator()
    m_file.add_command(label=T("新建文件夹"), command=app._do_new_folder)
    m_file.add_command(label=T("重命名…"), command=lambda: app._do_rename())
    m_file.add_command(label=T("删除到回收站"), command=lambda: app._do_delete())
    m_file.add_separator()
    m_file.add_command(label=T("退出"), command=app.on_close)
    menubar.add_cascade(label=T("文件"), menu=m_file)


def _menu_edit(app, menubar):
    # ★★ 从 `_build_menu` 里抽出来的一节（2026-10-08）——
    #   ★ 原来是个 416 行的巨型方法，按它**自带的分节**抽成小方法；
    #   ★★ 这样「一个菜单 = 一个方法」，看得清、也搬得走。
    #   ★★ `menubar` 是外面建的 → 当参数传进来。
    # ==================================================================
    #  ② 编辑 —— 只管"对内容做什么"（★ 新菜单）
    #    从原来的「文件」和「界面」里抽出来的
    # ==================================================================
    m_edit = tk.Menu(menubar, tearoff=0)
    m_edit.add_command(label=T("全选当前列表（Ctrl+A）"),
                       command=lambda: app.file_list.select_all_rows())
    m_edit.add_separator()
    m_edit.add_command(label=T("复制（Ctrl+C）"),
                       command=lambda: app.copy_selected(cut=False))
    m_edit.add_command(label=T("剪切（Ctrl+X）"),
                       command=lambda: app.copy_selected(cut=True))
    m_edit.add_command(label=T("粘贴到当前文件夹（Ctrl+V）"),
                       command=app.paste_into_current)
    m_edit.add_separator()
    m_edit.add_command(label=T("撤销上一步（Ctrl+Z）"),
                       command=app.undo_do)
    menubar.add_cascade(label=T("编辑"), menu=m_edit)


def _menu_tag(app, menubar):
    # ★★ 从 `_build_menu` 里抽出来的一节（2026-10-08）——
    #   ★ 原来是个 416 行的巨型方法，按它**自带的分节**抽成小方法；
    #   ★★ 这样「一个菜单 = 一个方法」，看得清、也搬得走。
    #   ★★ `menubar` 是外面建的 → 当参数传进来。
    # ==================================================================
    #  ③ 标签 —— 只管"对标签做什么"（**这次没动**）
    # ==================================================================
    m_tag = tk.Menu(menubar, tearoff=0)
    m_tag.add_command(label=T("标签星图"),
                      command=lambda: app.open_tag_tree())
    m_tag.add_command(label=T("同步所有文件的标签链"),
                      command=lambda: app.resync_now())
    m_tag.add_separator()
    m_tag.add_command(label=T("重新分配所有标签颜色"),
                      command=app.reassign_colors)
    m_tag.add_separator()
    m_tag.add_command(label=T("🔍 为当前列表打标签"),
                      command=app.scan_current_view_tags)
    m_tag.add_command(label=T("⚙ 自动标签规则…"),
                      command=app.open_auto_rules)
    m_tag.add_command(label=T("🧹 清除标签筛选"),
                      command=app.clear_tag_filter)
    m_tag.add_command(label=T("👁 全部显示被屏蔽的标签"),
                      command=app.clear_hidden_tags)
    menubar.add_cascade(label=T("标签"), menu=m_tag)


def _menu_switch(app, menubar):
    # ★★ 从 `_build_menu` 里抽出来的一节（2026-10-08）——
    #   ★ 原来是个 416 行的巨型方法，按它**自带的分节**抽成小方法；
    #   ★★ 这样「一个菜单 = 一个方法」，看得清、也搬得走。
    #   ★★ `menubar` 是外面建的 → 当参数传进来。
    # ==================================================================
    #  ④ 区域开关 —— 只管"哪块区域显示不显示"
    #    ★ 每项前面自动带状态圆点（● 绿=开 / ● 红=关），见
    #      `_tick_menu_states`（菜单弹出前会刷一次）。
    #    ★ 项名故意**不带**「（显示 / 收起）」那类字 ——
    #      圆点已经说明状态了，字面重复反而更乱。
    # ==================================================================
    m_sw = tk.Menu(menubar, tearoff=0,
                   postcommand=lambda: app._tick_menu_states())
    app._m_switches = m_sw
    app._menu_state_map = []      # [(项序号, 取状态函数, 干净名字)]
    app._menu_state_map2 = []

    def _sw(label, command, getter):
        """加一个"带状态圆点"的开关项，并把它的状态源登记下来。

        ★ 关键：**记的是加进去那一刻的项序号**。
          因为圆点机制会改 label（`标签盒` → `● 标签盒`），
          按 label 找的话刷一次之后就找不到了（踩过）。
        """
        m_sw.add_command(label=label, command=command)
        app._menu_state_map.append(
            (m_sw.index("end"), getter, label))

    _sw(T("左侧分类库"), app.toggle_sidebar,
        lambda: bool(getattr(app, "_sidebar_visible", True)))
    _sw(T("顶部工具栏"), app.toggle_top_bar,
        lambda: bool(getattr(app, "_top_bar_visible", True)))
    _sw(T("标签条"), app.toggle_tagbar,
        lambda: bool(getattr(getattr(app, "file_list", None),
                             "tagbar_visible", False)))
    _sw(T("标签盒"), app.toggle_tagbox,
        lambda: bool(getattr(app, "tagbox_visible", False)))
    m_sw.add_separator()
    _sw(T("鼠标悬停预览"), app.toggle_hover_preview,
        lambda: bool(getattr(getattr(app, "hover", None),
                             "enabled", False)))
    # ★ 2026-10-07：名字从「快速预览（空格键）」改成「快速预览窗」——
    #   用户报「快速预览没有开关的设置，只有开」。
    #   查证：**开关功能本身是好的**（实测 False→开→关→开 都对），
    #   问题在**它看起来不像个开关**：
    #     · 名字带「（空格键）」→ 像"快捷键说明"，不像开关
    #     · 更关键的是：**没选中文件时点它会毫无反应**
    #       （只在状态栏闪一句提示）→ 用户以为"点了没用/只能开"。
    #   所以：① 改名（状态圆点已经能显示开/关）
    #        ② `toggle_quick_preview` 里没选中文件时**弹个明确提示**。
    _sw(T("快速预览窗"), app.toggle_quick_preview,
        lambda: bool((getattr(app, "quick_preview", None) is not None)
                     and app.quick_preview.is_open()))
    m_sw.add_separator()
    # ★ 原来"列表模式 / 瀑布流模式"是两个单选项，用户说「合并成瀑布流模式」
    #   ★★ 状态要从 **file_list** 上读 —— `layout_mode` 是 `FileList` 的属性
    #     （见 FileList.__init__ 的 `app.layout_mode = "list"`），
    #     **FileTaggerApp 上没有这个属性**（踩过：写成 app.layout_mode →
    #      一点菜单就 AttributeError，被 except 吞掉、圆点永远显示"关"）。
    _sw(T("瀑布流模式"), app._toggle_layout_from_menu,
        lambda: (str(getattr(getattr(app, "file_list", None),
                             "layout_mode", "list")) == "grid"))
    menubar.add_cascade(label=T("区域开关"), menu=m_sw)


def _menu_data(app, menubar):
    # ★★ 从 `_build_menu` 里抽出来的一节（2026-10-08）——
    #   ★ 原来是个 416 行的巨型方法，按它**自带的分节**抽成小方法；
    #   ★★ 这样「一个菜单 = 一个方法」，看得清、也搬得走。
    #   ★★ `menubar` 是外面建的 → 当参数传进来。
    # ==================================================================
    #  ⑤ 用户数据 —— 只管"数据进出 / 存在哪"（★ 新菜单，两组）
    #    用户定的：导出导入 + 存储位置
    # ==================================================================
    m_data = tk.Menu(menubar, tearoff=0)

    m_exp = tk.Menu(m_data, tearoff=0)
    m_exp.add_command(label=T("导出标签结构…"),
                      command=app.export_tags_structure)
    m_exp.add_command(label=T("导出文件标签信息…"),
                      command=app.export_file_tags)
    m_exp.add_separator()
    m_exp.add_command(label=T("导入标签结构…"),
                      command=app.import_tags_structure)
    m_exp.add_command(label=T("导入文件标签信息…"),
                      command=app.import_file_tags)
    m_exp.add_separator()
    m_exp.add_command(label=T("打开导出文件夹"), command=app.open_export_dir)
    m_data.add_cascade(label=T("导出 / 导入"), menu=m_exp)

    m_loc = tk.Menu(m_data, tearoff=0)
    m_loc.add_command(label=T("设置数据存储位置…"), command=app.change_data_dir)
    m_loc.add_command(label=T("迁移设置文件到数据目录…"),
                      command=app.migrate_settings_now)
    m_loc.add_command(label=T("显示当前数据位置"), command=app.show_data_dir)
    m_data.add_cascade(label=T("存储位置"), menu=m_loc)
    menubar.add_cascade(label=T("用户数据"), menu=m_data)


def _menu_settings(app, menubar):
    # ★★ 从 `_build_menu` 里抽出来的一节（2026-10-08）——
    #   ★ 原来是个 416 行的巨型方法，按它**自带的分节**抽成小方法；
    #   ★★ 这样「一个菜单 = 一个方法」，看得清、也搬得走。
    #   ★★ `menubar` 是外面建的 → 当参数传进来。
    # ==================================================================
    #  ⑥ 设置 —— 只管"改程序怎么用"（★ 新菜单）
    #    用户原话：「快捷键设置感觉需要单独做一项，因为这些基本上都是设置」
    # ==================================================================
    m_set = tk.Menu(menubar, tearoff=0,
                    postcommand=lambda: app._tick_menu_states())
    app._m_settings = m_set
    m_set.add_command(label=T("⌨ 快捷键管理…"),
                      command=app.open_shortcut_dialog)
    m_set.add_separator()
    # ★ 皮肤
    app.theme_var = tk.StringVar(value=str(theme_get("name") or "light"))
    # ★★★ 2026-10-08：**菜单每次打开时重建**（用户要"配合插件入口"）★★★
    #   ★ 为什么不用"建菜单时列一遍"：
    #     插件是**建完菜单之后**才加载的（见 `__init__`）——
    #     建菜单时问"有哪些皮肤"，插件的皮肤**还没注册**，列不出来。
    #     实测就是这样：插件注册的配色**进了 `_THEMES`，但菜单里看不到**。
    #   ★ 修法：给菜单挂一个 `postcommand`（**每次点开都跑**）——
    #     每开一次就**重新问一遍"现在有哪些皮肤"**。
    #     ★ 这样插件的皮肤、以后运行时装的新皮肤，**自动就出现了**，
    #       不需要"重开程序"、也不需要改这段代码。
    #     ★ 代价：每次开菜单多跑十来行（可以忽略）。
    m_theme = tk.Menu(m_set, tearoff=0,
                      postcommand=lambda: app._fill_theme_menu(m_theme))
    # ★ 存个引用 —— 插件加载完之后要**重刷它一次**（见 `_attach_plugin_menus`）
    app._theme_menu = m_theme
    try:
        app._fill_theme_menu(m_theme)
    except Exception:
        pass
    m_set.add_cascade(label=T("🎨 皮肤（白天 / 夜间 / 自定义）"), menu=m_theme)
    m_set.add_command(label=T("🌓 快速切换白天 / 夜间"),
                      command=app.toggle_theme)
    m_set.add_command(label=T("🖥 调整界面缩放…"),
                      command=app.change_ui_scale)
    # ★★★ 2026-10-08：**悬浮球 + 菜单栏**（用户要"菜单栏改成悬浮球"）★★★
    #   ★ 为什么这两个入口必须在这儿：
    #     ① **悬浮球**：用户在球上右键"关掉这个球"之后，
    #        总得有个地方能**叫回来**（不然只能改设置文件了）
    #     ② **菜单栏**：它默认是藏起来的（那条白条修不了，只能藏），
    #        所以得有个**明确的地方**能显示/藏它 ——
    #        除了 `Alt` 快捷键，这里也给一个（鼠标党不用记快捷键）
    m_set.add_separator()

    return m_set


def _menu_lang_bg_cache(app, menubar, m_set):
    # ★★ 从 `_build_menu` 里抽出来的一节（2026-10-08）——
    #   ★ 原来是个 416 行的巨型方法，按它**自带的分节**抽成小方法；
    #   ★★ 这样「一个菜单 = 一个方法」，看得清、也搬得走。
    #   ★★ `menubar` 是外面建的 → 当参数传进来。
    # ==================================================================
    #  ★★★ 2026-10-08 **🌐 语言**（用户要的"联合国官方语言"起步）★★★
    #  ------------------------------------------------------------------
    #  ★★ 为什么做成"子菜单 + 每次打开时重建"（见 `_fill_lang_menu`）：
    #     · 语言列表是**扫描 `语言/` 目录**得到的 ——
    #       用户**丢一个新 json 进去就多一种语言**（不用改代码）
    #     · ★ 所以菜单要**每次打开重扫**，不然新加的语言看不到
    #       （这跟"皮肤菜单"是同一个坑，见错题本 #130）
    #
    #  ★★ 关于"选了之后要不要重启"（用户定：重启生效）：
    #     · Tk 的界面文字**不像颜色那样能热刷** ——
    #       颜色可以"扫一遍所有控件重设"，文字得**重设每一条**
    #     · 热切换要"销毁整个界面再重建"，**复杂且风险高**
    #     → 所以：**存设置 + 提示重启 + 给个"现在就重启"的按钮**
    #       （★ 用户不用自己去关开，算"半自动"）
    m_lang = tk.Menu(m_set, tearoff=0,
                     postcommand=lambda: app._fill_lang_menu(m_lang))
    app._lang_menu = m_lang
    try:
        app._fill_lang_menu(m_lang)
    except Exception:
        pass
    m_set.add_cascade(label=T("🌐 语言 / Language"), menu=m_lang)
    m_set.add_separator()
    # ★★★ 2026-10-08：**背景图**（用户要"搞个图片当背景"）★★★
    #   ★ 单独一个子菜单，因为"调透不透"这种事**要能反复试** ——
    #     做成滑杆/几档，用户挑到满意为止（跟"选一次就完"不一样）。
    m_bg = tk.Menu(m_set, tearoff=0)
    m_bg.add_command(label=T("🖼 选一张图当背景…"),
                     command=app.choose_background_image)
    m_bg.add_separator()
    # ★ "透不透"给几档（不用滑杆是因为菜单里滑杆不好用）
    for _lbl, _v in ((T("面板：完全不透（看不太出背景图）"), 0),
                     (T("面板：轻微透（背景若隐若现）"), 30),
                     (T("面板：中等透（推荐）"), 55),
                     (T("面板：很透（背景很清楚，字稍糊）"), 80)):
        m_bg.add_command(
            label=_lbl, command=lambda v=_v: app.set_bg_alpha(v))
    m_bg.add_separator()
    for _lbl, _v in ((T("模糊：不模糊（图很清楚）"), 0),
                     (T("模糊：轻微"), 4),
                     (T("模糊：像毛玻璃（推荐）"), 14),
                     (T("模糊：很糊（当纯色底用）"), 30)):
        m_bg.add_command(
            label=_lbl, command=lambda v=_v: app.set_bg_blur(v))
    m_bg.add_separator()
    for _lbl, _v in ((T("摆放：铺满（推荐）"), "cover"),
                     (T("摆放：完整显示（留边）"), "contain"),
                     (T("摆放：平铺"), "tile"),
                     (T("摆放：居中"), "center")):
        m_bg.add_command(
            label=_lbl, command=lambda v=_v: app.set_bg_mode(v))
    m_bg.add_separator()
    m_bg.add_command(label=T("✖ 去掉背景图"), command=app.clear_background)
    m_set.add_cascade(label=T("🖼 背景图（图片 / 毛玻璃）"), menu=m_bg)
    m_set.add_separator()
    m_set.add_command(label=T("⚪ 悬浮球（显示 / 收走）"),
                      command=app.toggle_floating_ball)
    # ★★★ 2026-10-08：**球的皮肤**（用户要求：跟主界面皮肤分开）★★★
    #   ★ 为什么"设置"里也要有一个入口：
    #     球可能被用户收走了（或者建不起来）——
    #     那时**总得有个地方能设球的样子**。
    #   ★★ 但这个入口**只管球**，跟上面那个「🎨 皮肤」**不是一回事**
    #     （用户特意强调"你可别搞混了啊"）。
    m_bskin = tk.Menu(m_set, tearoff=0)
    for _bk, _bl in ball_style_names():
        m_bskin.add_command(
            label="⚪ " + T(_bl),
            command=lambda k=_bk: app._set_ball_style_from_menu(k))
    m_bskin.add_separator()
    m_bshape = tk.Menu(m_bskin, tearoff=0)
    for _sk, _sl, _sd in BALL_SHAPES:
        m_bshape.add_command(
            label=T(_sl),
            command=lambda s=_sk: app._set_ball_shape_from_menu(s))
    m_bskin.add_cascade(label=T("形状 / 样式"), menu=m_bshape)
    m_set.add_cascade(label=T("⚪ 球的皮肤（只管悬浮球）"), menu=m_bskin)
    m_set.add_command(label=T("📋 菜单栏（显示 / 藏起　快捷键 Alt）"),
                      command=app._toggle_menubar)
    m_set.add_separator()
    # ★ 拉框方式（用户定：放设置）
    m_set.add_command(label=T("🖱 拉框方式：空白处优先 / 随处可拉（切换）"),
                      command=app.toggle_marquee_anywhere)
    # ★ 目录缓存
    m_cache = tk.Menu(m_set, tearoff=0,
                      postcommand=lambda: app._tick_menu_states())
    m_cache.add_command(label=T("目录缓存"), command=app.toggle_dir_cache)
    # ★ 记下**它真实的菜单对象**（在子菜单里，不是 _m_settings）——
    #   否则刷新时会在错的菜单上找序号，圆点刷不上去
    # ★★ 2026-10-08：**这里要 `T(...)`** ——
    #   `_refresh_menu_states()` 每次弹菜单都会拿这个 `name`
    #   **重设一遍 label**。存裸中文的话，
    #   切英文后菜单一弹就被**改回中文**（实测踩到，见错题本）。
    #   ★ 判据：**"会被回写的文字"必须存"已经翻好的"** ——
    #     不能存原文（否则等于每次都在"撤销翻译"）。
    app._menu_state_map2.append(
        (m_cache.index("end"), lambda: bool(
            getattr(app, "dir_cache_enabled", False)),
         T("目录缓存"),
         m_cache))
    m_cache.add_separator()
    m_cache.add_command(label=T("重扫当前目录（清缓存）"),
                        command=app.refresh_current_dir)
    m_cache.add_command(label=T("清除全部目录缓存"),
                        command=app.clear_all_dir_cache)
    m_cache.add_separator()
    m_cache.add_command(label=T("📚 索引管理…"),
                        command=app.open_index_manager)
    m_set.add_cascade(label=T("📁 缓存与索引"), menu=m_cache)
    m_set.add_command(label=T("📥 网盘预览缓存设置…"),
                      command=app._open_cache_settings)
    menubar.add_cascade(label=T("设置"), menu=m_set)


def _menu_refresh(app, menubar):
    # ★★ 从 `_build_menu` 里抽出来的一节（2026-10-08）——
    #   ★ 原来是个 416 行的巨型方法，按它**自带的分节**抽成小方法；
    #   ★★ 这样「一个菜单 = 一个方法」，看得清、也搬得走。
    #   ★★ `menubar` 是外面建的 → 当参数传进来。
    # ==================================================================
    m_ref = tk.Menu(menubar, tearoff=0)
    m_ref.add_command(label=T("刷新"), command=app.refresh_all)
    m_ref.add_command(label=T("🏷 重读标签（按自动规则更新当前视图）"),
                      command=app._refresh_current_dir_tags)
    menubar.add_cascade(label=T("刷新"), menu=m_ref)


def _menu_diag(app, menubar):
    # ★★ 从 `_build_menu` 里抽出来的一节（2026-10-08）——
    #   ★ 原来是个 416 行的巨型方法，按它**自带的分节**抽成小方法；
    #   ★★ 这样「一个菜单 = 一个方法」，看得清、也搬得走。
    #   ★★ `menubar` 是外面建的 → 当参数传进来。
    # ==================================================================
    m_diag = tk.Menu(menubar, tearoff=0)
    m_diag.add_command(
        label=T("📓 用法记录（哪儿出过问题 · 本次 / 历史）"),
        command=app.show_usage_log)
    m_diag.add_separator()
    m_diag.add_command(
        label=T("🩺 自检（孤立标签 / 重复路径 / 网盘与索引盘）…"),
        command=lambda: app._run_selfcheck(manual=True))
    m_diag.add_separator()
    m_diag.add_command(
        label=T("🧹 修复重复文件记录 / 规范路径（标签显示不全时用）…"),
        command=app._do_merge_duplicate_paths)
    m_diag.add_command(
        label=T("☁ 修复网盘路径（网盘改名后双击打不开时用）…"),
        command=app._do_heal_net_paths)
    m_diag.add_command(
        label=T("🧹 清理索引里的幽灵目录（网盘里已删除的）…"),
        command=app._do_prune_orphan_dirs)
    m_diag.add_command(
        label=T("☁ 让网盘目录缓存过期（下次读最新的）…"),
        command=app._do_expire_net_dir_cache)
    menubar.add_cascade(label=T("诊断"), menu=m_diag)

    # ==================================================================
    #  ⑨ 帮助

    # ==================================================================
    m_help = tk.Menu(menubar, tearoff=0)
    m_help.add_command(label=T("关于"), command=app.show_about)
    menubar.add_cascade(label=T("帮助"), menu=m_help)

    # ★★★ 2026-10-08 **插件菜单**（用户要"配合插件入口"）★★★
    #   ★ 这里只挂"**在 `_build_menu` 之前就已经注册好**"的插件 ——
    #     而实际上插件是在 `_build_ui()` 之后才加载的（见 `__init__`），
    #     所以**真正挂的地方是 `_attach_plugin_menus()`**。
    #   ★ 为什么两处都写：
    #     万一以后有人把插件加载**提前**（比如为了"插件能改菜单项文字"），
    #     这里也能接住 —— **冗余，防的是"以后改动"**（用户要的"留接口"）。
    try:
        app._attach_plugin_menus()
    except Exception:
        pass

    app.root.config(menu=menubar)
    # ★★★ 2026-10-08：**菜单栏默认藏起来**（用户要"菜单栏改成悬浮球"）★★★
    #   ★ 为什么要藏：用户实测反馈「都夜间模式了，菜单栏还白白的」——
    #     而**实测证明 Windows 的菜单栏 Tk 根本改不了颜色**
    #     （截图取像素：设了深色，菜单栏照样 (255,255,255)）。
    #     → 「改成悬浮球」不是"更好看"，而是**唯一的修法** ——
    #       藏起来，那条白条**从根上消失**。
    #   ★ 藏起来之后怎么找功能：
    #     ① **悬浮球左键**（主入口，复用这个同一个菜单）
    #     ② **按 `Alt`**（安全网 —— 万一悬浮球出问题，还能唤出来）
    #   ★ 为什么不真删掉这段代码：悬浮球的菜单**就是它** ——
    #     删了就得重写一遍，而且以后加功能要改两处（迟早漏）。
    #   ★ 万一悬浮球建不起来（任何原因），下面会**自动把菜单栏装回去**，
    #     保证"永远有一个能用的入口"（见 `_setup_floating_ball`）。
    try:
        app.root.config(menu="")
        app._menu_hidden = True
    except Exception:
        app._menu_hidden = False
    # ★ Alt 单击 → 临时唤出菜单栏（安全网）
    try:
        app.root.bind("<Alt-KeyPress>", app._on_alt_toggle_menu, add="+")
        app.root.bind("<KeyRelease-Alt_L>", app._on_alt_release, add="+")
        app.root.bind("<KeyRelease-Alt_R>", app._on_alt_release, add="+")
    except Exception as _e:
        note_swallowed(T("装 Alt 唤出菜单失败"), _e)
    # ★ 建完先刷一次状态圆点，免得第一次打开菜单时看不到圆点
    try:
        app.root.after(300, app._refresh_menu_states)
    except Exception:
        pass
