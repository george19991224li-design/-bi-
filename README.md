# 明析 BI

本地中文经营看板，支持 Windows、Linux 和 macOS。安装 Python 3.10 或更高版本（推荐 3.12），首次启动需联网安装依赖。启动器自动在项目的 `.venv` 中安装，不修改全局 Python 环境。

## 启动

下载仓库 ZIP 并解压，或通过 Git 克隆后，进入项目目录：

| 系统 | 启动方式 |
| --- | --- |
| Windows | 安装 Python 时勾选 Add Python to PATH，双击 `start.bat`，或在终端执行 `.\start.bat` |
| Linux | 运行 `bash start.sh` |
| macOS | 双击 `启动应用.command`，或运行 `bash start.sh` |

浏览器访问 http://127.0.0.1:8501 。关闭启动终端或按 Ctrl+C 停止服务。上传表格在本机处理。

Ubuntu/Debian 若提示缺少 venv，先执行 `sudo apt install python3 python3-venv`。Windows 若无法找到 Python，请安装 Python 后重新打开终端。不要复制其他系统的 `.venv`；只复制源代码，由启动器重新创建环境。

无桌面的 Linux 服务器：运行 `bash start.sh --no-browser`，在自己的电脑通过 `ssh -L 8501:127.0.0.1:8501 用户名@服务器` 转发端口后访问同一地址。默认仅监听本机，未实现账号登录。

端口被占用时可用 `bash start.sh --server.port 8502`（Windows：`start.bat --server.port 8502`）。只安装并检查依赖：`python launch.py --check`，Linux/macOS 使用 `python3`。

## 使用

支持 `.xlsx`、`.xls`、`.xlsm`、`.ods`、`.csv`、`.tsv`、分隔符文本 `.txt`。CSV 尝试 UTF-8、GB18030、UTF-16；支持选择工作表和表头行。上传内容在本地进程处理，未配置云端存储。

1. 上传表格，选择工作表与表头行。
2. 确认自动匹配的维度、毛利、售价、利润率列；字段名称不标准时手动选择。
3. 指定利润率的数值口径：0.25 或 25；带 `%` 的单元格自动识别。
4. 选择毛利合计或平均，筛选、排序、切换组合图。
5. 下载汇总 CSV、可离线打开的交互 HTML，或使用图表工具栏导出 PNG。

默认毛利柱状、售价折线、利润率折线。金额使用左轴，利润率使用右轴。售价与毛利差异大时可点击图例隐藏毛利。没有上传文件时展示明确标记的演示数据。

售价与利润率使用简单平均，不计算收入加权利润率；缺失/非法数值不填零，会显示数量。毛利合计适用于每行已经是毛利金额；单件毛利请考虑平均口径。利润率与毛利率并非一定同义，应用读取所选字段，不自行推导。公式型 Excel 读取已保存的计算结果，须先在 Excel/LibreOffice 中计算保存；不运行宏。不支持密码保护文件、PDF、图片 OCR 或跨文件自动合并。

手动启动（Linux/macOS）：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1
```

Windows 手动启动：

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

## 验证

Linux/macOS：`.venv/bin/python -m unittest discover -s tests -v`

Windows：`.venv\Scripts\python.exe -m unittest discover -s tests -v`

仓库包含 GitHub Actions 工作流，推送后在 Windows、Ubuntu、macOS 与 Python 3.10、3.12、3.14 上验证启动器和测试。工作流配置不等于实机验证结果，请以仓库 Actions 页面为准。
