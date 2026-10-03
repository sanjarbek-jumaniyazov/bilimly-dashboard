# ⚡ Quick Start Guide - Bilimly Dashboard

## 🎯 The Fastest Way to Deploy Your Dashboard

### ✅ What You Get
- **Beautiful Modern Dashboard** - gradient UI with smooth animations
- **Real-time Updates** - auto-refresh every 30 seconds
- **Complete Analytics** - users, themes, performance metrics
- **Mobile Responsive** - works on all devices
- **Production Ready** - deploy to Vercel in 5 minutes

---

## 🚀 5-Minute Setup

### 1. **Access Current Dashboard** (Right Now!)
```
🌐 URL: https://dot-panels-pets-lucia.trycloudflare.com/dashboard.html
🔑 Password: admin123
```

### 2. **Deploy to Vercel** (5 Minutes)

#### Copy-Paste Setup:
```bash
# Create directory
mkdir ~/bilimly-dashboard && cd ~/bilimly-dashboard

# Copy dashboard
cp ~/UniStudy/telegram-exam-prep-bot/webapp/dashboard.html index.html

# Initialize git
git init
echo "node_modules/" > .gitignore
echo ".env" >> .gitignore

# Create package.json
cat > package.json << 'EOF'
{
  "name": "bilimly-dashboard",
  "version": "2.0.0",
  "description": "Bilimly Analytics Dashboard",
  "private": true,
  "scripts": {
    "dev": "python3 -m http.server 3000",
    "build": "echo 'Static site'",
    "start": "python3 -m http.server 3000"
  }
}
EOF

# Create environment template
cat > .env.example << 'EOF'
VITE_API_URL=https://dot-panels-pets-lucia.trycloudflare.com
VITE_ADMIN_PASSWORD=admin123
EOF

# Commit
git add .
git commit -m "🎛️ Bilimly Dashboard - Initial commit"

# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/bilimly-dashboard.git
git branch -M main
git push -u origin main
```

#### Deploy:
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repo
4. Add Environment Variable:
   - **Key:** `VITE_API_URL`
   - **Value:** `https://dot-panels-pets-lucia.trycloudflare.com`
5. Click "Deploy" ✅

**Done!** Your dashboard is live! 🎉

---

## 📊 What's in the Dashboard?

### 👥 Users Tab
- See all registered users
- Track who's active (onboarded)
- View quiz attempts per user
- Check accuracy % (how many questions they got right)
- See which themes they're studying
- Last activity date

### 📚 Popular Themes Tab
- Most-attempted topics
- Subject categorization
- Success rate per theme
- Student engagement levels

### 📈 Statistics Cards
- **Total Users** - Everyone who started the bot
- **Onboarded** - Users who completed profile setup
- **Total Attempts** - Sum of all quiz submissions

---

## 🔑 Changing Admin Password

### Step 1: Update Backend
Edit `.env` file (on your server):
```
ADMIN_PASSWORD=your_new_super_secure_password
```

### Step 2: Restart API
```bash
pkill -f "uvicorn api.main:app"
cd ~/UniStudy/telegram-exam-prep-bot
nohup .venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8000 &
```

### Step 3: Update Vercel
In Vercel Dashboard → Settings → Environment Variables:
- Update `VITE_API_URL` (if API URL changed)
- Optionally add `VITE_ADMIN_PASSWORD` (but usually just login with new password)

---

## 🎨 Customizing the Dashboard

### Change Colors
Edit `index.html` in your repo:
```css
:root {
    --primary: #6366f1;      /* Purple - main accent */
    --accent: #ec4899;       /* Pink - secondary */
    --success: #10b981;      /* Green - success */
    --danger: #ef4444;       /* Red - errors */
}
```

### Change Auto-Refresh Rate
Find this line in `index.html`:
```javascript
refreshTimer = setInterval(() => {
    loadAllData();
}, 30000);  // 30000ms = 30 seconds
```

Change `30000` to:
- `10000` for 10 seconds
- `60000` for 1 minute
- `300000` for 5 minutes

### Add Your Branding
Replace "Bilimly" text in HTML:
```html
<h1>📊 Bilimly</h1>  <!-- Change this -->
```

---

## 📱 Testing Locally

```bash
# Serve locally
cd ~/bilimly-dashboard
python3 -m http.server 8080

# Visit
http://localhost:8080
```

---

## 🆘 Common Issues & Fixes

### "Invalid password or API unreachable"
```bash
# Check API is running
curl https://dot-panels-pets-lucia.trycloudflare.com/api/admin/stats?password=admin123

# Check password matches .env file
cat ~/UniStudy/telegram-exam-prep-bot/.env | grep ADMIN_PASSWORD
```

### "Data won't load"
1. Check browser console: Press `F12`
2. Look for error messages
3. Verify API URL in Vercel environment variables
4. Refresh page: `Ctrl+R` (or `Cmd+R` Mac)

### "Dashboard shows blank"
1. Check API is accessible: `curl https://your-api.com/api/admin/stats?password=xxx`
2. Wait 30 seconds for auto-refresh
3. Click "🔄 Refresh" button manually
4. Clear browser cache: `Ctrl+Shift+Delete`

### "Password not working"
1. Make sure you typed it correctly (case-sensitive)
2. Check `.env` file for typos
3. Restart API server
4. Wait 30 seconds
5. Try again

---

## 📈 Monitoring Tips

### Track Student Engagement
1. Open "👥 Users" tab
2. Look for users with many attempts
3. Check their accuracy %
4. See which themes they study most

### Find Popular Topics
1. Open "📚 Popular Themes" tab
2. See which themes have most attempts
3. Higher attempts = more students studying it
4. Higher accuracy = easier topic

### Identify Struggling Students
1. Sort users by accuracy (lowest first)
2. Click on low-accuracy users
3. See which themes they're struggling with
4. Note common problem areas

---

## 🔐 Security Checklist

- [ ] Changed admin password from `admin123`
- [ ] Never committed `.env` to GitHub
- [ ] Using HTTPS only
- [ ] Set strong environment variables in Vercel
- [ ] Limited API access (only to admin endpoints)
- [ ] Regularly monitor who has access

---

## 📚 Full Documentation

For detailed information, see:
- [DASHBOARD_README.md](./DASHBOARD_README.md) - Full features
- [GITHUB_SETUP.md](./GITHUB_SETUP.md) - Deployment steps
- [ADMIN_GUIDE.md](./ADMIN_GUIDE.md) - Admin features

---

## 💬 Quick Reference

| What | Where | How |
|------|-------|-----|
| **View Dashboard** | Browser | `https://your-vercel-url.com` |
| **Change Password** | Edit `.env` | `ADMIN_PASSWORD=...` |
| **Update API URL** | Vercel Settings | Environment Variables → `VITE_API_URL` |
| **Redeploy** | Git push | `git push origin main` |
| **Check Status** | Vercel Dashboard | Deployments tab |
| **View Logs** | Vercel Dashboard | Deployments → Logs |
| **Change Theme Colors** | Edit `index.html` | CSS `:root` variables |
| **Auto-refresh Rate** | Edit `index.html` | `setInterval` in JavaScript |

---

## 🎉 You're Ready!

Your modern admin dashboard is now:
- ✅ Running locally
- ✅ Deployed on Vercel
- ✅ Auto-refreshing with real data
- ✅ Beautiful and responsive
- ✅ Production ready

**Start analyzing! 📊**

---

**Dashboard Version:** 2.0  
**Last Updated:** 2026-10-03  
**Status:** ✅ Production Ready
