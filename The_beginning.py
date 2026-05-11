import pandas as pd
from flask import Flask, request, redirect, url_for, session, render_template_string

app = Flask(__name__)
app.secret_key = "your-secret-key-123"  # Needed for sessions

# --- DATABASE LOADING ---
def load_authorized_users():
    """Loads names from parquet files to act as the user database."""
    try:
        # Load given names and surnames
        df_given = pd.read_parquet('given_names_data.parquet')
        df_surnames = pd.read_parquet('surnames_data.parquet')
        
        # In the provided files, the columns are labeled 'surname'
        # We collect all unique names from both files
        names = set(df_given['surname'].dropna().unique())
        names.update(df_surnames['surname'].dropna().unique())
        
        # Add the original hardcoded accounts for safety
        users_dict = {name: name for name in names} # Using name as password for simplicity
        users_dict["admin"] = "password123"
        users_dict["neo"] = "matrix"
        
        return users_dict
    except Exception as e:
        print(f"Error loading database: {e}")
        # Fallback to default users if database fails to load
        return {"admin": "password123", "neo": "matrix"}

# Initialize the USERS dictionary from the parquet database
USERS = load_authorized_users()

@app.route("/")
def index():
    # If user is logged in, show their name
    if "username" in session:
        return f"""
        <div style="background:#070b0f; color:#00ff88; font-family:'Share Tech Mono',monospace; height:100vh; padding:50px;">
            <h1>> ACCESS GRANTED: {session['username']}</h1>
            <p>> System status: ONLINE</p>
            <br>
            <a href='/logout' style="color:#ff4466;">[ TERMINATE SESSION ]</a>
        </div>
        """
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Authentication logic: Check if user exists and password matches
        # Note: For the database names, we are checking if password == username
        if USERS.get(username) == password:
            session["username"] = username
            return redirect(url_for("index"))
        else:
            error = "ACCESS DENIED: INVALID IDENTIFIER OR KEY"

    # Load and render the custom login.html provided
    try:
        with open("login.html", "r") as f:
            template = f.read()
        return render_template_string(template, error=error)
    except FileNotFoundError:
        return "Login template not found. Please ensure login.html is in the same directory."

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    print(f"System ready. {len(USERS)} identifiers loaded into memory.")
    app.run(debug=True)