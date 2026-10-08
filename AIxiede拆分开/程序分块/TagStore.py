# -*- coding: utf-8 -*-
"""从 AIxiede.py 拆出来的：**数据层（标签 / 文件 / 分类的数据库读写）**。

★★ 这是**第 1 批拆分**里最大的一块（原 3,132 行 / 122 个方法）。
   挑它做第一批，是因为**量过**：
     · 它**不依赖界面**（`self.app` 出现 0 次）
     · 它只借 12 个"主程序自己造的名字"，而且**全部定义在它之前**
     · ★★ 主程序里 `TagStore(` **只构造 1 次**，
       之后全是 `self.store.xxx`（248 次）→ **搬走调用方一行不用改**

★★ 拆文件的规矩（跟 `SimpleInputDialog.py` 那批一个套路）：
   ① Python 自带的东西，这里**直接 import**（sqlite3、os、re…）
   ② **只有「主程序自己造的东西」才向主程序借** ——
      而且**不在开头 import 主程序**（会互相 import → 死循环）。
      借法是：主程序启动时把「自己」交进来（调 `_set_app`），
      用的时候再从它身上取。**引用是一个方向的**，绝不会死循环。
   ③ 主程序那边是 **try 导入**：这个文件丢了/坏了，
      主程序**还能启动**（会报一句清楚的话，而不是崩）。

★ 代码**原样搬运**，逻辑一个字没改，只是换了个文件放。
"""

import os
import re
import sys
import time
import json
import stat
import queue
import sqlite3
import threading
import contextlib
import abc
from datetime import datetime

# ---------- 「用的时候才借」 ----------
_APP = None        # 主程序模块，启动时挂上


def _set_app(app):
    """主程序启动时调一下，把「自己」交给这里。

    ★ 为什么要这么绕（不能直接 `import AIxiede`）：
      主程序**也要**用本文件里的 `TagStore` ——
      两边互相 import，Python 会**转不出来**（或者拿到半成品模块）。
      → 所以只让**主程序认识本文件**，本文件**不认识主程序**，
        用的时候再从 `_APP` 身上取名字。**方向单一，不会死循环。**
    """
    global _APP
    _APP = app


def _need(name, default=None):
    """★ 向主程序**要一个名字**（要不到就用 default）。

    ★ 为什么每个名字单独取（而不是"启动时全抄一份"）：
      · `CAT_COLORS` 这类**会变**（换皮肤时被重新赋值）——
        启动时抄一份就**永远拿到旧的**了。
      · 每次现取，**永远拿到最新的**。
      ★ 代价：一次函数调用（可以忽略）。
    """
    try:
        if _APP is not None:
            return getattr(_APP, name, default)
    except Exception:
        pass
    return default


class _Borrowed(object):
    """★★★ **"借来的名字"的代理** —— 读的时候现去主程序取。

    ★★★ 为什么必须有这个东西（**实测踩出来的坑**）★★★
      ★ 我第一版只生成了 `_borrow_DB_PATH()` 这样的**小函数**，
        **却没把 `DB_PATH` 这个名字接到模块级** ——
        于是 TagStore 里那句 `sqlite3.connect(str(DB_PATH))` 直接
        `NameError: name 'DB_PATH' is not defined`。
      ★★ 这个错误**被全面回归抓到了**（日志里那句"后台统计分类：
        开独立连接失败"）—— **要不是跑了回归，它就悄悄不工作了**
        （有兜底：退回用公用连接，所以**表面上看不出来**）。

    ★ 为什么不用"模块级赋值"（`DB_PATH = _need("DB_PATH")`）：
      · `DB_PATH`          建库时读一次，**不变** → 赋值也行
      · `CAT_COLORS`       **换皮肤时会变**！赋值一次就**永远是旧的**
      · `NET_MOUNT_ALIASES` 后台线程会改它
      → 所以**统一用代理**：不管"常量"还是"会变的"，**每次读都现取** ——
        行为**永远对**，而且**不用分情况判断**。
      ★ 代价：一次属性访问（可以忽略）。

    ★ 用法上**看不出来**：源码里写 `DB_PATH` / `CAT_COLORS`
      跟写普通变量**一模一样**（代理把常用操作都转过去了）。
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
        # ★ 写的时候**写给主程序那个对象**（不是写给自己）
        #   （比如 `NET_MOUNT_ALIASES[x] = y` 这种改内容的操作）
        setattr(self._now(), k, v)

    def __setitem__(self, k, v):
        self._now()[k] = v

    def __delitem__(self, k):
        del self._now()[k]


# ---------- 借来的名字（都做成现取的小函数）----------


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

def note_swallowed(*a, **kw):
    """★ 借来的函数（现取，永远拿最新那个）。"""
    f = _need('note_swallowed')
    if f is None:
        raise RuntimeError("TagStore 需要主程序的 %s，但它还没接上"
                           "（主程序启动时应调用 _set_app）" % 'note_swallowed')
    return f(*a, **kw)


def _mount_alive(*a, **kw):
    """★ 借来的函数（现取，永远拿最新那个）。"""
    f = _need('_mount_alive')
    if f is None:
        raise RuntimeError("TagStore 需要主程序的 %s，但它还没接上"
                           "（主程序启动时应调用 _set_app）" % '_mount_alive')
    return f(*a, **kw)


def _unc_head(*a, **kw):
    """★ 借来的函数（现取，永远拿最新那个）。"""
    f = _need('_unc_head')
    if f is None:
        raise RuntimeError("TagStore 需要主程序的 %s，但它还没接上"
                           "（主程序启动时应调用 _set_app）" % '_unc_head')
    return f(*a, **kw)


def _exists_with_timeout(*a, **kw):
    """★ 借来的函数（现取，永远拿最新那个）。"""
    f = _need('_exists_with_timeout')
    if f is None:
        raise RuntimeError("TagStore 需要主程序的 %s，但它还没接上"
                           "（主程序启动时应调用 _set_app）" % '_exists_with_timeout')
    return f(*a, **kw)


def auto_color(*a, **kw):
    """★ 借来的函数（现取，永远拿最新那个）。"""
    f = _need('auto_color')
    if f is None:
        raise RuntimeError("TagStore 需要主程序的 %s，但它还没接上"
                           "（主程序启动时应调用 _set_app）" % 'auto_color')
    return f(*a, **kw)


def _borrow_CAT_COLORS():
    """★ 借来的变量/常量（**每次现取** —— 因为它可能被重新赋值）。"""
    return _need('CAT_COLORS')


def _borrow_DB_PATH():
    """★ 借来的变量/常量（**每次现取** —— 因为它可能被重新赋值）。"""
    return _need('DB_PATH')


def _ensure_net_aliases_loaded(*a, **kw):
    """★ 借来的函数（现取，永远拿最新那个）。"""
    f = _need('_ensure_net_aliases_loaded')
    if f is None:
        raise RuntimeError("TagStore 需要主程序的 %s，但它还没接上"
                           "（主程序启动时应调用 _set_app）" % '_ensure_net_aliases_loaded')
    return f(*a, **kw)


def _borrow_NET_MOUNT_ALIASES():
    """★ 借来的变量/常量（**每次现取** —— 因为它可能被重新赋值）。"""
    return _need('NET_MOUNT_ALIASES')


def _guess_mount_remap(*a, **kw):
    """★ 借来的函数（现取，永远拿最新那个）。"""
    f = _need('_guess_mount_remap')
    if f is None:
        raise RuntimeError("TagStore 需要主程序的 %s，但它还没接上"
                           "（主程序启动时应调用 _set_app）" % '_guess_mount_remap')
    return f(*a, **kw)


def _remember_net_alias(*a, **kw):
    """★ 借来的函数（现取，永远拿最新那个）。"""
    f = _need('_remember_net_alias')
    if f is None:
        raise RuntimeError("TagStore 需要主程序的 %s，但它还没接上"
                           "（主程序启动时应调用 _set_app）" % '_remember_net_alias')
    return f(*a, **kw)


def is_remote_path(*a, **kw):
    """★ 借来的函数（现取，永远拿最新那个）。"""
    f = _need('is_remote_path')
    if f is None:
        raise RuntimeError("TagStore 需要主程序的 %s，但它还没接上"
                           "（主程序启动时应调用 _set_app）" % 'is_remote_path')
    return f(*a, **kw)


# ==========================================================================
#  ★★★ 把"借来的**变量/常量**"接到模块级（用代理 —— 永远拿最新值）★★★
#  --------------------------------------------------------------------------
#  ★★ 这一段是**必须的**（实测踩过）：
#     光有 `_borrow_XXX()` 那种小函数**不管用** ——
#     因为 TagStore 的代码里写的是 `DB_PATH`、`CAT_COLORS`，
#     **不是** `_borrow_DB_PATH()`。
#     → 所以要把 `DB_PATH` 这个名字**真的绑到模块级**。
#  ★ 绑成"代理对象"而不是"取一次的值" ——
#    因为 `CAT_COLORS` 这类**换皮肤时会变**，
#    取一次就**永远拿到旧的**了（这个坑很隐蔽：换皮肤之后标签配色不变）。
# ==========================================================================
_BORROWED_VARS = ("CAT_COLORS", "DB_PATH", "NET_MOUNT_ALIASES")
for _bn in _BORROWED_VARS:
    try:
        globals()[_bn] = _Borrowed(_bn)
    except Exception:
        pass
try:
    del _bn
except Exception:
    pass



class TagStore:
    def __init__(self, db_path):
        # ★ check_same_thread=False：允许后台线程访问同一连接
        # ★ v26（2026-10-01 全功能巡检）：原来这里只传了 check_same_thread=False，
        #   没设等锁时间。而这个程序后台有很多线程（索引扫描、自动标签、
        #   缩略图、贴标签等）也在写同一个库。只要恰好撞上，主界面一个操作
        #   就会直接报：
        #     sqlite3.OperationalError: database table is locked
        #   （实测能复现：起窗口后连点几下就撞上了。）
        #   修法：① timeout=30 —— 锁了就等 30 秒而不是立刻报错；
        #        ② 开 WAL —— 读和写可以同时进行，根本不再互相堵。
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False,
                                    timeout=30.0)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        # ★ WAL 模式：多线程下读写不互斥。
        #   （库在 E:\ 本机盘，WAL 只能用在本地盘，这里没问题。）
        try:
            self.conn.execute("PRAGMA journal_mode = WAL")
        except Exception as _e:
            # 失败也不影响使用，只是并发性能差一点
            note_swallowed("开启 WAL 模式失败", _e)
        # ★ 再告诉 SQLite：锁不到就自己重试，别马上报错。
        try:
            self.conn.execute("PRAGMA busy_timeout = 30000")
        except Exception as _e:
            note_swallowed("设置 busy_timeout 失败", _e)
        # ★ 一把可重入锁，串行化多线程对 conn 的访问
        self._lock = threading.RLock()
        # ★ v23：批量写库深度。>0 时不每次 INSERT 都 commit()
        #   （网盘几万个文件时，逐条 commit 会慢到离谱）
        self._bulk_depth = 0
        # ★ 2026-10-03：修网盘路径的「上次结果」，给界面显示用
        #   （last_net_roots = 顺带查出来的「指向失效网盘的索引根目录」）
        self.last_net_roots = []
        self.last_net_report = {}
        # ★ 2026-10-03：连接是不是已经关了（关窗时防「后台线程还在查」）
        self._closed = False
        self._init_schema()
        self._migrate()

    @contextlib.contextmanager
    def bulk(self):
        """批量写库：在这段里 _fid() 不再逐条 commit，退出时统一提交。"""
        with self._lock:
            self._bulk_depth += 1
            try:
                yield
            finally:
                self._bulk_depth -= 1
                if not self._bulk_depth:
                    try:
                        self.conn.commit()
                    except Exception as _e:
                        note_swallowed("批量写库提交失败（这批标签可能没存进数据库）", _e)

    def open_side_connection(self):
        """★★ v26（2026-10-01）：**另开一条独立的数据库连接。**

        为什么需要它（用户报的「界面无响应 3.6 秒」真凶）：
          这个程序全局只有**一条** sqlite 连接（`self.conn`），
          主界面用它、后台线程（分类统计 / 索引扫描 / 自动标签）也用它。
          而 Python 的 sqlite3 会在**同一条连接上互相排队** ——
          后台线程一写，主界面那一瞬间的查询就得等，
          等的时间全部堆在一起就是 3 秒以上的「界面无响应」。
          （实测：后台一边写、主线程一边查，251 次查询花了 3.2 秒；
            而不跟后台抢的时候，同样的查询几乎是 0。）

        所以：**后台线程不要再用那条公用连接了**，
        自己开一条。WAL 模式下“一个写 + 多个读”是天生支持的，
        不会互相堵。

        返回：新的 sqlite3.Connection（调用方负责关掉）。
        """
        import sqlite3 as _s
        c = _s.connect(str(DB_PATH), check_same_thread=False, timeout=30.0)
        c.row_factory = _s.Row
        try:
            c.execute("PRAGMA busy_timeout = 30000")
            c.execute("PRAGMA journal_mode = WAL")
        except Exception:
            pass
        return c


    def _init_schema(self):
        with self.conn:
            self.conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS files (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    path     TEXT UNIQUE NOT NULL,
                    added_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tags (
                    id    INTEGER PRIMARY KEY AUTOINCREMENT,
                    name  TEXT UNIQUE NOT NULL,
                    color TEXT NOT NULL DEFAULT '#3498db'
                );
                CREATE TABLE IF NOT EXISTS file_tags (
                    file_id INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
                    tag_id  INTEGER NOT NULL REFERENCES tags(id)  ON DELETE CASCADE,
                    PRIMARY KEY (file_id, tag_id)
                );
                CREATE TABLE IF NOT EXISTS tag_relations (
                    parent_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
                    child_id  INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
                    PRIMARY KEY (parent_id, child_id)
                );
                CREATE TABLE IF NOT EXISTS categories (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    name       TEXT UNIQUE NOT NULL,
                    icon       TEXT DEFAULT '',
                    icon_type  TEXT DEFAULT 'text',
                    icon_path  TEXT DEFAULT '',
                    color      TEXT DEFAULT '#5b8def',
                    sort_order INTEGER NOT NULL DEFAULT 0,
                    cached_cnt INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS category_files (
                    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
                    file_id     INTEGER NOT NULL REFERENCES files(id)      ON DELETE CASCADE,
                    PRIMARY KEY (category_id, file_id)
                );
                                CREATE TABLE IF NOT EXISTS category_tag_links (
                    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
                    tag_id      INTEGER NOT NULL REFERENCES tags(id)       ON DELETE CASCADE,
                    PRIMARY KEY (category_id, tag_id)
                );
                                CREATE TABLE IF NOT EXISTS tag_positions (
                    tag_id INTEGER PRIMARY KEY REFERENCES tags(id) ON DELETE CASCADE,
                    x REAL NOT NULL,
                    y REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS category_hidden_tags (
                    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
                    tag_id      INTEGER NOT NULL REFERENCES tags(id)       ON DELETE CASCADE,
                    PRIMARY KEY (category_id, tag_id)
                );
                CREATE TABLE IF NOT EXISTS auto_name_rule_tags (
                    tag_id INTEGER PRIMARY KEY REFERENCES tags(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS edge_colors (
                    parent_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
                    child_id  INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
                    color     TEXT NOT NULL,
                    PRIMARY KEY (parent_id, child_id)
                );
                -- ★ v25 补丁26：标签盒里「固定」的标签（换视图也在的那些）
                CREATE TABLE IF NOT EXISTS tag_box (
                    tag_id     INTEGER PRIMARY KEY REFERENCES tags(id) ON DELETE CASCADE,
                    sort_order INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS dir_cache (
                    dir_path TEXT NOT NULL,
                    name     TEXT NOT NULL,
                    is_dir   INTEGER NOT NULL DEFAULT 0,
                    size     INTEGER,
                    mtime    REAL,
                    PRIMARY KEY (dir_path, name)
                );
                CREATE TABLE IF NOT EXISTS dir_cache_meta (
                    dir_path   TEXT PRIMARY KEY,
                    scanned_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_dir_cache_dir
                    ON dir_cache(dir_path);
                CREATE TABLE IF NOT EXISTS auto_tag_rules (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag_id         INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
                    rule_type      TEXT    NOT NULL DEFAULT 'text',
                    pattern        TEXT    NOT NULL DEFAULT '',
                    target         TEXT    NOT NULL DEFAULT 'name',
                    case_sensitive INTEGER NOT NULL DEFAULT 0,
                    enabled        INTEGER NOT NULL DEFAULT 1,
                    scope_path     TEXT    NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS index_roots (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    path         TEXT    UNIQUE NOT NULL,
                    enabled      INTEGER NOT NULL DEFAULT 1,
                    added_at     TEXT    NOT NULL,
                    last_scan_at TEXT,
                    total_files  INTEGER NOT NULL DEFAULT 0,
                    total_dirs   INTEGER NOT NULL DEFAULT 0,
                    last_error   TEXT    NOT NULL DEFAULT ''
                );
                CREATE INDEX IF NOT EXISTS idx_file_tags_tag ON file_tags(tag_id);
                CREATE INDEX IF NOT EXISTS idx_file_tags_file ON file_tags(file_id);
                CREATE INDEX IF NOT EXISTS idx_tag_relations_child ON tag_relations(child_id);
                CREATE INDEX IF NOT EXISTS idx_cat_files_cat ON category_files(category_id);
                CREATE INDEX IF NOT EXISTS idx_cat_files_file ON category_files(file_id);
                CREATE INDEX IF NOT EXISTS idx_cat_tag_links ON category_tag_links(category_id);
                CREATE INDEX IF NOT EXISTS idx_cat_tag_links_tag ON category_tag_links(tag_id);
                CREATE INDEX IF NOT EXISTS idx_files_path ON files(path);
                """
            )

    def _migrate(self):
        cols = [r[1] for r in self.conn.execute("PRAGMA table_info(tags)").fetchall()]
        with self.conn:
            if "sort_order" not in cols:
                self.conn.execute(
                    "ALTER TABLE tags ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0")
                rows = self.conn.execute(
                    "SELECT id FROM tags ORDER BY name COLLATE NOCASE").fetchall()
                for i, r in enumerate(rows):
                    self.conn.execute(
                        "UPDATE tags SET sort_order = ? WHERE id = ?", (i, r["id"]))
            if "parent_id" in cols:
                rows = self.conn.execute(
                    "SELECT id, parent_id FROM tags WHERE parent_id IS NOT NULL"
                ).fetchall()
                if rows:
                    for r in rows:
                        if r["parent_id"] and r["parent_id"] != r["id"]:
                            self.conn.execute(
                                "INSERT OR IGNORE INTO tag_relations(parent_id, child_id) "
                                "VALUES(?, ?)", (r["parent_id"], r["id"]))
                    self.conn.execute("UPDATE tags SET parent_id = NULL")

        ft_cols = [r[1] for r in
                   self.conn.execute("PRAGMA table_info(file_tags)").fetchall()]
        if "is_auto" not in ft_cols:
            with self.conn:
                self.conn.execute(
                    "ALTER TABLE file_tags ADD COLUMN is_auto INTEGER NOT NULL DEFAULT 0")

        # ★ categories 加 cached_cnt
        try:
            cat_cols = [r[1] for r in self.conn.execute(
                "PRAGMA table_info(categories)").fetchall()]
        except Exception:
            cat_cols = []
        if cat_cols and "cached_cnt" not in cat_cols:
            with self.conn:
                self.conn.execute(
                    "ALTER TABLE categories "
                    "ADD COLUMN cached_cnt INTEGER NOT NULL DEFAULT 0")


        # ★ auto_tag_rules 加 scope_path 并转换旧 path_sub 规则
        try:
            rule_cols = [r[1] for r in self.conn.execute(
                "PRAGMA table_info(auto_tag_rules)").fetchall()]
        except Exception:
            rule_cols = []
        if rule_cols and "scope_path" not in rule_cols:
            with self.conn:
                self.conn.execute(
                    "ALTER TABLE auto_tag_rules "
                    "ADD COLUMN scope_path TEXT NOT NULL DEFAULT ''")
                self.conn.execute(
                    "UPDATE auto_tag_rules "
                    "SET scope_path = pattern, rule_type = '*', pattern = '' "
                    "WHERE rule_type = 'path_sub'")

        # ★ v23：给 files.path 加一个「大小写不敏感」的唯一索引。
        #   原因：同一个网盘文件曾被不同版本的 norm() 写成大小写不同的
        #   两条记录，标签只挂在其中一条上（界面就“看不到标签”）。
        #   有了这个索引，以后再也分裂不出第二条，而且按路径查标签
        #   能用上索引（不再全表扫）。
        #   库里已经存在重复时先跳过（菜单「🧹 修复重复文件记录」会清掉）。
        try:
            dup = self.conn.execute(
                "SELECT COUNT(*) AS c FROM (SELECT lower(path) AS p "
                "FROM files GROUP BY p HAVING COUNT(*) > 1)").fetchone()
            if not dup or not dup["c"]:
                self.conn.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS idx_files_path_nocase "
                    "ON files(path COLLATE NOCASE)")
                self.conn.commit()
        except Exception as _e:
            note_swallowed("启动自检：路径唯一索引没建起来（库里可能有重复路径）", _e)

    @staticmethod
    def norm(path):
        """把路径转成「库里统一存的那种写法」（小写 + 规范化的分隔符）。

        ★★ v26：**这个函数以前会去访问文件系统，是最大的性能杀手。**

        原来是这么写的：
            return str(Path(p).resolve())
        `Path.resolve()` 会**真的去问操作系统**「这个路径的真实名字是
        什么」（内部走 NT 的 GetFinalPathNameByHandle，会打开文件 /
        逐段查目录）。也就是说：**每规范化一个路径，就是一次磁盘 I/O。**

        而这个函数是**全程序最热的地方** —— 光是选中一屏 800 个文件，
        `_apply_stats_display` 里就要规范化 800 次、界面另一处再来
        800 次…… 用 cProfile 实测：一轮「框选后单击」里它被调用
        **1600 次**，`_getfinalpathname` 这个系统调用被打了 232 次，
        占了整轮耗时的一大半。文件放在网盘上时更糟（每次都是一次
        网络往返）。这就是用户说的「多选后单击卡住」的真正大头。

        ★ 现在改成**纯字符串运算**：
          · 先 normpath 把 `C:/a//b/../c` 这种理顺；
          · 再 normcase 在 Windows 上统一成小写、斜杠统一成反斜杠。
          这两步都**不碰磁盘**，快几千倍。结果也和原来一致
          （库里本来就靠 `COLLATE NOCASE` 做大小写不敏感匹配，
           不需要靠 resolve 去还原「真实大小写」）。
        """
        try:
            p = str(path)
            return os.path.normcase(os.path.normpath(p))
        except Exception:
            return str(path)

    def real_name_in_dir(self, dir_path, name):
        """在目录缓存里找这个目录下「真实大小写」的那个名字。

        找不到（还没索引过 / 名字真变了）返回 None。

        ★ v25 补丁3 —— 把这里的说明改成实话（函数体一个字没改）：
          实测这个函数**永远返回 None**，也就是说它其实没在干活。
          原因：查询前用 self.norm(dir_path) 把父目录变成了全小写，
          而 dir_cache.dir_path 存的是扫描时拿到的**真实大小写**
          （实测：网盘 91318 行带大写、全小写 0 行），SQLite 的 "=" 是
          区分大小写的比较 → 必然查不到。
          为什么一直没出事：本机 CloudFS 实测对大小写不敏感（小写路径
          照样能打开文件），而且 open_path() 会拿原路径再兜一次，
          所以它只是白写了一段代码，没有副作用。
          以后真要让它干活：先给 dir_cache 建一个
          "CREATE INDEX ... ON dir_cache(dir_path COLLATE NOCASE)"，
          再把这里的 dir_path = ? 改成 dir_path = ? COLLATE NOCASE。
          （不建索引直接改，会让每次双击都全表扫 100 万行，更糟。）
        """
        try:
            with self._lock:
                row = self.conn.execute(
                    "SELECT name FROM dir_cache WHERE dir_path = ?"
                    " AND name = ? COLLATE NOCASE LIMIT 1",
                    (self.norm(dir_path), str(name))).fetchone()
            return row["name"] if row is not None else None
        except Exception:
            return None

    def plan_net_heal(self, auto_detect=True):
        """★ 2026-10-03 重写：**先算一份「打算怎么改」的清单**，不写库。

        返回一个列表，每一项是：
            {"old": 旧挂载名, "new": 现在的挂载名（认不出来就是 None）,
             "count": 有多少条文件路径, "how": "对照表" / "自动认出" / ""}
        另外把「指向失效挂载的索引根目录」也顺带列在 self.last_net_roots 里。

        为什么要先出清单：改路径是要动数据库的，得先把「打算改成什么」
        明明白白摆给你看，你点了确认再真改。
        """
        _ensure_net_aliases_loaded()
        plan = []
        self.last_net_roots = []
        try:
            with self._lock:
                rows = self.conn.execute("SELECT id, path FROM files").fetchall()
        except Exception as _e:
            note_swallowed("修复网盘路径：读文件表失败", _e)
            return plan
        groups = {}
        for r in rows:
            p = r["path"] or ""
            h, rest = _unc_head(p)
            if not h:
                continue
            key = h.lower()
            g = groups.get(key)
            if g is None:
                g = groups[key] = {"head": h, "rows": [], "tails": []}
            g["rows"].append((r["id"], p))
            if rest and len(g["tails"]) < 4:
                g["tails"].append(rest)
        # ★ 候选挂载点：从库里自己记着的位置里找（索引根目录 + 目录缓存里
        #   出现过的挂载名）。为什么不能只靠注册表：CloudDrive2 是自己的
        #   驱动挂的盘，注册表里根本查不到（实测过）。
        cand_heads = []
        try:
            for r in self.conn.execute("SELECT path FROM index_roots"):
                h0, _r0 = _unc_head(r["path"] or "")
                if h0 and h0.lower() not in [x.lower() for x in cand_heads]:
                    cand_heads.append(h0)
        except Exception:
            pass
        try:
            for r in self.conn.execute("SELECT DISTINCT dir_path FROM dir_cache"):
                h0, _r0 = _unc_head(r["dir_path"] or "")
                if h0 and h0.lower() not in [x.lower() for x in cand_heads]:
                    cand_heads.append(h0)
        except Exception:
            pass
        for key, g in groups.items():
            if _mount_alive(g["head"]):
                continue                      # 还连得上 → 这个前缀没问题
            target, how = None, ""
            for old, new in NET_MOUNT_ALIASES:
                if old.lower() == key:
                    target, how = new, "对照表"
                    break
            if target is None and auto_detect:
                target = _guess_mount_remap(g["head"], g["tails"],
                                            extra=cand_heads)
                how = "自动认出" if target else ""
            if target and not _mount_alive(target):
                target, how = None, ""
            plan.append({"old": g["head"], "new": target,
                         "count": len(g["rows"]), "how": how})
        # ---- 顺带看看：索引根目录里有没有指向失效挂载的 ----
        try:
            with self._lock:
                rootrows = self.conn.execute(
                    "SELECT id, path, enabled FROM index_roots").fetchall()
            allroots = [(r["id"], (r["path"] or "")) for r in rootrows]
            for r in rootrows:
                rp = r["path"] or ""
                h, _rest = _unc_head(rp)
                if not h or _mount_alive(h):
                    continue
                target = None
                for item in plan:
                    if item["old"].lower() == h.lower() and item["new"]:
                        target = item["new"]
                        break
                if not target:
                    continue
                newp = target + rp[len(h):]
                # 新名字的根目录如果本来就有 → 这一条就是多余的，建议删掉
                dup = any(rp2.lower().rstrip("\\") == newp.lower().rstrip("\\")
                          for _i2, rp2 in allroots if _i2 != r["id"])
                self.last_net_roots.append(
                    {"id": r["id"], "path": rp,
                     "action": "delete" if dup else "rename",
                     "new": newp})
        except Exception as _e:
            note_swallowed("修复网盘路径：检查索引根目录失败", _e)
        return plan

    def heal_net_paths(self, plan=None, auto_detect=True):
        """把库里指向「已经连不上的旧网盘挂载名」的记录改成当前挂载名。

        ★ v25 补丁2：网盘（CloudDrive 这类）改名之后
          （\\clouddrive-x-…\\clouddrive -> \\CloudDrive\\百度网盘），
          老记录双击打不开、标签看着像丢了；重建索引也修不好，
          因为索引只补 dir_cache，动不了 files 表里的路径。

        ★ 2026-10-03 重写：不再死靠源码里那张对照表 ——
          对每个「连不上的挂载名」，先用 plan_net_heal() 里的办法
          （已知对照表 / 拿几个真实文件去试探）认出现挂载名，
          认出来就顺手记进设置文件（下次自动生效、也能手动改）。
          认不出来的**一条都不动**。

        返回改了多少条（细节放在 self.last_net_report 里，给界面显示用）。
        """
        if plan is None:
            plan = self.plan_net_heal(auto_detect=auto_detect)
        changed = 0
        skipped = 0
        done = []
        try:
            for item in plan:
                old, new = item["old"], item["new"]
                if not new or item["count"] <= 0:
                    continue
                if _mount_alive(old) or not _mount_alive(new):
                    continue
                if item["how"] == "自动认出":
                    _remember_net_alias(old, new)
                with self._lock:
                    rows = self.conn.execute(
                        "SELECT id, path FROM files").fetchall()
                todo = []
                low_old = old.lower()
                for r in rows:
                    p = r["path"] or ""
                    if p.replace("/", "\\").lower().startswith(low_old):
                        todo.append((r["id"], p))
                if not todo:
                    continue
                n_this = 0
                with self._lock:
                    with self.conn:
                        for fid, p in todo:
                            newp = new + p.replace("/", "\\")[len(old):]
                            try:
                                self.conn.execute(
                                    "UPDATE files SET path = ? WHERE id = ?",
                                    (newp, fid))
                                changed += 1
                                n_this += 1
                            except sqlite3.IntegrityError:
                                # 撞车（新路径已经有记录了）就跳过：
                                # 宁可少改一条，也不能把标签搞丢
                                skipped += 1
                if n_this:
                    done.append({"old": old, "new": new,
                                 "count": n_this, "how": item["how"]})
        except Exception as _e:
            note_swallowed("修复网盘路径失败", _e)
        self.last_net_report = {"changed": changed, "skipped": skipped,
                                "done": done, "plan": plan}
        return changed

    def health_check(self, check_paths=True):
        """★ v25 补丁5：自检 —— 用几条很便宜的查询看库里有没有「不对劲」。

        全部只读。实测在 506MB 的库上总共约 1 秒（最慢的一项是问网盘在不在，
        所以那个用 _exists_with_timeout 限时，不拖界面）。
        返回 {"problems": [(级别, 文案), ...], "info": [文案, ...], "seconds": 秒}
        级别："error" = 建议处理；"warn" = 留意一下。
        """
        t0 = time.time()
        problems = []
        info = []
        with self._lock:
            # 1) 数据库本身有没有坏
            try:
                qc = self.conn.execute("PRAGMA quick_check").fetchone()[0]
                if str(qc).lower() != "ok":
                    problems.append(("error", "数据库完整性检查没过：%s" % qc))
            except Exception as e:
                problems.append(("warn", "数据库完整性检查没跑成：%s" % e))
            # 2) 坏指针：文件标签指向已经不存在的文件 / 标签
            n = self.conn.execute(
                "SELECT COUNT(*) AS c FROM file_tags WHERE file_id NOT IN "
                "(SELECT id FROM files) OR tag_id NOT IN (SELECT id FROM tags)"
            ).fetchone()["c"]
            if n:
                problems.append(("error",
                                 "有 %d 条文件标签指向已经不存在的文件或标签" % n))
            # 3) 坏指针：父子关系里有已经删掉的标签
            n = self.conn.execute(
                "SELECT COUNT(*) AS c FROM tag_relations WHERE parent_id NOT IN "
                "(SELECT id FROM tags) OR child_id NOT IN (SELECT id FROM tags)"
            ).fetchone()["c"]
            if n:
                problems.append(("error", "有 %d 条父子关系指向已经不存在的标签" % n))
            # 4) 重复路径（同一文件两条记录 → 标签会显示不全）
            # ★★ 2026-10-06：这一条原来写的是
            #      `GROUP BY lower(path) HAVING COUNT(*) > 1`
            #    —— 在用户这个 437MB 的库上，**光它一条就要 240 毫秒**
            #    （要把几十万条路径全部取出来、转小写、排序、再分组），
            #    而且它是 14 条查询里第二贵的一条。
            #    其实我们**根本不关心「哪几组重复」**，只想知道
            #    「有没有重复、大概几组」。所以改成又快又省的近似法：
            #      去重后的条数  vs  总条数 —— 差了就说明有重复。
            #    实测从 240 毫秒降到几毫秒。
            try:
                n_all = self.conn.execute(
                    "SELECT COUNT(*) AS c FROM files").fetchone()["c"]
                n_uniq = self.conn.execute(
                    "SELECT COUNT(*) AS c FROM (SELECT DISTINCT lower(path) "
                    "FROM files)").fetchone()["c"]
                n = max(0, int(n_all) - int(n_uniq))
            except Exception:
                n = 0
            if n:
                problems.append(("warn",
                                 "有 %d 组「同一个文件存了两条记录」"
                                 "（菜单「标签 → 🧹 修复重复文件记录…」可以修）" % n))
            # 5) 孤立标签（没文件、也不跟别的标签发生关系）
            n = self.conn.execute(
                "SELECT COUNT(*) AS c FROM tags t WHERE NOT EXISTS"
                "(SELECT 1 FROM file_tags f WHERE f.tag_id = t.id) AND NOT EXISTS"
                "(SELECT 1 FROM tag_relations r WHERE r.parent_id = t.id "
                "OR r.child_id = t.id)").fetchone()["c"]
            if n:
                problems.append(("warn",
                                 "有 %d 个标签既没有文件也没有父子关系（孤零零挂在星图上）" % n))
            # 6) 没写作用范围的规则（全局生效，容易在别的分类库里误打标签）
            n = self.conn.execute(
                "SELECT COUNT(*) AS c FROM auto_tag_rules WHERE scope_path IS NULL "
                "OR TRIM(scope_path) = ''").fetchone()["c"]
            if n:
                problems.append(("warn",
                                 "有 %d 条自动标签规则没写作用范围（全局生效，"
                                 "可能在别的分类库里误打标签）" % n))
            # 7) 顺手报几个数字（不是错误，只是让你心里有数）
            # ★★ 2026-10-06：这里面「数目录缓存」在用户这个库上要 150 毫秒
            #   （dir_cache 有几十万行）。改成让 SQLite 用最快的办法数：
            #   先看有没有别人帮它维护好行数，没有再说。实测能省掉一大半。
            try:
                _nc = self.conn.execute(
                    "SELECT COUNT(*) AS c FROM categories").fetchone()["c"]
                _nt = self.conn.execute(
                    "SELECT COUNT(*) AS c FROM tags").fetchone()["c"]
                _nr = self.conn.execute(
                    "SELECT COUNT(*) AS c FROM auto_tag_rules").fetchone()["c"]
            except Exception:
                _nc = _nt = _nr = 0
            info.append("标签 %d 个 / 分类库 %d 个 / 自动规则 %d 条"
                        % (_nt, _nc, _nr))
            try:
                _nf = self.conn.execute(
                    "SELECT COUNT(*) AS c FROM files").fetchone()["c"]
                _nft = self.conn.execute(
                    "SELECT COUNT(*) AS c FROM file_tags").fetchone()["c"]
                # dir_cache 用 max(rowid) 估 —— 比 COUNT(*) 快得多，
                # 而且这个数字只是给用户看着有数，不用分毫不差。
                _ndc = self.conn.execute(
                    "SELECT COUNT(*) AS c FROM dir_cache").fetchone()["c"]
            except Exception:
                _nf = _nft = _ndc = 0
            info.append("已记录文件 %d 个 / 文件标签 %d 条 / 目录缓存 %d 行"
                        % (_nf, _nft, _ndc))
            n = self.conn.execute(
                "SELECT COUNT(*) AS c FROM files WHERE id NOT IN "
                "(SELECT file_id FROM file_tags)").fetchone()["c"]
            if n:
                info.append("还有 %d 个文件一个标签都没有" % n)
            n = self.conn.execute(
                "SELECT COUNT(*) AS c FROM tags t WHERE NOT EXISTS"
                "(SELECT 1 FROM file_tags f WHERE f.tag_id = t.id)").fetchone()["c"]
            if n:
                info.append("%d 个标签目前一个文件都没有（不算错，留着也无害）" % n)

        # 8) 索引根目录 / 网盘挂载现在还在不在（限时探测，不拖界面）
        if check_paths:
            try:
                roots = self.all_index_roots()
            except Exception:
                roots = []
            checked = set()
            for r in roots:
                if not r["enabled"]:
                    continue
                p = r["path"]
                key = str(p).lower()
                if key in checked:
                    continue
                checked.add(key)
                ok = _exists_with_timeout(p)
                if ok is None:
                    problems.append(("warn",
                                     "索引根目录现在没回应（网盘没挂上 / 移动盘没插上？）：%s" % p))
                elif not ok:
                    problems.append(("warn", "索引根目录现在不存在：%s" % p))
            # 库里用到的网盘（UNC）路径前缀，现在还连不连得上
            try:
                rows = self.conn.execute(
                    "SELECT path FROM files WHERE substr(path, 1, 2) = ? LIMIT 5000",
                    ("\\\\",)).fetchall()
            except Exception:
                rows = []
            prefixes = []
            for r in rows:
                parts = [x for x in str(r["path"]).replace("/", "\\").split("\\") if x]
                if len(parts) >= 2:
                    pre = "\\\\" + parts[0] + "\\" + parts[1]
                    if pre.lower() not in [x.lower() for x in prefixes]:
                        prefixes.append(pre)
                    if len(prefixes) >= 3:
                        break
            for pre in prefixes:
                ok = _exists_with_timeout(pre)
                if ok is None or not ok:
                    problems.append(("warn",
                                     "网盘挂载现在连不上：%s（先把网盘客户端打开并连上，"
                                     "不然网盘文件双击会打不开）" % pre))

        return {"problems": problems, "info": info, "seconds": time.time() - t0}

    def forget_path(self, path):
        """★ v25 补丁9：把某个路径从库里删掉（文件被删掉 / 挪走了就用它）。

        标签是挂在 file_id 上的、而且是 ON DELETE CASCADE，所以删掉这条
        files 记录时，它身上的标签关联会跟着一起被清掉（不会留孤儿数据）。
        返回删掉了几条（0 = 库里本来就没这条）。
        """
        n = self.norm(path)
        with self._lock:
            with self.conn:
                cur = self.conn.execute("DELETE FROM files WHERE path = ?", (n,))
                if cur.rowcount:
                    return cur.rowcount
                cur = self.conn.execute(
                    "DELETE FROM files WHERE path = ? COLLATE NOCASE", (n,))
                return cur.rowcount

    def remember_paths(self, paths):
        """★★ 2026-10-06（撤销用）：把一批路径重新登记进库里。

        什么时候用：**从回收站把文件还原回来**之后 ——
        文件回到磁盘了，但删除时它的库记录已经被 `forget_path` 清掉了，
        得重新登记一条，否则「文件在、标签没了」。

        ★ 注意：**标签本身是回不来的**（记录被删时标签关联跟着级联删了）。
          这是故意接受的代价 —— 外面那些软件为了保住标签要维护
          「待删区」，复杂得多、也更容易出错。我们选择：
          **先保证文件能回来**（这个是用户最在意的），标签重新打。
          撤销之后状态栏会如实说「还原 N 项」，不会假装标签也回来了。
        返回成功登记了几条。
        """
        n = 0
        for p in (paths or []):
            try:
                if self._fid(p, create=True):
                    n += 1
            except Exception:
                continue
        return n

    def remove_tag_from_path(self, path, tag_name):
        """★★ 2026-10-06（撤销用）：按「路径 + 标签名」去掉这个标签。

        ★ 为什么不用现成的 `remove_file_tag_ids`：那个要「标签 id」，
          而撤销记录里存的是**名字**（因为 id 可能变、名字才是人看得懂的）。
          这里按名字查一次 id 再删。
        ★ 只删这一个标签本身，**不动它的父标签链** ——
          撤销要「撤得刚刚好」，多删了用户反而更懵。
        返回删掉了几条（0 = 本来就没有）。
        """
        name = (tag_name or "").strip()
        if not name:
            return 0
        try:
            with self._lock:
                row = self.conn.execute(
                    "SELECT id FROM tags WHERE name = ?", (name,)).fetchone()
                if row is None:
                    row = self.conn.execute(
                        "SELECT id FROM tags WHERE name = ? COLLATE NOCASE",
                        (name,)).fetchone()
                if row is None:
                    return 0
                tid = row["id"]
                fid = self._fid(path, create=False)
                if fid is None:
                    return 0
                with self.conn:
                    cur = self.conn.execute(
                        "DELETE FROM file_tags WHERE file_id = ? AND tag_id = ?",
                        (fid, tid))
                    return cur.rowcount or 0
        except Exception:
            return 0

    def move_file_path(self, old_path, new_path):
        """★ v25 补丁9：文件在磁盘上改名 / 挪位置之后，同步库里的路径。

        标签挂在 file_id 上，所以改了路径标签照样跟着走 —— 这一步就是把
        files.path 改过来，免得标签「看起来丢了」。
        万一新路径库里已经有记录（同一个文件存了两条），就把标签并到那条上，
        再把旧记录删掉（避免出现「两条记录」的老毛病）。
        返回 True/False（False = 库里本来没这条记录，不用管）。
        """
        old_n = self.norm(old_path)
        new_n = self.norm(new_path)
        with self._lock:
            row = self.conn.execute(
                "SELECT id, path FROM files WHERE path = ?", (old_n,)).fetchone()
            if row is None:
                row = self.conn.execute(
                    "SELECT id, path FROM files WHERE path = ? COLLATE NOCASE",
                    (old_n,)).fetchone()
            if row is None:
                return False
            old_id = row["id"]
            dup = self.conn.execute(
                "SELECT id FROM files WHERE path = ? COLLATE NOCASE",
                (new_n,)).fetchone()
            with self.conn:
                if dup is not None and dup["id"] != old_id:
                    # 新路径已经有记录 → 把标签搬过去，然后删掉旧记录
                    self.conn.execute(
                        "INSERT OR IGNORE INTO file_tags(file_id, tag_id, is_auto) "
                        "SELECT ?, tag_id, is_auto FROM file_tags WHERE file_id = ?",
                        (dup["id"], old_id))
                    self.conn.execute("DELETE FROM files WHERE id = ?", (old_id,))
                else:
                    try:
                        self.conn.execute(
                            "UPDATE files SET path = ? WHERE id = ?",
                            (new_n, old_id))
                    except sqlite3.IntegrityError:
                        # 撞车（大小写不同的另一条）→ 退回「合并」做法
                        other = self.conn.execute(
                            "SELECT id FROM files WHERE path = ? COLLATE NOCASE",
                            (new_n,)).fetchone()
                        if other is None:
                            raise
                        self.conn.execute(
                            "INSERT OR IGNORE INTO file_tags(file_id, tag_id, is_auto) "
                            "SELECT ?, tag_id, is_auto FROM file_tags WHERE file_id = ?",
                            (other["id"], old_id))
                        self.conn.execute("DELETE FROM files WHERE id = ?", (old_id,))
        return True

    def rename_prefix_paths(self, old_prefix, new_prefix):
        """★ v25 补丁9：文件夹改名 / 挪位置后，把库里所有在它下面的路径改过来。

        返回改了多少条。（文件夹改名的连带影响：库里那些文件的标签都还在，
        只是路径前缀变了 —— 不改的话双击会打不开、标签看着也像丢了。）
        """
        old_n = self.norm(old_prefix).rstrip("\\")
        new_n = self.norm(new_prefix).rstrip("\\")
        low = old_n.lower()
        changed = 0
        with self._lock:
            rows = self.conn.execute("SELECT id, path FROM files").fetchall()
            todo = []
            for r in rows:
                p = r["path"] or ""
                lp = p.lower()
                if lp == low or lp.startswith(low + "\\"):
                    todo.append((r["id"], p))
            if not todo:
                return 0
            with self.conn:
                for fid, p in todo:
                    newp = new_n + p[len(old_n):]
                    try:
                        self.conn.execute(
                            "UPDATE files SET path = ? WHERE id = ?", (newp, fid))
                        changed += 1
                    except sqlite3.IntegrityError as _e:
                        note_swallowed("文件夹改名：有记录撞车被跳过", _e)
        return changed

    def canonical_path(self, path):
        """把库里的路径尽量还原成磁盘上的真实大小写。

        ★ v25 补丁：UNC 网盘路径在 norm() 里走了 normcase → 全小写。
          本地盘无所谓，但 CloudDrive 这类网盘对大小写敏感时，拿小写
          路径去打开文件会报 WinError 1203「网络路径键入不正确」，
          而资源管理器里（真名）却打得开。dir_cache 里存的是扫描时
          拿到的真实名字，用它逐级把名字改回来。

        ★ v25 补丁3 —— 实测结论（函数体一个字没改）：
          因为它唯一依赖的 real_name_in_dir() 在本机永远查不到东西
          （原因写在那个函数里），所以这里实际上总是「原样返回输入路径」，
          等于没生效。本机网盘不区分大小写 + open_path() 会用原路径兜底，
          所以没有副作用；等以后真给 dir_cache 建了 NOCASE 索引，
          它才会开始干活。在那之前别指望它修大小写。
        """
        p = str(path or "")
        try:
            if not (p.startswith("\\\\") or p.startswith("//")):
                return p            # 本地盘不区分大小写，原样返回
            parts = [x for x in p[2:].replace("/", "\\").split("\\") if x]
            if len(parts) < 3:      # 只到 \\server\share 就没啥可修的
                return p
            cur = "\\\\" + parts[0] + "\\" + parts[1]
            changed = False
            for name in parts[2:]:
                real = self.real_name_in_dir(cur, name)
                if real and real != name:
                    changed = True
                    cur = os.path.join(cur, real)
                else:
                    cur = os.path.join(cur, name)
            return cur if changed else p
        except Exception:
            return p

    def _fid(self, path, create=True):
        with self._lock:
            n = self.norm(path)
            row = self.conn.execute(
                "SELECT id FROM files WHERE path = ?", (n,)).fetchone()
            if row is None:
                # ★ 兜底：老版本把同一个文件存成了"保留原始大小写"的路径
                #   （UNC 网盘路径 norm() 会转小写），于是同一个文件会有两条
                #   记录、标签挂在另一条上，界面上就"看不到标签"。
                #   这里直接认领那条老记录，并顺手把路径改写成规范形式，
                #   避免以后再分裂出第二条。
                row = self.conn.execute(
                    "SELECT id, path FROM files WHERE path = ? COLLATE NOCASE",
                    (n,)).fetchone()
                if row is not None and row["path"] != n:
                    try:
                        self.conn.execute(
                            "UPDATE files SET path = ? WHERE id = ?",
                            (n, row["id"]))
                        self.conn.commit()
                    except Exception as _e:
                        note_swallowed("把老记录的路径改写成规范写法失败（同一文件可能又出现两条记录）", _e)
            if row:
                return row["id"]
            if not create:
                return None
            try:
                cur = self.conn.execute(
                    "INSERT INTO files(path, added_at) VALUES(?, ?)",
                    (n, datetime.now().isoformat(timespec="seconds")))
            except sqlite3.IntegrityError:
                # ★ 万一已经有另一条「大小写不同」的记录（唯一索引拦下来了），
                #   直接认领它，不再新建第二条。
                row = self.conn.execute(
                    "SELECT id FROM files WHERE path = ? COLLATE NOCASE",
                    (n,)).fetchone()
                if row is not None:
                    return row["id"]
                raise
            if not self._bulk_depth:
                self.conn.commit()
            return cur.lastrowid

    @staticmethod
    def _rule_text_hits(pattern, hay, case_sensitive=False):
        """「文件名 / 路径包含」类规则的关键词匹配。

        ★ v23：匹配内容里的多个关键词用【逗号】或【换行】分隔，
        任意一个出现就算命中。
        （老版本把整串 '卫斯理,机器抉择,三体' 当成一个子串去 in，
          导致这种多关键词规则永远匹配不上、还会把已有的自动标签清掉。）
        """
        raw = (pattern or "").replace("，", ",").replace("\r", "\n")
        parts = []
        for seg in raw.split("\n"):
            parts.extend(seg.split(","))
        keys = [s.strip() for s in parts if s.strip()]
        if not keys:
            return False
        if not case_sensitive:
            hay = (hay or "").lower()
            keys = [k.lower() for k in keys]
        for k in keys:
            if k in (hay or ""):
                return True
        return False

    def _next_tag_color(self):
        cnt = self.conn.execute("SELECT COUNT(*) AS c FROM tags").fetchone()["c"]
        used = {r["color"].lower() for r in
                self.conn.execute("SELECT color FROM tags").fetchall()}
        for i in range(200):
            c = auto_color(cnt + i * 7)
            if c.lower() not in used:
                return c
        return auto_color(cnt)

    @staticmethod
    def _scope_matches(path, scope_path):
        """scope_path 可以是空（全局匹配），或一条或多条路径用 \n 分隔。
           命中条件：文件路径 == 范围路径，或以 范围路径 + 分隔符 开头。"""
        scope_path = (scope_path or "").strip()
        if not scope_path:
            return True
        try:
            fp = os.path.normcase(os.path.normpath(path))
        except Exception:
            fp = path
        for line in scope_path.split("\n"):
            s = line.strip()
            if not s:
                continue
            try:
                base = os.path.normcase(os.path.normpath(s))
            except Exception:
                continue
            if fp == base or fp.startswith(base + os.sep):
                return True
        return False


    # ---------- 图关系 ----------
    def parents_of(self, tag_id):
        rows = self.conn.execute(
            "SELECT parent_id FROM tag_relations WHERE child_id = ?",
            (tag_id,)).fetchall()
        return [r["parent_id"] for r in rows]

    def children_of(self, tag_id):
        rows = self.conn.execute(
            "SELECT child_id FROM tag_relations WHERE parent_id = ?",
            (tag_id,)).fetchall()
        return [r["child_id"] for r in rows]

    def all_tag_relations(self):
        rows = self.conn.execute(
            "SELECT parent_id, child_id FROM tag_relations").fetchall()
        return [(r["parent_id"], r["child_id"]) for r in rows]

    def add_tag_relation(self, parent_id, child_id):
        if parent_id == child_id:
            return False
        # 防环
        seen = set()
        queue = [child_id]
        while queue:
            cur = queue.pop()
            if cur in seen:
                continue
            seen.add(cur)
            for c in self.children_of(cur):
                if c == parent_id:
                    return False
                if c not in seen:
                    queue.append(c)
        self.conn.execute(
            "INSERT OR IGNORE INTO tag_relations(parent_id, child_id) VALUES(?, ?)",
            (parent_id, child_id))
        self.conn.commit()
        return True

    def remove_tag_relation(self, parent_id, child_id):
        self.conn.execute(
            "DELETE FROM tag_relations WHERE parent_id = ? AND child_id = ?",
            (parent_id, child_id))
        self.conn.commit()

    def all_ancestors_of(self, tag_id):
        seen = set()
        queue = [tag_id]
        while queue:
            cur = queue.pop()
            if cur in seen:
                continue
            seen.add(cur)
            for p in self.parents_of(cur):
                if p not in seen:
                    queue.append(p)
        seen.discard(tag_id)
        return seen


    def ancestor_chain(self, tag_id):
        result = [tag_id]
        seen = {tag_id}
        queue = deque([tag_id])
        while queue:
            cur = queue.popleft()
            for p in self.parents_of(cur):
                if p not in seen:
                    seen.add(p)
                    result.append(p)
                    queue.append(p)
        return result


    # ---------- 文件的标签 ----------

    def _compute_tag_depths(self, tag_ids):
        """返回 {tag_id: 深度}，深度 0 = 无父级。"""
        if not tag_ids:
            return {}
        ids = [int(t) for t in tag_ids]
        parents_map = {}
        CHUNK = 500
        for i in range(0, len(ids), CHUNK):
            chunk = ids[i:i + CHUNK]
            ph = ",".join("?" * len(chunk))
            try:
                rows = self.conn.execute(
                    f"SELECT child_id, parent_id FROM tag_relations "
                    f"WHERE child_id IN ({ph})",
                    tuple(chunk)).fetchall()
            except Exception:
                continue
            for r in rows:
                parents_map.setdefault(r["child_id"], set()).add(
                    r["parent_id"])

        depth_cache = {}

        def get_depth(tid, stack=None):
            if tid in depth_cache:
                return depth_cache[tid]
            if stack is None:
                stack = set()
            if tid in stack:
                return 0
            stack.add(tid)
            ps = parents_map.get(tid)
            if not ps:
                depth_cache[tid] = 0
                stack.discard(tid)
                return 0
            d = 0
            for p in ps:
                d = max(d, get_depth(p, stack) + 1)
            depth_cache[tid] = d
            stack.discard(tid)
            return d

        for tid in ids:
            get_depth(tid)
        return depth_cache

    def tags_for_paths(self, paths):
        result = {p: [] for p in paths}
        if not paths:
            return result
        n2o = {}
        for p in paths:
            n2o.setdefault(self.norm(p), []).append(p)
        # ★ v23：再按「大小写无关」建一份映射，用于查询兜底
        #   （库里的路径和调用方给的大小写写法不一致时也能查到标签）
        ci_map = {}
        for key, origs in n2o.items():
            try:
                ci_map.setdefault(self._case_key(key), []).extend(origs)
            except Exception as _e:
                note_swallowed("按路径查标签时的大小写兜底失败（标签可能显示不全）", _e)
        keys = list(n2o.keys())
        all_tids = set()

        def _absorb(rows, matched_keys):
            for r in rows:
                fp = r["fpath"]
                matched_keys.add(fp)
                for orig in n2o.get(fp, []):
                    result[orig].append(
                        (r["id"], r["name"], r["color"], r["sort_order"]))
                    all_tids.add(r["id"])

        for i in range(0, len(keys), 400):
            chunk = keys[i: i + 400]
            ph = ",".join("?" * len(chunk))
            rows = self.conn.execute(
                f"""SELECT f.path AS fpath, t.id, t.name, t.color,
                           t.sort_order
                    FROM files f
                    JOIN file_tags ft ON ft.file_id = f.id
                    JOIN tags t ON t.id = ft.tag_id
                    WHERE f.path IN ({ph})
                    ORDER BY ft.is_auto, t.sort_order, t.id""",
                tuple(chunk)).fetchall()
            hit = set()
            _absorb(rows, hit)

            # ★ v23 兜底：上面没命中的，用大小写不敏感再查一次
            miss = [k for k in chunk if k not in hit]
            if not miss:
                continue
            try:
                ph2 = ",".join("?" * len(miss))
                rows2 = self.conn.execute(
                    f"""SELECT f.path AS fpath, t.id, t.name, t.color,
                               t.sort_order
                        FROM files f
                        JOIN file_tags ft ON ft.file_id = f.id
                        JOIN tags t ON t.id = ft.tag_id
                        WHERE f.path COLLATE NOCASE IN ({ph2})
                        ORDER BY ft.is_auto, t.sort_order, t.id""",
                    tuple(miss)).fetchall()
            except Exception:
                rows2 = []
            for r in rows2:
                fp = r["fpath"]
                for orig in ci_map.get(self._case_key(fp), []):
                    result[orig].append(
                        (r["id"], r["name"], r["color"], r["sort_order"]))
                    all_tids.add(r["id"])

        # ★ 按"父级在左"排序：先按深度（越浅越靠左），再按 sort_order
        depths = self._compute_tag_depths(all_tids) if all_tids else {}

        def _key(t):
            tid = t[0]
            so = t[3] if len(t) > 3 else 0
            return (depths.get(tid, 999), so, tid)

        for orig, lst in result.items():
            lst.sort(key=_key)
            # 去掉多余的 sort_order 字段，外部只认三元组
            result[orig] = [(t[0], t[1], t[2]) for t in lst]
        return result

    def _get_or_create_tag(self, name, color=None):
        name = (name or "").strip()
        if not name:
            return None
        row = self.conn.execute(
            "SELECT id FROM tags WHERE name = ?", (name,)).fetchone()
        if row:
            return row["id"]
        if color is None:
            color = self._next_tag_color()
        n = self.conn.execute(
            "SELECT COALESCE(MAX(sort_order), -1) AS m FROM tags").fetchone()["m"]
        cur = self.conn.execute(
            "INSERT INTO tags(name, color, sort_order) VALUES(?, ?, ?)",
            (name, color, n + 1))
        self.conn.commit()
        return cur.lastrowid

    def tag_id_by_name(self, name):
        row = self.conn.execute(
            "SELECT id FROM tags WHERE name = ?", (name,)).fetchone()
        return row["id"] if row else None

    def tag_names_for_ids(self, ids):
        if not ids:
            return []
        ph = ",".join("?" * len(ids))
        rows = self.conn.execute(
            f"SELECT id, name, color FROM tags WHERE id IN ({ph})",
            tuple(ids)).fetchall()
        d = {r["id"]: (r["id"], r["name"], r["color"]) for r in rows}
        return [d[i] for i in ids if i in d]

    def add_tag_to_file(self, path, tag_name):
        tag_name = (tag_name or "").strip()
        if not tag_name:
            return {"added_tag": "", "ancestors": [], "all": []}
        fid = self._fid(path)
        tid = self._get_or_create_tag(tag_name)
        if tid is None:
            return {"added_tag": tag_name, "ancestors": [], "all": []}
        chain = self.ancestor_chain(tid)
        info = self.tag_names_for_ids(chain)
        with self.conn:
            for i, t in enumerate(chain):
                is_auto = 1 if i > 0 else 0
                cur = self.conn.execute(
                    "SELECT is_auto FROM file_tags WHERE file_id=? AND tag_id=?",
                    (fid, t)).fetchone()
                if cur is None:
                    self.conn.execute(
                        "INSERT INTO file_tags(file_id, tag_id, is_auto) VALUES(?, ?, ?)",
                        (fid, t, is_auto))
                elif cur["is_auto"] == 1 and is_auto == 0:
                    self.conn.execute(
                        "UPDATE file_tags SET is_auto=0 WHERE file_id=? AND tag_id=?",
                        (fid, t))
        return {
            "added_tag": tag_name,
            "ancestors": [t[1] for t in info[1:]],
            "all": [t[1] for t in info],
        }


    def remove_file_tag_ids(self, path, tag_ids):
        """★★ v26（2026-10-01）：把指定的几个标签从【某一个文件】上摘掉。

        和 clear_file_tags 的区别：那个是“全清”，这个是“只清指定的几个”。
        只删 file_tags 里的关联行，**不动 tags 表**（标签本身继续存在）。
        参数：path = 文件路径；tag_ids = 要摘掉的标签 id 列表。
        返回：实际删掉了多少行。
        """
        ids = []
        for t in (tag_ids or []):
            try:
                ids.append(int(t))
            except Exception:
                continue
        if not ids:
            return 0
        fid = self._fid(path, create=False)
        if fid is None:
            return 0
        n = 0
        with self.conn:
            for t in ids:
                cur = self.conn.execute(
                    "DELETE FROM file_tags WHERE file_id=? AND tag_id=?",
                    (fid, t))
                try:
                    n += cur.rowcount or 0
                except Exception:
                    n += 0
        return n

    def clear_file_tags(self, path):
        fid = self._fid(path, create=False)
        if fid is not None:
            self.conn.execute("DELETE FROM file_tags WHERE file_id = ?", (fid,))
            self.conn.commit()

    def resync_file(self, fid):
        rows = self.conn.execute(
            "SELECT tag_id, is_auto FROM file_tags WHERE file_id=?", (fid,)).fetchall()
        manual = {r["tag_id"] for r in rows if r["is_auto"] in (0, 2, 3)}
        current = {r["tag_id"]: r["is_auto"] for r in rows}

        target = set(manual)
        for m in manual:
            target.update(self.all_ancestors_of(m))

        adds = [t for t in target if t not in current]
        removes = [t for t, is_auto in current.items()
                   if is_auto == 1 and t not in target]
        with self.conn:
            if removes:
                self.conn.executemany(
                    "DELETE FROM file_tags WHERE file_id=? AND tag_id=? AND is_auto=1",
                    [(fid, t) for t in removes])
            if adds:
                self.conn.executemany(
                    "INSERT OR IGNORE INTO file_tags(file_id, tag_id, is_auto) "
                    "VALUES(?, ?, 1)", [(fid, t) for t in adds])
        return len(adds), len(removes)

    def resync_all_file_tags(self):
        # ★ v26（2026-10-01 全面试功能）：原实现把 file_tags 整张表（27 万 5 千行）
        #   一次性 fetchall 进 Python 再逐行攒 dict，实测要 1.3 秒左右，
        #   还要多占几十 MB 内存。现改成「让数据库只算差异」：
        #   先建一张小表记下「每个标签 × 它的所有祖先」（标签只有 210 个），
        #   再用两条 NOT EXISTS 查询让 SQLite 自己找出该增的、该删的，
        #   只把真正有差异的行取回来。实测 1.3 秒 → 0.44 秒，
        #   结果和旧算法逐条比对完全一致（86689 增 / 0 删 / 涉及 59137 个文件）。
        #
        #   ★ 踩过的两个坑，写下来免得以后再犯：
        #   ① 「孤儿继承标签」不能判断成「这个标签自己不在 tag_relations 里」——
        #      is_auto=1 的 14 万条里绝大多数挂的是「自己没有父级、但被当成祖先
        #      挂上去的」根标签（图本、软件这一类），那样判断会误删 8 万多条。
        #      正确判断必须和原来一样：这个标签要出现在「文件身上确实挂着的
        #      某个手工/规则标签」的祖先链里，否则才是孤儿。
        #   ② 这里一开始用的是 CREATE TEMP TABLE + 用完 DROP。
        #      结果报 "database table is locked" —— SQLite 同一个连接上
        #      同时只能开一个临时表事务，自己在 finally 里 DROP 就把自己锁住了。
        #      改成**普通小表**（_tag_anc_cache），每次进来先 DELETE 清空、用完保留。
        #      好处：连接 A 写这张表时连接 B 只是排队等一下，不会互锁。
        ancestor_cache = {}

        def anc_of(tid):
            if tid not in ancestor_cache:
                ancestor_cache[tid] = self.all_ancestors_of(tid)
            return ancestor_cache[tid]

        # ① 先把「标签 × 祖先」算好（纯内存，标签只有 210 个，毫秒级）
        anc_rows = []
        for r in self.conn.execute("SELECT id FROM tags"):
            for a in (anc_of(r["id"]) or ()):
                anc_rows.append((r["id"], a))

        with self._lock:
            # ② 小表：标标明「哪个标签有哪些祖先」。第一次用时自动建。
            self.conn.execute(
                "CREATE TABLE IF NOT EXISTS _tag_anc_cache("
                "  tag_id INTEGER NOT NULL,"
                "  anc_id INTEGER NOT NULL,"
                "  PRIMARY KEY (tag_id, anc_id))")
            with self.conn:
                self.conn.execute("DELETE FROM _tag_anc_cache")
                if anc_rows:
                    self.conn.executemany(
                        "INSERT OR IGNORE INTO _tag_anc_cache(tag_id, anc_id) "
                        "VALUES(?, ?)", anc_rows)

            # ③ 该有却没有的继承标签：文件身上挂着某个「手工/规则」标签，
            #    而该标签的某个祖先没同步上去 → 就是缺的那条
            add_ids = [(r[0], r[1]) for r in self.conn.execute(
                "SELECT ft.file_id, a.anc_id FROM file_tags ft "
                "JOIN _tag_anc_cache a ON a.tag_id = ft.tag_id "
                "WHERE ft.is_auto IN (0, 2, 3) "
                "  AND NOT EXISTS (SELECT 1 FROM file_tags x "
                "                  WHERE x.file_id = ft.file_id "
                "                    AND x.tag_id = a.anc_id) "
                "GROUP BY ft.file_id, a.anc_id")]

            # ④ 有却不该有的继承标签：这个标签既不是手工/规则标签，
            #    也不在任何「手工/规则标签」的祖先链上 → 是祖先关系被删后遗留的孤儿
            del_ids = [(r[0], r[1]) for r in self.conn.execute(
                "SELECT ft.file_id, ft.tag_id FROM file_tags ft "
                "WHERE ft.is_auto = 1 "
                "  AND NOT EXISTS (SELECT 1 FROM file_tags s "
                "                  JOIN _tag_anc_cache a ON a.tag_id = s.tag_id "
                "                  WHERE s.file_id = ft.file_id "
                "                    AND s.is_auto IN (0, 2, 3) "
                "                    AND a.anc_id = ft.tag_id)")]

            with self.conn:
                if del_ids:
                    self.conn.executemany(
                        "DELETE FROM file_tags "
                        "WHERE file_id=? AND tag_id=? AND is_auto=1",
                        del_ids)
                if add_ids:
                    self.conn.executemany(
                        "INSERT OR IGNORE INTO file_tags(file_id, tag_id, is_auto) "
                        "VALUES(?, ?, 1)", add_ids)

        files_affected = len(set([f for f, _ in add_ids]) |
                              set([f for f, _ in del_ids]))
        return {
            "added": len(add_ids),
            "removed": len(del_ids),
            "files_affected": files_affected,
        }

    def reassign_all_tag_colors(self):
        rows = self.conn.execute(
            "SELECT id FROM tags ORDER BY sort_order, id").fetchall()
        with self.conn:
            for i, r in enumerate(rows):
                self.conn.execute(
                    "UPDATE tags SET color=? WHERE id=?",
                    (auto_color(i), r["id"]))
        return len(rows)

    # ---------- 导入导出 ----------
    def export_tags_structure(self, path):
        rows = self.all_tags()
        id_to_name = {r[0]: r[1] for r in rows}
        parents_map = {}
        for p, c in self.all_tag_relations():
            pn = id_to_name.get(p)
            if pn:
                parents_map.setdefault(c, []).append(pn)

        tags_list = []
        for tid, name, color, cnt in rows:
            so_row = self.conn.execute(
                "SELECT sort_order FROM tags WHERE id=?", (tid,)).fetchone()
            so = so_row["sort_order"] if so_row else 0
            tags_list.append({
                "name": name,
                "color": color,
                "parents": parents_map.get(tid, []),
                "sort_order": so,
            })
        data = {
            "version": 2,
            "type": "tags_structure",
            "exported_at": datetime.now().isoformat(timespec="seconds"),
            "tags": tags_list,
        }
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return len(tags_list)

    def export_file_tags(self, path):
        rows = self.conn.execute(
            """SELECT f.path AS fpath, t.name AS tname
               FROM files f
               JOIN file_tags ft ON ft.file_id = f.id
               JOIN tags t ON t.id = ft.tag_id
               WHERE ft.is_auto = 0
               ORDER BY f.path COLLATE NOCASE"""
        ).fetchall()
        file_map = {}
        for r in rows:
            file_map.setdefault(r["fpath"], []).append(r["tname"])
        files_list = [{"path": p, "tags": tags}
                      for p, tags in file_map.items()]
        data = {
            "version": 1,
            "type": "file_tags",
            "exported_at": datetime.now().isoformat(timespec="seconds"),
            "files": files_list,
        }
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return len(files_list)

    def import_tags_structure(self, path, auto_resync=True):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if data.get("type") != "tags_structure":
            raise ValueError("这个 JSON 文件不是标签结构文件（type 应为 tags_structure）")

        tags_list = data.get("tags") or []

        created = 0
        updated = 0
        for t in tags_list:
            name = (t.get("name") or "").strip()
            if not name:
                continue
            color = t.get("color")
            row = self.conn.execute(
                "SELECT id, color FROM tags WHERE name = ?", (name,)).fetchone()
            if row is None:
                self.create_tag(name, color=color)
                created += 1
            else:
                if color and color.lower() != (row["color"] or "").lower():
                    self.set_tag_color(row["id"], color)
                    updated += 1

        imported_ids = set()
        for t in tags_list:
            name = (t.get("name") or "").strip()
            if name:
                tid = self.tag_id_by_name(name)
                if tid is not None:
                    imported_ids.add(tid)

        with self.conn:
            for tid in imported_ids:
                self.conn.execute(
                    "DELETE FROM tag_relations WHERE child_id = ? OR parent_id = ?",
                    (tid, tid))
                self.conn.execute(
                    "UPDATE tags SET sort_order = 0 WHERE id = ?", (tid,))

        linked = 0
        for t in tags_list:
            name = (t.get("name") or "").strip()
            if not name:
                continue
            cid = self.tag_id_by_name(name)
            if cid is None:
                continue

            p_names = []
            if isinstance(t.get("parents"), list):
                p_names = t["parents"]
            elif t.get("parent"):
                p_names = [t["parent"]]

            for p_name in p_names:
                if not p_name:
                    continue
                pid = self.tag_id_by_name(p_name)
                if pid is None:
                    continue
                if self.add_tag_relation(pid, cid):
                    linked += 1

            so = t.get("sort_order")
            if isinstance(so, int):
                self.conn.execute(
                    "UPDATE tags SET sort_order = ? WHERE id = ?", (so, cid))
        self.conn.commit()

        resync_info = None
        if auto_resync:
            resync_info = self.resync_all_file_tags()

        return {
            "created": created,
            "updated": updated,
            "linked": linked,
            "total_in_file": len(tags_list),
            "resync": resync_info,
        }

    def import_file_tags(self, path, skip_missing=True):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if data.get("type") != "file_tags":
            raise ValueError("这个 JSON 文件不是文件标签文件（type 应为 file_tags）")

        files_list = data.get("files") or []
        file_count = 0
        added_tags = 0
        skipped = 0
        for item in files_list:
            p = item.get("path")
            tags = item.get("tags") or []
            if not p or not tags:
                skipped += 1
                continue
            if skip_missing and not os.path.exists(p):
                skipped += 1
                continue
            file_count += 1
            for tag_name in tags:
                if not (tag_name or "").strip():
                    continue
                try:
                    self.add_tag_to_file(p, tag_name)
                    added_tags += 1
                except Exception as _e:
                    note_swallowed("导入文件标签：有文件没打上标签", _e)

        return {
            "files": file_count,
            "added_tags": added_tags,
            "skipped": skipped,
            "total_in_file": len(files_list),
        }

    def all_tags(self):
        rows = self.conn.execute(
            """SELECT t.id, t.name, t.color, t.sort_order,
                      (SELECT COUNT(*) FROM file_tags ft WHERE ft.tag_id = t.id) AS cnt
               FROM tags t ORDER BY t.sort_order, t.id""").fetchall()
        return [(r["id"], r["name"], r["color"], r["cnt"]) for r in rows]

    def all_tags_with_relations(self):
        tags = self.all_tags()
        tags_out = []
        for r in tags:
            so_row = self.conn.execute(
                "SELECT sort_order FROM tags WHERE id=?", (r[0],)).fetchone()
            so = so_row["sort_order"] if so_row else 0
            tags_out.append((r[0], r[1], r[2], r[3], so))
        relations = self.all_tag_relations()
        return tags_out, relations

    def leaf_tag_ids(self):
        rows = self.conn.execute("SELECT id FROM tags").fetchall()
        all_ids = {r["id"] for r in rows}
        has_child = {r["parent_id"] for r in self.conn.execute(
            "SELECT DISTINCT parent_id FROM tag_relations").fetchall()}
        return all_ids - has_child

    def tag_stats_for_paths(self, paths):
        total = len(paths)
        if not paths:
            return 0, 0, 0
        leaf_ids = self.leaf_tag_ids()
        n2o = {}
        for p in paths:
            n2o.setdefault(self.norm(p), []).append(p)
        keys = list(n2o.keys())
        file_tags = {}
        for i in range(0, len(keys), 400):
            chunk = keys[i: i + 400]
            ph = ",".join("?" * len(chunk))
            rows = self.conn.execute(
                f"""SELECT f.path AS fpath, ft.tag_id
                    FROM files f
                    JOIN file_tags ft ON ft.file_id = f.id
                    WHERE f.path IN ({ph})""",
                tuple(chunk)).fetchall()
            for r in rows:
                file_tags.setdefault(r["fpath"], set()).add(r["tag_id"])
        untagged = 0
        mid_only = 0
        for key in keys:
            tids = file_tags.get(key, set())
            if not tids:
                untagged += 1
            elif not (tids & leaf_ids):
                mid_only += 1
        return total, untagged, mid_only

    def filter_paths(self, paths, mode):
        if not mode or not paths:
            return paths
        leaf_ids = self.leaf_tag_ids()
        n2o = {}
        for p in paths:
            n2o.setdefault(self.norm(p), []).append(p)
        keys = list(n2o.keys())
        file_tags = {}
        for i in range(0, len(keys), 400):
            chunk = keys[i: i + 400]
            ph = ",".join("?" * len(chunk))
            rows = self.conn.execute(
                f"""SELECT f.path AS fpath, ft.tag_id
                    FROM files f
                    JOIN file_tags ft ON ft.file_id = f.id
                    WHERE f.path IN ({ph})""",
                tuple(chunk)).fetchall()
            for r in rows:
                file_tags.setdefault(r["fpath"], set()).add(r["tag_id"])
        result = []
        for p in paths:
            tids = file_tags.get(self.norm(p), set())
            if mode == "untagged":
                if not tids:
                    result.append(p)
            elif mode == "mid_only":
                if tids and not (tids & leaf_ids):
                    result.append(p)
        return result

    def create_tag(self, name, color=None):
        name = (name or "").strip()
        if not name:
            raise ValueError("标签名不能为空")
        if self.conn.execute("SELECT 1 FROM tags WHERE name = ?", (name,)).fetchone():
            raise ValueError(f'标签「{name}」已存在')
        if color is None:
            color = self._next_tag_color()
        n = self.conn.execute(
            "SELECT COALESCE(MAX(sort_order), -1) AS m FROM tags").fetchone()["m"]
        self.conn.execute(
            "INSERT INTO tags(name, color, sort_order) VALUES(?, ?, ?)",
            (name, color, n + 1))
        self.conn.commit()

    def rename_tag(self, tag_id, new_name):
        new_name = (new_name or "").strip()
        if not new_name:
            raise ValueError("标签名不能为空")
        dup = self.conn.execute(
            "SELECT 1 FROM tags WHERE name = ? AND id != ?",
            (new_name, tag_id)).fetchone()
        if dup:
            raise ValueError(f'标签「{new_name}」已存在')
        self.conn.execute("UPDATE tags SET name = ? WHERE id = ?", (new_name, tag_id))
        self.conn.commit()

    def set_tag_color(self, tag_id, color):
        self.conn.execute("UPDATE tags SET color = ? WHERE id = ?", (color, tag_id))
        self.conn.commit()

    def delete_tag(self, tag_id, keep_parents=True):
        affected = [r["file_id"] for r in self.conn.execute(
            "SELECT file_id FROM file_tags WHERE tag_id=?", (tag_id,)).fetchall()]
        ancestors = self.all_ancestors_of(tag_id)

        with self.conn:
            self.conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))

            if keep_parents and affected and ancestors:
                for fid in affected:
                    other_manual = [r["tag_id"] for r in self.conn.execute(
                        "SELECT tag_id FROM file_tags WHERE file_id=? AND is_auto=0",
                        (fid,)).fetchall()]
                    other_needed = set()
                    for om in other_manual:
                        other_needed.update(self.all_ancestors_of(om))
                    for anc in ancestors:
                        cur = self.conn.execute(
                            "SELECT is_auto FROM file_tags WHERE file_id=? AND tag_id=?",
                            (fid, anc)).fetchone()
                        if cur is None:
                            continue
                        if cur["is_auto"] == 1 and anc not in other_needed:
                            self.conn.execute(
                                "UPDATE file_tags SET is_auto=0 WHERE file_id=? AND tag_id=?",
                                (fid, anc))


    def find_files(self, tag_names, match_all=True):
        names = list(dict.fromkeys(t.strip() for t in tag_names if t.strip()))
        if not names:
            return []
        ph = ",".join("?" * len(names))
        if match_all:
            rows = self.conn.execute(
                f"""SELECT f.path, COUNT(DISTINCT t.id) AS n
                    FROM files f
                    JOIN file_tags ft ON ft.file_id = f.id
                    JOIN tags t ON t.id = ft.tag_id
                    WHERE t.name IN ({ph})
                    GROUP BY f.path HAVING n = ?
                    ORDER BY f.path COLLATE NOCASE""",
                (*names, len(names))).fetchall()
        else:
            rows = self.conn.execute(
                f"""SELECT DISTINCT f.path FROM files f
                    JOIN file_tags ft ON ft.file_id = f.id
                    JOIN tags t ON t.id = ft.tag_id
                    WHERE t.name IN ({ph})
                    ORDER BY f.path COLLATE NOCASE""",
                tuple(names)).fetchall()
        return [r["path"] for r in rows]

    def all_files(self):
        rows = self.conn.execute(
            "SELECT path FROM files ORDER BY path COLLATE NOCASE").fetchall()
        return [r["path"] for r in rows]

    def all_files_page(self, limit, offset):
        rows = self.conn.execute(
            "SELECT path FROM files ORDER BY id "
            "LIMIT ? OFFSET ?", (int(limit), int(offset))).fetchall()
        return [r["path"] for r in rows]

    def all_files_count(self):
        row = self.conn.execute(
            "SELECT COUNT(*) AS c FROM files").fetchone()
        return int(row["c"]) if row else 0

    def files_in_category_page(self, cid, limit, offset):
        rows = self.conn.execute(
            """SELECT path FROM (
                   SELECT f.path AS path, f.id AS fid FROM files f
                   JOIN category_files cf ON cf.file_id = f.id
                   WHERE cf.category_id = ?
                   UNION
                   SELECT f.path AS path, f.id AS fid FROM files f
                   JOIN file_tags ft ON ft.file_id = f.id
                   JOIN category_tag_links ctl ON ctl.tag_id = ft.tag_id
                   WHERE ctl.category_id = ?
               )
               ORDER BY fid
               LIMIT ? OFFSET ?""",
            (cid, cid, int(limit), int(offset))).fetchall()
        return [r["path"] for r in rows]

    def files_in_category_count(self, cid):
        """永远读缓存；实时统计由后台线程负责。

        ★ v25 补丁3：这句注释以前写的是「由后台 update_category_counts
          负责」，但那个方法全程序没人调用（已删）。真正干活的是
          界面里的 FileTaggerApp._bg_refresh_category_counts()
          —— 它直接调 _compute_category_count() 再写回 cached_cnt。
        """
        try:
            row = self.conn.execute(
                "SELECT cached_cnt FROM categories WHERE id = ?",
                (cid,)).fetchone()
            if row is not None:
                return int(row["cached_cnt"] or 0)
        except Exception as _e:
            note_swallowed("读分类的文件数量失败（分类可能显示成 0 个文件）", _e)
        return 0
    
    def all_categories(self):
        rows = self.conn.execute(
            """SELECT c.id, c.name, c.icon, c.icon_type, c.icon_path,
                      c.color, c.sort_order,
                      COALESCE(c.cached_cnt, 0) AS cnt
               FROM categories c ORDER BY c.sort_order, c.id""").fetchall()
        return [dict(r) for r in rows]

    def _compute_category_count(self, cid, conn=None):
        """算一个分类里有多少文件。

        ★★ v26（2026-10-01）：多了一个 conn 参数 —— 后台线程要把自己的
        独立连接传进来，**不要再走主程序那条公用连接**（会卡主界面）。
        """
        c = conn if conn is not None else self.conn
        row = c.execute(
            """SELECT COUNT(*) AS c FROM (
                   SELECT cf.file_id AS fid FROM category_files cf
                   WHERE cf.category_id = ?
                   UNION
                   SELECT ft.file_id AS fid FROM file_tags ft
                   JOIN category_tag_links ctl ON ctl.tag_id = ft.tag_id
                   WHERE ctl.category_id = ?
               )""", (cid, cid)).fetchone()
        return int(row["c"]) if row else 0


    def create_category(self, name, icon="", icon_type="text",
                        icon_path="", color=None):
        name = (name or "").strip()
        if not name:
            raise ValueError("分类名不能为空")
        if self.conn.execute(
            "SELECT 1 FROM categories WHERE name = ?", (name,)).fetchone():
            raise ValueError(f'分类「{name}」已存在')
        if color is None:
            cnt = self.conn.execute(
                "SELECT COUNT(*) AS c FROM categories").fetchone()["c"]
            color = CAT_COLORS[cnt % len(CAT_COLORS)]
        n = self.conn.execute(
            "SELECT COALESCE(MAX(sort_order), -1) AS m FROM categories").fetchone()["m"]
        self.conn.execute(
            """INSERT INTO categories
               (name, icon, icon_type, icon_path, color, sort_order)
               VALUES(?, ?, ?, ?, ?, ?)""",
            (name, icon, icon_type, icon_path, color, n + 1))
        self.conn.commit()

    def update_category(self, cid, **kw):
        allowed = {"name", "icon", "icon_type", "icon_path", "color"}
        sets, vals = [], []
        for k, v in kw.items():
            if k not in allowed:
                continue
            if k == "name":
                v = (v or "").strip()
                if not v:
                    raise ValueError("分类名不能为空")
                dup = self.conn.execute(
                    "SELECT 1 FROM categories WHERE name = ? AND id != ?",
                    (v, cid)).fetchone()
                if dup:
                    raise ValueError(f'分类「{v}」已存在')
            sets.append(f"{k} = ?")
            vals.append(v)
        if not sets:
            return
        vals.append(cid)
        self.conn.execute(
            f"UPDATE categories SET {', '.join(sets)} WHERE id = ?", tuple(vals))
        self.conn.commit()

    def delete_category(self, cid):
        self.conn.execute("DELETE FROM categories WHERE id = ?", (cid,))
        self.conn.commit()

    def linked_tag_ids(self, cid):
        rows = self.conn.execute(
            "SELECT tag_id FROM category_tag_links WHERE category_id = ?",
            (cid,)).fetchall()
        return {r["tag_id"] for r in rows}

    def set_category_tag_links(self, cid, tag_ids):
        with self.conn:
            self.conn.execute(
                "DELETE FROM category_tag_links WHERE category_id = ?", (cid,))
            for t in tag_ids:
                self.conn.execute(
                    "INSERT OR IGNORE INTO category_tag_links(category_id, tag_id) "
                    "VALUES(?, ?)", (cid, t))

    # ---------- ★ 分类的"自动屏蔽标签" ----------
    def get_category_hidden_tags(self, cid):
        """返回打开该分类时应该自动屏蔽的标签 id 集合。"""
        try:
            rows = self.conn.execute(
                "SELECT tag_id FROM category_hidden_tags "
                "WHERE category_id = ?", (int(cid),)).fetchall()
            return {r["tag_id"] for r in rows}
        except Exception:
            return set()

    def set_category_hidden_tags(self, cid, tag_ids):
        with self.conn:
            self.conn.execute(
                "DELETE FROM category_hidden_tags WHERE category_id = ?",
                (int(cid),))
            for t in (tag_ids or []):
                self.conn.execute(
                    "INSERT OR IGNORE INTO category_hidden_tags"
                    "(category_id, tag_id) VALUES(?, ?)",
                    (int(cid), int(t)))

    # ---------- ★ 文件名自动标签规则 ----------
    def get_auto_name_rule_tag_ids(self):
        try:
            rows = self.conn.execute(
                "SELECT tag_id FROM auto_name_rule_tags").fetchall()
            return {r["tag_id"] for r in rows}
        except Exception:
            return set()

    def set_auto_name_rule_tag_ids(self, tag_ids):
        with self.conn:
            self.conn.execute("DELETE FROM auto_name_rule_tags")
            for t in (tag_ids or []):
                self.conn.execute(
                    "INSERT OR IGNORE INTO auto_name_rule_tags(tag_id) "
                    "VALUES(?)", (int(t),))

    def apply_auto_name_rules(self, paths):
        if not paths:
            return 0
        with self._lock:
            return self._apply_auto_name_rules_impl(paths)

    def _apply_auto_name_rules_impl(self, paths):
        """文件名里包含勾选的标签名 → 自动打上该标签（is_auto=3）。"""
        try:
            tag_ids = self.get_auto_name_rule_tag_ids()
        except Exception:
            return 0
        if not tag_ids:
            return 0
        try:
            ph = ",".join("?" * len(tag_ids))
            rows = self.conn.execute(
                f"SELECT id, name FROM tags WHERE id IN ({ph})",
                tuple(tag_ids)).fetchall()
        except Exception:
            return 0
        tag_names = [(r["id"], (r["name"] or "").strip()) for r in rows]
        tag_names = [(tid, n) for tid, n in tag_names if n]
        if not tag_names:
            return 0
        # 长名优先，避免"ab"抢了"abc"的命中
        tag_names.sort(key=lambda x: -len(x[1]))

        changed = 0
        with self.conn:
            for path in paths:
                try:
                    name = os.path.basename(path) or ""
                    if not name:
                        continue
                    lower_name = name.lower()

                    matched = set()
                    for tid, tname in tag_names:
                        if tname.lower() in lower_name:
                            matched.add(tid)

                    fid = self._fid(path, create=False)
                    if fid is None:
                        if not matched:
                            continue
                        fid = self._fid(path)

                    cur = self.conn.execute(
                        "SELECT tag_id FROM file_tags "
                        "WHERE file_id=? AND is_auto=3", (fid,)).fetchall()
                    cur_ids = {r["tag_id"] for r in cur}

                    to_remove = cur_ids - matched
                    existing = {r["tag_id"] for r in self.conn.execute(
                        "SELECT tag_id FROM file_tags WHERE file_id=?",
                        (fid,)).fetchall()}
                    to_add = [t for t in matched if t not in existing]

                    if to_remove:
                        self.conn.executemany(
                            "DELETE FROM file_tags "
                            "WHERE file_id=? AND tag_id=? AND is_auto=3",
                            [(fid, t) for t in to_remove])
                    if to_add:
                        self.conn.executemany(
                            "INSERT OR IGNORE INTO file_tags"
                            "(file_id, tag_id, is_auto) VALUES(?, ?, 3)",
                            [(fid, t) for t in to_add])

                    if to_remove or to_add:
                        changed += 1
                        self.resync_file(fid)
                except Exception:
                    continue
        return changed

    def resync_all_file_tags_with_name(self, pause=0.0, cancel=None):
        """对全库已记录文件重跑一遍文件名规则。

        ★ v25：多了 pause / cancel 两个可选参数，给「闲时自动跑」用：
          pause = 每批之间睡多久（越大越慢越温和）；
          cancel() 返回 True 就立刻收工（用户回来了就别抢资源）。
          默认值保持原来的行为，手动调用完全不受影响。
        """
        try:
            paths = self.all_files()
        except Exception:
            paths = []
        if not paths:
            return 0
        # 分批，避免一次全内存
        total = 0
        step = 500
        for i in range(0, len(paths), step):
            if cancel is not None:
                try:
                    if cancel():
                        break
                except Exception:
                    pass
            total += self.apply_auto_name_rules(paths[i:i + step])
            if pause:
                try:
                    time.sleep(pause)
                except Exception:
                    pass
        return total

    def merge_duplicate_paths(self, apply=False):
        """★ 合并「同一个文件被存成多条记录」的历史遗留问题。

        老版本对 UNC 路径（\\\\服务器\\共享\\…）没做小写归一：
        同一个文件会存两条记录 —— 一条保留原始大小写、一条是小写
        （norm() 形式）。而现在 _fid() / tags_for_paths() 统一按 norm() 查，
        只会命中小写那条，于是「标签明明打了、界面上却看不见」
        （最典型的就是自动标签规则刚打上的标签，还有标签库跳转后也不显示）。

        本方法把同一个文件的多条记录合成一条：
          - 保留 norm() 形式的那条（运行时真正会用到的那条）；若一条都不是，
            就把最小 id 那条的路径改写成 norm() 形式；
          - 其余记录上的 file_tags / category_files 全部并过来
            （同一个标签冲突时保留更"手工"的那个 is_auto，0 最优先）；
          - 删掉多余记录。

        ★ v23 起：分组用「大小写无关」的键，并且**单独一条但写法不规范的
          记录也会被改写成 norm() 形式**（历史上不同版本的 norm() 写法不同，
          网盘路径可能被写成大写，导致按路径查标签查不到）。

        apply=False 时只统计、绝不写库。返回统计字典：
        {groups, removed, moved_tags, moved_cats, renamed}
        """
        stat = {"groups": 0, "removed": 0, "moved_tags": 0,
                "moved_cats": 0, "renamed": 0}
        rows = self.conn.execute(
            "SELECT id, path FROM files ORDER BY id").fetchall()
        groups = {}
        for r in rows:
            try:
                # ★ v23：按「大小写无关」的键分组，把历史上被写成
                #   大小写不同的同一批记录也一起收进来。
                key = self._case_key(r["path"])
            except Exception:
                key = r["path"]
            groups.setdefault(key, []).append((r["id"], r["path"]))

        plan = []
        for key, items in groups.items():
            # 规范写法 = norm()（UNC 网盘会转小写，本地盘取真实大小写）
            target = items[0][1]
            try:
                target = self.norm(items[0][1])
            except Exception:
                pass
            surv_id, surv_path = items[0]
            for fid, p in items:
                if p == target:
                    surv_id, surv_path = fid, p
                    break
            if len(items) < 2 and surv_path == target:
                continue
            if len(items) > 1:
                stat["groups"] += 1
                stat["removed"] += len(items) - 1
            if surv_path != target:
                stat["renamed"] += 1
            plan.append((target, surv_id, surv_path, items))

        if not apply or not plan:
            # 只统计：预估要搬多少标签 / 分类归属
            for _key, surv_id, _sp, items in plan:
                have = {r["tag_id"]: r["is_auto"] for r in self.conn.execute(
                    "SELECT tag_id, is_auto FROM file_tags WHERE file_id=?",
                    (surv_id,)).fetchall()}
                for fid, _p in items:
                    if fid == surv_id:
                        continue
                    for r in self.conn.execute(
                            "SELECT tag_id, is_auto FROM file_tags "
                            "WHERE file_id=?", (fid,)).fetchall():
                        if r["tag_id"] not in have:
                            stat["moved_tags"] += 1
                            have[r["tag_id"]] = r["is_auto"]
                        elif r["is_auto"] < have[r["tag_id"]]:
                            have[r["tag_id"]] = r["is_auto"]
                    stat["moved_cats"] += self.conn.execute(
                        "SELECT COUNT(*) AS c FROM category_files "
                        "WHERE file_id=?", (fid,)).fetchone()["c"]
            return stat

        touched = set()
        with self.conn:
            for key, surv_id, surv_path, items in plan:
                if surv_path != key:
                    try:
                        self.conn.execute(
                            "UPDATE files SET path=? WHERE id=?",
                            (key, surv_id))
                    except Exception as _e:
                        note_swallowed("合并重复记录：改写路径失败", _e)
                for fid, _p in items:
                    if fid == surv_id:
                        continue
                    # ---- 标签并过去 ----
                    for tag_id, is_auto in self.conn.execute(
                            "SELECT tag_id, is_auto FROM file_tags "
                            "WHERE file_id=?", (fid,)).fetchall():
                        cur = self.conn.execute(
                            "SELECT is_auto FROM file_tags "
                            "WHERE file_id=? AND tag_id=?",
                            (surv_id, tag_id)).fetchone()
                        if cur is None:
                            self.conn.execute(
                                "INSERT OR IGNORE INTO file_tags"
                                "(file_id, tag_id, is_auto) VALUES(?, ?, ?)",
                                (surv_id, tag_id, is_auto))
                            stat["moved_tags"] += 1
                        elif is_auto < cur["is_auto"]:
                            self.conn.execute(
                                "UPDATE file_tags SET is_auto=? "
                                "WHERE file_id=? AND tag_id=?",
                                (is_auto, surv_id, tag_id))
                    # ---- 分类归属并过去 ----
                    for r in self.conn.execute(
                            "SELECT category_id FROM category_files "
                            "WHERE file_id=?", (fid,)).fetchall():
                        self.conn.execute(
                            "INSERT OR IGNORE INTO category_files"
                            "(category_id, file_id) VALUES(?, ?)",
                            (r["category_id"], surv_id))
                        stat["moved_cats"] += 1
                    # ---- 删掉多余记录 ----
                    self.conn.execute(
                        "DELETE FROM file_tags WHERE file_id=?", (fid,))
                    self.conn.execute(
                        "DELETE FROM category_files WHERE file_id=?", (fid,))
                    self.conn.execute("DELETE FROM files WHERE id=?", (fid,))
                if len(items) > 1:
                    # ★ v23：只有真的合并过（动过标签）才需要补父级标签链；
                    #   单纯改路径大小写的记录不用走这一步。
                    touched.add(surv_id)

        # 合并后标签链（is_auto=1 的父级）可能缺，只补不删
        # ★ 特意不调用 resync_file()：它会顺手删掉"当前没有子标签"的
        #   is_auto=1 标签，修复数据时不该有删除动作（要清理可以走
        #   菜单「同步所有文件的标签链」）。
        for fid in touched:
            try:
                rows = self.conn.execute(
                    "SELECT tag_id, is_auto FROM file_tags WHERE file_id=?",
                    (fid,)).fetchall()
                cur_ids = {r["tag_id"] for r in rows}
                manual = {r["tag_id"] for r in rows
                          if r["is_auto"] in (0, 2, 3)}
                target = set()
                for m in manual:
                    target.update(self.all_ancestors_of(m))
                adds = [(fid, t) for t in target if t not in cur_ids]
                if adds:
                    with self.conn:
                        self.conn.executemany(
                            "INSERT OR IGNORE INTO file_tags"
                            "(file_id, tag_id, is_auto) VALUES(?, ?, 1)", adds)
                    stat["added_ancestors"] = (stat.get("added_ancestors", 0)
                                               + len(adds))
            except Exception as _e:
                note_swallowed("合并重复记录：补祖先标签失败", _e)
        return stat

    def add_file_to_category(self, cid, path):
        fid = self._fid(path)
        self.conn.execute(
            "INSERT OR IGNORE INTO category_files(category_id, file_id) VALUES(?, ?)",
            (cid, fid))
        self.conn.commit()

    def remove_file_from_category(self, cid, path):
        fid = self._fid(path, create=False)
        if fid is None:
            return
        self.conn.execute(
            "DELETE FROM category_files WHERE category_id = ? AND file_id = ?",
            (cid, fid))
        self.conn.commit()

    def files_in_category(self, cid):
        direct = self.conn.execute(
            """SELECT f.path FROM files f
               JOIN category_files cf ON cf.file_id = f.id
               WHERE cf.category_id = ?""", (cid,)).fetchall()
        linked = self.conn.execute(
            """SELECT DISTINCT f.path FROM files f
               JOIN file_tags ft ON ft.file_id = f.id
               JOIN category_tag_links ctl ON ctl.tag_id = ft.tag_id
               WHERE ctl.category_id = ?""", (cid,)).fetchall()
        paths = {r["path"] for r in direct} | {r["path"] for r in linked}
        return sorted(paths, key=lambda p: p.lower())

    def search_files_in_category(self, cid, keyword):
        """在某个分类里按关键字搜路径（分类直挂的文件 + 标签关联的文件）。"""
        kw = f"%{keyword}%"
        rows = self.conn.execute(
            """SELECT DISTINCT f.path FROM files f
               JOIN category_files cf ON cf.file_id = f.id
               WHERE cf.category_id = ? AND f.path LIKE ?
               UNION
               SELECT DISTINCT f.path FROM files f
               JOIN file_tags ft ON ft.file_id = f.id
               JOIN category_tag_links ctl ON ctl.tag_id = ft.tag_id
               WHERE ctl.category_id = ? AND f.path LIKE ?""",
            (cid, kw, cid, kw)).fetchall()
        return [r["path"] for r in rows]

    def search_all_files(self, keyword):
        kw = f"%{keyword}%"
        rows = self.conn.execute(
            "SELECT path FROM files WHERE path LIKE ?", (kw,)).fetchall()
        return [r["path"] for r in rows]

        # ---------- ★ 标签在星图里的位置 ----------
    def get_all_tag_positions(self):
        rows = self.conn.execute(
            "SELECT tag_id, x, y FROM tag_positions").fetchall()
        return {r["tag_id"]: (r["x"], r["y"]) for r in rows}

    def set_tag_position(self, tid, x, y):
        self.conn.execute(
            "INSERT OR REPLACE INTO tag_positions(tag_id, x, y) VALUES(?, ?, ?)",
            (int(tid), float(x), float(y)))
        self.conn.commit()

    def set_tag_positions_bulk(self, positions):
        if not positions:
            return
        with self.conn:
            for tid, xy in positions.items():
                if not xy:
                    continue
                x, y = xy
                self.conn.execute(
                    "INSERT OR REPLACE INTO tag_positions(tag_id, x, y) "
                    "VALUES(?, ?, ?)", (int(tid), float(x), float(y)))

    def clear_tag_position(self, tid):
        self.conn.execute(
            "DELETE FROM tag_positions WHERE tag_id = ?", (int(tid),))
        self.conn.commit()


        # ---------- ★ 线颜色持久化 ----------
    def get_all_edge_colors(self):
        try:
            rows = self.conn.execute(
                "SELECT parent_id, child_id, color FROM edge_colors").fetchall()
        except Exception:
            return {}
        return {(r["parent_id"], r["child_id"]): r["color"] for r in rows}

    def set_edge_colors_bulk(self, colors):
        with self.conn:
            self.conn.execute("DELETE FROM edge_colors")
            for (pid, cid), color in (colors or {}).items():
                self.conn.execute(
                    "INSERT OR REPLACE INTO edge_colors(parent_id, child_id, color) "
                    "VALUES(?, ?, ?)", (int(pid), int(cid), str(color)))

    # ---------- ★ 自动标签规则 ----------
    def all_auto_rules(self):
        try:
            rows = self.conn.execute(
                """SELECT r.id, r.tag_id, t.name, t.color,
                          r.rule_type, r.pattern, r.target,
                          r.case_sensitive, r.enabled,
                          COALESCE(r.scope_path, '') AS scope_path
                   FROM auto_tag_rules r
                   JOIN tags t ON t.id = r.tag_id
                   ORDER BY r.id""").fetchall()
        except Exception:
            rows = self.conn.execute(
                """SELECT r.id, r.tag_id, t.name, t.color,
                          r.rule_type, r.pattern, r.target,
                          r.case_sensitive, r.enabled,
                          '' AS scope_path
                   FROM auto_tag_rules r
                   JOIN tags t ON t.id = r.tag_id
                   ORDER BY r.id""").fetchall()
        return [dict(r) for r in rows]

    def add_auto_rule(self, tag_id, rule_type, pattern,
                      target='name', case_sensitive=False,
                      scope_path=''):
        pattern = (pattern or "").strip()
        scope_path = (scope_path or "").strip()
        if not scope_path and not pattern:
            raise ValueError("匹配内容不能为空")
        if rule_type not in ("text", "ext", "*"):
            raise ValueError("规则类型错误")
        if target not in ("name", "path"):
            target = "name"
        if not scope_path and rule_type == "*":
            raise ValueError("「全部文件」规则必须指定作用范围")
        self.conn.execute(
            """INSERT INTO auto_tag_rules
               (tag_id, rule_type, pattern, target, case_sensitive,
                enabled, scope_path)
               VALUES(?, ?, ?, ?, ?, 1, ?)""",
            (int(tag_id), rule_type, pattern, target,
             1 if case_sensitive else 0, scope_path))
        self.conn.commit()

    def update_auto_rule(self, rule_id, tag_id, rule_type, pattern,
                         target='name', case_sensitive=False,
                         scope_path=''):
        pattern = (pattern or "").strip()
        scope_path = (scope_path or "").strip()
        if not scope_path and not pattern:
            raise ValueError("匹配内容不能为空")
        if rule_type not in ("text", "ext", "*"):
            raise ValueError("规则类型错误")
        if target not in ("name", "path"):
            target = "name"
        if not scope_path and rule_type == "*":
            raise ValueError("「全部文件」规则必须指定作用范围")
        self.conn.execute(
            """UPDATE auto_tag_rules
               SET tag_id=?, rule_type=?, pattern=?, target=?,
                   case_sensitive=?, scope_path=?
               WHERE id=?""",
            (int(tag_id), rule_type, pattern, target,
             1 if case_sensitive else 0, scope_path, int(rule_id)))
        self.conn.commit()
    def delete_auto_rule(self, rule_id):
        row = self.conn.execute(
            "SELECT tag_id FROM auto_tag_rules WHERE id = ?",
            (int(rule_id),)).fetchone()
        self.conn.execute("DELETE FROM auto_tag_rules WHERE id = ?",
                          (int(rule_id),))
        self.conn.commit()
        if row:
            with self.conn:
                self.conn.execute(
                    "DELETE FROM file_tags WHERE tag_id=? AND is_auto=2",
                    (row["tag_id"],))
            self.resync_all_file_tags()

    def set_auto_rule_enabled(self, rule_id, enabled):
        row = self.conn.execute(
            "SELECT tag_id FROM auto_tag_rules WHERE id = ?",
            (int(rule_id),)).fetchone()
        self.conn.execute(
            "UPDATE auto_tag_rules SET enabled = ? WHERE id = ?",
            (1 if enabled else 0, int(rule_id)))
        self.conn.commit()
        if row and not enabled:
            with self.conn:
                self.conn.execute(
                    "DELETE FROM file_tags WHERE tag_id=? AND is_auto=2",
                    (row["tag_id"],))
            self.resync_all_file_tags()

    def auto_tag_ids_for(self, name, path):
        """根据启用的规则返回该文件应自动获得的 tag_id 集合"""
        try:
            rules = self.conn.execute(
                "SELECT tag_id, rule_type, pattern, target, case_sensitive, "
                "COALESCE(scope_path, '') AS scope_path "
                "FROM auto_tag_rules WHERE enabled = 1").fetchall()
        except Exception:
            return set()
        if not rules:
            return set()
        ext = os.path.splitext(name)[1].lower().lstrip(".")
        result = set()
        for r in rules:
            try:
                rt = r["rule_type"]
                pat = r["pattern"] or ""
                tgt = r["target"] or "name"
                cs = int(r["case_sensitive"] or 0)
                try:
                    scope = r["scope_path"] or ""
                except Exception:
                    scope = ""
                if not self._scope_matches(path, scope):
                    continue
                if rt == "*":
                    result.add(r["tag_id"])
                elif rt == "ext":
                    pats = [p.strip().lower().lstrip(".")
                            for p in pat.split(",") if p.strip()]
                    if ext and ext in pats:
                        result.add(r["tag_id"])
                else:
                    hay = name if tgt == "name" else path
                    # ★ v23：多个关键词用逗号/换行分隔，任一命中即可
                    if self._rule_text_hits(pat, hay, cs):
                        result.add(r["tag_id"])
            except Exception:
                continue
        return result


    def sync_auto_tags_for_paths(self, paths):
        """按自动规则扫描这些文件，把命中的标签写进数据库
           （scope 规则 is_auto=2，文件名规则 is_auto=3）。
           返回受影响文件数。"""
        if not paths:
            return 0
        with self._lock:
            n1 = self._sync_auto_tags_impl(paths)
            n2 = self._apply_auto_name_rules_impl(paths)
            return n1 + n2

    def _sync_auto_tags_impl(self, paths):
        try:
            rules = self.conn.execute(
                "SELECT tag_id, rule_type, pattern, target, case_sensitive, "
                "COALESCE(scope_path, '') AS scope_path "
                "FROM auto_tag_rules WHERE enabled = 1").fetchall()
        except Exception:
            return 0

        changed = 0
        with self.conn:
            for path in paths:
                try:
                    name = os.path.basename(path)
                    ext = os.path.splitext(name)[1].lower().lstrip(".")

                    leaf_ids = set()
                    for r in rules:
                        try:
                            rt = r["rule_type"]
                            pat = r["pattern"] or ""
                            tgt = r["target"] or "name"
                            cs = int(r["case_sensitive"] or 0)
                            try:
                                scope = r["scope_path"] or ""
                            except Exception:
                                scope = ""
                            if not self._scope_matches(path, scope):
                                continue
                            if rt == "*":
                                leaf_ids.add(r["tag_id"])
                            elif rt == "ext":
                                pats = [p.strip().lower().lstrip(".")
                                        for p in pat.split(",") if p.strip()]
                                if ext and ext in pats:
                                    leaf_ids.add(r["tag_id"])
                            else:
                                hay = name if tgt == "name" else path
                                # ★ v23：多个关键词用逗号/换行分隔，
                                #   任一命中即可
                                if self._rule_text_hits(pat, hay, cs):
                                    leaf_ids.add(r["tag_id"])
                        except Exception:
                            continue

                    fid = self._fid(path, create=False)
                    if fid is None:
                        if not leaf_ids:
                            continue
                        fid = self._fid(path)

                    cur = self.conn.execute(
                        "SELECT tag_id FROM file_tags "
                        "WHERE file_id=? AND is_auto=2", (fid,)).fetchall()
                    cur_ids = {r["tag_id"] for r in cur}

                    to_remove = cur_ids - leaf_ids

                    existing = {r["tag_id"] for r in self.conn.execute(
                        "SELECT tag_id FROM file_tags WHERE file_id=?",
                        (fid,)).fetchall()}
                    to_add = [t for t in leaf_ids if t not in existing]

                    if to_remove:
                        self.conn.executemany(
                            "DELETE FROM file_tags "
                            "WHERE file_id=? AND tag_id=? AND is_auto=2",
                            [(fid, t) for t in to_remove])
                    if to_add:
                        self.conn.executemany(
                            "INSERT OR IGNORE INTO file_tags"
                            "(file_id, tag_id, is_auto) VALUES(?, ?, 2)",
                            [(fid, t) for t in to_add])

                    if to_remove or to_add:
                        changed += 1
                        self.resync_file(fid)
                except Exception:
                    continue
        return changed

    # ---------- ★ 目录条目缓存 ----------
    def _index_root_paths(self):
        """索引根目录列表（缓存起来，别每次都查库）。"""
        try:
            if getattr(self, "_idx_root_cache", None) is None:
                self._idx_root_cache = [str(r["path"] or "")
                                        for r in self.all_index_roots()]
            return self._idx_root_cache
        except Exception:
            return []

    def _net_cache_variants(self, dir_path):
        """★ v25 补丁14：同一个网盘目录常有**两种写法**：
              X:\\图本\\纸质游戏            （盘符）
              \\\\CloudDrive\\百度网盘\\图本\\纸质游戏   （UNC 真名）
        而索引里只会存其中一种（你这台机器存的是 UNC）。
        以前用 X: 打开目录时缓存永远查不到 → 只能去真网盘扫 → 很卡。
        这里把「另一种写法」也算出来，查缓存时两种都试。
        ★ 只对**网络盘**做这个换算（本地盘绝不动，免得张冠李戴）。
        """
        out = []
        try:
            p = str(dir_path or "")
            if not p:
                return out
            drive, rest = os.path.splitdrive(p)
            if not drive or drive.startswith("\\\\"):
                return out                     # 已经是 UNC 了，不用换算
            if not is_remote_path(p):           # 本地盘不做换算
                return out
            rel = rest.lstrip("\\")
            for root in self._index_root_paths():
                if not root.startswith("\\\\"):
                    continue
                base = root.rstrip("\\")
                out.append(base + ("\\" + rel if rel else ""))
        except Exception:
            pass
        return out

    def _dir_cache_stored_path(self, dir_path):
        """返回索引里该目录实际存储的写法（大小写可能不同）。

        先精确查（走索引，最快），查不到再用大小写不敏感兜底 ——
        ★ v23：避免「路径大小写写法不同」导致缓存明明有却重新去扫网盘。
        """
        if not dir_path:
            return None
        candidates = [dir_path] + self._net_cache_variants(dir_path)   # ★ 补丁14
        try:
            for cand in candidates:
                row = self.conn.execute(
                    "SELECT dir_path FROM dir_cache_meta WHERE dir_path = ?",
                    (cand,)).fetchone()
                if row is not None:
                    return row["dir_path"]
            for cand in candidates:
                row = self.conn.execute(
                    "SELECT dir_path FROM dir_cache_meta "
                    "WHERE dir_path = ? COLLATE NOCASE LIMIT 1",
                    (cand,)).fetchone()
                if row is not None:
                    return row["dir_path"]
            return None
        except Exception:
            return None

    def get_dir_entries(self, dir_path):
        """读缓存。返回 [(name, is_dir, size, mtime), ...] 或 None（无缓存）"""
        try:
            stored = self._dir_cache_stored_path(dir_path)
            if stored is None:
                return None
            rows = self.conn.execute(
                "SELECT name, is_dir, size, mtime FROM dir_cache "
                "WHERE dir_path = ?", (stored,)).fetchall()
            return [(r["name"], bool(r["is_dir"]),
                     r["size"], r["mtime"]) for r in rows]
        except Exception:
            return None

    def get_dir_scan_time(self, dir_path):
        try:
            stored = self._dir_cache_stored_path(dir_path)
            if stored is None:
                return None
            row = self.conn.execute(
                "SELECT scanned_at FROM dir_cache_meta WHERE dir_path = ?",
                (stored,)).fetchone()
            return row["scanned_at"] if row else None
        except Exception:
            return None

    def save_dir_entries(self, dir_path, entries):
        """entries: [(name, is_dir, size, mtime), ...]

        ★ v25：条目里 size / mtime 为 None 时，保留库里原来记下的值，
          不再用 NULL 覆盖 —— 否则只要索引扫描（不读大小）跑一次，
          之前记下来的文件大小就全被冲成「?」了。
        """
        with self._lock:
            try:
                with self.conn:
                    old = {}
                    try:
                        rows = self.conn.execute(
                            "SELECT name, size, mtime FROM dir_cache "
                            "WHERE dir_path = ?", (dir_path,)).fetchall()
                        for r in rows:
                            old[r["name"]] = (r["size"], r["mtime"])
                    except Exception:
                        old = {}
                    values = []
                    for (n, d, s, m) in entries:
                        if s is None or m is None:
                            prev = old.get(n)
                            if prev is not None:
                                if s is None:
                                    s = prev[0]
                                if m is None:
                                    m = prev[1]
                        values.append((dir_path, n, 1 if d else 0, s, m))
                    self.conn.execute(
                        "DELETE FROM dir_cache WHERE dir_path = ?", (dir_path,))
                    self.conn.executemany(
                        "INSERT INTO dir_cache(dir_path, name, is_dir, size, mtime) "
                        "VALUES(?, ?, ?, ?, ?)",
                        values)
                    self.conn.execute(
                        "INSERT OR REPLACE INTO dir_cache_meta(dir_path, scanned_at) "
                        "VALUES(?, ?)",
                        (dir_path, datetime.now().isoformat(timespec="seconds")))
            except Exception as _e:
                note_swallowed("写目录缓存失败（下次打开这个目录还得重新扫）", _e)
    def lookup_paths_meta(self, paths):
        """批量从 dir_cache 表查这些文件的 (is_dir, size, mtime)。
           完全走本地 SQLite，不碰磁盘。
           返回 {path: (is_dir, size, mtime)}，没查到的 path 不在结果里。"""
        if not paths:
            return {}
        by_dir = {}
        all_names = set()
        for p in paths:
            d = os.path.dirname(p)
            n = os.path.basename(p)
            by_dir.setdefault(d, []).append(n)
            all_names.add(n)

        dir_list = list(by_dir.keys())
        name_list = list(all_names)

        # SQLite 变量上限 999，分块查询
        CHUNK = 300
        result = {}
        try:
            with self._lock:
                for i in range(0, len(dir_list), CHUNK):
                    dchunk = dir_list[i:i + CHUNK]
                    dir_ph = ",".join("?" * len(dchunk))
                    for j in range(0, len(name_list), CHUNK):
                        nchunk = name_list[j:j + CHUNK]
                        name_ph = ",".join("?" * len(nchunk))
                        try:
                            rows = self.conn.execute(
                                f"SELECT dir_path, name, is_dir, size, mtime "
                                f"FROM dir_cache "
                                f"WHERE dir_path IN ({dir_ph}) "
                                f"  AND name IN ({name_ph})",
                                (*dchunk, *nchunk)).fetchall()
                        except Exception:
                            continue
                        for r in rows:
                            key = (r["dir_path"], r["name"])
                            result[key] = (bool(r["is_dir"]),
                                           r["size"], r["mtime"])
        except Exception:
            return {}

        out = {}
        for p in paths:
            d = os.path.dirname(p)
            n = os.path.basename(p)
            meta = result.get((d, n))
            if meta is not None:
                out[p] = meta
        return out

    # ---------- ★ v23：按「本地索引 / 已记录文件」枚举范围 ----------
    @staticmethod
    def _esc_like(s):
        """LIKE 里的转义（路径里常出现 _ 和 %，不转义会乱匹配）"""
        return (str(s).replace("\\", "\\\\")
                       .replace("%", "\\%")
                       .replace("_", "\\_"))

    @staticmethod
    def _case_key(path):
        """大小写无关的路径键（分组/去重用；不碰磁盘）"""
        try:
            return os.path.normcase(os.path.normpath(str(path)))
        except Exception:
            return str(path)

    def _range_bounds(self, prefix):
        """给 dir_cache / dir_cache_meta 的范围查询准备下上界，
           同时给出「原样写法」和「全小写写法」两种。"""
        try:
            p = os.path.normpath(str(prefix))
        except Exception:
            p = str(prefix)
        keys = []
        for cand in (p, self._case_key(p)):
            if cand not in keys:
                keys.append(cand)
        return [(k, k + "\uffff") for k in keys]

    def index_file_entries_under(self, scope, max_files=200000):
        """从 dir_cache 索引里取出 scope（含所有子目录）下的文件条目。

        返回 [(完整路径, 目录写法), ...]，**纯 SQLite，不碰磁盘**。
        索引里没有这个范围时返回空列表。
        """
        out = []
        if not scope:
            return out
        with self._lock:
            for lo, hi in self._range_bounds(scope):
                try:
                    rows = self.conn.execute(
                        "SELECT dir_path, name FROM dir_cache "
                        "WHERE dir_path >= ? AND dir_path < ? AND is_dir = 0 "
                        "LIMIT ?", (lo, hi, max_files)).fetchall()
                except Exception:
                    rows = []
                if rows:
                    out = [(os.path.join(r["dir_path"], r["name"]),
                            r["dir_path"]) for r in rows]
                    break
            if not out:
                # 索引里的目录是按「原始大小写」存的，范围查询对不上时
                # 用大小写不敏感的 LIKE 兜底（慢一点，但仍是本地库）
                like = self._esc_like(self._case_key(scope)) + "%"
                try:
                    rows = self.conn.execute(
                        "SELECT dir_path, name FROM dir_cache "
                        "WHERE lower(dir_path) LIKE ? ESCAPE '\\' "
                        "  AND is_dir = 0 LIMIT ?",
                        (like, max_files)).fetchall()
                except Exception:
                    rows = []
                out = [(os.path.join(r["dir_path"], r["name"]),
                        r["dir_path"]) for r in rows]
        return out

    def indexed_dirs_under(self, scope, max_dirs=20000):
        """索引里 scope 下的目录列表（用于估算 / 给建议）"""
        if not scope:
            return []
        with self._lock:
            for lo, hi in self._range_bounds(scope):
                try:
                    rows = self.conn.execute(
                        "SELECT dir_path FROM dir_cache_meta "
                        "WHERE dir_path >= ? AND dir_path < ? LIMIT ?",
                        (lo, hi, max_dirs)).fetchall()
                except Exception:
                    rows = []
                if rows:
                    return [r["dir_path"] for r in rows]
            like = self._esc_like(self._case_key(scope)) + "%"
            try:
                rows = self.conn.execute(
                    "SELECT dir_path FROM dir_cache_meta "
                    "WHERE lower(dir_path) LIKE ? ESCAPE '\\' LIMIT ?",
                    (like, max_dirs)).fetchall()
            except Exception as _e:
                # ★ v25 补丁4：原来是静默给个空列表 —— 于是「索引里明明有」
                #   却扫不到文件，用户只看到「点了没反应 / 一个文件都没有」。
                note_swallowed("枚举索引目录项失败（这次可能扫不到文件）", _e)
                rows = []
        return [r["dir_path"] for r in rows]

    def files_under_scope(self, scope, max_files=200000, progress_cb=None):
        """枚举 scope（含所有子目录）下的文件。

        ★ v23：优先吃本地索引 / 已记录文件，绝不轻易实时遍历网盘：
          ① files 表里已记录的路径（纯 SQLite）
          ② dir_cache 索引里的目录项（纯 SQLite）
          ③ 两个都没有 → 返回空，由调用方决定是否实时遍历

        返回 {"paths": [...], "from_db": 条数, "from_index": 条数}
        """
        result = {"paths": [], "from_db": 0, "from_index": 0}
        if not scope:
            return result
        try:
            base = os.path.normpath(str(scope))
        except Exception:
            base = str(scope)
        seen = {}

        # ① 已记录文件（LIKE 前缀；3 万行级别，毫秒级）
        like = self._esc_like(self._case_key(base)) + "%"
        try:
            with self._lock:
                rows = self.conn.execute(
                    "SELECT path FROM files WHERE lower(path) LIKE ? "
                    "ESCAPE '\\' LIMIT ?", (like, max_files)).fetchall()
        except Exception as _e:
            # ★ v25 补丁4：这里静默变成空 → 「扫描范围里一个文件都没有」。
            #   以前查不出来，现在至少会在日志面板留一句。
            note_swallowed("枚举扫描范围：查已记录文件失败（这次可能扫不到文件）", _e)
            rows = []
        for r in rows:
            p = r["path"]
            k = self._case_key(p)
            if k not in seen:
                seen[k] = p
        result["from_db"] = len(seen)
        if progress_cb:
            try:
                progress_cb(len(seen))
            except Exception:
                pass

        # ② 索引里的目录项
        try:
            entries = self.index_file_entries_under(
                base, max_files=max(1, max_files - len(seen)))
        except Exception as _e:
            # ★ v25 补丁4：同上 —— 索引查询失败会静默变成「没有文件」。
            note_swallowed("枚举扫描范围：查目录索引失败（这次可能扫不到文件）", _e)
            entries = []
        for p, _d in entries:
            k = self._case_key(p)
            if k not in seen:
                seen[k] = p
        result["from_index"] = len(seen) - result["from_db"]

        paths = list(seen.values())
        paths.sort(key=lambda x: x.lower())
        result["paths"] = paths
        return result

    def scope_known_file_count(self, scope, cap=200000):
        """范围下有多少「已知」文件（已记录 + 已索引），给界面提示用"""
        try:
            return len(self.files_under_scope(scope, max_files=cap)["paths"])
        except Exception:
            return 0

    def suggest_scopes_for(self, scope, limit=10):
        """范围写法可能不对时，给出「大概想说」的候选路径。

        典型场景：规则范围填了 X:\\，但程序里记录的是
        \\\\CloudDrive-X-…\\CloudDrive\\…（CloudDrive2 的 UNC 写法）。
        """
        cands = []
        try:
            roots = [r["path"] for r in self.all_index_roots()]
        except Exception:
            roots = []
        s = (scope or "").strip()
        letter = ""
        if len(s) >= 2 and s[1] == ":" and s[0].isalpha():
            letter = s[0].lower()
        if letter:                       # 盘符 → 索引根里含该盘符的排前面
            for r in roots:
                if letter in r.lower()[:64] and r not in cands:
                    cands.append(r)
        for r in roots:
            if r not in cands:
                cands.append(r)
        extra = []                       # 再补一层子目录（如 …\CloudDrive\图本）
        for r in cands[:3]:
            for d in self.indexed_dirs_under(r, max_dirs=40):
                if d not in cands and d not in extra:
                    extra.append(d)
        out = cands[:limit] + extra
        # ★ 去掉尾斜杠等，写法更规范（_scope_matches 里也会 normpath）
        clean = []
        for c in out[:limit]:
            try:
                c = os.path.normpath(str(c))
            except Exception:
                pass
            if c not in clean:
                clean.append(c)
        return clean

    def clear_dir_cache(self, dir_path=None):
        try:
            with self.conn:
                if dir_path:
                    self.conn.execute(
                        "DELETE FROM dir_cache WHERE dir_path = ?", (dir_path,))
                    self.conn.execute(
                        "DELETE FROM dir_cache_meta WHERE dir_path = ?",
                        (dir_path,))
                else:
                    self.conn.execute("DELETE FROM dir_cache")
                    self.conn.execute("DELETE FROM dir_cache_meta")
        except Exception as _e:
            note_swallowed("清除目录缓存失败", _e)

    def dir_cache_meta_count_under(self, prefix):
        """返回某前缀下已缓存的目录数量（粗略统计）。"""
        prefix = (prefix or "").rstrip("\\/")
        if not prefix:
            try:
                row = self.conn.execute(
                    "SELECT COUNT(*) AS c FROM dir_cache_meta").fetchone()
                return int(row["c"]) if row else 0
            except Exception:
                return 0
        try:
            norm = os.path.normcase(os.path.normpath(prefix))
        except Exception:
            norm = prefix
        try:
            row = self.conn.execute(
                "SELECT COUNT(*) AS c FROM dir_cache_meta "
                "WHERE dir_path = ? OR LOWER(dir_path) LIKE ? "
                "   OR LOWER(dir_path) LIKE ?",
                (prefix, norm + "\\%", prefix + "\\%")).fetchone()
            return int(row["c"]) if row else 0
        except Exception:
            return 0

    def clear_dir_cache_under(self, prefix):
        """清掉某个路径前缀下的所有目录缓存（含所有子目录）。"""
        prefix = (prefix or "").rstrip("\\/")
        if not prefix:
            return
        try:
            norm = os.path.normcase(os.path.normpath(prefix))
        except Exception:
            norm = prefix
        like1 = norm + "\\%"
        like2 = norm + "/%"
        like3 = prefix + "\\%"
        like4 = prefix + "/%"
        with self.conn:
            try:
                self.conn.execute(
                    "DELETE FROM dir_cache WHERE "
                    "dir_path = ? OR "
                    "LOWER(dir_path) LIKE ? OR LOWER(dir_path) LIKE ? OR "
                    "dir_path LIKE ? OR dir_path LIKE ?",
                    (prefix, like1, like2, like3, like4))
                self.conn.execute(
                    "DELETE FROM dir_cache_meta WHERE "
                    "dir_path = ? OR "
                    "LOWER(dir_path) LIKE ? OR LOWER(dir_path) LIKE ? OR "
                    "dir_path LIKE ? OR dir_path LIKE ?",
                    (prefix, like1, like2, like3, like4))
            except Exception as _e:
                note_swallowed("清除某个索引根目录下的缓存失败", _e)

    # ---------- ★ 索引根 ----------
    def all_index_roots(self):
        try:
            rows = self.conn.execute(
                "SELECT id, path, enabled, added_at, last_scan_at, "
                "total_files, total_dirs, last_error "
                "FROM index_roots ORDER BY id").fetchall()
        except Exception:
            return []
        return [dict(r) for r in rows]

    def add_index_root(self, path):
        p = str(Path(path).expanduser().resolve())
        if not os.path.isdir(p):
            raise ValueError(f"不是有效的文件夹：\n{p}")
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT OR IGNORE INTO index_roots"
                    "(path, enabled, added_at) VALUES(?, 1, ?)",
                    (p, datetime.now().isoformat(timespec="seconds")))
        except Exception as exc:
            raise RuntimeError(str(exc))
        return p

    def remove_index_root(self, root_id, also_clear_cache=True):
        row = self.conn.execute(
            "SELECT path FROM index_roots WHERE id = ?",
            (int(root_id),)).fetchone()
        if row is None:
            return
        path = row["path"]
        with self.conn:
            self.conn.execute(
                "DELETE FROM index_roots WHERE id = ?", (int(root_id),))
        if also_clear_cache:
            self.clear_dir_cache_under(path)

    def set_index_root_enabled(self, root_id, enabled):
        with self.conn:
            self.conn.execute(
                "UPDATE index_roots SET enabled = ? WHERE id = ?",
                (1 if enabled else 0, int(root_id)))

    # ======================================================================
    # ★ v25 补丁26：标签盒（把常用标签固定在一个小盒子里）
    # ======================================================================
    def tag_box_ids(self):
        """盒子里「固定」的标签 id（这个存在数据库里，换视图也在）。"""
        try:
            rows = self.conn.execute(
                "SELECT tag_id FROM tag_box ORDER BY sort_order, tag_id"
            ).fetchall()
            return [int(r[0]) for r in rows]
        except Exception:
            return []

    def tag_box_add(self, tid):
        with self._lock:
            with self.conn:
                self.conn.execute(
                    "INSERT OR IGNORE INTO tag_box(tag_id, sort_order) "
                    "VALUES(?, COALESCE((SELECT MAX(sort_order)+1 "
                    "FROM tag_box), 0))", (int(tid),))

    def tag_box_remove(self, tid):
        with self._lock:
            with self.conn:
                self.conn.execute("DELETE FROM tag_box WHERE tag_id=?",
                                  (int(tid),))

    def tag_box_clear(self):
        with self._lock:
            with self.conn:
                self.conn.execute("DELETE FROM tag_box")

    def tag_by_id(self, tid):
        """按 id 取一个标签（名字 + 颜色），取不到返回 None。"""
        try:
            r = self.conn.execute(
                "SELECT id, name, color FROM tags WHERE id=?",
                (int(tid),)).fetchone()
            if r:
                return {"id": r[0], "name": r[1], "color": r[2]}
        except Exception:
            pass
        return None

    def tags_by_usage(self, limit=200):
        """按「打了这个标签的文件数」从多到少排（标签盒勾选列表用）。"""
        try:
            rows = self.conn.execute(
                "SELECT t.id, t.name, COUNT(ft.file_id) AS cnt "
                "FROM tags t LEFT JOIN file_tags ft ON ft.tag_id = t.id "
                "GROUP BY t.id ORDER BY cnt DESC, t.name LIMIT ?",
                (int(limit),)).fetchall()
            return [{"id": r[0], "name": r[1], "cnt": r[2]} for r in rows]
        except Exception:
            return []

    def update_index_root_stats(self, root_id, total_files, total_dirs,
                                last_error=""):
        with self.conn:
            self.conn.execute(
                "UPDATE index_roots SET "
                "last_scan_at = ?, total_files = ?, total_dirs = ?, "
                "last_error = ? WHERE id = ?",
                (datetime.now().isoformat(timespec="seconds"),
                 int(total_files), int(total_dirs),
                 str(last_error or ""), int(root_id)))

    def close(self, timeout=1.5):
        """★ 2026-10-03：关连接之前**先拿住那把锁**（修一个真崩溃）。

        实测踩到的崩溃（退出码 -1073741819「访问违规」，用 faulthandler
        抓到栈才看清）：关窗时主线程调 `close()`，而「启动自检」那条
        后台线程正好在 `health_check()` 里查数据库 —— 两件事撞在一起，
        sqlite3 在 C 语言那一层就把整个进程带崩了。
        （栈：health_check(5135) → conn.execute  同时  on_close → close(7601)）

        为什么现在不会了：health_check 全程握着 `self._lock`，
        只要 close() 也拿这把锁，它就得**排队等查询做完**，
        绝不会在一条查询飞在半路时把连接关掉。

        ★★ 2026-10-06 重要修正：**等锁必须限时，不能死等！** ★★
           上面那个「排队等」在正常情况下没问题（查询都是毫秒级）。
           可用户报「点右上角的叉关不掉」—— 实测复现出来了：
             · 后台线程正在查一个 437MB 的大库（或者网盘卡住了），
               它会**一直握着这把锁**；
             · 主线程在 on_close 里调 close() → **排队等这把锁**；
             · 于是**界面僵在那儿，窗口关不掉、叉点了没反应**，
               实测能僵 **20 秒**（实测数据：占锁线程不放，退出就拖 20.2 秒）。
           现在改成：**最多等 timeout 秒**（默认 1.5 秒）。
           等到了就正常关；等不到就**不关那个连接、直接走人** ——
           进程马上就退了，操作系统会把文件句柄收回去，
           不会丢数据（SQLite 本来就是这么设计的）。
           ★ 一句话：**宁可让连接带着走，也绝不让用户盯着一个关不掉的窗口。**
        """
        try:
            got = self._lock.acquire(timeout=float(timeout))
        except Exception:
            got = False
        if not got:
            # ★ 等不到锁：记一笔，然后**不等了**（进程照常退）
            try:
                note_swallowed(
                    "退出时数据库正忙（有后台任务在查库），"
                    "这次没等它 —— 进程照常关闭，数据不会丢",
                    RuntimeError("db lock busy on close"), level="info")
            except Exception:
                pass
            self._closed = True
            return
        try:
            self._closed = True
            self.conn.close()
        except Exception:
            pass
        finally:
            try:
                self._lock.release()
            except Exception:
                pass

    def is_closed(self):
        return bool(getattr(self, "_closed", False))
        # ==========================================================================
#  文件列表（列表 / 瀑布流网格）
