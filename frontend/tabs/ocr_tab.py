# frontend/tabs/ocr_tab.py
import gradio as gr
import os
import tempfile
import requests

from utils.config import config

def process_file(file, prompt_text):
    try:
        if file is None:
            return "Please upload a file to process."
        
        # Get the original file name
        original_filename = os.path.basename(file.name)
        file_name, file_ext = os.path.splitext(original_filename)
        
        # Create output CSV filename
        output_filename = f"{file_name}.csv"
        
        # Read the file content
        with open(file.name, "rb") as f:
            file_blob = f.read()
        
        # Call the API to extract text
        try:
            # This would be replaced with your actual API endpoint
            response = requests.post(
                f'http://localhost:{config["API"]["Port"]}/ocr',
                files={"file": (original_filename, file_blob)},
                data={"prompt_text": prompt_text}
            )
            
            if response.status_code == 200:
                # Save the response content as a CSV file
                csv_content = response.text
                
                # Create a temporary file path to save the CSV
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                    temp_file.write(csv_content.encode('utf-8'))
                    temp_csv_path = temp_file.name
                
                return temp_csv_path, f"Text successfully extracted and saved as {output_filename}"
            else:
                return None, f"Error from API: {response.json().get('error', 'Unknown error')}"
                
        except requests.exceptions.RequestException as e:
            return None, f"Failed to connect to API: {str(e)}"
    
    except Exception as e:
        return None, f"Error processing file: {str(e)}"

def create_ocr_tab():
    with gr.Group():
        gr.Markdown("## OCR Text Extraction")
        gr.Markdown("Upload a file and process it to extract text")
        
        with gr.Row():
            file_input = gr.File(label="Upload File")
        
        prompt_text = gr.Textbox(
            label="Prompt Text", 
            placeholder="Enter prompt text to guide the OCR extraction...",
            lines=2
        )
        
        with gr.Row():
            process_btn = gr.Button("Process File")
        
        output_file = gr.File(label="Output CSV")
        status_text = gr.Textbox(label="Status")
        
        process_btn.click(
            fn=process_file,
            inputs=[file_input, prompt_text],
            outputs=[output_file, status_text]
        )