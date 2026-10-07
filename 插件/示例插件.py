# -*- coding: utf-8 -*-
"""★★ 一个**示例插件** —— 同时也当"插件怎么写"的说明书。

★ 你以后想写插件，照这个抄就行：
  ① 一个 `.py` 文件，放进 `<程序目录>/插件/` 里
  ② 里面必须有一个 `register(api)` 函数
  ③ 通过 `api.add_menu(...)` / `api.add_settings_item(...)` 加东西

★ 文件名**不要以 `_` 开头** —— 那是"不想被加载"的约定
  （写了一半的插件可以改成 `_我的插件.py` 先放着）。

★★★ 2026-10-08 **插件也要支持多语言**（用户说"要做就做全套"）：
   ★ 主程序把 `T()` 交给了插件（`api.T`）——
     **插件里的界面文字也走它**，这样切英文时插件文字也是英文。
   ★★ 为什么让插件用**主程序的** T（而不是自己 import i18n）：
      · 插件的翻译**应该跟主程序同一套语言文件** ——
        用户切语言时**一次生效**，不用每个插件各切一次。
      · 而且插件**不需要知道**语言文件在哪（那是主程序的事）。
   ★★★ 判据：**"给插件的是能力，不是实现"** ——
      插件只管"我要显示这句话"，**怎么翻、翻成什么，主程序管**。
"""


def register(api):
    """★ 插件入口 —— 程序启动时会自动调这个函数。"""

    # ★★ **先把它存起来**（关键！）
    #    菜单回调是"以后"才被点的，那时 `api` 这个参数早没了 ——
    #    所以必须存到模块级变量里。
    global _API
    _API = api

    # ★ 取主程序的翻译函数（取不到就退回"原样返回"——
    #   ★ 这样**老版本主程序**也能跑这个插件，不会因为少个函数就崩）
    global _T
    try:
        _T = api.T
    except Exception:
        _T = lambda s, **kw: s          # noqa: E731

    # ---- ① 加一个自己的顶层菜单 ----
    api.add_menu(_T("示例插件"), [
        (_T("打个招呼"), _hello),
        None,                                    # ★ None = 一条分隔线
        (_T("看看现在在哪个文件夹"), _where),
        (_T("看选中了什么"), _selected),
        (_T("往输出面板写一行"), _log_something),
    ])

    # ---- ② 往「设置」里插一项（省得自己建顶层菜单）----
    api.add_settings_item(_T("🧩 示例插件：关于"), _about)

    # ---- ③ 插件可以有自己的配色（复用主程序那套皮肤机制）----
    #    ★ 只要名字不跟已有皮肤撞，就会出现在「设置 → 皮肤」里
    api.register_theme("example_skin", {
        "name": "example_skin",
        "label": _T("示例插件的配色"),
        # ★ 只给几个关键色就行 —— 缺的**自动从默认皮肤继承**
        "win_bg": "#0d1b2a",
        "card_bg": "#152a3d",
        "panel_bg": "#122436",
        "fg": "#dce8f5",
        "accent": "#3a86c8",
    })

    api.log(_T("示例插件已加载（菜单里能看到「示例插件」）"))


# --------------------------------------------------------------------------
#  ★ 下面是插件自己干的事 —— 随便写，只要不崩就行
# --------------------------------------------------------------------------
def _hello():
    from tkinter import messagebox
    messagebox.showinfo(_T("示例插件"), _T("你好！我是从「插件」目录加载进来的。"))


def _where():
    """★ 显示当前文件夹。"""
    from tkinter import messagebox
    messagebox.showinfo(_T("示例插件"),
                        _T("当前文件夹：{p}",
                           p=(_API.current_dir() or _T("（没打开）"))))


def _selected():
    from tkinter import messagebox
    paths = _API.selected_paths()
    if not paths:
        messagebox.showinfo(_T("示例插件"), _T("现在没选中任何文件。"))
        return
    messagebox.showinfo(_T("示例插件"),
                        _T("选中了 {n} 个：\n\n{x}",
                           n=len(paths), x="\n".join(paths[:10])))


def _log_something():
    _API.log(_T("这是示例插件写的一行日志（你应该能在「输出」面板看到）"))


def _about():
    from tkinter import messagebox
    messagebox.showinfo(
        _T("示例插件"),
        _T("这是一个**演示插件怎么写**的例子。\n\n"
           "你可以：\n"
           "· 把它删掉（程序照常跑）\n"
           "· 照着它改一个自己的\n"
           "· 改坏了也没事（程序会记一笔，但不会打不开）\n\n"
           "★ 文件位置：程序目录 / 插件 / 示例插件.py"))


# ★★ 把 api 存起来 —— **插件里必用的小技巧**：
#    `register(api)` 只在启动时调一次，之后菜单回调里想用它，
#    就得自己存一份（模块级变量）。
#    ★ 忘了存的话，回调里 `_API` 是 `None` → 会报错
#      （不过别怕：程序会把错误记到账本里，而且**不会崩**）。
_API = None

# ★ 翻译函数（同上：也要存一份）
#   ★ 默认值是"原样返回" —— 这样**万一 register 没被调用**，
#     直接调用里面的函数也不会 `NameError`。
_T = lambda s, **kw: s                  # noqa: E731
