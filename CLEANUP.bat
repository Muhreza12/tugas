@echo off
echo Deleting unnecessary files...
echo.

REM Documentation files
del /f /q BEAUTIFUL_UI_GUIDE.md 2>nul
del /f /q BEFORE_AFTER_COMPARISON.md 2>nul
del /f /q IMAGE_UPLOAD_GUIDE.md 2>nul
del /f /q PENERBIT_DASHBOARD_GUIDE.md 2>nul
del /f /q QUICK_START.md 2>nul
del /f /q README.md 2>nul
del /f /q README.txt 2>nul
del /f /q README_FIXES.md 2>nul
del /f /q TESTING_REPORT.md 2>nul
del /f /q TIKTOK_STYLE_GUIDE.md 2>nul
del /f /q UI_IMPROVEMENT_GUIDE.md 2>nul

REM Old auth UI files
del /f /q auth_ui.py 2>nul
del /f /q auth_ui_fixed.py 2>nul
del /f /q auth_ui_beautiful.py 2>nul
del /f /q auth_ui_enhanced.py 2>nul

REM Old database modules
del /f /q db.py 2>nul
del /f /q app_config.py 2>nul
del /f /q app_db.py 2>nul

REM Old main files
del /f /q integrated_main.py 2>nul
del /f /q integrated_main_with_monitoring.py 2>nul
del /f /q main_beautiful.py 2>nul
del /f /q main_enhanced.py 2>nul
del /f /q main_fixed.py 2>nul
del /f /q main_tiktok_style.py 2>nul

REM Test/demo files
del /f /q connect_test.py 2>nul
del /f /q demo_penerbit_dashboard.py 2>nul
del /f /q print_db_url.py 2>nul
del /f /q set_admin_pw.py 2>nul
del /f /q test_connect_verbose.py 2>nul
del /f /q test_suite.py 2>nul

REM Build files
del /f /q build_crypto_insight.bat 2>nul
del /f /q build_simple.ps1 2>nul
del /f /q crypto_insight_installer.iss 2>nul
del /f /q main.spec 2>nul
del /f /q set_env_and_run_safe.ps1 2>nul

REM Other files
del /f /q gitignore.txt 2>nul
del /f /q register_form.py 2>nul
del /f /q style.qss 2>nul
del /f /q TATIAAAAa.html 2>nul

echo.
echo Done! Files deleted.
echo.
pause
