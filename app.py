import os
from groq import Groq
from dotenv import load_dotenv
from retriever import retrieve

# Load the GROQ_API_KEY from your .env file
load_dotenv()

# Initialize the Groq client — it automatically picks up GROQ_API_KEY from environment
groq_client = Groq()


def generate_response(query: str) -> dict:
    """
    Full RAG pipeline: retrieve relevant chunks, then generate a grounded answer.
    
    Returns a dict with:
    - "answer": the LLM's response (grounded in retrieved chunks only)
    - "sources": list of source filenames the answer drew from
    """
    # Step 1: Retrieve the most relevant chunks for this query
    chunks = retrieve(query, top_k=5)

    # Step 2: Format the retrieved chunks as context for the LLM
    # We label each chunk with its source so the model can cite it
    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(f"[Source: {chunk['source']}]\n{chunk['text']}")
    context = "\n\n---\n\n".join(context_parts)

    # Step 3: Build the prompt
    # The system prompt is what enforces grounding — it explicitly tells the model
    # NOT to use outside knowledge. This is the most important part of RAG generation.
    system_prompt = """You are a helpful assistant answering questions about tech internship experiences.

Answer using ONLY the information provided in the documents below. 
Do not use any outside knowledge or make assumptions beyond what is in the text.
If the documents do not contain enough information to answer the question, say exactly:
"I don't have enough information in my documents to answer that."

Always cite your sources by mentioning the document name (e.g. "According to 01_google_internship.txt...").
Keep your answer concise and focused on what the documents actually say."""

    # The user message contains both the context and the question
    user_message = f"""Documents:
{context}

Question: {query}"""

    # Step 4: Call the Groq API
    # We use llama-3.3-70b-versatile — free tier, fast, good at following instructions
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.2,  # low temperature = more focused, less creative = better grounding
        max_tokens=500
    )

    # Extract the answer text from the response
    answer = response.choices[0].message.content

    # Collect unique source filenames from the retrieved chunks
    sources = list(set(chunk["source"] for chunk in chunks))

    return {
        "answer": answer,
        "sources": sources
    }


# Gradio UI — runs when you do: py app.py
import gradio as gr

def handle_query(question: str):
    """Wrapper for Gradio — takes a question string, returns (answer, sources) tuple."""
    if not question.strip():
        return "Please enter a question.", ""
    
    result = generate_response(question)
    
    # Format sources as a bullet list for display
    sources_text = "\n".join(f"• {s}" for s in result["sources"])
    
    return result["answer"], sources_text


# Build the Gradio interface
with gr.Blocks(title="The Unofficial Internship Guide") as demo:
    gr.Markdown("## 🎓 The Unofficial Internship Guide")
    gr.Markdown("Ask anything about tech internships — WLB, salary, red flags, how to get one.")
    
    with gr.Row():
        inp = gr.Textbox(
            label="Your question",
            placeholder="e.g. What do students say about WLB at Google?",
            lines=2
        )
    
    btn = gr.Button("Ask", variant="primary")
    
    with gr.Row():
        answer = gr.Textbox(label="Answer", lines=8)
        sources = gr.Textbox(label="Sources", lines=8)
    
    # Both the button click and pressing Enter trigger the query
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()