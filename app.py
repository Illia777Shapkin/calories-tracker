import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import sqlite3
import os
import json
import hashlib
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file in the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

st.set_page_config(page_title="Calorie & Macro Tracker", layout="wide")

# Database setup
USERS_DB = "users.db"  # Global users database
DB_PATH_TEMPLATE = "user_{}.db"  # Per-user database template


def hash_password(password: str) -> str:
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def init_users_db():
    """Initialize the users database"""
    conn = sqlite3.connect(USERS_DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def create_user(username: str, password: str) -> bool:
    """Create a new user. Returns True if successful, False if username exists"""
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        password_hash = hash_password(password)
        c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def check_user_login(username: str, password: str) -> bool:
    """Check if username and password are correct"""
    conn = sqlite3.connect(USERS_DB)
    c = conn.cursor()
    password_hash = hash_password(password)
    c.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password_hash))
    result = c.fetchone()
    conn.close()
    return result is not None


def get_user_db_path(username: str) -> str:
    """Get the database path for a specific user"""
    return DB_PATH_TEMPLATE.format(username)


def init_database(username: str):
    """Initialize SQLite database for a specific user"""
    db_path = get_user_db_path(username)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            description TEXT NOT NULL,
            calories REAL NOT NULL,
            protein REAL NOT NULL,
            carbs REAL NOT NULL,
            fat REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def load_meals_from_db(username: str):
    """Load all meals from database into session state"""
    db_path = get_user_db_path(username)
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM meals ORDER BY date DESC, time DESC", conn)
    conn.close()
    return df


def save_meal_to_db(username: str, entry):
    """Save a meal to the database"""
    db_path = get_user_db_path(username)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        INSERT INTO meals (date, time, meal_type, description, calories, protein, carbs, fat)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (entry['date'], entry['time'], entry['meal_type'], entry['description'],
          entry['calories'], entry['protein'], entry['carbs'], entry['fat']))
    conn.commit()
    conn.close()

def delete_meal_from_db(username, meal_id):
    """Delete a meal from the database"""
    db_path = get_user_db_path(username)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('DELETE FROM meals WHERE id = ?', (meal_id,))
    conn.commit()
    conn.close()

def update_meal_in_db(username, meal_id, updated_entry):
    """Update a meal in the database"""
    db_path = get_user_db_path(username)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        UPDATE meals 
        SET date = ?, time = ?, meal_type = ?, description = ?, calories = ?, protein = ?, carbs = ?, fat = ?
        WHERE id = ?
    ''', (updated_entry['date'], updated_entry['time'], updated_entry['meal_type'], 
          updated_entry['description'], updated_entry['calories'], updated_entry['protein'],
          updated_entry['carbs'], updated_entry['fat'], meal_id))
    conn.commit()
    conn.close()

# Initialize users database (global, runs once)
init_users_db()

# Initialize logged_in_user session state if not already done
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# Initialize auth mode session state if not already done
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"  # "login" or "signup"

def show_login_signup_ui():
    """Show login/signup UI for unauthenticated users"""
    st.title("🍎 Calories Tracker")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("---")
        
        # Toggle between login and signup
        login_tab, signup_tab = st.tabs(["Login", "Sign Up"])
        
        with login_tab:
            st.subheader("Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", use_container_width=True):
                if username and password:
                    if check_user_login(username, password):
                        st.session_state.logged_in_user = username
                        st.success(f"✅ Welcome, {username}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("Please enter username and password")
        
        with signup_tab:
            st.subheader("Create Account")
            new_username = st.text_input("Username", key="signup_username")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
            
            if st.button("Sign Up", use_container_width=True):
                if not new_username or not new_password:
                    st.warning("Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("Passwords don't match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    if create_user(new_username, new_password):
                        st.success("✅ Account created! Please log in.")
                    else:
                        st.error("❌ Username already exists")
        
        st.markdown("---")

# Show login/signup if user not authenticated
if st.session_state.logged_in_user is None:
    show_login_signup_ui()
    st.stop()

# User is authenticated - initialize their database and session state
init_database(st.session_state.logged_in_user)

def init_session_state():
    if "entries" not in st.session_state:
        # Load from database
        df = load_meals_from_db(st.session_state.logged_in_user)
        st.session_state.entries = df if not df.empty else pd.DataFrame(
            columns=[
                "id",
                "date",
                "time",
                "meal_type",
                "description",
                "calories",
                "protein",
                "carbs",
                "fat",
                "created_at",
            ]
        )


def add_entry(entry):
    # Save to database
    save_meal_to_db(st.session_state.logged_in_user, entry)
    # Reload from database
    st.session_state.entries = load_meals_from_db(st.session_state.logged_in_user)


def get_entries_for_date(target_date: date):
    df = st.session_state.entries
    if df.empty:
        return df

    # dates are stored as ISO strings "YYYY-MM-DD"
    return df[df["date"] == target_date.isoformat()]


def delete_entry(index):
    """Delete an entry by index"""
    if 'id' in st.session_state.entries.columns:
        meal_id = st.session_state.entries.loc[index, 'id']
        delete_meal_from_db(st.session_state.logged_in_user, meal_id)
        st.session_state.entries = load_meals_from_db(st.session_state.logged_in_user)
    else:
        st.session_state.entries = st.session_state.entries.drop(index).reset_index(drop=True)


def update_entry(index, updated_entry):
    """Update an entry by index"""
    if 'id' in st.session_state.entries.columns:
        meal_id = st.session_state.entries.loc[index, 'id']
        # Remove id from updated_entry to avoid SQL issues
        updated_entry_copy = updated_entry.copy()
        if 'id' in updated_entry_copy:
            del updated_entry_copy['id']
        if 'created_at' in updated_entry_copy:
            del updated_entry_copy['created_at']
        update_meal_in_db(st.session_state.logged_in_user, meal_id, updated_entry_copy)
        st.session_state.entries = load_meals_from_db(st.session_state.logged_in_user)
    else:
        st.session_state.entries.loc[index] = updated_entry


def calculate_totals(df: pd.DataFrame):
    if df.empty:
        return {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    totals = df[["calories", "protein", "carbs", "fat"]].sum()
    return totals.to_dict()


def get_llm_client():
    """
    Returns a Groq client using the secret API key from .streamlit/secrets.toml
    """
    api_key = st.secrets["groq"]["api_key"]
    client = Groq(api_key=api_key)
    return client


# Placeholder for future AI integration
def ai_parse_meal(text: str):
    """
    Use Groq API to estimate macros from meal description.
    API key is loaded from .streamlit/secrets.toml
    """
    try:
        client = get_llm_client()
        
        prompt = f"""Your job is to analyze a meal description and calculate nutritional values with maximum consistency and mathematical accuracy.

You must always produce the SAME output for the SAME input.

Respond with ONLY valid JSON. Do not output explanations, text, markdown, or comments.

STRICT CALCULATION PROCESS:

1. Parse the meal text and extract ALL ingredients with quantities.
2. Do NOT ignore any ingredient mentioned in the meal.
3. Convert quantities into the reference unit before calculation.
4. Calculate nutrition values using proportional scaling.
5. Sum the values of all ingredients to produce totals.
6. Verify that totals equal the sum of ingredient values.

VALIDATION RULES:

- If an ingredient appears in the meal but is missing in the calculation, the response is invalid.
- If totals do not match the sum of ingredients, recompute before responding.
- If quantity is missing, assume a standard portion but apply the SAME assumption consistently.
- Never guess different values for the same ingredient in the same context.

REALISM CHECK:

Before returning JSON verify that:
- Calories are realistic for the listed foods.
- Totals match ingredient sums.
- No ingredient was skipped.

If any rule fails, recompute before responding.

Output must be deterministic and mathematically correct.

MEAL: {text}

RESPOND WITH THIS JSON FORMAT ONLY - NO OTHER TEXT:
{{"calories": <number>, "protein": <number>, "carbs": <number>, "fat": <number>, "description": "<simple text>"}}"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Debug: check if response is empty
        if not result_text:
            raise ValueError("AI returned empty response")
        
        # Try to parse JSON - if it fails, try to extract and fix it
        import re
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            # Try to extract JSON from the response if it has extra text
            # Look for JSON object - use a more robust pattern that handles newlines
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                except json.JSONDecodeError as e:
                    # If still fails, try to clean up the JSON
                    dirty_json = json_match.group()
                    # Try removing newlines and extra spaces
                    clean_json = dirty_json.replace('\n', ' ').replace('\r', '')
                    try:
                        result = json.loads(clean_json)
                    except json.JSONDecodeError:
                        # Last resort: try to build JSON manually from the response
                        # Look for any numbers in quotes
                        cal_match = re.search(r'"?calories"?\s*:\s*(\d+)', result_text)
                        prot_match = re.search(r'"?protein"?\s*:\s*(\d+)', result_text)
                        carb_match = re.search(r'"?carbs"?\s*:\s*(\d+)', result_text)
                        fat_match = re.search(r'"?fat"?\s*:\s*(\d+)', result_text)
                        
                        if cal_match and prot_match and carb_match and fat_match:
                            result = {
                                "calories": int(cal_match.group(1)),
                                "protein": int(prot_match.group(1)),
                                "carbs": int(carb_match.group(1)),
                                "fat": int(fat_match.group(1)),
                                "description": text.strip()
                            }
                        else:
                            # If we still can't parse, use simple estimation based on meal type
                            raise ValueError(f"Could not parse AI response. Response was: {result_text[:300]}")
            else:
                # No JSON found at all - fallback to simple estimation
                raise ValueError(f"Could not find valid JSON in response: {result_text[:300]}")
        
        return {
            "calories": int(result.get("calories", 0)),
            "protein": int(result.get("protein", 0)),
            "carbs": int(result.get("carbs", 0)),
            "fat": int(result.get("fat", 0)),
            "normalized_description": result.get("description", text.strip()),
        }
    except Exception as e:
        return {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "normalized_description": text.strip(),
            "error": f"AI estimation failed: {str(e)}"
        }


# ---------- App UI ----------

init_session_state()

# Top bar with title and logout
col_title, col_logout = st.columns([5, 1])
with col_title:
    st.title("🍽️ Calorie & Macro Tracker")
with col_logout:
    st.markdown("")  # spacing
    st.markdown("")  # spacing
    if st.button("🚪 Logout", help="Logout from current account"):
        st.session_state.logged_in_user = None
        st.success("✅ Logged out successfully!")
        st.rerun()

st.markdown(f"*Logged in as:* **{st.session_state.logged_in_user}**")
st.markdown("---")

# Sidebar: goals
st.sidebar.header("Daily goals")

default_cal_goal = 3000
default_protein_goal = 140
default_carbs_goal = 350
default_fat_goal = 70

# Initialize session state for goal toggles if not already done
if "goal_toggles" not in st.session_state:
    st.session_state.goal_toggles = {
        "calories": True,
        "protein": True,
        "carbs": True,
        "fat": True,
    }

st.sidebar.markdown("#### Which goals do you want to track?")
st.sidebar.markdown("_Note: All macros are tracked and displayed. These toggles only affect goal progress._")
st.session_state.goal_toggles["calories"] = st.sidebar.checkbox("Calories goal", value=st.session_state.goal_toggles["calories"])
st.session_state.goal_toggles["protein"] = st.sidebar.checkbox("Protein goal", value=st.session_state.goal_toggles["protein"])
st.session_state.goal_toggles["carbs"] = st.sidebar.checkbox("Carbs goal", value=st.session_state.goal_toggles["carbs"])
st.session_state.goal_toggles["fat"] = st.sidebar.checkbox("Fat goal", value=st.session_state.goal_toggles["fat"])

st.sidebar.markdown("#### Set your goals")

calorie_goal = st.sidebar.number_input(
    "Calories (kcal)", min_value=0, max_value=10000, value=default_cal_goal, step=50,
    disabled=not st.session_state.goal_toggles["calories"]
)
protein_goal = st.sidebar.number_input(
    "Protein (g)", min_value=0, max_value=500, value=default_protein_goal, step=5,
    disabled=not st.session_state.goal_toggles["protein"]
)
carbs_goal = st.sidebar.number_input(
    "Carbs (g)", min_value=0, max_value=1000, value=default_carbs_goal, step=10,
    disabled=not st.session_state.goal_toggles["carbs"]
)
fat_goal = st.sidebar.number_input(
    "Fat (g)", min_value=0, max_value=300, value=default_fat_goal, step=5,
    disabled=not st.session_state.goal_toggles["fat"]
)

goals = {
    "calories": calorie_goal if st.session_state.goal_toggles["calories"] else None,
    "protein": protein_goal if st.session_state.goal_toggles["protein"] else None,
    "carbs": carbs_goal if st.session_state.goal_toggles["carbs"] else None,
    "fat": fat_goal if st.session_state.goal_toggles["fat"] else None,
}

# Initialize session state for meal type if not already done
if "meal_type_custom" not in st.session_state:
    st.session_state.meal_type_custom = ""

if "meal_time" not in st.session_state:
    st.session_state.meal_time = datetime.now().time()

# Main layout: two columns (left: input/chat, right: table & totals)
left_col, right_col = st.columns([1, 1.2])

# ----- Left: date selection & add meal -----
with left_col:
    st.subheader("Log your meals")

    selected_date = st.date_input("Select date", value=date.today())

    st.markdown("#### Add a meal")
    
    # Meal type selection OUTSIDE the form
    meal_type_option = st.selectbox(
        "Meal type",
        options=["Breakfast", "Lunch", "Dinner", "Snack", "Custom"],
        index=0
    )
    
    if meal_type_option == "Custom":
        st.session_state.meal_type_custom = st.text_input(
            "Enter custom meal type",
            value=st.session_state.meal_type_custom,
            placeholder="e.g., Pre-workout, Post-workout, Dessert"
        )
        final_meal_type = st.session_state.meal_type_custom
    else:
        st.session_state.meal_type_custom = ""
        final_meal_type = meal_type_option

    # Time input OUTSIDE the form
    st.session_state.meal_time = st.time_input("Time of meal", value=st.session_state.meal_time)

    # Initialize AI session state for macro inputs
    if "ai_cal" not in st.session_state:
        st.session_state.ai_cal = 0
    if "ai_protein" not in st.session_state:
        st.session_state.ai_protein = 0
    if "ai_carbs" not in st.session_state:
        st.session_state.ai_carbs = 0
    if "ai_fat" not in st.session_state:
        st.session_state.ai_fat = 0
    if "meal_description" not in st.session_state:
        st.session_state.meal_description = ""

    # SINGLE unified meal description input
    st.markdown("#### What did you eat?")
    st.session_state.meal_description = st.text_area(
        "Describe your meal",
        placeholder="Example: 80g oats with 250ml whole milk and 1 banana",
        height=120,
        value=st.session_state.meal_description,
        key="meal_desc_unified"
    )

    # AI estimation section
    st.markdown("#### 🤖 Use AI to estimate macros (optional)")
    col_ai_button, col_manual = st.columns([1, 3])
    
    with col_ai_button:
        if st.button("🤖 Estimate", help="Use AI to estimate calories and macros", use_container_width=True):
            if st.session_state.meal_description.strip():
                with st.spinner("Analyzing meal with AI..."):
                    result = ai_parse_meal(st.session_state.meal_description)
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.session_state.ai_cal = result["calories"]
                        st.session_state.ai_protein = result["protein"]
                        st.session_state.ai_carbs = result["carbs"]
                        st.session_state.ai_fat = result["fat"]
                        st.success("✅ Macros estimated!")
            else:
                st.warning("Please describe what you ate first.")
    
    with col_manual:
        st.write("**Or enter macros manually:**")

    with st.form("meal_form"):
        st.markdown("Fill in the macros below:")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            cal_manual = st.number_input("Calories", min_value=0, max_value=max(5000, st.session_state.ai_cal), value=st.session_state.ai_cal)
        with col2:
            protein_manual = st.number_input("Protein (g)", min_value=0, max_value=max(300, st.session_state.ai_protein), value=st.session_state.ai_protein)
        with col3:
            carbs_manual = st.number_input("Carbs (g)", min_value=0, max_value=max(600, st.session_state.ai_carbs), value=st.session_state.ai_carbs)
        with col4:
            fat_manual = st.number_input("Fat (g)", min_value=0, max_value=max(300, st.session_state.ai_fat), value=st.session_state.ai_fat)

        submitted = st.form_submit_button("Add meal")

    if submitted:
        if not st.session_state.meal_description.strip():
            st.warning("Please describe what you ate.")
        elif meal_type_option == "Custom" and not final_meal_type.strip():
            st.warning("Please enter a custom meal type.")
        else:
            calories = cal_manual
            protein = protein_manual
            carbs = carbs_manual
            fat = fat_manual
            desc = st.session_state.meal_description.strip()

            entry = {
                "date": selected_date.isoformat(),
                "time": st.session_state.meal_time.strftime("%H:%M"),
                "meal_type": final_meal_type,
                "description": desc,
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fat": fat,
            }
            add_entry(entry)
            
            # Clear AI values and form
            st.session_state.ai_cal = 0
            st.session_state.ai_protein = 0
            st.session_state.ai_carbs = 0
            st.session_state.ai_fat = 0
            st.session_state.meal_description = ""
            
            st.success("Meal added!")

# ----- Right: today's entries & totals -----
with right_col:
    st.subheader("Daily Summary")

    day_entries = get_entries_for_date(selected_date)
    totals = calculate_totals(day_entries)

    # Totals summary
    st.markdown("#### Daily totals vs goals")

    def progress_bar(label, current, goal):
        if goal is None:
            st.write(
                f"**{label}:** {current:.0f} _(no goal set)_"
            )
            st.progress(0.0)
            return
        st.write(
            f"**{label}:** {current:.0f} / {goal:.0f} "
            f"({'+' if current >= goal else ''}{current - goal:.0f} vs goal)"
        )
        # Avoid division by zero
        pct = (current / goal) if goal > 0 else 0
        pct = max(0.0, min(1.0, pct))
        st.progress(pct)

    progress_bar("Calories (kcal)", totals["calories"], goals["calories"])
    progress_bar("Protein (g)", totals["protein"], goals["protein"])
    progress_bar("Carbs (g)", totals["carbs"], goals["carbs"])
    progress_bar("Fat (g)", totals["fat"], goals["fat"])

# ----- Bottom: Logged meals (full width) -----
st.markdown("---")
st.subheader(f"Logged meals for {selected_date.isoformat()}")

day_entries = get_entries_for_date(selected_date)

if day_entries.empty:
    st.info("No meals logged for this date yet.")
else:
    # Sort meals by time
    day_entries = day_entries.sort_values("time").reset_index(drop=True)
    # Show meals with delete buttons - with proper column headers
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.8, 1.2, 3, 1, 1, 1, 1, 0.8])
    
    with col1:
        st.markdown("**Time**")
    with col2:
        st.markdown("**Meal Type**")
    with col3:
        st.markdown("**Description**")
    with col4:
        st.markdown("**Calories**")
    with col5:
        st.markdown("**Protein (g)**")
    with col6:
        st.markdown("**Carbs (g)**")
    with col7:
        st.markdown("**Fat (g)**")
    with col8:
        st.markdown("**Delete**")
    
    st.divider()
    
    for idx, (orig_idx, row) in enumerate(day_entries.iterrows()):
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.8, 1.2, 3, 1, 1, 1, 1, 0.8])
        
        with col1:
            st.write(row["time"])
        with col2:
            st.write(row["meal_type"])
        with col3:
            st.write(row["description"])
        with col4:
            st.write(f"{row['calories']:.0f}")
        with col5:
            st.write(f"{row['protein']:.0f}g")
        with col6:
            st.write(f"{row['carbs']:.0f}g")
        with col7:
            st.write(f"{row['fat']:.0f}g")
        with col8:
            col_edit, col_delete = st.columns(2)
            with col_edit:
                if st.button("✏️", key=f"edit_{row['id']}_{idx}", help="Edit meal"):
                    st.session_state[f"edit_meal_{row['id']}"] = True
            with col_delete:
                if st.button("🗑️", key=f"delete_{row['id']}_{idx}", help="Delete meal"):
                    delete_meal_from_db(st.session_state.logged_in_user, row['id'])
                    st.session_state.entries = load_meals_from_db(st.session_state.logged_in_user)
                    st.rerun()
        
        # Edit modal
        if st.session_state.get(f"edit_meal_{row['id']}", False):
            with st.container():
                st.markdown("---")
                st.markdown(f"### Edit Meal")
                
                with st.form(f"edit_form_{row['id']}"):
                    # Parse the time string back to time object
                    meal_time_obj = datetime.strptime(row["time"], "%H:%M").time()
                    
                    edit_time = st.time_input("Time", value=meal_time_obj, key=f"edit_time_{row['id']}")
                    edit_meal_type = st.text_input("Meal type", value=row["meal_type"], key=f"edit_type_{row['id']}")
                    edit_description = st.text_area("Description", value=row["description"], height=80, key=f"edit_desc_{row['id']}")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        edit_calories = st.number_input("Calories", min_value=0, max_value=5000, value=int(row['calories']), key=f"edit_cal_{row['id']}")
                    with col2:
                        edit_protein = st.number_input("Protein (g)", min_value=0, max_value=300, value=int(row['protein']), key=f"edit_prot_{row['id']}")
                    with col3:
                        edit_carbs = st.number_input("Carbs (g)", min_value=0, max_value=600, value=int(row['carbs']), key=f"edit_carbs_{row['id']}")
                    with col4:
                        edit_fat = st.number_input("Fat (g)", min_value=0, max_value=300, value=int(row['fat']), key=f"edit_fat_{row['id']}")
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("Save changes"):
                            updated_entry = {
                                'date': row['date'],
                                'time': edit_time.strftime("%H:%M"),
                                'meal_type': edit_meal_type,
                                'description': edit_description,
                                'calories': edit_calories,
                                'protein': edit_protein,
                                'carbs': edit_carbs,
                                'fat': edit_fat,
                            }
                            update_meal_in_db(st.session_state.logged_in_user, row['id'], updated_entry)
                            st.session_state.entries = load_meals_from_db(st.session_state.logged_in_user)
                            st.session_state[f"edit_meal_{row['id']}"] = False
                            st.success("Meal updated!")
                            st.rerun()
                    with col_cancel:
                        if st.form_submit_button("Cancel"):
                            st.session_state[f"edit_meal_{row['id']}"] = False
                            st.rerun()

