@echo off
echo 正在清理多余文件...

:: 确保没有Python进程在运行
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul

:: 等待一秒让进程完全结束
timeout /t 1 /nobreak >nul

:: 删除python目录（准备重新解压）
if exist "python" (
    rd /s /q "python" 2>nul
    if exist "python" (
        echo 正在强制删除python目录...
        rmdir /s /q "python"
    )
)

:: 删除build和dist目录
if exist "build" (
    echo 正在删除build目录...
    rmdir /s /q "build"
)

if exist "dist" (
    echo 正在删除dist目录...
    rmdir /s /q "dist"
)

:: 删除spec文件
if exist "DDSTGA.spec" (
    echo 正在删除spec文件...
    del /f /q "DDSTGA.spec"
)

:: 创建新的python目录
mkdir "python"


echo 清理完成！
echo 现在可以运行Build.bat了
pause 