from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from database import db
from models import User
from services.email_service import send_email  # 🟢 Import Day 22 Email Service
from app import mail
from flask_mail import Message

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

@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()

        if user:
            user.generate_reset_token()
            db.session.commit()

            reset_link = url_for(
                "auth.reset_password",
                token=user.reset_token,
                _external=True
            )

            # print("RESET LINK (DEV):", reset_link)  # Email later
            msg = Message(
                subject="Password Reset",
                sender=os.getenv("MAIL_USERNAME"),
                recipients=[user.email],
                body=f"Reset your password using this link:\n\n{reset_link}"
            )

            mail.send(msg)

        flash("If the email exists, a reset link has been sent.", "info")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")


@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()

    if not user or user.reset_token_expiry < datetime.utcnow():
        flash("Reset link is invalid or expired", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        new_password = request.form.get("password")
        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()

        flash("Password reset successful. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html")


@auth.route("/logout")
@login_required
def logout():
    """Ends the user session."""
    logout_user()
    flash("You have been logged out. 👋")
    return redirect(url_for("auth.login"))