import os
import shutil
import csv
import io
from datetime import date
from flask import (
    Flask, render_template, request, flash,
    redirect, url_for, send_file, Response
)
from flask_login import LoginManager, login_required, current_user
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from xhtml2pdf import pisa  # 🟢 New PDF Library

# 1. LOAD CONFIG & DATABASE
load_dotenv()
from config import Config
from database import db
from models import User, ChatHistory, UsageAnalytics

# --- RAG SERVICE IMPORTS ---
from services.pdf_loader import extract_text_from_pdf
from services.text_cleaner import clean_text
from services.text_chunker import chunk_text
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore
from services.qa_engine import QAEngine
from services.hybrid_search import hybrid_rerank

# Initialize Services
embedding_service = EmbeddingService()
qa_engine = QAEngine()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"pdf"}

# --- ANALYTICS HELPERS ---
def track_usage(action):
    record = UsageAnalytics.query.filter_by(
        user_id=current_user.id, action=action, day=date.today()
    ).first()
    if record:
        record.count += 1
    else:
        record = UsageAnalytics(user_id=current_user.id, action=action)
        db.session.add(record)
    db.session.commit()

def check_rate_limit(max_limit):
    if current_user.role == "admin": return True
    record = UsageAnalytics.query.filter_by(
        user_id=current_user.id, action="ask_question", day=date.today()
    ).first()
    return not (record and record.count >= max_limit)

def create_app():
    app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
    app.config.from_object(Config) #
    
    db.init_app(app)

    # REGISTER BLUEPRINTS
    from authentication import auth 
    from admin import admin as admin_blueprint
    app.register_blueprint(auth)
    app.register_blueprint(admin_blueprint)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    # --- PRODUCTION ENDPOINTS ---
    @app.route("/health")
    def health():
        return {"status": "ok", "service": "AI Document Q&A", "version": "1.0.0"}, 200

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", message="Page not found"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", message="Internal server error"), 500

    # --- EXPORT ROUTES ---
    @app.route("/export/csv")
    @login_required
    def export_csv():
        history = ChatHistory.query.filter_by(user_id=current_user.id).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Date", "Question", "Answer"])
        for item in history:
            writer.writerow([item.created_at, item.question, item.answer])
        output.seek(0)
        return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=chat_history.csv"})

    @app.route("/export/pdf")
    @login_required
    def export_pdf():
        """Generates PDF using HTML templates for better text wrapping."""
        history = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.created_at.desc()).all()
        
        # Create a simple HTML string for the PDF content
        html_content = f"<html><body><h1 style='text-align:center;'>Chat History: {current_user.username}</h1>"
        for item in history:
            html_content += f"<div style='border-bottom:1px solid #ccc; padding:10px;'>"
            html_content += f"<p><b>Q:</b> {item.question}</p>"
            html_content += f"<p><b>A:</b> {item.answer}</p>"
            html_content += f"<p style='font-size:10px; color:#666;'>Date: {item.created_at}</p></div>"
        html_content += "</body></html>"

        # Convert HTML to PDF in memory
        pdf_out = io.BytesIO()
        pisa.CreatePDF(html_content, dest=pdf_out)
        pdf_out.seek(0)

        return send_file(
            pdf_out,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="chat_history.pdf"
        )

    # --- HOME LOGIC ---
    @app.route("/", methods=["GET", "POST"])
    @login_required
    def home():
        answer_data = None
        user_folder = f"user_{current_user.id}"
        user_upload_dir = os.path.join(app.config["UPLOAD_DIR"], user_folder)
        user_index_dir = os.path.join(app.config["INDEX_DIR"], user_folder)
        os.makedirs(user_upload_dir, exist_ok=True)
        os.makedirs(user_index_dir, exist_ok=True)

        vector_store = VectorStore(user_index_dir)
        vector_store.load()

        if request.method == "POST":
            if "pdf_files" in request.files:
                files = request.files.getlist("pdf_files")
                count = 0
                for file in files:
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        path = os.path.join(user_upload_dir, filename)
                        file.save(path)
                        text = clean_text(extract_text_from_pdf(path))
                        chunks = chunk_text(text, source=filename)
                        embeddings = embedding_service.embed_texts([c["text"] for c in chunks])
                        vector_store.create_or_update_index(embeddings, chunks)
                        count += 1
                if count > 0: track_usage("upload_pdf")
                flash(f"{count} PDF(s) Indexed! ✅")

            elif "query" in request.form:
                if not check_rate_limit(app.config["MAX_QUESTIONS_PER_DAY"]):
                    flash("Daily limit reached! ⚠️")
                    return redirect(url_for("home"))

                question = request.form.get("query")
                if not vector_store.index:
                    flash("Upload PDFs first! ⚠️")
                else:
                    query_embedding = embedding_service.embed_texts([question])[0]
                    retrieved_chunks = vector_store.search(query_embedding, top_k=8)
                    retrieved_chunks = hybrid_rerank(question, retrieved_chunks)
                    answer_data = qa_engine.generate_answer(question, retrieved_chunks)
                    track_usage("ask_question")
                    db.session.add(ChatHistory(question=question, answer=answer_data["answer"], user_id=current_user.id))
                    db.session.commit()

        history = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.created_at.desc()).all()
        pdfs = os.listdir(user_upload_dir) if os.path.exists(user_upload_dir) else []
        stats = UsageAnalytics.query.filter_by(user_id=current_user.id, day=date.today()).all()
        return render_template("index.html", answer_data=answer_data, history=history, pdfs=pdfs, stats=stats, max_limit=app.config["MAX_QUESTIONS_PER_DAY"])

    @app.route("/delete-pdf/<filename>", methods=["POST"])
    @login_required
    def delete_pdf(filename):
        user_folder = f"user_{current_user.id}"
        user_upload_dir = os.path.join(app.config["UPLOAD_DIR"], user_folder)
        user_index_dir = os.path.join(app.config["INDEX_DIR"], user_folder)
        file_path = os.path.join(user_upload_dir, filename)
        if os.path.exists(file_path): os.remove(file_path)
        if os.path.exists(user_index_dir): shutil.rmtree(user_index_dir)
        os.makedirs(user_index_dir, exist_ok=True)
        # Re-index remaining
        vs = VectorStore(user_index_dir)
        for pdf in os.listdir(user_upload_dir):
            txt = clean_text(extract_text_from_pdf(os.path.join(user_upload_dir, pdf)))
            chunks = chunk_text(txt, source=pdf)
            vs.create_or_update_index(embedding_service.embed_texts([c["text"] for c in chunks]), chunks)
        flash(f"Deleted {filename} and re-indexed. ✅")
        return redirect(url_for("home"))

    return app

if __name__ == "__main__":
    # Get the port from Render's environment, default to 5000 for local testing
    port = int(os.environ.get("PORT", 10000))
    
    # Run with host '0.0.0.0' to be accessible on Render
    # Set debug=False for production safety
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=False)