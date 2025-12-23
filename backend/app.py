import os
from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename

# Service Imports
from services.pdf_loader import extract_text_from_pdf
from services.text_cleaner import clean_text
from services.text_chunker import chunk_text
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore
from services.qa_engine import QAEngine

# Database Imports
from database import db
from models import ChatHistory

# Configuration & Paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "data", "uploads")
INDEX_FOLDER = os.path.join(BASE_DIR, "data", "faiss_index")
# DB path inside the container
DB_PATH = os.path.join(BASE_DIR, "rag.db") 

ALLOWED_EXTENSIONS = {"pdf"}

# Initialize Services
embedding_service = EmbeddingService()
vector_store = VectorStore(INDEX_FOLDER)
qa_engine = QAEngine()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app():
    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static"
    )

    # Production Configurations
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "prod-secret-789")
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Ensure system folders exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(INDEX_FOLDER, exist_ok=True)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/", methods=["GET", "POST"])
    def home():
        answer_data = None
        vector_store.load()

        if request.method == "POST":
            # 1. Handle Multiple PDF Uploads
            if "pdf_files" in request.files:
                files = request.files.getlist("pdf_files")
                count = 0
                for file in files:
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        path = os.path.join(UPLOAD_FOLDER, filename)
                        file.save(path)

                        # RAG Processing with Metadata
                        text = clean_text(extract_text_from_pdf(path))
                        chunks = chunk_text(text, source=filename)
                        
                        # Generate Embeddings & Append to FAISS
                        embeddings = embedding_service.embed_texts([c["text"] for c in chunks])
                        vector_store.create_or_update_index(embeddings, chunks)
                        count += 1
                flash(f"Indexed {count} file(s) successfully! ✅")

            # 2. Handle Semantic Question Answering
            elif "query" in request.form:
                question = request.form.get("query")
                if not vector_store.index:
                    flash("Upload PDFs first! ⚠️")
                else:
                    query_embedding = embedding_service.embed_texts([question])[0]
                    retrieved_chunks = vector_store.search(query_embedding)

                    # Generation with citations
                    answer_data = qa_engine.generate_answer(
                        question=question,
                        context_chunks=[c["text"] for c in retrieved_chunks]
                    )

                    # 💾 Save to SQL History
                    chat = ChatHistory(
                        question=question,
                        answer=answer_data["answer"],
                        sources="\n\n".join(f"[{c['source']}] {c['text'][:200]}..." for c in retrieved_chunks[:2])
                    )
                    db.session.add(chat)
                    db.session.commit()

        # Load history for the frontend
        history = ChatHistory.query.order_by(ChatHistory.created_at.desc()).all()
        return render_template("index.html", answer_data=answer_data, history=history)

    return app

# Only used for LOCAL development (python app.py)
# Production uses wsgi.py + gunicorn
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)