@echo off

if exist "runtime/command" (
    set /p command=< runtime\command
) else (
    set command=runtime\bin\python\python
)

"%command%" runtime\makepatches.py %*
pause
