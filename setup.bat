@echo off
title Initial MCP Setup

echo Initial MCP Setup
echo -------------------
echo.

::
:: Confirmation
::

set /P c=Are you sure you want to run the setup? [Y/N]? 
if /I "%c%" EQU "Y" goto :start 
if /I "%c%" EQU "N" goto :end

::
:: Methods
::

rem Download function
rem Arguments: 
rem         URL, Output file
rem     URL: a http(s) link 
rem     Output file: A path that will be output for the downloaded file
:download
runtime\bin\wget.exe -q -O %2 %1
exit /b

rem Unzip function
rem Arguments: 
rem         archive path, output path
rem     archive path: Path to the archive
rem     output path: Output folder 
:unzip
runtime\bin\7z.exe x -y -o%2 %1 >>nul
exit /b

:start

::
:: Create folders
::

echo.
echo Creating folders...
echo.

mkdir jars\bin\natives >> nul

::
:: Download runtimes
::

echo Downloading runtimes...
echo.

:: Kotlin Confirmation

set /P c=Do you want to use Kotlin in your project? [Y/N]? 
if /I "%c%" EQU "Y" goto :kotlin 
if /I "%c%" EQU "N" goto :skip

:kotlin

:: Kotlin Installation

call :download https://github.com/JetBrains/kotlin/releases/download/v1.2.61/kotlin-compiler-1.2.61.zip runtime\kotlinc.zip
call :unzip runtime\kotlinc.zip runtime
del /Q runtime\kotlinc.zip >> nul

echo  ^> Kotlin

:skip

:: Client
call :download https://launcher.mojang.com/v1/objects/43db9b498cb67058d2e12d394e6507722e71bb45/client.jar jars\bin\minecraft.jar

echo  ^> Client

:: Server (From BetaCraft, official would be better...)
call :download https://betacraft.ovh/server-archive/minecraft/b1.7.3.jar jars\minecraft_server.jar

echo  ^> Server

:: LWJGL 2.8.4
call :download http://central.maven.org/maven2/org/lwjgl/lwjgl/lwjgl/2.8.4/lwjgl-2.8.4.jar jars\bin\lwjgl.jar
call :download http://central.maven.org/maven2/org/lwjgl/lwjgl/lwjgl_util/2.8.4/lwjgl_util-2.8.4.jar jars\bin\lwjgl_util.jar
call :download http://central.maven.org/maven2/org/lwjgl/lwjgl/lwjgl-platform/2.8.4/lwjgl-platform-2.8.4-natives-windows.jar jars\bin\natives\lwjgl_platform.jar

echo  ^> LWJGL

:: jinput 2.0.5
call :download http://central.maven.org/maven2/net/java/jinput/jinput/2.0.5/jinput-2.0.5.jar jars\bin\jinput.jar
call :download http://central.maven.org/maven2/net/java/jinput/jinput-platform/2.0.5/jinput-platform-2.0.5-natives-windows.jar jars\bin\natives\jinput_platform.jar

echo  ^> jinput

::
:: Unzipping natives
::

echo.
echo Unzipping natives...

call :unzip jars\bin\natives\lwjgl_platform.jar jars\bin\natives
echo  ^> lwjgl_platform.jar
call :unzip jars\bin\natives\jinput_platform.jar jars\bin\natives
echo  ^> jinput_platform.jar
echo.

::
:: Clean up
::

echo Cleaning up...
echo.

rmdir /S /Q jars\bin\natives\META-INF >> nul
del /Q jars\bin\natives\lwjgl_platform.jar >> nul
del /Q jars\bin\natives\jinput_platform.jar >> nul

:end
echo Finished^!
echo.

pause