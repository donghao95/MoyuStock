# Stock Monitor (股票监控助手)

一个基于 PySide6 开发的桌面即时股票行情监控工具。支持悬浮窗模式和主窗口模式，方便上班族摸鱼查看行情。

## ✨ 功能特性

*   **双模式显示**：
    *   **迷你悬浮窗**：背景透明，置顶显示，仅显示核心数据，不影响其他工作。
    *   **标准主窗口**：详细表格展示，支持查看更多数据字段。
*   **实时行情**：
    *   接入百度财经 API，支持 A 股、港股等多市场行情。
    *   实时监控价格变动和涨跌幅。
*   **便捷操作**：
    *   **系统托盘集成**：最小化至托盘，随时唤起。
    *   **全局快捷键**：
        *   `Alt + S`：一键显示/隐藏所有窗口（老板键）。
        *   `Alt + M`：快速切换迷你/主窗口模式。
*   **自定义设置**：
    *   支持添加、删除监控的股票代码。

## 🛠️ 环境要求

*   Python 3.8+
*   依赖库：参见 `requirements.txt`

## 🚀 安装与运行

1.  **克隆项目**
    ```bash
    git clone https://github.com/yourusername/stock_monitor.git
    cd stock_monitor
    ```

2.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

3.  **运行程序**
    ```bash
    python main.py
    ```

## 📦 打包说明

本项目支持使用 `PyInstaller` 打包为独立的可执行文件 (`.exe`)。

1.  运行构建脚本：
    ```bash
    python build.py
    ```
2.  构建完成后，可执行文件将生成在 `dist/` 目录下。
3.  你可以直接分发 `dist/StockMonitor.exe`，无需对方安装 Python 环境。

## 📝 许可证

MIT License
