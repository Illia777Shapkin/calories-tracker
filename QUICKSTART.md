# Quick Start Commands

## Local Development Setup

```bash
# Navigate to project
cd "/Users/nicksimon/PycharmExos /pythonProject2/Calories tracker"

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Get Groq API key from https://console.groq.com
# Create .streamlit/secrets.toml with:
# [groq]
# api_key = "your_key_here"

# Run the app
streamlit run app.py
```

The app opens at: http://localhost:8501

---

## Deploy to GitHub & Streamlit Cloud

```bash
# 1. Create repo on GitHub: https://github.com/new
#    (make it PUBLIC, name it "calories-tracker")

# 2. Push your code
cd "/Users/nicksimon/PycharmExos /pythonProject2/Calories tracker"

git remote add origin https://github.com/YOUR_USERNAME/calories-tracker.git
git branch -M main
git push -u origin main

# 3. Go to https://share.streamlit.io
#    - Click "Create app"
#    - Select your repo
#    - Main file: app.py
#    - Click Deploy

# 4. Once deployed, add your Groq API key in Streamlit Cloud Secrets
#    Menu → Settings → Secrets → Add [groq] api_key

# Done! Your app is live at:
# https://share.streamlit.io/YOUR_USERNAME/calories-tracker
```

---

## File Structure

```
calories-tracker/
├── app.py                    # Main Streamlit app
├── requirements.txt          # Python dependencies
├── README.md                 # User documentation
├── DEPLOYMENT.md             # Detailed deployment guide
├── .gitignore               # Git ignore rules
├── .streamlit/
│   ├── config.toml          # Streamlit configuration
│   └── secrets.toml         # API keys (not committed)
└── users.db                 # Global users database (local only)
    user_*.db                # Per-user meal databases (local only)
```

---

## Key Features Ready to Deploy

✅ User authentication with password hashing
✅ Per-user data isolation
✅ SQLite database persistence
✅ AI macro estimation with Groq API
✅ Meal CRUD operations
✅ Goal tracking with progress bars
✅ Beautiful Streamlit UI
✅ All dependencies in requirements.txt

---

## Environment Variable Notes

- `.env` file is optional (used for local testing)
- `.streamlit/secrets.toml` is required for Groq API (add in Streamlit Cloud dashboard)
- Never commit secrets to GitHub (protected by `.gitignore`)

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Run `pip install -r requirements.txt` |
| Groq API error | Add API key to `.streamlit/secrets.toml` |
| Database locked | Close other instances of the app |
| "Value above max_value" | Already fixed! Max values now dynamic |
| App won't deploy | Check GitHub repo is PUBLIC |

---

## Next Steps

1. Create GitHub repo at https://github.com/new
2. Push code with `git push`
3. Deploy on https://share.streamlit.io
4. Share your live app link!

For detailed instructions, see `DEPLOYMENT.md`
