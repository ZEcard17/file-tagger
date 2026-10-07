# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：**背景图 + 颜色工具**。

★★ 这一组干什么：
   · `_hex_to_rgb` / `_rgb_to_hex`  —— 颜色字符串和 RGB 互转
   · `blend_color_over`             —— 两个颜色混合（面板"看着半透明"用的）
   · `average_color_of_image`       —— 取一张图的平均色
   · `make_background_layer`        —— **铺背景图**（支持 铺满/适应/平铺/居中）

★ 只借主程序**一个名字**：`note_swallowed`（记账用）—— 量过。
  ★ 借法见下面 `_set_app`（**不 import 主程序**，免得死循环）。

★ 代码**原样搬运**，逻辑一个字没改。
"""

import io
import os
import sys

import tkinter as tk

# ---------- 「用的时候才借」 ----------
_APP = None


def _set_app(app):
    """主程序启动时调一下，把「自己」交给这里。"""
    global _APP
    _APP = app


def _need(name, default=None):
    """★ 向主程序要一个名字（要不到就用 default）。"""
    try:
        if _APP is not None:
            return getattr(_APP, name, default)
    except Exception:
        pass
    return default


def note_swallowed(*a, **kw):
    """★ 借来的函数（现取，永远拿最新那个）。"""
    f = _need("note_swallowed")
    if f is None:
        return None
    return f(*a, **kw)


def _hex_to_rgb(h):
    """`#rrggbb` → (r,g,b)；认不出来返回 None。"""
    try:
        s = str(h).strip().lstrip("#")
        if len(s) == 3:
            s = "".join(c * 2 for c in s)
        if len(s) != 6:
            return None
        return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
    except Exception:
        return None


def _rgb_to_hex(rgb):
    try:
        return "#%02x%02x%02x" % (int(rgb[0]), int(rgb[1]), int(rgb[2]))
    except Exception:
        return "#000000"


def blend_color_over(base_hex, over_hex, k):
    """★ 两个颜色按比例混：`k=0` 全是 base，`k=1` 全是 over。

    ★ 用途（**这是"看着像半透明"的关键**）：
      把"面板色"按 `k` 混进"背景图的平均色"——
      `k` 越小 → 越透（越像看到背景）；越大 → 面板越实（越清楚）。
      ★ 不是真透明（Tk 做不到），但**看起来就是这个意思**，
        而且**文字永远清楚**。
    """
    a = _hex_to_rgb(base_hex)
    b = _hex_to_rgb(over_hex)
    if a is None:
        return over_hex or "#000000"
    if b is None:
        return base_hex or "#000000"
    k = max(0.0, min(1.0, float(k)))
    return _rgb_to_hex(tuple(a[i] * (1 - k) + b[i] * k for i in range(3)))


def average_color_of_image(path, blur=0):
    """★ 取一张图的**平均色**（缩到 1x1 再读，最省事也最准）。

    ★ 为什么要它：面板色要"混进图的颜色"才像半透明 ——
      而这个"图的颜色"最合适的代表就是**平均色**。
    ★ `blur` > 0 时，先模糊再取（跟实际铺上去的效果一致）。
    """
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB")
        if blur and blur > 0:
            from PIL import ImageFilter
            im = im.filter(ImageFilter.GaussianBlur(radius=float(blur)))
        im = im.resize((1, 1), Image.LANCZOS)
        return _rgb_to_hex(im.getpixel((0, 0)))
    except Exception as exc:
        try:
            note_swallowed("读背景图平均色失败", exc, level="warn")
        except Exception:
            pass
        return None


def make_background_layer(parent, path, mode="cover", blur=0,
                          fallback_bg=None):
    """★★ **铺背景图** —— 返回一个 `tk.Label`（已经 `place` 满整个 parent）。

    ★ 用法：
        lbl = make_background_layer(root, "D:/图.jpg", "cover", blur=12)
        lbl.lower()          # ★ 压到最底层（不然会盖住控件）

    ★ 参数：
      · `parent`   —— 铺在哪个容器里（一般是 `self.root`）
      · `path`     —— 图片路径（**不存在/读不了就返回 None**，不抛错）
      · `mode`     —— `cover`（铺满）/ `contain`（完整显示）/ `tile`（平铺）/ `center`
      · `blur`     —— 高斯模糊半径（**0 = 不模糊**；`8~20` 看着像毛玻璃）
      · `fallback_bg` —— 图读不了时，铺一块这个颜色（**保证不会露出一片白**）

    ★★ 为什么"失败要给 fallback_bg"：
      用户设了背景图但文件被删了/挪了 → 如果只是"铺不上"，
      窗口底下就是**系统默认的浅灰** → **夜间模式下会闪一片白**
      （用户报过好几次"夜间还有白"）。所以这里**必须有兜底色**。
    """
    layer = None
    img = None
    try:
        if path and os.path.isfile(path):
            from PIL import Image, ImageTk, ImageFilter
            img = Image.open(path).convert("RGB")
            if blur and float(blur) > 0:
                img = img.filter(
                    ImageFilter.GaussianBlur(radius=float(blur)))
            # ★ 按 parent 当前尺寸缩放（不够就撑到够，免得留白）
            try:
                pw = max(1, parent.winfo_width())
                ph = max(1, parent.winfo_height())
            except Exception:
                pw, ph = 1000, 700
            if mode == "cover":
                # ★ 等比放大到"铺满"，多出来的裁掉
                r = max(pw / img.width, ph / img.height)
                nw, nh = max(1, int(img.width * r)), max(1, int(img.height * r))
                img2 = img.resize((nw, nh), Image.LANCZOS)
                left = max(0, (nw - pw) // 2)
                top = max(0, (nh - ph) // 2)
                img = img2.crop((left, top, left + pw, top + ph))
            elif mode == "contain":
                r = min(pw / img.width, ph / img.height)
                img = img.resize((max(1, int(img.width * r)),
                                  max(1, int(img.height * r))), Image.LANCZOS)
            elif mode == "center":
                pass                    # 原尺寸居中（不缩放）
            # ★ tile 不缩放，用 PIL 自己拼一张够大的（Tk 的 Label 不会平铺）
            elif mode == "tile":
                nw = max(pw, img.width)
                nh = max(ph, img.height)
                big = Image.new("RGB", (nw, nh))
                for y in range(0, nh, img.height):
                    for x in range(0, nw, img.width):
                        big.paste(img, (x, y))
                img = big.crop((0, 0, pw, ph))
            photo = ImageTk.PhotoImage(img)
            layer = tk.Label(parent, image=photo, bd=0, highlightthickness=0)
            # ★ 把 PhotoImage 挂在 Label 上 —— 不挂的话会被垃圾回收，图变白
            layer._bg_photo = photo
            layer.place(x=0, y=0, relwidth=1, relheight=1)
            layer.lower()
            return layer
    except Exception as exc:
        try:
            note_swallowed("铺背景图失败（会用兜底色）", exc, level="warn")
        except Exception:
            pass
        try:
            if layer is not None:
                layer.destroy()
        except Exception:
            pass
        layer = None
    # ★ 兜底：图没读成 → 铺一块颜色（**避免露出一片白**）
    try:
        if fallback_bg:
            layer = tk.Label(parent, bg=fallback_bg, bd=0,
                             highlightthickness=0)
            layer.place(x=0, y=0, relwidth=1, relheight=1)
            layer.lower()
            return layer
    except Exception:
        pass
    return None
