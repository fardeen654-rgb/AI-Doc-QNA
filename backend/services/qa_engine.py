import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class QAEngine:
    """
    Citation-aware QA Engine using Groq (FREE & High Speed)
    """

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env")

        self.client = Groq(api_key=api_key)

    def generate_answer(self, question: str, context_chunks: list) -> dict:
        """
        Generates answer + returns supporting document chunks.
        """
        if not context_chunks:
            return {
                "answer": "Answer not found in the document.",
                "sources": []
            }

        # Combine the top retrieved chunks into one context string
        context = "\n\n".join(context_chunks)

        # The System Prompt for Grounding
        system_prompt = "You are a professional assistant. Answer questions ONLY using the provided document context. If the answer is not in the context, say 'Answer not found in the document.' Be concise."
        
        user_prompt = f"DOCUMENT CONTEXT:\n{context}\n\nQUESTION: {question}"

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1  # Low temperature keeps it factual
            )

            # Return both the AI text and the top 2 chunks as 'sources'
            return {
                "answer": response.choices[0].message.content.strip(),
                "sources": context_chunks[:2]
            }

        except Exception as e:
            return {"answer": f"Groq Error: {str(e)}", "sources": []}