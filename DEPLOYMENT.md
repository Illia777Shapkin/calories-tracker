# Deployment Guide for Calories Tracker

## Step-by-Step Guide to Deploy to Streamlit Cloud

### Prerequisites
✅ You need:
1. A GitHub account
2. A Groq API key (free from https://console.groq.com)
3. The app code ready (you have it!)

---

## Phase 1: Create GitHub Repository

### 1. Create a New Repository on GitHub

1. Go to https://github.com/new
2. Fill in:
   - **Repository name**: `calories-tracker` (or any name you prefer)
   - **Description**: "AI-powered calorie and macro tracker with Streamlit"
   - **Visibility**: Public (required for free Streamlit Cloud deployment)
   - **Add .gitignore**: Python (optional, we already have one)
   - **Add README**: No (we already have one)

3. Click **Create repository**

### 2. Push Your Code to GitHub

After creating the repo, GitHub will show you commands. Run these in your terminal:

```bash
cd "/Users/nicksimon/PycharmExos /pythonProject2/Calories tracker"

# Set the remote URL (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/calories-tracker.git

# Rename branch to main if needed
git branch -M main

# Push the code
git push -u origin main
```

**Note**: You'll be prompted for authentication. Use a Personal Access Token:
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Give it "repo" permission and copy the token
4. When asked for password in terminal, paste the token

---

## Phase 2: Deploy to Streamlit Cloud

### 1. Connect to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click **Create app** (you may need to sign in with GitHub)
3. Grant Streamlit permission to access your GitHub repositories

### 2. Deploy the App

1. **Repository**: Select `YOUR_USERNAME/calories-tracker`
2. **Branch**: `main`
3. **Main file path**: `app.py`
4. Click **Deploy**

Streamlit will install dependencies and launch your app. This may take 1-2 minutes. ⏳

### 3. Add Groq API Secret

⚠️ **Important**: Never commit your API key to GitHub!

1. Once deployed, click the **three dots menu** (top right)
2. Select **Settings** → **Secrets**
3. Add your Groq API key in this format:

```toml
[groq]
api_key = "gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

4. Save and the app will automatically reload

---

## Phase 3: Launch & Share

Your app is now live! 🎉

- **URL**: `https://share.streamlit.io/YOUR_USERNAME/calories-tracker`
- Share this link with anyone to use the app
- Each user will have their own account and database

---

## Troubleshooting

### App won't deploy
- Check `.gitignore` - make sure it doesn't exclude important files
- Check `requirements.txt` - all dependencies listed?
- Check logs in Streamlit Cloud dashboard

### "ModuleNotFoundError"
- Missing dependency in `requirements.txt`
- Add it: `pip freeze | grep package_name >> requirements.txt`
- Commit and push the change

### "Groq API error"
- Verify API key is correct in Secrets
- Check API key has quota at https://console.groq.com
- Check app has internet connection (it should on Streamlit Cloud)

### Database errors
- First login creates the database automatically ✅
- Don't commit `.db` files (in `.gitignore`) ✅

---

## Future Updates

To update your app:

```bash
cd "/Users/nicksimon/PycharmExos /pythonProject2/Calories tracker"

# Make your changes
# ...

git add .
git commit -m "Description of changes"
git push origin main
```

Streamlit Cloud will automatically redeploy! 🚀

---

## Optional Customizations

### Change App Name/Icon
Edit `.streamlit/config.toml`:
```toml
[client]
showMenuItems = true

[browser]
favicon = "🍎"
```

### Change Theme Colors
Already configured in `config.toml`, but you can customize:
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
```

### Add Custom Domain (Premium)
With Streamlit Cloud Pro, add your own domain name

---

## Need Help?

- Streamlit Docs: https://docs.streamlit.io
- Groq Docs: https://console.groq.com/docs
- GitHub Help: https://docs.github.com

Happy deploying! 🚀
