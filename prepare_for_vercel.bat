@echo off
REM Prepare Anthill IQ Chatbot for Vercel deployment
REM This script helps prepare the project for deployment on Vercel

echo Preparing Anthill IQ Chatbot for Vercel deployment...

REM Run tests to ensure everything imports correctly
echo Running import tests...
python test_vercel.py

if %ERRORLEVEL% NEQ 0 (
    echo Tests failed! Please fix the issues before deploying.
    exit /b 1
)

REM Clean up unnecessary files
echo Cleaning up unnecessary files...

REM Remove unnecessary directories to reduce package size
if exist "api\backend_for_vercel\__pycache__" (
    rmdir /s /q "api\backend_for_vercel\__pycache__"
)

if exist "api\__pycache__" (
    rmdir /s /q "api\__pycache__"
)

if exist "__pycache__" (
    rmdir /s /q "__pycache__"
)

REM Verify requirements.txt exists in api folder
if not exist "api\requirements.txt" (
    echo ERROR: api\requirements.txt not found
    exit /b 1
)

REM Verify key files exist
echo Verifying key files...
set FILES_TO_CHECK=api\index.py api\simple_db.py api\service_account_handler.py vercel.json .vercelignore

for %%F in (%FILES_TO_CHECK%) do (
    if not exist "%%F" (
        echo ERROR: %%F not found!
        exit /b 1
    )
)

echo Verification complete! Project is ready for Vercel deployment.
echo.
echo Next steps:
echo 1. Commit and push changes to GitHub
echo 2. Import project in Vercel
echo 3. Set environment variables (OPENAI_API_KEY, DATABASE_URL)
echo 4. Deploy
echo.
echo See VERCEL-DEPLOY-GUIDE.md for detailed instructions. 