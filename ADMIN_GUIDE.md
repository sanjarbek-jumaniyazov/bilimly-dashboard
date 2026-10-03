# 🎛️ Bilimly Admin Dashboard Guide

## Overview

The Bilimly Admin Dashboard provides comprehensive analytics and monitoring tools to track student activity, performance, and engagement with the exam prep system.

## Access Methods

### 1. **Web Dashboard** (Recommended)
Access the full-featured admin panel at:
```
https://dot-panels-pets-lucia.trycloudflare.com/admin.html
```

**Default Password:** `admin123` (configured in `.env` as `ADMIN_PASSWORD`)

### 2. **Telegram Bot Commands** (Quick Stats)
Send these commands to the bot to get quick statistics:

- `/admin` - Get overview dashboard with top 5 active users
- `/stats` - Get quick statistics summary
- `/help` - Get general help

**Important:** Admin commands only work if your Telegram ID is in the `ADMIN_IDS` list in `bot/handlers/admin.py`

## Web Dashboard Features

### 📊 Statistics Cards
At the top of the dashboard, you'll see key metrics:
- **Total Users** - All registered users
- **Onboarded** - Users who completed profile setup
- **Total Attempts** - Sum of all quiz attempts across all users

### 👥 Users Tab
View all users with their activity metrics:

| Column | Description |
|--------|-------------|
| **User** | Full name and @username |
| **Status** | Onboarded (setup complete) or Pending |
| **Course** | Academic year (1-4) |
| **Group** | Student group ID |
| **Attempts** | Total quiz submissions |
| **Accuracy** | Percentage of correct answers |
| **Themes** | Number of themes started |
| **Last Activity** | Date of last quiz attempt |

**Click any user row** to see detailed activity breakdown including:
- Time spent on the platform
- Performance by theme
- Detailed attempt history

### 📚 Subjects Tab
Popular themes and subject performance:

- **Subject Name** - Course name (e.g., "Economic Theory 1")
- **Theme Name** - Specific chapter/topic
- **Attempts** - Total quiz submissions for that theme
- **Accuracy** - Average correctness percentage

## API Endpoints

If you want to integrate with your own tools, use these API endpoints:

### Authentication
All admin endpoints require the `password` query parameter:
```
?password=admin123
```

### Endpoints

#### Get Statistics
```bash
GET /api/admin/stats?password=admin123
```
Returns:
```json
{
  "total_users": 100,
  "onboarded_users": 85,
  "total_attempts": 450
}
```

#### List All Users (Paginated)
```bash
GET /api/admin/users?password=admin123&limit=50&offset=0
```
Parameters:
- `limit` (1-500, default 100): Records per page
- `offset` (default 0): Starting record number

#### User Detail
```bash
GET /api/admin/users/{user_id}?password=admin123
```
Returns detailed user profile and activity breakdown

#### Subject/Theme Statistics
```bash
GET /api/admin/subjects?password=admin123
```
Returns list of themes sorted by popularity

## Changing Admin Password

To change the admin password:

1. Edit `.env` file
2. Find `ADMIN_PASSWORD=admin123`
3. Change to your desired password: `ADMIN_PASSWORD=your_new_password`
4. Restart the API server:
   ```bash
   pkill -f "uvicorn api.main:app"
   sleep 2
   cd /path/to/bot && nohup .venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8000 &
   ```

## Adding Admin Telegram Commands

To enable `/admin` and `/stats` commands for your Telegram ID:

1. Get your Telegram ID (send message to @userinfobot)
2. Edit `bot/handlers/admin.py`
3. Update the `ADMIN_IDS` list:
   ```python
   ADMIN_IDS = [6220653511, 123456789]  # Add your ID here
   ```
4. Restart the bot:
   ```bash
   pkill -f "bot.main"
   sleep 2
   cd /path/to/bot && nohup .venv/bin/python -m bot.main &
   ```

## Metrics Explained

### Accuracy
Percentage of quiz answers that were correct:
```
Accuracy = (Correct Answers / Total Answers) × 100%
```

### Themes Started
Number of unique themes (chapters) a student has attempted quizzes for.

### Best Score
Highest percentage achieved on any single theme quiz.

### Time Spent
Calculated from first quiz attempt to most recent activity for that user.

## Common Use Cases

### 📈 Track Engagement
1. Go to Users tab
2. Sort by "Last Activity" to find active students
3. Click a user to see detailed engagement metrics

### 🏆 Identify Top Performers
1. Sort the Users table by "Accuracy" (highest first)
2. Check their theme progress
3. Identify which topics are easiest/hardest

### 📊 Find Struggling Students
1. Look for users with <60% accuracy
2. Check which themes they're struggling with
3. Identify common problem areas

### 🎯 Monitor Popular Themes
1. Go to Subjects tab
2. See which themes have most attempts
3. Identify which topics students focus on most

## Data Privacy

The admin dashboard shows:
- ✅ User names and usernames
- ✅ Academic information (course year, group)
- ✅ Quiz performance metrics
- ❌ Does NOT show personal data beyond what's needed for learning analytics

## Troubleshooting

### Dashboard won't load
- Check if `https://dot-panels-pets-lucia.trycloudflare.com` is accessible
- Verify the tunnel is running: `ps aux | grep cloudflared`
- Check API server: `ps aux | grep uvicorn`

### Wrong password error
- Verify you're using the password from `.env` file
- Check for typos (passwords are case-sensitive)
- Restart the API server after changing password

### No users showing
- Check if API is running: `curl http://localhost:8000/api/admin/stats?password=admin123`
- Verify database has data: Check if `/data/bot.db` exists
- Run `seed_all()` to populate test data

### Can't access Telegram admin commands
- Verify your Telegram ID is in `ADMIN_IDS` list
- Restart the bot after adding your ID
- Test with `/admin` command

## Security Notes

⚠️ **Important Security Reminders:**

1. **Change Default Password** - Don't leave it as `admin123`
2. **Protect .env File** - Never commit to git or share
3. **Restrict Access** - Run admin dashboard only on secure networks
4. **Audit Logs** - No access logging is currently implemented
5. **HTTPS Only** - Always use https:// for remote access (tunnel provides this)

## Support

For issues or questions:
1. Check logs: `tail -100 /tmp/api.log`
2. Check bot logs: `tail -100 /tmp/bot.log`
3. Verify database exists: `ls -la /path/to/data/bot.db`
