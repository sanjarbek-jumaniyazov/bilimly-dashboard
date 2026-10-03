# 🚀 GitHub & Vercel Deployment Guide

## Step-by-Step Setup

### Step 1: Prepare Dashboard Files

```bash
# Create a new directory for the dashboard repo
mkdir ~/bilimly-dashboard
cd ~/bilimly-dashboard

# Copy the dashboard HTML
cp ~/UniStudy/telegram-exam-prep-bot/webapp/dashboard.html index.html
```

### Step 2: Create Required Files

Create `.gitignore`:
```
node_modules/
.env
.env.local
.env.*.local
*.log
.DS_Store
.vscode/
.idea/
dist/
build/
.vercel/
```

Create `vercel.json`:
```json
{
  "env": [
    {
      "key": "VITE_API_URL",
      "value": "https://dot-panels-pets-lucia.trycloudflare.com"
    }
  ],
  "builds": [
    {
      "src": "index.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

Create `package.json`:
```json
{
  "name": "bilimly-dashboard",
  "version": "2.0.0",
  "description": "Modern analytics dashboard for Bilimly exam prep platform",
  "private": true,
  "scripts": {
    "dev": "python3 -m http.server 3000",
    "build": "echo 'Static site - no build needed'",
    "start": "python3 -m http.server 3000"
  }
}
```

Create `.env.example`:
```
VITE_API_URL=https://your-api-url.trycloudflare.com
VITE_ADMIN_PASSWORD=
```

### Step 3: Initialize Git Repository

```bash
# Initialize git
git init

# Add all files
git add .
git commit -m "🚀 Initial dashboard commit - production ready"

# Create main branch
git branch -M main
```

### Step 4: Push to GitHub

```bash
# Create new repository at github.com

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/bilimly-dashboard.git

# Push
git push -u origin main
```

### Step 5: Deploy to Vercel

**Option A: Using Vercel Website (Easiest)**
1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click "New Project"
4. Select your `bilimly-dashboard` repository
5. Click "Import"
6. In "Environment Variables" section, add:
   - Name: `VITE_API_URL`
   - Value: `https://dot-panels-pets-lucia.trycloudflare.com`
7. Click "Deploy"

**Option B: Using Vercel CLI**
```bash
npm install -g vercel

# Deploy to staging
vercel

# Deploy to production
vercel --prod

# Set environment variables
vercel env add VITE_API_URL
# Paste: https://dot-panels-pets-lucia.trycloudflare.com
```

### Step 6: Configure Custom Domain (Optional)

In Vercel Dashboard:
1. Go to Project Settings
2. Domains
3. Add custom domain: `dashboard.yourdomain.com`
4. Follow DNS setup instructions

## 📋 File Structure for GitHub

```
bilimly-dashboard/
├── index.html              # Main dashboard (from dashboard.html)
├── package.json            # Project metadata
├── vercel.json             # Vercel configuration
├── .gitignore              # Git ignore rules
├── .env.example            # Environment template
├── README.md               # Dashboard documentation
└── DEPLOYMENT.md           # Deployment guide
```

## 🔄 Updating the Dashboard

### Push Code Changes

```bash
# Make edits to index.html
# Then commit and push:

git add index.html
git commit -m "✨ Update dashboard features"
git push origin main

# Vercel will auto-deploy within 1 minute
```

### Update API URL

If your API URL changes:

```bash
# In Vercel Dashboard:
# Settings → Environment Variables → VITE_API_URL → Update value

# Or using CLI:
vercel env add VITE_API_URL
```

## 🔐 Environment Variables in Vercel

### Setting Up

1. **Web Interface:**
   - Project Settings → Environment Variables
   - Click "Add"
   - Key: `VITE_API_URL`
   - Value: `https://your-tunnel-url.trycloudflare.com`
   - Select "Production" and "Development"
   - Save

2. **CLI:**
   ```bash
   vercel env add VITE_API_URL
   # Enter: https://dot-panels-pets-lucia.trycloudflare.com
   ```

### Using in Code

```javascript
const API_URL = process.env.VITE_API_URL || 'https://localhost:8000';
```

## 📊 Monitoring Deployments

### View Deployment Status
```bash
vercel deployments
```

### View Recent Deployments
1. Go to Vercel Dashboard
2. Select project
3. "Deployments" tab shows:
   - Deployment status
   - Build logs
   - Timestamps
   - Git commit info

### Monitor Performance
- Vercel provides analytics
- See pageload times
- Monitor uptime
- Track API calls

## 🚀 CI/CD with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Vercel

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Vercel
        uses: vercel/action@master
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

Setup secrets in GitHub:
1. Settings → Secrets and Variables → Actions
2. Add:
   - `VERCEL_TOKEN` (from vercel.com/account/tokens)
   - `VERCEL_ORG_ID` (from Vercel settings)
   - `VERCEL_PROJECT_ID` (from Vercel project)

## 🆘 Troubleshooting

### Deployment Failed
```bash
# Check build logs
vercel logs [project-id]

# Redeploy
vercel --prod
```

### Cannot Connect to API
- Verify `VITE_API_URL` environment variable is set
- Check API is running: `curl https://your-api-url/api/admin/stats?password=xxx`
- Verify CORS is enabled on API
- Check browser console for errors

### Changes Not Showing
```bash
# Hard refresh browser
Ctrl+Shift+R (Windows)
Cmd+Shift+R (Mac)

# Or clear Vercel cache
vercel env rm [env-var-name]
vercel env add [env-var-name]
```

## 📈 Best Practices

✅ **Do:**
- Use `.env.example` as template
- Keep secrets in environment variables
- Enable branch protection
- Use meaningful commit messages
- Test locally before pushing
- Monitor deployment logs

❌ **Don't:**
- Commit `.env` file
- Hardcode API URLs
- Store passwords in code
- Push to main without testing
- Use weak passwords
- Expose sensitive data in logs

## 📞 Support

### Vercel Docs
- [Vercel Documentation](https://vercel.com/docs)
- [Environment Variables](https://vercel.com/docs/projects/environment-variables)
- [Deployments](https://vercel.com/docs/deployments)

### GitHub Docs
- [GitHub Help](https://docs.github.com)
- [Git Commands](https://git-scm.com/doc)

### Troubleshooting
1. Check Vercel logs
2. Check GitHub Actions (if enabled)
3. Review API server logs
4. Test with curl directly

## 🎉 You're Done!

Your dashboard should now be live at:
```
https://[your-dashboard-name].vercel.app
```

Login with your admin password and enjoy the analytics! 📊

---

**Next Steps:**
- [ ] Create GitHub repository
- [ ] Push dashboard files
- [ ] Connect to Vercel
- [ ] Set environment variables
- [ ] Test dashboard
- [ ] Configure custom domain
- [ ] Share with team
