# frontend/tabs/ocr_tab.py
import gradio as gr
import os
import requests
from utils.config import config

PROCESSED_DIR = "data/processed"


def process_file(file, prompt_text):
    try:
        if file is None:
            return None, "Please upload a file to process."
        
        # Get the original file name
        original_filename = os.path.basename(file.name)
        file_name, _ = os.path.splitext(original_filename)
        
        # Create output CSV filename
        output_filename = f"{file_name}.csv"
        
        # Create output directory if it doesn't exist
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        
        # Full path for the output file
        output_file_path = os.path.join(PROCESSED_DIR, output_filename)
        
        # Read the file content
        with open(file.name, "rb") as f:
            file_blob = f.read()
        
        # Call the API to extract text
        try:
            # Send request to API endpoint
            response = requests.post(
                f'http://localhost:{config["API"]["Port"]}/ocr',
                files={"file": (original_filename, file_blob)},
                data={"prompt_text": prompt_text}
            )
            
            if response.status_code == 200:
                # Get the CSV content directly from the response
                csv_content = response.content
                
                # Write the content to the file
                with open(output_file_path, 'wb') as f:
                    f.write(csv_content)
                
                # Return the path to the file and a success message
                return output_file_path, f"CSV text successfully extracted and saved as '{output_filename}'"
            else:
                # Handle error response
                error_msg = "Unknown error"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Unknown error')
                except:
                    error_msg = f"Error code: {response.status_code}"
                
                return None, f"Error from API: {error_msg}"
                
        except requests.exceptions.RequestException as e:
            return None, f"Failed to connect to API: {str(e)}"
    
    except Exception as e:
        return None, f"Error processing file: {str(e)}"

def create_ocr_tab():
    with gr.Group():
        gr.Markdown("## OCR CSV Text Extraction")
        gr.Markdown("Upload a file and process it to extract CSV text")
        
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
        
        # Connect the process button to the processing function
        process_btn.click(
            fn=process_file,
            inputs=[file_input, prompt_text],
            outputs=[output_file, status_text]
        )