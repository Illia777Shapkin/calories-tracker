# 🍎 Calorie & Macro Tracker

A beautiful Streamlit app for tracking daily calories and macronutrients with AI-powered macro estimation using the Groq API.

## Features

✨ **User Authentication**
- Create accounts with secure password hashing
- Per-user database isolation
- Login/logout functionality

📊 **Meal Tracking**
- Log meals with date, time, and meal type (Breakfast, Lunch, Dinner, Snack, or Custom)
- Edit and delete meals
- Automatic time sorting

🤖 **AI Macro Estimation**
- Describe your meal and let AI estimate calories, protein, carbs, and fat
- Powered by Groq's `openai/gpt-oss-120b` model
- Manual override for precise tracking

📈 **Goal Tracking**
- Set custom goals for calories, protein, carbs, and fat
- Toggle which goals you want to track
- Real-time progress bars showing daily totals vs goals

💾 **Data Persistence**
- SQLite database for each user
- 3+ months of meal history
- All data stored locally

## Installation

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/calories-tracker.git
cd calories-tracker
```

2. **Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up Groq API key**
Create a `.streamlit/secrets.toml` file:
```toml
[groq]
api_key = "your_groq_api_key_here"
```

Get your free API key from [Groq Console](https://console.groq.com)

5. **Run the app**
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Deployment to Streamlit Cloud

### Prerequisites
- GitHub account with this repo pushed
- Groq API key

### Steps

1. **Push code to GitHub**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Go to Streamlit Cloud**
- Visit [share.streamlit.io](https://share.streamlit.io)
- Click "Create app"
- Select your GitHub repo and `app.py` as the main file

3. **Add Groq API Secret**
- In the Streamlit Cloud app settings, go to "Secrets"
- Add your Groq API key:
```toml
[groq]
api_key = "your_groq_api_key_here"
```

4. **Deploy**
- Click "Deploy" and wait for the app to build

Your app will be live at: `https://share.streamlit.io/YOUR_USERNAME/calories-tracker`

## Usage

### Create an Account
1. Click "Sign Up" on the login screen
2. Enter a username and password (min 6 characters)
3. Confirm your password and click "Sign Up"

### Log In
1. Enter your credentials on the "Login" tab
2. Click "Login"

### Log a Meal
1. Select the date
2. Choose meal type or enter a custom one
3. Enter the time (defaults to current time)
4. Describe what you ate (e.g., "80g oats with 250ml milk and 1 banana")
5. Click "🤖 Estimate" to use AI, or manually enter the macros
6. Click "Add meal"

### Edit or Delete Meals
- Use the ✏️ button to edit a meal
- Use the 🗑️ button to delete a meal

### Set Goals
- Use the sidebar to toggle which goals you want to track
- Set custom values for each macro

## Database Structure

### Global (users.db)
```sql
users
├── id (PK)
├── username (UNIQUE)
├── password_hash
└── created_at
```

### Per-User (user_{username}.db)
```sql
meals
├── id (PK)
├── date
├── time
├── meal_type
├── description
├── calories
├── protein
├── carbs
├── fat
└── created_at
```

## Technologies Used

- **Streamlit** - Web framework
- **SQLite** - Local database
- **Groq API** - AI macro estimation
- **Pandas** - Data manipulation
- **Python 3.12+** - Language

## Configuration

Edit `.streamlit/config.toml` to customize:
- Theme colors
- Font
- Error details visibility

## Troubleshooting

### "API key not found"
- Ensure `.streamlit/secrets.toml` exists with your Groq API key

### "Database is locked"
- Close other instances of the app

### AI not working
- Check your Groq API key is valid and has quota
- Ensure your meal description is detailed enough

## Privacy & Security

- Passwords are hashed with SHA256
- Each user's data is isolated in separate databases
- No data is sent to external servers (except Groq API for meal analysis)
- Databases are stored locally on Streamlit Cloud

## Future Enhancements

- [ ] Weekly/monthly summaries
- [ ] Favorite meals library
- [ ] Barcode scanning
- [ ] Export data as CSV
- [ ] Food photography recognition
- [ ] Meal recommendations
- [ ] Dark mode

## License

MIT License - feel free to use this for personal or commercial projects

## Contributing

Found a bug or have a feature request? Feel free to open an issue or pull request!

## Support

Need help? Check the [Streamlit documentation](https://docs.streamlit.io) or open an issue on GitHub.

---

Made with ❤️ using Streamlit and Groq AI
