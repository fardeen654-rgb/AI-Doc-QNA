from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from database import db
from models import User
from services.email_service import send_email  # 🟢 Import Day 22 Email Service

# Define the blueprint for authentication routes
auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():
    """Handles new user signups with email notifications."""
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email") # 🟢 Captured for Day 22
        password = request.form.get("password")

        # Basic validation: ensure all fields are provided
        if not (username and email and password):
            flash("All fields (Username, Email, Password) are required! ⚠️")
            return redirect(url_for("auth.register"))

        # Check if user or email already exists to prevent duplicates
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash("Username or Email already registered. Please login. ⚠️")
            return redirect(url_for("auth.register"))

        # Create new user and hash the password for security
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method="pbkdf2:sha256")
        )

        try:
            db.session.add(new_user)
            db.session.commit()

            # 📧 Day 22: Send the Welcome Email
            subject = "Welcome to AI Document Q&A! 🎉"
            body = f"Hi {username},\n\nWelcome! You can now upload PDFs and ask questions securely.\n\n- AI Doc Q&A Team"
            send_email(to_email=email, subject=subject, body=body)

            flash("Success! A welcome email has been sent. Please login. ✅")
            return redirect(url_for("auth.login"))
            
        except Exception as e:
            db.session.rollback()
            flash("Registration failed. Please try again.")
            print(f"Error: {e}")

    return render_template("register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    """Authenticates existing users."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        # Verify username exists and password hash matches
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
        
        flash("Invalid username or password. ❌")
        
    return render_template("login.html")

@auth.route("/logout")
@login_required
def logout():
    """Ends the user session."""
    logout_user()
    flash("You have been logged out. 👋")
    return redirect(url_for("auth.login"))