import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class QAEngine:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def generate_answer(self, question, chunks):
        if not chunks:
            return {"answer": "Answer not found in the provided document.", "confidence": 0.0, "sources": []}

        # Format context with explicit source markers
        context = "\n\n".join(f"Source: {c['source']}\nContent: {c['text']}" for c in chunks)

        system_prompt = """
        You are a document-grounded assistant.
        Rules:
        1. Answer ONLY from the provided context. Do NOT use external knowledge.
        2. If the answer is not in the context, say "Answer not found in the provided document."
        3. Be precise. Cite your findings.
        """

        user_prompt = f"DOCUMENT CONTEXT:\n{context}\n\nQUESTION: {question}"

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1 # Low temperature for factual consistency
        )

        answer = response.choices[0].message.content.strip()
        # Basic confidence score based on chunk availability
        confidence = min(1.0, len(chunks) / 8)

        return {
            "answer": answer,
            "confidence": round(confidence, 2),
            "sources": chunks[:2] # Top 2 citations
        }