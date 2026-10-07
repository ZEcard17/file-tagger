# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：**多语言（i18n）框架**。

★★★ 这是"多语言"的**地基** —— 界面上的字都走这里，就能换语言。

★★ 用户的想法（很实际）：
  「如果可以的话我很想联合国官方语言都做出来弄上去，但是我很穷，所以暂时 A」
  → 先做**框架 + 英文**；以后加俄语/法语/西班牙语/阿拉伯语 = **加一个 JSON 文件**。

★★★ 设计要点（每一条都是"为了以后能加语言"）：

  ① **翻译写在 JSON 文件里**（`语言/zh_CN.json` / `语言/en_US.json`）
     ★ 不写在代码里 —— 这样**加语言不用碰代码**，
       而且**不懂代码的人也能翻**（拿 JSON 给翻译软件/人就行）。

  ② **查不到就返回原文**（`T("取消")` 在英文表里没有 → 返回 `"取消"`）
     ★★ 这条**极重要**：500 句里翻漏 3 句，
       界面会**显示中文**（看得懂），而**不会变成空白/报错**。
     ★ 判据：**"翻译缺失"必须"降级成能看懂"，不能"降级成崩溃"。**

  ③ **`T()` 只在"真的要显示"的时候调**，不在导入时调
     ★ 因为语言是**启动时**从设置读的 —— 导入时还不知道用哪种语言。

  ④ **支持"占位符"**：`T("共 {n} 项", n=5)` → `"5 items"`
     ★ 为什么不用 `%` 格式化：**不同语言的语序不同**，
       占位符让翻译者**自己决定把数字放哪儿**。

  ⑤ **术语表**（`术语表.json`）—— 把"标签/分类/根标签"这些**统一译法**
     固定下来。★ 不然 500 句里"标签"可能被翻成 Tag/Label/Mark 三种。

  ⑥ ★ **不做"热切换"**（用户定：重启生效）——
     切换语言 = 改设置 + 重启。**简单、稳**。

★★ 用法（主程序里）：
```python
from i18n import T, set_language, current_language
label = T("取消")                       # → "Cancel"
msg   = T("共 {n} 项", n=5)             # → "5 items"
```
"""
import io
import json
import os
import sys

# ---------- 状态 ----------
_LANG = "zh_CN"          # 当前语言代码
_TABLE = {}              # 当前语言的"原文 → 译文"表
_FALLBACK = {}           # 兜底表（通常是英文 —— 英文缺了就退回中文）
_MISSING = set()         # ★ 记下"哪些没翻到"（方便统计还差多少）
_LANG_DIR = None         # 语言文件目录


def _candidates_dir():
    """★ 语言文件可能在哪儿（**按顺序找，哪个有算哪个**）。

    ★ 为什么要这么找（不能写死一个路径）：
      · **源码跑**：`<程序目录>/语言/`
      · **打包成 exe**：`sys._MEIPASS/语言/`（打包时打进去的）
      · **用户自己加**：exe 旁边放个 `语言/` —— ★ 这样**别人能自己加语言**
        （不用重新打包！）★ 这一点很重要：**加语言不需要开发者**。

    ★★★ 2026-10-08 **实测踩的坑**：
      `i18n.py` 自己住在 `AIxiede拆分开\\程序分块\\` 里 ——
      所以 `dirname(__file__)/语言` 会算成
      **`AIxiede拆分开\\程序分块\\语言`**（**多了一层，那儿没有语言文件**）。
      → 实测语言列表里只有"中文"一个（因为那个目录不存在，
        走了兜底的 `out = [("zh_CN", ...)]`）。
      ★ 修法：**从 `__file__` 往上找 2~3 层**，
        哪一层有 `语言/` 就用哪一层。
      ★★ 教训：**拆出去的模块"找自己的资源"要多退几层** ——
        因为它的位置比主程序**深**。
    """
    cands = []
    here = os.path.dirname(os.path.abspath(__file__))
    up = here
    try:
        if getattr(sys, "frozen", False):
            mp = getattr(sys, "_MEIPASS", None)
            if mp:
                cands.append(os.path.join(mp, "语言"))
            cands.append(os.path.join(
                os.path.dirname(os.path.abspath(sys.executable)), "语言"))
        # ★ 从自己所在目录，一层层往上找（最多 3 层）
        for _ in range(4):
            cands.append(os.path.join(up, "语言"))
            nxt = os.path.dirname(up)
            if nxt == up:
                break
            up = nxt
    except Exception:
        pass
    for c in cands:
        try:
            if c and os.path.isdir(c) and os.listdir(c):
                return c
        except Exception:
            continue
    for c in cands:
        try:
            if c and os.path.isdir(c):
                return c
        except Exception:
            continue
    return cands[0] if cands else "语言"


def available_languages():
    """★ 现在有哪些语言可选：`[(代码, 显示名, 文件路径), ...]`。

    ★ **扫描目录**而不是写死列表 —— 这样：
      · **加语言 = 丢一个 json 文件进去**（不用改代码）
      · 用户自己也能加（★ 见 `_candidates_dir` 的说明）
    ★ 排在最前的是中文（默认）；找不到任何文件时**至少返回中文**，
      免得"语言菜单是空的"（那用户就没法选了）。
    """
    out = []
    d = _LANG_DIR or _candidates_dir()
    try:
        for f in sorted(os.listdir(d)):
            if not f.lower().endswith(".json"):
                continue
            code = f[:-5]
            label = code
            try:
                data = json.loads(io.open(os.path.join(d, f),
                                          encoding="utf-8").read())
                label = str(data.get("_label") or code)
            except Exception:
                pass
            out.append((code, label, os.path.join(d, f)))
    except Exception:
        pass
    if not out:
        out = [("zh_CN", "中文（简体）", os.path.join(d, "zh_CN.json"))]
    # ★ 中文排最前（默认语言）
    out.sort(key=lambda x: (0 if x[0].startswith("zh") else 1, x[0]))
    return out


def _load_table(code):
    """★ 读一个语言文件 → `(翻译表, 语言显示名)`。

    ★ 失败返回空表（**不抛错**）—— 语言文件坏了不该让程序打不开。
    """
    global _LANG_DIR
    _LANG_DIR = _LANG_DIR or _candidates_dir()
    for f in os.listdir(_LANG_DIR) if os.path.isdir(_LANG_DIR) else []:
        if f.lower() == (code + ".json").lower():
            try:
                data = json.loads(io.open(os.path.join(_LANG_DIR, f),
                                          encoding="utf-8").read())
                tbl = {k: v for k, v in data.items()
                       if not k.startswith("_") and isinstance(v, str)}
                return tbl, str(data.get("_label") or code)
            except Exception:
                return {}, code
    return {}, code


def set_language(code, fallback="en_US"):
    """★ **设置当前语言**（启动时调一次）。

    ★ 参数：
      · `code`     —— 语言代码（`zh_CN` / `en_US` / …）
      · `fallback` —— 兜底语言（★ 一般是英文：中文缺了它）
    ★ 中文（`zh_CN`）**不需要翻译表** —— 原文就是中文，
      所以 `T("取消")` 直接返回 `"取消"`。★ 这样省掉 754 条冗余数据。
    """
    global _LANG, _TABLE, _FALLBACK
    _LANG = str(code or "zh_CN")
    if _LANG.startswith("zh"):
        _TABLE = {}          # ★ 中文 = 原文，不用表
        _FALLBACK = {}
        return True
    _TABLE, _lbl = _load_table(_LANG)
    try:
        _FALLBACK = _load_table(fallback)[0] if fallback else {}
    except Exception:
        _FALLBACK = {}
    return bool(_TABLE)


def current_language():
    """★ 现在是什么语言。"""
    return _LANG


def T(text, **kw):
    """★★★ **翻译一句话**（界面上的字都走这里）。

    ★ 用法：
        T("取消")                    → 中文环境返回 "取消"；英文 "Cancel"
        T("共 {n} 项", n=5)          → "5 items"
    ★ 查找顺序：**当前语言 → 兜底语言（英文）→ 原文**。
      ★★ 最后一层"返回原文"是**安全网**：
        翻漏了只会**显示中文**（看得懂），**不会空白、不会报错**。
    ★ `kw` 是占位符值（`{n}` 这种）。
      ★ 用 `{}` 而不是 `%`：**不同语言语序不同**，
        让翻译者自己决定把数字放句首还是句尾。
    ★ 翻译失败（占位符名字对不上、译文格式错）→ **退回原文**，
      并把这事儿记到 `_MISSING`（不报错 —— 界面上的字不该让程序崩）。
    """
    s = str(text)
    try:
        if _LANG.startswith("zh"):
            out = s                       # ★ 中文：原文就是译文
        else:
            out = _TABLE.get(s)
            if out is None:
                out = _FALLBACK.get(s)
            if out is None:
                _MISSING.add(s)           # ★ 记一笔（统计还差多少）
                out = s
        if kw:
            try:
                out = out.format(**kw)
            except Exception:
                # ★ 占位符对不上（比如译文里写成 {num}）→ 退回原文再试一次
                try:
                    out = s.format(**kw)
                except Exception:
                    out = s
        return out
    except Exception:
        return s


def missing_count():
    """★ 这次运行**有多少句没翻到**（方便看"还差多少"）。"""
    return len(_MISSING)


def missing_list(limit=40):
    """★ 没翻到的句子列表（给开发者看"还差哪些"）。"""
    return sorted(_MISSING)[:limit]


def coverage(total):
    """★ **翻译覆盖率**（翻了多少 / 共多少）。

    ★ 为什么要这个东西：754 句翻起来是长期活儿 ——
      有个百分比，**才知道还差多远**（也方便给别人看"欢迎来翻"）。
    """
    try:
        total = int(total)
        if total <= 0:
            return "（没有统计）"
        done = total - len(_MISSING)
        return "%d / %d（%.0f%%）" % (done, total, done * 100.0 / total)
    except Exception:
        return "（算不了）"
