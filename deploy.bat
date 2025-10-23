@echo off
echo 🚀 EduSphere Deployment Script
echo ================================

REM Check if git is initialized
if not exist ".git" (
    echo 📁 Initializing Git repository...
    git init
)

REM Add all files
echo 📦 Adding files to Git...
git add .

REM Commit changes
echo 💾 Committing changes...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Deploy: EduSphere Complete Learning Platform
git commit -m "%commit_msg%"

REM Check if remote origin exists
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo 🔗 Setting up GitHub remote...
    set /p repo_url="Enter your GitHub repository URL: "
    git remote add origin "%repo_url%"
)

REM Push to GitHub
echo ⬆️ Pushing to GitHub...
git branch -M main
git push -u origin main

echo.
echo ✅ Successfully pushed to GitHub!
echo.
echo 🌐 Next Steps for Render Deployment:
echo 1. Go to https://render.com
echo 2. Sign up/Login with your GitHub account
echo 3. Click 'New +' → 'Web Service'
echo 4. Select your repository
echo 5. Configure:
echo    - Build Command: pip install -r requirements.txt
echo    - Start Command: python app.py
echo 6. Add environment variables:
echo    - FLASK_ENV=production
echo    - FLASK_DEBUG=false
echo    - GEMINI_API_KEY=your_api_key (optional)
echo 7. Click 'Create Web Service'
echo.
echo 📖 For detailed instructions, see DEPLOYMENT_GUIDE.md
echo.
echo 🎉 Happy Deploying!
pause