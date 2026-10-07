# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：**单位换算 + 网速/内存/硬盘的显示文本**。

★★ 为什么这一组要**整体搬**（不能一个一个搬）：
   它们**互相依赖**：
     `_net_speed_text` 用 `_bytes_per_sec_text`
     `_bytes_per_sec_text` 用 `_bytes_text`
     `_mem_text` 用 `_net_speed_text`
   → **拆开搬就要来回借，整体搬最干净。**

★★★ 这一组是**完全自洽的**（量过）：
   · **零外部依赖** —— 只用自己这一组的常量和函数
   · 没有 `self`、不碰界面
   · 纯函数：给数字，返回字符串

★ 代码**原样搬运**，逻辑一个字没改。
"""

import os
import sys
import time
import ctypes


_NET_PREV = {"t": 0.0, "in": 0, "out": 0}


# ★ 单位档位（**顺序不能乱**）—— B → KB → MB → GB → TB → PB


_BYTE_UNITS = ("B", "KB", "MB", "GB", "TB", "PB")


def _bytes_text(n, unit_sep=" "):
    """★★★ **把字节数说成人话** —— 自动跳档 + **真正定宽**（2026-10-08 重写）。

    ★★ 用户要求：「网速、硬盘单位什么的要**自动切换，根据快慢自动切换**」

    ★★ 旧实现的毛病（我都实测过）：
      ① **没有 GB** —— `1GB → 1024.0M`、`99GB → 101376.0M`（数字越来越长）
      ② **小数被吃掉** —— `1500 → 1K`（该是 1.5K）
      ③ **跨档不干净** —— `1048575 → 1024K`（该是 1.0M）
      ④ **单位写法不统一** —— `1K` 该是 `1KB`
      ⑤ ★★ **宽度忽大忽小** —— 长度在 **6~15** 之间跳 →
         **球每秒"变宽变窄"一次**，看着一直在抖（这是最烦人的）

    ★★ 我自己第一版"定宽"也**没做对**（实测宽度还有 5/6/7 三种）：
      · B 档写 `%3d` —— 可 `1023 B` 有 4 位数字，**溢出了**
      · KB 以上"1.0~9.9 一位小数、10~999 整数" —— **两种格式宽度不同**
      · `1048575` 除完是 `1023.999`，**四舍五入成 1024** → 跨档不干净
      · `inf` 会抛 `OverflowError`
      · `1e30` → `888178419700125 PB`（**数字爆长**，没有上限）

    ★★★ v2 的思路（跟 v1 有本质区别）：
      **不要"先算字符串再想办法对齐"，而是"先把数值规范化到 0~999.9，
        再用同一种格式输出"** —— 这样**天然同宽**。

      ① 跳档到"数值落在 0 ~ 999.9"
      ② ★ **跨档修正**：四舍五入后若是 1024（或 ≥1000）→ **再跳一档**
         （`1048575` → 修正成 `1.0 MB`，而不是 `1024 KB`）
      ③ ★ **统一格式**：**永远** `"%5.1f"` —— 也就是
         `  0.0 B` / `512.0 B` / `  1.5 KB` / ` 10.0 KB` / `999.0 KB`
         ★ 全都 "5 位数字 + 空格 + 单位" → **宽度铁定一样**
      ④ ★ **防爆**：超过 PB 就**夹在 PB**（不然数字会越来越长）；
         `inf` / `nan` / 负数 / 乱七八糟的输入 → **一律当 0**

    ★ 参数：
      · `n`         —— 字节数
      · `unit_sep`  —— 数字和单位之间放什么（默认一个空格）

    ★ 返回：**定宽**字符串，比如 `"  1.5 KB"` / `" 12.0 MB"` / `"512.0 B"`。
    """
    try:
        n = float(n)
    except Exception:
        n = 0.0
    # ★ 防爆：NaN / inf / 负数 → 当 0
    #   （`inf` 不防会抛 `OverflowError` —— 实测踩过）
    if n != n or n < 0:
        n = 0.0
    try:
        if n == float("inf"):
            n = 0.0
    except Exception:
        pass
    # ★★ 2026-10-08 v3：**夹上限** ——
    #   实测 `1e30` 会输出 `888178419700125.2 PB`（数字爆长，球被撑爆）。
    #   ★ 到了 PB 还超大 → **就显示 999.9 PB**（"大得没边了"的意思）。
    #     ★ 为什么不加 EB/ZB：那些单位**日常根本用不到**，
    #       加了只是让"数字越界"这件事**更难被发现**。
    try:
        if n > 999.9 * (1024.0 ** (len(_BYTE_UNITS) - 1)):
            n = 999.0 * (1024.0 ** (len(_BYTE_UNITS) - 1))
    except Exception:
        n = 0.0
    # ---- ① 跳到"数值落在 0 ~ 999.9" ----
    i = 0
    while n >= 1000.0 and i < len(_BYTE_UNITS) - 1:
        n /= 1024.0
        i += 1
    # ---- ② ★ 跨档修正：四舍五入后如果 ≥1000，再跳一档 ----
    #   ★ 为什么不能省：`1048575 / 1024 = 1023.999` →
    #     下面 `%5.1f` 会输出 `1024.0`（**看着像没跳档**）。
    #     ★ 实测就是这个把"跨档"弄脏的。
    while n >= 999.95 and i < len(_BYTE_UNITS) - 1:
        n /= 1024.0
        i += 1
    # ---- ③ ★ 统一格式（**这是"定宽"的关键**）----
    #   ★★ 2026-10-08 v3 修正（实测 v2 还差 1 个字符）：
    #     v2 用 `%5.1f` —— 结果 `999.0 B`（7 位）和 `  1.0 KB`（8 位）
    #     **差 1 个字符**，球还是会轻微抖一下。
    #     ★ 而且 `.0` 很啰嗦（`512.0 B` 该是 `512 B`）——
    #       **它俩其实是同一个原因**。
    #   ★ v3 的规矩：**整数就不带小数**，而且**给每个数字位留够地方**：
    #       字节档（B）  ：最多 4 位整数  → ` 512 B` / `1023 B`
    #       KB 以上      ：最多 3 位整数 + 1 位小数 → `  1.5 KB` / ` 10.0 KB`
    #     ★ **两档的总宽度算得一样长**（关键是 B 档也补一个空格）。
    #   ★ 为什么"整数不带小数"：
    #       网速每秒变 —— `24.4 KB/s` 和 `24 KB/s` 反复切会**跳一下**；
    #       但**小数位一直在变反而更难看**（`1.0` `10.0` `100.0` 对不齐）。
    #       ★ 所以折中：**统一"整数不补小数、非整数保留一位"**，
    #         宽度用"补空格"补平 —— 这样**宽度恒定、数字也自然**。
    unit = _BYTE_UNITS[i]
    # ★★ 2026-10-08 v5：**单位名统一占 2 格**（`B` 补成 `B `）——
    #   实测踩出来的：`B`（1 格）跟 `KB`（2 格）**差一个字符**。
    unit2 = unit if len(unit) >= 2 else (unit + " ")
    # ★★ v5 又修一处（实测：`878.9 KB` 比 `3 MB` 多一位）：
    #   **小数只在"数字小"的时候才用** ——
    #     · 0 ~ 9.9  ：`1.5`（一位小数，**含小数点 3 个字符**）
    #     · 10 ~ 99  ：` 42`（整数，**2 个字符 + 前导空格 = 3 格**）
    #     · 100 ~ 999：`999`（整数，**3 格**）
    #   ★ 关键在于**这三档的字符数都是 3**（小数点和前导空格互相顶替）——
    #     所以整串宽度**恒定**。
    #   ★ 为什么 10 以上不保留小数：
    #     网速每秒变，`24.4` 和 `24` 反复切会**跳**；
    #     而"整数档"看着更稳（这也是资源管理器的做法）。
    if abs(n - round(n)) < 0.05 or n >= 10:
        # 整数（10 以上一律整数；小于 10 时"刚好是整数"也走这里）
        if n < 10:
            # ` 5 `（3 格）—— 用 `%3d` 右边不留空，靠 unit2 补的那个空格对齐
            return "%3d%s%s" % (int(round(n)), " ", unit2)
        return "%3d%s%s" % (int(round(n)), unit_sep, unit2)
    # 0 ~ 9.9 的"非整数"：`1.5`（3 格，含小数点）
    return "%3.1f%s%s" % (n, unit_sep, unit2)


# ★ 兼容旧名字（程序里别处可能还在用 `_kb_text`）


def _kb_text(n):
    """★ 老名字，转给新函数（**保持兼容**，免得改一处连累别处）。"""
    return _bytes_text(n)


def _bytes_per_sec_text(n, unit_sep=" "):
    """★ **速度**专用：`12.3 KB/s`（自动跳档 + **定宽**）。

    ★ 跟 `_bytes_text` 的区别：**尾巴多个 `/s`** ——
      不写 `/s` 的话，看的人不知道是"总共多少"还是"每秒多少"。

    ★★ 2026-10-08 实测踩的坑（**改了三次才对**）：
      `_bytes_text` 为了"单位名对齐"，给 `B` 补了一个**尾空格**
      （`"512 B "`）—— 于是：
        · 直接接 `/s` → `512 B /s`（**空格跑到斜杠前面**，难看）
        · 用 `rstrip()` 去掉 → `512 B/s`（好看）**但宽度少一格**，
          球上"上下行"两个数字 → **一共差 2 格** → **球还是会抖**
      ★★ 正解：**不要去空格，而是把 `/s` 接在"单位"后面、
        用同一个位置补齐** ——
        也就是**速度版自己拼**，保证"数字 + 单位 + /s"总宽一致：
          `512 B/s `（B 档补一格）/ ` 24 KB/s`（KB 档本来就 2 格）
        → 两者**都是 8 格** ✔
    """
    try:
        s = _bytes_text(n, unit_sep)
    except Exception:
        return "—"
    # ★ 把"单位后面补的那一格"挪到 `/s` 后面 ——
    #   这样 `B` 档和 `KB` 档**总宽一样**（`512 B/s ` vs ` 24 KB/s`）
    if s.endswith(" "):
        return s.rstrip() + "/s "
    return s + "/s"


def _net_speed_text():
    """★ 网速：用 `GetIfTable2`（Windows 自带）读累计字节，两次相减 = 速度。

    ★ 实测：**能拿到**（下行 305.2 KB/s, 上行 551.8 KB/s），
      而且**不起进程、几乎不花时间** —— 适合每秒刷。
    ★ 失败就返回空串（球上会显示 `↓— ↑—`，不会崩）。
    """
    import ctypes
    import time as _t
    # ★★ 2026-10-08 **踩过的坑**：`import ctypes` **不会**带 `wintypes` 子模块 ——
    #   直接用 `wintypes.DWORD` 会 `AttributeError`，
    #   而它又被下面的 `except` 吞掉 → **整个函数静默返回空**（球上一直显示 `↓— ↑—`）。
    #   实测方法：把异常打出来（别吞）→ 一眼看到 "module ctypes has no attribute wintypes"。
    #   ★★ 同一个地方**还踩了第二个坑**：本程序**模块级没有 `import ctypes`**
    #     （一直是"函数内局部导入"的风格），所以这里也**必须自己导** ——
    #     不然 `NameError: name 'ctypes' is not defined`，
    #     同样被 `except` 吞掉、同样**静默返回空**。
    #   ★ 教训：**写新函数时，先看这个文件"别的函数是怎么导库的"** ——
    #     照它的风格来（这个文件是"谁用谁导"）。
    from ctypes import wintypes
    class MIB_IF_ROW2(ctypes.Structure):
        _fields_ = [
            ("InterfaceLuid", ctypes.c_ulonglong),
            ("InterfaceIndex", wintypes.DWORD),
            ("InterfaceGuid", ctypes.c_byte * 16),
            ("Alias", ctypes.c_wchar * 257),
            ("Description", ctypes.c_wchar * 257),
            ("PhysicalAddressLength", wintypes.DWORD),
            ("PhysicalAddress", ctypes.c_byte * 32),
            ("PermanentPhysicalAddress", ctypes.c_byte * 32),
            ("Mtu", wintypes.DWORD), ("Type", wintypes.DWORD),
            ("TunnelType", wintypes.DWORD),
            ("MediaType", wintypes.DWORD),
            ("PhysicalMediumType", wintypes.DWORD),
            ("AccessType", wintypes.DWORD),
            ("DirectionType", wintypes.DWORD),
            ("InterfaceAndOperStatusFlags", ctypes.c_byte),
            ("OperStatus", wintypes.DWORD),
            ("AdminStatus", wintypes.DWORD),
            ("MediaConnectState", wintypes.DWORD),
            ("NetworkGuid", ctypes.c_byte * 16),
            ("ConnectionType", wintypes.DWORD),
            ("TransmitLinkSpeed", ctypes.c_ulonglong),
            ("ReceiveLinkSpeed", ctypes.c_ulonglong),
            ("InOctets", ctypes.c_ulonglong),
            ("InUcastPkts", ctypes.c_ulonglong),
            ("InNUcastPkts", ctypes.c_ulonglong),
            ("InDiscards", ctypes.c_ulonglong),
            ("InErrors", ctypes.c_ulonglong),
            ("InUnknownProtos", ctypes.c_ulonglong),
            ("InUcastOctets", ctypes.c_ulonglong),
            ("InMulticastOctets", ctypes.c_ulonglong),
            ("InBroadcastOctets", ctypes.c_ulonglong),
            ("OutOctets", ctypes.c_ulonglong),
            ("OutUcastPkts", ctypes.c_ulonglong),
            ("OutNUcastPkts", ctypes.c_ulonglong),
            ("OutDiscards", ctypes.c_ulonglong),
            ("OutErrors", ctypes.c_ulonglong),
            ("OutUcastOctets", ctypes.c_ulonglong),
            ("OutMulticastOctets", ctypes.c_ulonglong),
            ("OutBroadcastOctets", ctypes.c_ulonglong),
            ("OutQLen", ctypes.c_ulonglong)]

    class MIB_IF_TABLE2(ctypes.Structure):
        _fields_ = [("NumEntries", ctypes.c_ulong),
                    ("Table", MIB_IF_ROW2 * 1)]

    iphlp = ctypes.windll.iphlpapi
    tb = ctypes.POINTER(MIB_IF_TABLE2)()
    if iphlp.GetIfTable2(ctypes.byref(tb)) != 0:
        return ""
    try:
        n = tb.contents.NumEntries
        rows = ctypes.cast(tb.contents.Table,
                           ctypes.POINTER(MIB_IF_ROW2 * n)).contents
        tin = tout = 0
        for row in rows:
            if row.OperStatus == 1:          # ★ 1 = 已连接
                tin += row.InOctets
                tout += row.OutOctets
    finally:
        try:
            iphlp.FreeMibTable(tb)
        except Exception:
            pass
    now = _t.time()
    p = _NET_PREV
    if p["t"] > 0 and now > p["t"]:
        dt = now - p["t"]
        din = max(0, tin - p["in"]) / dt
        dout = max(0, tout - p["out"]) / dt
        # ★★ 2026-10-08：用**速度专用**的换算（自动跳档 + 定宽 + 带 `/s`）
        #   ★ 定宽是**关键**：球上的字每秒变一次，位数一变**球就变形**
        #     （实测旧实现长度在 6~15 之间跳）。
        #   ★ 带 `/s` 是免得看的人不知道"这是每秒多少"还是"总共多少"。
        txt = "↓%s ↑%s" % (_bytes_per_sec_text(din),
                           _bytes_per_sec_text(dout))
    else:
        txt = "↓… ↑…"
    p["t"], p["in"], p["out"] = now, tin, tout
    return txt


def _mem_text():
    """★ 内存占用（`psapi.GetPerformanceInfo`，纯 ctypes，实测好使）。"""
    import ctypes
    from ctypes import wintypes   # ★ 同上：必须显式导入（见 `_net_speed_text` 说明）
    class PERFINFO(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD),
                    ("CommitTotal", ctypes.c_size_t),
                    ("CommitLimit", ctypes.c_size_t),
                    ("CommitPeak", ctypes.c_size_t),
                    ("PhysicalTotal", ctypes.c_size_t),
                    ("PhysicalAvailable", ctypes.c_size_t),
                    ("SystemCache", ctypes.c_size_t),
                    ("KernelTotal", ctypes.c_size_t),
                    ("KernelPaged", ctypes.c_size_t),
                    ("KernelNonpaged", ctypes.c_size_t),
                    ("PageSize", ctypes.c_size_t),
                    ("HandleCount", wintypes.DWORD),
                    ("ProcessCount", wintypes.DWORD),
                    ("ThreadCount", wintypes.DWORD)]
    pi = PERFINFO()
    pi.cb = ctypes.sizeof(PERFINFO)
    if not ctypes.windll.psapi.GetPerformanceInfo(ctypes.byref(pi), pi.cb):
        return ""
    total = pi.PhysicalTotal * pi.PageSize
    avail = pi.PhysicalAvailable * pi.PageSize
    if total <= 0:
        return ""
    used = (total - avail) / 1024.0 ** 3
    pct = int(round((total - avail) * 100.0 / total))
    return "RAM %.1fG %d%%" % (used, pct)


def _disk_speed_text():
    """★ 硬盘读写：`typeperf`（Windows 自带）。

    ★★ 为什么是"每 5 秒"而不是每秒（实测出来的，不是偷懒）：
      · `typeperf` 一次要 **1.26 秒**（要起一个进程）；
      · 试过用 ctypes 走 `IOCTL_DISK_PERFORMANCE`（理论上是"读内存"很快），
        但实测 **错误码 6（要管理员权限）** —— 普通权限拿不到。
      → 只能慢点刷（跑在后台线程里，**不卡界面**）。
    ★ 失败返回空串（球上显示 `R— W—`，不会崩）。
    """
    import subprocess
    try:
        r = subprocess.run(
            ["typeperf",
             r"\PhysicalDisk(_Total)\Disk Read Bytes/sec",
             r"\PhysicalDisk(_Total)\Disk Write Bytes/sec",
             "-sc", "1"],
            capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace",
            creationflags=0x08000000)      # ★ 不弹黑框
        lines = [L for L in (r.stdout or "").split("\n") if L.strip('" ,')]
        # ★ 最后一行数据形如："时间","读","写"
        for L in reversed(lines):
            parts = [p.strip('"') for p in L.split(",")]
            nums = []
            for p in parts:
                try:
                    nums.append(float(p))
                except Exception:
                    pass
            if len(nums) >= 2:
                # ★★ 2026-10-08：用**速度专用**的换算（自动跳档 + 定宽 + `/s`）
                #   ★ 硬盘读写是"每秒字节数"（typeperf 的计数器就叫
                #     `Disk Read Bytes/sec`）—— 所以也要带 `/s`。
                return "R%s W%s" % (_bytes_per_sec_text(nums[-2]),
                                    _bytes_per_sec_text(nums[-1]))
    except Exception:
        pass
    return ""
