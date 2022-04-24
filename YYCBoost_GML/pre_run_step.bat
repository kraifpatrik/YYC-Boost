@echo off

if "%IGOR_BUILD_ONLY%" == "1" (
    echo "[pre_run_step.bat] Called recursively; skipping."
    exit
)
set IGOR_BUILD_ONLY=1

set PROJECT_CACHE=%YYMACROS_asset_compiler_cache_directory:/=%\%YYMACROS_project_cache_directory_name%

if %YYTARGET_runtime% == YYC (
    echo "[pre_run_step.bat] STEP 1/5: Saving configuration before clean..."
    mkdir %PROJECT_CACHE%.save
    copy %PROJECT_CACHE%\*.* %PROJECT_CACHE%.save\

    echo "[pre_run_step.bat] STEP 2/5: Cleaning..."
    %YYMACROS_runtimeLocation%\bin\Igor.exe ^
        -j=%NUMBER_OF_PROCESSORS% -options="%YYtempFolder%\build.bff" -v -- Windows Clean

    echo "[pre_run_step.bat] STEP 3/5: Restoring configuration after clean..."
    mkdir %PROJECT_CACHE%
    move %PROJECT_CACHE%.save\* %PROJECT_CACHE%\
    rmdir %PROJECT_CACHE%.save

    echo "[pre_run_step.bat] STEP 4/5: Running preliminary build..."
    %YYMACROS_runtimeLocation%\bin\Igor.exe ^
        -j=%NUMBER_OF_PROCESSORS% -options="%YYtempFolder%\build.bff" -v -- Windows Run

    echo "[pre_run_step.bat] STEP 5/5: Starting YYCBoost background process..."
    %YYprojectDir%\..\YYCBoost_CLI\dist\yycboost.exe ^
        /background -logfile="%YYtempFolder%\yycboost.log" -timeout=60 ^
        -pidfile="%YYtempFolder%\yycboost.pid" -buildpath="%YYtempFolder%\build.bff"
)

set IGOR_BUILD_ONLY=