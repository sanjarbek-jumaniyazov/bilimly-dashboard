# 🎛️ Bilimly Admin Dashboard

**Modern Analytics Dashboard for Bilimly Exam Prep Platform**

> Built for Vercel deployment with real-time updates, beautiful UI, and comprehensive analytics.

## 🚀 Quick Start

### Access Live Dashboard
```
https://dot-panels-pets-lucia.trycloudflare.com/dashboard.html
Password: admin123
```

### Features

✨ **Modern UI**
- Gradient design with smooth animations
- Responsive layout (desktop, tablet, mobile)
- Auto-refresh every 30 seconds
- Real-time status indicators

📊 **Analytics**
- User statistics (total, onboarded, engagement)
- User activity tracking (attempts, accuracy, last login)
- Popular themes/topics analysis
- Performance metrics per subject

🔄 **Real-time Updates**
- Auto-refresh data every 30 seconds
- Manual refresh button
- Countdown timer
- Last updated timestamp

👥 **User Management**
- Paginated user list (50 per page)
- Filter by onboarding status
- Track accuracy and attempts
- View theme progress

📈 **Theme Analytics**
- Popular topics by attempts
- Accuracy per theme
- Subject categorization
- Performance trends

## 📱 Deploy to Vercel

### Option 1: Direct Upload (Simple)

1. **Download Files**
   ```bash
   # Copy the dashboard.html file
   cp /Users/uzmacbook/UniStudy/telegram-exam-prep-bot/webapp/dashboard.html ~/bilimly-dashboard/index.html
   ```

2. **Create GitHub Repository**
   ```bash
   cd ~/bilimly-dashboard
   git init
   git add .
   git commit -m "Initial dashboard commit"
   git remote add origin https://github.com/YOUR_USERNAME/bilimly-dashboard.git
   git push -u origin main
   ```

3. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Configure environment variable:
     ```
     VITE_API_URL = https://dot-panels-pets-lucia.trycloudflare.com
     ```
   - Deploy!

### Option 2: Using Vercel CLI

```bash
npm install -g vercel

cd ~/bilimly-dashboard

# Deploy
vercel

# For production
vercel --prod
```

## 🔐 Configuration

### Environment Variables

When deploying to Vercel, set these environment variables:

```env
VITE_API_URL=https://your-api-url.com
VITE_ADMIN_PASSWORD=your_secure_password_here
```

### Updating API URL

Edit the `API_URL` in your deployed dashboard:

1. **In Vercel Dashboard:**
   - Project Settings → Environment Variables
   - Add: `VITE_API_URL`
   - Value: `https://your-tunnel-url.trycloudflare.com`

2. **Or update in JavaScript:**
   ```javascript
   const API_URL = process.env.VITE_API_URL || 'https://dot-panels-pets-lucia.trycloudflare.com';
   ```

## 🎨 Customization

### Change Admin Password

In `.env` (backend):
```
ADMIN_PASSWORD=your_new_password
```

Then restart API:
```bash
pkill -f "uvicorn api.main:app"
```

### Change Theme Colors

Edit `dashboard.html` CSS variables:
```css
:root {
    --primary: #6366f1;      /* Main color */
    --accent: #ec4899;       /* Accent color */
    --success: #10b981;      /* Success color */
    --danger: #ef4444;       /* Error color */
}
```

### Auto-Refresh Interval

Change line in `dashboard.html`:
```javascript
refreshTimer = setInterval(() => {
    loadAllData();
}, 30000);  // 30 seconds - change to desired interval (in milliseconds)
```

## 📊 Dashboard Tabs

### 👥 Users Tab
- Full user directory
- Onboarding status
- Academic year & group
- Performance metrics
- Activity timeline

### 📚 Popular Themes Tab
- Most-attempted topics
- Subject categorization
- Accuracy trends
- Engagement metrics

## 🔗 API Endpoints

The dashboard uses these API endpoints (all require `?password=admin123`):

```
GET /api/admin/stats              → Overall statistics
GET /api/admin/users              → Paginated user list
GET /api/admin/users/{id}         → User detail
GET /api/admin/subjects           → Theme/subject stats
```

## 🛠️ Local Development

### Run Locally
```bash
# Serve with Python
python3 -m http.server 8080

# Visit
http://localhost:8080/dashboard.html
```

### Edit & Refresh
1. Edit `dashboard.html`
2. Save
3. Refresh browser (Ctrl+R or Cmd+R)

## 📈 Performance Tips

### Optimize for Vercel
- Cache dashboard in browser
- Minimize API calls
- Use pagination for large datasets
- Auto-refresh at reasonable intervals (30-60s)

### Monitor Metrics
1. User engagement (login frequency)
2. Popular topics (by attempts)
3. Performance trends (accuracy over time)
4. Retention rate (active vs total users)

## 🐛 Troubleshooting

### Dashboard Won't Load
```bash
# Check API is working
curl https://your-api-url.com/api/admin/stats?password=admin123

# Check for CORS errors (browser console: F12)
```

### Wrong Password Error
- Verify password matches `.env` file
- Passwords are case-sensitive
- Restart API after changing password

### Auto-Refresh Not Working
- Check browser console for errors (F12)
- Verify API URL is correct
- Ensure password is still valid

### Data Not Updating
- Click "🔄 Refresh" button
- Check network tab in browser dev tools
- Verify API connectivity

## 📝 Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🔐 Security

⚠️ **Important:**
- Never commit `.env` with passwords to GitHub
- Use strong admin password (minimum 12 characters)
- Change password regularly
- Only access from secure networks
- Use HTTPS only (tunnel provides this)

## 📄 File Structure

```
dashboard/
├── dashboard.html           # Main dashboard app
├── index.html              # Entry point (rename from dashboard.html)
├── package.json            # Project metadata
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── README.md               # Documentation
└── vercel.json             # Vercel config
```

## 🚀 Deployment Checklist

- [ ] Clone/download dashboard files
- [ ] Create GitHub repository
- [ ] Push to GitHub
- [ ] Connect to Vercel
- [ ] Set environment variables
- [ ] Configure custom domain (optional)
- [ ] Test login & data loading
- [ ] Monitor deployment
- [ ] Update documentation

## 📞 Support

For issues:
1. Check browser console (F12)
2. Review API logs: `tail -100 /tmp/api.log`
3. Verify network connectivity
4. Test API directly with curl

## 📖 Related Documentation

- [Admin Guide](./ADMIN_GUIDE.md) - Full admin features
- [API Endpoints](./api/main.py) - API documentation
- [Database Schema](./bot/db.py) - Data model

## 📄 License

MIT License - See LICENSE file for details

---

**Last Updated:** 2026-10-03
**Dashboard Version:** 2.0
**Status:** Production Ready ✅
