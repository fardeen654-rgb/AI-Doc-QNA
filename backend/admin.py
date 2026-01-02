import os
from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from models import User, ChatHistory, UsageAnalytics
from config import Config # Using centralized config
from datetime import date

# Define the Admin Blueprint
admin = Blueprint('admin', __name__)

@admin.route("/users")
@login_required
def list_users():
    """Directory view of all registered users."""
    # 🔒 RBAC: Ensure only admins can see the user list
    if current_user.role != 'admin':
        abort(403) 
    
    # Query all users for the management table
    all_users = User.query.all()
    return render_template("admin_users.html", users=all_users)

@admin.route("/admin/user/<int:user_id>")
@login_required
def user_detail(user_id):
    """Detailed inspection of a specific user's activity and files."""
    if current_user.role != 'admin':
        abort(403)
    
    # Fetch the specific user or return 404 if invalid ID
    user = User.query.get_or_404(user_id)
    
    # Retrieve user-specific chat logs
    chats = ChatHistory.query.filter_by(user_id=user.id).order_by(ChatHistory.created_at.desc()).all()
    
    # Locate user-specific file directory
    user_folder = f"user_{user.id}"
    user_upload_dir = os.path.join(Config.UPLOAD_DIR, user_folder)
    
    pdfs = []
    if os.path.exists(user_upload_dir):
        pdfs = os.listdir(user_upload_dir)
        
    return render_template("admin_user_detail.html", user=user, chats=chats, pdfs=pdfs)

@admin.route("/admin/analytics")
@login_required
def analytics():
    """Aggregates system-wide usage metrics for monitoring."""
    if current_user.role != 'admin':
        abort(403)

    # 📊 Real-time Monitoring: Stats for today
    today = date.today()
    global_stats = UsageAnalytics.query.filter_by(day=today).all()
    
    # Aggregate counts for dashboard summary cards
    today_uploads = sum(s.count for s in global_stats if s.action == "upload_pdf")
    today_queries = sum(s.count for s in global_stats if s.action == "ask_question")
    
    # Fetch historical logs for trend analysis (limited to last 50 entries)
    all_time_stats = UsageAnalytics.query.order_by(UsageAnalytics.day.desc()).limit(50).all()

    return render_template(
        "admin_analytics.html", 
        stats=all_time_stats, 
        today_uploads=today_uploads, 
        today_queries=today_queries
    )