@echo off
echo 正在运行鼠大师测试...

cd /d "%~dp0dist"

if exist "鼠大师.exe" (
    echo 找到可执行文件，正在启动...
    "鼠大师.exe"
) else (
    echo 错误：未找到鼠大师.exe，请确保已成功打包
    pause
)

echo.
echo 测试完成！
pause
