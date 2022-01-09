@echo off

if "%PRE_RUN_STEP%" == "1" (
    echo "[pre_run_step.bat] Called recursively; skipping."
    exit
)
set PRE_RUN_STEP=1

if %YYTARGET_runtime% == YYC (
    echo "[pre_run_step.bat] STEP 1/5: Saving configuration before clean..."
    mkdir Z:\%YYMACROS_project_cache_directory_name%.save
    copy Z:\%YYMACROS_project_cache_directory_name%\*.* Z:\%YYMACROS_project_cache_directory_name%.save\

    echo "[pre_run_step.bat] STEP 2/5: Cleaning..."
    %YYMACROS_runtimeLocation%\bin\Igor.exe ^
        -j=%NUMBER_OF_PROCESSORS% -options="%YYtempFolder%\build.bff" -v -- Windows Clean

    echo "[pre_run_step.bat] STEP 3/5: Restoring configuration after clean..."
    move Z:\%YYMACROS_project_cache_directory_name%.save\* Z:\%YYMACROS_project_cache_directory_name%\
    rmdir Z:\%YYMACROS_project_cache_directory_name%.save

    echo "[pre_run_step.bat] STEP 4/5: Running initial build..."
    %YYMACROS_runtimeLocation%\bin\Igor.exe ^
        -j=%NUMBER_OF_PROCESSORS% -options="%YYtempFolder%\build.bff" -v -- Windows Run

    echo "[pre_run_step.bat] STEP 5/5: Starting YYCBoost background process..."
    %YYprojectDir%\..\YYCBoost_CLI\dist\yycboost.exe ^
        /background -logfile="%YYtempFolder%\yycboost.log" -timeout=60 ^
        -pidfile="%YYtempFolder%\yycboost.pid" -buildpath="%YYtempFolder%\build.bff"
)

set PRE_RUN_STEP=