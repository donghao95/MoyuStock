import PyInstaller.__main__
import os
import shutil

# 清理之前的构建文件
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

print("Starting build process...")

PyInstaller.__main__.run([
    'main.py',
    '--name=StockMonitor',
    '--onefile',          # 单文件打包
    '--windowed',         # 无控制台窗口
    '--clean',            # 清理临时文件
    '--noconfirm',        # 不确认覆盖
    
    # 排除不必要的库（如果有的话）
    '--exclude-module=pandas',
    '--exclude-module=tkinter',
    '--exclude-module=unittest',
    
    # 添加数据文件（如果有图标等资源需要添加）
    # '--add-data=resources;resources',
    
    # 优化参数
    '--noupx',            # 暂不使用UPX（以免需要额外下载）
    '--strip',            # 剥离符号表（减小体积）
])

print("Build complete! Check dist/StockMonitor.exe")
