import gradio as gr
import subprocess
import time
import requests
import json
import os
from pathlib import Path

# Start Ollama server
def start_ollama():
    try:
        subprocess.Popen(['ollama', 'serve'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(10)
        return "✅ Ollama started"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Download model if needed
def setup_model():
    try:
        result = subprocess.run(['ollama', 'pull', 'phi3:mini'], capture_output=True, text=True)
        return "✅ Model ready"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Basic chat function
def ask_ollama(prompt, model="phi3:mini"):
    try:
        url = "http://localhost:11434/api/generate"
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(url, json=data, timeout=60)
        if response.status_code == 200:
            return response.json()['response']
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# Simple document processing
def process_document(text_content):
    # For now, just store the text (we'll add vector search later)
    global document_content
    document_content = text_content
    return f"✅ Document processed! ({len(text_content)} characters)"

def ask_document(question):
    global document_content
    if 'document_content' not in globals():
        return "Please upload a document first!"
    
    # Simple prompt with document context
    prompt = f"""Du är en svensk juridisk AI-assistent. Svara på svenska baserat på dokumentet nedan.

DOKUMENT:
{document_content[:2000]}  # First 2000 chars to avoid token limits

FRÅGA: {question}

SVAR (på svenska, kort och tydligt):"""
    
    return ask_ollama(prompt)

# Gradio interface
def create_interface():
    with gr.Blocks(title="Swedish Legal AI") as demo:
        gr.Markdown("# 🏛️ Swedish Legal Document AI Assistant")
        
        with gr.Tab("Setup"):
            setup_btn = gr.Button("🚀 Start Ollama Server")
            setup_output = gr.Textbox(label="Setup Status")
            
            model_btn = gr.Button("📥 Download Model")
            model_output = gr.Textbox(label="Model Status")
            
            setup_btn.click(start_ollama, outputs=setup_output)
            model_btn.click(setup_model, outputs=model_output)
        
        with gr.Tab("Chat"):
            chat_input = gr.Textbox(label="Ask a question in Swedish")
            chat_btn = gr.Button("💬 Ask")
            chat_output = gr.Textbox(label="AI Response", lines=5)
            
            chat_btn.click(ask_ollama, inputs=chat_input, outputs=chat_output)
        
        with gr.Tab("Document Q&A"):
            doc_input = gr.Textbox(
                label="Paste Swedish Legal Text",
                lines=10,
                placeholder="Klistra in din svenska juridiska text här..."
            )
            process_btn = gr.Button("📄 Process Document")
            process_output = gr.Textbox(label="Processing Status")
            
            question_input = gr.Textbox(
                label="Ask about the document",
                placeholder="Vad handlar dokumentet om?"
            )
            ask_btn = gr.Button("❓ Ask Question")
            answer_output = gr.Textbox(label="Answer", lines=8)
            
            process_btn.click(process_document, inputs=doc_input, outputs=process_output)
            ask_btn.click(ask_document, inputs=question_input, outputs=answer_output)
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)
