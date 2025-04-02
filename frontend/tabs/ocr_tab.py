# frontend/tabs/ocr_tab.py
import gradio as gr
import os
import requests

from utils.config import config
import utils.md_utils as md_utils
from utils.call_ai import load_prompts


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
        requires_url_val = selected_prompt['id'] in ['summary']
        return selected_prompt['Prompt'], selected_prompt['Model'], selected_prompt['FileExt'], requires_url_val

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
            url_input = gr.Textbox(
                label="URL",
                placeholder="Enter optional URL to scrape...",
            )
        
        # Hidden fields to store selected prompt details
        model_value = gr.Textbox(visible=False, value=default_prompt["Model"])
        file_ext_value = gr.Textbox(visible=False, value=default_prompt["FileExt"])
        requires_url = gr.Textbox(visible=False, value=str(default_prompt['id'] in ['summary']))
        
        prompt_text = gr.Textbox(
            label="Prompt Text", 
            placeholder="Enter prompt text to guide the AI...",
            lines=5,
            value=default_prompt["Prompt"]
        )
        
        with gr.Row():
            process_btn = gr.Button("Invoke Artificial Intelligence (AI)", size="sm")
        
        with gr.Row():
            # Use columns to control the width
            with gr.Column(variant="compact"):
                output_file = gr.File(label="Download Output")
            with gr.Column(variant="compact"):
                status_text = gr.Textbox(label="Status")
        
        # Add a preview section with tabs for different view types
        gr.Markdown("### Output")
        with gr.Tabs():
            with gr.TabItem("Plain Text"):
                preview_text = gr.Textbox(
                    label="",
                    value="Processed content will appear here...",
                    lines=12
                )
            with gr.TabItem("Rendered View"):
                preview_html = gr.HTML(
                    label="",
                    value="<div style='height: 300px; overflow-y: auto; padding: 10px; border: 1px solid #ddd;'><p>Processed content will appear here...</p></div>"
                )
        
        # Connect the prompt dropdown to update the prompt text and hidden fields
        prompt_dropdown.change(
            fn=on_prompt_selected,
            inputs=[prompt_dropdown],
            outputs=[prompt_text, model_value, file_ext_value, requires_url]
        )
        
        # Connect the process button to the processing function with all details
        process_btn.click(
            fn=process_file,
            inputs=[file_input, prompt_text, model_value, file_ext_value, model_dropdown, url_input, requires_url],
            outputs=[output_file, status_text, preview_html, preview_text]
        )

def process_file(file, prompt_text, default_model, file_ext, selected_model, url, requires_url_str):
    try:
        # Convert requires_url string to boolean
        requires_url = requires_url_str.lower() == 'true'
        
        # Check if appropriate inputs are provided
        if not requires_url and file is None:
            return None, "Please upload a file to process.", "", ""
        
        if requires_url and not url:
            return None, "URL must be specified for summary.", "", ""
        
        # Determine which model to use
        model = default_model if selected_model == "Default" else selected_model
        
        # Create output directory if it doesn't exist
        dir = config['UI']['ProcessedDir']
        os.makedirs(dir, exist_ok=True)
        
        # Call the API to process the content
        try:
            # Prepare data dictionary for the API request
            data = {
                "prompt_text": prompt_text,
                "file_ext": file_ext,
                "model": model
            }
            
            # Add URL to the data dictionary if using the summary endpoint
            if requires_url:
                data["url"] = url
                
                # Make the API request without files
                response = requests.post(
                    f'http://localhost:{config["API"]["Port"]}/summary',
                    data=data
                )
                
                # Generate filename from URL (assuming we'll get this from the response headers)
                if response.status_code == 200:
                    # Extract filename from content-disposition header if present
                    cd_header = response.headers.get('content-disposition', '')
                    output_filename = cd_header.split('filename=')[1].strip('"')
                else:
                    # Will be handled in the error section below
                    output_filename = None
            else:
                # For OCR endpoint, include the file
                original_filename = os.path.basename(file.name)
                file_name, _ = os.path.splitext(original_filename)
                output_filename = f"{file_name}.{file_ext}"
                
                # Read the file content
                with open(file.name, "rb") as f:
                    file_blob = f.read()
                
                # Make the API request with file
                response = requests.post(
                    f'http://localhost:{config["API"]["Port"]}/ocr',
                    files={"file": (original_filename, file_blob)},
                    data=data
                )
            
            # Process the response
            if response.status_code == 200:
                # Get the text content directly from the response
                text_content = response.content
                
                # Full path for the output file
                output_file_path = os.path.join(dir, output_filename)
                
                # Write the content to the file
                with open(output_file_path, 'wb') as f:
                    f.write(text_content)
                
                # Get the content as text for display
                try:
                    text_display = text_content.decode('utf-8')
                except UnicodeDecodeError:
                    text_display = "Binary content cannot be displayed as text."
                
                # Use the utility function to create the HTML preview
                html_preview = md_utils.create_html_preview(text_display, file_ext)
                
                # Return the path to the file, success message, and preview content
                return output_file_path, f"Content successfully processed.", html_preview, text_display
            else:
                # Handle error response
                error_msg = "Unknown error"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Unknown error')
                except:
                    error_msg = f"Error code: {response.status_code}"
                
                error_html = f"Error from API: {error_msg}"
                return None, error_html, error_html, f"Error from API: {error_msg}"
                
        except requests.exceptions.RequestException as e:
            error_html = f"Failed to connect to API: {str(e)}"
            return None, error_html, error_html, f"Failed to connect to API: {str(e)}"
    
    except Exception as e:
        error_html = f"Error processing content: {str(e)}"
        return None, error_html, error_html, f"Error processing content: {str(e)}"