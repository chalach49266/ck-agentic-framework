@echo off
setlocal DisableDelayedExpansion
set "DRY_ARG="
if "%~1"=="--dry-run" set "DRY_ARG=--dry-run"
if not "%~1"=="" if not "%~1"=="--dry-run" goto usage
set "KIT=%~dp0"
set "BIN=%USERPROFILE%\.local\bin"
set "HERDR=%USERPROFILE%\.config\herdr-app"
rem Collect the same values for both preview and install before changing anything.
set "WIN_USER=%USERNAME%"
set "WIN_USER_INPUT="
set /p "WIN_USER_INPUT=Windows user [%WIN_USER%]: "
if defined WIN_USER_INPUT set "WIN_USER=%WIN_USER_INPUT%"
set "PHD_DEFAULT="
rem Offer the profile-based default only when the PhD directory exists.
if exist "%USERPROFILE%\Documents\PhD\" for /f "delims=" %%P in ('wsl.exe -d Ubuntu --exec wslpath -u "%USERPROFILE%\Documents\PhD"') do set "PHD_DEFAULT=%%P"
set "PHD_ROOT="
if defined PHD_DEFAULT goto ask_phd_default
set /p "PHD_ROOT=Full PhD folder (WSL path, required): "
goto check_phd
:ask_phd_default
set /p "PHD_ROOT=Full PhD folder (WSL path) [%PHD_DEFAULT%]: "
if not defined PHD_ROOT set "PHD_ROOT=%PHD_DEFAULT%"
:check_phd
if not defined PHD_ROOT goto missing_phd
if defined DRY_ARG goto preview
if not exist "%BIN%" mkdir "%BIN%"
if errorlevel 1 exit /b 1
copy /Y "%KIT%bin\*.cmd" "%BIN%\" >nul
if errorlevel 1 exit /b 1
if not exist "%HERDR%\layouts" mkdir "%HERDR%\layouts"
copy /Y "%KIT%herdr\layouts\main-ck.json" "%HERDR%\layouts\main-ck.json" >nul
if errorlevel 1 exit /b 1
xcopy /E /I /Y "%KIT%herdr\mods\agents-ck" "%HERDR%\mods\agents-ck" >nul
if errorlevel 1 exit /b 1
xcopy /E /I /Y "%KIT%herdr\mods\tabs-ck" "%HERDR%\mods\tabs-ck" >nul
if errorlevel 1 exit /b 1
xcopy /E /I /Y "%KIT%herdr\mods\pane-ck" "%HERDR%\mods\pane-ck" >nul
if errorlevel 1 exit /b 1
call :copy_pref "%KIT%herdr\settings.json" "%HERDR%\settings.json"
if errorlevel 1 exit /b 1
call :copy_pref "%KIT%herdr\keys.json" "%HERDR%\keys.json"
if errorlevel 1 exit /b 1
if not exist "%HERDR%\themes" mkdir "%HERDR%\themes"
if errorlevel 1 exit /b 1
for %%F in ("%KIT%herdr\themes\*.json") do (
  call :copy_pref "%%~fF" "%HERDR%\themes\%%~nxF"
  if errorlevel 1 exit /b 1
)
rem Use the ck look (green done, yellow needs-you, agents-ck, tabs-ck) when Herdr is installed; best effort.
if exist "%LOCALAPPDATA%\Programs\herdr-app\herdr-app.exe" "%LOCALAPPDATA%\Programs\herdr-app\herdr-app.exe" do layout.switch --name main-ck >nul 2>&1
set "USER_PATH="
for /f "tokens=2,*" %%A in ('reg query HKCU\Environment /v Path 2^>nul') do set "USER_PATH=%%B"
rem Quoted echo keeps spaces and ampersands in the existing PATH as data.
echo(";%USER_PATH%;" | findstr /I /L /C:";%BIN%;" /C:";%BIN%\;" >nul
if not errorlevel 1 goto wsl
if defined USER_PATH goto append_path
set "USER_PATH=%BIN%"
goto save_path
:append_path
set "USER_PATH=%USER_PATH%;%BIN%"
:save_path
reg add HKCU\Environment /v Path /t REG_EXPAND_SZ /d "%USER_PATH%" /f >nul
if errorlevel 1 exit /b 1
echo User PATH updated. Open a new terminal after setup.
goto wsl
:preview
echo DRY-RUN MKDIR "%BIN%"
for %%F in ("%KIT%bin\*.cmd") do echo DRY-RUN COPY "%%~fF" to "%BIN%\%%~nxF"
echo DRY-RUN ENSURE user PATH includes "%BIN%" using reg.exe
for /R "%KIT%herdr" %%F in (*) do echo DRY-RUN COPY "%%F" under "%HERDR%" keeping its relative folder
echo DRY-RUN BACKUP changed settings.json, keys.json and themes to .bak if no backup exists
echo DRY-RUN SWITCH Herdr to main-ck layout if the app is installed
:wsl
rem bash receives the kit path as an argument; wslpath handles Windows paths; strip WSL share prefixes for a Linux clone.
wsl.exe -d Ubuntu --exec bash -c "kit=$(wslpath -u \"$1\"); kit=${kit#//wsl.localhost/Ubuntu}; kit=${kit#//wsl$/Ubuntu}; exec bash \"$kit/setup.sh\" --yes --win-user \"$2\" --phd-root \"$3\" $4" setup "%~dp0." "%WIN_USER%" "%PHD_ROOT%" "%DRY_ARG%"
if errorlevel 1 exit /b 1
if defined DRY_ARG echo Dry-run finished. No setup changes were made.
if defined DRY_ARG exit /b 0
echo Setup finished. Restart Herdr and open a new Windows terminal.
exit /b 0
:copy_pref
rem Keep the original once. Identical repeat installs leave the file and backup alone.
if not exist "%~2" goto copy_pref_write
fc /B "%~1" "%~2" >nul 2>&1
if not errorlevel 1 exit /b 0
if exist "%~2.bak" goto copy_pref_write
copy /Y "%~2" "%~2.bak" >nul
if errorlevel 1 exit /b 1
:copy_pref_write
copy /Y "%~1" "%~2" >nul
exit /b %ERRORLEVEL%
:missing_phd
echo Full PhD folder is required. Rerun setup and enter its WSL path. No files were changed.
exit /b 2
:usage
echo Usage: setup.cmd [--dry-run]
exit /b 2
