@echo off

set IGOR_BUILD_ONLY=1
set PROJECT_CACHE=%YYMACROS_asset_compiler_cache_directory:/=%\%YYMACROS_project_cache_directory_name%

if %YYTARGET_runtime% == YYC (
    echo "[pre_package_step.bat] STEP 1/7: Saving configuration before clean..."
    mkdir %PROJECT_CACHE%.save
    copy %PROJECT_CACHE%\*.* %PROJECT_CACHE%.save\

    echo "[pre_package_step.bat] STEP 2/7: Cleaning..."
    %YYMACROS_runtimeLocation%\bin\Igor.exe ^
        -j=%NUMBER_OF_PROCESSORS% -options="%YYtempFolder%\build.bff" -v -- Windows Clean

    echo "[pre_package_step.bat] STEP 3/7: Restoring configuration after clean..."
    mkdir %PROJECT_CACHE%
    move %PROJECT_CACHE%.save\* %PROJECT_CACHE%\
    rmdir %PROJECT_CACHE%.save

    echo "[pre_package_step.bat] STEP 4/7: Running preliminary build..."
    %YYMACROS_runtimeLocation%\bin\Igor.exe ^
        -j=%NUMBER_OF_PROCESSORS% -options="%YYtempFolder%\build.bff" -v -- Windows Run

    echo "[pre_package_step.bat] STEP 5/7: Starting YYCBoost background process..."
    %YYprojectDir%\..\YYCBoost_CLI\dist\yycboost.exe ^
        /background -logfile="%YYtempFolder%\yycboost.log" -timeout=60 ^
        -pidfile="%YYtempFolder%\yycboost.pid" -buildpath="%YYtempFolder%\build.bff"

    echo "[pre_package_step.bat] STEP 6/7: Running final build..."
    %YYMACROS_runtimeLocation%\bin\Igor.exe ^
        -j=%NUMBER_OF_PROCESSORS% -options="%YYtempFolder%\build.bff" -v -- Windows Run

    echo "[pre_package_step.bat] STEP 7/7: Terminating YYCBoost..."
    %YYprojectDir%\..\YYCBoost_CLI\dist\yycboost.exe ^
        /close -pidfile="%YYtempFolder%\yycboost.pid"
)

set IGOR_BUILD_ONLY=