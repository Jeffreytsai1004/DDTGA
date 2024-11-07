@echo off
:: 设置代码页为UTF-8
chcp 65001 >nul
:: 设置控制台字体为支持中文的字体
reg add "HKEY_CURRENT_USER\Console" /v "FaceName" /t REG_SZ /d "NSimSun" /f >nul
:: 设置控制台代码页
reg add "HKEY_CURRENT_USER\Console\%%SystemRoot%%_system32_cmd.exe" /v "CodePage" /t REG_DWORD /d 65001 /f >nul

echo ============================================
echo [32m正在初始化环境...[0m
echo ============================================

:: 检查Python压缩包是否存在
if not exist "python-embed.zip" (
    echo [31mPython嵌入式包不存在，请下载python-3.13.0-embed-amd64.zip并重命名为python-embed.zip[0m
    pause
    exit /b 1
)

:: 创建必要的目录
if not exist ".\python" mkdir ".\python"
if not exist ".\python\Lib" mkdir ".\python\Lib"
if not exist ".\python\Lib\site-packages" mkdir ".\python\Lib\site-packages"
if not exist ".\python\DLLs" mkdir ".\python\DLLs"
if not exist ".\python\Scripts" mkdir ".\python\Scripts"

:: 解压Python
echo [32m正在解压Python...[0m
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 1 /nobreak >nul
powershell -Command "if (Test-Path python) { Remove-Item -Path python -Recurse -Force }"
mkdir "python"
powershell -Command "Expand-Archive -Path python-embed.zip -DestinationPath python -Force"

:: 下载并安装完整Python以获取tkinter
echo [32m正在下载Python标准库...[0m
powershell -Command "$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe' -OutFile 'python-installer.exe'"
echo [32m正在安装Python标准库...[0m
start /wait python-installer.exe /quiet InstallAllUsers=0 Include_launcher=0 Include_test=0 Include_tools=0
xcopy /E /I /Y "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\Lib\tkinter" ".\python\Lib\tkinter\"
xcopy /E /I /Y "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\DLLs\_tkinter.pyd" ".\python\DLLs\"
xcopy /E /I /Y "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\DLLs\tcl86t.dll" ".\python\DLLs\"
xcopy /E /I /Y "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\DLLs\tk86t.dll" ".\python\DLLs\"
del python-installer.exe

:: 复制tkinter相关文件
xcopy /E /I /Y "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\tcl" ".\python\tcl\"
xcopy /E /I /Y "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\Lib\tkinter" ".\python\Lib\tkinter\"
xcopy /E /I /Y "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\DLLs\_tkinter.pyd" ".\python\DLLs\"
xcopy /E /I /Y "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\DLLs\tcl86t.dll" ".\python\DLLs\"
xcopy /E /I /Y "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\DLLs\tk86t.dll" ".\python\DLLs\"

:: 解除嵌入式Python的限制
echo python313.zip > .\python\python313._pth
echo . >> .\python\python313._pth
echo Lib >> .\python\python313._pth
echo DLLs >> .\python\python313._pth
echo Lib\site-packages >> .\python\python313._pth

:: 设置环境变量
set PYTHONHOME=%CD%\python
set PYTHONPATH=%CD%\python;%CD%\python\Lib;%CD%\python\DLLs;%CD%\python\Lib\site-packages
set PATH=%CD%\python;%CD%\python\Scripts;%CD%\imagemagick;%PATH%
set MAGICK_HOME=%CD%\imagemagick

:: 安装pip和setuptools
echo [32m正在安装pip和setuptools...[0m
powershell -Command "$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py'"
.\python\python.exe get-pip.py --no-cache-dir --no-warn-script-location
.\python\Scripts\pip.exe install --no-cache-dir setuptools wheel
del /f /q get-pip.py

:: 安装依赖
echo ============================================
echo [32m正在安装依赖...[0m
echo ============================================
.\python\Scripts\pip.exe install --no-cache-dir --only-binary :all: -r requirements.txt

:: 如果安装失败，回退到最新版本
if errorlevel 1 (
    echo [33m尝试安装最新版本...[0m
    .\python\Scripts\pip.exe install --no-cache-dir --only-binary :all: ^
    customtkinter==5.2.2 ^
    Pillow==11.0.0 ^
    Wand==0.6.13 ^
    pyinstaller==6.11.0 ^
    packaging==23.2
)

:: 在打包应用之前添加这段代码
echo ============================================
echo [32m正在创建ImageMagick配置...[0m
echo ============================================

:: 创建delegates.xml
echo ^<?xml version="1.0" encoding="UTF-8"?^> > .\imagemagick\delegates.xml
echo ^<delegatemap^> >> .\imagemagick\delegates.xml
echo   ^<delegate decode="dds" command="convert &quot;%%i&quot; &quot;%%o&quot;"/^> >> .\imagemagick\delegates.xml
echo   ^<delegate decode="tga" command="convert &quot;%%i&quot; &quot;%%o&quot;"/^> >> .\imagemagick\delegates.xml
echo ^</delegatemap^> >> .\imagemagick\delegates.xml

:: 创建policy.xml
echo ^<?xml version="1.0" encoding="UTF-8"?^> > .\imagemagick\policy.xml
echo ^<policymap^> >> .\imagemagick\policy.xml
echo   ^<policy domain="coder" rights="read|write" pattern="TGA" /^> >> .\imagemagick\policy.xml
echo   ^<policy domain="coder" rights="read|write" pattern="DDS" /^> >> .\imagemagick\policy.xml
echo   ^<policy domain="coder" rights="read|write" pattern="*" /^> >> .\imagemagick\policy.xml
echo ^</policymap^> >> .\imagemagick\policy.xml

:: 创建magic.xml
echo ^<?xml version="1.0" encoding="UTF-8"?^> > .\imagemagick\magic.xml
echo ^<magicmap^> >> .\imagemagick\magic.xml
echo   ^<magic name="TGA" offset="0" target="0x0,0x0,0x2,0x0,0x0,0x0,0x0,0x0"/^> >> .\imagemagick\magic.xml
echo   ^<magic name="DDS" offset="0" target="44 44 53 20"/^> >> .\imagemagick\magic.xml
echo ^</magicmap^> >> .\imagemagick\magic.xml

:: 打包应用
echo ============================================
echo [32m正在打包应用...[0m
echo ============================================
.\python\python.exe build_exe.py

echo ============================================
echo [32m完成！[0m
echo ============================================
pause