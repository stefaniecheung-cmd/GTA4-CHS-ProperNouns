@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x86
cd /d "%~dp0"
cl /nologo /O2 /MT /LD mapfix.cpp /Fe:mapfix.asi /link /MACHINE:X86
echo BUILD_EXIT=%errorlevel%
if exist mapfix.asi echo CL_OK
