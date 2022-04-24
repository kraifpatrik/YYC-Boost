@echo off

if "%IGOR_BUILD_ONLY%" == "1" (
   echo "[post_run_step.bat] Called recursively; terminating recursive build."
   :: A non-zero exit code causes the calling instance of Igor.exe to terminate:
   exit 1
)

if %YYTARGET_runtime% == YYC (
    echo "[post_run_step.bat] Terminating YYCBoost..."
    %YYprojectDir%\..\YYCBoost_CLI\dist\yycboost.exe ^
        /close -pidfile="%YYtempFolder%\yycboost.pid"
)