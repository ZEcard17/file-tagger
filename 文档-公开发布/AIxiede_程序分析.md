# AIxiede.py 程序结构与运行逻辑分析

## 概述

`AIxiede.py` 是一个基于 Tkinter 的**文件标签管理器**（版本 v26），用于管理本地/网盘文件并为其打标签。核心使用 SQLite 数据库存储文件路径、标签及关联关系。

---

## 1. 主要类及其作用

### 核心应用类

| 类名 | 行号 | 作用 |
|------|------|------|
| `FileTaggerApp` | 22672 | 主应用类，管理整个窗口、UI布局、后天任务协调 |
| `FileList` | 7715 | 文件列表控件，支持列表/瀑布流视图、搜索、标签条筛选、框选拖拽 |
| `CategorySidebar` | 16302 | 左侧分类库面板，同时包含文件目录树 |
| `PreviewPane` | 14785 | 右侧预览窗格，支持文本/图片/PDF/视频/电子书预览 |
| `HoverPreview` | 20777 | 鼠标悬停小预览窗口 |

### 数据层类

| 类名 | 行号 | 作用 |
|------|------|------|
| `TagStore` | 4708 | 数据库封装类，封装所有 SQLite 操作（文件、标签、分类、规则） |
| `CloudDriveApiClient` | 3378 | 网盘 API 客户端（百度网盘等） |

---

## 2. 程序启动流程

```
main() [29327]
  │
  ├─ 创建 Tk root（支持拖放的用 TkinterDnD.Tk）
  ├─ _pick_font_family() — 探测系统字体
  ├─ _auto_ui_scale() — 计算 UI 缩放
  ├─ root.tk.call("tk", "scaling", ...) — 应用 DPI 缩放
  ├─ apply_unified_fonts() — 统一全程序字体
  │
  └─ FileTaggerApp(root, ui_scale) [22675]
        │
        ├─ self.store = TagStore(DB_PATH)  [22682]
        │     ├─ 连接 SQLite（timeout=30, WAL模式, busy_timeout=30000）
        │     ├─ _init_schema() — 建表
        │     └─ _migrate() — 数据迁移
        │
        ├─ heal_net_paths() — 自愈旧网盘路径 [22690]
        │
        ├─ _build_menu() — 构建菜单栏 [22758]
        │
        ├─ _build_ui() — 构建主界面 [22759]
        │     ├─ 顶部工具栏
        │     ├─ 左侧 CategorySidebar
        │     ├─ 中间 FileList
        │     ├─ 右侧 PreviewPane（默认隐藏）
        │     ├─ 底部状态栏 + 标签盒
        │     └─ PanedWindow 分栏
        │
        ├─ _ui_poll_job = root.after(60, self._ui_poll)  [22763]
        │     └─ 启动"后台线程信箱"轮询（每60ms取一次件）
        │
        ├─ refresh_categories() — 刷新分类库
        ├─ refresh_tags() — 刷新标签
        ├─ load_directory() — 加载目录
        │
        ├─ sidebar.refresh_file_tree() — 初始化文件树
        │
        ├─ _setup_idle_jobs() — 闲时任务
        │
        └─ root.after(3000, self._run_selfcheck) — 3秒后自检
```

---

## 3. 左侧分类库（CategorySidebar）工作流程

```
CategorySidebar [16302]
  │
  ├─ 上下分区 PanedWindow
  │     ├─ 上半部：分类库（Canvas + Scrollbar）
  │     └─ 下半部：文件目录树（ttk.Treeview）
  │
  ├─ set_categories(cats) [16543]
  │     ├─ 销毁旧 CategoryItem
  │     ├─ 创建新 CategoryItem（图标+名字+计数）
  │     └─ set_selected() 高亮当前分类
  │
  └─ 文件目录树操作
        ├─ refresh_file_tree() [16437]
        │     ├─ _get_root_paths() — 找文件树根目录
        │     └─ _add_tree_node() — 懒加载子节点
        │
        ├─ _expand_tree_node() [16487] — 双击展开时加载子目录
        │
        └─ _on_tree_double_click() [16513] → app.navigate_to_path()
```

---

## 4. 中间文件列表（FileList）加载和显示流程

```
load_directory(path) [主程序]
  │
  ├─ 清除旧数据
  ├─ 判断视图模式
  │     ├─ "dir" — 目录文件列表
  │     ├─ "category" — 分类视图
  │     ├─ "all" — 全部文件
  │     └─ "search" — 搜索结果
  │
  ├─ 后台扫描目录 → _ui_queue 回主线程
  │
  └─ FileList.set_rows(rows) [8020+]
        │
        ├─ 排序（按名称/大小/类型/标签）
        ├─ 计算布局
        │     ├─ 列表模式：按列宽分
        │     └─ 瀑布流模式：ICON_SIZES[level] 计算卡片尺寸
        │
        ├─ 缩略图后台加载
        │     ├─ _thumb_queue — 待加载队列
        │     ├─ _thumb_loading — 正在加载的（避免重复）
        │     └─ 后台线程 _thumb_worker()
        │
        └─ _redraw() — 绘制到 Canvas
```

---

## 5. 右侧预览窗格（PreviewPane）工作流程

```
PreviewPane [14785]
  │
  ├─ 文件类型判断
  │     ├─ TEXT_EXTS — 文本文件
  │     ├─ IMAGE_EXTS — 图片
  │     ├─ VIDEO_EXTS — 视频
  │     └─ BOOK_EXTS — 电子书
  │
  ├─ 加载内容
  │     ├─ 文本文件：_show_text() → tk.Text
  │     ├─ 图片：_show_pil_image() → Canvas.create_image
  │     ├─ PDF：_show_pdf_scroll() → 连续滚动模式
  │     └─ 视频：get_video_thumbnail_pil() → 缩略图
  │
  └─ 网盘文件处理
        ├─ _remote_tmp = {} — 本地缓存映射
        └─ 后台拷贝到本地 → 预览使用本地副本
```

---

## 6. 悬停预览（HoverPreview）工作流程

```
HoverPreview [20777]
  │
  ├─ on_motion(event) [20812]
  │     ├─ 获取 x_root, y_root
  │     ├─ app.file_list.get_path_at_y() — 找到悬停的文件
  │     └─ delay_ms 后调用 _show_now()
  │
  ├─ on_leave() [20839]
  │     └─ _cancel() — 取消计时器 + 销毁窗口
  │
  └─ _show_now() [20862]
        ├─ _build_window(path)
        │     ├─ 图片：PIL缩放显示
        │     ├─ PDF：get_pdf_page_pil(0)
        │     ├─ 视频：get_video_thumbnail_pil()
        │     └─ 其他：_quick_text() 前2KB
        └─ 定位窗口到鼠标附近
```

---

## 7. 视频缩略图获取完整流程

```python
def get_video_thumbnail_pil(path, size=320) [4557]
  │
  ├─ 方法1：Windows资源管理器缩略图（pywin32）
  │     └─ shell.Namespace + ExtendedProperty
  │
  ├─ 方法2：ffmpeg截帧
  │     └─ subprocess.run(["ffmpeg", "-ss", "1", "-i", path, "-frames:v", "1", ...])
  │
  └─ 方法3：cv2直接解码（主要方法）
        ├─ cv2.VideoCapture(path)
        ├─ 跳到约 1/4 处（跳过开场黑帧/字幕）
        └─ cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) → PIL Image
```

---

## 8. 数据库Schema [4793-4903]

```sql
-- 核心表
files           -- 文件路径记录
tags            -- 标签（id, name, color, sort_order）
file_tags       -- 文件-标签关联（file_id, tag_id, is_auto）
tag_relations   -- 标签父子关系（parent_id, child_id）

-- 扩展表
categories              -- 分类库
category_files         -- 分类-文件关联
category_tag_links     -- 分类-标签超链接
tag_positions          -- 标签星图位置
auto_tag_rules         -- 自动标签规则
dir_cache              -- 目录缓存（加速扫描）
```

---

## 9. 数据流总图

```
┌─────────────────────────────────────────────────────────┐
│                      main()                              │
│                   FileTaggerApp                          │
├──────────────┬──────────────────┬───────────────────────┤
│  CategorySidebar   │    FileList     │    PreviewPane      │
│  ·分类库           │  ·文件列表      │  ·文本/图片预览      │
│  ·文件目录树       │  ·搜索过滤      │  ·PDF滚动           │
│  ·右键菜单         │  ·框选拖拽      │  ·视频缩略图        │
└───────┬──────┴────────┬─────────┴───────────┬────────────┘
        │               │                      │
        └───────────────┴──────────────────────┘
                        │
              ┌─────────▼─────────┐
              │    TagStore      │
              │  (SQLite封装)    │
              ├──────────────────┤
              │ files           │
              │ tags            │
              │ file_tags       │
              │ tag_relations   │
              │ categories      │
              │ auto_tag_rules  │
              └──────────────────┘
```

---

## 10. 已知问题

1. **文件目录树空白**：`_get_root_paths()` 中属性名错误（`_cur_dir` vs `current_dir`）
2. **预览宽度不跟随**：canvas 宽度没有随窗格更新
3. **视频预览是静态图**：悬停/右侧预览只有一帧，没有循环播放
