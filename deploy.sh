#!/bin/bash

# EduSphere Deployment Script
echo "🚀 EduSphere Deployment Script"
echo "================================"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
fi

# Add all files
echo "📦 Adding files to Git..."
git add .

# Commit changes
echo "💾 Committing changes..."
read -p "Enter commit message (or press Enter for default): " commit_msg
if [ -z "$commit_msg" ]; then
    commit_msg="Deploy: EduSphere Complete Learning Platform"
fi
git commit -m "$commit_msg"

# Check if remote origin exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "🔗 Setting up GitHub remote..."
    read -p "Enter your GitHub repository URL: " repo_url
    git remote add origin "$repo_url"
fi

# Push to GitHub
echo "⬆️ Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ Successfully pushed to GitHub!"
echo ""
echo "🌐 Next Steps for Render Deployment:"
echo "1. Go to https://render.com"
echo "2. Sign up/Login with your GitHub account"
echo "3. Click 'New +' → 'Web Service'"
echo "4. Select your repository"
echo "5. Configure:"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: python app.py"
echo "6. Add environment variables:"
echo "   - FLASK_ENV=production"
echo "   - FLASK_DEBUG=false"
echo "   - GEMINI_API_KEY=your_api_key (optional)"
echo "7. Click 'Create Web Service'"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT_GUIDE.md"
echo ""
echo "🎉 Happy Deploying!"