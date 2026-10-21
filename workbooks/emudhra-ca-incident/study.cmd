@echo off
rem Opens the workbook in your browser, with Run and Submit working. Double-click me,
rem and leave this window open while you work.
where py >nul 2>nul
if errorlevel 1 (
  echo Python 3.11 or newer is needed to open the workbook.
  echo Install it from https://www.python.org/downloads/ or run:  winget install Python.Python.3.12
  pause
  exit /b 1
)
py -c "import sys; sys.exit(sys.version_info < (3, 11))"
if errorlevel 1 (
  echo Python 3.11 or newer is needed to open the workbook. Install it from https://www.python.org/downloads/
  pause
  exit /b 1
)
py -P "%~dp0tools\serve.py" %*
if errorlevel 1 pause
