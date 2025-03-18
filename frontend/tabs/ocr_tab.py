# frontend/tabs/ocr_tab.py
import gradio as gr
import os
import requests
from utils.config import config
from utils.call_ai import load_prompts

PROCESSED_DIR = "data/processed"

def create_ocr_tab():
    # Load prompts for the dropdown
    sorted_names, prompt_map = load_prompts()
    
    # Create the models list
    models_list = ['Default'] + config['API']['Models'].split('|')
    
    default_prompt_name = config['UI']['DefaultPrompt']
    default_prompt = prompt_map.get(default_prompt_name)
    
    # Handler for when a prompt is selected
    def on_prompt_selected(prompt_name):
        selected_prompt = prompt_map[prompt_name]
        return selected_prompt['Prompt'], selected_prompt['Model'], selected_prompt['FileExt']

    with gr.Group():
        gr.Markdown("## Text Extraction and Processing")
        
        with gr.Row():
            file_input = gr.File(label="Upload File")
            
        with gr.Row():
            prompt_dropdown = gr.Dropdown(
                choices=sorted_names,
                value=default_prompt_name if default_prompt_name in sorted_names else None,
                label="Select Prompt Template"
            )
            model_dropdown = gr.Dropdown(
                choices=models_list,
                value="Default",
                label="Select Model"
            )
        
        # Hidden fields to store selected prompt details
        model_value = gr.Textbox(visible=False, value=default_prompt["Model"])
        file_ext_value = gr.Textbox(visible=False, value=default_prompt["FileExt"])
        
        prompt_text = gr.Textbox(
            label="Prompt Text", 
            placeholder="Enter prompt text to guide the OCR extraction...",
            lines=5,
            value=default_prompt["Prompt"]
        )
        
        with gr.Row():
            process_btn = gr.Button("Process File", size="sm")
        
        # Instead of using scale, we'll use a more compatible approach
        with gr.Row():
            # Use columns to control the width
            with gr.Column(variant="compact"):
                output_file = gr.File(label="Output File")
            with gr.Column(variant="compact"):
                status_text = gr.Textbox(label="Status")
        
        # Connect the prompt dropdown to update the prompt text and hidden fields
        prompt_dropdown.change(
            fn=on_prompt_selected,
            inputs=[prompt_dropdown],
            outputs=[prompt_text, model_value, file_ext_value]
        )
        
        # Connect the process button to the processing function with all details
        process_btn.click(
            fn=process_file,
            inputs=[file_input, prompt_text, model_value, file_ext_value, model_dropdown],
            outputs=[output_file, status_text]
        )

def process_file(file, prompt_text, default_model, file_ext, selected_model):
    try:
        if file is None:
            return None, "Please upload a file to process."
        
        # Get the original file name
        original_filename = os.path.basename(file.name)
        file_name, _ = os.path.splitext(original_filename)
        
        # Use the extension from the selected prompt
        output_filename = f"{file_name}.{file_ext}"
        
        # Create output directory if it doesn't exist
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        
        # Full path for the output file
        output_file_path = os.path.join(PROCESSED_DIR, output_filename)
        
        # Read the file content
        with open(file.name, "rb") as f:
            file_blob = f.read()
        
        # Determine which model to use
        model = default_model if selected_model == "Default" else selected_model
        
        # Call the API to extract text
        try:
            # Send request to API endpoint
            response = requests.post(
                f'http://localhost:{config["API"]["Port"]}/ocr',
                files={"file": (original_filename, file_blob)},
                data={
                    "prompt_text": prompt_text,
                    "file_ext": file_ext,
                    "model": model
                }
            )
            
            if response.status_code == 200:
                # Get the text content directly from the response
                text_content = response.content
                
                # Write the content to the file
                with open(output_file_path, 'wb') as f:
                    f.write(text_content)
                
                # Return the path to the file and a success message
                return output_file_path, f"Text successfully extracted, processed and saved as '{output_filename}'"
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