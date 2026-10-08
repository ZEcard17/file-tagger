# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：**电子书元数据 + 视频缩略图 + 缓存清理 + 网盘索引**。

★★ 这是**第 2 批拆分**。挑它们的理由（**量过**）：
```
   _mobi_meta_and_text      155 行  依赖 1 个
   _epub_chapters           140 行  ★ 零依赖
   get_video_thumbnail_pil  103 行  ★ 零依赖
   _cache_clean_old         120 行  依赖 2 个
   scan_index_root_via_api  130 行  依赖 2 个
```
   ★ 共同点：**`self.app` 出现 0 次**（不碰界面）、被别处引用 <= 3 次。

★★ 拆文件的规矩（跟第 1 批一个套路，见 `TagStore.py` 的说明）：
   ① Python 自带的直接 import
   ② **只有「主程序自己造的东西」才借** —— 而且**不 import 主程序**
      （会互相 import → 死循环）。借法是主程序启动时调 `_set_app`。
   ③ ★★ **借"变量/常量"要用代理对象**（`_Borrowed`）——
      不能用"取一次的值"：`CAT_COLORS` 这类**换皮肤时会变**，
      取一次就**永远是旧的**（错题本 #145）。

★ 代码**原样搬运**，逻辑一个字没改。
"""

import os
import sys
import re
import time
import json
import threading

# ★ 这几个是用到了但没 import 的（用工具查出来的，不是猜的）
import shutil
import tempfile
import zipfile


# ---------- 「用的时候才借」 ----------
_APP = None


def _set_app(app):
    """主程序启动时调一下，把「自己」交给这里。

    ★ 为什么不直接 `import AIxiede`：两边互相 import 会让 Python
      **转不出来**（拿到半成品模块）。→ 只让**主程序认识本文件**，
      本文件**不认识主程序**，用的时候再从 `_APP` 取。**方向单一。**
    """
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


class _Borrowed(object):
    """★★★ **"借来的名字"的代理** —— 读的时候现去主程序取。

    ★★★ 为什么必须有它（**实测踩出来的**，错题本 #145）：
      我第一版只生成了 `_borrow_XXX()` 这种小函数，
      **但代码里写的是 `XXX`**（小函数根本没人调）→ `NameError`。
      → 所以要把名字**真的绑到模块级**。

    ★ 为什么绑成"代理"而不是"取一次的值"：
      · `DB_PATH` 这类**不变** → 取一次也行
      · 但 `CAT_COLORS` 这类**换皮肤时会变** → 取一次就**永远是旧的**
        （而且这个 bug **很隐蔽**：换皮肤后**只有标签配色不变**）
      → **统一用代理**：不管常量还是会变的，**每次读都现取**，
        **行为永远对，也不用分情况判断**。
    """

    __slots__ = ("_bname",)

    def __init__(self, name):
        object.__setattr__(self, "_bname", name)

    def _now(self):
        return _need(object.__getattribute__(self, "_bname"))

    def __repr__(self):
        return repr(self._now())

    def __str__(self):
        return str(self._now())

    def __bool__(self):
        return bool(self._now())

    def __len__(self):
        return len(self._now())

    def __iter__(self):
        return iter(self._now())

    def __getitem__(self, k):
        return self._now()[k]

    def __contains__(self, k):
        return k in self._now()

    def __eq__(self, o):
        return self._now() == o

    def __hash__(self):
        return hash(repr(self._now()))

    def __call__(self, *a, **kw):
        return self._now()(*a, **kw)

    def __getattr__(self, k):
        return getattr(self._now(), k)

    def __setattr__(self, k, v):
        setattr(self._now(), k, v)

    def __setitem__(self, k, v):
        self._now()[k] = v


# ---------- 借来的函数（现取，永远拿最新那个）----------




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
            return self._now() < o


    def __le__(self, o):
            return self._now() <= o


    def __gt__(self, o):
            return self._now() > o


    def __ge__(self, o):
            return self._now() >= o


    def __ne__(self, o):
            return self._now() != o


    def __mul__(self, o):
            return self._now() * o


    def __rmul__(self, o):
            return o * self._now()


    def __sub__(self, o):
            return self._now() - o


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


    def __round__(self, n=None):
            return round(self._v(), n) if n else round(self._v())


    def __abs__(self):
            return abs(self._v())


    def __int__(self):
            return int(self._v())


    def __float__(self):
            return float(self._v())


    def __index__(self):
            return self._v().__index__()


    def __next__(self):
            return next(self._v())


    def __neg__(self):
            return -self._v()


    def __pos__(self):
            return +self._v()


    def __invert__(self):
            return ~self._v()


    def __bytes__(self):
            return bytes(self._v())


    def __fspath__(self):
            return os.fspath(self._v())


    def __format__(self, spec):
            return format(self._v(), spec)


    def __copy__(self):
            return self._v()


    def __enter__(self):
            return self._v().__enter__()


    def __exit__(self, *a):
            return self._v().__exit__(*a)


    def __add__(self, o):
            return self._v() + o


    def __radd__(self, o):
            return o + self._v()

def _preview_cache_dir(*a, **kw):
    """★ 借来的函数（现取）。"""
    f = _need('_preview_cache_dir')
    if f is None:
        raise RuntimeError("本模块需要主程序的 %s，但它还没接上"
                           "（主程序启动时应调用 _set_app）" % '_preview_cache_dir')
    return f(*a, **kw)


def cd_api_workers(*a, **kw):
    """★ 借来的函数（现取）。"""
    f = _need('cd_api_workers')
    if f is None:
        raise RuntimeError("本模块需要主程序的 %s，但它还没接上"
                           "（主程序启动时应调用 _set_app）" % 'cd_api_workers')
    return f(*a, **kw)


def load_ui_setting(*a, **kw):
    """★ 借来的函数（现取）。"""
    f = _need('load_ui_setting')
    if f is None:
        raise RuntimeError("本模块需要主程序的 %s，但它还没接上"
                           "（主程序启动时应调用 _set_app）" % 'load_ui_setting')
    return f(*a, **kw)


def note_swallowed(*a, **kw):
    """★ 借来的函数（现取）。"""
    f = _need('note_swallowed')
    if f is None:
        raise RuntimeError("本模块需要主程序的 %s，但它还没接上"
                           "（主程序启动时应调用 _set_app）" % 'note_swallowed')
    return f(*a, **kw)


def prune_orphan_dir_cache(*a, **kw):
    """★ 借来的函数（现取）。"""
    f = _need('prune_orphan_dir_cache')
    if f is None:
        raise RuntimeError("本模块需要主程序的 %s，但它还没接上"
                           "（主程序启动时应调用 _set_app）" % 'prune_orphan_dir_cache')
    return f(*a, **kw)


def scan_index_root_via_api(client, store, rid, root_path, cancel_flag=None,
                            progress_cb=None, workers=None):
    """★ v25 补丁17：通过 CloudDrive2 本地接口扫一个网盘根目录，写进 dir_cache。

    返回 (目录数, 文件数, 说明字符串)，含义跟挂载盘那套完全一致：
      - 目录数只统计「真的列到了内容」的目录；
      - 列不到的目录先记着，整棵树扫完之后自动补扫两轮（隔 1 秒 / 3 秒）；
      - 两轮都读不到才算「跳过 N 个目录」，说明照样是「人话」。

    为什么可以并发：CloudDrive2 自己管着每个网盘的「每秒查询数」上限，
    我们只要别一次发太多（默认 4 个并发）就行。实测单个目录 0.4 秒左右，
    4 个并发把 3000 多个目录压到几分钟，比过 WinFSP 一层层摸快得多。
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    root_cd = None
    try:
        root_cd = client.cd_path_of(root_path)
    except Exception:
        root_cd = None
    if not root_cd:
        return 0, 0, "这个根目录不在 CloudDrive2 里（不是网盘目录？）"
    if not workers:
        workers = cd_api_workers()

    pending = [root_cd]
    retry = []
    skipped = []
    skip_count = 0
    round_no = 0
    dir_count = 0
    file_count = 0
    stat_skip = 0
    last_err = ""

    def _cancelled():
        try:
            return bool(cancel_flag and cancel_flag())
        except Exception:
            return False

    with ThreadPoolExecutor(max_workers=workers) as pool:
        while pending or (retry and round_no < 2):
            if _cancelled():
                break
            if not pending:
                # 主扫描跑完了，回头补扫刚才读不到的目录
                round_no += 1
                try:
                    time.sleep(1.0 if round_no == 1 else 3.0)
                except Exception:
                    pass
                pending = retry
                retry = []
            # 一批一批发（别把几千个请求一次性塞进去）
            batch = pending[:max(workers * 4, 8)]
            del pending[:len(batch)]
            futs = {}
            for p in batch:
                futs[pool.submit(client.list_dir, p)] = p
            for fut in as_completed(futs):
                if _cancelled():
                    break
                p = futs[fut]
                try:
                    entries = fut.result()
                    ok = True
                    err = ""
                except Exception as exc:
                    ok = False
                    err = str(exc)
                if ok:
                    key = None
                    if p.strip("/") == root_cd.strip("/"):
                        key = root_path            # 根目录沿用原来的写法（带结尾反斜杠）
                    else:
                        try:
                            key = client.unc_path_of(p)
                        except Exception:
                            key = None
                    if not key:
                        key = p
                    try:
                        store.save_dir_entries(key, entries)
                    except Exception as exc:
                        last_err = str(exc)
                    dir_count += 1
                    for nm, is_d, sz, _mt in entries:
                        if is_d:
                            pending.append(p.rstrip("/") + "/" + nm)
                        else:
                            file_count += 1
                            if sz is None:
                                stat_skip += 1
                else:
                    last_err = err
                    if round_no < 2:
                        retry.append(p)            # 留着待会儿补扫
                    else:
                        skip_count += 1            # 补扫也读不到，才算真的跳过
                        if len(skipped) < 3:
                            skipped.append(p)
                if progress_cb is not None:
                    try:
                        progress_cb(rid, root_path, dir_count, file_count, p)
                    except Exception:
                        pass

    err_line = last_err
    if skip_count:
        parts = "、".join(skipped)
        more = "…" if skip_count > len(skipped) else ""
        err_line = (f"跳过 {skip_count} 个目录（这些目录在网盘里已经不存在了 / "
                    f"一时读不到，不影响其它目录）：{parts}{more}")
    if stat_skip and not err_line:
        err_line = (f"有 {stat_skip} 个文件读不到大小"
                    f"（网盘文件常见，列表里会显示成问号）")
    # ★ v25 补丁20：扫完顺手把「幽灵目录」清掉（网盘里删掉的目录留下的空壳），
    #   这样索引里不会一直留着一小撮点开就报错的目录。
    try:
        n_dirs, n_rows = prune_orphan_dir_cache(store, root_path)
        if n_dirs:
            err_line = ((err_line + "  ·  " if err_line else "")
                        + f"顺带清掉 {n_dirs} 个已经不存在的目录缓存"
                          f"（{n_rows} 行）")
    except Exception:
        pass
    return dir_count, file_count, err_line


def _epub_chapters(path):
    """★ v25 补丁29：把 EPUB 拆成 [(章节名, 纯文本), ...]。

    EPUB 本质就是个 zip：里面是 spine 里按阅读顺序排的 XHTML 文件。
    这里用标准库 zipfile + html.parser 解析（**不需要装任何东西**）。
    解析失败返回 []。
    """
    import zipfile
    import html.parser

    class _TextGrab(html.parser.HTMLParser):
        """把 HTML 抠成纯文字（跳过 script/style，块级标签之间加换行）。"""

        SKIP = {"script", "style", "head"}
        BREAK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4",
                 "h5", "h6", "section", "article"}

        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.buf = []
            self._skip = 0
            self.title = None
            self._in_title = False

        def handle_starttag(self, tag, attrs):
            t = tag.lower()
            if t in self.SKIP:
                self._skip += 1
            if t in self.BREAK:
                self.buf.append("\n")
            if t == "title":
                self._in_title = True

        def handle_endtag(self, tag):
            t = tag.lower()
            if t in self.SKIP and self._skip:
                self._skip -= 1
            if t in self.BREAK:
                self.buf.append("\n")
            if t == "title":
                self._in_title = False

        def handle_data(self, data):
            if self._in_title and not self.title:
                self.title = data.strip()
            if self._skip:
                return
            self.buf.append(data)

        def text(self):
            s = "".join(self.buf)
            # 去掉多余空行
            lines = [ln.strip() for ln in s.splitlines()]
            out = []
            for ln in lines:
                if ln:
                    out.append(ln)
                elif out and out[-1] != "":
                    out.append("")
            return "\n".join(out).strip()

    try:
        z = zipfile.ZipFile(path)
    except Exception:
        return []
    names = z.namelist()
    order = []

    def _read(name):
        try:
            return z.read(name)
        except Exception:
            return b""

    # ① 想从 content.opf 里拿 spine（最准），拿不到就按文件名排
    opf_name = None
    for n in names:
        if n.lower().endswith(".opf"):
            opf_name = n
            break
    if opf_name:
        try:
            raw = _read(opf_name).decode("utf-8", "replace")
            import re as _re
            base_dir = os.path.dirname(opf_name)
            # manifest: id -> href
            id2href = {}
            for m in _re.finditer(
                    r"<item\b[^>]*\bid=[\"']([^\"']+)[\"'][^>]*>", raw):
                tag = m.group(0)
                h = _re.search(r'href=["\']([^"\']+)["\']', tag)
                if h:
                    id2href[m.group(1)] = h.group(1)
            for m in _re.finditer(
                    r"<itemref\b[^>]*\bidref=[\"']([^\"']+)[\"'][^>]*/?>", raw):
                h = id2href.get(m.group(1))
                if h:
                    full = (base_dir + "/" + h) if base_dir else h
                    order.append(full)
        except Exception:
            order = []
    if not order:
        for n in names:
            low = n.lower()
            if low.endswith((".xhtml", ".html", ".htm")) and "/" in low:
                order.append(n)
        order.sort()

    chapters = []
    for n in order:
        if n not in names:
            # 路径写法可能带 ./ 或反斜杠
            cand = [x for x in names if x.endswith(n.split("/")[-1])]
            if not cand:
                continue
            n = cand[0]
        raw = _read(n)
        for enc in ("utf-8", "utf-16", "gbk"):
            try:
                text = raw.decode(enc)
                break
            except Exception:
                text = None
        if text is None:
            continue
        p = _TextGrab()
        try:
            p.feed(text)
        except Exception:
            continue
        body = p.text()
        if body:
            chapters.append((p.title or os.path.basename(n), body))
    try:
        z.close()
    except Exception:
        pass
    return chapters


def _mobi_meta_and_text(path):
    """★ v25 补丁29：从 MOBI / AZW / AZW3 里抠出「书名 + 正文」。

    MOBI 是二进制格式（PalmDOC 压缩），这里做**够用就好**的解析：
      · 读 PalmDB 头 → 找 MOBI 记录 → 解出书名和正文的起始位置；
      · 正文大多可能是压缩的（PalmDOC LZ77），能解就解一段纯文字。
    解析不出来就返回 (None, "")，界面会退回显示文件信息 + 提示用系统阅读器打开。
    """
    try:
        with open(path, "rb") as f:
            data = f.read()
    except Exception:
        return None, ""
    if len(data) < 200:
        return None, ""
    try:
        # --- PalmDB 头 ---
        num_records = int.from_bytes(data[76:78], "big")
        rec_offsets = []
        pos = 78
        for i in range(num_records):
            if pos + 8 > len(data):
                break
            off = int.from_bytes(data[pos:pos + 4], "big")
            rec_offsets.append(off)
            pos += 8
        if not rec_offsets:
            return None, ""
        rec_offsets.append(len(data))
        rec0 = data[rec_offsets[0]:rec_offsets[1]]
        if len(rec0) < 24:
            return None, ""
        # --- MOBI 头 ---
        if rec0[16:20] != b"MOBI":
            return None, ""
        header_len = int.from_bytes(rec0[20:24], "big")
        text_encoding = int.from_bytes(rec0[28:32], "big")
        # 书名在 MOBI 头里偏移 0x54（相对记录 0 开头）
        title = None
        try:
            tlen = int.from_bytes(rec0[0x54:0x58], "big")
            toff = int.from_bytes(rec0[0x58:0x5C], "big")
            if 0 < tlen < 500 and toff + tlen <= len(rec0):
                raw = rec0[toff:toff + tlen]
                title = raw.decode("utf-8", "replace").strip("\x00 ").strip()
        except Exception:
            title = None
        # --- 正文：第 1 条记录开始（记录 0 是头） ---
        # 压缩方式在 rec0[0:2]
        compression = int.from_bytes(rec0[0:2], "big")
        text_start_rec = 1
        chunk = data[rec_offsets[text_start_rec]:
                     rec_offsets[min(text_start_rec + 8, len(rec_offsets) - 1)]]
        txt = ""
        if compression == 1:            # 不压缩
            txt = chunk.decode("utf-8", "replace")
        elif compression == 2:          # PalmDOC LZ77
            out = bytearray()
            i = 0
            n = len(chunk)
            while i < n and len(out) < 40000:
                c = chunk[i]
                i += 1
                if c == 0:
                    out.append(0)
                elif 1 <= c <= 8:
                    out.extend(chunk[i:i + c])
                    i += c
                elif c <= 0x7F:
                    out.append(c)
                elif c <= 0xBF:
                    if i >= n:
                        break
                    c2 = chunk[i]
                    i += 1
                    pair = (c << 8) | c2
                    dist = (pair >> 3) & 0x07FF
                    length = (pair & 7) + 3
                    if dist == 0:
                        continue
                    start = len(out) - dist
                    for k in range(length):
                        idx2 = start + k
                        if 0 <= idx2 < len(out):
                            out.append(out[idx2])
                        elif len(out) > 100000:
                            break
                else:
                    out.append(32)
                    out.append(c ^ 0x80)
            txt = out.decode("utf-8", "replace")
        else:
            txt = ""
        # 只留能看的字符
        keep = []
        for ch in txt:
            o = ord(ch)
            if ch in "\n\r\t" or (32 <= o < 0x110000 and o != 0xFFFD):
                keep.append(ch)
            else:
                keep.append(" ")
        txt = "".join(keep)
        # ★ 补丁29：MOBI 正文里常混着 HTML 标签（<html><head>…），
        #   这里用同一个 HTML 解析器把标签和脚本抠掉，只留文字。
        try:
            import html.parser

            class _G2(html.parser.HTMLParser):
                SKIP = {"script", "style", "head"}
                BREAK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3",
                         "h4", "h5", "h6"}

                def __init__(self):
                    super().__init__(convert_charrefs=True)
                    self.buf = []
                    self._skip = 0

                def handle_starttag(self, tag, attrs):
                    t = tag.lower()
                    if t in self.SKIP:
                        self._skip += 1
                    if t in self.BREAK:
                        self.buf.append("\n")

                def handle_endtag(self, tag):
                    t = tag.lower()
                    if t in self.SKIP and self._skip:
                        self._skip -= 1
                    if t in self.BREAK:
                        self.buf.append("\n")

                def handle_data(self, d):
                    if not self._skip:
                        self.buf.append(d)

            if "<" in txt and ">" in txt:
                g = _G2()
                g.feed(txt)
                cleaned = "".join(g.buf)
                lines = [ln.strip() for ln in cleaned.splitlines()]
                txt = "\n".join(ln for ln in lines if ln)
        except Exception:
            pass
        # 压掉连着的空行
        while "\n\n\n" in txt:
            txt = txt.replace("\n\n\n", "\n\n")
        return (title or None), txt.strip()
    except Exception as exc:
        try:
            note_swallowed("MOBI 解析失败", exc)
        except Exception:
            pass
        return None, ""


def get_video_thumbnail_pil(path, size=320):
    """★ 补丁27+43：给视频弄一张「封面图」（PIL 图片对象），弄不到返回 None。

    按省事程度依次试：
      1) 问 Windows 资源管理器要它自己生成的缩略图；
      2) 机器上要是装了 ffmpeg，就截第 1 秒那一帧（没装也不影响）；
      3) cv2 直接解码（★★★ 重装系统后 Windows 缩略图丢失，主要靠这个）；
      4) 都不行返回 None，调用方显示「▶ 视频」提示牌。
    """
    # ① Windows 缩略图（走 pywin32 的 shell 接口）
    try:
        import pythoncom  # type: ignore
        import win32com.client  # type: ignore
        from PIL import Image  # type: ignore
        import io

        pythoncom.CoInitialize()
        try:
            shell = win32com.client.Dispatch("Shell.Application")
            folder = shell.Namespace(os.path.dirname(path))
            item = folder.ParseName(os.path.basename(path)) if folder else None
            if item is not None:
                for idx in range(0, 340):
                    try:
                        nm = folder.GetDetailsOf(None, idx)
                    except Exception:
                        nm = None
                    if nm and ("缩略图" in nm or "Thumbnail" in nm.lower()):
                        stream = item.ExtendedProperty(nm)
                        if stream is not None:
                            try:
                                data = stream.Read(stream.Stat()[2])
                                im = Image.open(io.BytesIO(data))
                                im.load()
                                im.thumbnail((size, size))
                                return im
                            except Exception:
                                pass
        finally:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass
    except Exception:
        pass
    # ② ffmpeg 截帧
    try:
        import shutil as _sh
        import subprocess as _sp
        import tempfile
        exe = _sh.which("ffmpeg")
        if exe:
            out = os.path.join(tempfile.gettempdir(),
                               "dsh_vthumb_%d.jpg" % os.getpid())
            r = _sp.run([exe, "-y", "-ss", "1", "-i", path, "-frames:v", "1",
                         "-vf", "scale=%d:-1" % int(size), out],
                        stdout=_sp.DEVNULL, stderr=_sp.DEVNULL, timeout=25,
                        creationflags=getattr(_sp, "CREATE_NO_WINDOW", 0))
            if r.returncode == 0 and os.path.exists(out):
                from PIL import Image  # type: ignore
                im = Image.open(out)
                im.load()
                try:
                    os.remove(out)
                except Exception:
                    pass
                return im
    except Exception:
        pass
    # ③ cv2 直接解码（★★★ 重装系统后 Windows 缩略图丢失，主要靠这个）
    if HAS_CV2:
        try:
            import cv2 as _cv2
            cap = _cv2.VideoCapture(path)
            if cap.isOpened():
                try:
                    total = int(cap.get(_cv2.CAP_PROP_FRAME_COUNT) or 0)
                    # 取约 1/4 处的帧（跳过开场黑帧/字幕）
                    # 注意：网络路径上 seek 到中间比从头读慢很多，
                    # 故先试 1/4，失败再从头（两头都试，保证有输出）
                    target_idx = max(1, total // 4) if total > 8 else 0
                    cap.set(_cv2.CAP_PROP_POS_FRAMES, target_idx)
                    ok, frame = cap.read()
                    if not ok:
                        cap.set(_cv2.CAP_PROP_POS_FRAMES, 0)
                        ok, frame = cap.read()
                    cap.release()
                    if ok and frame is not None:
                        frame = _cv2.cvtColor(frame, _cv2.COLOR_BGR2RGB)
                        from PIL import Image as _PIL_Image
                        im = _PIL_Image.fromarray(frame)
                        im.thumbnail((size, size), _PIL_Image.LANCZOS)
                        return im
                except Exception:
                    try:
                        cap.release()
                    except Exception:
                        pass
        except Exception:
            pass
    return None


def _cache_clean_old(d=None, force=False):
    """★★ 2026-10-06：按用户的「缓存设置」清理旧缓存。

    三种清理规则（都在「界面 → 📥 网盘预览缓存…」里能设）：
      · 无痕模式（cache_incognito）：删掉**别的会话**留下的目录（阅后即焚）
      · 定时清理（cache_ttl_hours）：多久没用过的文件就删
      · 超大小清理（cache_max_mb）：整个缓存目录超过多少 MB 就清最旧的

    返回一句人话说明（清理了多少、为什么）。**任何一步失败都不报错**
    —— 清缓存这种事绝不能影响正常使用。
    """
    import time as _t
    import tempfile as _tf
    removed = 0
    freed = 0
    why = []
    try:
        base = str(load_ui_setting("preview_cache_dir", "") or "").strip() \
            or os.path.join(_tf.gettempdir(), "file_tagger_cache")
        if not os.path.isdir(base):
            return "缓存目录不存在，不用清。"

        # ① 无痕模式：删掉别的会话目录
        try:
            if bool(load_ui_setting("cache_incognito", True)):
                mine = ""
                try:
                    mine = os.path.basename(_preview_cache_dir())
                except Exception:
                    mine = ""
                for name in os.listdir(base):
                    p = os.path.join(base, name)
                    if not os.path.isdir(p) or not name.startswith("本次_"):
                        continue
                    if name == mine:
                        continue          # 正在用的这个不能删
                    try:
                        sz = sum(os.path.getsize(os.path.join(dp, f))
                                 for dp, dn, fs in os.walk(p)
                                 for f in fs)
                    except Exception:
                        sz = 0
                    try:
                        shutil.rmtree(p, ignore_errors=True)
                        removed += 1
                        freed += sz
                        why.append("无痕：清掉上次会话")
                    except Exception:
                        pass
        except Exception:
            pass

        # ② 定时清理：太久没用的文件
        try:
            ttl = float(load_ui_setting("cache_ttl_hours", 24) or 0)
        except Exception:
            ttl = 24
        if ttl > 0:
            cut = _t.time() - ttl * 3600
            for dp, dn, fs in os.walk(base):
                for f in fs:
                    p = os.path.join(dp, f)
                    try:
                        if os.path.getmtime(p) < cut:
                            sz = os.path.getsize(p)
                            os.remove(p)
                            removed += 1
                            freed += sz
                    except Exception:
                        pass
            if removed:
                why.append("超时（%g 小时没用）" % ttl)

        # ③ 超大小清理：整个目录太大就把最旧的删掉，直到降到限制以下
        try:
            limit_mb = float(load_ui_setting("cache_max_mb", 2048) or 0)
        except Exception:
            limit_mb = 2048
        if limit_mb > 0:
            files = []
            total = 0
            for dp, dn, fs in os.walk(base):
                for f in fs:
                    p = os.path.join(dp, f)
                    try:
                        st = os.stat(p)
                        files.append((st.st_mtime, st.st_size, p))
                        total += st.st_size
                    except Exception:
                        pass
            limit = limit_mb * 1024 * 1024
            if total > limit:
                files.sort()          # 最旧的排前面
                dropped = 0
                for mt, sz, p in files:
                    if total <= limit:
                        break
                    try:
                        os.remove(p)
                        total -= sz
                        freed += sz
                        removed += 1
                        dropped += 1
                    except Exception:
                        pass
                if dropped:
                    why.append("超 %g MB 上限" % limit_mb)
    except Exception:
        pass

    if not removed:
        return "缓存很干净，不用清。"
    return ("已清理 %d 个缓存文件，腾出 %.1f MB（%s）"
            % (removed, freed / 1024 / 1024, "、".join(why) or "手动清理"))


# ★★ v26 补丁（2026-10-03）注意：**上面这个函数以前被原样写了两遍**，
#   两段的代码一字不差。Python 里后写的会盖掉先写的，所以运行时看不出
#   任何毛病 —— 但那是「白白多了一坨肉」，而且以后改一处忘了另一处，
#   就会出现「改了没反应」这种最难查的毛病。第二份已经删掉了。
