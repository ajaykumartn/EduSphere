# 🚀 EduSphere Deployment Guide

## 📋 Prerequisites

- Git installed on your system
- GitHub account
- Render account (free tier available)
- Google Gemini API key (optional, for AI features)

---

## 🔧 Step 1: Prepare for GitHub

### 1.1 Initialize Git Repository (if not already done)
```bash
git init
git add .
git commit -m "Initial commit: EduSphere Complete Learning Platform"
```

### 1.2 Create GitHub Repository
1. Go to [GitHub](https://github.com) and create a new repository
2. Name it `edusphere-learning-platform` or similar
3. Don't initialize with README (we already have one)
4. Copy the repository URL

### 1.3 Connect Local Repository to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
git branch -M main
git push -u origin main
```

---

## 🌐 Step 2: Deploy on Render

### 2.1 Create Render Account
1. Go to [Render](https://render.com)
2. Sign up using your GitHub account
3. This will automatically connect your GitHub repositories

### 2.2 Create New Web Service
1. Click "New +" button in Render dashboard
2. Select "Web Service"
3. Connect your GitHub repository
4. Choose the repository you just created

### 2.3 Configure Deployment Settings
```yaml
Name: edusphere-learning-platform
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: python app.py
```

### 2.4 Set Environment Variables
In the Render dashboard, add these environment variables:

**Required:**
- `FLASK_ENV` = `production`
- `FLASK_DEBUG` = `false`
- `FLASK_SECRET_KEY` = `your-secure-secret-key-here`

**Optional (for AI features):**
- `GEMINI_API_KEY` = `your-gemini-api-key`

### 2.5 Deploy
1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Wait for the build to complete (usually 2-5 minutes)

---

## 🔑 Step 3: Get Gemini API Key (Optional)

### 3.1 Get API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### 3.2 Add to Render
1. Go to your Render service dashboard
2. Navigate to "Environment" tab
3. Add `GEMINI_API_KEY` with your API key value
4. Save changes (this will trigger a redeploy)

---

## 📱 Step 4: Access Your Application

### 4.1 Get Your URL
- Your app will be available at: `https://your-service-name.onrender.com`
- Render provides this URL in your service dashboard

### 4.2 Demo Credentials
Use these credentials to test your deployed application:

**Administrator:**
- Email: `admin@edusphere.com`
- Password: `admin123`

**Faculty:**
- Email: `teacher1@edusphere.com`
- Password: `teacher123`

**Student:**
- Email: `student1@edusphere.com`
- Password: `student123`

---

## 🔧 Step 5: Post-Deployment Configuration

### 5.1 Database Initialization
The application will automatically:
- Initialize the SQLite database
- Populate sample data (70+ courses)
- Create demo users
- Set up test series

### 5.2 Verify Features
Test these key features:
- [ ] User registration and login
- [ ] Role-based dashboards
- [ ] Course enrollment
- [ ] Test series functionality
- [ ] FLUX classroom (create and join sessions)
- [ ] AI chat (if API key configured)
- [ ] Live classes
- [ ] Admin panel

---

## 🚨 Troubleshooting

### Common Issues:

**Build Fails:**
- Check `requirements.txt` for correct dependencies
- Ensure Python version compatibility

**App Crashes:**
- Check Render logs in the dashboard
- Verify environment variables are set correctly

**Database Issues:**
- SQLite database is created automatically
- Check file permissions and disk space

**AI Features Not Working:**
- Verify `GEMINI_API_KEY` is set correctly
- Check API key validity and quotas

### Getting Help:
- Check Render logs for detailed error messages
- Review the application logs in Render dashboard
- Ensure all environment variables are properly configured

---

## 🔄 Step 6: Continuous Deployment

### 6.1 Automatic Deployments
Render automatically deploys when you push to your main branch:

```bash
# Make changes to your code
git add .
git commit -m "Update: description of changes"
git push origin main
```

### 6.2 Manual Deployments
You can also trigger manual deployments from the Render dashboard.

---

## 📊 Step 7: Monitoring & Maintenance

### 7.1 Monitor Performance
- Use Render's built-in monitoring
- Check application logs regularly
- Monitor resource usage

### 7.2 Database Backups
- Implement regular database backups
- Use the admin panel's backup feature
- Store backups securely

### 7.3 Security Updates
- Keep dependencies updated
- Monitor for security vulnerabilities
- Update API keys if compromised

---

## 🎉 Success!

Your EduSphere platform is now live and accessible to users worldwide!

**Next Steps:**
1. Share your deployment URL
2. Create user accounts for testing
3. Customize content for your specific needs
4. Monitor usage and performance
5. Gather user feedback for improvements

---

## 📞 Support

If you encounter any issues during deployment:

1. Check the troubleshooting section above
2. Review Render's documentation
3. Check GitHub repository for updates
4. Contact the development team

**Happy Learning! 🎓**