from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from seo import SEOAnalyzer  # Your SEO script

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key

# MySQL Configuration
db_config = {
    "host": "localhost",
    "user": "root",  # Change to your MySQL username
    "password": "",  # Change to your MySQL password
    "database": "seo_monitor"
}

def get_db_connection():
    """Establish a connection to MySQL"""
    return mysql.connector.connect(**db_config)

# SIGNUP ROUTE
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]  # Storing plain passwords (NOT recommended for production!)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("login"))
        except mysql.connector.Error:
            flash("Username already exists. Try a different one.", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("signup.html")

#  LOGIN ROUTE
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials. Try again.", "danger")

    return render_template("login.html")

#  LOGOUT ROUTE
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

#  DASHBOARD ROUTE
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM seo_results WHERE user_id = %s", (user_id,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("dashboard.html", results=results, username=session["username"])

#  SEO ANALYSIS ROUTE
@app.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        url = request.form.get("url")
        try:
            analyzer = SEOAnalyzer(url)
            result = analyzer.analyze()
            user_id = session["user_id"]

            # Store results in MySQL
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO seo_results (user_id, url, meta_title, word_count, keyword_density) VALUES (%s, %s, %s, %s, %s)",
                           (user_id, url, result["meta_tags"]["title"], result["word_count"], str(result["keyword_density"])))
            conn.commit()
            cursor.close()
            conn.close()

            return render_template("result.html", url=url, result=result)
        except Exception as e:
            return render_template("index.html", error=str(e))

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
