# frontend/app.py
from fastapi import FastAPI
import gradio as gr
import os

# Import tab modules
from frontend.tabs.add_tab import create_add_tab
from frontend.tabs.ocr_tab import create_ocr_tab

# Create FastAPI app
app = FastAPI()

def create_gradio_interface():
    # Create tabs
    with gr.Blocks() as demo:
        with gr.Tabs():
            with gr.Tab("OCR"):
                create_ocr_tab()
            
            with gr.Tab("Playground"):
                create_add_tab()
    
    return demo

# Create the Gradio interface
demo = create_gradio_interface()

def is_run_by_systemd():
    # systemd sets specific environment variables
    return 'INVOCATION_ID' in os.environ or 'JOURNAL_STREAM' in os.environ

# Mount the Gradio app with explicit root_path
app = gr.mount_gradio_app(app, demo, path="/", 
                          root_path=("/" if is_run_by_systemd() else "/"))  # ("/ui"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

